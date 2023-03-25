
from abc import ABC, abstractmethod


class Editor(ABC):

    @abstractmethod
    def iter_drafts(self):
        pass

    @abstractmethod
    def iter_updates(self):
        pass

    @abstractmethod
    def publish_drafts(self):
        pass

    @abstractmethod
    def load_titles(self):
        pass
