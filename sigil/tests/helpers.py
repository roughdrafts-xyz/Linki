from os import chdir, remove, listdir
from sigil.commandInterfaces.cli.init import init
from sigil.commandInterfaces.cli.publish import publish
from sigil.commandInterfaces.cli.checkout import checkout
from tempfile import TemporaryDirectory


def getInitializedDirectory(bare=False):
    dir = TemporaryDirectory()
    chdir(dir.name)
    init(bare=bare)
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


def getClonedDirectory(src):
    from sigil.remoteInterfaces.LocalCopy import LocalCopy
    remote = LocalCopy(src)

    dir = TemporaryDirectory()

    remote.clone(dir.name)
    return dir


def populateRepo(n):
    start = len(listdir('.sigil/refs/'))
    end = start+n
    for i in range(start, end):
        with open('hello_world.md', 'wb') as file:
            file.write(i.to_bytes(1, byteorder='big'))
        publish()
