import string
from hypothesis import assume, strategies
from linki.article import Article, Article

from linki.id import SimpleLabel


@strategies.composite
def a_label(draw: strategies.DrawFn):
    label = draw(strategies.text(alphabet=string.printable))
    assume(SimpleLabel.is_valid(label))
    return SimpleLabel(label)


@strategies.composite
def some_content(draw: strategies.DrawFn):
    content = draw(strategies.text(alphabet=string.printable))
    assume(len(content) > 0)
    return content


@strategies.composite
def an_article(draw: strategies.DrawFn, editOf: Article | None = None) -> Article:
    label = draw(a_label())
    data = draw(some_content())
    article = Article(
        label,
        data,
        editOf
    )
    if (editOf is not None):
        assume(
            article.label != editOf.label or
            article.content != editOf.content
        )
    return article


@strategies.composite
def some_articles(draw: strategies.DrawFn, amount: int):
    return draw(strategies.lists(an_article(), min_size=amount, max_size=amount))
