#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import Geohash
import pyproj
import cdb

from pyproj import Geod
geod = Geod(ellps='WGS84')

class Geocoord(object):

  def __init__(self, precision=5):
    self.db = cdb.init(os.path.dirname(os.path.abspath(__file__)) + '/geoseed.db')
    self.precision = precision

  def reverse(self, lat, lon):
    nearest = None
    nearest_d = sys.maxint
    
    geohash = Geohash.encode(lat, lon, self.precision) 
    if self.db.has_key(geohash):
      nearest_d = sys.maxint
      for block in self.db[geohash].split(';'):
        block = block.split('/')
        d = geod.inv(lon, lat, float(block[1]), float(block[0]))[2]
        if d < nearest_d:
          nearest = ((block[2], block[3], block[4]), d)
          nearest_d = d
    
    return nearest
