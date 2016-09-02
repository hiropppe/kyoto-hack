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
    geo_type TEXT,
    geo_hash TEXT,
    pref_code TEXT,
    region_code TEXT,
    modified INTEGER,
    insert_datetime DATETIME DEFAULT (DATETIME('now', 'localtime')),
    update_datetime DATETIME DEFAULT (DATETIME('now', 'localtime')),
    delete_flag INTEGER DEFAULT 0
  )
""")

conn.execute("""
  CREATE TABLE IF NOT EXISTS Alias (
    alias_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    geo_id INTEGER,
    extern_id TEXT,
    insert_datetime DATETIME DEFAULT (DATETIME('now', 'localtime')),
    update_datetime DATETIME DEFAULT (DATETIME('now', 'localtime')),
    delete_flag INTEGER DEFAULT 0,
    FOREIGN KEY(geo_id) REFERENCES Geo(geo_id),
    FOREIGN KEY(extern_id) REFERENCES GeoExtern(extern_id)
  )
""")

conn.execute("""
  CREATE TABLE IF NOT EXISTS GeoExtern (
    extern_id INTEGER PRIMARY KEY,
    data_hash TEXT,
    data_id TEXT,
    geo_id INTEGER,
    uri TEXT,
    name TEXT,
    address TEXT,
    geo_type TEXT,
    geo_hash TEXT,
    pref_code TEXT,
    region_code TEXT,
    datasource TEXT,
    insert_datetime DATETIME DEFAULT (DATETIME('now', 'localtime')),
    update_datetime DATETIME DEFAULT (DATETIME('now', 'localtime')),
    delete_flag INTEGER DEFAULT 0,
    FOREIGN KEY(geo_id) REFERENCES Geo(geo_id)
  )
""")

conn.execute("CREATE UNIQUE INDEX UNIQUE_IDX_Alias ON Alias(name, geo_id)")
conn.execute("CREATE UNIQUE INDEX UNIQUE_IDX_GEO_EXTERN ON GeoExtern(data_hash, data_id)")

conn.execute("SELECT AddGeometryColumn('Geo', 'geo_point', 0, 'POINT', 'XY')")
conn.execute("SELECT AddGeometryColumn('GeoExtern', 'geo_point', 0, 'POINT', 'XY')")

conn.close()
