import random
import string
from hypothesis import assume, strategies
from sigili.article.repository import Article, ArticleUpdate

from sigili.type.id import ArticleID, ContentID, Label


@strategies.composite
def a_label(draw: strategies.DrawFn):
    label = draw(strategies.text(alphabet=string.printable))
    assume(Label.is_valid(label))
    return Label(label)


@strategies.composite
def a_new_article(draw: strategies.DrawFn, data: bytes | None = None) -> Article:
    if (data is None):
        data = draw(strategies.binary())
    groups = ['test']
    title = draw(a_label())
    article_update = ArticleUpdate(
        title.name,
        data,
        groups
    )
    return Article.fromArticleUpdate(article_update)


@strategies.composite
def an_edit_of(draw: strategies.DrawFn, base_article: Article, data: bytes | None = None):
    if (data is None):
        data = draw(strategies.binary())
    article_update = ArticleUpdate.createUpdate(base_article, data)
    contentID = ContentID.getContentID(data)
    articleID = ArticleID.getArticleID(article_update)
    return Article(
        base_article.title,
        articleID,
        contentID,
        base_article.groups,
        base_article.articleId
    )


@strategies.composite
def an_article(draw: strategies.DrawFn, data: bytes | None = None):
    if (data is not None):
        article = a_new_article(data)
        update = an_edit_of(draw(article), data)
        article = strategies.one_of(article, update)
    else:
        article = a_new_article(data)
        update = an_edit_of(draw(article), data)
        new_update = an_edit_of(draw(article))
        article = strategies.one_of(article, update, new_update)
    article = draw(article)
    return article


@strategies.composite
def some_articles(draw: strategies.DrawFn, amount: int):
    return draw(strategies.lists(an_article(), min_size=amount, max_size=amount))


@strategies.composite
def an_article_update(draw: strategies.DrawFn, data: bytes | None = None):
    if (data is None):
        data = draw(strategies.binary())
    article = draw(an_article(data))
    return ArticleUpdate.createUpdate(article, data)
