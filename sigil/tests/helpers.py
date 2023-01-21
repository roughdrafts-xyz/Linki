import os
from sigil.cli.commands.init import init
from sigil.cli.commands.publish import publish
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


def getSeededDirectory():
    dir = getPopulatedDirectory()
    publish()
    os.remove('hello_world.md')
    return dir
