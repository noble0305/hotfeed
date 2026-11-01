from __future__ import annotations

from datetime import datetime, timezone

import httpx

from ..models import HotPost
from .base import FetchError, register

TOP_API = "https://linux.do/top.json"


@register
class LinuxDoAdapter:
    """linux.do is a Discourse forum behind Cloudflare.

    Copy the `_t` cookie value from a logged-in browser session
    (DevTools -> Application -> Cookies -> linux.do) and put it in
    config.toml under [linux_do] or in env HOTFEED_LINUXDO_COOKIE.
    """

    name = "linux.do"

    def __init__(self, cookie=None, period: str = "weekly"):
        self.cookie = cookie
        self.period = period

    def fetch(self) -> list[HotPost]:
        if not self.cookie:
            raise FetchError(
                "linux.do requires a Discourse `_t` cookie. "
                "See README for how to export it from a logged-in browser."
            )
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Cookie": f"_t={self.cookie}",
        }
        resp = httpx.get(TOP_API, params={"period": self.period},
                         timeout=20, headers=headers)
        if resp.status_code != 200:
            raise FetchError(
                f"linux.do returned HTTP {resp.status_code}. "
                "If 403, your cookie likely expired - re-export it."
            )
        if "Just a moment..." in resp.text:
            raise FetchError("Blocked by Cloudflare challenge - re-export cookie")
        data = resp.json()
        users = {u["id"]: u["username"] for u in data.get("users", [])}
        posts = []
        for t in data.get("topic_list", {}).get("topics", []):
            posters = t.get("posters") or []
            author = users.get(posters[0].get("user_id")) if posters else None
            posts.append(HotPost(
                site=self.name,
                title=t["title"],
                url=f"https://linux.do/t/topic/{t['id']}",
                node=None,
                author=author,
                heat=int(t.get("posts_count", 1)) - 1,
                heat_type="replies",
                created_at=datetime.fromtimestamp(t["created_at"] / 1000, tz=timezone.utc),
            ))
        return posts
