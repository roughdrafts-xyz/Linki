from dataclasses import dataclass


@dataclass
class RefItem:
    refId: str
    # TODO This shouldn't be a path, exactly. It should be a list of groups and the name of the file should be its own thing.
    # If this is just a list of groups, then the groups can care about what group they're part of. Make a GroupItem or something for that or store Groups as refs like we're planning to with comments later.
    pathName: str
