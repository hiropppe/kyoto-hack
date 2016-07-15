#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from tqdm import tqdm
from tinydb import TinyDB

import sqlite3
import transaction

base_dir = os.path.dirname(os.path.abspath(__file__))

if 2 < len(sys.argv) and sys.argv[1] == '-d':
  geo_db = sys.argv[2]
else:
  geo_db = base_dir + '/../geo.db'

conn = sqlite3.connect(geo_db)
script = transaction.Script(conn)

db = TinyDB(base_dir + '/place.json')

for item in tqdm(db.all()):
  try:
    db_item = {
      'source_type': 'fb',
      'source_id': item['id'],
      'name': item['name'],
      'uri': os.path.join('https://www.facebook.com/pages/', item['name'], item['id']),
      'address': item['location']['street'],
      'geo_type': 'Point',
      'coordinates': '[%13.10f, %13.10f]' % (item['location']['longitude'], item['location']['latitude']),
      'latitude': item['location']['latitude'],
      'longitude': item['location']['longitude']
    }
    script.insert_or_update(db_item) 
  except Exception, details:
    raise
    #sys.stderr.write('%s\n' % details)
    #continue

conn.commit()
conn.close()
db.close()