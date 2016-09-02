#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from tqdm import tqdm
from tinydb import TinyDB

from pysqlite2 import dbapi2 as sqlite

import transaction

base_dir = os.path.dirname(os.path.abspath(__file__))

if 2 < len(sys.argv) and sys.argv[1] == '-d':
  geo_db = sys.argv[2]
else:
  geo_db = base_dir + '/../geo.db'

conn = sqlite.connect(geo_db)
script = transaction.Script(conn)

db = TinyDB(base_dir + '/place.json')

for item in tqdm(db.all()):
  try:
    db_item = {
      'datasource': 'fb',
      'data_id': item['id'],
      'name': item['name'],
      'uri': os.path.join('https://www.facebook.com/pages/', item['name'], item['id']),
      'address': item['location']['street'],
      'geo_type': 'Point',
      'latitude': item['location']['latitude'],
      'longitude': item['location']['longitude']
    }
    script.insert_or_update(db_item) 
  except Exception, details:
    sys.stderr.write('%s\n' % details)
    continue

conn.commit()
conn.close()
db.close()
