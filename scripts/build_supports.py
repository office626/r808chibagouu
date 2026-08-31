# -*- coding: utf-8 -*-
"""市町村公式の支援リンク（罹災証明・災害ごみ・消毒・住まい・ボランティアなど）を data/supports.csv から
site/data/supports.json へ変換する。全文転載しない。見出しとURLのみ。

CSV の列:
  slug      municipalities.json の slug
  kind      hub / risai / support / waste / disinfect / water / housing / vc / home
  title     公式ページの見出し（そのまま。言い換えは最小限）
  url       公式ページの URL
  status    open（受付中・掲載中）/ preparing（準備中）/ closed（終了）/ checking（通報を受けて確認中）/ unknown（未確認）
  checked   最後に人が確認した日 YYYY-MM-DD
  deadline  期限（公式に書かれているときだけ。例 2026-09-30、または「9月末まで」など）
  note      補足（サイトには短く出る）

支援者は CSV に1行足す・直すだけでよい。ビルドは日次ジョブと手動で行う。
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import site_config

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "supports.csv"
OUT = ROOT / "site" / "data" / "supports.json"

NOTE = (
    "各市町村公式のお知らせへのリンク。今回の大雨専用ページでない場合もある。"
    "受付の有無・対象・期限は必ず公式で確認すること。status と checked は有志が確認した時点の値。"
)

KIND_LABEL = {
    "hub": "大雨情報まとめ",
    "risai": "罹災証明",
    "support": "支援策",
    "business": "事業者向け",
    "waste": "災害ごみ",
    "disinfect": "消毒",
    "water": "断水・水道",
    "housing": "住まい",
    "vc": "ボランティア",
    "home": "公式",
}
KIND_LABEL_EN = {
    "hub": "Heavy-rain information hub",
    "risai": "Damage certificate",
    "support": "Support",
    "business": "For businesses",
    "waste": "Disaster waste",
    "disinfect": "Disinfection",
    "water": "Water supply",
    "housing": "Housing",
    "vc": "Volunteer center",
    "home": "Official site",
}
KIND_ORDER = ["hub", "risai", "support", "business", "waste", "disinfect", "water", "housing", "vc", "home"]
STATUS_LABEL = {"open": "受付中・掲載中", "preparing": "準備中", "closed": "終了", "checking": "確認中", "unknown": "要確認"}
STATUS_LABEL_EN = {"open": "Open / posted", "preparing": "Preparing", "closed": "Closed", "checking": "Being verified", "unknown": "Unverified"}


EXTRA_GROUPS = site_config.regions()


def main() -> int:
    munis = json.loads((ROOT / "site" / "data" / "municipalities.json").read_text(encoding="utf-8"))
    slugs = {m["slug"] for m in munis} | {g["slug"] for g in EXTRA_GROUPS}
    rows_by_slug: dict[str, list[dict]] = {}
    bad = []
    with CSV.open(encoding="utf-8", newline="") as f:
        for i, r in enumerate(csv.DictReader(f), start=2):
            slug = (r.get("slug") or "").strip()
            kind = (r.get("kind") or "").strip()
            title = (r.get("title") or "").strip()
            url = (r.get("url") or "").strip()
            status = (r.get("status") or "unknown").strip() or "unknown"
            if slug not in slugs or kind not in KIND_LABEL or not title or not url.startswith("http"):
                bad.append((i, slug, kind, title[:30], url[:40]))
                continue
            if status not in STATUS_LABEL:
                status = "unknown"
            rows_by_slug.setdefault(slug, []).append({
                "kind": kind,
                "kind_label": KIND_LABEL[kind],
                "kind_label_en": KIND_LABEL_EN[kind],
                "title": title,
                "url": url,
                "status": status,
                "status_label": STATUS_LABEL[status],
                "status_label_en": STATUS_LABEL_EN[status],
                "checked": (r.get("checked") or "").strip(),
                "deadline": (r.get("deadline") or "").strip(),
                "note": (r.get("note") or "").strip(),
            })
    if bad:
        for b in bad:
            print("skip row", b)

    by_slug = {}
    for g in EXTRA_GROUPS:
        by_slug[g["slug"]] = sorted(rows_by_slug.get(g["slug"], []), key=lambda x: KIND_ORDER.index(x["kind"]))
    for m in munis:
        slug = m["slug"]
        rows = rows_by_slug.get(slug, [])
        rows.sort(key=lambda x: KIND_ORDER.index(x["kind"]))
        if not rows:
            rows.append({
                "kind": "home", "kind_label": "公式", "kind_label_en": KIND_LABEL_EN["home"],
                "title": m["name"] + "公式サイトで罹災証明・支援窓口を検索",
                "url": m["url"], "status": "unknown", "status_label": STATUS_LABEL["unknown"],
                "status_label_en": STATUS_LABEL_EN["unknown"],
                "checked": "", "deadline": "", "note": "",
            })
        by_slug[slug] = rows

    kinds_present = sorted({r["kind"] for rows in by_slug.values() for r in rows})
    out = {
        "note": NOTE,
        "groups": EXTRA_GROUPS,
        "kind_labels": KIND_LABEL,
        "kind_labels_en": KIND_LABEL_EN,
        "status_labels": STATUS_LABEL,
        "status_labels_en": STATUS_LABEL_EN,
        "by_slug": by_slug,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    dedicated = sum(1 for rows in by_slug.values() if rows and rows[0]["kind"] != "home")
    total = sum(len(rows) for rows in by_slug.values())
    print(f"wrote {OUT} rows={total} dedicated={dedicated} fallback={len(by_slug) - dedicated} kinds={kinds_present}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
