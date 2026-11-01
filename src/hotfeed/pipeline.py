from __future__ import annotations

from .adapters.base import SiteAdapter
from .models import HotPost
from .store import Store


def normalize(posts: list[HotPost]) -> list[HotPost]:
    seen = set()
    out = []
    for p in posts:
        if p.url not in seen:
            seen.add(p.url)
            out.append(p)
    return out


def run(adapter: SiteAdapter, store: Store, renderers=(), save: bool = True) -> list[HotPost]:
    posts = normalize(adapter.fetch())
    if save:
        store.save_batch(posts)
    for r in renderers:
        r.render(adapter.name, posts)
    return posts
