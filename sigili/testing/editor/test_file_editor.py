
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from sigili.editor import FileEditor
from sigili.type.id import Label


@contextmanager
def get_file_editor():
    with TemporaryDirectory() as _dir:
        _path = Path(_dir)
        FileEditor.init(_path)
        yield FileEditor.fromPath(_path)


def test_loads_drafts():
    with get_file_editor() as editor:
        editor._path.joinpath('hello_world.md').write_text('Hello World')
        editor.load_drafts()
        assert editor._drafts.get_draft(Label('hello_world.md')) is not None
