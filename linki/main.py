from pathlib import Path
import typer

from linki.editor import FileCopier, FileEditor
from linki.inbox import Inbox
from linki.outbox import Outbox
from linki.repository import FileRepository, Repository
from linki.viewer import WebView, WebViewConf

app = typer.Typer()


@app.command()
def init(destination: str):
    path = Path(destination).resolve().as_uri()
    Repository.create(path)
    typer.echo(f"Initialized wiki in {destination}.")


@app.command()
def publish(location: str):
    editor = FileEditor.fromPath(location)
    editor.load_drafts()
    x = editor.publish_drafts()
    typer.echo(f"Published {x} drafts.")


@app.command()
def copy(source: str, destination: str):
    source_repo = FileRepository.fromPath(source)
    copier = FileCopier(source_repo, destination)
    articles_count = copier.copy_articles()
    titles_count = copier.copy_titles()
    copier.unload_titles()

    typer.echo(f"Copied {titles_count} titles and {articles_count} articles.")


@app.command()
def subscribe(url: str, location: str):
    repo = FileRepository.fromPath(location)
    subs = repo.subs
    sub_url = Path(url).resolve().as_uri()
    subs.add_url(sub_url)
    typer.echo(f"Subscribed to {str(url)}.")


@app.command()
def subscriptions(location: str):
    repo = FileRepository.fromPath(location)
    subs = repo.subs
    typer.echo(f"Subscriptions by priority (highest to lowest)")
    priority = 0
    typer.echo(f'{priority}\tThis Wiki')
    for subscription in subs.get_urls():
        priority += 1
        typer.echo(f"{priority}\t{subscription.url}")


@app.command()
def inbox(location: str):
    repo = FileRepository.fromPath(location)
    subs = repo.subs
    titles = repo.titles
    inbox = Inbox(subs, titles)
    for update in inbox.get_inbox():
        typer.echo(
            f"{update.rowId} {update.url.url}/{update.label.name} ({update.size:+n})")


@app.command()
def serve(location: str):
    print("hi")
    repo = FileRepository.fromPath(location)
    viewer = WebView(repo, WebViewConf(
        sub=True,
        api=True,
        web=True
    ))

    viewer.run(host='localhost', port=8080)


@app.command()
def contribute(url: str, location: str):
    repo = FileRepository.fromPath(location)
    contribs = repo.contribs
    contrib_url = Path(url).resolve().as_uri()
    contribs.add_url(contrib_url)
    typer.echo(f"Contributing to {str(url)}.")


@app.command()
def contributions(location: str):
    repo = FileRepository.fromPath(location)
    contribs = repo.contribs
    typer.echo(f"Contributions by priority (highest to lowest)")
    priority = 0
    typer.echo(f'{priority}\tThis Wiki')
    for contrib in contribs.get_urls():
        priority += 1
        typer.echo(f"{priority}\t{contrib.url}")


@app.command()
def announce(location: str):
    # add subscribers to announcement list or ping subscribers
    repo = FileRepository.fromPath(location)
    outbox = Outbox(repo)
    update_count = outbox.send_updates()
    typer.echo(
        f"Announced updates to {update_count} wikis you're contributing to.")


if __name__ == "__main__":
    app()
