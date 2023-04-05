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
    x = 1
    typer.echo(f"Published {x} drafts.")


@app.command()
def copy():
    typer.echo(f"TODO copy")


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
