# remotes have three directions
# -sync (push then pull)
# -push (outgoing updates only)
# -pull (incoming updates only)
# direction is relative to the local. IE a pull remote is a remote that you receive updates from when you sync to it.
# pushing doesn't exist intentionally, uni-directional design is simpler.
from sigil.repo.abc import Repo


def pull(local: Repo, remote: Repo):
    # Get Remote Refs
    remoteRefs: set = remote.getRefIds()
    localRefs: set = local.getRefIds()
    # Compare Refs
    missingRefs: set = remoteRefs.difference(localRefs)

    # Copy Missing Refs
    local.copy(remote, missingRefs)

    # First Draft
    #
    # Get the remote's db
    # Attach it to the local's db (https://stackoverflow.com/a/11089277)
    # List histories in remote not in local
    # Copy over those rows and files
    # Repeat in reverse?

    # None of these features should be interface dependent. They should all take the same input/output.
    pass


def sync(local: Repo, remote: Repo):
    pull(remote, local)  # push
    pull(local, remote)  # pull
    pass


def sync_all_remotes(local: Repo):
    remotes = local.getRemotes()
    for remote in remotes:
        sync(local, remote)
    pass


def clone(source: Repo, destination: Repo):
    destination.addRemote(source)
    sync(destination, source)
