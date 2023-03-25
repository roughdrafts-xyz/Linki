# Sigili

> A library to create a Distributed Wiki.

```
pip install sigili
```

## What is Sigili?

A distributed wiki concept and a library implementing them. By replicating files using deterministic identifiers, we can have all the benefits of a wiki and a distributed repository. This means no central host. This means peer-to-peer replication.

## Who is this for?

Anyone who would benefit from distributed documentation. While making this I had Activists, Collaborative Fiction Authors, Developers, and Fandoms in mind. People who are either already familiar with distributed concepts or those who have been burned from centralized document storage.

## How do I use this?

Sigili is more of a set of concepts to allow for consistent data replication and history of data. This repository offers a library to help build tools with that concept. If you want to develop on top of it, install this library. If you want to use it, install sigili-cli.

```
pip install sigili-cli
```

# How does this work?

## Users and Editors

```mermaid
erDiagram
EDITOR}|--|{WIKI: edits
COMMAND-LINE}|..|{EDITOR: is
WEB-INTERFACE}|..|{EDITOR: is
PHONE-APP}|..|{EDITOR: is
```

High-level view, a User uses an editor to manage a wiki. The editor includes drafting tools, wiki management tools, and the things necessary for a distributed service to work like remote repository management.

An editor can be anything that can talk to a wiki. Check out sigili-cli if you'd like to use something familiar to git. Check out roughdrafts.xyz if you'd like to see a web host for it.

## Wikis and Articles

```mermaid
erDiagram
WIKI ||--|{ ARTICLE-REPOSITORIES: collates
WIKI ||--|{ ARTICLE-REPOSITORIES: manages
WIKI ||--|{ ARTICLE-REPOSITORIES: clones
ARTICLE-REPOSITORIES||..||LOCALLY: located
ARTICLE-REPOSITORIES||..||REMOTELY: located
ARTICLE-REPOSITORIES}|--o{ARTICLES: contain
```

A wiki is just a library that manages and collates article repositories. You can find this in sigili/wiki.py

## Articles and their services

```mermaid
erDiagram
CONTENT||--||ARTICLES: comprise
HISTORY||--||ARTICLES: comprise
GROUPS||--||ARTICLES: comprise
STORAGE-INTERFACE}o--|{HISTORY: store
STORAGE-INTERFACE}o--|{GROUPS: store
STORAGE-INTERFACE}o--|{CONTENT: store
```

An article repository receives commands from a wiki, and then manages everything from there. This is just instructing different services on top of storage interfaces. You can see the repository types and their services in sigili/article/

## Examples of Storage Interfaces

```mermaid
erDiagram
FILE-SYSTEM||..||STORAGE-INTERFACE:is
MEMORY||..||STORAGE-INTERFACE: is
SSH-CONNECTION||..||STORAGE-INTERFACE: is
API-CONNECTION||..||STORAGE-INTERFACE: is
PLUGIN||..||STORAGE-INTERFACE: is
```

A storage interface can be a large number of things - If it can be written and read from, it can be used as a storage interface. An Article Repository's services can all be connected to different storage interfaces as well.

Interaction with a storage interface is implemented via the services located in sigili/article.

## Titles

A Wiki knows what articles it has on display! It calls these titles. Every title has many articles, but an article can only belong to a single title.

```mermaid
erDiagram
WIKI}|--|{TITLE: displays
ARTICLE-REPOSITORY}|--|{ARTICLE: track
TITLE-REPOSITORY}|--|{TITLE: track
TITLE||--|{ARTICLE: represent
```

Since articles and content get their ids deterministically, multiple wikis can display the same titles without a central service tracking them.

### Article ID

```mermaid
erDiagram
CONTENT||--||ARTICLE: identify
TITLE||--||ARTICLE: identify
EDIT-OF||--||ARTICLE: identify
```

Articles have an identification code. Content does as well, to help cut down on storage used. An Article's ID is created from the title's name, the content's id, and the id of the article that the article is an edit of.

This helps to provide an edit history that can account for changes in title or content.

## What does Sigili mean?

I wanted to use the name Sigil, but a popular library on pypi already uses that. Sigili is the plural of Sigil. Sigils are representations of concepts. I like that.

A collection of representations of concepts.
