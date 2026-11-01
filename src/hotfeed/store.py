from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .models import HotPost


SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    node TEXT,
    author TEXT,
    heat INTEGER NOT NULL DEFAULT 0,
    heat_type TEXT NOT NULL DEFAULT 'replies',
    created_at TEXT,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fetched_at TEXT NOT NULL,
    post_id INTEGER NOT NULL REFERENCES posts(id),
    heat INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_snapshots_post ON snapshots(post_id);
"""


class Store:
    def __init__(self, db_path: str | Path = "hotfeed.db"):
        self.conn = sqlite3.connect(str(db_path))
        self.conn.executescript(SCHEMA)

    def save_batch(self, posts: list[HotPost]) -> None:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self.conn:
            for p in posts:
                created = p.created_at.isoformat(timespec="seconds") if p.created_at else None
                row = self.conn.execute(
                    "SELECT id FROM posts WHERE url = ?", (p.url,)
                ).fetchone()
                if row:
                    post_id = row[0]
                    self.conn.execute(
                        "UPDATE posts SET title = ?, heat = ?, last_seen = ? WHERE id = ?",
                        (p.title, p.heat, now, post_id),
                    )
                else:
                    cur = self.conn.execute(
                        "INSERT INTO posts (site, url, title, node, author, heat, heat_type,"
                        " created_at, first_seen, last_seen) VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (p.site, p.url, p.title, p.node, p.author, p.heat, p.heat_type,
                         created, now, now),
                    )
                    post_id = cur.lastrowid
                self.conn.execute(
                    "INSERT INTO snapshots (fetched_at, post_id, heat) VALUES (?,?,?)",
                    (now, post_id, p.heat),
                )

    def latest(self, site: str | None = None, limit: int = 20) -> list:
        sql = ("SELECT site, title, url, node, heat, heat_type, last_seen FROM posts "
               "WHERE last_seen = (SELECT MAX(last_seen) FROM posts p2 "
               "WHERE p2.site = posts.site AND p2.url = posts.url)")
        args: list = []
        if site:
            sql += " AND site = ?"
            args.append(site)
        sql += " ORDER BY heat DESC LIMIT ?"
        args.append(limit)
        return self.conn.execute(sql, args).fetchall()
