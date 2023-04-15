from pathlib import Path
from typer.testing import CliRunner
from linki.main import app, inbox, init

runner = CliRunner()


def test_init_repositories(tmp_path: Path):
    res = runner.invoke(app, ["init", str(tmp_path)])
    assert res.stdout == f"Initialized wiki in {str(tmp_path)}.\n"


def test_publish_drafts(tmp_path: Path):
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


def test_create_local_copy(tmp_path: Path):
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


def test_add_subscription(tmp_path: Path):
    base = tmp_path.joinpath('base')
    copy = tmp_path.joinpath('copy')
    base.mkdir()
    copy.mkdir()

    runner.invoke(app, ["init", str(base)])
    runner.invoke(app, ["init", str(copy)])
    res = runner.invoke(app, ["subscribe", str(base), str(copy)])

    assert res.stdout == f"Subscribed to {str(base)}.\n"

    res = runner.invoke(app, ["subscriptions", str(copy)])
    assert res.stdout == f"Subscriptions by priority (highest to lowest)\n0\tThis Wiki\n1\t{base.resolve().as_uri()}\n"


def test_view_subscription_update(tmp_path: Path):
    # checks Inbox command
    base = tmp_path.joinpath('base')
    copy = tmp_path.joinpath('copy')
    base.mkdir()
    copy.mkdir()

    update_path = base.joinpath('hello.md').resolve()

    runner.invoke(app, ["init", str(base)])
    runner.invoke(app, ["init", str(copy)])
    runner.invoke(app, ["subscribe", str(base), str(copy)])

    update = 'Hello World!'
    update_path.write_text(update)
    runner.invoke(app, ["publish", str(base)])
    res = runner.invoke(app, ["inbox", str(copy)])
    assert res.stdout == f'{0} {update_path.as_uri()} (+{len(update)})\n'


def test_successful_serve():
    pass


def test_successful_announce():
    pass
