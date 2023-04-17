from pathlib import Path
import typer

from linki.editor import FileEditor
from linki.inbox import Inbox
from linki.repository import Repository
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
    path = Path(source).resolve().as_uri()
    repo = Repository(path)
    editor = FileEditor.fromPath(destination)
    articles_count = editor.copy_articles(repo.articles)
    titles_count = editor.copy_titles(repo.titles)
    editor.unload_titles()

    typer.echo(f"Copied {titles_count} titles and {articles_count} articles.")


@app.command()
def subscribe(url: str, location: str):
    path = Path(location).resolve().as_uri()
    repo = Repository(path)
    subs = repo.subs
    sub_url = Path(url).resolve().as_uri()
    subs.add_url(sub_url)
    typer.echo(f"Subscribed to {str(url)}.")


@app.command()
def subscriptions(location: str):
    path = Path(location).resolve().as_uri()
    repo = Repository(path)
    subs = repo.subs
    typer.echo(f"Subscriptions by priority (highest to lowest)")
    priority = 0
    typer.echo(f'{priority}\tThis Wiki')
    for subscription in subs.get_urls():
        priority += 1
        typer.echo(f"{priority}\t{subscription.url}")


@app.command()
def inbox(location: str):
    path = Path(location).resolve().as_uri()
    repo = Repository(path)
    subs = repo.subs
    titles = repo.titles
    inbox = Inbox(subs, titles)
    for update in inbox.get_inbox():
        typer.echo(
            f"{update.rowId} {update.url.url}/{update.label.name} ({update.size:+n})")


@app.command()
def serve(location: str):
    print("hi")
    path = Path(location).resolve().as_uri()
    repo = Repository(path)
    viewer = WebView(repo, WebViewConf(
        sub=True,
        api=True,
        web=True
    ))

    viewer.run(host='localhost', port=8080)


@app.command()
def contribute(url: str, location: str):
    path = Path(location).resolve().as_uri()
    repo = Repository(path)
    contribs = repo.contribs
    contrib_url = Path(url).resolve().as_uri()
    contribs.add_url(contrib_url)
    typer.echo(f"Contributing to {str(url)}.")


@app.command()
def contributions(location: str):
    path = Path(location).resolve().as_uri()
    repo = Repository(path)
    contribs = repo.contribs
    typer.echo(f"contributions by priority (highest to lowest)")
    priority = 0
    typer.echo(f'{priority}\tThis Wiki')
    for contrib in contribs.get_urls():
        priority += 1
        typer.echo(f"{priority}\t{contrib.url}")


@app.command()
def announce():
    # add subscribers to announcement list or ping subscribers
    typer.echo(f"TODO announce")


if __name__ == "__main__":
    app()
