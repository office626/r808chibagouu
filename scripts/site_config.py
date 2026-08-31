# -*- coding: utf-8 -*-
"""サイト固有の設定（site/data/config.json）を読む。

別の災害・地域へ複製するときに書き換える値を1か所に集めるための入り口。
各スクリプトは定数を直書きせず、ここから取る。
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "site" / "data" / "config.json"


@lru_cache(maxsize=1)
def config() -> dict:
    return json.loads(PATH.read_text(encoding="utf-8"))


def base_url() -> str:
    """サイトの公開URL（末尾スラッシュあり）。"""
    return config()["base_url"].rstrip("/") + "/"


def repo() -> str:
    """owner/name。通知やUAに使う。"""
    return config()["repo"]


def user_agent(role: str) -> str:
    """外部サイトへ名乗るUA。role は watch / archive / collector / discover など。"""
    return f'{config()["ua_prefix"]}-{role}/1.0 (+https://github.com/{repo()})'


def regions() -> list[dict]:
    """市町村以外のまとまり（県・国）。slug / name / name_en を持つ。"""
    return config()["regions"]


def region_names() -> dict[str, str]:
    return {r["slug"]: r["name"] for r in regions()}


def onset() -> str:
    """発災日 YYYY-MM-DD。"""
    return config()["disaster"]["onset"]
