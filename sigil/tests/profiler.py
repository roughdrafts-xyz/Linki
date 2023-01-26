import cProfile
from sigil.tests.helpers import getInitializedDirectory, populateRepo

dir = getInitializedDirectory()
cProfile.run("populateRepo(256)")
dir.cleanup()
