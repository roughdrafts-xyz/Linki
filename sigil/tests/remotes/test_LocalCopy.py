import unittest
import os
from sigil.repo.Repo import Repo
from sigil.tests.helpers import getCheckedOutDirectory
from sigil.remoteInterfaces.LocalCopy import LocalCopy
from tempfile import TemporaryDirectory


class TestLocalCopy(unittest.TestCase):
    def setUp(self):
        self.src = getCheckedOutDirectory()
        os.chdir(self.src.name)
        self.repo = Repo()
        self.remote = LocalCopy(self.src.name)

        self.dst = TemporaryDirectory()
        os.chdir(self.dst.name)

    def tearDown(self):
        self.src.cleanup()
        self.dst.cleanup()

    def test_does_bare_copy(self):
        os.chdir(self.src.name)
        srcObjects = os.listdir('.sigil/refs/')
        srcRepo = os.listdir('.sigil/')

        self.remote.clone(self.dst.name, bare=True)

        os.chdir(self.dst.name)
        dstObjects = os.listdir('./refs/')
        dstRepo = os.listdir('.')

        srcObjects.sort()
        dstObjects.sort()

        # Working Directory should be empty
        self.assertNotEqual(dstObjects, [])

        # Should only copy ref objects
        self.assertEqual(srcObjects, dstObjects)

        # Should only copy refs and sigil.db
        self.assertNotEqual(srcRepo, dstRepo)
        self.assertIn('sigil.db', dstRepo)

    def test_does_messy_copy(self):
        os.chdir(self.src.name)
        srcObjects = os.listdir('.sigil/refs')
        srcFiles = os.listdir('.')

        self.remote.clone(self.dst.name)

        os.chdir(self.dst.name)
        dstObjects = os.listdir('.sigil/refs')
        dstFiles = os.listdir('.')

        srcObjects.sort()
        dstObjects.sort()

        srcFiles.sort()
        dstFiles.sort()
        self.assertEqual(srcObjects, dstObjects)
        self.assertEqual(srcFiles, dstFiles)
