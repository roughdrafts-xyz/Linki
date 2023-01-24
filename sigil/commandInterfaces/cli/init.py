import sqlite3
from sigil.repo.Init import init_repo


def init():
    try:
        init_repo()
        sqlite3.connect('.sigil/shadow_fs.db')
        print('.sigil directory initiated')
    except FileExistsError:
        print('.sigil directory already exists.')
        exit(0)
