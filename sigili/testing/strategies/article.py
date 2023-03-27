import random
from hypothesis import assume, strategies
from sigili.article.repository import Article, ArticleUpdate

from sigili.type.id import ArticleID, ContentID


@strategies.composite
def a_group(draw: strategies.DrawFn):
    group = draw(strategies.text())
    return group


@strategies.composite
def an_article(draw: strategies.DrawFn, data: bytes | None = None) -> Article:
    if (data is None):
        data = draw(strategies.binary())
    groups = draw(strategies.lists(a_group(), unique=True))
    title = draw(strategies.text())
    article_update = ArticleUpdate(
        title,
        data,
        groups
    )
    contentID = ContentID.getContentID(data)
    articleID = ArticleID.getArticleID(article_update)
    article = Article(
        title,
        articleID,
        contentID,
        groups
    )
    return article


@strategies.composite
def some_articles(draw: strategies.DrawFn, amount: int):
    return draw(strategies.lists(an_article(), min_size=amount, max_size=amount))