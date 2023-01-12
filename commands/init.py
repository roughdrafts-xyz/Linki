import sqlite3
from os import mkdir
from sys import exit


def init():
    try:
        mkdir('./.sigil')
    except FileExistsError:
        print('.sigil directory already exists.')
        exit(0)
    con = sqlite3.connect('./.sigil/sigil.db')
    cur = con.cursor()
    cur.execute("""
    --sql
    /**
    * refid - reference id - generated from the diff+prefid+rrefid+kind
    * prefid - parent reference id - which row was this diffed off of?
    * diff - changes made to the prefid (apparently this has the pathname, huh)
    */
    CREATE TABLE IF NOT EXISTS reflog(
      refid NOT NULL PRIMARY KEY,
      prefid NOT NULL,
      diff NOT NULL
    ) WITHOUT ROWID
    --endsql
    """)

    cur.execute("""
    --sql
    /**
    * refid - parent reference id - which row was this diffed off of?
    * inode - populated during hydration, used for publishing
    * pathname - path to file
    * payload - the latest version with all edits
    */ 
    CREATE TABLE IF NOT EXISTS head(
      refid NOT NULL PRIMARY KEY,
      inode NOT NULL UNIQUE,
      ctimeMs NOT NULL,
      pathname NOT NULL,
      payload NOT NULL
    ) WITHOUT ROWID
    --endsql
    """)

    # TODO Comment system that cares about the refid

    print('.sigil directory initiated')
