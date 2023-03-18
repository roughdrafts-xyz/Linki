import os
import unittest
from pathlib import Path
from sigili.tests.helpers import getCheckedOutDirectory


class TestCheckoutCommand(unittest.TestCase):
    def setUp(self):
        self.dir = getCheckedOutDirectory()

    def tearDown(self):
        self.dir.cleanup()

    def test_does_checkout(self):
        fs_contents = os.listdir(self.dir.name)
        self.assertIn('hello_world.md', fs_contents)
        file = Path(self.dir.name).joinpath('hello_world.md').read_text()
        self.assertEqual(file, 'Hello World!')


if __name__ == '__main__':
    unittest.main(buffer=True)
