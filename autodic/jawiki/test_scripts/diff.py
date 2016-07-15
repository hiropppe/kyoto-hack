#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import codecs

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

a = set((codecs.open('kyoto_word', 'r', 'utf8').read().split('\n')))
b = set((codecs.open('my_word', 'r', 'utf8').read().split('\n')))

a_b = a - b
b_a = b - a

for w in sorted(a_b):
  sys.stdout.write(u'%s\n'%w)

for w in sorted(b_a):
  sys.stderr.write(u'%s\n'%w)
