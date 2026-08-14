# -*- coding: utf-8 -*-
"""毎日 6:00 JST 向け。許可リストの見出し・URL を追記する。失敗時は前回データを残す。"""
from __future__ import annotations

import html as htmlmod
import json
import re
import ssl
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urljoin

JST = timezone(timedelta(hours=9))
UA = "CTZC-r808chibagouu-collector/1.0 (+https://github.com/office626/r808chibagouu)"
CTX = ssl.create_default_context()

PORTAL = "https://www.bousai.pref.chiba.lg.jp/"
FDMA_RSS = "https://www.fdma.go.jp/disaster/info/index.xml"
FDMA_BASE = "https://www.fdma.go.jp"
JMA_FEED = "https://www.data.jma.go.jp/developer/xml/feed/extra_l.xml"
PREF_HQ = "https://www.pref.chiba.lg.jp/bousai/bousai/r8-0813ooame.html"
CHIBA_RISAI = "https://www.city.chiba.jp/sogoseisaku/kikikanri/kikikanri/sinnrisaishomei.html"

KW = re.compile(r"(豪雨|大雨|浸水|避難|特別警報|警戒レベル|罹災|災害救助|土砂|千葉豪雨)")
CHIBA = re.compile(r"千葉")

SLUG_BY_NAME = {
    "千葉市": "chiba", "市川市": "ichikawa", "船橋市": "funabashi", "松戸市": "matsudo",
    "茂原市": "mobara", "佐倉市": "sakura", "東金市": "togane", "習志野市": "narashino",
    "柏市": "kashiwa", "市原市": "ichihara", "八千代市": "yachiyo", "我孫子市": "abiko",
    "鎌ケ谷市": "kamagaya", "四街道市": "yotsukaido", "八街市": "yachimata", "印西市": "inzai",
    "白井市": "shiroi", "山武市": "sammu", "大網白里市": "oamishirasato", "九十九里町": "kujukuri",
    "白子町": "shirako", "長柄町": "nagara", "流山市": "nagareyama", "銚子市": "choshi",
    "館山市": "tateyama", "木更津市": "kisarazu", "野田市": "noda", "成田市": "narita",
    "旭市": "asahi", "勝浦市": "katsuura", "鴨川市": "kamogawa", "君津市": "kimitsu",
    "富津市": "futtsu", "浦安市": "urayasu", "袖ケ浦市": "sodegaura", "富里市": "tomisato",
    "南房総市": "minamiboso", "匝瑳市": "sosa", "香取市": "katori", "いすみ市": "isumi",
    "酒々井町": "shisui", "栄町": "sakae", "神崎町": "kozaki", "多古町": "tako",
    "東庄町": "tonosho", "芝山町": "shibayama", "横芝光町": "yokoshibahikari",
    "一宮町": "ichinomiya", "睦沢町": "mutsuzawa", "長生村": "chosei", "長南町": "chonan",
    "大多喜町": "otaki", "御宿町": "onjuku", "鋸南町": "kyonan",
}


def now_jst() -> datetime:
    return datetime.now(JST)


def fetch(url: str, timeout: int = 40) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as res:
        raw = res.read()
        enc = res.headers.get_content_charset() or "utf-8"
        return raw.decode(enc, errors="replace")


def add_item(col: dict, item: dict) -> bool:
    key = (item.get("slug"), item.get("source_url"), item.get("title"))
    for old in col["items"]:
        if (old.get("slug"), old.get("source_url"), old.get("title")) == key:
            return False
    col["items"].append(item)
    return True


def parse_rss_items(xml_text: str, base: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    out = []
    for it in root.findall(".//item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        if link.startswith("/"):
            link = urljoin(base, link)
        pub = it.findtext("pubDate") or ""
        occurred = now_jst().isoformat(timespec="seconds")
        if pub:
            try:
                occurred = parsedate_to_datetime(pub).astimezone(JST).isoformat(timespec="seconds")
            except Exception:
                pass
        out.append({"title": title, "url": link, "occurred_at": occurred})
    return out


def parse_atom_items(xml_text: str) -> list[dict]:
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml_text)
    out = []
    for ent in root.findall("a:entry", ns):
        title = (ent.findtext("a:title", default="", namespaces=ns) or "").strip()
        link_el = ent.find("a:link", ns)
        href = link_el.get("href") if link_el is not None else ""
        updated = ent.findtext("a:updated", default="", namespaces=ns) or now_jst().isoformat()
        out.append({"title": title, "url": href, "occurred_at": updated})
    return out


EVAC_CELL = re.compile(
    r">([^<]+)</a>\s*</td>\s*<td class=\"tdR\">\s*"
    r"<div class=\"kankokuWarning\">(\d{2}/\d{2}\s+\d{2}:\d{2})\s*発表</div>"
    r"[\s\S]{0,400}?<div class=\"kankokuWarning[^\"]*\">\s*([^<]+?)\s*</div>",
)
SHEL_CELL = re.compile(
    r">([^<]+)</a>\s*</td>\s*<td class=\"tdHR\">\s*"
    r"<div class=\"hinanjyoWarning\">(\d{2}/\d{2}\s+\d{2}:\d{2})\s*発表</div>"
    r"[\s\S]{0,400}?<div class=\"hinanjyoWarning[^\"]*\">\s*([^<]+?)\s*</div>",
)


def at_to_iso(at: str) -> str:
    try:
        dt = datetime.strptime(at, "%m/%d %H:%M").replace(year=now_jst().year, tzinfo=JST)
        return dt.isoformat(timespec="seconds")
    except ValueError:
        return now_jst().isoformat(timespec="seconds")


def refresh_portal_snapshots(col: dict, html: str) -> None:
    """県ポータルの表から今回災害（8月）の避難・避難所だけを更新する。"""
    text = htmlmod.unescape(html)
    snaps = col.setdefault("snapshots", {})
    for name, at, label in EVAC_CELL.findall(text):
        slug = SLUG_BY_NAME.get(name.strip())
        if not slug or not at.startswith("08/"):
            continue
        snap = snaps.setdefault(slug, {})
        status = "指示継続" if "避難指示" in label else "解除"
        new = {"status": status, "at": at, "label": label.strip()}
        old = snap.get("evacuation") or {}
        snap["evacuation"] = new
        if (old.get("status"), old.get("at")) != (new["status"], new["at"]):
            add_item(col, {
                "id": f"evac-{slug}-{at.replace(' ', '-').replace(':', '')}",
                "slug": slug,
                "occurred_at": at_to_iso(at),
                "kind": "warning",
                "title": f"県ポータル：{name}の避難情報は{label.strip()}（{at}発表）",
                "summary": "県防災ポータルの避難情報表の見出し。対象区域・解除範囲は県ポータルと市町村公式で確認すること。",
                "source_url": PORTAL,
                "source_type": "admin",
                "medium": "千葉県防災ポータル",
            })
    for name, at, status in SHEL_CELL.findall(text):
        slug = SLUG_BY_NAME.get(name.strip())
        if not slug or not at.startswith("08/"):
            continue
        snap = snaps.setdefault(slug, {})
        new = {"status": status.strip(), "at": at}
        old = snap.get("shelter") or {}
        snap["shelter"] = new
        if (old.get("status"), old.get("at")) != (new["status"], new["at"]):
            add_item(col, {
                "id": f"shelter-{slug}-{at.replace(' ', '-').replace(':', '')}",
                "slug": slug,
                "occurred_at": at_to_iso(at),
                "kind": "shelter",
                "title": f"県ポータル：{name}の避難所は{status.strip()}（{at}発表）",
                "summary": "県防災ポータルの避難所開設状況の見出し。施設名・対象は県ポータルと市町村公式で確認すること。",
                "source_url": PORTAL,
                "source_type": "admin",
                "medium": "千葉県防災ポータル",
            })


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    path = root / "site" / "data" / "collection.json"
    col = json.loads(path.read_text(encoding="utf-8"))
    ok = False
    errors = []
    added = 0
    fetched = now_jst().isoformat(timespec="seconds")

    try:
        portal = fetch(PORTAL)
        refresh_portal_snapshots(col, portal)
        ok = True
        if add_item(col, {
            "id": f"portal-refresh-{fetched[:10]}",
            "slug": "prefecture",
            "occurred_at": fetched,
            "kind": "warning",
            "title": "県防災ポータルの避難・避難所情報を再取得",
            "summary": "8月13日からの大雨に関する市町村の避難情報・避難所開設状況を県ポータルから更新した。地盤が緩んでいるため、少雨でも土砂災害に注意するよう呼びかけが続いている。",
            "source_url": PORTAL,
            "source_type": "admin",
            "medium": "千葉県防災ポータル",
        }):
            added += 1
    except Exception as e:
        errors.append(f"portal: {e}")

    try:
        rss = fetch(FDMA_RSS)
        for it in parse_rss_items(rss, FDMA_BASE):
            if "千葉豪雨" not in it["title"] and not (CHIBA.search(it["title"]) and KW.search(it["title"])):
                continue
            if add_item(col, {
                "id": "fdma-" + re.sub(r"[^a-zA-Z0-9]+", "-", it["url"])[-40:],
                "slug": "prefecture",
                "occurred_at": it["occurred_at"],
                "kind": "damage",
                "title": it["title"],
                "summary": "消防庁の災害情報一覧の見出し。詳細は公式PDF・ページで確認すること。速報であり数値は変わりうる。",
                "source_url": it["url"],
                "source_type": "admin",
                "medium": "総務省消防庁",
            }):
                added += 1
        ok = True
    except Exception as e:
        errors.append(f"fdma: {e}")

    try:
        atom = fetch(JMA_FEED)
        for it in parse_atom_items(atom):
            text = it["title"]
            if "千葉" not in text:
                continue
            if not KW.search(text):
                continue
            if add_item(col, {
                "id": "jma-" + re.sub(r"[^a-zA-Z0-9]+", "-", it["url"])[-40:],
                "slug": "prefecture",
                "occurred_at": it["occurred_at"],
                "kind": "warning",
                "title": text[:120],
                "summary": "気象庁XMLフィードの見出し。警報の最新は気象庁の千葉県ページで確認すること。",
                "source_url": it["url"] or "https://www.jma.go.jp/bosai/warning/#area_type=offices&area_code=120000",
                "source_type": "admin",
                "medium": "気象庁",
            }):
                added += 1
        ok = True
    except Exception as e:
        errors.append(f"jma: {e}")

    try:
        html = fetch(CHIBA_RISAI)
        if "臨時窓口" in html or "８月１５日" in html or "8月15日" in html:
            if add_item(col, {
                "id": "chiba-risai-temp-20260815",
                "slug": "chiba",
                "occurred_at": "2026-08-14T00:00:00+09:00",
                "kind": "support",
                "title": "千葉市：8月15・16日に罹災証明の臨時窓口",
                "summary": "令和8年8月13日の大雨による罹災証明書・被災証明書の申請のため、15日・16日に各区で臨時窓口を開設すると公式が案内。即日交付は行わない。詳細は市公式。",
                "source_url": CHIBA_RISAI,
                "source_type": "admin",
                "medium": "千葉市",
            }):
                added += 1
        ok = True
    except Exception as e:
        errors.append(f"chiba-risai: {e}")

    try:
        fetch(PREF_HQ)
        ok = True
    except Exception as e:
        errors.append(f"pref-hq: {e}")

    if ok:
        col["fetched_at"] = fetched
        col["method"] = "日次ジョブ。許可リストの見出しとURLのみ。失敗したソースは前回を維持。"
        if errors:
            col["last_errors"] = errors
        else:
            col.pop("last_errors", None)
        path.write_text(json.dumps(col, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"updated fetched_at={fetched} added={added}")
        return 0

    print("all sources failed; keeping previous data")
    for e in errors:
        print(e)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
