from abc import ABC, abstractmethod


class Repo(ABC):
    @property
    @abstractmethod
    def refLog(self) -> 'RefLog':
        pass

    @property
    @abstractmethod
    def remotePath(self) -> 'Path':
        pass

    @property
    @abstractmethod
    def remoteStyle(self) -> str:
        pass

    @abstractmethod
    def getRefIds(self) -> set:
        pass

    # TODO This needs something like a RepoData object to list and send to a builder.
    # Maybe a Remote object? or a RemoteList or RepoList.
    @abstractmethod
    def getRemotes(self) -> list['RemoteItem']:
        pass

    @abstractmethod
    def addRemote(self, remote):
        pass

    @abstractmethod
    def delRemote(self, pathname):
        pass

    @abstractmethod
    def getArticlesRefItems(self) -> list['RefItem']:
        pass

    @abstractmethod
    def viewRefid(self, refid):
        pass

    @abstractmethod
    def getHistory(self, refid):
        pass

    @abstractmethod
    def getDetailedHistory(self, refid, pathname):
        pass

    @abstractmethod
    def addNewArticle(self, pathname):
        pass

    @abstractmethod
    def updateExistingArticle(self, prefid, pathname):
        pass
