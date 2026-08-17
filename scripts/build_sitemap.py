# -*- coding: utf-8 -*-
"""日英 sitemap.xml と robots.txt を生成する。市町村は slug から並べる。"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BASE = "https://office626.github.io/r808chibagouu/"

STATIC = [
    ("", "daily", "1.0"),
    ("resident/index.html", "daily", "0.9"),
    ("resident/timeline.html", "weekly", "0.9"),
    ("resident/situations.html", "weekly", "0.9"),
    ("resident/housing.html", "weekly", "0.8"),
    ("resident/life.html", "weekly", "0.8"),
    ("resident/business.html", "weekly", "0.8"),
    ("resident/municipalities.html", "daily", "0.9"),
    ("resident/prefecture.html", "daily", "0.7"),
    ("supporters/index.html", "weekly", "0.5"),
    ("supporters/ideas.html", "weekly", "0.4"),
]


def main() -> int:
    munis = json.loads((SITE / "data" / "municipalities.json").read_text(encoding="utf-8"))
    rows = list(STATIC)
    for m in munis:
        rows.append((f"resident/municipality.html?slug={quote(m['slug'])}", "daily", "0.8"))
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]
    for path, freq, pri in rows:
        ja = BASE + path
        en = BASE + "en/" + path
        for loc in (ja, en):
            loc_xml = loc.replace("&", "&amp;")
            ja_xml = ja.replace("&", "&amp;")
            en_xml = en.replace("&", "&amp;")
            lines.extend([
                "  <url>",
                f"    <loc>{loc_xml}</loc>",
                f'    <xhtml:link rel="alternate" hreflang="ja" href="{ja_xml}"/>',
                f'    <xhtml:link rel="alternate" hreflang="en" href="{en_xml}"/>',
                f'    <xhtml:link rel="alternate" hreflang="x-default" href="{ja_xml}"/>',
                f"    <changefreq>{freq}</changefreq>",
                f"    <priority>{pri}</priority>",
                "  </url>",
            ])
    lines.append("</urlset>")
    (SITE / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (SITE / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: " + BASE + "sitemap.xml\n", encoding="utf-8"
    )
    print(f"wrote sitemap.xml ({len(rows) * 2} urls) and robots.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
