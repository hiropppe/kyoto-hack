#!/usr/bin/env python

from __future__ import division

import sys
import os
import json
import requests
import time

from tqdm import tqdm
from tinydb import TinyDB, Query

import me

template = 'https://graph.facebook.com/%s/search?type=place&center=%s&distance=%s&access_token=%s'

base_dir = os.path.dirname(os.path.abspath(__file__))
f = open(base_dir + '/station20160401free.csv')
eki_data = f.readlines()

db = TinyDB(base_dir + '/place.json')

begin = 1
if 2 < len(sys.argv) and sys.argv[1] == '-l':
  begin = int(sys.argv[2])

for i, l in enumerate(tqdm(eki_data[begin:])):
  cols = l[:-1].split(',')
  lon, lat = cols[9], cols[10]
  url = template % (me.version, lat + ',' + lon, me.distance, me.access_token)
  #print 'Search around %s %s' % (cols[2], cols[8])
  while url:
    try:
      r = requests.get(url)
      page = json.loads(r.text)
      if 'error' in page:
        print(page)
        if page['error']['code'] == 190:
          sys.stderr.write('Access Token invalidated !! Exit at line %d\n' % (begin+i))
          sys.exit(-1) 
        else:
          continue
      
      if 'paging' in page and 'next' in page['paging']:
        url = page['paging']['next']
      else:
        url = None
      
      for item in page['data']:
        q = Query()
        pid = item['id']
        if db.search(q.id == pid):
          db.update(item, q.id == pid)
        else:
          db.insert(item)
    except Exception, details:
      sys.stderr.write('%s\n' % details)
      break
    finally:
      pass
      #time.sleep(.1)
