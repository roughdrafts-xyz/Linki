from abc import ABC, abstractmethod


class Repo(ABC):

    @abstractmethod
    def getRefs(self) -> set:
        pass

    @abstractmethod
    def getRefIds(self) -> set:
        pass

    @abstractmethod
    def getRemotePath(self):
        pass

    @abstractmethod
    def getRemoteStyle(self):
        pass

    @abstractmethod
    def getRemotes(self):
        pass

    @abstractmethod
    def addRemote(self, remote):
        pass

    @abstractmethod
    def delRemote(self, pathname):
        pass

    @abstractmethod
    def getArticles(self):
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
