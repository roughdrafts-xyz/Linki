import copy
from dataclasses import asdict
from typing import Dict
from boddle import boddle
import bottle

from hypothesis import given
import pypandoc
from linki.article import Article, ArticleCollection
from linki.connection import MemoryConnection
from linki.testing.editor.test_editor import MemoryRepository
from linki.testing.strategies.article import an_article
from linki.title import Title, TitleCollection
from linki.viewer import WebView, WebViewConf


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


@given(an_article())
def test_does_handle_contribute(article: Article):
    def compare_res(self: bottle.HTTPResponse, __value: object):
        if (not isinstance(__value, bottle.HTTPResponse)):
            return False

        return (
            self.body == __value.body and
            self.status_code == __value.status_code
        )
    bottle.HTTPResponse.__eq__ = compare_res
    article_conn = MemoryConnection[Article]()
    title_conn = MemoryConnection[Title]()
    articles = ArticleCollection(article_conn)
    titles = TitleCollection(title_conn)

    articles.merge_article(article)
    titles.set_title(article)

    pak_contents: Dict[str, MemoryConnection] = {
        'titles': title_conn,
        'articles': article_conn
    }
    update_pak = pak_contents

    with boddle(params={
        'url': 'https://localhost:8080/',
        'update': update_pak
    }):
        viewer = get_memory_server()
        viewer.repo.subs.add_url('https://localhost:8080/')
        res = viewer.handle_contribution()
        expected = bottle.HTTPResponse('/updates', 201)
        assert res == expected
        assert pak_contents.get(
            'titles') == viewer.repo.get_collection('titles')
        assert pak_contents.get(
            'articles') == viewer.repo.get_collection('articles')

    with boddle(params={
        'url': 'https://localhost:8888/',
        'update': update_pak
    }):
        viewer = get_memory_server()
        viewer.repo.subs.add_url('https://localhost:8080/')
        res = viewer.handle_contribution()
        expected = bottle.HTTPResponse('', 403)
        assert res == expected
        assert pak_contents.get(
            'titles') != viewer.repo.get_collection('titles')
        assert pak_contents.get(
            'articles') != viewer.repo.get_collection('articles')

    # TODO - Requires configuration options
    # handles contributions from illegal users
    #   expect some kind of failure indicator


@given(an_article())
def test_does_handle_copy(article: Article):
    viewer = get_memory_server()
    do_handle_copy(viewer, article)
    pass


def get_memory_server():
    repo = MemoryRepository()
    viewer = WebView(repo, WebViewConf(
        web=True,
        api=True,
        copy=True
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


def do_handle_copy(viewer: WebView, article: Article):
    output = 'copy'
    viewer.repo.articles.merge_article(article)
    viewer.repo.titles.set_title(article)
    title = Title.fromArticle(article)

    def one_article():
        res: bytes = viewer.handle(
            output, 'articles', article.articleId)  # type: ignore
        return Article.fromStream(res)

    def many_articles():
        res: bytes = viewer.handle(output, 'articles')  # type: ignore
        return ArticleCollection.fromStream(res)

    assert article == one_article()

    articles = ArticleCollection(MemoryConnection[Article]())
    articles.merge_article(article)
    assert articles == many_articles()

    def one_title_id():
        res: bytes = viewer.handle(
            output, 'titles', article.label.labelId)  # type: ignore
        return Title.fromStream(res)

    def one_title_path():
        res: bytes = viewer.handle(
            output, 'titles', '/'.join(article.label.path))  # type: ignore
        return Title.fromStream(res)

    def many_titles():
        res: bytes = viewer.handle(output, 'titles')  # type: ignore
        return TitleCollection.fromStream(res)

    titles = TitleCollection(MemoryConnection[Title]())
    titles.set_title(title)

    assert article == one_title_id()
    assert article == one_title_path()
    assert titles == many_titles()
