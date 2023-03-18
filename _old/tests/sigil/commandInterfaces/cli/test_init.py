import unittest
import os
from sigili.commandInterfaces.cli.init import init
from sigili.tests.helpers import getInitializedDirectory
from pathlib import Path


class TestInitCommand(unittest.TestCase):
    def setUp(self):
        self.dir = getInitializedDirectory()

    def tearDown(self):
        self.dir.cleanup()

    def test_file_structure(self):
        # TODO Document the whole repo structure. 3 Weeks later and I've totally forgotten it.
        files = os.listdir(Path(self.dir.name).joinpath('.sigil'))

        expected_files = ['refs', 'sigil.db', 'shadow_fs.db']
        self.assertCountEqual(files, expected_files)

    def test_should_not_init_twice(self):
        with self.assertRaises(FileExistsError):
            init(self.dir.name)


if __name__ == '__main__':
    unittest.main(buffer=True)
