from operator import xor
import string
from hypothesis import assume, strategies
from linki.article import Article, BaseArticle, BaseArticle

from linki.id import SimpleLabel


@strategies.composite
def a_label(draw: strategies.DrawFn):
    label = draw(strategies.text(alphabet=string.printable))
    return SimpleLabel(label)


@strategies.composite
def some_content(draw: strategies.DrawFn):
    content = draw(strategies.text(alphabet=string.printable))
    return content.replace('\r\n', '\n').replace('\r', '\n')


@strategies.composite
def an_article(draw: strategies.DrawFn, editOf: BaseArticle | None = None) -> BaseArticle:
    label = draw(a_label())
    data = draw(some_content())
    article = Article(
        label,
        data,
        editOf
    )
    if (editOf is not None):
        assume(
            xor(
                article.label == editOf.label,
                article.content == editOf.content
            )
        )
    return article


@strategies.composite
def some_articles(draw: strategies.DrawFn, amount: int):
    return draw(strategies.lists(an_article(), min_size=amount, max_size=amount))
