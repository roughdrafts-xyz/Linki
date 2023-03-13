import click
import os


class _Group(click.Group):
    def invoke(self, ctx):
        ctx.is_help = '--help' in ctx.args
        return super(_Group, self).invoke(ctx)
    pass


@click.group(cls=_Group)
@click.pass_context
def cli(ctx):
    "A Distributed Wiki using a repository structure and made to be familiar to developers and authors. Supports any kind of file, but expects markdown."
    is_init = ctx.invoked_subcommand == 'init'
    is_clone = ctx.invoked_subcommand == 'clone'
    if (ctx.is_help or is_init or is_clone):
        return

    dbExists = os.access('.sigil/sigil.db', os.F_OK)
    if (not dbExists):
        raise click.ClickException(
            'sigil database not found, please run `sigil init`')


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
    from sigil.commandInterfaces.cli.history import getFormattedHistory
    history = getFormattedHistory(file)
    click.echo('Refid \tPath Name')
    click.echo('------\t---------')
    for histor in history:
        click.echo(histor)


@cli.command()
@click.argument('pathname', required=False, default=None, help="Destination to create the repository in. Defaults to the current directory.")
@click.option('--quiet', default=False, help='Suppress output messages.', is_flag=True)
@click.option('--bare', default=False, help="Destination will be the sigil folder instead of the working directory.", is_flag=True)
def init(pathname, quiet, bare):
    "Create a new Sigil repository in the current directory."
    from sigil.commandInterfaces.cli.init import init
    try:
        init(pathname=pathname, bare=bare)
        if not quiet:
            click.echo('.sigil directory initiated')
    except FileExistsError:
        if not quiet:
            click.echo('.sigil directory already exists.')


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


@cli.command()
@click.argument('source', required=True)
@click.argument('destination', required=False)
@click.option('--bare', default=False, help="Destination will be the sigil folder instead of the working directory.", is_flag=True)
def clone(source, destination, bare=False):
    "Copy a repo into a new folder."
    from sigil.remoteInterfaces.LocalCopy import LocalCopy
    lCopy = LocalCopy(source)
    lCopy.clone(dst=destination, bare=bare)
    pass


if (__name__ == '__main__'):
    cli()
