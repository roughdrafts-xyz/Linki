from pathlib import Path
from unittest import TestCase

from linki.main import app, copy as copyCMD
from typer.testing import CliRunner

runner = CliRunner()


def test_publish_changed_paths(tmp_path: Path):
    source = tmp_path.joinpath('source').resolve()
    runner.invoke(app, ["init", str(source)])
    s_folder = source.joinpath('folder').resolve()
    s_folder.mkdir()

    s_file = s_folder.joinpath('hello_world.md')
    s_file.write_text('Hello World')
    res = runner.invoke(app, ["publish", str(source)])
    assert res.stdout == f"Published {1} drafts.\n"

    s_folder = s_folder.rename(source / 'folder2').resolve()
    print(s_folder)
    res = runner.invoke(app, ["publish", str(source)])

    assert res.stdout == f"Published {1} drafts.\n"


def test_copy_changed_paths(tmp_path: Path):
    source = tmp_path.joinpath('source').resolve()
    runner.invoke(app, ["init", str(source)])
    s_folder = source.joinpath('folder').resolve()
    s_folder.mkdir()

    s_file = s_folder.joinpath('hello_world.md')
    s_file.write_text('Hello World')
    res = runner.invoke(app, ["publish", str(source)])
    assert res.stdout == f"Published {1} drafts.\n"

    copy = tmp_path.joinpath('copy').resolve()
    # Initial Copy
    runner.invoke(app, ["copy", str(source), str(copy)])

    s_folder = s_folder.rename(source / 'folder2').resolve()
    print(s_folder)
    res = runner.invoke(app, ["publish", str(source)])

    assert res.stdout == f"Published {1} drafts.\n"

    # Update Copy
    # runner.invoke(app, ["copy", str(source), str(copy)])
    copyCMD(str(source), copy)

    test = TestCase()
    s_files = [f.relative_to(source)
               for f in source.iterdir()]
    c_files = [f.relative_to(copy)
               for f in copy.iterdir()]
    test.assertCountEqual(s_files, c_files)
