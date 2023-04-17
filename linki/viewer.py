from linki.id import ArticleID, Label, LabelID
from linki.repository import Repository
from dataclasses import asdict, dataclass
import json
from typing import Dict, TypedDict
import bottle
bottle.debug(True)


# https://bottlepy.org/docs/dev/routing.html#explicit-routing-configuration
# Do some magic with this to make your life easier with the CRUD shit - its already dev'd, it just needs to be linked
# probably need to add a hook for receiving announcements?
# Should ignore drafts - only cares about articles and titles?
# Might just be time to do the WebViewer thing.


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
            self.app.route('/w', 'GET', self.handle_web)
        if (conf.api):
            self.app.route('/api/<style>/<label:path>',
                           'GET', self.handle_api)
        if (conf.sub):
            # self.app.route('/sub', 'GET', self.handle_sub)
            self.app.route('/announce', 'POST', self.handle_announce)

    def handle_web(self):
        return "Web"

    def handle_api(self, style: str, label: str):
        # Note to self - if you return a dictionary to bottle it automatically converts to json API.
        # TODO This is not useful
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

        return asdict(item, dict_factory=self.decoded_dict)

    @staticmethod
    def decoded_dict(item) -> Dict:
        dic = dict(item)
        for key in dic:
            val = dic[key]
            if (type(val) == bytes):
                dic[key] = bytes.decode(val)
        return dic
    # def handle_sub(self):
        # return "Sub"

    def handle_announce(self):
        return "Announce"

    def run(self, host: str, port: int):
        self.app.run(host=host, port=port, reloader=True)
