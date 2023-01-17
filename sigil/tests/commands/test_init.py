import unittest
import os
from glob import glob
from sigil.tests.helpers import getInitializedDirectory
from sigil.cli.init import init


class TestInitCommand(unittest.TestCase):
    def setUp(self):
        self.dir = getInitializedDirectory()
        os.chdir(self.dir.name)

    def tearDown(self):
        self.dir.cleanup()

    def test_file_structure(self):
        files = glob(pathname='**', recursive=True, include_hidden=True)
        expected_files = ['.sigil', '.sigil/refs',
                          '.sigil/sigil.db', '.sigil/shadow_fs.db']
        self.assertEqual(files, expected_files)

    def test_should_not_init_twice(self):
        with self.assertRaises(SystemExit):
            init()


if __name__ == '__main__':
    unittest.main(buffer=True)
