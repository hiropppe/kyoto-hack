#!/usr/bin/env python

import sys
import os
if len(sys.argv) < 2:
  db = os.path.dirname(os.path.abspath(__file__)) + '/../geo.db'
else:
  db = sys.argv[1]

import sqlite3

db = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
sqlite3.dbapi2.converters['DATETIME'] = sqlite3.dbapi2.converters['TIMESTAMP']

db.execute("""
  CREATE TABLE IF NOT EXISTS Geo (
    geo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    uri TEXT,
    name TEXT,
    address TEXT,
    geo_type INTEGER,
    geo_hash TEXT,
    pref_code TEXT,
    region_code TEXT,
    latitude REAL,
    longitude REAL,
    coordinates TEXT,
    insert_datetime DATETIME DEFAULT (DATETIME('now', 'localtime')),
    update_datetime DATETIME DEFAULT (DATETIME('now', 'localtime')),
    delete_flag INTEGER DEFAULT 0
  )
""")

db.execute("""
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

db.execute("""
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
    latitude REAL,
    longitude REAL,
    coordinates TEXT,
    insert_datetime DATETIME DEFAULT (DATETIME('now', 'localtime')),
    update_datetime DATETIME DEFAULT (DATETIME('now', 'localtime')),
    delete_flag INTEGER DEFAULT 0,
    FOREIGN KEY(geo_id) REFERENCES Geo(geo_id)
  )
""")

db.close()
