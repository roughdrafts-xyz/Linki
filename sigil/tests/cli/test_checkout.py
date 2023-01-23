import unittest
from sigil.tests.helpers import getCheckedOutDirectory
from sigil.commandInterfaces.cli.checkout import checkout
import os


class TestCheckoutCommand(unittest.TestCase):
    def setUp(self):
        self.dir = getCheckedOutDirectory()
        os.chdir(self.dir.name)

    def tearDown(self):
        self.dir.cleanup()

    def test_does_checkout(self):
        fs_contents = os.listdir()
        self.assertIn('hello_world.md', fs_contents)
        with open('hello_world.md') as file:
            self.assertEqual(file.read(), 'Hello World!')


if __name__ == '__main__':
    unittest.main(buffer=True)
