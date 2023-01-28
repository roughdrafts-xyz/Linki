use: sigil [<args>]

# Sigil

A Distributed Wiki using a repository structure and made to be familiar to developers and authors. Supports any kind of file, but expects markdown.

## basic commands

init
: Create a new Sigil repository in the current directory.

publish
: Write every updated file to the repository.

checkout
: Populate the working directory with the repository's wiki.

copy <uri>
: Copy an edit from another repository.

clone <uri>
: Copy an existing repository.

status
: Show updated files that will be written to the repository.

history <file>
: Show the edit history of the <file>.

view <refid>
: Prints the article associated with the <refid> to stdout.

serve <port>
: Serve a simple web version of the wiki.
