from typing import Iterable
from sigili.article.repository import ArticleRepository
from sigili.draft.repository import Draft, DraftRepository
from sigili.title.repository import TitleRepository


class Editor():

    def __init__(self, titles: TitleRepository, drafts: DraftRepository, articles: ArticleRepository) -> None:
        self._titles = titles
        self._drafts = drafts
        self._articles = articles

    def get_updates(self) -> Iterable[Draft]:
        return (_draft for _draft in self._drafts.get_drafts() if _draft.should_update())

    def publish_drafts(self) -> None:
        for title in self._titles.get_titles():
            hasDraft = self._drafts.get_draft(title.title) != None
            if not hasDraft:
                self._titles.clear_title(title.title)

        for draft in self.get_updates():
            update = draft.asArticleUpdate()
            self._titles.set_title(update.title, update)

    def load_titles(self) -> None:
        for title in self._titles.get_titles():
            content = self._titles.articles.content.get_content(
                title.contentId)
            draft = Draft(
                title.title,
                content,
                title.groups,
                title
            )
            self._drafts.set_draft(draft)
