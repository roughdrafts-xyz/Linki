import sys
from commands.init import init
from commands.publish import publish

try:
    command = sys.argv[1]

    if(command == 'init'):
        init()
    elif(command == 'publish'):
        publish()
    else:
        raise IndexError
except IndexError:
    print('Help Script')
