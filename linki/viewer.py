from linki.id import Label, LabelID
from linki.repository import Repository
from dataclasses import asdict, dataclass
import bottle


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
        if (conf.web):
            self.app.route('/w/<style>/<label:path>', 'GET', self.handle_web)
        if (conf.api):
            self.app.route('/api/<style>/<label:path>',
                           'GET', self.handle_api)
        if (conf.sub):
            self.app.route('/announce', 'POST', self.handle_announce)

    def handle_web(self, style: str, label: str):
        item = self.handle_api(style, label)
        template = None
        match style:
            case 'titles':
                template = 'titles'
            case 'articles':
                template = 'articles'
        return template

    def handle_api(self, style: str, label: str):
        label_id = None
        match style:
            case 'titles':
                _label = Label(label)
                label_id = _label.labelId
            case 'articles':
                label_id = LabelID(label)

        if (label_id is None):
            raise bottle.HTTPError(404, f'style not found: {style}')

        item = self.repo.get_item(style, label_id)

        if (item is None):
            raise bottle.HTTPError(404, f'label not found: {label}')

        return asdict(item)

    def handle_announce(self):
        return "Announce"

    def run(self, host: str, port: int):
        self.app.run(host=host, port=port, reloader=True)
