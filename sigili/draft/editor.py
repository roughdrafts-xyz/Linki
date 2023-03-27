
from abc import ABC, abstractmethod
from typing import Iterable
from sigili.article.repository import ArticleRepository, ArticleUpdate

from sigili.draft.repository import Draft, DraftRepository
from sigili.draft.source import Source, SourceRepository
from sigili.title.repository import TitleRepository


class Editor():

    def __init__(self, repo: ArticleRepository, titles: TitleRepository, drafts: DraftRepository) -> None:
        self._repo = repo
        self._titles = titles
        self._drafts = drafts

    def get_updates(self) -> Iterable[Draft]:
        return (_draft for _draft in self._drafts.get_drafts() if _draft.should_update())

    def publish_drafts(self) -> None:
        for draft in self.get_updates():
            update = draft.asArticleUpdate()
            update = self._repo.merge_article(update)
            self._titles.set_title(update.title, update)

    @abstractmethod
    def load_titles(self) -> None:
        for title in self._titles.get_titles():
            article = self._repo.get_article(title.articleId)
            content = self._repo.content.get_content(article.contentId)
            draft = Draft(
                title,
                content,
                article.contentId,
                article.groups
            )
            self._drafts.set_draft(draft)
