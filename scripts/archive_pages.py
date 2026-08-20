# -*- coding: utf-8 -*-
"""data/supports.csv の全公式ページを Wayback Machine に保存する（初回バックフィルと週次の定期保存）。

- 1件ずつ直列で、間隔（--wait 秒、既定20）をあけて依頼する。失敗は記録して続行
- 保存結果は site/data/archive-index.json（url → [{at, archive_url}] の追記）に残す
- 既定では「直近 --skip-days 日以内に保存済みの URL」はスキップする（再実行・再開に安全）
- 手動: python scripts/archive_pages.py [--wait 20] [--skip-days 6] [--limit N] [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
import json
import ssl
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "supports.csv"
INDEX = ROOT / "site" / "data" / "archive-index.json"
JST = timezone(timedelta(hours=9))
UA = "CTZC-r808chibagouu-archive/1.0 (+https://github.com/office626/r808chibagouu)"
CTX = ssl.create_default_context()


def now() -> datetime:
    return datetime.now(JST)


def save(url: str) -> str:
    stamp = now().astimezone(timezone.utc).strftime("%Y%m%d%H%M%S")
    for attempt in range(2):
        try:
            req = urllib.request.Request("https://web.archive.org/save/" + url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45, context=CTX) as res:
                res.read(1024)
            return f"https://web.archive.org/web/{stamp}/{url}"
        except Exception as e:
            if attempt == 0:
                time.sleep(10)
            else:
                print("  ERR", url, str(e)[:80])
    return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wait", type=int, default=20)
    ap.add_argument("--skip-days", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    index: dict = {}
    if INDEX.exists():
        try:
            index = json.loads(INDEX.read_text(encoding="utf-8"))
        except Exception:
            index = {}
    entries: dict = index.setdefault("by_url", {})
    cutoff = (now() - timedelta(days=args.skip_days)).isoformat(timespec="seconds")

    rows = list(csv.DictReader(CSV.open(encoding="utf-8", newline="")))
    urls = []
    seen = set()
    for r in rows:
        u = (r.get("url") or "").strip()
        if not u.startswith("http") or u in seen:
            continue
        seen.add(u)
        recs = entries.get(u) or []
        if recs and recs[-1].get("at", "") >= cutoff:
            continue
        urls.append(u)
    if args.limit:
        urls = urls[: args.limit]
    print(f"targets={len(urls)} (skip within {args.skip_days} days) wait={args.wait}s")
    if args.dry_run:
        for u in urls[:20]:
            print(" ", u)
        return 0

    done = 0
    for i, u in enumerate(urls):
        if i:
            time.sleep(args.wait)
        a = save(u)
        ts = now().isoformat(timespec="seconds")
        if a:
            entries.setdefault(u, []).append({"at": ts, "archive_url": a})
            done += 1
            print(f"[{i + 1}/{len(urls)}] saved {u}")
        # 途中経過を毎回書き出す（中断しても再開できる）
        index["updated_at"] = ts
        INDEX.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"saved={done}/{len(urls)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
