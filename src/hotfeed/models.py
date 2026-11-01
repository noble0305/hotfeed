from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class HotPost:
    site: str
    title: str
    url: str
    node: str | None = None
    author: str | None = None
    heat: int = 0
    heat_type: str = "replies"
    created_at: datetime | None = None
    fetched_at: datetime = field(default_factory=utcnow)
