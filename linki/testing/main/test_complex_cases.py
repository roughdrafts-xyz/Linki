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
