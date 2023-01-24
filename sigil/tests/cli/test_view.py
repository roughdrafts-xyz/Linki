import os
import unittest
from sigil.commandInterfaces.cli.publish import publish
from sigil.commandInterfaces.cli.view import view
from sigil.editingInterfaces.FileSystem import FileSystem
from sigil.tests.helpers import getCheckedOutDirectory


class TestViewCommand(unittest.TestCase):
    def setUp(self):
        self.dir = getCheckedOutDirectory()
        self.sfs = FileSystem()
        os.chdir(self.dir.name)

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

    def test_should_display_center_edit(self):
        with open('hello_world.md', 'w') as file:
            file.write('Goodnight Moon')
        publish()
        refid = self.sfs.getRefid('hello_world.md')
        with open('hello_world.md', 'rb') as file:
            original_bytes = file.read()
        with open('hello_world.md', 'w') as file:
            file.write('Hello Moon')
        publish()
        ref_bytes = view(refid)
        self.assertEqual(original_bytes, ref_bytes)


if __name__ == '__main__':
    unittest.main(buffer=True)
