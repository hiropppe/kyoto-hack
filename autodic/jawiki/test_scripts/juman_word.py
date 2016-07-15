#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import sys
import codecs

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

re1 = re.compile(ur'\(見出し語 \((.+?) \d\.\d\)')
re2 = re.compile(ur'\(見出し語 (.+?)\)')
words = set()
for l in codecs.open('Wikipedia.dic', 'r', 'utf-8'):
  m = re1.search(l)
  if not m:
    m = re2.search(l)
  if m:
    words.add(m.group(1))
  else:
    sys.stderr.write(l)

for w in words:
  sys.stdout.write('%s\n'%w)
