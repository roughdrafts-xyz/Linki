from pathlib import Path
import pytest
from typer.testing import CliRunner
from sigili.main import app, copy as copy_cmd

runner = CliRunner()


def test_successful_init(tmp_path: Path):
    res = runner.invoke(app, ["init", str(tmp_path)])
    assert res.stdout == f"Initialized wiki in {str(tmp_path)}.\n"


def test_successful_publish(tmp_path: Path):
    runner.invoke(app, ["init", str(tmp_path)])
    tmp_path.joinpath('hello_world.md').write_text('Hello World')

    res = runner.invoke(app, ["publish", str(tmp_path)])
    x = 1
    assert res.stdout == f"Published {x} drafts.\n"

    tmp_path.joinpath('hello_world.md').write_text('Hello World')
    res = runner.invoke(app, ["publish", str(tmp_path)])
    x = 0
    assert res.stdout == f"Published {x} drafts.\n"

    tmp_path.joinpath('hello_world.md').write_text('Goodnight Moon')
    res = runner.invoke(app, ["publish", str(tmp_path)])
    x = 1
    assert res.stdout == f"Published {x} drafts.\n"

    tmp_path.joinpath('good_moon.md').write_text('Goodnight Moon')
    tmp_path.joinpath('hello_world.md').write_text('Hello World')
    res = runner.invoke(app, ["publish", str(tmp_path)])
    x = 2
    assert res.stdout == f"Published {x} drafts.\n"


def test_successful_local_copy(tmp_path: Path):
    base = tmp_path.joinpath('base')
    copy = tmp_path.joinpath('copy')
    base.mkdir()
    copy.mkdir()
    res = runner.invoke(app, ["init", str(base)])
    assert res.stdout == f"Initialized wiki in {str(base)}.\n"
    res = runner.invoke(app, ["init", str(copy)])
    assert res.stdout == f"Initialized wiki in {str(copy)}.\n"
    base.joinpath('hello_world.md').write_text('Hello World')
    res = runner.invoke(app, ["publish", str(base)])
    assert res.stdout == f"Published 1 drafts.\n"
    res = runner.invoke(app, ["copy", str(base), str(copy)])
    x = 1
    y = 1
    assert res.stdout == f"Copied {x} titles and {y} articles.\n"

    content = copy.joinpath('hello_world.md').read_text()
    assert content == "Hello World"


def test_successful_subscribe():
    pass


def test_successful_serve():
    # also announce
    pass
