import unittest
import os
from sigil.tests.helpers import getCheckedOutDirectory
from sigil.cli.commands.view import view
from sigil.editingInterfaces.FileSystem import FileSystem
from sigil.cli.commands.publish import publish


class TestViewCommand(unittest.TestCase):
    def setUp(self):
        self.dir = getCheckedOutDirectory()
        self.sfs = FileSystem()
        os.chdir(self.dir.name)
        self.sfs.connect()

    def tearDown(self):
        self.dir.cleanup()

    def test_should_display_bytes(self):
        refid = self.sfs.getRefid('hello_world.md')
        with open('hello_world.md', 'rb') as file:
            original_bytes = file.read()
        with open('hello_world.md', 'w') as file:
            file.write('Goodnight Moon')
        publish()
        with open('hello_world.md', 'w') as file:
            file.write('Hello Moon')
        publish()
        ref_bytes = view(refid)
        self.assertEqual(original_bytes, ref_bytes)
