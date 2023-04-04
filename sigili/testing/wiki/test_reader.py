from hypothesis import given
from sigili.article.repository import Article, ArticleUpdate, MemoryArticleRepository
from sigili.reader import Reader
from sigili.testing.strategies.article import an_article, an_article_update
from sigili.title.repository import MemoryTitleRepository, Title


@given(an_article_update())
def test_should_load_a_title(update: ArticleUpdate):
    articles = MemoryArticleRepository()
    titles = MemoryTitleRepository()
    reader = Reader(titles, articles)

    article = articles.add_article(update)
    titles.set_title(article.title, article)

    read_titles = list(reader.load_titles())
    title: Title = read_titles[0]
    assert articles.get_article(title.articleId) == article
