from abc import ABC, abstractmethod

from sigili.old_repo.RefItem import RefItem

# TODO for right now this is just here to be pretty. I don't remember why I felt it needed to exist. I'm sure it will come back to me.


class RefLog(ABC):
    @abstractmethod
    def getVersion(self, refid: str):
        pass

    @abstractmethod
    def getHistory(self, refid: str):
        pass

    @abstractmethod
    def getRefItem(self, refid: str) -> RefItem:
        pass

    @abstractmethod
    def addRefItem(self, refItem: RefItem):
        pass
