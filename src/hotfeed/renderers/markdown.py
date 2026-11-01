from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


class MarkdownRenderer:
    def __init__(self, out_dir="reports"):
        self.out_dir = Path(out_dir)

    def render(self, site: str, posts) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        path = self.out_dir / f"{date}-{site.replace('.', '_')}.md"
        lines = [f"# {site} hot topics - {date}", ""]
        for i, p in enumerate(posts, 1):
            node = f" ({p.node})" if p.node else ""
            lines.append(f"{i}. [{p.title}]({p.url}){node} - {p.heat_type}: {p.heat}")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[hotfeed] markdown saved: {path}")
