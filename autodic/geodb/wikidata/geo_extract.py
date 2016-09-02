#!/usr/bin/env python

from __future__ import print_function

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

import json
import gzip

from collections import defaultdict
from tqdm import tqdm
from pysqlite2 import dbapi2 as sqlite

import argparse

import transaction 

parser = argparse.ArgumentParser(
  description='Wikidata geo loader'
)
parser.add_argument('-d', '--geo-db', type=str,
                    default=os.path.dirname(os.path.abspath(__file__)) + '/../geo.db',
                    help="")
parser.add_argument('-f', '--dump-file', type=str,
                    default=os.path.dirname(os.path.abspath(__file__)) + '/latest-all.json.gz',
                    help="")

args = vars(parser.parse_args())

dump_file = args['dump_file']

conn = sqlite.connect(args['geo_db'])
script = transaction.Script(conn)

with gzip.GzipFile(dump_file) as fd:
  try:
    fd.next()
    bar = tqdm(fd)
    bar.set_description(dump_file)
    for line in bar:
      try:
        d = json.loads(line[:-2])
      except Exception, details:
        sys.stderr.write('%s %s\n' % (details, line))
        continue
    
      if ('ja' in d['labels'] and 
          'claims' in d and 'P625' in d['claims'] and
          'datavalue' in d['claims']['P625'][0]['mainsnak']):
      
        lon = d['claims']['P625'][0]['mainsnak']['datavalue']['value']['longitude']
        lat = d['claims']['P625'][0]['mainsnak']['datavalue']['value']['latitude']

        item = {
          'data_id': d['id'],
          'datasource': 'wikidata',
          'name': d['labels']['ja']['value'],
          'uri': os.path.join('https://www.wikidata.org/wiki/', d['id']),
          'address': '',
          'geo_type': 'Point',
          'latitude': lat,
          'longitude': lon
        }
      
        if 20 < lat and lat < 46 and 122 < lon and lon < 154:
          script.insert_or_update(item) 
  
  except Exception, details:
    sys.stderr.write('%s\n' % details)

conn.commit()
conn.close()
