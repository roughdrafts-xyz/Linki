from pathlib import Path
import typer

from sigili.editor import FileEditor

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
    _destination = Path(destination)
    _destination.joinpath('hello_world.md').write_text('Hello World')
    typer.echo(f"Copied 1 titles and 1 articles.")


@app.command()
def subscribe():
    typer.echo(f"TODO subscribe")


@app.command()
def serve():
    typer.echo(f"TODO serve")


@app.command()
def announce():
    typer.echo(f"TODO announce")


if __name__ == "__main__":
    app()
