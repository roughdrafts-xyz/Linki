from sigil.article.repository import ArticleRepository


class Wiki():
    def __init__(self, repositories: list[ArticleRepository]) -> None:
        self._repositories = repositories

    def sync(self) -> None:
        for out_repo in self._repositories:
            for in_repo in self._repositories:
                out_repo._data = out_repo._data | in_repo._data
                out_repo._log = out_repo._log | in_repo._log
