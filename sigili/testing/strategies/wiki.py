from hypothesis import strategies
from sigili.article.repository import ArticleUpdate, MemoryArticleRepository
from sigili.draft.repository import MemoryDraftRepository
from sigili.testing.strategies.article import an_article

from sigili.title.repository import MemoryTitleRepository
from sigili.wiki import Wiki


@strategies.composite
def a_wiki(draw: strategies.DrawFn):
    articles = MemoryArticleRepository()
    titles = MemoryTitleRepository(articles)
    drafts = MemoryDraftRepository()

    wiki = Wiki(articles, titles, drafts)
    return wiki


@strategies.composite
def a_wiki_with_an_update(draw: strategies.DrawFn):
    articles = MemoryArticleRepository()
    titles = MemoryTitleRepository(articles)
    drafts = MemoryDraftRepository()
    article = draw(an_article())
    content = articles.content.get_content(article.contentId)
    update = ArticleUpdate(article.title, content,
                           article.groups, article.editOf)
    titles.set_title(article.title, update)

    wiki = Wiki(articles, titles, drafts)
    return wiki
