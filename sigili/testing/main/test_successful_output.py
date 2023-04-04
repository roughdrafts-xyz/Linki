from pathlib import Path
import pytest
from typer.testing import CliRunner
from sigili.main import app

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


def test_successful_copy():
    pass


def test_successful_subscribe():
    pass


def test_successful_serve():
    # also announce
    pass
