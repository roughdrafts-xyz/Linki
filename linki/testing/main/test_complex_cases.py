from pathlib import Path
from unittest import TestCase

import requests
from linki.inbox import Inbox

from linki.main import app
from typer.testing import CliRunner

from linki.testing.server.test_happy_path import get_client, get_memory_server

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
    runner.invoke(app, ["copy", str(source), str(copy)])

    test = TestCase()
    s_files = [f.relative_to(source)
               for f in source.iterdir()]
    c_files = [f.relative_to(copy)
               for f in copy.iterdir()]
    test.assertCountEqual(s_files, c_files)


def test_add_http_contribution_with_flags(tmp_path: Path, monkeypatch):
    server = get_memory_server()
    server_url = "https://localhost/"
    client = get_client(server)
    monkeypatch.setattr(requests, "get", client.get)
    username = 'user'
    password = 'pass'
    server.repo.users.add_user(username, password)

    linki = tmp_path.joinpath('client')
    linki.mkdir()
    runner.invoke(app, ["init", str(linki)])
    res = runner.invoke(app, ["contribute", server_url, "--location", str(
        linki), "--username", username, "--password", password])

    assert res.stdout == f"Contributing to {server_url}.\n"

    res = runner.invoke(
        app, ["contribute", "--location", str(linki), "--list"])
    assert res.stdout == f"Contributions by priority (highest to lowest)\n0\tThis Wiki\n1\t{server_url}\n"


def test_add_http_contribution_without_flags(tmp_path: Path, monkeypatch):
    server = get_memory_server()
    server_url = "https://localhost/"
    client = get_client(server)
    monkeypatch.setattr(requests, "get", client.get)
    username = 'user'
    password = 'pass'
    server.repo.users.add_user(username, password)

    linki = tmp_path.joinpath('client')
    linki.mkdir()
    runner.invoke(app, ["init", str(linki)])
    res = runner.invoke(app, ["contribute", server_url, "--location", str(
        linki)], input="user\npass")

    assert res.stdout == ('' +
                          f"Please authenticate\n" +
                          f"Username: user\n" +
                          f"Password: \n"
                          f"Contributing to {server_url}.\n")

    res = runner.invoke(
        app, ["contribute", "--location", str(linki), "--list"])
    assert res.stdout == f"Contributions by priority (highest to lowest)\n0\tThis Wiki\n1\t{server_url}\n"


def test_successful_http_contribute(tmp_path: Path, monkeypatch):
    server = get_memory_server()
    server_url = "https://localhost/"
    client = get_client(server)
    monkeypatch.setattr(requests, "get", client.get)
    monkeypatch.setattr(requests, "post", client.post)
    username = 'user'
    password = 'pass'
    server.repo.users.add_user(username, password)

    linki = tmp_path.joinpath('client')
    linki.mkdir()
    runner.invoke(app, ["init", str(linki)])
    res = runner.invoke(app, ["contribute", server_url, "--location", str(
        linki), "--username", "user", "--password", "pass"])
    update_path = linki.joinpath('hello.md').resolve()

    update = 'Hello World!'
    update_path.write_text(update)

    res = runner.invoke(app, ["publish", str(linki), "--contribute"])
    assert f"Sent contributions to 1 wikis.\n" in res.stdout

    inbox = Inbox(server.repo)
    assert 'hello.md' in ''.join(inbox.render_inbox())
