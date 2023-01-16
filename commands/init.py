import sqlite3
from os import mkdir
from sys import exit
import pathlib


def init():
    try:
        mkdir('./.sigil')
        # sigil folder also has a folder of multiple zstd'd files that represent the various articles and their deltas and edit historys. The database merely tracks what refids care about each other. Every file is stored as a refid.
    except FileExistsError:
        print('.sigil directory already exists.')
        exit(0)

    con = sqlite3.connect('./.sigil/sigil.db')
    con.execute("""
    --sql
    /**
    * articles holds the most up to date version of every active article for conveinence.
    * refid - reference id - generated from the diff+prefid+rrefid+kind
    * pathname - where to put the file or url lookup or whatever
    */
    CREATE TABLE IF NOT EXISTS articles (
      refid NOT NULL PRIMARY KEY,
      pathname NOT NULL,
    ) WITHOUT ROWID
    --endsql
    """)

    con.execute("""
    --sql
    /**
    * pathnames holds every refid's pathname, since articles doesn't have any historical data and I don't want to have the zstd'd files to have anything other than their content in them. 
    * refid - reference id - generated from the diff+prefid+rrefid+kind
    * pathname - where to put the file or url lookup or whatever
    */
    CREATE TABLE IF NOT EXISTS refid_info (
      refid NOT NULL PRIMARY KEY,
      pathname NOT NULL,
    ) WITHOUT ROWID
    --endsql
    """)

    con.execute("""
    --sql
    /**
    * this stores the edit history of an article, letting every article have a history of edits that can be rolled back to or viewed
    * this doesn't care about the *order* because it'll automatically be assumed based off of branching.
    * crefid - child reference id - which row updated off of this?
    * it should be impossible for a crefid to ever clash because of how the refid is hashed
    * prefid - parent reference id - which row was this updated from?
    * this is not unique because multiple edits can come from the same refid
    */
    CREATE TABLE IF NOT EXISTS edit_log (
      crefid NOT NULL PRIMARY KEY,
      prefid NOT NULL PRIMARY KEY
    ) WITHOUT ROWID
    --endsql
    """)

    con.execute("""
    --sql
    CREATE TRIGGER preventDuplicateRefIds BEFORE UPDATE ON articles WHEN new.refid == old.refid
    BEGIN
      SELECT RAISE(ABORT, 'refid must be changed');
    END
    --endsql
    """)

    con.execute("""
    --sql
    CREATE TRIGGER updateEditLogAfterUpdate AFTER UPDATE ON articles
    BEGIN
    --sql
      INSERT INTO edit_log VALUES(new.refid, old.refid) ON CONFLICT DO NOTHING;
    --sql
      INSERT INTO refid_info VALUES(new.refid, new.pathname) ON CONFLICT DO NOTHING;
    END
    """)

    print('.sigil directory initiated')
