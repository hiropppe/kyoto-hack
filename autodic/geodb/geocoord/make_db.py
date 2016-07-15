#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, codecs
import argparse, textwrap
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

import glob
import zipfile
import codecs

import cdb
import Geohash

from collections import defaultdict

def main(args):
  if args['isj']:
    make_db_from_isj(args['isj'], args['precision'])

def make_db_from_isj(data_dir, precision):
  db_name = os.path.dirname(os.path.abspath(__file__)) + '/geoseed.db'
  maker = cdb.cdbmake(db_name, db_name + '.tmp')
  
  for filename in glob.glob(os.path.join(data_dir, '*.zip')):
    geodict = defaultdict(list)
    with zipfile.ZipFile(filename) as zf:
      print('Add from %s' % (filename))
      for name in zf.namelist():
        if not name.endswith('.csv'):
          continue

        with zf.open(name) as csv:
          csv.next()
          for row in csv:
            row = codecs.decode(row[:-1].replace('"', ''), 'ms932')
            row = row.split(',')
            
            pref_code = row[0]
            region_code = row[2]
            block_code = row[4]
            
            lat = row[6]
            lon = row[7]
            
            geohash = Geohash.encode(float(lat), float(lon), precision)
            geodict[geohash].append('/'.join([lat, lon, pref_code, region_code, block_code]))
      
      if len(geodict) == 0:
        sys.stderr.write('No data found in %s' % (zipfile))
      else:
        for k, v in geodict.iteritems():
          maker.add(k, ';'.join(v))
        geodict.clear()
  
  maker.finish()
  print('Finish.')

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
      description=''
  )

  parser.add_argument('-i', '--isj', type=str, default=os.path.dirname(os.path.abspath(__file__)) + '/isj/b',
                        help=u'位置参照情報データ（大字・町丁目レベル）')
  parser.add_argument('-p', '--precision', type=int, default=5,
                        help='')

  main(vars(parser.parse_args()))
