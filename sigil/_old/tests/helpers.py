from os import listdir
from sigil.commandInterfaces.cli.init import init
from sigil.commandInterfaces.cli.publish import publish
from sigil.commandInterfaces.cli.checkout import checkout
from tempfile import TemporaryDirectory
from pathlib import Path


def getInitializedDirectory(bare=False):
    dir = TemporaryDirectory()
    init(pathname=dir.name, bare=bare)
    return dir


def getPopulatedDirectory():
    dir = getInitializedDirectory()
    path = Path(dir.name).joinpath('hello_world.md')
    with open(path, 'x') as file:
        file.write('Hello World!')
    return dir


def getSeededDirectory():
    dir = getPopulatedDirectory()
    publish(pathname=dir.name)
    Path(dir.name).joinpath('hello_world.md').unlink()
    return dir


def getCheckedOutDirectory():
    dir = getSeededDirectory()
    checkout(pathname=dir.name)
    return dir


def getClonedDirectory(src):
    from sigil.old_repo.LocalRepo.LocalRepo import LocalRepo
    from sigil.old_repo.remotes import clone
    remoteRepo = LocalRepo(src)

    dir = getInitializedDirectory()
    localRepo = LocalRepo(dir.name)

    clone(remoteRepo, localRepo)
    return dir


def populateRepo(n):
    start = len(listdir('.sigil/refs/'))
    end = start+n
    for i in range(start, end):
        with open('hello_world.md', 'wb') as file:
            file.write(i.to_bytes(1, byteorder='big'))
        publish()
