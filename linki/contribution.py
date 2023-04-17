from dataclasses import dataclass
from linki.editor import FileCopier
from linki.repository import Repository
from linki.url import URL


@dataclass
class Contribution():
    source: Repository
    destination: URL

    def announce_updates(self) -> bool:
        match self.destination.parsed.scheme:
            case 'file':
                destination = self.destination.parsed.path
                copier = FileCopier(self.source, destination)
                copier.copy_articles()
                copier.copy_titles()
                copier.unload_titles()
                return True
            case 'http' | 'https':
                return True
        return False
