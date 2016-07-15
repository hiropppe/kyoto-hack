#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

import json
import re
import mojimoji

from collections import defaultdict

import sqlite3

import pandas as pd
import pandas.io.sql as sql

from pandas import DataFrame, Series

if 2 < len(sys.argv) and sys.argv[1] == '-d':
  geo_db = sys.argv[2]
else:
  geo_db = os.path.dirname(os.path.abspath(__file__)) + '/../geo.db'

conn = sqlite3.connect(geo_db)

df = sql.read_sql("SELECT geo_id, name FROM Geo WHERE delete_flag = 0 ORDER BY geo_id", conn)

from pyknp import Juman

juman = Juman()

re_space = re.compile(ur'[　]+')
def normalize_name(name):
  name = mojimoji.han_to_zen(name)
  name = re_space.sub(u'　', name)
  name = name.strip(u'　')
  return name  

for _, v in df.iterrows():
  geo_id = v['geo_id']
  name = normalize_name(v['name'])
  mrphs = juman.analysis(name).mrph_list()

  #sys.stdout.write(u'%s Geodb:Entry/%s/%d\n' % \
  #  ('+'.join([mrph.midasi + '/' + mrph.yomi for mrph in mrphs]), name, geo_id)
  #)
  sys.stdout.write(u'%s Geodb:Entry/%s/%d\n' % \
    ('+'.join([mrph.midasi for mrph in mrphs]), name, geo_id)
  )

del df
df = sql.read_sql("""
  SELECT
    g.geo_id
  , a.name `alias`
  , g.name
  FROM
    Alias a
    INNER JOIN Geo g
      ON g.geo_id = a.geo_id
  WHERE
      a.delete_flag = 0
  AND g.delete_flag = 0
""", conn)

for _, v in df.iterrows():
  geo_id = v['geo_id']
  alias = normalize_name(v['alias'])
  name = normalize_name(v['name'])
  mrphs = juman.analysis(alias).mrph_list()
  
  #sys.stdout.write(u'%s Geodb:Alias/%s/%s/%d\n' % \
  #  ('+'.join([mrph.midasi + '/' + mrph.yomi for mrph in mrphs]), alias, name, geo_id)
  #)
  sys.stdout.write(u'%s Geodb:Alias/%s/%s/%d\n' % \
    ('+'.join([mrph.midasi for mrph in mrphs]), alias, name, geo_id)
  )

conn.close()
