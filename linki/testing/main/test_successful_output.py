from pathlib import Path
from typer.testing import CliRunner
from linki.change import ChangeLabel
from linki.id import Label, SimpleLabel
from linki.main import app

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
    assert tmp_path.joinpath('hello_world.md').read_text() == 'Hello World'

    tmp_path.joinpath('hello_world.md').write_text('Hello World')
    res = runner.invoke(app, ["publish", str(tmp_path)])
    x = 0
    assert res.stdout == f"Published {x} drafts.\n"
    assert tmp_path.joinpath('hello_world.md').read_text() == 'Hello World'

    tmp_path.joinpath('hello_world.md').write_text('Goodnight Moon')
    res = runner.invoke(app, ["publish", str(tmp_path)])
    x = 1
    assert res.stdout == f"Published {x} drafts.\n"
    assert tmp_path.joinpath('hello_world.md').read_text() == 'Goodnight Moon'

    tmp_path.joinpath('good_moon.md').write_text('Goodnight Moon')
    tmp_path.joinpath('hello_world.md').write_text('Hello World')
    res = runner.invoke(app, ["publish", str(tmp_path)])
    x = 2
    assert res.stdout == f"Published {x} drafts.\n"
    assert tmp_path.joinpath('hello_world.md').read_text() == 'Hello World'
    assert tmp_path.joinpath('good_moon.md').read_text() == 'Goodnight Moon'


def test_create_local_linki_copy(tmp_path: Path):
    base = tmp_path.joinpath('base')
    copy = tmp_path.joinpath('copy')
    base.mkdir()
    base.joinpath('folder').mkdir()

    res = runner.invoke(app, ["init", str(base)])
    base.joinpath('folder', 'hello_world.md').write_text('Hello World')
    res = runner.invoke(app, ["publish", str(base)])

    res = runner.invoke(app, ["copy", str(base), str(copy)])
    x = 1
    y = 1
    assert res.stdout == f"Copied {x} titles and {y} articles.\n"

    content = copy.joinpath('folder', 'hello_world.md').read_text()
    assert content == "Hello World"


def test_create_local_group_copy(tmp_path: Path):
    base = tmp_path.joinpath('base')
    copy = tmp_path.joinpath('copy')
    base.mkdir()
    base.joinpath('folder').mkdir()

    res = runner.invoke(app, ["init", str(base)])
    group = base.joinpath('folder')
    group.joinpath('hello_world.md').write_text('Hello World')
    group.joinpath('moon_night.md').write_text('Hello Moon')
    res = runner.invoke(app, ["publish", str(base)])

    res = runner.invoke(app, ["copy", str(group), str(copy)])
    x = 2
    y = 2
    assert res.stdout == f"Copied {x} titles and {y} articles.\n"

    content = copy.joinpath('folder', 'hello_world.md').read_text()
    assert content == "Hello World"


def test_create_local_article_copy(tmp_path: Path):
    base = tmp_path.joinpath('base')
    copy = tmp_path.joinpath('copy')
    base.mkdir()
    base.joinpath('folder').mkdir()

    res = runner.invoke(app, ["init", str(base)])
    article = base.joinpath('folder')
    article.joinpath('moon_night.md').write_text('Hello Moon')
    article = article.joinpath('hello_moon.md')
    article.write_text('Hello World')
    res = runner.invoke(app, ["publish", str(base)])

    res = runner.invoke(app, ["copy", str(article), str(copy)])
    x = 1
    y = 1
    assert res.stdout == f"Copied {x} titles and {y} articles.\n"

    content = copy.joinpath('folder', 'hello_moon.md').read_text()
    assert content == "Hello World"


def test_refuse_contribution(tmp_path: Path):
    base = tmp_path.joinpath('base')
    copy = tmp_path.joinpath('copy')
    base.mkdir()
    copy.mkdir()

    update_path = base.joinpath('hello.md').resolve()

    runner.invoke(app, ["init", str(base)])
    runner.invoke(app, ["init", str(copy)])
    runner.invoke(app, ["subscribe", "--location", str(copy), str(base)])

    update = 'Hello World!'
    update_path.write_text(update)
    runner.invoke(app, ["publish", str(base)])
    inbox_id = Label([base.as_uri(), 'hello.md']).labelId[0:7]
    runner.invoke(app, ["inbox", "--location", str(copy)])
    res = runner.invoke(app, ["refuse", "--location", str(copy), inbox_id])
    assert res.stdout == f"Refusing contribution {inbox_id}\n"
    res = runner.invoke(app, ["refuse", "--location", str(copy), "--list"])
    assert inbox_id in res.output


def test_approve_contribution(tmp_path: Path):
    base = tmp_path.joinpath('base')
    copy = tmp_path.joinpath('copy')
    base.mkdir()
    copy.mkdir()

    update_path = base.joinpath('hello.md').resolve()

    runner.invoke(app, ["init", str(base)])
    runner.invoke(app, ["init", str(copy)])
    runner.invoke(app, ["subscribe", "--location", str(copy), str(base)])

    update = 'Hello World!'
    update_path.write_text(update)
    runner.invoke(app, ["publish", str(base)])
    inbox_id = Label([base.as_uri(), 'hello.md']).labelId[0:7]
    runner.invoke(app, ["inbox", "--location", str(copy)])
    res = runner.invoke(app, ["approve", "--location", str(copy), inbox_id])
    assert res.stdout == f"Approving contribution {inbox_id}\n"
    res = runner.invoke(app, ["approve", "--location", str(copy), "--list"])
    assert inbox_id in res.output


def test_add_subscription(tmp_path: Path):
    base = tmp_path.joinpath('base')
    copy = tmp_path.joinpath('copy')
    base.mkdir()
    copy.mkdir()

    runner.invoke(app, ["init", str(base)])
    runner.invoke(app, ["init", str(copy)])
    res = runner.invoke(app, ["subscribe", "--location", str(copy), str(base)])

    assert res.stdout == f"Subscribed to {str(base)}.\n"

    res = runner.invoke(app, ["subscribe", "--location", str(copy), "--list"])
    assert res.stdout == f"Subscriptions by priority (highest to lowest)\n0\tThis Wiki\n1\t{base.resolve().as_uri()}\n"


def test_view_inbox_updates(tmp_path: Path):
    base = tmp_path.joinpath('base')
    copy = tmp_path.joinpath('copy')
    base.mkdir()
    copy.mkdir()

    update_path = base.joinpath('hello.md').resolve()

    runner.invoke(app, ["init", str(base)])
    runner.invoke(app, ["init", str(copy)])
    runner.invoke(app, ["subscribe", "--location", str(copy), str(base)])

    update = 'Hello World!'
    update_path.write_text(update)
    runner.invoke(app, ["publish", str(base)])
    res = runner.invoke(app, ["inbox", "--location", str(copy)])

    inbox_id = SimpleLabel(update_path.as_uri()).labelId[0:7]
    update_path = update_path.relative_to(base)
    assert res.stdout == (''
                          + f'{base.as_uri()}\n'
                          + f'└┤{inbox_id}├ {update_path} (+{len(update)})\n'
                          )


def test_view_inbox_update_details(tmp_path: Path):
    base = tmp_path.joinpath('base')
    copy = tmp_path.joinpath('copy')
    base.mkdir()
    copy.mkdir()

    update_path = base.joinpath('hello.md').resolve()

    runner.invoke(app, ["init", str(base)])
    runner.invoke(app, ["init", str(copy)])
    runner.invoke(app, ["subscribe", "--location", str(copy), str(base)])

    update = 'Hello World!'
    update_path.write_text(update)
    runner.invoke(app, ["publish", str(base)])

    inbox_id = SimpleLabel(update_path.as_uri()).labelId[0:7]
    update_path = update_path.relative_to(base)
    res = runner.invoke(app, ["inbox", "--location", str(copy), inbox_id])
# ```
# │d507cef│ hello.md (+12)
# ├───────┴───────────────
# ╎--- Removes
# ╎+++ Adds
# ╎@@ -1,3 +1,3 @@
# ╎Great Story
# ╎-Hello Moon
# ╎+Hello World
# ╎Finale
# ├────────────────────────
# └file:///tmp/pytest-of-zone/pytest-168/test_view_inbox_update_details0/base
# ```
    header_left = f'│{inbox_id}│'
    header_right = f'{update_path} (+{len(update)})'
    header = f'{header_left} {header_right}\n'

    line_left = '─' * (len(header_left)-2)
    line_right = '─' * len(header_right)
    line_top = f'├{line_left}┴{line_right}\n'
    line_bottom = f'├{line_left}─{line_right}\n'
    output = (''
              + header
              + line_top
              + '╎--- Removes\n'
              + '╎+++ Adds\n'
              + '╎@@ -0,0 +1 @@\n'
              + '╎+Hello World!\n'
              + line_bottom
              + f'└{base.as_uri()}\n'
              )
    assert res.stdout == output


def test_add_contribution(tmp_path: Path):
    base = tmp_path.joinpath('base')
    copy = tmp_path.joinpath('copy')
    base.mkdir()
    copy.mkdir()

    runner.invoke(app, ["init", str(base)])
    runner.invoke(app, ["init", str(copy)])
    res = runner.invoke(
        app, ["contribute", "--location", str(copy), str(base)])

    assert res.stdout == f"Contributing to {str(base)}.\n"

    res = runner.invoke(app, ["contribute", "--location", str(copy), "--list"])
    assert res.stdout == f"Contributions by priority (highest to lowest)\n0\tThis Wiki\n1\t{base.resolve().as_uri()}\n"


def test_successful_contribute(tmp_path: Path):
    base = tmp_path.joinpath('base')
    copy = tmp_path.joinpath('copy')
    base.mkdir()
    copy.mkdir()

    update_path = copy.joinpath('hello.md').resolve()

    runner.invoke(app, ["init", str(base)])
    runner.invoke(app, ["init", str(copy)])
    runner.invoke(app, ["contribute", "--location", str(copy), str(base)])

    update = 'Hello World!'
    update_path.write_text(update)

    res = runner.invoke(app, ["publish", str(copy), "--contribute"])
    assert f"Sent contributions to 1 wikis.\n" in res.stdout

    res = runner.invoke(app, ["inbox", "--location", str(base)])
    assert 'hello.md' in res.stdout


def test_auth_user_with_flags(tmp_path: Path):
    base = tmp_path.joinpath('base')
    runner.invoke(app, ["init", str(base)])
    user = 'username'
    res = runner.invoke(app, ['authenticate', str(
        base), '--user', user, '--password', 'pass'])
    assert res.stdout == f"Added {user} to list of authorized users.\n"


def test_auth_user_without_flags(tmp_path: Path):
    base = tmp_path.joinpath('base')
    runner.invoke(app, ["init", str(base)])
    user = 'username'
    password = 'pass'
    res = runner.invoke(app, ['authenticate', str(
        base), '--user', user], input=f'{password}\n{password}\n')
    assert res.stdout == (''
                          + f"Password: \n"
                          + f"Repeat for confirmation: \n"
                          + f"Added {user} to list of authorized users.\n")
