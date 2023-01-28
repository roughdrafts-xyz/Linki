import click


@click.group
def cli():
    "A Distributed Wiki using a repository structure and made to be familiar to developers and authors. Supports any kind of file, but expects markdown."
    pass


@cli.command()
@click.option('--quiet', default=False, help='Suppress output messages.', is_flag=True)
def checkout(quiet):
    "Populate the working directory with the repository's wiki."
    from sigil.commandInterfaces.cli.checkout import checkout
    count = checkout()
    if not quiet:
        click.echo(f'Checked out {count} file(s)')


@cli.command()
@click.argument('file', required=True)
def history(file):
    "Show the edit history of the FILE"
    # TODO Fill this in properly
    from sigil.commandInterfaces.cli.history import getFormattedHistory
    history = getFormattedHistory(file)
    click.echo('Refid \tPath Name')
    click.echo('------\t---------')
    for histor in history:
        click.echo(histor)


@cli.command()
@click.option('--quiet', default=False, help='Suppress output messages.', is_flag=True)
def init(quiet):
    "Create a new Sigil repository in the current directory."
    from sigil.commandInterfaces.cli.init import init
    try:
        init()
        if not quiet:
            click.echo('.sigil directory initiated')
    except FileExistsError:
        if not quiet:
            click.echo('.sigil directory already exists.')


@cli.command()
def log():
    "Show recent changes made to the repository"
    # TODO Fill this in properly
    pass


@cli.command()
@click.option('--quiet', default=False, help='Suppress output messages.', is_flag=True)
def publish(quiet):
    "Write every updated file to the repository."
    from sigil.commandInterfaces.cli.publish import publish
    count = publish()
    if not quiet:
        click.echo(f'Added {count[0]} new files.')
        click.echo(f'Updated {count[1]} files.')


@cli.command()
def status():
    "Show updated files that will be written to the repository."
    from sigil.commandInterfaces.cli.status import getStagedChanges
    changes = getStagedChanges()
    if (len(changes) > 0):
        changes = ', '.join(changes)
        click.echo(f'These files will be published: {changes}')
    else:
        click.echo('No files will be published.')


@cli.command()
@click.argument('refid', required=True)
def view(refid):
    "Prints the article associated with the REFID to stdout."
    from sigil.commandInterfaces.cli.view import view
    outp = view(refid)
    click.echo(outp)


if (__name__ == '__main__'):
    cli()
