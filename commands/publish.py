import sqlite3
from sys import exit


def publish():
    try:
        con = sqlite3.connect("fil:./sigil/sigil.db?mode=rw", uri=True)
    except sqlite3.OperationalError:
        print("sigil database note found, please run `sigil init`")
        exit(0)

    cur = con.cursor()
