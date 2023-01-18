import os
from sigil.cli.commands.init import init
from tempfile import TemporaryDirectory


def getInitializedDirectory():
    dir = TemporaryDirectory()
    os.chdir(dir.name)
    init()
    return dir


def getPopulatedDirectory():
    dir = getInitializedDirectory()
    file = open('hello_world.md', 'x')
    file.write('Hello World!')
    file.close()
    return dir
