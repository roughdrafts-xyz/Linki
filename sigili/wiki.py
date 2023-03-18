from sigili.article.repository import ArticleRepository


class Wiki():
    def __init__(self, repositories: set[ArticleRepository]) -> None:
        self._repositories = repositories

    def sync(self) -> None:
        for out_repo in self._repositories:
            for in_repo in self._repositories:
                out_refs = out_repo.get_refs()
                in_refs = in_repo.get_refs()
                missing_refs = in_refs - out_refs
                for ref in missing_refs:
                    article = in_repo.get_article(ref)
                    details = in_repo.get_details(ref)
                    out_repo.update_article(
                        refId=details.prefId,
                        content=article
                    )
