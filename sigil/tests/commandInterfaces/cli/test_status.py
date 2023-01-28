import os
import unittest
from sigil.commandInterfaces.cli.status import getStagedChanges
from sigil.tests.helpers import getCheckedOutDirectory


class TestStatusCommand(unittest.TestCase):
    def setUp(self):
        self.dir = getCheckedOutDirectory()
        os.chdir(self.dir.name)

    def tearDown(self):
        self.dir.cleanup()

    def test_edited_repo_hasChangedFiles(self):
        with open('hello_world.md', 'w') as file:
            file.write('Hello Moon!')
        changedFiles = getStagedChanges()
        self.assertEqual(changedFiles, ['hello_world.md'])

    def test_unedited_repo_hasNoChangedFiles(self):
        changedFiles = getStagedChanges()
        self.assertEqual(changedFiles, [])

    def test_edited_file_hasChangedFiles(self):
        with open('hello_world.md', 'w') as file:
            file.write('Hello Moon!')
        changedFiles = getStagedChanges('hello_world.md')
        self.assertEqual(changedFiles, ['hello_world.md'])

    def test_unedited_file_hasNoChangedFiles(self):
        changedFiles = getStagedChanges('hello_world.md')
        self.assertEqual(changedFiles, [])

    def test_new_file(self):
        with open('goodnight_moon.md', 'x') as file:
            file.write('Goodnight Moon.')
        changedFiles = getStagedChanges()
        self.assertEqual(changedFiles, ['goodnight_moon.md'])


if __name__ == '__main__':
    unittest.main(buffer=True)
