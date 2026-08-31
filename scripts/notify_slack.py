# -*- coding: utf-8 -*-
"""公式ページの更新検知（site/data/watch.json の events）を Slack にデイリーでまとめて投稿する。

- 直近24時間の events を市町村ごとにまとめ、1投稿にする
- 0件なら投稿しない（終了コード 0）
- Webhook URL は環境変数 SLACK_WEBHOOK_URL で渡す（コード・リポジトリに書かない）
- 手動確認: SLACK_WEBHOOK_URL=... python scripts/notify_slack.py [--dry-run] [--hours 24]
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WATCH = ROOT / "site" / "data" / "watch.json"
CAND = ROOT / "site" / "data" / "candidates.json"
JST = timezone(timedelta(hours=9))
SITE = "https://office626.github.io/r808chibagouu/"
KIND_JA = {
    "hub": "大雨情報まとめ", "risai": "罹災証明", "support": "支援策", "waste": "災害ごみ",
    "disinfect": "消毒", "water": "断水・水道", "housing": "住まい", "vc": "ボランティア", "home": "公式",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="投稿せず本文を表示する")
    ap.add_argument("--hours", type=int, default=24)
    args = ap.parse_args()

    webhook = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if not webhook and not args.dry_run:
        print("SLACK_WEBHOOK_URL is not set; skipping")
        return 0

    if not WATCH.exists():
        print("watch.json not found; skipping")
        return 0
    watch = json.loads(WATCH.read_text(encoding="utf-8"))
    now = datetime.now(JST)
    since = now - timedelta(hours=args.hours)

    recent = []
    for e in watch.get("events", []):
        try:
            at = datetime.fromisoformat(e.get("at", ""))
        except ValueError:
            continue
        if at >= since:
            recent.append(e)
    has_broken = any(v.get("last_error") for v in (watch.get("by_url") or {}).values())
    if not recent and not has_broken:
        print("no updates in window; not posting")
        return 0

    # 同じページが期間内に複数回変わっていたら最新だけにする
    recent.sort(key=lambda e: e.get("at", ""), reverse=True)
    seen_urls = set()
    deduped = []
    for e in recent:
        u = e.get("url")
        if u in seen_urls:
            continue
        seen_urls.add(u)
        deduped.append(e)
    recent = deduped

    # 市町村ごとにまとめる（新しい順）
    by_muni: dict[str, list[dict]] = {}
    order: list[str] = []
    for e in recent:
        name = e.get("name") or e.get("slug", "")
        if name not in by_muni:
            by_muni[name] = []
            order.append(name)
        by_muni[name].append(e)

    date_label = now.strftime("%-m/%-d")
    if recent:
        lines = [f"*【公式ページ更新 {date_label}】{len(order)}市町村・{len(recent)}件*（過去{args.hours}時間・自動検知）"]
    else:
        lines = [f"*【公式ページ更新 {date_label}】この24時間の更新検知はありません*"]
    for name in order:
        evs = by_muni[name]
        for e in evs[:3]:
            kind = KIND_JA.get(e.get("kind", ""), "")
            t = (e.get("title") or "").strip()
            added = e.get("added") or []
            hint = f"｜{added[0][:48]}" if added else ""
            lines.append(f"・{name}（{kind}）<{e.get('url')}|{t[:60]}>{hint}")
        if len(evs) > 3:
            lines.append(f"・{name}：ほか{len(evs) - 3}件")
    # 要張り替え：直近の自動確認で開けなかった公式リンク
    broken = [(u, v) for u, v in (watch.get("by_url") or {}).items() if v.get("last_error")]
    if broken:
        lines.append(f"\n*要対応：開けない公式リンク {len(broken)}件*（移設の可能性。張り替え先を探して CSV を修正）")
        for u, v in broken[:8]:
            lines.append(f"・{v.get('slug','')}（{KIND_JA.get(v.get('kind',''),'')}）{(v.get('title') or '')[:40]}｜{u}")
        if len(broken) > 8:
            lines.append(f"・ほか{len(broken) - 8}件")

    # 本日の候補：公式トップから拾った未収載リンク
    try:
        cand = json.loads(CAND.read_text(encoding="utf-8")) if CAND.exists() else {}
    except Exception:
        cand = {}
    cands = cand.get("candidates") or []
    if cands:
        lines.append(f"\n*本日の候補：未収載の公式リンク {len(cands)}件*（公式を見て、載せる価値があれば CSV に1行追加）")
        for c in cands[:10]:
            lines.append(f"・{c['name']}：<{c['url']}|{c['title'][:48]}>")
        if len(cands) > 10:
            lines.append(f"・ほか{len(cands) - 10}件")

    lines.append(f"\n検知は数時間おきで、実際の更新は検知より前のことがあります。何が変わったかは公式ページで確認してください。サイト: <{SITE}resident/index.html|最近の更新一覧>")
    lines.append(f"CSV を直す: <https://github.com/office626/r808chibagouu/edit/main/data/supports.csv|data/supports.csv を編集>（列: slug,kind,title,url,status,checked,deadline,note）。反映は毎朝6:00、急ぎは Actions の Daily collect を手動実行。")
    text = "\n".join(lines)

    if args.dry_run:
        print(text)
        return 0

    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(webhook, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20, context=ssl.create_default_context()) as res:
        body = res.read().decode("utf-8", errors="replace")
    print(f"posted {len(recent)} events; slack said: {body}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
