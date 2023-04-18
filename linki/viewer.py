import pickle
from linki.editor import Copier, Editor, FileCopier
from linki.id import ID, Label, LabelID
from linki.repository import Repository
from dataclasses import asdict, dataclass
import bottle

from linki.url import URL
bottle.debug(True)


@dataclass(kw_only=True)
class WebViewConf:
    sub: bool = False
    api: bool = False
    web: bool = False


class WebView:
    def __init__(self, repo: Repository, conf: WebViewConf) -> None:
        self.app = bottle.Bottle()
        self.repo = repo
        self.conf = conf
        self.app.route('/<output>/<style>/<label:path>',
                       'GET', self.handle)
        self.app.route('/<output>/<style>/',
                       'GET', self.handle)
        self.app.route('/<output>/<style>',
                       'GET', self.handle)
        if (self.conf.sub):
            self.app.route('/announce', 'POST', self.handle)

    def handle_web(self, style: str, label: str):
        item = self.handle_single('api', style, label)
        template = None
        match style:
            case 'titles':
                template = 'titles'
            case 'articles':
                template = 'articles'
        return template

    def handle(self, output: str, style: str, label: str | None = None):
        unsupported = bottle.HTTPError(400, f'{output} not supported.')
        match output:
            case 'count' | 'pickles':
                if (not self.conf.sub):
                    raise unsupported
            case 'api':
                if (not self.conf.api):
                    raise unsupported
            case 'w':
                if (not self.conf.web):
                    raise unsupported
                raise NotImplementedError

        if style not in ['titles', 'articles']:
            raise bottle.HTTPError(404, f'style not found: {style}')

        if (label is None):
            return self.handle_iter(output, style)
        return self.handle_single(output, style, label)

    def convert_path(self, style: str, label: str):
        item_id = None
        match style:
            case 'titles':
                item_id = Label(label).labelId
            case _:
                raise bottle.HTTPError(404, f'pathed style not found: {style}')
        return item_id

    def handle_single(self, output: str, style: str, label: str):
        if (not LabelID.isValidID(label)):
            label = self.convert_path(style, label)
        else:
            label = LabelID(label)

        item = self.repo.get_item(style, label)

        if (item is None):
            raise bottle.HTTPError(404, f'label not found: {label}')

        match output:
            case 'pickles':
                return pickle.dumps(item)
            case 'api':
                return asdict(item)

    def handle_iter(self, output: str, style: str):
        if style not in ['titles', 'articles']:
            raise bottle.HTTPError(404, f'style not found: {style}')
        iter_item = self.repo.iter_item(style)
        match output:
            case 'pickles':
                return pickle.dumps(iter_item)
            case 'api':
                return {style: list(iter_item)}
            case 'count':
                return f"{self.repo.get_count(style)}"

    def handle_announce(self):
        url = bottle.request.forms.getter('url')
        url = URL(url)
        if (url not in self.repo.subs.urls.values()):
            return False

        destination = Editor(self.repo)
        source = Repository(url.url)
        copier = Copier(source, destination)

        copier.copy_articles()
        copier.copy_titles()
        return True

    def run(self, host: str, port: int):
        self.app.run(host=host, port=port, reloader=True)
