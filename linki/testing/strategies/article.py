import string
from hypothesis import assume, strategies
from linki.article import SimpleArticle

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
def a_new_article(draw: strategies.DrawFn, data: str | None = None) -> SimpleArticle:
    if (data is None):
        data = draw(some_content())
    label = draw(a_label())
    return SimpleArticle(
        label.unsafe_raw_name,
        data,
        None
    )


@strategies.composite
def an_edit_of(draw: strategies.DrawFn, base_article: SimpleArticle, data: str | None = None):
    if (data is None):
        data = draw(some_content())
    return SimpleArticle(
        base_article.label.unsafe_raw_name,
        data,
        base_article
    )


@strategies.composite
def an_article(draw: strategies.DrawFn, data: str | None = None):
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
