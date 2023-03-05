# remotes have three directions
# -sync (push then pull)
# -push (outgoing updates only)
# -pull (incoming updates only)
# direction is relative to the local. IE a pull remote is a remote that you receive updates from when you sync to it.
# pushing doesn't exist intentionally, uni-directional design is simpler.

def sync(local, remote):
    remote.pull(local)  # push
    local.pull(remote)  # pull
    pass


def sync_all_remotes(local):
    remotes = local.getRemotes()
    for remote in remotes:
        sync(local, remote)
    pass


def clone(source, destination):
    destination.addRemote(source)
    sync(destination, source)
