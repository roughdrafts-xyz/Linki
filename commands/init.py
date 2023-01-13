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
    * refid - reference id - generated from the diff+prefid+rrefid+kind
    * prefid - parent reference id - which row was this diffed off of?
    * pathname - where to put the file or url lookup or whatever
    * content - the actual article
    */
    CREATE TABLE IF NOT EXISTS edit_log (
      refid NOT NULL PRIMARY KEY,
      prefid NOT NULL,
      pathname NOT NULL,
      content NOT NULL
    ) WITHOUT ROWID
    --endsql
    """)

    con.execute("""
    --sql
    PRAGMA recursive_triggers = OFF
    --endsql
    """)

    con.execute("""
    --sql
    CREATE TRIGGER updateEditLogAfterUpdate AFTER UPDATE ON articles
    BEGIN
      INSERT INTO edit_log VALUES(new.refid, old.refid, new.pathname, new.content);
    END
    --endsql
    """)

    con.execute("""
    --sql
    CREATE TRIGGER preventEditLogInsert BEFORE INSERT ON edit_log
    BEGIN
      SELECT RAISE(ABORT, 'Edit Log is Read Only.');
    END
    --endsql
    """)

    con.execute("""
    --sql
    CREATE TRIGGER preventEditLogUpdate BEFORE UPDATE ON edit_log
    BEGIN
      SELECT RAISE(ABORT, 'Edit Log is Read Only.');
    END
    --endsql
    """)

    con.execute("""
    --sql
    CREATE TRIGGER preventEditLogDelete BEFORE DELETE ON edit_log
    BEGIN
      SELECT RAISE(ABORT, 'Edit Log is Read Only.');
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
