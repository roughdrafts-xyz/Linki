import random
import string
from hypothesis import assume, strategies
from sigili.article.repository import Article, ArticleUpdate

from sigili.type.id import ArticleID, ContentID, Label


@strategies.composite
def a_group(draw: strategies.DrawFn):
    group = draw(strategies.text(alphabet=string.printable, min_size=1))
    return group


@strategies.composite
def an_article(draw: strategies.DrawFn, data: bytes | None = None) -> Article:
    if (data is None):
        data = draw(strategies.binary())
    groups = draw(strategies.lists(a_group(), unique=True))
    _title = draw(strategies.text(min_size=1))
    title = Label(_title)
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
