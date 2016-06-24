#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

import sys
import codecs
sys.stdin = codecs.getreader('utf8')(sys.stdin)
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

import gzip
import re
import mojimoji
from pyknp import Juman
juman = Juman()

import cdb
hypos = cdb.init('hyponymy.cdb')

re_parentheses_id2title = re.compile(r"\((\d+),\d+,'?([^,']+)'?,[^\)]+\)")

def extract_title2id_from_sql(path):
  with gzip.GzipFile(path) as fd:
    return dict(((e[1], e[0]) for e in re_parentheses_id2title.findall(fd.read().decode('utf8'))))

def extract_id2title_from_sql(path):
  with gzip.GzipFile(path) as fd:
    return dict(re_parentheses_id2title.findall(fd.read().decode('utf8')))

title2id = extract_title2id_from_sql('jawiki-latest-page.sql.gz')
id2redirect = extract_id2title_from_sql('jawiki-latest-redirect.sql.gz') 

def morph(mrph):
  if mrph.midasi in [u'\u30fb', u'\uff0f', u'\u3000']:
    return mrph.midasi
  else:
    return mrph.midasi + '/' + mrph.yomi

def get_best_hypo(title):
  title_str = title.encode('utf8')
  if hypos.has_key(title_str):
    return re.split(r'\s', hypos[title_str])[0].decode('utf8')
  else:
    return u'不明'

redirect_cache = set()
for title in sys.stdin:
  title = title[:-1]
  try:
    page_id = title2id[title.replace(' ', '_')]
  except KeyError, details:
    sys.stderr.write(u'%s\n' % details)
    continue
  
  if title in redirect_cache:
    continue
  
  if page_id in id2redirect:
    redirect_title = id2redirect[page_id].replace('_', ' ')
    redirect_title_zen = mojimoji.han_to_zen(redirect_title)
    
    # Workaround. redirection target entry required
    if not redirect_title in redirect_cache:
      redirect_mrphs = '+'.join([morph(mrph) for mrph in juman.analysis(redirect_title_zen).mrph_list()])
      redirect_best_hypo = get_best_hypo(redirect_title)
      redirect_cache.add(redirect_title)
    else:
      redirect_mrphs = None
  else:
    redirect_title = None
    redirect_mrphs = None
     
  best_hypo = get_best_hypo(title)

  title = mojimoji.han_to_zen(title)
  mrphs = '+'.join([morph(mrph) for mrph in juman.analysis(title).mrph_list()])
  
  sys.stdout.write(u'%s Wikipediaエントリ:%s\n' % (mrphs, title))
  if redirect_title:
    sys.stdout.write(u'%s Wikipediaリダイレクト:%s\n' % (mrphs, redirect_title_zen))
    
    if redirect_mrphs: 
      sys.stdout.write(u'%s Wikipediaエントリ:%s\n' % (redirect_mrphs, redirect_title_zen))
      sys.stdout.write(u'%s Wikipedia上位語:%s\n' % (redirect_mrphs, redirect_best_hypo))
  else:
    sys.stdout.write(u'%s Wikipedia上位語:%s\n' % (mrphs, best_hypo))
