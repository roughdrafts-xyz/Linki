# `linki`

A tool to create distributed wikis, and link them together through subscriptions and contributions.

**Usage**:

```console
$ linki [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `approve`: Accept a change
* `authenticate`: Allow someone to contribute to your linki
* `contribute`: Contribute to a linki!
* `contributions`: DEPRECATED
* `copy`: Replicate another wiki
* `inbox`: See changes from your subscriptions and...
* `init`: This is how you get started!
* `install-pandoc`: Installs pandoc
* `publish`: Write your drafts to the linki.
* `refuse`: Refuse a change
* `serve`: Run a web server!
* `subscribe`: Follow a wiki for updates
* `subscriptions`: DEPRECATED

## `linki approve`

Accept a change

When you run this command pointing at a copy id (the ids to the left side of the inbox command), it'll copy those changes into your wiki.

**Usage**:

```console
$ linki approve [OPTIONS] [COPY_ID]
```

**Arguments**:

* `[COPY_ID]`

**Options**:

* `--location PATH`: [default: /home/zone/Documents/DistWiki/linki]
* `--list / --no-list`: [default: no-list]
* `--help`: Show this message and exit.

## `linki authenticate`

Allow someone to contribute to your linki

This version of linki only allows username and passwords as a way to authenticate a user. Use this command to add a new user to your linki, and they'll be able to send your linki contributions when you run a server with `linki serve`.

**Usage**:

```console
$ linki authenticate [OPTIONS] [LOCATION]
```

**Arguments**:

* `[LOCATION]`: [default: /home/zone/Documents/DistWiki/linki]

**Options**:

* `--user TEXT`: [required]
* `--password TEXT`: [required]
* `--help`: Show this message and exit.

## `linki contribute`

Contribute to a linki!

When you contribute to a linki you can use `linki publish --contribute` to send your changes to linkis that you contribute to. Just add the urls for those linkis to your contributors list by using this command and point it at the root of the linki you're contributing to.

**Usage**:

```console
$ linki contribute [OPTIONS] URL [LOCATION]
```

**Arguments**:

* `URL`: [required]
* `[LOCATION]`: [default: /home/zone/Documents/DistWiki/linki]

**Options**:

* `--username TEXT`
* `--password TEXT`
* `--help`: Show this message and exit.

## `linki contributions`

DEPRECATED

This needs to become `linki contribute --list`

**Usage**:

```console
$ linki contributions [OPTIONS] [LOCATION]
```

**Arguments**:

* `[LOCATION]`: [default: /home/zone/Documents/DistWiki/linki]

**Options**:

* `--help`: Show this message and exit.

## `linki copy`

Replicate another wiki

Do you like something you see on someone else's linki? Go ahead and run this command pointing at the linki you'd like to replicate. It'll copy over the whole linki and all of its history. Its yours to change and host now.

**Usage**:

```console
$ linki copy [OPTIONS] SOURCE [DESTINATION]
```

**Arguments**:

* `SOURCE`: [required]
* `[DESTINATION]`: [default: /home/zone/Documents/DistWiki/linki]

**Options**:

* `--help`: Show this message and exit.

## `linki inbox`

See changes from your subscriptions and contributions

When you make a contribution, its stored in the inbox. When a subscription updates, the changes are stored in the inbox. This lets you view them all or individual changes. You can use `linki approve` or `linki refuse` to choose what you will do with these changes.

**Usage**:

```console
$ linki inbox [OPTIONS] [COPY_ID]
```

**Arguments**:

* `[COPY_ID]`

**Options**:

* `--location PATH`: [default: /home/zone/Documents/DistWiki/linki]
* `--help`: Show this message and exit.

## `linki init`

This is how you get started!

Just go ahead and run it in the folder you want to use as your linki, or give it the destination of where you want your linki.

**Usage**:

```console
$ linki init [OPTIONS] [DESTINATION]
```

**Arguments**:

* `[DESTINATION]`: [default: /home/zone/Documents/DistWiki/linki]

**Options**:

* `--silent / --no-silent`: [default: no-silent]
* `--help`: Show this message and exit.

## `linki install-pandoc`

Installs pandoc

**Usage**:

```console
$ linki install-pandoc [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `linki publish`

Write your drafts to the linki.

When you run this command it takes all your drafts and saves them as titles to your linki. Any overwritten titles get added to your article repository to act as history. You can send out updates to wikis you contribute to using the --contribute flag  

### Titles ###

A title is an article that is on display. They think in paths. On the file system, this is the file's path from the root (the folder you initialized). On the web, this is the file's path in the url.  

### Articles ###

When you publish a title, you create an article. Articles are stored seperately from titles, and they think in ids. Consider them a title's history. On the file system and on the web, this is all encapsulated inside the linki program and commands in it allow you to interact with the articles in a title's history.

**Usage**:

```console
$ linki publish [OPTIONS] [LOCATION]
```

**Arguments**:

* `[LOCATION]`: [default: /home/zone/Documents/DistWiki/linki]

**Options**:

* `--contribute / --no-contribute`: [default: no-contribute]
* `--help`: Show this message and exit.

## `linki refuse`

Refuse a change

When you run this command pointing at a copy id (the ids to the left side of the inbox command), it'll save that id and ignore it when updating the inbox in the future.

**Usage**:

```console
$ linki refuse [OPTIONS] [COPY_ID]
```

**Arguments**:

* `[COPY_ID]`

**Options**:

* `--location PATH`: [default: /home/zone/Documents/DistWiki/linki]
* `--list / --no-list`: [default: no-list]
* `--help`: Show this message and exit.

## `linki serve`

Run a web server!

When you run this, you can have a read-only web interface that displays your articles on the web. You'll need to provide your own machine and url of course, but this will make the process very easy.

You can toggle the api, web views, and linki specific endpoints such as copying and contributing.

To use the web views, you must have pandoc installed. You can install it with `linki install-pandoc`

To accept contributions, you must add contributing users with `linki authenticate` and run this command with the --contribute flag.

**Usage**:

```console
$ linki serve [OPTIONS] [LOCATION]
```

**Arguments**:

* `[LOCATION]`: [default: /home/zone/Documents/DistWiki/linki]

**Options**:

* `--api / --no-api`: [default: api]
* `--web / --no-web`: [default: web]
* `--copy / --no-copy`: [default: copy]
* `--contribute / --no-contribute`: [default: no-contribute]
* `--host TEXT`: [default: localhost]
* `--port INTEGER`: [default: 80]
* `--home PATH`
* `--help`: Show this message and exit.

## `linki subscribe`

Follow a wiki for updates

When you run linki inbox, it will check what you're subscribed to and if that linki has any updates. If it does have any updates, it'll download them to your inbox

**Usage**:

```console
$ linki subscribe [OPTIONS] URL [LOCATION]
```

**Arguments**:

* `URL`: [required]
* `[LOCATION]`: [default: /home/zone/Documents/DistWiki/linki]

**Options**:

* `--help`: Show this message and exit.

## `linki subscriptions`

DEPRECATED

Needs to become subscribe --list

**Usage**:

```console
$ linki subscriptions [OPTIONS] [LOCATION]
```

**Arguments**:

* `[LOCATION]`: [default: /home/zone/Documents/DistWiki/linki]

**Options**:

* `--help`: Show this message and exit.
