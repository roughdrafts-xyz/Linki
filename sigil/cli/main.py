import sys
from sigil.cli.commands.init import init
from sigil.cli.commands.publish import publish

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
