import unittest
import os
from sigili.old_repo.LocalRepo.LocalRepo import LocalRepo
from sigili.tests.helpers import getInitializedDirectory


class TestGenerateNewRefid(unittest.TestCase):
    def setUp(self):
        self.dir = getInitializedDirectory()
        self.repo = LocalRepo(self.dir.name)

    def tearDown(self):
        self.dir.cleanup()

    def test_refids_different_with_different_content(self):
        with open('hello_world.md', 'w') as file:
            file.write('Hello World!')

        with open('goodnight_moon.md', 'w') as file:
            file.write('Goodnight Moon!')

        hw_refid = self.repo._generateNewRefid('', 'hello_world.md')
        gm_refid = self.repo._generateNewRefid('', 'goodnight_moon.md')
        up_refid = self.repo._generateNewRefid(hw_refid, 'goodnight_moon.md')

        self.assertNotEqual(hw_refid, gm_refid)
        self.assertNotEqual(gm_refid, up_refid)
        self.assertNotEqual(hw_refid, up_refid)

    def test_refids_different_with_same_content(self):
        with open('hello_world.md', 'w') as file:
            file.write('Goodnight Moon!')

        with open('goodnight_moon.md', 'w') as file:
            file.write('Goodnight Moon!')

        hw_refid = self.repo._generateNewRefid('', 'hello_world.md')
        gm_refid = self.repo._generateNewRefid('', 'goodnight_moon.md')
        up_refid = self.repo._generateNewRefid(hw_refid, 'goodnight_moon.md')

        self.assertNotEqual(hw_refid, gm_refid)
        self.assertNotEqual(gm_refid, up_refid)
        self.assertNotEqual(hw_refid, up_refid)
