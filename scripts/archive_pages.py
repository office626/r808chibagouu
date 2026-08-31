# -*- coding: utf-8 -*-
"""data/supports.csv の全公式ページを Wayback Machine に保存する（初回バックフィルと週次の定期保存）。

- 1件ずつ直列で、間隔（--wait 秒、既定10）をあけて依頼する。失敗は記録して続行
- Wayback 側の保存に1件あたり45秒前後かかる。全体の所要はほぼこれで決まる
- 保存結果は site/data/archive-index.json（url → [{at, archive_url}] の追記）に残す
- 既定では「直近 --skip-days 日以内に保存済みの URL」はスキップする（再実行・再開に安全）
- 保存が古いものから先に処理する。1回で全部を回れなくても、次の回で取り残しが先頭に来る
- --max-minutes を過ぎたら、そこで止めて残りを次回に回す（ジョブのタイムアウトで
  強制終了され、途中経過のコミットに到達しない事故を避けるため）
- 手動: python scripts/archive_pages.py [--wait 10] [--skip-days 6] [--limit N]
        [--max-minutes N] [--dry-run]
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

import site_config

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "supports.csv"
INDEX = ROOT / "site" / "data" / "archive-index.json"
JST = timezone(timedelta(hours=9))
UA = site_config.user_agent("archive")
CTX = ssl.create_default_context()


def now() -> datetime:
    return datetime.now(JST)


def save(url: str, timeout: int = 60) -> str:
    stamp = now().astimezone(timezone.utc).strftime("%Y%m%d%H%M%S")
    for attempt in range(2):
        try:
            req = urllib.request.Request("https://web.archive.org/save/" + url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout, context=CTX) as res:
                res.read(1024)
            return f"https://web.archive.org/web/{stamp}/{url}"
        except Exception as e:
            if attempt == 0:
                time.sleep(5)
            else:
                print("  ERR", url, str(e)[:80])
    return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wait", type=int, default=10)
    ap.add_argument("--skip-days", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--max-minutes", type=int, default=0, help="この分数を過ぎたら止める（0は無制限）")
    ap.add_argument("--timeout", type=int, default=60, help="1件あたりの待ち上限（秒）")
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
        # 未保存を先頭に、そのあとは保存が古い順。1回で回りきれなくても取り残しが残らない
        urls.append(((recs[-1].get("at", "") if recs else ""), u))
    urls.sort()
    urls = [u for _, u in urls]
    if args.limit:
        urls = urls[: args.limit]
    print(f"targets={len(urls)} (skip within {args.skip_days} days) wait={args.wait}s "
          f"max_minutes={args.max_minutes or '-'}")
    if args.dry_run:
        for u in urls[:20]:
            print(" ", u)
        return 0

    done = 0
    started = time.monotonic()
    budget = args.max_minutes * 60
    stopped_at = 0
    for i, u in enumerate(urls):
        if budget and time.monotonic() - started > budget:
            stopped_at = i
            break
        if i:
            time.sleep(args.wait)
        a = save(u, args.timeout)
        ts = now().isoformat(timespec="seconds")
        if a:
            entries.setdefault(u, []).append({"at": ts, "archive_url": a})
            done += 1
            print(f"[{i + 1}/{len(urls)}] saved {u}")
        # 途中経過を毎回書き出す（中断しても再開できる）
        index["updated_at"] = ts
        INDEX.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    if stopped_at:
        print(f"saved={done}/{len(urls)} (stopped at {stopped_at} after {args.max_minutes} min; "
              f"{len(urls) - stopped_at} left for the next run)")
    else:
        print(f"saved={done}/{len(urls)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
