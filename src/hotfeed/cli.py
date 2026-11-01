from __future__ import annotations

import os
try:
    import tomllib
except ImportError:  # Python < 3.11
    import tomli as tomllib
from pathlib import Path

import typer

from .adapters.base import ADAPTERS, FetchError
from .adapters.linuxdo import LinuxDoAdapter
from .adapters.v2ex import V2exAdapter
from .pipeline import run
from .renderers.console import ConsoleRenderer
from .renderers.markdown import MarkdownRenderer
from .store import Store

app = typer.Typer(help="hotfeed - aggregate hot topics from community sites")

CONFIG_PATHS = [Path("config.toml"), Path.home() / ".config/hotfeed/config.toml"]


def load_config() -> dict:
    for p in CONFIG_PATHS:
        if p.exists():
            with open(p, "rb") as f:
                return tomllib.load(f)
    return {}


def build_adapter(name: str, cfg: dict):
    if name == "v2ex":
        return V2exAdapter()
    if name == "linux.do":
        section = cfg.get("linux_do", {})
        cookie = section.get("cookie") or os.environ.get("HOTFEED_LINUXDO_COOKIE")
        return LinuxDoAdapter(cookie=cookie, period=section.get("period", "weekly"))
    raise typer.BadParameter(f"unknown site: {name}. available: {', '.join(ADAPTERS)}")


@app.command(name="run")
def run_cmd(
    site: str = typer.Option("all", help="v2ex / linux.do / all"),
    save: bool = typer.Option(True, help="save results into hotfeed.db"),
    markdown: bool = typer.Option(False, "--markdown", help="also write markdown reports/"),
):
    """Fetch hot topics now."""
    cfg = load_config()
    names = list(ADAPTERS) if site == "all" else [site]
    store = Store(cfg.get("db_path", "hotfeed.db"))
    renderers = [ConsoleRenderer()]
    if markdown:
        renderers.append(MarkdownRenderer(cfg.get("markdown_dir", "reports")))
    exit_code = 0
    for name in names:
        try:
            adapter = build_adapter(name, cfg)
            run(adapter, store, renderers, save=save)
        except FetchError as e:
            typer.secho(f"[hotfeed] {name}: {e}", fg=typer.colors.RED)
            exit_code = 1
    raise typer.Exit(exit_code)


@app.command()
def show(
    site: str = typer.Option(None, help="filter by site"),
    limit: int = typer.Option(20, help="max rows"),
):
    """Show latest saved snapshot from the local database."""
    store = Store(load_config().get("db_path", "hotfeed.db"))
    rows = store.latest(site=site, limit=limit)
    for site_name, title, url, node, heat, heat_type, last_seen in rows:
        node_s = f" [{node}]" if node else ""
        print(f"{site_name:<9} {heat:>5} {heat_type:<7} {title}{node_s}  {url}")
