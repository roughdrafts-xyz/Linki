import os
from sigil.cli.commands.init import init
from sigil.cli.commands.publish import publish
from sigil.cli.commands.checkout import checkout
from tempfile import TemporaryDirectory


def getInitializedDirectory():
    dir = TemporaryDirectory()
    os.chdir(dir.name)
    init()
    return dir


def getPopulatedDirectory():
    dir = getInitializedDirectory()
    with open('hello_world.md', 'x') as file:
        file.write('Hello World!')
    return dir


def getSeededDirectory():
    dir = getPopulatedDirectory()
    publish()
    os.remove('hello_world.md')
    return dir


def getCheckedOutDirectory():
    dir = getSeededDirectory()
    checkout()
    return dir
