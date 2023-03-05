import unittest
import os
from sigil.repo.LocalRepo.LocalRepo import Repo
from sigil.tests.helpers import getCheckedOutDirectory, getClonedDirectory


class TestLocalCopyConfigure(unittest.TestCase):
    def setUp(self):
        self.src = getCheckedOutDirectory()
        os.chdir(self.src.name)

        self.dst = getClonedDirectory(self.src.name)
        os.chdir(self.dst.name)

        self.repo = Repo()

    def tearDown(self):
        self.src.cleanup()
        self.dst.cleanup()

    def test_clone_should_have_remote(self):
        # Check db to see if it has a remote
        rows = list(self.repo.getRemotes())
        remotes = [row["pathname"] for row in rows]
        expected = [self.src.name]
        self.assertEqual(remotes, expected)

    def test_should_add_remote(self):
        # Make 3rd Repo and add that as a new remote?
        # Check db to see if db lists every remote
        third_repo = getClonedDirectory(self.src.name)
        self.repo.addRemote(third_repo.name)
        rows = list(self.repo.getRemotes())
        remotes = [row["pathname"] for row in rows]
        expected = [self.src.name, third_repo.name]

        remotes.sort()
        expected.sort()

        self.assertEqual(remotes, expected)
        third_repo.cleanup()

    def test_should_del_remote(self):
        # Remove the clone's remote and see if the db still lists it
        self.repo.delRemote(self.src.name)
        rows = list(self.repo.getRemotes())
        remotes = [row["pathname"] for row in rows]
        expected = []
        self.assertEqual(remotes, expected)
