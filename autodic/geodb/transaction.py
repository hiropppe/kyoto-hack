# -*- coding:utf-8 -*-

import binascii
import datetime
import Geohash

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from geocoord import Geocoord

import pysqlite2


class Script(object):

  def __init__(self, conn):
    self.commit_buffer = 0
    self.commit_interval = 10000
    self.conn = conn
    self.cur = conn.cursor()
    self.geohash_precision = 5 
    self.geocoorder = Geocoord(self.geohash_precision)
    
    self.conn.enable_load_extension(True)
    self.conn.execute("SELECT load_extension('/usr/local/lib/mod_spatialite.so')")

  def insert_geo(self, geo, geo_externs, aliases):
    current_geo_ids = [geo_extern['geo_id'] for geo_extern in geo_externs if geo_extern['geo_id']]
    if current_geo_ids:
        geo_id = sorted(current_geo_ids)[0]
    else:
        geo_id = None

    if not geo_id:
        result = self.cur.execute("""
            INSERT INTO Geo (
                name,
                uri,
                address,
                geo_type,
                geo_hash,
                pref_code,
                region_code,
                geo_point
            ) VALUES (
                :name,
                :uri,
                :address,
                :geo_type,
                :geo_hash,
                :pref_code,
                :region_code,
                GeomFromText(:geo_point)
            )
            """, geo)
    
        geo_id = result.lastrowid
    else:
        geo_externs = [geo_extern for geo_extern in geo_externs if not geo_extern['geo_id']]
        
        self.cur.execute("""
            UPDATE
                Geo
            SET
                name = :name,
                uri = :uri,
                address = :address,
                geo_type = :geo_type,
                pref_code = :pref_code,
                region_code = :region_code,
                geo_point = GeomFromText(:geo_point),
                update_datetime = DATETIME('now', '+09:00:00')
            WHERE
                geo_id = :geo_id
            AND modified = 0
        """, geo)

    for each_extern in geo_externs:
        self.cur.execute("""
            UPDATE
                GeoExtern
            SET
                geo_id = :geo_id,
                update_datetime = DATETIME('now', '+09:00:00')
            WHERE
                extern_id = :extern_id
            """,
            {'geo_id': geo_id, 'extern_id': each_extern['extern_id']}
        )
        
    for aliase in aliases:
        self.cur.execute("INSERT OR IGNORE INTO Alias(geo_id, name) VALUES (:geo_id, :name)",
        {'geo_id': geo_id, 'name': aliase})

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
      'data_hash': '%08X' % (binascii.crc32(''.join([item['datasource'], item['data_id']]).encode('utf8')) & 0xffffffff),
      'geo_hash': Geohash.encode(item['latitude'], item['longitude'], precision=self.geohash_precision),
      'geo_point': 'POINT(%13.10f %13.10f)' % (item['longitude'], item['latitude']),
      'pref_code': pref_code,
      'region_code': region_code
    })

    result = self.cur.execute("""
      INSERT OR IGNORE INTO GeoExtern (
        data_hash,
        data_id,
        datasource,
        uri,
        name,
        address,
        geo_type,
        geo_hash,
        pref_code,
        region_code,
        geo_point
      ) VALUES (
        :data_hash,
        :data_id,
        :datasource,
        :uri,
        :name,
        :address,
        :geo_type,
        :geo_hash,
        :pref_code,
        :region_code,
        GeomFromText(:geo_point)
      )
      """, item
    )

    if result.rowcount == 0:
      self.cur.execute("""
        UPDATE
          GeoExtern
        SET
          datasource = :datasource,
          uri = :uri,
          name = :name,
          address = :address,
          geo_type = :geo_type,
          geo_hash = :geo_hash,
          pref_code = :pref_code,
          region_code = :region_code,
          geo_point = GeomFromText(:geo_point),
          update_datetime = DATETIME('now', '+09:00:00')        
        WHERE
            data_hash = :data_hash
        AND data_id = :data_id
        """, item
      )
    
    self.lazy_commit()

  def lazy_commit(self):
    self.commit_buffer += 1
    if self.commit_interval <= self.commit_buffer:
      self.conn.commit()
      self.commit_buffer = 0
