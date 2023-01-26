from os import chdir, remove, listdir
from sigil.commandInterfaces.cli.init import init
from sigil.commandInterfaces.cli.publish import publish
from sigil.commandInterfaces.cli.checkout import checkout
from tempfile import TemporaryDirectory


def getInitializedDirectory():
    dir = TemporaryDirectory()
    chdir(dir.name)
    init(quiet=True)
    return dir


def getPopulatedDirectory():
    dir = getInitializedDirectory()
    with open('hello_world.md', 'x') as file:
        file.write('Hello World!')
    return dir


def getSeededDirectory():
    dir = getPopulatedDirectory()
    publish()
    remove('hello_world.md')
    return dir


def getCheckedOutDirectory():
    dir = getSeededDirectory()
    checkout()
    return dir


def getVeryPopulatedRepo(n=100, dir=None):
    if (dir == None):
        dir = getInitializedDirectory()
    start = len(listdir('.sigil/refs/'))
    end = start+n
    for i in range(start, end):
        with open('hello_world.md', 'w') as file:
            file.write(str(i))
        publish()
    return dir
