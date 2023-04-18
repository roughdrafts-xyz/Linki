from pathlib import Path
import pickle
from linki.editor import Copier, Editor
from linki.id import Label, LabelID
from linki.repository import Repository
from dataclasses import asdict, dataclass
import bottle

from linki.url import URL


@dataclass(kw_only=True)
class WebViewConf:
    sub: bool = False
    api: bool = False
    web: bool = False
    debug: bool = False


class WebView:
    styles = ['titles', 'articles']

    def __init__(self, repo: Repository, conf: WebViewConf) -> None:
        self.app = bottle.Bottle()
        self.repo = repo
        self.conf = conf
        bottle.debug(self.conf.debug)
        self.app.route('/<output>/<style>/<label:path>',
                       'GET', self.handle)
        self.app.route('/<output>/<style>/',
                       'GET', self.handle)
        self.app.route('/<output>/<style>',
                       'GET', self.handle)
        if (self.conf.sub):
            self.app.route('/announce', 'POST', self.handle_announce)
        if (self.conf.web):
            self.single_templates = dict()
            self.iter_templates = dict()
            single_lookup = [
                Path(__file__).resolve().joinpath('templates', 'single')]
            iter_lookup = [
                Path(__file__).resolve().joinpath('templates', 'iter')]
            for style in self.styles:
                self.single_templates[style] = bottle.SimpleTemplate(
                    name=style, lookup=single_lookup)
                self.single_templates[style].prepare()

                self.iter_templates[style] = bottle.SimpleTemplate(
                    name=style, lookup=iter_lookup)
                self.iter_templates[style].prepare()

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

        if style not in self.styles:
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
            case 'w':
                return self.single_templates[style].render(item)

    def handle_iter(self, output: str, style: str):
        if style not in self.styles:
            raise bottle.HTTPError(404, f'style not found: {style}')
        iter_item = self.repo.iter_item(style)
        match output:
            case 'pickles':
                return pickle.dumps(iter_item)
            case 'api':
                return {style: list(iter_item)}
            case 'count':
                return f"{self.repo.get_count(style)}"
            case 'w':
                return self.iter_templates[style].render(iter_item)

    def handle_announce(self):
        url = bottle.request.forms.get('url')  # type: ignore
        if (URL(url).labelId not in self.repo.subs.urls):
            return "1"

        destination = Editor(self.repo)
        source = Repository(url)
        copier = Copier(source, destination)

        copier.copy_articles()
        copier.copy_titles()
        return "0"

    def run(self, host: str, port: int):
        self.app.run(host=host, port=port, reloader=self.conf.debug)
