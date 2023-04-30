from io import BytesIO
from pathlib import Path
import msgspec

import pypandoc
from linki.article import BaseArticle
from linki.change import Change
from linki.editor import Copier, Editor
from linki.id import ID, Label, LabelID
from linki.repository import Repository, TemporaryRepository
from dataclasses import dataclass
import bottle

from linki.url import URL


@dataclass(kw_only=True)
class WebViewConf:
    copy: bool = False
    contribute: bool = False
    api: bool = False
    web: bool = False
    debug: bool = False
    home: str | None = None


class RenderedArticle(BaseArticle, frozen=True):
    web_content: str
    web_id: str

    @classmethod
    def fromArticle(cls, article: BaseArticle, label: str):
        # if(article.redirect is None):
        raw = article.content
        # raw = pypandoc.convert_text(
        # article.content, format='markdown', to='markdown')
        web_content = pypandoc.convert_text(
            article.content, format='markdown', to='html')
        # TODO Write redirect test for /w/
        # if (article.redirect is not None):
        #   redirect = f"0; URL='/w/{article.redirect.labelId}'"
        #   content = f'<meta http-equiv="refresh" content="{redirect}"/>'

        return cls(
            label=article.label,
            web_content=web_content,
            content=raw,
            editOf=article.editOf,
            web_id=label
        )

    @classmethod
    def render(cls, collection: list[BaseArticle], collection_type: str):
        match collection_type:
            case 'articles':
                return {
                    cls.fromArticle(article, str(article.articleId))
                    for article in collection
                }
            case 'titles':
                return {
                    cls.fromArticle(
                        article, '/'.join(article.label.path))
                    for article in collection
                }


class WebView:
    styles = ['titles', 'articles']

    def __init__(self, repo: Repository, conf: WebViewConf) -> None:
        self.app = bottle.Bottle()
        self.repo = repo
        self.conf = conf
        bottle.debug(self.conf.debug)
        if (self.conf.contribute):
            self.app.route('/api/me', 'GET', self.handle_get_me)
            self.app.route('/api/contribute', 'POST', self.handle_contribution)
        self.app.route('/', 'GET', self.handle_home)
        self.app.route('/<style>/titles/',
                       'GET', self.handle_many_titles)
        self.app.route('/<style>/articles/',
                       'GET', self.handle_many_articles)
        self.app.route('/<style>/<label:path>',
                       'GET', self.handle_single_article)
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

        item = self.repo.titles.store.get(item_id, None)
        if (item is None):
            item = self.repo.articles.store.get(item_id, None)
        if (item is None):
            return error

        match style:
            case 'copy':
                return msgspec.msgpack.encode(item)
            case 'api':
                return msgspec.to_builtins(item)
            case 'w':
                web_item = RenderedArticle.fromArticle(item, label)
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
                items = RenderedArticle.render(collection, collection_type)
                return self.many_tmpl.render({
                    'items': items,
                    'style': collection_type.capitalize(),
                    'style_root': f"/w/"
                })

    def handle_contribution(self):
        (username, password) = bottle.request.auth or (None, None)
        if (
            (username is None) or (password is None) or
            (not isinstance(username, str)) or
            (not isinstance(password, str)) or
            (not self.repo.users.verify_user(username, password))
        ):
            return bottle.HTTPResponse('', 403)
        files: bottle.FormsDict = bottle.request.files  # type: ignore
        f_changes: bottle.FileUpload | None = files.get('changes')
        if (f_changes is None):
            return bottle.HTTPError(500)

        c_changes: bottle.FileUpload = f_changes

        b_changes: BytesIO = c_changes.file

        r_changes = msgspec.msgpack.decode(
            b_changes.read(), type=list[BaseArticle])
        can_edit = False
        for change in r_changes:
            new_change = Change(
                source=username,
                article=change
            )
            if (can_edit):
                # merge directly
                self.repo.titles.set_title(change)
                # TODO Also add the articles to the article db
                # TODO self.repo.changes.accept_change(new_change)
                pass
            else:
                self.repo.changes.add_change(new_change)
        title_text = ','.join([title.articleId for title in r_changes])
        if (can_edit):
            return bottle.HTTPResponse(f'/w/titles/{title_text}', 201)
        return bottle.HTTPResponse(f'/w/contributions/{title_text}', 202)

    def handle_get_me(self):
        (username, password) = bottle.request.auth or (None, None)
        is_user = self.repo.users.verify_user(username, password)
        if (not is_user):
            return bottle.HTTPResponse('', 403)
        return {
            'username': username
        }

    def run(self, host: str, port: int):
        self.app.run(host=host, port=port, reloader=self.conf.debug)
