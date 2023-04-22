from io import BytesIO
from pathlib import Path
import pickle
import msgspec

import pypandoc
from linki.article import BaseArticle
from linki.editor import Copier, Editor
from linki.id import ID, Label, LabelID
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


class RenderedArticle(BaseArticle, frozen=True):
    raw: str

    @classmethod
    def fromArticle(cls, article: BaseArticle):
        raw = pypandoc.convert_text(
            article.content, format='markdown', to='markdown')
        content = pypandoc.convert_text(
            article.content, format='markdown', to='html')
        return cls(
            label=article.label,
            content=content,
            raw=raw,
            editOf=article.editOf
        )


class WebView:
    styles = ['titles', 'articles']

    def __init__(self, repo: Repository, conf: WebViewConf) -> None:
        self.app = bottle.Bottle()
        self.repo = repo
        self.conf = conf
        bottle.debug(self.conf.debug)
        self.app.route('/', 'GET', self.handle_home)
        self.app.route('/<style>/titles/',
                       'GET', self.handle_many_titles)
        self.app.route('/<style>/articles/',
                       'GET', self.handle_many_articles)
        self.app.route('/<style>/<label:path>',
                       'GET', self.handle_single_article)
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
        if (self.conf.home is not None):
            return self.handle_single_article('w', self.conf.home)
        return self.handle_many_titles('w')

    def confirm_support(self, style: str):
        unsupported = bottle.HTTPError(400, f'{style} not supported.')
        match style:
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

    def convert_path(self, label: str):
        return Label(label.split('/')).labelId

    def handle_single_article(self, style: str, label: str):
        self.confirm_support(style)
        if (not LabelID.isValidID(label)):
            item_id = self.convert_path(label)
            error = bottle.HTTPError(404, f'path not found: {label}')
        else:
            item_id = ID(label)
            error = bottle.HTTPError(404, f'item not found: {label}')

        item = self.repo.titles.titles.get(item_id, None)
        if (item is None):
            item = self.repo.articles.articles.get(item_id, None)
        if (item is None):
            return error

        match style:
            case 'copy':
                return msgspec.msgpack.encode(item)
            case 'api':
                return msgspec.to_builtins(item)
            case 'w':
                web_item = RenderedArticle.fromArticle(item)
                return self.one_tmpl.render({'item': web_item})

    def handle_many_titles(self, style: str):
        return self.handle_many(style, 'titles')

    def handle_many_articles(self, style: str):
        return self.handle_many(style, 'articles')

    def handle_many(self, style: str, collection_type: str):
        self.confirm_support(style)
        collection = self.repo.get_collection(collection_type)
        match style:
            case 'copy':
                return msgspec.msgpack.encode(collection)
            case 'api':
                return {collection_type: [msgspec.to_builtins(item) for item in collection]}
            case 'count':
                return f"{self.repo.get_count(collection_type)}"
            case 'w':
                items = [RenderedArticle.fromArticle(
                    article) for article in collection]
                return self.many_tmpl.render({
                    'items': items,
                    'style': collection_type.capitalize(),
                    'style_root': f"/w/{collection_type}/"
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
