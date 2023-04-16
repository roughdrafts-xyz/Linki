from dataclasses import asdict, dataclass
import json
from typing import Dict, TypedDict
from bottle import Bottle

from linki.repository import Repository

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
        self.app = Bottle()
        self.repo = repo
        self.conf = conf
        if (conf.web):
            self.app.route('/w', 'GET', self.handle_web)
        if (conf.api):
            self.app.route('/api/title/<label_name:path>',
                           'GET', self.handle_title_api)
            self.app.route('/api/article/<label_id>',
                           'GET', self.handle_article_api)
        if (conf.sub):
            # self.app.route('/sub', 'GET', self.handle_sub)
            self.app.route('/announce', 'POST', self.handle_announce)

    def handle_web(self):
        return "Web"

    def handle_article_api(self, label_id: str):
        # Note to self - if you return a dictionary to bottle it automatically converts to json API.
        # TODO This is not useful
        return {'v': label_id}

    def handle_title_api(self, label_name: str):
        # Note to self - if you return a dictionary to bottle it automatically converts to json API.
        # TODO This is not useful
        return {'v': label_name}

    # def handle_sub(self):
        # return "Sub"

    def handle_announce(self):
        return "Announce"

    def run(self, host: str, port: int):
        self.app.run(host=host, port=port)
