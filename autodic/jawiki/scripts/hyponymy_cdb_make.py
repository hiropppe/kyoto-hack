#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from collections import defaultdict
import cdb
from tqdm import tqdm

if 1 < len(sys.argv) and sys.argv[1] == '-d':
  db_name = sys.argv[2]
else:
  db_name = 'hyponymy.cdb'

hyponymy = defaultdict(list)

for line in tqdm(sys.stdin):
  cols = line[:-1].split()
  hyponymy[cols[1]].append((cols[0], cols[2]))
  hyponymy[cols[1]] = sorted(hyponymy[cols[1]], key=lambda x: float(x[1]), reverse=True)

maker = cdb.cdbmake(db_name, db_name + '.tmp')

for k, v in hyponymy.iteritems():
  maker.add(k, '\t'.join((' '.join(e) for e in v)))

maker.finish()
