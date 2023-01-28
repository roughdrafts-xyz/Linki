import os
import unittest
from glob import glob
from sigil.commandInterfaces.cli.init import init
from sigil.tests.helpers import getInitializedDirectory


class TestInitCommand(unittest.TestCase):
    def setUp(self):
        self.dir = getInitializedDirectory()
        os.chdir(self.dir.name)

    def tearDown(self):
        self.dir.cleanup()

    def test_file_structure(self):
        files = glob(pathname='.sigil/**', recursive=True)
        expected_files = ['.sigil/', '.sigil/refs',
                          '.sigil/sigil.db', '.sigil/shadow_fs.db']
        self.assertEqual(files, expected_files)

    def test_should_not_init_twice(self):
        with self.assertRaises(FileExistsError):
            init()


if __name__ == '__main__':
    unittest.main(buffer=True)
