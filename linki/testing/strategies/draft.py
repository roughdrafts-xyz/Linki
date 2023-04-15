from hypothesis import strategies
from linki.draft import Draft
from linki.testing.strategies.article import a_new_article, an_article, an_edit_of


@strategies.composite
def an_update_draft(draw: strategies.DrawFn):
    base_data = draw(strategies.binary())
    base_article = draw(an_article(base_data))
    new_data = draw(strategies.binary())
    new_article = draw(an_edit_of(base_article, new_data))
    return Draft(
        new_article.label,
        new_data,
        base_article
    )


@strategies.composite
def a_new_draft(draw: strategies.DrawFn):
    base_data = draw(strategies.binary())
    base_article = draw(a_new_article(base_data))
    return Draft(
        base_article.label,
        base_data,
        None
    )


@strategies.composite
def a_draft(draw: strategies.DrawFn):
    draft = draw(strategies.one_of(a_new_draft(), an_update_draft()))
    return draft


@strategies.composite
def some_drafts(draw: strategies.DrawFn, amount: int):
    return (draw(a_draft()) for _ in range(amount))


@strategies.composite
def some_new_drafts(draw: strategies.DrawFn, amount: int):
    return (draw(a_new_draft()) for _ in range(amount))
