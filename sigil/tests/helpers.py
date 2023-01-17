
from sigil.commands.init import init
from tempfile import TemporaryDirectory
import os


def getInitializedDirectory():
    dir = TemporaryDirectory()
    os.chdir(dir.name)
    init()
    return dir
