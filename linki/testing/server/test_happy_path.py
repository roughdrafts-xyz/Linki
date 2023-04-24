from io import BytesIO
from typing import Dict, TypedDict

from hypothesis import given, settings
import msgspec
from linki.article import BaseArticle, ArticleCollection
from linki.connection import MemoryConnection
from linki.testing.editor.test_editor import MemoryRepository
from linki.testing.strategies.article import an_article
from linki.testing.strategies.draft import some_drafts
from linki.title import BaseArticle, TitleCollection
from linki.viewer import RenderedArticle, WebView, WebViewConf

from werkzeug.test import Client


def get_memory_server():
    repo = MemoryRepository()
    viewer = WebView(repo, WebViewConf(
        web=True,
        api=True,
        copy=True,
        contribute=True
    ))
    return viewer


@given(some_drafts(2))
def test_does_handle_articles(article_set: set[BaseArticle]):
    articles = list(article_set)
    article = articles[0]
    title = articles[1]
    viewer = get_memory_server()
    viewer.repo.articles.merge_article(article)
    viewer.repo.articles.merge_article(title)
    viewer.repo.titles.set_title(title)
    client = get_client(viewer)

    path = '/'.join(title.label.path)
    single_calls = (
        {
            'style': 'article',
            'url': f'/api/{title.articleId}'
        },
        {
            'style': 'path',
            'url': f'/api/{path}'
        },
        {
            'style': 'title',
            'url': f'/api/{title.label.labelId}'
        },
    )

    expected = title
    for call in single_calls:
        res = client.get(call['url'])
        assert res.status_code == 200
        assert msgspec.from_builtins(res.json, type=BaseArticle) == expected

    res = client.get('/api/articles/')
    expected = {
        'articles': [
            article,
            title
        ]
    }
    assert res.status_code == 200
    assert msgspec.from_builtins(
        res.json, type=dict[str, list[BaseArticle]]) == expected

    res = client.get('/api/titles/')
    expected = {
        'titles': [
            title
        ]
    }
    assert res.status_code == 200
    assert msgspec.from_builtins(
        res.json, type=dict[str, list[BaseArticle]]) == expected


@given(some_drafts(2))
@settings(deadline=10000)
def test_does_handle_web(article_set: set[BaseArticle]):
    articles = list(article_set)
    article = articles[0]
    title = articles[1]
    viewer = get_memory_server()
    viewer.repo.articles.merge_article(article)
    viewer.repo.articles.merge_article(title)
    viewer.repo.titles.set_title(title)

    viewer.one_tmpl.render = msgspec.to_builtins  # type: ignore
    viewer.many_tmpl.render = msgspec.to_builtins  # type: ignore
    client = get_client(viewer)

    e_article = RenderedArticle.fromArticle(article)
    e_title = RenderedArticle.fromArticle(title)

    path = '/'.join(title.label.path)
    single_calls = (
        {
            'style': 'article',
            'url': f'/w/{title.articleId}'
        },
        {
            'style': 'path',
            'url': f'/w/{path}'
        },
        {
            'style': 'title',
            'url': f'/w/{title.label.labelId}'
        },
    )

    expected = {
        'item': e_title
    }
    for call in single_calls:
        res = client.get(call['url'])
        assert res.status_code == 200
        assert msgspec.from_builtins(
            res.json, type=dict[str, RenderedArticle]) == expected

    class RenderRes(TypedDict):
        items: list[RenderedArticle]
        style: str
        style_root: str

    res = client.get('/w/articles/')
    expected = {
        'items': [
            e_article,
            e_title
        ],
        'style': 'articles'.capitalize(),
        'style_root': f"/w/articles/"
    }
    assert res.status_code == 200
    assert msgspec.from_builtins(
        res.json, type=RenderRes) == expected

    res = client.get('/w/titles/')
    expected = {
        'items': [
            e_title
        ],
        'style': 'titles'.capitalize(),
        'style_root': f"/w/titles/"
    }
    assert res.status_code == 200
    assert msgspec.from_builtins(
        res.json, type=RenderRes) == expected


@given(some_drafts(2))
@settings(deadline=10000)
def test_does_render_web(article_set: set[BaseArticle]):
    articles = list(article_set)
    article = articles[0]
    title = articles[1]
    viewer = get_memory_server()
    viewer.repo.articles.merge_article(article)
    viewer.repo.articles.merge_article(title)
    viewer.repo.titles.set_title(title)

    client = get_client(viewer)

    path = '/'.join(title.label.path)
    single_calls = (
        {
            'style': 'article',
            'url': f'/w/{title.articleId}'
        },
        {
            'style': 'path',
            'url': f'/w/{path}'
        },
        {
            'style': 'title',
            'url': f'/w/{title.label.labelId}'
        },
    )
    for call in single_calls:
        res = client.get(call['url'])
        assert res.status_code == 200

    res = client.get('/w/articles/')
    assert res.status_code == 200

    res = client.get('/w/titles/')
    assert res.status_code == 200


def setup_contribute(article) -> Dict[str, MemoryConnection]:
    article_conn = MemoryConnection[BaseArticle]()
    title_conn = MemoryConnection[BaseArticle]()
    articles = ArticleCollection(article_conn)
    titles = TitleCollection(title_conn)

    articles.merge_article(article)
    titles.set_title(article)
    return {
        'titles': title_conn,
        'articles': article_conn
    }


def get_client(viewer: WebView | None = None) -> Client:
    if (viewer is None):
        viewer = get_memory_server()
    return Client(viewer.app)  # type: ignore


@given(an_article())
def test_does_handle_contributions(article: BaseArticle):
    conns = setup_contribute(article)
    articles = conns['articles']
    titles = conns['titles']

    def contents() -> Dict[str, BytesIO]:
        return {
            'articles': articles.toFile(),
            'titles': titles.toFile(),
        }

    username = 'user'
    password = 'pass'

    viewer = get_memory_server()

    client = get_client(viewer)

    def contribute():
        pak_contents = contents()
        return client.post('/contribute', data={
            'titles': (pak_contents['titles'], 'titles'),
            'articles': (pak_contents['articles'], 'articles')
        }, auth=(username, password))

    # Invalid User
    res = contribute()

    assert res.status_code == 403
    assert res.text == ''

    assert list(titles.values()) != viewer.repo.get_collection('titles')
    assert list(articles.values()) != viewer.repo.get_collection('articles')

    # Valid User
    viewer.repo.users.add_user(username, password)
    res = contribute()
    assert res.status_code == 201
    title_text = ','.join([title.articleId for title in titles.values()])
    assert res.text == f'/w/titles/{title_text}'

    assert list(titles.values()) == viewer.repo.get_collection('titles')
    assert list(articles.values()) == viewer.repo.get_collection('articles')


@given(some_drafts(2))
def test_does_handle_copy(article_set: set[BaseArticle]):
    articles = list(article_set)
    article = articles[0]
    title = articles[1]
    viewer = get_memory_server()
    viewer.repo.articles.merge_article(article)
    viewer.repo.articles.merge_article(title)
    viewer.repo.titles.set_title(title)
    client = get_client(viewer)

    path = '/'.join(title.label.path)
    single_calls = (
        {
            'style': 'article',
            'url': f'/copy/{title.articleId}'
        },
        {
            'style': 'path',
            'url': f'/copy/{path}'
        },
        {
            'style': 'title',
            'url': f'/copy/{title.label.labelId}'
        },
    )

    expected = title
    for call in single_calls:
        res = client.get(call['url'])
        assert res.status_code == 200
        assert msgspec.msgpack.decode(res.data, type=BaseArticle) == expected

    res = client.get('/copy/articles/')
    expected = [
        article,
        title
    ]
    assert res.status_code == 200
    assert msgspec.msgpack.decode(res.data, type=list[BaseArticle]) == expected

    res = client.get('/copy/titles/')
    expected = [
        title
    ]
    assert res.status_code == 200
    assert msgspec.msgpack.decode(res.data, type=list[BaseArticle]) == expected
