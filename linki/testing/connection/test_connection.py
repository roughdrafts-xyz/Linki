from dataclasses import asdict
from io import StringIO
import json
import pickle
from urllib.parse import urlparse
import urllib.request
from hypothesis import given
import pytest
import linki.connection
from linki.connection import Connection, MemoryConnection, PathConnection, ROWebConnection
from linki.id import Label
from linki.testing.strategies.article import an_article
from linki.title import Title


def do_test(connection: Connection):
    key = Label('key').labelId

    # Don't get a non-existent key
    with pytest.raises(KeyError):
        connection[key]

    # set and get a key
    connection[key] = 0
    assert connection[key] == 0
    assert key in connection  # iter test
    assert len(connection) == 1  # len test

    # Don't get a deleted key
    del connection[key]
    with pytest.raises(KeyError):
        del connection[key]  # Don't delete a deleted key
    assert key not in connection  # iter test
    assert len(connection) == 0  # len test

    with pytest.raises(KeyError):
        connection[key]


def test_mem_connection():
    connection = MemoryConnection[int]()
    do_test(connection)


def test_path_connection(tmp_path):
    connection = PathConnection[int](tmp_path)
    do_test(connection)


class MockRes:
    def __init__(self, obj) -> None:
        self.obj = pickle.dumps(obj)

    def read(self):
        return self.obj


@given(an_article())
def test_article_web_connection(article):
    def mock_open(*args, **kwargs):
        return MockRes(article)
    linki.connection.urlopen = mock_open
    url = urlparse('http://test')
    style = 'articles'
    key = Label('key').labelId

    connection = ROWebConnection(url, style)
    assert connection[key] == article


@given(an_article())
def test_title_web_connection(article):
    title = Title.fromArticle(article)

    def mock_open(*args, **kwargs):
        return MockRes(title)
    linki.connection.urlopen = mock_open
    url = urlparse('http://test')
    style = 'titles'
    key = Label('key').labelId

    connection = ROWebConnection(url, style)
    assert connection[key] == title
