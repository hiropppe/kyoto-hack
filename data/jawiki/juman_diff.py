#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import codecs
import re
import mojimoji

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

dat = 'Wikipedia.dic'
mydat = 'juman.dat'

dat_set = set()
mydat_set = set()

re1 = re.compile(ur'\(見出し語 \((.+?) \d\.\d\)')
re2 = re.compile(ur'\(見出し語 (.+?)\)')
for l in codecs.open(dat, 'r', 'utf-8'):
  m = re1.search(l)
  if not m:
    m = re2.search(l)
  if m:
    dat_set.add(m.group(1))
  else:
    print l

for l in codecs.open(mydat, 'r', 'utf8'):
  mydat_set.add(mojimoji.han_to_zen(l[:-1]))

dat_mydat = dat_set - mydat_set
mydat_dat = mydat_set - dat_set

for w in sorted(dat_mydat):
  sys.stdout.write(u'%s\n'%w)

for w in sorted(mydat_dat):
  sys.stderr.write(u'%s\n'%mojimoji.han_to_zen(w))
