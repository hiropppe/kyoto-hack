#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

import re
import json

import sqlite3
from sqlite3 import IntegrityError

import mojimoji

from collections import defaultdict

from tqdm import tqdm

base_dir = os.path.dirname(os.path.abspath(__file__))

if 2 < len(sys.argv) and sys.argv[1] == '-d':
  geo_db = sys.argv[2]
else:
  geo_db = base_dir + '/../geo.db'

conn = sqlite3.connect(geo_db, isolation_level=None)

data_json = json.load(open(os.path.dirname(os.path.abspath(__file__)) + '/place.json'))
data = data_json['_default'].values()
  
re_paren = re.compile(ur'（.+?）')
re_space = re.compile(ur'[　]+')

known_garbages = {
  u'株式会社', u'有限会社',
  u'ラーメン', u'らーめん', u'麺や', u'麺処', u'麺屋', u'みそラーメン',
  u'ステーキ', u'焼肉', u'焼鳥ダイニング', u'炭火やきとり',
  u'回転寿し', u'回転寿司',
  u'居酒屋', u'大衆居酒屋', u'海鮮居酒屋',
  u'第一会館', u'Ｉ　Ｃ',
  u'北海道'
}

ignore_keyword = {
  u'グループ'
}

def normalize_name(name):
  name = mojimoji.han_to_zen(name)
  name = re_paren.sub('', name)
  name = re_space.sub(u'　', name)
  name = name.strip(u'　')
  return name  

shop_name_count = defaultdict(int)
shop_chain_suffix_count = defaultdict(int)

# Step.1 ○○　●●店
for row in data:
  name = normalize_name(row['name'])  
  last_sepalation = max(name.rfind(u'　'), name.rfind(u'／'))
  if not last_sepalation == -1 and name.endswith(u'店'):
    shop_name_count[name[:last_sepalation]] += 1
    shop_chain_suffix_count[name[last_sepalation+1:]] += 1

shop_names = shop_name_count.keys()
shop_chain_suffixes = shop_chain_suffix_count.keys()

# Step.2 ○○●●店
for row in data:
  name = normalize_name(row['name'])  
  last_sepalation = max(name.rfind(u'　'), name.rfind(u'／'))
  if last_sepalation == -1 and name.endswith(u'店'):
    for shop_name in shop_names:
      if len(shop_name) < len(name) and name.startswith(shop_name):
        if not name[len(shop_name):] in shop_chain_suffix_count:
          shop_chain_suffix_count[name[len(shop_name):]] += 1
    
    for suffix in shop_chain_suffixes:
      if len(suffix) < len(name) and name.endswith(suffix):
        if not name[:-len(suffix)] in shop_name_count:
          shop_name_count[name[:-len(suffix)]] += 1

len_dict = defaultdict(set)
for name, count in sorted(shop_name_count.items(), key=lambda x: x[1], reverse=True):
  if (not name in known_garbages and 
      not any(ignore in name for ignore in ignore_keyword)):
    len_dict[len(name)].add(name)

cursor = conn.execute("SELECT geo_id, name FROM Geo WHERE delete_flag = 0")
row = cursor.fetchone()
while(row):
  for length, name_set in len_dict.iteritems():
    if length < len(row[1]) and not (row[1] in name_set) and row[1][:length] in name_set:
      try:
        #print('%s -> %s' % (row[1], row[1][:length]))
        conn.execute("INSERT OR IGNORE INTO Alias (geo_id, name) VALUES (:geo_id, :name)",
            {'geo_id': row[0], 'name': row[1][:length]})
      except IntegrityError:
        pass
  row = cursor.fetchone()
cursor.close()
