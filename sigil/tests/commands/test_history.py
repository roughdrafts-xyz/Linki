
import unittest
import os
from sigil.tests.helpers import getCheckedOutDirectory
from sigil.cli.commands.history import getFormattedHistory
from sigil.editingInterfaces.FileSystem import FileSystem
from sigil.cli.commands.publish import publish


class TestHistoryCommand(unittest.TestCase):
    def setUp(self):
        self.dir = getCheckedOutDirectory()
        self.sfs = FileSystem()
        os.chdir(self.dir.name)
        self.sfs.connect()

    def tearDown(self):
        self.dir.cleanup()

    def _mockFormatHistoryRow(self, refid):
        return refid

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

        history = list(getFormattedHistory(refids[-1]))
        mockHistory = list(map(self._mockFormatHistoryRow, refids))

        self.assertEqual(history, mockHistory)

        car_refid = self.sfs.getRefid('red_car.md')
        self.assertNotIn(car_refid, history)


if __name__ == '__main__':
    unittest.main(buffer=True)
