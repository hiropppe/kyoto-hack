#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

import sys
import os
import codecs
sys.stdin = codecs.getreader('utf8')(sys.stdin)
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

import gzip
import re
import jctconv
import mojimoji
import unicodedata
import Levenshtein

from pyknp import Juman
juman = Juman()

if 2 < len(sys.argv) and sys.argv[1] == '-d':
  data_dir = sys.argv[2]
else:
  data_dir = os.path.dirname(os.path.abspath(__file__)) 

import cdb
hypos = cdb.init(os.path.join(data_dir, 'hyponymy.cdb'))
readings = cdb.init(os.path.join(data_dir, 'reading.cdb'))

re_parentheses_id2title = re.compile(r"\((\d+),\d+,'?([^,']+)'?,[^\)]+\)")

def extract_title2id_from_sql(path):
  with gzip.GzipFile(path) as fd:
    return dict(((e[1], e[0]) for e in re_parentheses_id2title.findall(fd.read().decode('utf8'))))

def extract_id2title_from_sql(path):
  with gzip.GzipFile(path) as fd:
    return dict(re_parentheses_id2title.findall(fd.read().decode('utf8')))

title2id = extract_title2id_from_sql(os.path.join(data_dir, 'jawiki-latest-page.sql.gz'))
id2redirect = extract_id2title_from_sql(os.path.join(data_dir, 'jawiki-latest-redirect.sql.gz')) 

for title in sys.stdin:
  title = title[:-1]
  try:
    page_id = title2id[title.replace(' ', '_')]
  except KeyError, details:
    sys.stderr.write(u'%s\n' % details)
    continue
  
  F_cost = 1.0
  for c in title:
    if unicodedata.name(c)[0:8] == "HIRAGANA":
      F_cost = 1.6
      break
    elif not unicodedata.name(c)[0:5] == "LATIN":
      F_cost = 1.1
      break
    else:
      pass
  
  if page_id in id2redirect:
    redirect = mojimoji.han_to_zen(id2redirect[page_id].replace('_', ' '))
    F_redirect = u'Wikipediaリダイレクト:' + redirect 
    
    kata_title = jctconv.kata2hira(redirect)
    kata_redirect = jctconv.kata2hira(mojimoji.han_to_zen(title))
    if Levenshtein.distance(kata_title, kata_redirect) < 5:
      F_head = u'代表表記:' + redirect
    else:
      F_head = ''
  else:
    F_redirect = None
    F_head = None
  
  title_str = title.encode('utf8')
  if hypos.has_key(title_str):
    F_best_hypo = u'Wikipedia上位語:' + re.split(r'\s', hypos[title_str])[0].decode('utf8')
    imis = juman.analysis(F_best_hypo).mrph_list()[-1].imis
    if u'人' in imis:
      F_bunrui = u'人名'
    elif u'場所' in imis:
      F_bunrui = u'地名'
    elif u'組織' in imis:
      F_bunrui = u'組織名'
    else:
      F_bunrui = u'普通名詞'
  else:
    F_best_hypo = None
    F_bunrui = u'普通名詞'
  
  title_str = title.encode('utf8')
  F_title = mojimoji.han_to_zen(title)
  if readings.has_key(title_str):
    F_reading = readings[title_str].decode('utf-8')
    F_auto = u'Wikipedia'
  elif re.match(ur'^[ぁ-んァ-ンー]+$', F_title):
    F_reading = F_title
    F_auto = u'Wikipedia'
  else:
    F_reading = F_title
    F_auto = u'Wikipedia 読み不明'
  
  if F_redirect:
    F_semantic = ' '.join([F_auto, F_redirect, F_head])
  elif F_best_hypo:
    F_semantic = ' '.join([F_auto, F_best_hypo])
  else:
    F_semantic = F_auto
  F_semantic = re.sub(r'\s+', ' ', F_semantic).strip() 
  
  sys.stdout.write(u'(名詞 (%s ((読み %s)(見出し語 (%s %1.1f))(意味情報 "自動獲得:%s"))))\n' % (F_bunrui, F_reading, F_title, F_cost, F_semantic)) 
