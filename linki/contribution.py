from dataclasses import dataclass
from urllib.parse import urlencode
import msgspec
import requests
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
                url = self.destination.url + 'api/contribute'
                titles = self.source.titles.store.toFile()
                articles = self.source.articles.store.toFile()
                auth = self.source.config.get_auth(URL(self.destination.url))
                if (auth is None):
                    raise AttributeError(
                        "You need to authenticate this URL. Add it again using contribute.")
                res = requests.post(
                    url,
                    data={'titles': (titles, 'titles'),
                          'articles': (articles, 'articles')},
                    auth=(auth.username, auth.password)
                )
                return res.status_code == 201
        return False

    def authenticate(self, url: str, username: str, password: str):
        if not self.destination.parsed.scheme == 'https':
            raise NotImplementedError('authentication works with: https')

        url = self.destination.url + 'api/me'
        res = requests.get(url, auth=(username, password))
        if (res.status_code == 200):
            user = res.json.get('username')
            return user == username
        return False
