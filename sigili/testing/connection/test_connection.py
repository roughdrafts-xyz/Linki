import pytest
from sigili.connection import Connection, MemoryConnection
from sigili.type.id import Label, LabelID


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
    assert key not in connection  # iter test
    assert len(connection) == 0  # len test

    with pytest.raises(KeyError):
        connection[key]


def test_mem_connection():
    connection = MemoryConnection[LabelID, int]()
    do_test(connection)
