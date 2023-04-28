from typing import Any, TypeAlias
from linki.connection import Connection
from linki.id import SimpleLabel

Config: TypeAlias = object
Refusals: TypeAlias = list[str]


class ConfigCollection():
    def __init__(self, connection: Connection[Any]) -> None:
        self.store = connection

    def add_refusal(self, copy_id: str):
        refusal_label = SimpleLabel('refusals').labelId
        refusals: set = self.store.get(refusal_label, set())
        refusals.add(copy_id)
        self.store[refusal_label] = refusals

    def render_refusals(self):
        refusal_label = SimpleLabel('refusals').labelId
        refusals: set | None = self.store.get(refusal_label, None)
        if (refusals is None):
            return "No refusals."

        return ', '.join(refusals)
