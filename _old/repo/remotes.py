# remotes have three directions
# -sync (push then pull)
# -push (outgoing updates only)
# -pull (incoming updates only)
# direction is relative to the local. IE a pull remote is a remote that you receive updates from when you sync to it.
# pushing doesn't exist intentionally, uni-directional design is simpler.
from sigili.old_repo.abc.Repo import Repo


class _RepoGroup():
    def __init__(self, local, remote):
        self._local = local
        self._remote = remote

    def copyRef(self, refId):
        try:
            refData = self._remote.refLog.getRefItem(refId)
            self._local.refLog.addRefItem(refData)
            return True
        except Exception:
            return False


def copy(local: Repo, remote: Repo, missingRefs: set):
    repoGroup = _RepoGroup(local, remote)
    # TODO this needs to do something with the True/False like reporting or something. Maybe just return it up the chain and let something else handle that?
    return all(map(repoGroup.copyRef, missingRefs))


def pull(local: Repo, remote: Repo):
    # Get Remote Refs
    remoteRefs = remote.getRefIds()
    localRefs = local.getRefIds()

    # Compare Refs
    missingRefs = remoteRefs.difference(localRefs)

    # Copy Missing Refs
    copy(local, remote, missingRefs)
    pass


def sync(local: Repo, remote: Repo):
    pull(remote, local)  # push
    pull(local, remote)  # pull
    pass


def sync_all_remotes(local: Repo):
    remotes = local.getRemotes()
    for remote in remotes:
        sync(local, remote.repo)
    pass


def clone(source: Repo, destination: Repo):
    destination.addRemote(source)
    sync(destination, source)
