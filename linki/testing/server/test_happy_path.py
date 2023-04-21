import copy
from dataclasses import asdict

from hypothesis import given
import pypandoc
from linki.article import Article
from linki.testing.editor.test_editor import MemoryRepository
from linki.testing.strategies.article import an_article
from linki.title import Title
from linki.viewer import WebView, WebViewConf


def get_memory_server():
    repo = MemoryRepository()
    viewer = WebView(repo, WebViewConf(
        web=True,
        api=True
    ))
    return viewer


def do_handle_api(viewer: WebView, article: Article):
    output = 'api'
    viewer.repo.articles.merge_article(article)
    viewer.repo.titles.set_title(article)
    title = Title.fromArticle(article)

    expected = asdict(article)
    assert viewer.handle(
        output, 'articles', article.articleId) == expected
    assert viewer.handle(
        output, 'articles') == {'articles': [expected]}

    expected = asdict(title)
    assert viewer.handle(
        output, 'titles', article.label.labelId) == expected
    assert viewer.handle(
        output, 'titles', '/'.join(article.label.path)) == expected
    assert viewer.handle(
        output, 'titles') == {'titles': [expected]}


def do_handle_web(viewer: WebView, article: Article):
    output = 'w'
    viewer.repo.articles.merge_article(article)
    viewer.repo.titles.set_title(article)

    one_article = copy.copy(article)
    one_article.content = pypandoc.convert_text(
        one_article.content, format='markdown', to='html')
    many_article = copy.copy(article)

    one_title = Title.fromArticle(one_article)
    many_title = Title.fromArticle(article)

    assert viewer.handle(
        output, 'articles', article.articleId) == one_article
    assert viewer.handle(
        output, 'articles') == [many_article]

    assert viewer.handle(
        output, 'titles', article.label.labelId) == one_title
    assert viewer.handle(
        output, 'titles', '/'.join(article.label.path)) == one_title
    assert viewer.handle(
        output, 'titles') == [many_title]


@given(an_article())
def test_does_handle_api(article: Article):
    viewer = get_memory_server()
    do_handle_api(viewer, article)


@given(an_article())
def test_does_handle_web(article: Article):
    viewer = get_memory_server()

    def handleArgs(*args, **kwargs):
        env = {}
        for dict_arg in args:
            env.update(dict_arg)
        env.update(kwargs)
        return env

    def retSingle(*args, **kwargs):
        env = handleArgs(*args, **kwargs)
        return env.get('item')

    def retMany(*args, **kwargs):
        env = handleArgs(*args, **kwargs)
        return env.get('items')

    viewer.one_tmpl.render = retSingle  # type: ignore
    viewer.many_tmpl.render = retMany  # type: ignore

    do_handle_web(viewer, article)


def test_does_handle_contribute():
    # previously announce
    pass


def test_does_handle_copy():
    # previously pickle / subscribe
    pass
