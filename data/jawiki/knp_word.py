#!/usr/bin/env python

import sys
import codecs

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

words = set()
for l in codecs.open('wikipedia.dat', 'r', 'utf-8'):
  cols = l[:l.find('Wikipedia')-1].split('+')
  words.add(''.join([col.split('/')[0] for col in cols]))

for w in words:
  sys.stdout.write('%s\n'%w)
