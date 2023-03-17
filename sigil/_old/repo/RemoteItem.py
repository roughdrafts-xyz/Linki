class RemoteItem:
    def __init__(self, location: str, style: str) -> None:
        match style:
            case "local":
                from sigil.old_repo.LocalRepo.LocalRepo import LocalRepo
                self._repo = LocalRepo(location)
            case _:
                raise NotImplementedError

    @property
    def repo(self) -> 'Repo':
        return self._repo
