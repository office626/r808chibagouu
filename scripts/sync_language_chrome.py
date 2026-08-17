# -*- coding: utf-8 -*-
"""全HTMLへ言語切替スクリプトと hreflang を追加・更新する。"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BASE = "https://office626.github.io/r808chibagouu/"


def page_files() -> list[Path]:
    return sorted(
        path for path in SITE.rglob("*.html")
        if "node_modules" not in path.parts
    )


def language_urls(path: Path) -> tuple[str, str]:
    rel = path.relative_to(SITE).as_posix()
    if rel.startswith("en/"):
        plain = rel[3:]
    else:
        plain = rel
    if plain == "index.html":
        plain_url = ""
    else:
        plain_url = plain
    return BASE + plain_url, BASE + "en/" + plain_url


def script_src(path: Path) -> str:
    depth = len(path.relative_to(SITE).parents) - 1
    return "../" * depth + "js/language-switch.js"


def update(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    ja_url, en_url = language_urls(path)

    if 'hreflang="ja"' not in text:
        canonical = re.search(r'(?m)^(\s*)<link rel="canonical"[^>]*>\s*$', text)
        if not canonical:
            raise ValueError(f"canonical link not found: {path}")
        indent = canonical.group(1)
        alternates = (
            f'{indent}<link rel="alternate" hreflang="ja" href="{ja_url}">\n'
            f'{indent}<link rel="alternate" hreflang="en" href="{en_url}">\n'
            f'{indent}<link rel="alternate" hreflang="x-default" href="{ja_url}">\n'
        )
        text = text[:canonical.end()] + "\n" + alternates + text[canonical.end():]

    if "language-switch.js" not in text:
        tag = f'  <script src="{script_src(path)}"></script>\n'
        text = text.replace("</body>", tag + "</body>")

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    changed = []
    for path in page_files():
        if update(path):
            changed.append(path.relative_to(ROOT).as_posix())
    print(f"updated language chrome in {len(changed)} page(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
