# Editing Context or Program

Working Directory (Folder), Web API, etc

- CommandLine (for concrete usage)
- WebFrontend (Not for this iteration, but for editing over http with WebRemote)
- Testing? (automated tests)

Editors have a _list of remotes_ that they _sync to_ when you _publish_.

# Remote Strategy

Stuff that calls the Storage

- TemporaryRemote (for testing) _calls LocalStorage with temporary dir and memory sqlite_
- LocalRemote (for actual use and concrete testing)
- WebRemote (Not for this iteration, but for talking to other wikis over http - Might be Fast API)

# Storage Strategy

Files, Databases, etc

- LocalStorage (folder based storage with sqlite for history)
- DatabaseStorage (??? Not for this iteration, but something that makes multi-tenancy in an API easier)

:: Might be a good idea to consider splitting this further into Diff Strategy and History Strategy
