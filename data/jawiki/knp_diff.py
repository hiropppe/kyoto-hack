#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import codecs
import re
import mojimoji

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

dat = 'wikipedia.dat'
mydat = 'knp.dat'

dat_set = set()
mydat_set = set()
for l in codecs.open(dat, 'r', 'utf-8'):
  cols = l[:l.find('Wikipedia')-1].split('+')
  dat_set.add(''.join([col.split('/')[0] for col in cols]))

for l in codecs.open(mydat, 'r', 'utf8'):
  mydat_set.add(mojimoji.han_to_zen(l[:-1]))

dat_mydat = dat_set - mydat_set
mydat_dat = mydat_set - dat_set

print(len(dat_set))
print(len(mydat_set))
for w in sorted(dat_mydat):
  sys.stdout.write(u'%s\n'%w)

for w in sorted(mydat_dat):
  sys.stderr.write(u'%s\n'%w)
