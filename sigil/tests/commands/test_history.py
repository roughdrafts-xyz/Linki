
import unittest
import os
from sigil.tests.helpers import getCheckedOutDirectory
from sigil.cli.commands.history import getFormattedHistory
from sigil.editingInterfaces.FileSystem import FileSystem
from sigil.cli.commands.publish import publish


class TestHistoryCommand(unittest.TestCase):
    def setUp(self):
        self.dir = getCheckedOutDirectory()
        self.sfs = FileSystem()
        os.chdir(self.dir.name)
        self.sfs.connect()

    def tearDown(self):
        self.dir.cleanup()

    def test_should_display_history(self):
        with open('hello_world.md', 'w') as file:
            file.write('Goodnight Moon')
        publish()
        with open('hello_world.md', 'w') as file:
            file.write('Hello Moon')
        publish()
        refid = self.sfs.getRefid('hello_world.md')
        history = getFormattedHistory(refid)
        self.assertEqual(list(history), [])


if __name__ == '__main__':
    unittest.main(buffer=True)
