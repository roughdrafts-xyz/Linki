from pathlib import Path
import typer

from sigili.editor import FileEditor
from sigili.subscription import PathSubscriptionRepository, Subscription

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
    subscription = Subscription.fromPath(Path(source))
    editor = FileEditor.fromPath(Path(destination))
    articles_count = editor.copy_articles(subscription.articles)
    titles_count = editor.copy_titles(subscription.titles)
    editor.unload_titles()

    typer.echo(f"Copied {titles_count} titles and {articles_count} articles.")


@app.command()
def subscribe(url: str, location: str):
    subscriptions = PathSubscriptionRepository(Path(location))
    _url = Path(url).resolve().as_uri()
    subscriptions.add_subscription(_url)
    typer.echo(f"Subscribed to {str(url)}.")


@app.command()
def subscriptions(location: str):
    subscriptions = PathSubscriptionRepository(Path(location))
    typer.echo(f"Subscriptions by priority (highest to lowest)")
    priority = 0
    typer.echo(f'{priority}\tThis Wiki')
    for subscription in subscriptions.get_subscriptions():
        priority += 1
        _subscription = subscriptions.get_subscription(subscription)
        if (_subscription is None):
            continue
        typer.echo(f"{priority}\t{_subscription.url}")


@app.command()
def inbox(location: str):
    # tells you what wikis have updates
    subscriptions = PathSubscriptionRepository(Path(location))
    for update in subscriptions.get_updates():
        typer.echo(f"{update.labelId} {update.url} ({update.size:+g})")


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
