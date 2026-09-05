# -*- coding: utf-8 -*-
"""supports.csv の行を機械的に見直すための材料を集める。

このスクリプトは status を書き換えない。判断は人がする。
自動で「終了」を付けると、本文にある別の災害の話や過去の期限を拾って
誤って閉じてしまう（実例：我孫子市の東日本大震災の記述、匝瑳市の2019年の期限）。
そこで、判断に使える証拠（更新日・終了らしき文とその前後・期限らしき日付）を
そのまま出して、人が読んで決められる形にする。

使い方:
    python3 scripts/recheck_supports.py --stale-before 2026-08-20
    python3 scripts/recheck_supports.py --slug pref-chiba --json out.json
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_config  # noqa: E402
from watch_pages import CTX, cut_chrome, to_lines  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "supports.csv"
UA = site_config.user_agent("recheck")

# 受付が終わったことを示しそうな言い回し。これだけでは決められないので前後を一緒に出す。
CLOSED_HINTS = re.compile(
    r"(受付(は)?(を)?(終了|締切|しめきり)|申請(の)?受付(は)?終了|終了しました|"
    r"終了いたしました|締め切りました|締切ました|受付を終了|配布(は)?終了|"
    r"開設(は)?終了|閉所|終了となりました)"
)
# 期限らしき日付。年が無いものもあるので、そのまま出して人に見せる。
DEADLINE = re.compile(
    r"(令和\s*\d+\s*年\s*)?\d{1,2}\s*月\s*\d{1,2}\s*日\s*(（[月火水木金土日]）|\([月火水木金土日]\))?\s*"
    r"(まで|必着|消印有効|をもって|が期限|が締切)"
)
UPDATED = re.compile(r"(更新日|掲載日|公開日)\s*[:：]?\s*([^\s<]{4,24})")


def fetch(url: str) -> tuple[int, str, str]:
    """(status, 最終URL, 本文HTML)。エラーでも落とさず status に載せる。"""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=30, context=CTX) as res:
            raw = res.read()
            enc = res.headers.get_content_charset() or "utf-8"
            try:
                body = raw.decode(enc, errors="replace")
            except LookupError:
                body = raw.decode("utf-8", errors="replace")
            return res.status, res.geturl(), body
    except urllib.error.HTTPError as e:
        return e.code, url, ""
    except Exception as e:  # ネットワーク側の事情。行は残して人に見せる。
        return -1, f"{type(e).__name__}", ""


def title_of(html: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    if not m:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()


def context(text: str, m: re.Match, width: int = 60) -> str:
    return text[max(0, m.start() - width): m.end() + width].strip()


def inspect(row: dict) -> dict:
    status, final, html = fetch(row["url"])
    out = {
        "slug": row["slug"],
        "kind": row["kind"],
        "title_csv": row["title"],
        "url": row["url"],
        "status_csv": row["status"],
        "checked_csv": row["checked"],
        "deadline_csv": row["deadline"],
        "http": status,
        "final_url": final if final != row["url"] else "",
        "title_web": "",
        "updated": "",
        "closed_hits": [],
        "deadline_hits": [],
    }
    if status != 200 or not html:
        return out

    out["title_web"] = title_of(html)
    text = re.sub(r"\s+", " ", " ".join(to_lines(cut_chrome(html))))

    m = UPDATED.search(text)
    if m:
        out["updated"] = m.group(0).strip()
    seen = set()
    for m in CLOSED_HINTS.finditer(text):
        c = context(text, m)
        if c not in seen:
            seen.add(c)
            out["closed_hits"].append(c)
        if len(out["closed_hits"]) >= 3:
            break
    seen = set()
    for m in DEADLINE.finditer(text):
        c = context(text, m, 30)
        if c not in seen:
            seen.add(c)
            out["deadline_hits"].append(c)
        if len(out["deadline_hits"]) >= 4:
            break
    return out


def verdict(r: dict) -> str:
    """人が最初に見る順番をつけるためのラベル。決定ではない。"""
    if r["http"] != 200:
        return "要確認:取得できず"
    if r["closed_hits"]:
        return "要確認:終了らしき記述"
    if r["deadline_hits"]:
        return "要確認:期限の記述"
    return "変化なしに見える"


ORDER = {"要確認:取得できず": 0, "要確認:終了らしき記述": 1, "要確認:期限の記述": 2, "変化なしに見える": 3}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stale-before", help="checked がこの日付より前の行だけ見る（YYYY-MM-DD）")
    ap.add_argument("--slug", action="append", help="この slug だけ（複数可）")
    ap.add_argument("--kind", action="append", help="この kind だけ（複数可）")
    ap.add_argument("--limit", type=int, help="先頭からこの件数だけ")
    ap.add_argument("--wait", type=float, default=1.5, help="1件ごとの待ち秒数")
    ap.add_argument("--json", help="結果を書き出すファイル")
    args = ap.parse_args()

    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    if args.stale_before:
        rows = [r for r in rows if (r["checked"] or "9999-99-99") < args.stale_before]
    if args.slug:
        rows = [r for r in rows if r["slug"] in set(args.slug)]
    if args.kind:
        rows = [r for r in rows if r["kind"] in set(args.kind)]
    if args.limit:
        rows = rows[: args.limit]

    print(f"# 見直しの材料 {date.today().isoformat()}  対象 {len(rows)} 行", file=sys.stderr)
    results = []
    for i, row in enumerate(rows, 1):
        r = inspect(row)
        r["verdict"] = verdict(r)
        results.append(r)
        print(f"  {i}/{len(rows)} {r['slug']:<14} {r['verdict']}", file=sys.stderr)
        if i < len(rows):
            time.sleep(args.wait)

    results.sort(key=lambda r: (ORDER[r["verdict"]], r["slug"]))
    if args.json:
        Path(args.json).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {args.json}", file=sys.stderr)

    for r in results:
        print(f"\n## [{r['verdict']}] {r['slug']} / {r['kind']} / status={r['status_csv']} / checked={r['checked_csv']}")
        print(f"- CSV: {r['title_csv']}")
        print(f"- URL: {r['url']}  (HTTP {r['http']})")
        if r["final_url"]:
            print(f"- 転送先: {r['final_url']}")
        if r["title_web"]:
            print(f"- ページ題: {r['title_web']}")
        if r["updated"]:
            print(f"- {r['updated']}")
        for c in r["closed_hits"]:
            print(f"- 終了？: …{c}…")
        for c in r["deadline_hits"]:
            print(f"- 期限？: …{c}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
