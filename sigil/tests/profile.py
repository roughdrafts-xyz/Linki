from os import listdir
from sigil.tests.helpers import getInitializedDirectory, populateRepo
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
    dir.cleanup()
    print(totalPublishes)
