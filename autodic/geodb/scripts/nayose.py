#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import division

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

import re
import gzip

import Levenshtein

import pandas as pd
import pandas.io.sql as sql

from pysqlite2 import dbapi2 as sqlite


sql_pref_codes = "SELECT DISTINCT pref_code FROM GeoCollection ORDER BY pref_code"
sql_geo_hashes = "SELECT DISTINCT geo_hash FROM GeoCollection WHERE pref_code = '%s' ORDER BY geo_hash"
sql_hash = """
SELECT
    id,
    source_id,
    source_type,
    name,
    uri,
    address,
    geo_type,
    geo_hash,
    pref_code,
    region_code,
    ASTEXT(geo_point) `geo_point`,
    coordinates
FROM
    GeoCollection
WHERE
    geo_hash = '%s'
AND delete_flag = 0
ORDER BY
    id
"""

import itertools

from collections import defaultdict

from pyproj import Geod
geod = Geod(ellps='WGS84')

re_alias = re.compile(r'[_ ]\(.*?\)')

import transaction

if 2 < len(sys.argv) and sys.argv[1] == '-d':
  geo_db = sys.argv[2]
else:
  geo_db = os.path.dirname(os.path.abspath(__file__)) + '/../geo.db'

conn = sqlite.connect(geo_db, isolation_level=None)
script = transaction.Script(conn)

re_parentheses_id2title = re.compile(r"\((\d+),\d+,'?([^,']+)'?,[^\)]+\)")
re_title_brackets = re.compile(r'[ _]\([^\)]+\)$')

from tqdm import tqdm

def main(args):
  global r2t, t2r
  r2t, t2r = get_redirect_dict()
  script.truncate_geo()

  pref_df = sql.read_sql(sql_pref_codes, conn)
  for pref_code in pref_df['pref_code'].values:
    if pref_code:
      hash_df = sql.read_sql(sql_geo_hashes % (pref_code), conn) 
      pref_tqdm = tqdm(hash_df['geo_hash'].values)
      pref_tqdm.set_description(pref_code)
      for geo_hash in pref_tqdm:
        exec_nayose(geo_hash)

  conn.close()

def get_redirect_dict():
  print('Reading redirect dict ...')
  data_dir = os.path.dirname(os.path.abspath(__file__)) + '/../../data'
  id_redirect = extract_id2title_from_sql(os.path.join(data_dir, 'jawiki-latest-redirect.sql.gz'))
  id_title = extract_id2title_from_sql(os.path.join(data_dir, 'jawiki-latest-page.sql.gz'))

  r2t = dict((normalize_title(id_title[e[0]]), normalize_title(e[1])) for e in id_redirect.iteritems() if e[0] in id_title)
  
  del id_redirect
  
  t2r = defaultdict(set)
  map(lambda x: t2r[x[1]].add(x[0]), r2t.iteritems())
  
  return r2t, t2r

def extract_id2title_from_sql(path):
  with gzip.GzipFile(path) as fd:
    return dict(re_parentheses_id2title.findall(fd.read().decode('utf8')))

def normalize_title(title):
  title = re_title_brackets.sub('', title)
  return title.replace('_', ' ')

def distance(p1, p2):
  return geod.inv(p1[0], p1[1], p2[0], p2[1])[2]

def exec_nayose(geo_hash):
  geo_cluster_dict = defaultdict(dict)
  df = sql.read_sql(sql_hash % (geo_hash), conn)
  for k, v in df.iterrows():
    g = {
      'id': v['id'],
      'source_id': v['source_id'],
      'source_type': v['source_type'],
      'name': v['name'],
      'uri': v['uri'],
      'address': v['address'],
      'geo_type': v['geo_type'],
      'geo_hash': v['geo_hash'],
      'pref_code': v['pref_code'],
      'region_code': v['region_code'],
      'geo_point': v['geo_point'],
      'coordinates': v['coordinates']
    }

    name = re_alias.sub('', v['name'])
    geo_cluster_dict[name][g['source_type']] = g
  
  for name, cluster in geo_cluster_dict.iteritems():
    if not name in r2t:
      geo, aliase = inspect_geo_cluster(cluster)
      script.insert_geo(geo, cluster.values(), aliase)

def inspect_geo_cluster(cluster):
  names = set() 
  
  if 'dbpedia' in cluster:
    geo = cluster['dbpedia']
  elif 'wikidata' in cluster:
    geo = cluster['wikidata']
  else:
    geo = cluster['fb']

  for v in cluster.itervalues():
    names.add(v['name'])
  
  nlen = len(geo['name'])
  #if geo['name'] in r2t:
  #  tlen = len(r2t[geo['name']])
  #  d = Levenshtein.distance(geo['name'], r2t[geo['name']])
  #  if d < 0.4 * max(nlen, tlen):
  #    geo['name'] = r2t[geo['name']]
  #elif geo['name'] in t2r:
  if geo['name'] in t2r:
    for name in t2r[geo['name']]:
      d = Levenshtein.distance(geo['name'], name)
      rlen = len(name)
      if d < 0.4 * max(nlen, rlen):
        names.add(name)
  else:
    pass

  return geo, names - {geo['name']}

if __name__ == '__main__':
  main(sys.argv)
