from dataclasses import asdict

from hypothesis import given
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


@given(an_article())
def test_does_handle_api(article: Article):
    viewer = get_memory_server()
    viewer.repo.articles.merge_article(article)
    viewer.repo.titles.set_title(article)

    expected = asdict(article)
    assert viewer.handle(
        'api', 'articles', article.articleId) == expected
    assert viewer.handle(
        'api', 'articles') == {'articles': [expected]}

    title = Title.fromArticle(article)
    expected = asdict(title)
    assert viewer.handle(
        'api', 'titles', article.label.labelId) == expected
    assert viewer.handle(
        'api', 'titles', '/'.join(article.label.path)) == expected
    assert viewer.handle(
        'api', 'titles') == {'titles': [expected]}


def test_does_handle_web():
    pass


def test_does_handle_contribute():
    # previously announce
    pass


def test_does_handle_copy():
    # previously pickle / subscribe
    pass

    self.app.route('/', 'GET', viewer.handle_home)
    self.app.route('/<output>/<style>/<label:path>',
                   'GET', viewer.handle)
    self.app.route('/<output>/<style>/',
                   'GET', viewer.handle)
    self.app.route('/<output>/<style>',
                   'GET', viewer.handle)
    self.app.route('/announce', 'POST', viewer.handle_announce)
