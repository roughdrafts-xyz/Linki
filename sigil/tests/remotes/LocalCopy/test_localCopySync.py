import unittest
import os
from sigil.repo.LocalRepo.LocalRepo import Repo
from sigil.commandInterfaces.cli.publish import publish
from sigil.tests.helpers import getCheckedOutDirectory, getClonedDirectory
from sigil.repo.remotes import sync_all_remotes
from pathlib import Path


class TestLocalCopySync(unittest.TestCase):
    def setUp(self):
        self.remoteFolder = getCheckedOutDirectory()
        self.remote = Path(self.remoteFolder.name)

        self.remoteRepo = Repo(str(self.remote.resolve()))
        self.remoteRef = self.remote.joinpath('.sigil', 'refs')

        self.localFolder = getClonedDirectory(self.remoteFolder.name)
        self.local = Path(self.localFolder.name)

        self.localRepo = Repo(str(self.local.resolve()))
        self.localRef = self.local.joinpath('.sigil', 'refs')

    def tearDown(self):
        self.remoteFolder.cleanup()
        self.localFolder.cleanup()

    def test_remote_sync_unaware_of_local_should_not_equal(self):
        os.chdir(self.local.resolve())

        # update local file
        self.file = self.local.joinpath('hello_world.md')
        self.file.write_text('Hello Moon!')

        publish()

        # run sync on remote
        sync_all_remotes(self.remoteRepo)

        # check for matching refs folders
        localFiles = os.listdir(self.localRef.resolve())
        remoteFiles = os.listdir(self.remoteRef.resolve())

        localFiles.sort()
        remoteFiles.sort()

        self.assertNotEqual(localFiles, remoteFiles)

    def test_local_sync_should_updated_remotes(self):
        os.chdir(self.local.resolve())

        # update local file
        self.file = self.local.joinpath('hello_world.md')
        self.file.write_text('Hello Moon!')

        publish()

        # run sync on local
        sync_all_remotes(self.localRepo)

        # check for matching refs folders
        localFiles = os.listdir(self.localRef.resolve())
        remoteFiles = os.listdir(self.remoteRef.resolve())

        self.assertCountEqual(localFiles, remoteFiles)
        pass

    def test_should_sync_new_files_from_local_to_remote_via_remote(self):
        # create local file
        # run sync on remote
        # check for matching refs folders
        pass

    def test_should_sync_new_files_from_local_to_remote_via_local(self):
        # create local file
        # run sync on local
        # check for matching refs folders
        pass

    def test_should_sync_existing_files_from_remote_to_local_via_remote(self):
        # update remote file
        # run sync on remote
        # check for matching refs folders
        pass

    def test_should_sync_existing_files_from_remote_to_local_via_local(self):
        # update remote file
        # run sync on local
        # check for matching refs folders
        pass

    def test_should_sync_new_files_from_remote_to_local_via_remote(self):
        # create remote file
        # run sync on remote
        # check for matching refs folders
        pass

    def test_should_sync_new_files_from_remote_to_local_via_local(self):
        # create remote file
        # run sync on local
        # check for matching refs folders
        pass
