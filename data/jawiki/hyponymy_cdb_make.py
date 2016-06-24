#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from collections import defaultdict
import cdb

db_name = 'hyponymy.cdb'

hyponymy = defaultdict(list)

for line in sys.stdin:
  cols = line[:-1].split()
  hyponymy[cols[1]].append((cols[0], cols[2]))
  hyponymy[cols[1]] = sorted(hyponymy[cols[1]], key=lambda x: float(x[1]), reverse=True)

maker = cdb.cdbmake(db_name, db_name + '.tmp')

for k, v in hyponymy.iteritems():
  maker.add(k, '\t'.join((' '.join(e) for e in v)))

maker.finish()
