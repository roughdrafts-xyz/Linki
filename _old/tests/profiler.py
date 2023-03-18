import cProfile
from sigili.tests.helpers import getInitializedDirectory, populateRepo

dir = getInitializedDirectory()
cProfile.run("populateRepo(256)")
dir.cleanup()
