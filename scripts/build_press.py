# -*- coding: utf-8 -*-
"""市町村ページ用の報道リンク（見出し・URLのみ。RSS再配信はしない）。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site" / "data" / "press.json"

# 県全体。全文転載せず、見出しと1文の要約のみ。
COUNTY = [
    {
        "id": "nhk-20260815-deaths",
        "occurred_at": "2026-08-15T06:05:00+09:00",
        "title": "千葉で記録的豪雨 ８人死亡 浸水被害相次ぐ",
        "summary": "NHKは、線状降水帯が相次いだ県内で死亡8人、建物浸水が相次いでいると報じた。数値は速報。",
        "url": "https://news.web.nhk/newsweb/na/nd-20260815de44204",
        "medium": "NHK",
    },
    {
        "id": "tvasahi-timeline",
        "occurred_at": "2026-08-14T12:00:00+09:00",
        "title": "【発生からの情報まとめ】千葉の記録的豪雨　車内“閉じ込め”など…線状降水帯3回",
        "summary": "テレ朝NEWSの時系列。大網白里の冠水、東金・九十九里・山武の記録的短時間大雨、レベル5対象市町を伝えている。",
        "url": "https://news.tv-asahi.co.jp/news_society/articles/900197093.html",
        "medium": "テレ朝NEWS",
    },
    {
        "id": "tvasahi-flood-continue",
        "occurred_at": "2026-08-15T12:25:00+09:00",
        "title": "千葉豪雨 広範囲で浸水続く 各地で土砂災害も",
        "summary": "テレ朝NEWSは、千葉市の記録的雨量や茂原市の線路が水没した跡のドローン映像などを伝えている。",
        "url": "https://news.tv-asahi.co.jp/news_society/articles/900197180.html",
        "medium": "テレ朝NEWS",
    },
    {
        "id": "tbs-line",
        "occurred_at": "2026-08-15T05:30:00+09:00",
        "title": "千葉県で相次ぎ線状降水帯　記録的豪雨で8人死亡　成田空港では約7000人が一夜明かす　自衛隊に災害派遣要請も",
        "summary": "TBS NEWS DIGは冠水した道路での車水没、大網白里のドローン映像、成田空港の滞留などを報じた。",
        "url": "https://newsdig.tbs.co.jp/articles/-/2873319",
        "medium": "TBS NEWS DIG",
    },
    {
        "id": "yahoo-tbs",
        "occurred_at": "2026-08-15T05:30:00+09:00",
        "title": "千葉県で相次ぎ線状降水帯が発生　記録的豪雨で8人死亡　冠水した道路で車水没、成田空港では約7000人が一夜明かす（TBS NEWS DIG）",
        "summary": "Yahoo!ニュース経由のテレビ報道。詳細は各社のページで確認すること。",
        "url": "https://news.yahoo.co.jp/articles/844c7143b7d021d63c815158d661ab208726af57",
        "medium": "Yahoo!ニュース（TBS）",
    },
    {
        "id": "yahoo-ntv",
        "occurred_at": "2026-08-14T12:00:00+09:00",
        "title": "【千葉豪雨・被害まとめ】死者8人“帰宅困難者”1万人超（日テレNEWS）",
        "summary": "Yahoo!ニュース経由の日本テレビ報道。見出しとリンクのみ掲載する。",
        "url": "https://news.yahoo.co.jp/articles/bac5a2da72a077e7ce512304980fb67a1d2e3abe",
        "medium": "Yahoo!ニュース（日テレNEWS）",
    },
    {
        "id": "yahoo-chibatv",
        "occurred_at": "2026-08-14T12:00:00+09:00",
        "title": "千葉県内で記録的大雨　8人死亡32人重軽傷　各地で冠水　住宅全壊など被害多数（チバテレ）",
        "summary": "Yahoo!ニュース経由の千葉テレビ報道。地元局の続報はリンク先で確認すること。",
        "url": "https://news.yahoo.co.jp/articles/12f6a45c831ba435dbabbd982b48f34adee1e19d",
        "medium": "Yahoo!ニュース（チバテレ）",
    },
    {
        "id": "jiji-l5",
        "occurred_at": "2026-08-14T08:00:00+09:00",
        "title": "千葉豪雨　死者の内訳とレベル5対象市町（時事）",
        "summary": "時事通信は人的被害の市町村内訳と、大雨特別警報の対象22市町を伝えている。数値は速報。",
        "url": "https://sp.m.jiji.com/article/show/3845233",
        "medium": "時事通信",
    },
    {
        "id": "sankei-overview",
        "occurred_at": "2026-08-14T10:00:00+09:00",
        "title": "千葉の記録的大雨　被害の様子",
        "summary": "産経新聞の報道。写真・続報は出典で確認すること。",
        "url": "https://www.sankei.com/article/20260814-LAABO5FPYJK25IRXWHJOAIC5IY/",
        "medium": "産経新聞",
    },
    {
        "id": "mainichi-places",
        "occurred_at": "2026-08-13T22:00:00+09:00",
        "title": "千葉県内で冠水・浸水　市川・佐倉・八千代・柏・千葉など",
        "summary": "毎日新聞は市川市二俣、佐倉市小竹・上志津、八千代市上高野、柏市八幡町、千葉市若葉区和泉町などに触れている。",
        "url": "https://mainichi.jp/articles/20260813/hrc/00m/040/001000d",
        "medium": "毎日新聞",
    },
    {
        "id": "nikkei-l5",
        "occurred_at": "2026-08-13T19:30:00+09:00",
        "title": "千葉にレベル5大雨特別警報　運用見直し後初",
        "summary": "日本経済新聞は22市町への大雨特別警報と6市への土砂災害特別警報、河川の水位超過を報じた。",
        "url": "https://www.nikkei.com/article/DGXZQOUD137E20T10C26A8000000/",
        "medium": "日本経済新聞",
    },
    {
        "id": "wni-l5",
        "occurred_at": "2026-08-13T19:30:00+09:00",
        "title": "レベル5大雨特別警報の対象22市町",
        "summary": "ウェザーニュースが伝えた対象リスト。特別警報は14日明け方に切替との後報あり。最新は気象庁。",
        "url": "https://weathernews.jp/news/202608/130321/",
        "medium": "ウェザーニュース",
    },
    {
        "id": "sponichi-stranded",
        "occurred_at": "2026-08-15T05:30:00+09:00",
        "title": "成田空港で7000人足止め　千葉駅などターミナルで帰宅困難者であふれる",
        "summary": "スポニチは成田空港・千葉駅・蘇我駅周辺・大網駅前などの滞留・冠水を伝えている。",
        "url": "https://www.sponichi.co.jp/society/news/2026/08/15/kiji/20260815s00042000050000c.html",
        "medium": "スポーツニッポン",
    },
]

LOCAL: dict[str, list[dict]] = {
    "chiba": [
        {
            "id": "yomiuri-soga",
            "occurred_at": "2026-08-14T10:13:00+09:00",
            "title": "千葉大雨で1万人超える帰宅困難者…成田空港や県庁で一夜、JR蘇我駅は周辺が水没",
            "summary": "読売新聞は県庁の一時滞在、蘇我駅周辺の冠水、自衛隊による輸送支援を報じた。",
            "url": "https://topics.smt.docomo.ne.jp/article/yomiuri/nation/20260814-567-GYT1T00104",
            "medium": "読売新聞",
        },
        {
            "id": "fnn-soga",
            "occurred_at": "2026-08-14T08:38:00+09:00",
            "title": "自衛隊　JR蘇我駅周辺の帰宅困難者約4000人の輸送支援を開始",
            "summary": "FNNは県知事の災害派遣要請を受け、蘇我駅から県文化会館へのバス輸送が始まったと報じた。",
            "url": "https://www.fnn.jp/articles/-/1094510",
            "medium": "FNNプライムオンライン",
        },
        {
            "id": "yahoo-sento",
            "occurred_at": "2026-08-15T12:00:00+09:00",
            "title": "停電・断水で風呂に入れない人へ千葉市の銭湯が入浴支援",
            "summary": "Yahoo!ニュース（エキスパート）。稲毛区の銭湯が入浴支援を呼びかけたと報じている。支援の可否は店舗へ。",
            "url": "https://news.yahoo.co.jp/expert/articles/716d78c02c7c95387d83f6c08d28944485a1ba0e",
            "medium": "Yahoo!ニュース",
        },
    ],
    "ichikawa": [
        {
            "id": "nhk-ichikawa",
            "occurred_at": "2026-08-15T06:05:00+09:00",
            "title": "市川市でも人的被害が報じられている（県全体のNHK記事）",
            "summary": "NHK・消防庁などの速報で、市川市の死亡が県内被害の内訳に含まれている。詳細は公式・出典。",
            "url": "https://news.web.nhk/newsweb/na/nd-20260815de44204",
            "medium": "NHK",
        },
    ],
    "sakura": [
        {
            "id": "nhk-sakura",
            "occurred_at": "2026-08-15T06:05:00+09:00",
            "title": "佐倉市でも人的被害が報じられている（県全体のNHK記事）",
            "summary": "NHKは佐倉市で複数の死亡が確認されたと伝えている。数値は速報。",
            "url": "https://news.web.nhk/newsweb/na/nd-20260815de44204",
            "medium": "NHK",
        },
    ],
    "yachiyo": [
        {
            "id": "nhk-yachiyo",
            "occurred_at": "2026-08-15T06:05:00+09:00",
            "title": "八千代市上高野付近の冠水が報じられている（NHK）",
            "summary": "NHKは八千代市での人的被害を県内内訳として伝えている。詳細は市公式・出典。",
            "url": "https://news.web.nhk/newsweb/na/nd-20260815de44204",
            "medium": "NHK",
        },
    ],
    "kashiwa": [
        {
            "id": "nikkei-kashiwa",
            "occurred_at": "2026-08-13T19:30:00+09:00",
            "title": "柏市などで道路冠水・住宅浸水の情報が多数（日経）",
            "summary": "日本経済新聞は坂川・新坂川・国分川の水位超過と、柏市への冠水情報を報じた。",
            "url": "https://www.nikkei.com/article/DGXZQOUD137E20T10C26A8000000/",
            "medium": "日本経済新聞",
        },
    ],
    "oamishirasato": [
        {
            "id": "tvasahi-oami",
            "occurred_at": "2026-08-14T08:40:00+09:00",
            "title": "大網白里市で大規模冠水　多数の車が水没、床上浸水も",
            "summary": "テレ朝NEWSは大網駅付近の広範囲冠水と床上・床下浸水の報告を伝えている。",
            "url": "https://news.tv-asahi.co.jp/news_society/articles/900197093.html",
            "medium": "テレ朝NEWS",
        },
    ],
    "mobara": [
        {
            "id": "tvasahi-mobara",
            "occurred_at": "2026-08-15T12:25:00+09:00",
            "title": "茂原市をドローンで撮影　線路が水没した跡",
            "summary": "テレ朝NEWSは一夜明けの茂原市で線路が水没した跡が見て取れると報じた。",
            "url": "https://news.tv-asahi.co.jp/news_society/articles/900197180.html",
            "medium": "テレ朝NEWS",
        },
    ],
    "togane": [
        {
            "id": "tvasahi-togane-rain",
            "occurred_at": "2026-08-14T01:17:00+09:00",
            "title": "東金市で記録的短時間大雨　気象庁",
            "summary": "テレ朝NEWSのまとめは、東金市付近で1時間に約100ミリと伝え、レベル5土砂災害特別警報の対象にも触れている。",
            "url": "https://news.tv-asahi.co.jp/news_society/articles/900197093.html",
            "medium": "テレ朝NEWS",
        },
    ],
    "kujukuri": [
        {
            "id": "tvasahi-kujukuri-rain",
            "occurred_at": "2026-08-14T01:07:00+09:00",
            "title": "九十九里町で記録的短時間大雨　気象庁",
            "summary": "テレ朝NEWSのまとめは、九十九里町付近で1時間に約120ミリ、レベル5大雨特別警報を伝えている。",
            "url": "https://news.tv-asahi.co.jp/news_society/articles/900197093.html",
            "medium": "テレ朝NEWS",
        },
    ],
    "sammu": [
        {
            "id": "tvasahi-sammu-rain",
            "occurred_at": "2026-08-14T00:37:00+09:00",
            "title": "山武市で記録的短時間大雨　レベル5大雨",
            "summary": "テレ朝NEWSのまとめは、山武市付近の猛烈な雨とレベル5大雨特別警報を伝えている。",
            "url": "https://news.tv-asahi.co.jp/news_society/articles/900197093.html",
            "medium": "テレ朝NEWS",
        },
    ],
    "yachimata": [
        {
            "id": "tvasahi-yachimata",
            "occurred_at": "2026-08-14T00:10:00+09:00",
            "title": "八街市で記録的短時間大雨　レベル5土砂",
            "summary": "テレ朝NEWSのまとめは、八街市付近の猛烈な雨とレベル5土砂災害特別警報を伝えている。",
            "url": "https://news.tv-asahi.co.jp/news_society/articles/900197093.html",
            "medium": "テレ朝NEWS",
        },
    ],
    "ichihara": [
        {
            "id": "nikkei-ichihara",
            "occurred_at": "2026-08-13T22:00:00+09:00",
            "title": "市原市で水路に流されたとの通報（日経）",
            "summary": "日本経済新聞は市原市で「水路で人が流されて見えなくなった」との通報があったと報じた。続報は公式。",
            "url": "https://www.nikkei.com/article/DGXZQOUD137E20T10C26A8000000/",
            "medium": "日本経済新聞",
        },
    ],
    "narita": [
        {
            "id": "sponichi-narita",
            "occurred_at": "2026-08-15T05:30:00+09:00",
            "title": "成田空港で約7000人が足止め",
            "summary": "鉄道・バス運休で旅客ターミナルに滞留したと複数社が報じている。数値は速報。",
            "url": "https://www.sponichi.co.jp/society/news/2026/08/15/kiji/20260815s00042000050000c.html",
            "medium": "スポーツニッポン",
        },
        {
            "id": "tbs-narita",
            "occurred_at": "2026-08-15T05:30:00+09:00",
            "title": "成田空港では約7000人が一夜明かす（TBS）",
            "summary": "TBS NEWS DIGの県内まとめ。空港アクセスの運休が背景。",
            "url": "https://newsdig.tbs.co.jp/articles/-/2873319",
            "medium": "TBS NEWS DIG",
        },
    ],
    "tateyama": [
        {
            "id": "nikkei-tateyama-rain",
            "occurred_at": "2026-08-13T19:30:00+09:00",
            "title": "館山市で3時間降水量が観測史上最大との報道（日経）",
            "summary": "日本経済新聞は館山市の3時間降水量183ミリが観測史上最大だったと伝えている。",
            "url": "https://www.nikkei.com/article/DGXZQOUD137E20T10C26A8000000/",
            "medium": "日本経済新聞",
        },
    ],
}

# レベル5対象（報道リスト）。県全体まとめを「この市町も対象に含まれる」として載せる。
L5 = {
    "chiba", "ichikawa", "funabashi", "matsudo", "mobara", "sakura", "togane",
    "narashino", "kashiwa", "ichihara", "yachiyo", "abiko", "kamagaya",
    "yotsukaido", "yachimata", "inzai", "shiroi", "sammu", "oamishirasato",
    "kujukuri", "shirako", "nagara",
}


def tag(item: dict, source_type: str = "news") -> dict:
    return {
        "id": item["id"],
        "occurred_at": item["occurred_at"],
        "title": item["title"],
        "summary": item["summary"],
        "source_url": item["url"],
        "source_type": source_type,
        "medium": item["medium"],
    }


def main() -> None:
    by_slug: dict[str, list[dict]] = {}
    for slug, items in LOCAL.items():
        by_slug.setdefault(slug, [])
        for it in items:
            by_slug[slug].append(tag(it))
    payload = {
        "fetched_at": "2026-08-15T21:00:00+09:00",
        "method": "人手で各社公式HTMLとYahoo!ニュース記事を検索し、見出し・URL・1文要約のみ収録。RSSの再配信はしない。",
        "search": {
            "yahoo": "https://news.search.yahoo.co.jp/search?ei=UTF-8&p={q}",
            "nhk_chiba": "https://news.web.nhk/newsweb/area/120",
        },
        "county": [tag(it) for it in COUNTY],
        "l5_slugs": sorted(L5),
        "by_slug": by_slug,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote", OUT, "local slugs", len(by_slug), "county", len(COUNTY))


if __name__ == "__main__":
    main()
