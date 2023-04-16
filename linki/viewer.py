from typing import Dict
from bottle import Bottle

from linki.repository import Repository

# https://bottlepy.org/docs/dev/routing.html#explicit-routing-configuration
# Do some magic with this to make your life easier with the CRUD shit - its already dev'd, it just needs to be linked
# probably need to add a hook for receiving announcements?
# Should ignore drafts - only cares about articles and titles?
# Might just be time to do the WebViewer thing.


class WebView:
    def __init__(self, repo: Repository, conf: Dict[str, bool]) -> None:
        self.app = Bottle()

    def run(self, host: str, port: int):
        self.app.run(host=host, port=port)
