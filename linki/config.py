from typing import Any, TypeAlias

import msgspec
from linki.connection import Connection
from linki.id import SimpleLabel
from linki.url import URL

Config: TypeAlias = object
Refusals: TypeAlias = list[str]
# TODO This is ugly, find a more elegant solution


class AuthDetails(msgspec.Struct, frozen=True):
    url: str
    username: str
    password: str


class ConfigCollection():
    def __init__(self, connection: Connection[Any]) -> None:
        self.store = connection

    def add_refusal(self, copy_id: str):
        refusal_label = SimpleLabel('refusals').labelId
        refusals: set = self.store.get(refusal_label, set())
        refusals.add(copy_id)
        self.store[refusal_label] = refusals

    def get_refusals(self):
        refusal_label = SimpleLabel('refusals').labelId
        return self.store.get(refusal_label, [])

    def render_refusals(self):
        refusal_label = SimpleLabel('refusals').labelId
        refusals: set | None = self.store.get(refusal_label, None)
        if (refusals is None):
            return "No refusals."

        return ', '.join(refusals)

    def add_approval(self, copy_id: str):
        approval_label = SimpleLabel('approvals').labelId
        approvals: set = self.store.get(approval_label, set())
        approvals.add(copy_id)
        self.store[approval_label] = approvals

    def render_approvals(self):
        approval_label = SimpleLabel('approvals').labelId
        approvals: set | None = self.store.get(approval_label, None)
        if (approvals is None):
            return "No approvals."

        return ', '.join(approvals)

    def add_auth(self, url: URL, username: str, password: str):
        auth = AuthDetails(
            url.url,
            username,
            password
        )
        self.store[url.labelId] = auth

    def get_auth(self, url: URL) -> AuthDetails | None:
        auth = self.store.get(url.labelId)
        if (isinstance(auth, AuthDetails)):
            return auth
        return None
