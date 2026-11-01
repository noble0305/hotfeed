from __future__ import annotations

from datetime import datetime, timezone

import httpx

from ..models import HotPost
from .base import FetchError, register

HOT_API = "https://www.v2ex.com/api/topics/hot.json"


@register
class V2exAdapter:
    name = "v2ex"

    def fetch(self) -> list[HotPost]:
        resp = httpx.get(HOT_API, timeout=15, headers={"User-Agent": "hotfeed/0.1"})
        if resp.status_code != 200:
            raise FetchError(f"v2ex API returned HTTP {resp.status_code}")
        try:
            topics = resp.json()
        except ValueError as e:
            raise FetchError("v2ex API returned non-JSON response") from e
        posts = []
        for t in topics:
            posts.append(HotPost(
                site=self.name,
                title=t["title"],
                url=t["url"],
                node=t.get("node", {}).get("title"),
                author=t.get("member", {}).get("username"),
                heat=int(t.get("replies", 0)),
                heat_type="replies",
                created_at=datetime.fromtimestamp(t["created"], tz=timezone.utc),
            ))
        return posts
