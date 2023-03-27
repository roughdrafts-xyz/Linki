from hypothesis import strategies
from sigili.draft.repository import Draft

from sigili.testing.article.strategies import an_article


@strategies.composite
def a_draft(draw: strategies.DrawFn):
    base_data = draw(strategies.binary())
    base_article = draw(an_article(base_data))
    new_data = draw(strategies.binary())
    new_article = draw(an_article(new_data))
    new_article.editOf = base_article.articleId
    return Draft(base_article, new_data, new_article.contentId, new_article.groups)
