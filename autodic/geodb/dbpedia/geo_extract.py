#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function, division

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

import re
import codecs
import shutil
import glob
import bz2
import datetime

from tqdm import tqdm
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from pysqlite2 import dbapi2 as sqlite

import transaction 


if 2 < len(sys.argv) and sys.argv[1] == '-d':
  geo_db = sys.argv[2]
else:
  geo_db = os.path.dirname(os.path.abspath(__file__)) + '/../geo.db'

conn = sqlite.connect(geo_db)
script = transaction.Script(conn)

re_geocoord = re.compile(ur'<http://ja.dbpedia.org/resource/(.+?)> <http://www.georss.org/georss/point> "(.+?)"')
re_infobox_triple = re.compile(ur'<http://ja.dbpedia.org/resource/(.+?)> <http://ja.dbpedia.org/property/(.+?)> ["<](.+?)[">]')

geo_property_set = {u'緯度度', u'緯度分', u'緯度秒', u'経度度', u'経度分', u'経度秒'}

def extract_from_geocoord(dump_file):
  bzf = tqdm(bz2.BZ2File(dump_file))
  bzf.set_description(dump_file)
  for line in bzf:
    line = line.decode('utf8')
    if not line[0] == '#':
      match = re_geocoord.match(line)
      if match:
        subject = match.group(1)
        lat_lon = match.group(2).split()
        
        item = {
          'data_id': subject,
          'name': subject,
          'uri': os.path.join('http://ja.dbpedia.org/page/', subject),
          'latitude': float(lat_lon[0]),
          'longitude': float(lat_lon[1])
        }
        if 20 < float(lat_lon[0]) and float(lat_lon[0]) < 46 and 122 < float(lat_lon[1]) and float(lat_lon[1]) < 154:
          yield item

def extract_from_infobox(dump_file):
  current_subject = None
  current_geo_info = []
  bzf = tqdm(bz2.BZ2File(dump_file))
  bzf.set_description(dump_file)
  for line in bzf:
    line = line.decode('utf8')
    if not line[0] == '#':
      match = re_infobox_triple.match(line)
      if match:
        triple = (match.group(1), match.group(2), match.group(3))
      
        if not triple[0] == current_subject:
          if current_subject:
            if len(current_geo_info) == 6:
              lat = float(current_geo_info[0] + current_geo_info[1]/60 + current_geo_info[2]/3600)
              lon = float(current_geo_info[3] + current_geo_info[4]/60 + current_geo_info[5]/3600)
              item = {
                'data_id': current_subject,
                'name': current_subject,
                'uri': os.path.join('http://ja.dbpedia.org/page/', current_subject),
                'latitude': lat,
                'longitude': lon
              }
              
              if 20 < lat and lat < 46 and 122 < lon and lon < 154:
                yield item

            del current_geo_info[:] 
        
          current_subject = triple[0]

        if triple[1] in geo_property_set:
          try: 
            current_geo_info.append(float(triple[2]))
          except UnicodeEncodeError:
            print(u'Invalid geo coordinate. %s,%s,%s' % (triple[0], triple[1], triple[2]))
        
def pick_file(pattern):
  files = glob.glob(pattern)
  if files:
    return files[0]

def update(dump_file, make_func):
  dump_file = pick_file(dump_file)
  if dump_file:
    for item in make_func(dump_file):
      item.update({
        'datasource': 'dbpedia',
        'address': '',
        'geo_type': 'Point',
      })
      
      script.insert_or_update(item)
    
    conn.commit()

data_dir = os.path.dirname(os.path.abspath(__file__))
update(os.path.join(data_dir, 'jawiki-*-geo-coordinates.ttl.bz2'), extract_from_geocoord)
update(os.path.join(data_dir, 'jawiki-*-geo-coordinates-mappingbased.ttl.bz2'), extract_from_geocoord)
update(os.path.join(data_dir, 'jawiki-*-infobox-properties-unredirected.ttl.bz2'), extract_from_infobox)

conn.close()
