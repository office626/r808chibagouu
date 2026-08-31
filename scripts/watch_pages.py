# -*- coding: utf-8 -*-
"""市町村公式ページ（data/supports.csv の URL）の更新を検知して site/data/watch.json に記録する。

- 本文テキスト（script/style/nav を除き、空白を正規化）のハッシュを前回と比べる
- 変わっていたら last_changed を更新し、増えた行（見出し候補）を added に残す。履歴は events に追記
- 初回に見た URL は基準を作るだけで「更新」にはしない
- 取得に失敗した URL は前回の値を維持し、errors に記録する
- 変更を検知したページは Internet Archive（Wayback Machine）へ保存を依頼し、スナップショットURLを記録する
  （fire-and-forget。失敗しても処理は続行。1回の実行で最大 ARCHIVE_MAX 件・間隔をあけて直列）
- events は消さずに月別ログ site/data/watch-log/YYYY-MM.json へも追記する（追記専用。履歴ページが読む）
- 3時間おきの schedule で GitHub Actions から実行する想定。ただし実際の間隔は
  GitHub 側の都合で延びる（実測の中央値は約5時間、最大8時間超）。表示の文言は
  「数時間おき」に合わせてある。手動: python scripts/watch_pages.py
"""
from __future__ import annotations

import csv
import hashlib
import html as htmlmod
import json
import re
import ssl
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import site_config

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "supports.csv"
OUT = ROOT / "site" / "data" / "watch.json"
STATE = ROOT / "data" / "watch-state.json"
MUNIS = ROOT / "site" / "data" / "municipalities.json"
JST = timezone(timedelta(hours=9))
UA = site_config.user_agent("watch")
CTX = ssl.create_default_context()
MAX_EVENTS = 600
MAX_ADDED = 5
MAX_REMOVED = 3
EXTRACT = 2               # 本文抽出のやり方の版。変えたら全ページの基準を取り直す
ARCHIVE_MAX = 10          # 1回の実行で Wayback に依頼する最大件数
ARCHIVE_WAIT = 4          # 依頼の間隔（秒）
LOG_DIR = ROOT / "site" / "data" / "watch-log"

STRIP = re.compile(r"<(script|style|noscript|nav|header|footer|aside|svg|iframe)\b[^>]*>.*?</\1>", re.S | re.I)
# 共通パーツ（パンくず・関連リンク・問い合わせ欄など）は div で組まれていることが多く、
# タグ名だけでは落とせない。id/class で見て切る
TAG = re.compile(r"<(/?)([a-zA-Z][\w:-]*)([^>]*)>")
VOID = {"br", "hr", "img", "input", "meta", "link", "area", "base", "col", "embed", "source", "track", "wbr"}
CHROME = re.compile(
    r'(id|class)="[^"]*('
    r"nav|menu|sidebar|side_|side-|breadcrumb|pankuzu|topicpath|topic-path|topic_path"
    r"|related|relation|banner|social|share|footer|header|search|pagetop|page-top|page_top|totop"
    r"|inquiry|otoiawase|toiawase|utility|language|fontsize|font-size|moji|onsei|accessibility"
    r')[^"]*"',
    re.I,
)
# 本文らしい id/class を持つ要素は、共通パーツの語を含んでいても切らない
CONTENT = re.compile(r'(id|class)="[^"]*(content|honbun|main|detail|article|kiji|shousai)[^"]*"', re.I)
CHROME_MAX = 1200         # これより本文が長い要素は共通パーツ扱いしない（本文を丸ごと切らないため）
CHROME_RATIO = 0.3        # ページ全体の文字数に対する上限も同時にかける
TAGS = re.compile(r"<[^>]+>")
BLOCK = re.compile(r"</(p|li|h[1-6]|div|tr|td|th|section|article|dd|dt)>|<br\s*/?>", re.I)
NOISE = re.compile(r"(現在時刻|アクセス数|カウンター|\d{4}年\d{1,2}月\d{1,2}日\s*\d{1,2}:\d{2}:\d{2}|ファクス|FAX|ＦＡＸ|かけ間違い|お問い合わせフォーム|お問い合わせ先|ページの先頭|ページトップ|文字サイズ|印刷する|Copyright|All Rights Reserved|メニューを閉じる|閲覧支援|音声読み上げ|ふりがな|スキップ|本文へ移動|メニューを飛ばして)", re.I)


def now() -> datetime:
    return datetime.now(JST)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    with urllib.request.urlopen(req, timeout=30, context=CTX) as res:
        raw = res.read()
        enc = res.headers.get_content_charset() or "utf-8"
        try:
            return raw.decode(enc, errors="replace")
        except LookupError:
            return raw.decode("utf-8", errors="replace")


def request_archive(url: str) -> str:
    """Wayback Machine に保存を依頼し、タイムスタンプ付きのスナップショットURL（近似）を返す。
    失敗したら空文字。結果は待たない（レスポンスは読み捨て）。"""
    stamp = now().astimezone(timezone.utc).strftime("%Y%m%d%H%M%S")
    for attempt in range(2):
        try:
            req = urllib.request.Request("https://web.archive.org/save/" + url,
                                         headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30, context=CTX) as res:
                res.read(1024)
            return f"https://web.archive.org/web/{stamp}/{url}"
        except Exception:
            if attempt == 0:
                time.sleep(3)
    return ""


def append_month_log(new_events: list[dict]) -> None:
    """月別の追記専用ログへイベントを足す（重複は at+url で排除）。"""
    if not new_events:
        return
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    by_month: dict[str, list[dict]] = {}
    for e in new_events:
        by_month.setdefault(e["at"][:7], []).append(e)
    for month, evs in by_month.items():
        path = LOG_DIR / f"{month}.json"
        data = []
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                data = []
        seen = {(x.get("at"), x.get("url")) for x in data}
        for e in evs:
            if (e.get("at"), e.get("url")) not in seen:
                data.append(e)
        data.sort(key=lambda x: x.get("at", ""))
        path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def close_at(html: str, start: int, name: str) -> int | None:
    """start 以降で name の対応する閉じタグを探し、その終端位置を返す。"""
    depth = 1
    for m in TAG.finditer(html, start):
        if m.group(2).lower() != name:
            continue
        if m.group(3).rstrip().endswith("/"):
            continue
        if m.group(1):
            depth -= 1
            if depth == 0:
                return m.end()
        else:
            depth += 1
    return None


def cut_chrome(html: str) -> str:
    """id/class が共通パーツらしい要素を、対応する閉じタグまで丸ごと取り除く。

    本文を包む div が class に navi などを含むことがあるので、中の文字数が多い要素は
    共通パーツとみなさず、その内側だけを見に行く。
    """
    limit = max(CHROME_MAX, int(len(TAGS.sub(" ", html)) * CHROME_RATIO))
    kept: list[str] = []
    cursor = pos = 0
    while True:
        m = next((m for m in TAG.finditer(html, pos)
                  if not m.group(1) and m.group(2).lower() not in VOID
                  and not m.group(3).rstrip().endswith("/")
                  and CHROME.search(m.group(3)) and not CONTENT.search(m.group(3))), None)
        if m is None:
            break
        end = close_at(html, m.end(), m.group(2).lower())
        if end is None or len(TAGS.sub(" ", html[m.end():end])) > limit:
            pos = m.end()
            continue
        kept.append(html[cursor:m.start()])
        cursor = pos = end
    kept.append(html[cursor:])
    return " ".join(kept)


def to_lines(page: str) -> list[str]:
    body = page
    m = re.search(r"<main\b[^>]*>(.*?)</main>", page, re.S | re.I)
    if m:
        body = m.group(1)
    body = STRIP.sub(" ", body)
    body = cut_chrome(body)
    body = BLOCK.sub("\n", body)
    text = TAGS.sub(" ", body)
    text = htmlmod.unescape(text)
    lines = []
    for ln in text.split("\n"):
        ln = re.sub(r"\s+", " ", ln).strip()
        if len(ln) < 8:
            continue
        if NOISE.search(ln):
            continue
        lines.append(ln)
    return lines


def digest(lines: list[str]) -> str:
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()[:16]


def main() -> int:
    munis = {m["slug"]: m["name"] for m in json.loads(MUNIS.read_text(encoding="utf-8"))}
    munis.update(site_config.region_names())
    rows = list(csv.DictReader(CSV.open(encoding="utf-8", newline="")))
    state = {"checked_at": "", "by_url": {}, "events": [], "errors": []}
    if STATE.exists():
        try:
            state = json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            pass
    by_url: dict = state.get("by_url", {})
    events: list = state.get("events", [])
    errors: list = []
    ts = now().isoformat(timespec="seconds")
    changed = 0
    rebaselined = 0
    seen = 0
    new_events: list[dict] = []
    only = sys.argv[1:]  # slug で絞る（手動確認用）

    for r in rows:
        url = (r.get("url") or "").strip()
        slug = (r.get("slug") or "").strip()
        if not url.startswith("http") or (only and slug not in only):
            continue
        seen += 1
        prev = by_url.get(url)
        try:
            lines = to_lines(fetch(url))
        except Exception as e:
            msg = str(e)[:120]
            errors.append({"url": url, "slug": slug, "error": msg})
            # 前回の値は残しつつ、開けなかったことを記録する（404 などは UI で「開けない」と出す）
            entry = prev.copy() if prev else {"slug": slug, "kind": r.get("kind", ""), "title": (r.get("title") or "").strip(),
                                                "hash": "", "first_seen": ts, "last_changed": "", "added": [], "lines": []}
            entry["last_error"] = msg
            entry["last_error_at"] = ts
            by_url[url] = entry
            continue
        h = digest(lines)
        entry = prev.copy() if prev else {}
        entry.pop("last_error", None)
        entry.pop("last_error_at", None)
        entry.update({
            "slug": slug,
            "kind": r.get("kind", ""),
            "title": (r.get("title") or "").strip(),
            "hash": h,
            "extract": EXTRACT,
            "last_checked": ts,
        })
        if not prev or not prev.get("hash"):
            entry["first_seen"] = entry.get("first_seen") or ts
            entry["last_changed"] = ""
            entry["added"] = []
            entry["lines"] = lines[:400]
        elif prev.get("extract") != EXTRACT:
            # 抽出方法を変えた直後は前回と比べる土台が違う。基準を取り直すだけで「更新」にはしない
            entry["lines"] = lines[:400]
            rebaselined += 1
        elif prev.get("hash") != h:
            old = set(prev.get("lines") or [])
            newset = set(lines)
            added = [ln for ln in lines if ln not in old][:MAX_ADDED]
            removed = [ln for ln in (prev.get("lines") or []) if ln not in newset][:MAX_REMOVED]
            entry["last_changed"] = ts
            entry["added"] = added
            entry["lines"] = lines[:400]
            ev = {
                "at": ts, "slug": slug, "name": munis.get(slug, slug), "kind": r.get("kind", ""),
                "title": entry["title"], "url": url, "added": added, "removed": removed,
            }
            events.append(ev)
            new_events.append(ev)
            changed += 1
        by_url[url] = entry

    # 監視対象から外れた URL は残さない
    keep = {(r.get("url") or "").strip() for r in rows}
    removed = [u for u in by_url if u not in keep]
    by_url = {u: v for u, v in by_url.items() if u in keep}
    events = events[-MAX_EVENTS:]

    # 変化がないときはファイルを書かない（定期実行のたびにコミットを増やさないため）
    prev_errors = {(e.get("url"), e.get("error")) for e in state.get("errors", [])}
    now_errors = {(e.get("url"), e.get("error")) for e in errors}
    new_urls = [u for u, e in by_url.items() if e.get("first_seen") == ts]
    significant = changed > 0 or rebaselined > 0 or prev_errors != now_errors or bool(new_urls) or bool(removed) or not OUT.exists() or not STATE.exists()
    if not significant:
        print(f"watched={seen} changed=0 errors={len(errors)} no-change at {ts}")
        return 0

    # 変更のあったページを Wayback Machine へ保存依頼（直列・間隔あり・失敗は無視）
    for i, ev in enumerate(new_events[:ARCHIVE_MAX]):
        if i:
            time.sleep(ARCHIVE_WAIT)
        a = request_archive(ev["url"])
        if a:
            ev["archive_url"] = a
            e = by_url.get(ev["url"])
            if e is not None:
                e["archive_url"] = a
    if len(new_events) > ARCHIVE_MAX:
        print(f"archive skipped for {len(new_events) - ARCHIVE_MAX} events (over ARCHIVE_MAX)")

    # 月別の追記専用ログ（消えない履歴）
    append_month_log(new_events)

    # 比較用の状態（本文行を含む）は data/ に、公開用（軽い）は site/data/ に分ける
    STATE.write_text(json.dumps({"checked_at": ts, "by_url": by_url, "events": events, "errors": errors},
                                ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    public = {
        "checked_at": ts,
        "note": "市町村公式ページの本文が前回取得時から変わったかを自動で見ています。何が変わったかは公式ページで確認してください。added は機械抽出の見出し候補で、正確でないことがあります。",
        "by_url": {u: {k: v for k, v in e.items() if k not in ("lines", "extract")} for u, e in by_url.items()},
        "events": events,
        "errors": errors,
    }
    OUT.write_text(json.dumps(public, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"watched={seen} changed={changed} rebaselined={rebaselined} errors={len(errors)} events={len(events)} at {ts}")
    for e in errors:
        print("  ERR", e["slug"], e["url"], e["error"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
