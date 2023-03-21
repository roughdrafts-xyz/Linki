from pathlib import Path
import sqlite3


def getRepoPath(pathname=None, bare=False):
    if pathname is None:
        pathname = Path.cwd()
    if not bare:
        path = Path(pathname).joinpath('.sigil')
    else:
        path = Path(pathname)

    return path.resolve()


def init_repo(pathname=None, bare=False):
    path = getRepoPath(pathname=pathname, bare=bare)
    if not path.exists():
        path.mkdir()
    elif path.exists() and len(list(path.iterdir())) > 0:
        raise FileExistsError
    path.joinpath('refs').mkdir()
    con = sqlite3.connect(path.joinpath("sigil.db").resolve())
    # sigil folder also has a folder of multiple zstd'd files that represent the various articles and their deltas and edit historys. The database merely tracks what refids care about each other. Every file is stored as a refid.

    con.execute("""
    --sql
    /**
    * articles holds the most up to date version of every active article for conveinence.
    * refid - reference id - generated from the diff+prefid+rrefid+kind
    * pathname - where to put the file or url lookup or whatever
    */
    CREATE TABLE IF NOT EXISTS articles (
      refid NOT NULL UNIQUE,
      pathname NOT NULL UNIQUE,
      PRIMARY KEY(refid, pathname)
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
      pathname NOT NULL
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
      crefid NOT NULL,
      prefid NOT NULL,
      PRIMARY KEY(crefid, prefid)
    ) WITHOUT ROWID
    --endsql
    """)

    con.execute("""
    --sql
    CREATE INDEX edit_log_back ON edit_log(crefid, prefid);
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
    --endsql
    """)

    con.execute("""
    --sql
    /**
    */
    CREATE TABLE IF NOT EXISTS remotes (
      pathname PRIMARY KEY,
      style
      -- TODO add type eventually, depending on whether or not automatically determining type based on pathname is easier.
    ) WITHOUT ROWID
    --endsql
    """)