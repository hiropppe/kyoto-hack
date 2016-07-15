#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import codecs
sys.stdin = codecs.getreader('utf8')(sys.stdin)
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

import re
re_title = re.compile(r'<title>Wikipedia: (.+?)</title>')
re_abstract = re.compile(r'<abstract>(.+?)</abstract>')

import jctconv

re_all_hirakana = re.compile(ur'^[ぁ-ん ]+$')

import cdb

if 1 < len(sys.argv) and sys.argv[1] == '-d':
  db_name = sys.argv[2]
else:
  db_name = 'reading.cdb'

maker = cdb.cdbmake(db_name, db_name + '.tmp')

from tqdm import tqdm
for l in tqdm(sys.stdin):
  title_match = re_title.search(l)
  abstract_match = re_abstract.search(l)
  
  if title_match:
    title = title_match.group(1)
    title = re.sub(ur'\(.+\)$', '', title)
    if not title:
      title = title_match.group(1)
  elif abstract_match:
    if not title:
      sys.stderr.write(u'Abstract without title, %s' % abstract_match.group(1))
    abstract = abstract_match.group(1)
    if abstract.startswith(title):
      abstract = abstract[len(title):]
      paren = re.search(ur'^（(.+?)[,:、：。）]', abstract)
      if paren:
        reading = jctconv.kata2hira(paren.group(1)).strip()
        if re.search(ur'\sまたは\s', reading):
          reading = reading.split(u'または')[0]
        if re_all_hirakana.match(reading):
          reading = re.sub(ur'[\s　]', '', reading)
          if 'maker' in locals():
            maker.add(title.encode('utf8'), reading.encode('utf8'))
    title = None 
  else:
    pass

if 'maker' in locals():
  maker.finish()
