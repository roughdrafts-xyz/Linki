import sqlite3
from os import mkdir
from sys import exit
import pathlib


def init():
    try:
        mkdir('./.sigil')
    except FileExistsError:
        print('.sigil directory already exists.')
        exit(0)
    con = sqlite3.connect(':memory:')
    con.execute("""
    --sql
    /**
    * refid - reference id - generated from the diff+prefid+rrefid+kind
    * pathname - where to put the file or url lookup or whatever
    * content - the actual article
    */
    CREATE TABLE IF NOT EXISTS articles (
      refid NOT NULL PRIMARY KEY,
      pathname NOT NULL,
      content NOT NULL
    ) WITHOUT ROWID
    --endsql
    """)

    con.execute("""
    --sql
    /**
    * crefid - child reference id - which row updated off of this?
    * prefid - parent reference id - which row was this updated from?
    * pathname - where to put the file or url lookup or whatever
    * content - the actual article
    */
    CREATE TABLE IF NOT EXISTS edit_log (
      crefid NOT NULL PRIMARY KEY,
      prefid NOT NULL,
      pathname NOT NULL,
      content NOT NULL
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
    CREATE TRIGGER preventNoOpUpdates BEFORE UPDATE ON articles 
    WHEN (new.pathname == old.pathname AND new.content == old.content)
    BEGIN
      SELECT RAISE(ABORT, 'refid must be changed');
    END
    --endsql
    """)

    con.execute("""
    --sql
    CREATE TRIGGER updateEditLogAfterUpdate AFTER UPDATE ON articles
    BEGIN
      INSERT INTO edit_log VALUES(new.refid, old.refid, old.pathname, old.content);
    END
    --endsql
    """)

    # TODO Comment system that cares about the refid

    con.enable_load_extension(True)
    this_path = pathlib.Path(__file__).parent
    zstd_path = this_path.joinpath('../deps/zstd_vfs')
    con.load_extension(str(zstd_path))
    con.execute("""
    --sql
    VACUUM INTO 'file:./.sigil/sigil.db?vfs=zstd'
    --endsql
    """)

    print('.sigil directory initiated')
