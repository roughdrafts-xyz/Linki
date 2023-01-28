
import os
import unittest
from sigil.commandInterfaces.cli.history import getFormattedHistory
from sigil.commandInterfaces.cli.publish import publish
from sigil.editingInterfaces.FileSystem import FileSystem
from sigil.tests.helpers import getCheckedOutDirectory


class TestHistoryCommand(unittest.TestCase):
    def setUp(self):
        self.dir = getCheckedOutDirectory()
        self.sfs = FileSystem()
        os.chdir(self.dir.name)

    def tearDown(self):
        self.dir.cleanup()

    def _mockFormatHistoryRow(self, refid):
        return f'{refid[0:6]}\thello_world.md'

    def test_should_display_history_exclusively(self):
        refids = [self.sfs.getRefid('hello_world.md')]
        with open('hello_world.md', 'w') as file:
            file.write('Goodnight Moon')
        publish()
        refids.append(self.sfs.getRefid('hello_world.md'))
        with open('hello_world.md', 'w') as file:
            file.write('Hello Moon')
        publish()
        refids.append(self.sfs.getRefid('hello_world.md'))
        with open('red_car.md', 'x') as file:
            file.write('The Car is Red.')
        publish()

        history = list(getFormattedHistory('hello_world.md'))
        mockHistory = list(map(self._mockFormatHistoryRow, refids))

        self.assertEqual(history, mockHistory)

        car_refid = self.sfs.getRefid('red_car.md')
        self.assertNotIn(car_refid, history)


if __name__ == '__main__':
    unittest.main(buffer=True)
