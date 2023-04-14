from pathlib import Path
import typer

from sigili.editor import FileEditor
from sigili.subscription import Inbox, PathSubscriptionRepository
from sigili.title.repository import FileSystemTitleRepository, TitleRepository

app = typer.Typer()


@app.command()
def init(destination: str):
    path = Path(destination).resolve()
    FileEditor.init(path)
    typer.echo(f"Initialized wiki in {destination}.")


@app.command()
def publish(location: str):
    editor = FileEditor.fromPath(Path(location))
    editor.load_drafts()
    x = editor.publish_drafts()
    typer.echo(f"Published {x} drafts.")


@app.command()
def copy(source: str, destination: str):
    # subscription = Subscription.fromPath(Path(source))
    # editor = FileEditor.fromPath(Path(destination))
    # articles_count = editor.copy_articles(subscription.articles)
    # titles_count = editor.copy_titles(subscription.titles)
    # editor.unload_titles()
    titles_count = -1
    articles_count = -1

    typer.echo(f"Copied {titles_count} titles and {articles_count} articles.")


@app.command()
def subscribe(url: str, location: str):
    subscriptions = PathSubscriptionRepository(Path(location))
    _url = Path(url).resolve().as_uri()
    subscriptions.add_sub_url(_url)
    typer.echo(f"Subscribed to {str(url)}.")


@app.command()
def subscriptions(location: str):
    subscriptions = PathSubscriptionRepository(Path(location))
    typer.echo(f"Subscriptions by priority (highest to lowest)")
    priority = 0
    typer.echo(f'{priority}\tThis Wiki')
    for subscription in subscriptions.get_sub_urls():
        priority += 1
        typer.echo(f"{priority}\t{subscription.url}")


@app.command()
def inbox(location: str):
    subscriptions = PathSubscriptionRepository(Path(location))
    titles = FileSystemTitleRepository(Path(location))
    inbox = Inbox(subscriptions, titles)
    for update in inbox.get_inbox():
        typer.echo(
            f"{update.rowId} {update.url.url}{update.label.name} ({update.size:+n})")


@app.command()
def serve():
    # run a fastapi server
    # also provides endpoint for receiving announcements
    typer.echo(f"TODO serve")


@app.command()
def contribute(url: str, location: str):
    typer.echo(f"TODO contribute")


@app.command()
def contributions(url: str, location: str):
    typer.echo(f"TODO contributions")


@app.command()
def announce():
    # add subscribers to announcement list or ping subscribers
    typer.echo(f"TODO announce")


if __name__ == "__main__":
    app()
