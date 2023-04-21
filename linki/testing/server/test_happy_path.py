import copy
from dataclasses import asdict
from io import BytesIO
import pickle
from typing import Dict, List
import bottle

from hypothesis import given
import pypandoc
from linki.article import Article, ArticleCollection
from linki.connection import MemoryConnection
from linki.testing.editor.test_editor import MemoryRepository
from linki.testing.strategies.article import an_article
from linki.title import Title, TitleCollection
from linki.viewer import WebView, WebViewConf

from werkzeug.test import Client


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


def setup_contribute(article) -> Dict[str, MemoryConnection]:
    article_conn = MemoryConnection[Article]()
    title_conn = MemoryConnection[Title]()
    articles = ArticleCollection(article_conn)
    titles = TitleCollection(title_conn)

    articles.merge_article(article)
    titles.set_title(article)
    return {
        'titles': title_conn,
        'articles': article_conn
    }


@given(an_article())
def test_does_handle_legit_contribute(article: Article):
    conns = setup_contribute(article)
    articles = conns['articles']
    titles = conns['titles']

    pak_contents: Dict[str, BytesIO] = {
        'articles': articles.toFile(),
        'titles': titles.toFile(),
    }

    viewer = get_memory_server()
    url = 'https://localhost:8080/'
    viewer.repo.subs.add_url(url)

    client = Client(viewer.app)
    res = client.post('/contribute', data={
        'url': url,
        'titles': (pak_contents['titles'], 'titles'),
        'articles': (pak_contents['articles'], 'articles')
    })

    assert res.status_code == 201
    assert res.text == '/updates'

    assert titles == viewer.repo.get_collection('titles')
    assert articles == viewer.repo.get_collection('articles')


@given(an_article())
def test_does_handle_not_legit_contribute(article: Article):
    conns = setup_contribute(article)
    articles = conns['articles']
    titles = conns['titles']

    pak_contents: Dict[str, bytes] = {
        'articles': articles.toStream(),
        'titles': titles.toStream(),
    }
    viewer = get_memory_server()
    viewer.repo.subs.add_url('https://localhost:8080/')

    client = Client(viewer.app)
    res = client.post('/contribute', data={
        'url': url
    })
    assert res.status_code == 200
    assert res.text == '/updates'
    assert title_conn != viewer.repo.get_collection('titles')
    assert article_conn != viewer.repo.get_collection('articles')

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
        copy=True,
        contribute=True
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
