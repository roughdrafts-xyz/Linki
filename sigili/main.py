from pathlib import Path
import typer
from sigili.article.repository import ArticleRepository

from sigili.editor import FileEditor, Subscription
from sigili.title.repository import TitleRepository

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
def subscribe():
    # add a subscription to the subscriptions repository
    typer.echo(f"TODO subscribe")


@app.command()
def serve():
    # run a fastapi server
    # also provides endpoint for receiving announcements
    typer.echo(f"TODO serve")


@app.command()
def announce():
    # add subscribers to announcement list or ping subscribers
    typer.echo(f"TODO announce")


if __name__ == "__main__":
    app()
