from pathlib import Path
from linki.main import app
from typer.testing import CliRunner

runner = CliRunner()


def test_publish_changed_paths(tmp_path: Path):
    runner.invoke(app, ["init", str(tmp_path)])
    path = tmp_path.joinpath('hello_world.md')
    path.write_text('Hello World')
    runner.invoke(app, ["publish", str(tmp_path)])
    tmp_path.joinpath('folder').mkdir()
    path = path.replace(tmp_path / 'folder' / 'hello_world.md')
    res = runner.invoke(app, ["publish", str(tmp_path)])
    assert res.stdout == f"Published {1} drafts.\n"


def test_copy_changed_paths(tmp_path: Path):
    runner.invoke(app, ["init", str(tmp_path)])
    folder = tmp_path.joinpath('folder')
    folder.mkdir()

    file = folder.joinpath('hello_world.md')
    file.write_text('Hello World')
    runner.invoke(app, ["publish", str(tmp_path)])

    # Initial Copy

    folder = folder.rename(tmp_path / 'folder2')
    res = runner.invoke(app, ["publish", str(tmp_path)])

    assert res.stdout == f"Published {1} drafts.\n"

    # Update Copy
