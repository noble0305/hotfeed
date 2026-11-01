from __future__ import annotations


class ConsoleRenderer:
    def render(self, site: str, posts) -> None:
        print(f"\n== {site} ({len(posts)} posts) ==")
        for i, p in enumerate(posts, 1):
            node = f" [{p.node}]" if p.node else ""
            print(f"{i:>3}. {p.title}{node} | {p.heat_type}: {p.heat}")
