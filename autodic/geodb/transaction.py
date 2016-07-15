# -*- coding:utf-8 -*-

import datetime
import Geohash

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from geocoord import Geocoord

class Script(object):

  def __init__(self, conn):
    self.commit_buffer = 0
    self.commit_interval = 10000
    self.conn = conn
    self.cur = conn.cursor()
    self.geohash_precision = 5 
    self.geocoorder = Geocoord(self.geohash_precision)

  def truncate_geo(self):
    self.cur.execute('delete from Alias')
    self.cur.execute('delete from Geo')

  def insert_geo(self, geo, geo_children, aliases):
    result = self.cur.execute("""
      INSERT INTO Geo (
        name,
        uri,
        address,
        geo_type,
        geo_hash,
        pref_code,
        region_code,
        latitude,
        longitude,
        coordinates
      ) VALUES (
        :name,
        :uri,
        :address,
        :geo_type,
        :geo_hash,
        :pref_code,
        :region_code,
        :latitude,
        :longitude,
        :coordinates
      )
    """, geo)
    
    geo_id = result.lastrowid

    for aliase in aliases:
      self.cur.execute("INSERT INTO Alias(geo_id, name) VALUES (:geo_id, :name)",
          {'geo_id': geo_id, 'name': aliase})
    
    for geo_child in geo_children:
      self.cur.execute("UPDATE GeoCollection SET geo_id = :geo_id WHERE id = :id",
          {'geo_id': geo_id, 'id': geo_child['id']})

    self.lazy_commit()

  def insert_or_update(self, item):
    nearest_isj = self.geocoorder.reverse(item['latitude'], item['longitude'])
    if nearest_isj:
      pref_code = nearest_isj[0][0]
      region_code = nearest_isj[0][1]
    else:
      pref_code = ''
      region_code = ''

    item.update({
      'geo_hash': Geohash.encode(item['latitude'], item['longitude'], precision=self.geohash_precision),
      'pref_code': pref_code,
      'region_code': region_code,
      'now': datetime.datetime.now()
    })
    
    result = self.cur.execute("""
      INSERT OR IGNORE INTO GeoCollection (
        source_id,
        source_type,
        name,
        uri,
        address,
        geo_type,
        geo_hash,
        pref_code,
        region_code,
        latitude,
        longitude,
        coordinates
      ) VALUES (
        :source_id,
        :source_type,
        :name,
        :uri,
        :address,
        :geo_type,
        :geo_hash,
        :pref_code,
        :region_code,
        :latitude,
        :longitude,
        :coordinates
      )
      """, item
    )

    if result.rowcount == 0:
      self.cur.execute("""
        UPDATE GeoCollection
          name = :name,
          uri = :uri,
          address = :address,
          geo_type = :geo_type,
          geo_hash = :geo_hash,
          pref_code = :pref_code,
          region_code = :region_code,
          latitude = :latitude,
          longitude = :longitude,
          coordinates = :coordinates,
          update_datetime = :now        
        WHERE
            source_id = :source_id,
        AND source_type = :source_type
        """, item
      )
    
    self.lazy_commit()

  def lazy_commit(self):
    self.commit_buffer += 1
    if self.commit_interval <= self.commit_buffer:
      self.conn.commit()
      self.commit_buffer = 0
