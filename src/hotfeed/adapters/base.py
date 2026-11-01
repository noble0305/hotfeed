from __future__ import annotations

from typing import Protocol

from ..models import HotPost


class FetchError(Exception):
    """Raised when a site cannot be fetched (blocked, bad response, etc.)."""


class SiteAdapter(Protocol):
    name: str

    def fetch(self) -> list[HotPost]: ...


ADAPTERS: dict = {}


def register(cls):
    ADAPTERS[cls.name] = cls
    return cls
