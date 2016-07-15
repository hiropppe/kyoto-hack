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

def best_category(name):
  if name in shop_name_category_count and 0 < len(shop_name_category_count[name]):
    return sorted(shop_name_category_count[name].items(), key=lambda x: x[1], reverse=True)[0][0]
  else:
    return 'Local Business'

shop_name_count = defaultdict(int)
shop_name_category_count = defaultdict(lambda: defaultdict(int))
shop_chain_suffix_count = defaultdict(int)

# Step.1 ○○　●●店
for row in data:
  name = normalize_name(row['name'])  
  last_sepalation = max(name.rfind(u'　'), name.rfind(u'／'))
  if not last_sepalation == -1 and name.endswith(u'店'):
    shop_name_count[name[:last_sepalation]] += 1
    shop_name_category_count[name[:last_sepalation]][row['category_list'][0]['name']] += 1
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
          shop_name_category_count[name[:len(suffix)]][row['category_list'][0]['name']] += 1


from pyknp import Juman
juman = Juman()

single_mrph_words, multiple_mrph_words = [], []

for name, count in sorted(shop_name_count.items(), key=lambda x: x[1], reverse=True):
  mrphs = juman.analysis(name).mrph_list()
  
  if (not name in known_garbages and 
      not (len(mrphs) == 1 and mrphs[0].bunrui == u'地名') and
      not any(ignore in name for ignore in ignore_keyword)):
    
    #  print name, count, best_category(name)    
    
    if all(1 == len(mrph.midasi) for mrph in mrphs):
      sys.stdout.write(u'(名詞 (%s ((読み %s)(見出し語 (%s %1.1f))(意味情報 "Geodb:Shop/%s/%s"))))\n' % \
        (u'地名', ''.join([mrph.yomi for mrph in mrphs]), name, 1.0, name, best_category(name))
      )
      #sys.stdout.write('%s %s %d\n' % (name, best_category(name), count))
    else:
      sys.stderr.write(u'%s Geodb:Shop/%s/%s\n' % \
        ('+'.join([mrph.midasi for mrph in mrphs]), name, best_category(name))
      )
      #sys.stderr.write(u'%s Geodb:Shop/%s/%s\n' % \
      #  ('+'.join([mrph.midasi + '/' + mrph.yomi for mrph in mrphs]), name, best_category(name))
      #)
      #sys.stshderr.write('%s %s %d\n' % (name, best_category(name), count))
