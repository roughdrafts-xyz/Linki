class ShadowFileSystem():
    makeFileSystem = """
    --sql
    /**
    * refid - parent reference id - which row was this diffed off of?
    * inode - populated during hydration, used for publishing
    * ctimeMs - populated during hydration, used for publishing
    * pathname - where to put the file or url lookup or whatever
    * content - the actual article
    */ 
    CREATE TABLE IF NOT EXISTS shadow_filesystem(
      refid NOT NULL PRIMARY KEY,
      inode NOT NULL UNIQUE,
      ctimeMs NOT NULL,
    ) WITHOUT ROWID
    --endsql
    """

    def doesInodeExist(self, ino):
        _inoExistsCursor = self.db.execute("""
        --sql
        SELECT COUNT(inode) FROM shadow_filesystem WHERE inode=? LIMIT 1
        --endsql
        """, (ino))
        _inodeCount = _inoExistsCursor.fetchone()[0]
        return _inodeCount > 0
