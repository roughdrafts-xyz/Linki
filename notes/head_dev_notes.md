probably need this for check out code?
not sure how I wanna structure it
checkout action should probably be part of working directory project
check out _tools_ should be part of this repository for sure

DisplayRepository
LiveRepository
CurrentRepository
CurrentArticleRepository <- this is the one.

Current Article Repository is responsible for helping the checkout and also probably for the web interface.

Don't really know how I'll test the MemoryCAR.

CAR needs to be able to track what the CAs are.
CAR needs to provide CAs or information about them.
