from pathlib import Path
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
    destination: Path = typer.Argument(Path.cwd())
):
    FileRepository.createPath(destination)
    typer.echo(f"Initialized wiki in {destination}.")


@app.command()
def publish(
    location: Path = typer.Argument(Path.cwd())
):
    editor = FileEditor.fromPath(location)
    editor.load_drafts()
    x = editor.publish_drafts()
    typer.echo(f"Published {x} drafts.")


@app.command()
def copy(source: str, destination: Path = typer.Argument(Path.cwd())):
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
    location: Path = typer.Argument(Path.cwd())
):
    repo = FileRepository.fromPath(location)
    subs = repo.subs
    titles = repo.titles
    inbox = Inbox(subs, titles)
    for update in inbox.get_inbox():
        typer.echo(
            f"{update.rowId} {update.url.url}/{update.label.name} ({update.size:+n})")


@app.command()
def serve(
    location: Path = typer.Argument(Path.cwd()),
    api: bool = typer.Option(True),
    web: bool = typer.Option(True),
    subscribe: bool = typer.Option(True)
):
    repo = FileRepository.fromPath(location)
    viewer = WebView(repo, WebViewConf(
        sub=subscribe,
        api=api,
        web=web
    ))

    viewer.run(host='localhost', port=8080)


@app.command()
def contribute(url: str,  location: Path = typer.Argument(Path.cwd())):
    repo = FileRepository.fromPath(location)
    contribs = repo.contribs
    contribs.add_url(url)
    typer.echo(f"Contributing to {url}.")


@app.command()
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


@app.command()
def announce(
    location: Path = typer.Argument(Path.cwd()),
):
    # add subscribers to announcement list or ping subscribers
    repo = FileRepository.fromPath(location)
    outbox = Outbox(repo)
    update_count = outbox.send_updates()
    typer.echo(
        f"Announced updates to {update_count} wikis you're contributing to.")


def run():
    try:
        app()
    except Exception as e:
        typer.echo(e)


if __name__ == "__main__":
    run()
