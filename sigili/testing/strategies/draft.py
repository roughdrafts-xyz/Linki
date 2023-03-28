from hypothesis import strategies
from sigili.draft.repository import Draft
from sigili.testing.strategies.article import an_article, an_edit_of


@strategies.composite
def a_draft(draw: strategies.DrawFn):
    base_data = draw(strategies.binary())
    base_article = draw(an_article(base_data))
    new_data = draw(strategies.binary())
    new_article = draw(an_edit_of(base_article, new_data))
    return Draft(
        new_article.title,
        new_data,
        new_article.groups,
        base_article
    )


@strategies.composite
def a_draft_as_an_article_update(draw: strategies.DrawFn):
    return draw(a_draft()).asArticleUpdate()


@strategies.composite
def some_drafts(draw: strategies.DrawFn, amount: int):
    return (draw(a_draft()) for _ in range(amount))
