from dataclasses import dataclass
from urllib.parse import urlencode
from urllib.request import Request, urlopen
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
            case 'https':
                data = urlencode({'url': self.destination.url})
                request = Request(self.destination.url, str.encode(data))
                res = urlopen(request).read()
                if (res == "0"):
                    return True
        return False
