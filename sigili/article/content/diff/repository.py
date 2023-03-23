from abc import ABC, abstractmethod


class DiffRepository(ABC):
    @abstractmethod
    def add_diff(self, refId, prefId, refBytes, prefBytes):
        raise NotImplementedError

    @abstractmethod
    def get_diff(self, refId, prefId):
        raise NotImplementedError
