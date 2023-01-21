import unittest
import os
from sigil.tests.helpers import getCheckedOutDirectory
from sigil.cli.commands.status import hasChanged


class TestStatusCommand(unittest.TestCase):
    def setUp(self):
        self.dir = getCheckedOutDirectory()
        os.chdir(self.dir.name)

    def tearDown(self):
        self.dir.cleanup()

    def test_edited_repo_hasChanged(self):
        _hasChanged = hasChanged()
        self.assertTrue(_hasChanged)

    def test_unedited_repo_hasNotChanged(self):
        _hasChanged = hasChanged()
        self.assertFalse(_hasChanged)

    def test_edited_file_hasChanged(self):
        _hasChanged = hasChanged('hello_world.md')
        self.assertTrue(_hasChanged)

    def test_unedited_file_hasNotChanged(self):
        _hasChanged = hasChanged('hello_world.md')
        self.assertFalse(_hasChanged)


if __name__ == '__main__':
    unittest.main(buffer=True)
