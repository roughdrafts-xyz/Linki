import pytest
from linki.connection import Connection, MemoryConnection, PathConnection
from linki.id import Label


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
