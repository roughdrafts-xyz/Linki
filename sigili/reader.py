from typing import Iterable
from sigili.article.repository import ArticleRepository
from sigili.title.repository import Title, TitleRepository


class Reader():
    def __init__(self, titles: TitleRepository, articles: ArticleRepository):
        self._titles = titles
        self._articles = articles
        pass

    def load_titles(self) -> Iterable[Title]:
        return self._titles.get_titles()
