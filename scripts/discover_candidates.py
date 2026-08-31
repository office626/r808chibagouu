# -*- coding: utf-8 -*-
"""市町村公式トップ（と防災ページ・収載済みの総合ページ）から災害関連リンクを拾い、supports.csv に未収載の候補を書き出す。

- 出力: site/data/candidates.json（Slack デイリー通知と支援者の採用判断に使う）
- 採用の判断は人が行う。ここでは列挙まで。
- 日次ジョブ（6:00 JST）から実行する想定。手動: python scripts/discover_candidates.py
"""
from __future__ import annotations

import csv
import html as htmlmod
import json
import re
import ssl
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin

import site_config

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "supports.csv"
MUNIS = ROOT / "site" / "data" / "municipalities.json"
OUT = ROOT / "site" / "data" / "candidates.json"
JST = timezone(timedelta(hours=9))
UA = site_config.user_agent("discover")
CTX = ssl.create_default_context()

KW = re.compile(r"(豪雨|大雨.{0,12}(被害|被災|災害|情報)|罹災|り災|災害ごみ|災害廃棄物|仮置|消毒|義援|応急修理|みなし仮設|応急住宅|市営住宅.{0,10}提供|県営住宅.{0,10}提供|災害ボランティア|被災者支援|被災された|見舞金|災害弔慰金|援護資金|生活再建支援金|減免.{0,10}(災害|大雨|豪雨)|(災害|大雨|豪雨).{0,10}減免)")
NEG = re.compile(r"(ハザードマップ|防災計画|処理計画|パブリックコメント|協定|戦没者|訓練|平成|令和[1-7]年|台風|地震|東日本大震災|熊本|能登|備え|マイ・タイムライン|プロポーザル|入札|募集要項|例規)")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25, context=CTX) as res:
        raw = res.read()
        enc = res.headers.get_content_charset() or "utf-8"
        try:
            return raw.decode(enc, errors="replace")
        except LookupError:
            return raw.decode("utf-8", errors="replace")


def norm_url(u: str) -> str:
    return u.split("#")[0].rstrip("/")


def main() -> int:
    munis = json.loads(MUNIS.read_text(encoding="utf-8"))
    known = set()
    hubs: dict[str, list[str]] = {}
    for r in csv.DictReader(CSV.open(encoding="utf-8", newline="")):
        url = (r.get("url") or "").strip()
        known.add(norm_url(url))
        # 収載済みの総合ページは、その市町村の子ページへの入口としても使う
        if (r.get("kind") or "").strip() == "hub" and url:
            hubs.setdefault((r.get("slug") or "").strip(), []).append(url)
    ts = datetime.now(JST).isoformat(timespec="seconds")
    candidates = []
    errors = 0
    for m in munis:
        pages = [m["url"]] + ([m["bousai"]] if m.get("bousai") else []) + hubs.get(m["slug"], [])
        found = {}
        for page in pages:
            try:
                text = fetch(page)
            except Exception:
                errors += 1
                continue
            for href, label in re.findall(r'<a[^>]+href="([^"#]+)"[^>]*>(.*?)</a>', text, flags=re.S | re.I):
                t = htmlmod.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", label))).strip()
                if not t or len(t) > 90 or len(t) < 6:
                    continue
                if not KW.search(t) or NEG.search(t):
                    continue
                u = urljoin(page, href)
                if not u.startswith("http") or norm_url(u) in known:
                    continue
                found[norm_url(u)] = {"slug": m["slug"], "name": m["name"], "title": t, "url": u}
        candidates.extend(found.values())
    OUT.write_text(json.dumps({
        "checked_at": ts,
        "note": "市町村公式トップ・防災ページ・収載済みの総合ページから拾った、supports.csv 未収載の候補。採用の判断は公式ページを見て人が行う。",
        "candidates": candidates,
    }, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"candidates={len(candidates)} errors={errors} at {ts}")
    for c in candidates[:20]:
        print(" ", c["name"], "|", c["title"][:50], "|", c["url"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
