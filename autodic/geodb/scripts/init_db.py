#!/usr/bin/env python

import sys
import os
if len(sys.argv) < 2:
  db = os.path.dirname(os.path.abspath(__file__)) + '/../geo.db'
else:
  db = sys.argv[1]


from pysqlite2 import dbapi2 as sqlite

conn = sqlite.connect(db, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
sqlite.converters['DATETIME'] = sqlite.converters['TIMESTAMP']

conn.enable_load_extension(True)
conn.execute("SELECT load_extension('/usr/local/lib/mod_spatialite.so')")
conn.execute("SELECT InitSpatialMetaData()")

conn.execute("""
  CREATE TABLE IF NOT EXISTS Geo (
    geo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    uri TEXT,
    name TEXT,
    address TEXT,
    geo_type INTEGER,
    geo_hash TEXT,
    pref_code TEXT,
    region_code TEXT,
    coordinates TEXT,
    insert_datetime DATETIME DEFAULT (DATETIME('now', 'localtime')),
    update_datetime DATETIME DEFAULT (DATETIME('now', 'localtime')),
    delete_flag INTEGER DEFAULT 0
  )
""")

conn.execute("""
  CREATE TABLE IF NOT EXISTS Alias (
    alias_id INTEGER PRIMARY KEY AUTOINCREMENT,
    geo_id INTEGER,
    name TEXT,
    insert_datetime DATETIME DEFAULT (DATETIME('now', 'localtime')),
    update_datetime DATETIME DEFAULT (DATETIME('now', 'localtime')),
    delete_flag INTEGER DEFAULT 0,
    FOREIGN KEY(geo_id) REFERENCES Geo(geo_id)
  )
""")

conn.execute("""
  CREATE TABLE IF NOT EXISTS GeoCollection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    geo_id INTEGER,
    source_id TEXT,
    source_type TEXT,
    uri TEXT,
    name TEXT,
    address TEXT,
    geo_type INTEGER,
    geo_hash TEXT,
    pref_code TEXT,
    region_code TEXT,
    coordinates TEXT,
    insert_datetime DATETIME DEFAULT (DATETIME('now', 'localtime')),
    update_datetime DATETIME DEFAULT (DATETIME('now', 'localtime')),
    delete_flag INTEGER DEFAULT 0,
    FOREIGN KEY(geo_id) REFERENCES Geo(geo_id)
  )
""")

conn.execute("SELECT AddGeometryColumn('Geo', 'geo_point', 0, 'POINT', 'XY')")
conn.execute("SELECT AddGeometryColumn('GeoCollection', 'geo_point', 0, 'POINT', 'XY')")

conn.close()
