from pathlib import Path
from typing import Optional
from typing_extensions import Annotated
import pypandoc
import typer
from linki.contribution import Contribution

from linki.editor import FileCopier, FileEditor
from linki.inbox import Inbox
from linki.outbox import Outbox
from linki.repository import FileRepository, Repository
from linki.viewer import WebView, WebViewConf
from linki import __version__

app = typer.Typer(
    no_args_is_help=True,
    add_help_option=False,
    add_completion=False,
    help="A tool to create distributed wikis, and link them together through subscriptions and contributions.",
)


@app.command()
def init(
    destination: Path = typer.Argument(Path.cwd()),
    silent: bool = typer.Option(False)
):
    """
    This is how you get started!

    Just go ahead and run it in the folder you want to use as your linki, or give it the destination of where you want your linki.
    """
    if (not destination.exists()):
        destination.mkdir()
    FileRepository.createPath(destination)
    if (not silent):
        typer.echo(f"Initialized wiki in {destination}.")


@app.command()
def publish(
    location: Path = typer.Argument(Path.cwd()),
    contribute: bool = typer.Option(False)
):
    """
    Write your drafts to the linki.

    When you run this command it takes all your drafts and saves them as titles to your linki. Any overwritten titles get added to your article repository to act as history. You can send out updates to wikis you contribute to using the --contribute flag  

    ### Titles ###

    A title is an article that is on display. They think in paths. On the file system, this is the file's path from the root (the folder you initialized). On the web, this is the file's path in the url.  

    ### Articles ###

    When you publish a title, you create an article. Articles are stored seperately from titles, and they think in ids. Consider them a title's history. On the file system and on the web, this is all encapsulated inside the linki program and commands in it allow you to interact with the articles in a title's history.
    """
    editor = FileEditor.fromPath(location)
    editor.load_drafts()
    x = editor.publish_drafts()
    editor.unload_titles()
    typer.echo(f"Published {x} drafts.")
    if (contribute):
        outbox = Outbox(editor.repo)
        update_count = outbox.send_updates()
        typer.echo(
            f"Sent contributions to {update_count} wikis.")


@app.command()
def copy(source: str, destination: Path = typer.Argument(Path.cwd(), file_okay=False)):
    """
    Replicate another wiki

    Do you like something you see on someone else's linki? Go ahead and run this command pointing at the linki you'd like to replicate. It'll copy over the whole linki and all of its history. Its yours to change and host now.
    """
    if (not destination.exists()):
        init(destination, True)
    source_repo = Repository(source)
    copier = FileCopier(source_repo, destination)

    articles_count = copier.copy_articles()
    titles_count = copier.copy_titles()
    copier.unload_titles()

    typer.echo(f"Copied {titles_count} titles and {articles_count} articles.")


@app.command()
def subscribe(
    location: Path = typer.Option(Path.cwd()),
    url: str = typer.Argument(None),
    list: bool = typer.Option(False),
):
    """
    Follow a wiki for updates

    When you run linki inbox, it will check what you're subscribed to and if that linki has any updates. If it does have any updates, it'll download them to your inbox
    """
    editor = FileEditor.fromPath(location)
    if (list):
        typer.echo(f"Subscriptions by priority (highest to lowest)")
        typer.echo(editor.repo.subs.render_urls())
    else:
        subs = editor.repo.subs
        subs.add_url(url)
        typer.echo(f"Subscribed to {url}.")


@app.command()
def inbox(
    location: Path = typer.Option(Path.cwd()),
    copy_id: Optional[str] = typer.Argument(None)
):
    """
    See changes from your subscriptions and contributions

    When you make a contribution, its stored in the inbox. When a subscription updates, the changes are stored in the inbox. This lets you view them all or individual changes. You can use `linki approve` or `linki refuse` to choose what you will do with these changes.
    """
    repo = FileRepository.fromPath(location)
    inbox = Inbox(repo)
    inbox.load_inbox()
    if (copy_id is None):
        output = ''.join(inbox.render_inbox())
    else:
        output = ''.join(inbox.render_copy(copy_id))
    typer.echo(output)


@app.command()
def refuse(
    location: Path = typer.Option(Path.cwd()),
    copy_id: str = typer.Argument(None),
    list: bool = typer.Option(False)
):
    """
    Refuse a change

    When you run this command pointing at a copy id (the ids to the left side of the inbox command), it'll save that id and ignore it when updating the inbox in the future.
    """
    repo = FileRepository.fromPath(location)
    if (list):
        typer.echo(repo.config.render_refusals())
    else:
        inbox = Inbox(repo)
        inbox.refuse(copy_id)
        repo.config.add_refusal(copy_id)
        typer.echo(f"Refusing contribution {copy_id}")


@app.command()
def approve(
    location: Path = typer.Option(Path.cwd()),
    copy_id: str = typer.Argument(None),
    list: bool = typer.Option(False)
):
    """
    Accept a change

    When you run this command pointing at a copy id (the ids to the left side of the inbox command), it'll copy those changes into your wiki.
    """
    editor = FileEditor.fromPath(location)
    if (list):
        typer.echo(editor.repo.config.render_approvals())
    else:
        inbox = Inbox(editor.repo)
        inbox.approve(copy_id)
        editor.unload_titles()
        typer.echo(f"Approving contribution {copy_id}")


@ app.command()
def serve(
    location: Path = typer.Argument(Path.cwd()),
    api: bool = typer.Option(True),
    web: bool = typer.Option(True),
    copy: bool = typer.Option(True),
    contribute: bool = typer.Option(False),
    debug: bool = typer.Option(False, hidden=True),
    host: str = typer.Option('localhost'),
    port: int = typer.Option(80),
    home: Annotated[Optional[Path], typer.Option()] = None,
):
    """
    Run a web server!

    When you run this, you can have a read-only web interface that displays your articles on the web. You'll need to provide your own machine and url of course, but this will make the process very easy.

    You can toggle the api, web views, and linki specific endpoints such as copying and contributing.

    To use the web views, you must have pandoc installed. You can install it with `linki install-pandoc`

    To accept contributions, you must add contributing users with `linki authenticate` and run this command with the --contribute flag.
    """
    if (web):
        try:
            pypandoc.get_pandoc_path()
        except OSError:
            typer.echo(
                "Pandoc not found. Run using linki serve --no-web or install pandoc with linki install-pandoc.")
            typer.Exit()
    home_str = None
    if (home is not None):
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


@ app.command(hidden=True)
def install_pandoc():
    """
    Installs pandoc
    """
    try:
        pandoc = pypandoc.get_pandoc_path()
        if (pandoc is not None):
            typer.echo("Pandoc is already installed.")
    except OSError:
        pypandoc.ensure_pandoc_installed()
        typer.echo("Pandoc installed successfully.")


@ app.command()
def contribute(
    url: str = typer.Argument(None),
    location: Path = typer.Option(Path.cwd()),
    username: Optional[str] = typer.Option(None),
    password: Optional[str] = typer.Option(None),
    list: bool = typer.Option(False)
):
    """
    Contribute to a linki!

    When you contribute to a linki you can use `linki publish --contribute` to send your changes to linkis that you contribute to. Just add the urls for those linkis to your contributors list by using this command and point it at the root of the linki you're contributing to.
    """
    repo = FileRepository.fromPath(location)
    if (list):
        typer.echo(f"Contributions by priority (highest to lowest)")
        typer.echo(repo.contribs.render_urls())
        pass
    else:
        new_url = repo.contribs.add_url(url)
        if (new_url.parsed.scheme == 'https'):
            contrib = Contribution(repo, new_url)
            if (not username or not password):
                typer.echo("Please authenticate")
            while (not username):
                username = typer.prompt('Username')
            while (not password):
                password = typer.prompt('Password', hide_input=True)

            if (not contrib.authenticate(url, username, password)):
                return typer.echo("Username or Password was incorrect")
            repo.config.add_auth(new_url, username, password)
        typer.echo(f"Contributing to {url}.")


@ app.command()
def authenticate(
    location: Path = typer.Argument(Path.cwd()),
    user: str = typer.Option(...),
    password: str = typer.Option(..., prompt=True,
                                 hide_input=True, confirmation_prompt=True)
):
    """
    Allow someone to contribute to your linki

    This version of linki only allows username and passwords as a way to authenticate a user. Use this command to add a new user to your linki, and they'll be able to send your linki contributions when you run a server with `linki serve`.
    """
    repo = FileRepository.fromPath(location)
    repo.users.add_user(user, password)
    typer.echo(f"Added {user} to list of authorized users.")


@app.command(hidden=True)
def version():
    typer.echo(f"linki v{__version__}")
