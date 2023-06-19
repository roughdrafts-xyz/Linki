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
        assert msgspec.convert(res.json, type=BaseArticle) == expected

    res = client.get('/api/articles/')
    expected = {
        'articles': [
            article,
            title
        ]
    }
    assert res.status_code == 200
    assert msgspec.convert(
        res.json, type=dict[str, list[BaseArticle]]) == expected

    res = client.get('/api/titles/')
    expected = {
        'titles': [
            title
        ]
    }
    assert res.status_code == 200
    assert msgspec.convert(
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

    e_article = RenderedArticle.fromArticle(article, str(article.articleId))
    e_title_by_a_id = RenderedArticle.fromArticle(title, str(title.articleId))
    e_title_by_l_id = RenderedArticle.fromArticle(title, title.label.labelId)
    e_title_by_path = RenderedArticle.fromArticle(
        title, '/'.join(title.label.path))

    path = '/'.join(title.label.path)
    single_calls = (
        {
            'style': 'article',
            'expect': e_title_by_a_id,
            'url': f'/w/{title.articleId}'
        },
        {
            'style': 'path',
            'expect': e_title_by_path,
            'url': f'/w/{path}'
        },
        {
            'style': 'title',
            'expect': e_title_by_l_id,
            'url': f'/w/{title.label.labelId}'
        },
    )
    for call in single_calls:
        res = client.get(call['url'])
        expected = {'item': call['expect']}
        assert res.status_code == 200
        assert msgspec.convert(
            res.json, type=dict[str, RenderedArticle]) == expected

    class RenderRes(TypedDict):
        items: set[RenderedArticle]
        style: str
        style_root: str

    res = client.get('/w/articles/')
    expected = {
        'items': {
            e_article,
            e_title_by_a_id
        },
        'style': 'articles'.capitalize(),
        'style_root': f"/w/"
    }
    assert res.status_code == 200
    actual = msgspec.convert(res.json, type=RenderRes)
    assert actual['style'] == expected['style']
    assert actual['style_root'] == expected['style_root']
    assert actual['items'] == expected['items']

    res = client.get('/w/titles/')
    expected = {
        'items': {
            e_title_by_path
        },
        'style': 'titles'.capitalize(),
        'style_root': f"/w/"
    }
    assert res.status_code == 200
    actual = msgspec.convert(res.json, type=RenderRes)
    assert actual['style'] == expected['style']
    assert actual['style_root'] == expected['style_root']
    assert actual['items'] == expected['items']


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


def get_client(viewer: WebView | None = None) -> Client:
    if (viewer is None):
        viewer = get_memory_server()
    return Client(viewer.app)  # type: ignore


@given(an_article())
def test_does_handle_contributions(article: BaseArticle):
    titles = MemoryConnection[BaseArticle]()
    title_collection = TitleCollection(titles)
    title_collection.set_title(article)

    def contents() -> Dict[str, BytesIO]:
        return {
            'changes': titles.toFile(),
        }

    username = 'user'
    password = 'pass'

    viewer = get_memory_server()

    client = get_client(viewer)

    def contribute():
        pak_contents = contents()
        return client.post('/api/contribute', data={
            'changes': (pak_contents['changes'], 'changes')
        }, auth=(username, password))

    # Invalid User
    res = contribute()

    assert res.status_code == 403
    assert res.text == ''

    # Valid User
    viewer.repo.users.add_user(username, password)
    res = contribute()
    assert res.status_code == 202
    change_text = ','.join([change.articleId for change in titles.values()])
    assert res.text == f'/w/contributions/{change_text}'

    # TODO Test for 201 (can_edit=True)


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
