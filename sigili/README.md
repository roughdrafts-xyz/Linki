# Sigili

> A library to create a Distributed Wiki.

You're looking at the workhorse library that makes the whole thing work.

If you wanna use it for your own project, install it with `pip install sigili`

```mermaid
erDiagram
    User}|--|{Editor: Uses
    Editor}|--|{Wiki: Edits
    Editor||..||"Command Line":"Can Be"
    Editor||..||"Web Interface":"Can Be"
    Editor||..||"Phone App":"Can Be"
```

High-level view, a User uses an editor to manage a wiki. The editor includes drafting tools, wiki management tools, and the things necessary for a distributed service to work like remote repository management.

An editor can be anything that can talk to a wiki. Check out sigili-cli if you'd like to use something familiar to git. Check out roughdrafts.xyz if you'd like to see a web host for it.

```mermaid
erDiagram
    Wiki ||--|{ "Article Repositories": "Collates"
    Wiki ||--|{ "Article Repositories": "Manages"
    Wiki ||--|{ "Article Repositories": "Clones"
    "Article Repositories"||..||"Local": "Can Be"
    "Article Repositories"||..||"Remote": "Can Be"
```

A wiki is just a library that manages and collates article repositories. You can find this in sigili/wiki.py

```mermaid
erDiagram
    "Article Repositories"||--||Content: Manage
    "Article Repositories"||--||"Article Repositories": Manage
    "Article Repositories"||--||History: Manage
    "Article Repositories"||--||Group: Manage
    "Article Repositories"||--||"Storage Interface": "Records On"
    History}|--o{"Storage Interface":"Records On"
    Content}|--o{"Storage Interface":"Records On"
    Group}|--o{"Storage Interface":"Records On"
```

An article repository receives commands from a wiki, and then manages everything from there. This is just instructing different services on top of storage interfaces. You can see the repository types and their services in sigili/article/

```mermaid
erDiagram
    "Storage Interface"||..||"File System":"Can Be"
    "Storage Interface"||..||"Memory":"Can Be"
    "Storage Interface"||..||"SSH Connection":"Can Be"
    "Storage Interface"||..||"API Connection":"Can Be"
    "Storage Interface"||..||"Plugins":"Can Be"
```

A storage interface can be a large number of things - If it can be written and read from, it can be used as a storage interface. An Article Repository's services can all be connected to different storage interfaces as well.

Interaction with a storage interface is implemented via the services located in sigili/article.
