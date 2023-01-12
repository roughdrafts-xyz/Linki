import sys
from commands.init import init

try:
    command = sys.argv[1]

    if(command == 'init'):
        init()
    else:
        raise IndexError
except IndexError:
    print('Help Script')
