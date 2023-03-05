import unittest
import os
from sigil.repo.LocalRepo.LocalRepo import Repo
from sigil.repo.remotes import clone
from sigil.tests.helpers import getCheckedOutDirectory, getInitializedDirectory


class TestLocalCopyClone(unittest.TestCase):
    def setUp(self):
        self.src = getCheckedOutDirectory()
        self.srcRepo = Repo(self.src.name)

    def tearDown(self):
        self.src.cleanup()

    def test_does_bare_copy(self):
        with getInitializedDirectory(bare=True) as dst:
            dstRepo = Repo(dst.name)
            os.chdir(self.src.name)
            srcObjects = os.listdir('.sigil/refs/')
            srcRepo = os.listdir('.sigil/')

            clone(self.repo, dstRepo)

            os.chdir(dst.name)
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

        clone(self.repo, self.dstRepo)

        os.chdir(self.dst.name)
        dstObjects = os.listdir('.sigil/refs')
        dstFiles = os.listdir('.')

        srcObjects.sort()
        dstObjects.sort()

        srcFiles.sort()
        dstFiles.sort()
        self.assertEqual(srcObjects, dstObjects)
        self.assertEqual(srcFiles, dstFiles)
