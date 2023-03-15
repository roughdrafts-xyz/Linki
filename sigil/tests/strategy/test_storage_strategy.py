import unittest
from sigil.data.ref import RefDetail
from sigil.strategy.storage import MemoryStorageStrategy


class TestMemoryStorageStrategy(unittest.TestCase):
    def setUp(self):
        self.remote = MemoryStorageStrategy()

    def test_does_add_and_get_bytes(self):
        helloWorld = b'Hello World'
        refId = self.remote.add_bytes(helloWorld)
        expected = helloWorld
        actual = self.remote.get_bytes(refId)
        self.assertEqual(expected, actual)

    def test_does_update_bytes_and_get_details(self):
        helloWorld = b'Hello World'
        goodnightMoon = b'Goodnight Moon'

        prefId = self.remote.add_bytes(helloWorld)
        refId = self.remote.update_bytes(refId=prefId, update=goodnightMoon)

        expected = RefDetail(refId=refId, prefId=prefId)
        actual = self.remote.get_details(refId)

        self.assertEqual(expected, actual)
        self.assertNotEqual(expected.refId, expected.prefId)
