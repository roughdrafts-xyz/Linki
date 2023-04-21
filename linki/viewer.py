from io import BytesIO
from pathlib import Path
import pickle
import msgspec

import pypandoc
from linki.editor import Copier, Editor
from linki.id import Label, LabelID
from linki.repository import Repository, TemporaryRepository
from dataclasses import dataclass
import bottle



@dataclass(kw_only=True)
class WebViewConf:
    copy: bool = False
    contribute: bool = False
    api: bool = False
    web: bool = False
    debug: bool = False
    home: str | None = None


class WebView:
    styles = ['titles', 'articles']

    def __init__(self, repo: Repository, conf: WebViewConf) -> None:
        self.app = bottle.Bottle()
        self.repo = repo
        self.conf = conf
        bottle.debug(self.conf.debug)
        self.app.route('/', 'GET', self.handle_home)
        self.app.route('/<output>/<style>/<label:path>',
                       'GET', self.handle)
        self.app.route('/<output>/<style>/',
                       'GET', self.handle)
        self.app.route('/<output>/<style>',
                       'GET', self.handle)
        if (self.conf.contribute):
            self.app.route('/contribute', 'POST', self.handle_contribution)
        if (self.conf.web):
            self.single_templates = dict()
            self.iter_templates = dict()
            lookup = [
                Path(__file__).resolve().joinpath('..', 'templates')]
            self.one_tmpl = bottle.SimpleTemplate(
                name='one.html', lookup=lookup)
            self.many_tmpl = bottle.SimpleTemplate(
                name='many.html', lookup=lookup)

            self.one_tmpl.prepare()
            self.many_tmpl.prepare()

    def handle_home(self):
        return self.handle('w', 'titles', self.conf.home)

    def handle(self, output: str, style: str, label: str | None = None):
        unsupported = bottle.HTTPError(400, f'{output} not supported.')
        match output:
            case 'count' | 'copy':
                if (not self.conf.copy):
                    raise unsupported
            case 'api':
                if (not self.conf.api):
                    raise unsupported
            case 'w':
                if (not self.conf.web):
                    raise unsupported
            case _:
                raise unsupported

        if style not in self.styles:
            raise bottle.HTTPError(404, f'style not found: {style}')

        if (label is None):
            return self.handle_many(output, style)
        return self.handle_single(output, style, label)

    def convert_path(self, style: str, label: str):
        item_id = None
        match style:
            case 'titles':
                item_id = Label(label.split('/')).labelId
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
            case 'copy':
                return pickle.dumps(item)
            case 'api':
                return msgspec.structs.asdict(item)
            case 'w':
                item.content = pypandoc.convert_text(
                    item.content, format='markdown', to='html')
                return self.one_tmpl.render({'item': item})

    def handle_many(self, output: str, style: str):
        if style not in self.styles:
            raise bottle.HTTPError(404, f'style not found: {style}')
        collection = self.repo.get_collection(style)
        match output:
            case 'copy':
                return pickle.dumps(collection)
            case 'api':
                return {style: [msgspec.structs.asdict(item) for item in collection.values()]}
            case 'count':
                return f"{self.repo.get_count(style)}"
            case 'w':
                items = list(collection.values())
                for item in items:
                    if (style == 'titles'):
                        item.web_id = item.label.labelId
                    else:
                        item.web_id = item.articleId

                return self.many_tmpl.render({
                    'items': items,
                    'style': style.capitalize(),
                    'style_root': f"/w/{style}/"
                })

    def handle_contribution(self):
        req: bottle.FormsDict = bottle.request.params  # type: ignore
        files: bottle.FormsDict = bottle.request.files  # type: ignore
        url = req.get('url')
        if (url == 'https://localhost:8080/'):
            f_titles: bottle.FileUpload | None = files.get('titles')
            f_articles: bottle.FileUpload | None = files.get('articles')
            if (f_articles is None or f_titles is None):
                return bottle.HTTPError(500)

            c_titles: bottle.FileUpload = f_titles
            c_articles: bottle.FileUpload = f_articles

            b_titles: BytesIO = c_titles.file
            b_articles: BytesIO = c_articles.file
            source = TemporaryRepository.fromStreams(
                titles=b_titles.read(),
                articles=b_articles.read()
            )

            destination = Editor(self.repo)
            copier = Copier(source, destination)

            copier.copy_articles()
            copier.copy_titles()
            return bottle.HTTPResponse('/updates', 201)
        else:
            return bottle.HTTPResponse('', 403)

    def run(self, host: str, port: int):
        self.app.run(host=host, port=port, reloader=self.conf.debug)
