from typing import Set
from hypothesis import assume, strategies
from linki.draft import BaseArticle
from linki.testing.strategies.article import an_article


@strategies.composite
def an_update_draft(draw: strategies.DrawFn):
    base_article = draw(an_article())
    new_article = draw(an_article(base_article))
    return new_article


@strategies.composite
def a_new_draft(draw: strategies.DrawFn):
    base_article = draw(an_article())
    return base_article


@strategies.composite
def a_draft(draw: strategies.DrawFn):
    draft = draw(strategies.one_of(a_new_draft(), an_update_draft()))
    return draft


@strategies.composite
def some_drafts(draw: strategies.DrawFn, amount: int):
    drafts: Set[BaseArticle] = set()
    for i in range(amount):
        draft = draw(a_draft())
        drafts.add(draft)
        assume(len(drafts) == i+1)

    for x_draft in drafts:
        for y_draft in drafts - {x_draft}:
            assume(x_draft.label != y_draft.label)
            y_edit = y_draft.editOf
            while (y_edit is not None):
                # TODO This seems unrealistic
                # I don't think its a good assumption
                assume(x_draft.label != y_edit.label)
                y_edit = y_edit.editOf
    return drafts


@strategies.composite
def some_new_drafts(draw: strategies.DrawFn, amount: int):
    return (draw(a_new_draft()) for _ in range(amount))
