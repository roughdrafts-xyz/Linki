from typing import Set
from hypothesis import assume, strategies
from linki.draft import Draft
from linki.testing.strategies.article import an_article


@strategies.composite
def an_update_draft(draw: strategies.DrawFn):
    base_article = draw(an_article())
    new_article = draw(an_article(base_article))
    return Draft.fromArticle(new_article)


@strategies.composite
def a_new_draft(draw: strategies.DrawFn):
    base_article = draw(an_article())
    return Draft.fromArticle(base_article)


@strategies.composite
def a_draft(draw: strategies.DrawFn):
    draft = draw(strategies.one_of(a_new_draft(), an_update_draft()))
    return draft


@strategies.composite
def some_drafts(draw: strategies.DrawFn, amount: int):
    drafts: Set[Draft] = set()
    for i in range(amount):
        draft = draw(a_draft())
        for _ in drafts:
            assume(draft.label != _.label)

        if (draft.editOf is not None):
            for _ in drafts:
                if _.editOf is not None:
                    assume(draft.editOf.label != _.editOf.label)

        drafts.add(draft)
        assume(len(drafts) == i+1)
    return drafts


@strategies.composite
def some_new_drafts(draw: strategies.DrawFn, amount: int):
    return (draw(a_new_draft()) for _ in range(amount))
