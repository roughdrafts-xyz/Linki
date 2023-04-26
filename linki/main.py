from pathlib import Path
from typing import Optional
import pypandoc
import typer

from linki.editor import FileCopier, FileEditor
from linki.inbox import Inbox
from linki.outbox import Outbox
from linki.repository import FileRepository, Repository
from linki.viewer import WebView, WebViewConf


app = typer.Typer(
    no_args_is_help=True
)


@app.command()
def init(
    destination: Path = typer.Argument(Path.cwd()),
    silent: bool = typer.Option(False)
):
    if (not destination.exists()):
        destination.mkdir()
    FileRepository.createPath(destination)
    if (not silent):
        typer.echo(f"Initialized wiki in {destination}.")


@app.command()
def publish(
    location: Path = typer.Argument(Path.cwd())
):
    editor = FileEditor.fromPath(location)
    editor.load_drafts()
    x = editor.publish_drafts()
    editor.unload_titles()
    typer.echo(f"Published {x} drafts.")


@app.command()
def copy(source: str, destination: Path = typer.Argument(Path.cwd(), file_okay=False)):
    if (not destination.exists()):
        init(destination, True)
    source_repo = Repository(source)
    copier = FileCopier(source_repo, destination)

    articles_count = copier.copy_articles()
    titles_count = copier.copy_titles()
    copier.unload_titles()

    typer.echo(f"Copied {titles_count} titles and {articles_count} articles.")


@app.command()
def subscribe(url: str, location: Path = typer.Argument(Path.cwd())):
    repo = FileRepository.fromPath(location)
    subs = repo.subs
    subs.add_url(url)
    typer.echo(f"Subscribed to {url}.")


@app.command()
def subscriptions(
    location: Path = typer.Argument(Path.cwd())
):
    repo = FileRepository.fromPath(location)
    subs = repo.subs
    typer.echo(f"Subscriptions by priority (highest to lowest)")
    priority = 0
    typer.echo(f'{priority}\tThis Wiki')
    for subscription in subs.get_urls():
        priority += 1
        typer.echo(f"{priority}\t{subscription.url}")


@app.command()
def inbox(
    location: Path = typer.Argument(Path.cwd()),
    copy_id: Optional[str] = typer.Argument(None)
):
    repo = FileRepository.fromPath(location)
    inbox = Inbox(repo)
    inbox.load_inbox()
    if (copy_id is None):
        output = ''.join(inbox.render_inbox())
    else:
        output = ''.join(inbox.render_copy(copy_id))
    typer.echo(output)


@ app.command()
def serve(
    location: Path = typer.Argument(Path.cwd()),
    api: bool = typer.Option(True),
    web: bool = typer.Option(True),
    copy: bool = typer.Option(True),
    contribute: bool = typer.Option(False),
    debug: bool = typer.Option(False, hidden=True),
    host: str = typer.Option('localhost'),
    port: int = typer.Option(8080),
    home: Optional[Path] = typer.Option(None),
):
    try:
        if (web):
            pypandoc.get_pandoc_path()
        home_str = None
        if (home):
            home = home.resolve().relative_to(Path.cwd().resolve())
            home_str = str(home)
        repo = FileRepository.fromPath(location)
        viewer = WebView(repo, WebViewConf(
            copy=copy,
            contribute=contribute,
            api=api,
            web=web,
            debug=debug,
            home=home_str
        ))

        viewer.run(host, port)
    except OSError:
        typer.echo(
            "Pandoc not found. Run using linki serve --no-web or install pandoc with linki install-pandoc.")
        typer.Exit()


@ app.command(hidden=True)
def install_pandoc():
    try:
        pandoc = pypandoc.get_pandoc_path()
        if (pandoc is not None):
            typer.echo("Pandoc is already installed.")
    except OSError:
        pypandoc.ensure_pandoc_installed()
        typer.echo("Pandoc installed successfully.")


@ app.command()
def contribute(url: str,  location: Path = typer.Argument(Path.cwd())):
    repo = FileRepository.fromPath(location)
    contribs = repo.contribs
    contribs.add_url(url)
    typer.echo(f"Contributing to {url}.")


@ app.command()
def contributions(
    location: Path = typer.Argument(Path.cwd()),
):
    repo = FileRepository.fromPath(location)
    contribs = repo.contribs
    typer.echo(f"Contributions by priority (highest to lowest)")
    priority = 0
    typer.echo(f'{priority}\tThis Wiki')
    for contrib in contribs.get_urls():
        priority += 1
        typer.echo(f"{priority}\t{contrib.url}")


@ app.command()
def announce(
    location: Path = typer.Argument(Path.cwd()),
):
    repo = FileRepository.fromPath(location)
    outbox = Outbox(repo)
    update_count = outbox.send_updates()
    typer.echo(
        f"Sent contributions to {update_count} wikis.")


@ app.command()
def authenticate(
    location: Path = typer.Argument(Path.cwd()),
    user: str = typer.Option(...),
    password: str = typer.Option(..., prompt=True,
                                 hide_input=True, confirmation_prompt=True)
):
    repo = FileRepository.fromPath(location)
    repo.users.add_user(user, password)
    typer.echo(f"Added {user} to list of authorized users.")


def run():
    app()


if __name__ == "__main__":
    app()
