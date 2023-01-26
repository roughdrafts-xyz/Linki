from os import listdir, remove
from sigil.tests.helpers import getInitializedDirectory, populateRepo
from sigil.commandInterfaces.cli.checkout import checkout
from sigil.repo.RefLog import _modifyFile
from time import time


if __name__ == '__main__':
    _time = 0.0
    i = 1
    totalPublishes = 1
    dir = getInitializedDirectory()
    populateRepo(totalPublishes)
    print('publishes', 'refs', 'time')
    while (_time < 1.0):
        start = time()
        populateRepo(i)
        end = time()
        _time = end-start
        print(i, len(listdir('.sigil/refs')), _time)
        totalPublishes += i
        i = i * 2
    print(totalPublishes)
    print('Cache info', _modifyFile.cache_info())
    remove('hello_world.md')
    _modifyFile.cache_clear()
    start = time()
    checkout()
    end = time()
    _time = end-start
    print('Time to checkout', _time)

    dir.cleanup()
