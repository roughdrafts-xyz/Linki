import string
from hypothesis import assume, strategies
from linki.article import Article

from linki.id import Label


@strategies.composite
def a_label(draw: strategies.DrawFn):
    label = draw(strategies.text(alphabet=string.printable))
    assume(Label.is_valid(label))
    return Label(label)


@strategies.composite
def a_new_article(draw: strategies.DrawFn, data: bytes | None = None) -> Article:
    if (data is None):
        data = draw(strategies.binary())
    label = draw(a_label())
    return Article(
        label.unsafe_raw_name,
        data,
        None
    )


@strategies.composite
def an_edit_of(draw: strategies.DrawFn, base_article: Article, data: bytes | None = None):
    if (data is None):
        data = draw(strategies.binary())
    return Article(
        base_article.label.unsafe_raw_name,
        data,
        base_article
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
