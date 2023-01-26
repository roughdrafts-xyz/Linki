import sys
from sigil.commandInterfaces.cli.init import init
from sigil.commandInterfaces.cli.publish import publish

try:
    command = sys.argv[1]

    if (command == 'init'):
        init()
    elif (command == 'publish'):
        publish()
    else:
        raise IndexError
except IndexError:
    print('Help Script')