# -*- coding: utf-8 -*-
"""初回の手動収集結果を site/data/collection.json に書き出す。全文転載しない。"""
import json
from pathlib import Path

FETCHED = "2026-08-14T21:20:00+09:00"
PORTAL = "https://www.bousai.pref.chiba.lg.jp/"
PORTAL_DOCS = "https://www.bousai.pref.chiba.lg.jp/PUB_VF_Detail_Docs"
PREF_HQ = "https://www.pref.chiba.lg.jp/bousai/bousai/r8-0813ooame.html"
RELIEF = "https://www.pref.chiba.lg.jp/bousaik/press/2026/saigaikyujoho-r813v3.html"
FDMA8 = "https://www.fdma.go.jp/disaster/info/items/20260813ooame8.pdf"
FDMA = "https://www.fdma.go.jp/disaster/info/"
WNI_L5 = "https://weathernews.jp/news/202608/130321/"
WNI_MECH = "https://weathernews.jp/news/202608/140101/"
NIKKEI = "https://www.nikkei.com/article/DGXZQOUD137E20T10C26A8000000/"
JMA = "https://www.jma.go.jp/bosai/warning/#area_type=offices&area_code=120000"
CAO = "https://www.bousai.go.jp/taisaku/hisaisyagyousei/"
SAMMU_L5 = "https://www.city.sammu.lg.jp/bousai-syobo/bousai-kikinogashi/page008716.html"

L5_RAIN = [
    "chiba", "ichikawa", "funabashi", "matsudo", "mobara", "sakura", "togane",
    "narashino", "kashiwa", "ichihara", "yachiyo", "abiko", "kamagaya",
    "yotsukaido", "yachimata", "inzai", "shiroi", "sammu", "oamishirasato",
    "kujukuri", "shirako", "nagara",
]
L5_LANDSLIDE = ["chiba", "mobara", "togane", "ichihara", "yachimata", "oamishirasato"]

# 県第3報。千葉市は直接実施。
RELIEF_APPLIED = [
    "ichikawa", "funabashi", "tateyama", "matsudo", "mobara", "sakura", "togane",
    "narashino", "kashiwa", "ichihara", "yachiyo", "abiko", "kamagaya",
    "yotsukaido", "yachimata", "inzai", "shiroi", "oamishirasato", "shirako",
    "nagara", "tomisato", "sammu", "shisui", "kujukuri",
]
RELIEF_CHIBA_DIRECT = ["chiba"]

# 県防災ポータル 避難情報（8月13–14日の今回災害に限る）
EVAC = {
    "chiba": ("指示継続", "08/14 10:41", "避難指示（警戒レベル4）"),
    "ichihara": ("解除", "08/14 16:48", "避難情報"),
    "narita": ("解除", "08/14 05:37", "避難情報"),
    "sakura": ("解除", "08/14 11:23", "避難情報"),
    "yotsukaido": ("解除", "08/14 11:57", "避難情報"),
    "yachimata": ("解除", "08/14 12:39", "避難情報"),
    "inzai": ("解除", "08/14 17:10", "避難情報"),
    "shiroi": ("解除", "08/14 05:32", "避難情報"),
    "tomisato": ("解除", "08/14 06:19", "避難情報"),
    "shisui": ("解除", "08/14 09:19", "避難情報"),
    "sakae": ("解除", "08/14 08:30", "避難情報"),
    "ichikawa": ("解除", "08/14 05:36", "避難情報"),
    "funabashi": ("解除", "08/14 06:18", "避難情報"),
    "matsudo": ("解除", "08/14 08:12", "避難情報"),
    "narashino": ("解除", "08/14 06:12", "避難情報"),
    "kashiwa": ("解除", "08/14 05:39", "避難情報"),
    "yachiyo": ("解除", "08/14 11:01", "避難情報"),
    "abiko": ("解除", "08/14 09:41", "避難情報"),
    "kamagaya": ("解除", "08/14 07:47", "避難情報"),
    "mobara": ("解除", "08/14 15:01", "避難情報"),
    "togane": ("解除", "08/14 11:21", "避難情報"),
    "sammu": ("解除", "08/14 06:28", "避難情報"),
    "oamishirasato": ("解除", "08/14 15:35", "避難情報"),
    "kujukuri": ("解除", "08/14 05:41", "避難情報"),
    "shirako": ("解除", "08/14 05:25", "避難情報"),
    "nagara": ("解除", "08/14 05:20", "避難情報"),
    "kisarazu": ("解除", "08/14 05:49", "避難情報"),
    "kimitsu": ("解除", "08/14 06:34", "避難情報"),
    "futtsu": ("解除", "08/14 05:43", "避難情報"),
    "sodegaura": ("解除", "08/14 11:00", "避難情報"),
    "tateyama": ("解除", "08/14 05:20", "避難情報"),
    "katsuura": ("解除", "08/14 05:21", "避難情報"),
    "minamiboso": ("解除", "08/14 05:59", "避難情報"),
    "isumi": ("解除", "08/14 05:56", "避難情報"),
    "otaki": ("解除", "08/14 05:49", "避難情報"),
    "kyonan": ("解除", "08/14 05:28", "避難情報"),
}

SHELTER = {
    "chiba": ("開設", "08/14 19:35"),
    "ichihara": ("開設", "08/14 19:09"),
    "narita": ("開設", "08/14 18:48"),
    "sakura": ("開設", "08/14 16:25"),
    "yotsukaido": ("開設", "08/14 19:19"),
    "yachimata": ("閉鎖", "08/14 14:14"),
    "inzai": ("閉鎖", "08/14 10:51"),
    "shiroi": ("閉鎖", "08/14 08:02"),
    "tomisato": ("閉鎖", "08/14 07:03"),
    "shisui": ("閉鎖", "08/14 15:10"),
    "sakae": ("閉鎖", "08/14 08:35"),
    "ichikawa": ("閉鎖", "08/14 05:40"),
    "funabashi": ("閉鎖", "08/14 09:38"),
    "matsudo": ("開設", "08/13 18:22"),
    "noda": ("閉鎖", "08/14 08:26"),
    "narashino": ("閉鎖", "08/14 09:25"),
    "kashiwa": ("閉鎖", "08/14 16:46"),
    "nagareyama": ("閉鎖", "08/14 09:11"),
    "yachiyo": ("開設", "08/14 16:13"),
    "abiko": ("閉鎖", "08/14 12:18"),
    "kamagaya": ("閉鎖", "08/14 11:13"),
    "sosa": ("閉鎖", "08/14 05:50"),
    "mobara": ("開設", "08/14 19:35"),
    "togane": ("開設", "08/14 11:47"),
    "sammu": ("閉鎖", "08/14 06:29"),
    "oamishirasato": ("開設", "08/14 17:42"),
    "kujukuri": ("閉鎖", "08/14 14:41"),
    "yokoshibahikari": ("閉鎖", "08/14 06:10"),
    "shirako": ("閉鎖", "08/14 06:42"),
    "nagara": ("閉鎖", "08/14 11:00"),
    "kisarazu": ("閉鎖", "08/14 05:37"),
    "kimitsu": ("閉鎖", "08/14 08:18"),
    "futtsu": ("閉鎖", "08/14 06:57"),
    "sodegaura": ("閉鎖", "08/14 13:19"),
    "tateyama": ("閉鎖", "08/14 06:08"),
    "kamogawa": ("閉鎖", "08/14 08:16"),
    "minamiboso": ("閉鎖", "08/14 06:08"),
    "otaki": ("閉鎖", "08/14 05:47"),
    "kyonan": ("閉鎖", "08/14 05:31"),
}

NAMES = {
    "chiba": "千葉市", "ichikawa": "市川市", "funabashi": "船橋市", "matsudo": "松戸市",
    "mobara": "茂原市", "sakura": "佐倉市", "togane": "東金市", "narashino": "習志野市",
    "kashiwa": "柏市", "ichihara": "市原市", "yachiyo": "八千代市", "abiko": "我孫子市",
    "kamagaya": "鎌ケ谷市", "yotsukaido": "四街道市", "yachimata": "八街市", "inzai": "印西市",
    "shiroi": "白井市", "sammu": "山武市", "oamishirasato": "大網白里市", "kujukuri": "九十九里町",
    "shirako": "白子町", "nagara": "長柄町", "nagareyama": "流山市", "choshi": "銚子市",
    "tateyama": "館山市", "kisarazu": "木更津市", "noda": "野田市", "narita": "成田市",
    "asahi": "旭市", "katsuura": "勝浦市", "kamogawa": "鴨川市", "kimitsu": "君津市",
    "futtsu": "富津市", "urayasu": "浦安市", "sodegaura": "袖ケ浦市", "tomisato": "富里市",
    "minamiboso": "南房総市", "sosa": "匝瑳市", "katori": "香取市", "isumi": "いすみ市",
    "shisui": "酒々井町", "sakae": "栄町", "kozaki": "神崎町", "tako": "多古町",
    "tonosho": "東庄町", "shibayama": "芝山町", "yokoshibahikari": "横芝光町",
    "ichinomiya": "一宮町", "mutsuzawa": "睦沢町", "chosei": "長生村", "chonan": "長南町",
    "otaki": "大多喜町", "onjuku": "御宿町", "kyonan": "鋸南町",
}

items = []


def add(item):
    items.append(item)


add({
    "id": "pref-hq",
    "slug": "prefecture",
    "occurred_at": "2026-08-13T19:30:00+09:00",
    "kind": "hq",
    "title": "千葉県が災害対策本部を設置",
    "summary": "県は令和8年8月13日からの大雨に伴う対応ページを公開。第1〜3回災害対策本部会議資料と、帰宅困難者輸送等のための自衛隊災害派遣要請を案内している。",
    "source_url": PREF_HQ,
    "source_type": "admin",
    "medium": "千葉県",
})
add({
    "id": "pref-portal-now",
    "slug": "prefecture",
    "occurred_at": "2026-08-14T14:36:00+09:00",
    "kind": "warning",
    "title": "県防災ポータル：14日も大雨と土砂災害に警戒",
    "summary": "13日の前例がないほどの大雨で甚大な被害。地盤が水を含み少雨でも土砂災害の危険があるとして、不要不急の外出を控えるよう呼びかけている。冠水した道路への進入も避けるよう注意がある。",
    "source_url": PORTAL,
    "source_type": "admin",
    "medium": "千葉県防災ポータル",
})
add({
    "id": "pref-damage-docs",
    "slug": "prefecture",
    "occurred_at": "2026-08-14T18:21:00+09:00",
    "kind": "damage",
    "title": "県の被害情報PDF（第5報修正まで）",
    "summary": "県防災ポータルの被害集計に、令和8年8月13日大雨の被害情報第1報〜第5報（修正）が掲載されている。数値は公式PDFで確認すること。",
    "source_url": PORTAL_DOCS,
    "source_type": "admin",
    "medium": "千葉県防災ポータル",
})
add({
    "id": "pref-relief",
    "slug": "prefecture",
    "occurred_at": "2026-08-14T00:00:00+09:00",
    "kind": "support",
    "title": "災害救助法を24市町に適用（千葉市は直接実施）",
    "summary": "適用日は令和8年8月13日。第3報時点の追加は富里市・山武市・酒々井町・九十九里町。効果は県が行う救助の費用負担。避難所設置等が措置として挙げられている。",
    "source_url": RELIEF,
    "source_type": "admin",
    "medium": "千葉県",
})
add({
    "id": "fdma-8",
    "slug": "prefecture",
    "occurred_at": "2026-08-14T17:00:00+09:00",
    "kind": "damage",
    "title": "消防庁「令和8年8月千葉豪雨」第8報",
    "summary": "速報であり数値は変わりうる。人的被害の内訳として市川市1人・佐倉市2人・八千代市1人が記載されている。県は13日19時30分に災害対策本部を設置。",
    "source_url": FDMA8,
    "source_type": "admin",
    "medium": "総務省消防庁",
})
add({
    "id": "wni-l5",
    "slug": "prefecture",
    "occurred_at": "2026-08-13T19:30:00+09:00",
    "kind": "warning",
    "title": "レベル5大雨特別警報の対象22市町（報道）",
    "summary": "ウェザーニュースは対象を千葉市・市川市・船橋市・松戸市・茂原市・佐倉市・東金市・習志野市・柏市・市原市・八千代市・我孫子市・鎌ケ谷市・四街道市・八街市・印西市・白井市・山武市・大網白里市・九十九里町・白子町・長柄町と伝え、土砂災害特別警報は6市とした。",
    "source_url": WNI_L5,
    "source_type": "news",
    "medium": "ウェザーニュース",
})
add({
    "id": "wni-switch",
    "slug": "prefecture",
    "occurred_at": "2026-08-14T05:15:00+09:00",
    "kind": "warning",
    "title": "特別警報は14日明け方にレベル4へ切替（報道）",
    "summary": "ウェザーニュースは、広範囲のレベル5特別警報が14日明け方にレベル4危険警報等へ切り替わったと伝えている。地盤が緩んでおり少ない雨でも災害につながるおそれがあるとしている。",
    "source_url": WNI_MECH,
    "source_type": "news",
    "medium": "ウェザーニュース",
})
add({
    "id": "nikkei-l5",
    "slug": "prefecture",
    "occurred_at": "2026-08-13T19:30:00+09:00",
    "kind": "warning",
    "title": "運用見直し後、大雨・土砂のレベル5は初めて（報道）",
    "summary": "日本経済新聞は、気象庁が県内22市町にレベル5大雨特別警報を発表し、うち6市に土砂災害特別警報も出たと報じた。見出しとリンクのみ掲載する。",
    "source_url": NIKKEI,
    "source_type": "news",
    "medium": "日本経済新聞",
})

# 消防庁が市町村名を出した人的被害（速報）
for slug, n, note in [
    ("ichikawa", "1人", "市川市"),
    ("sakura", "2人", "佐倉市"),
    ("yachiyo", "1人", "八千代市"),
]:
    add({
        "id": f"fdma-casualty-{slug}",
        "slug": slug,
        "occurred_at": "2026-08-14T17:00:00+09:00",
        "kind": "damage",
        "title": f"消防庁第8報：{note}の死者{n}（速報）",
        "summary": "総務省消防庁の第8報に記載。速報であり数値は今後変わることがある。詳細は公式PDFと各市の発表を確認すること。",
        "source_url": FDMA8,
        "source_type": "admin",
        "medium": "総務省消防庁",
    })

add({
    "id": "sammu-jma-relay",
    "slug": "sammu",
    "occurred_at": "2026-08-14T00:30:00+09:00",
    "kind": "warning",
    "title": "山武市が気象警報の発表を公式に転載",
    "summary": "山武市公式サイトが、8月14日0時30分配信の千葉県気象警報・注意報を掲載している。詳細は気象庁の発表を確認するよう案内している。",
    "source_url": SAMMU_L5,
    "source_type": "admin",
    "medium": "山武市",
})

for slug in L5_RAIN:
    add({
        "id": f"l5-rain-{slug}",
        "slug": slug,
        "occurred_at": "2026-08-13T19:30:00+09:00",
        "kind": "warning",
        "title": "レベル5大雨特別警報の対象に含まれた（報道による対象リスト）",
        "summary": "ウェザーニュースが伝えた気象庁発表の二次細分区域。特別警報は14日明け方に切り替えられたと後報がある。最新の警報は気象庁で確認すること。",
        "source_url": WNI_L5,
        "source_type": "news",
        "medium": "ウェザーニュース",
    })

for slug in L5_LANDSLIDE:
    add({
        "id": f"l5-landslide-{slug}",
        "slug": slug,
        "occurred_at": "2026-08-13T21:55:00+09:00",
        "kind": "warning",
        "title": "レベル5土砂災害特別警報の対象に含まれた（報道による対象リスト）",
        "summary": "ウェザーニュースは千葉市・茂原市・東金市・市原市・八街市・大網白里市を対象とした。地盤が緩んでいるため、解除後も斜面や渓流に近づかないこと。",
        "source_url": WNI_L5,
        "source_type": "news",
        "medium": "ウェザーニュース",
    })

for slug in RELIEF_APPLIED:
    add({
        "id": f"relief-{slug}",
        "slug": slug,
        "occurred_at": "2026-08-13T00:00:00+09:00",
        "kind": "support",
        "title": "災害救助法の適用市町に含まれる（県第3報）",
        "summary": "適用日は令和8年8月13日。県が行う救助の費用を国と県が負担する。罹災証明や応急修理などの窓口・受付開始は各市町の公式発表を確認すること。",
        "source_url": RELIEF,
        "source_type": "admin",
        "medium": "千葉県",
    })

for slug in RELIEF_CHIBA_DIRECT:
    add({
        "id": f"relief-{slug}",
        "slug": slug,
        "occurred_at": "2026-08-13T00:00:00+09:00",
        "kind": "support",
        "title": "千葉市は災害救助を直接実施（県第3報）",
        "summary": "県の適用市町一覧では千葉市を除き、千葉市は直接災害救助を実施するとされている。申請先は市の公式窓口。",
        "source_url": RELIEF,
        "source_type": "admin",
        "medium": "千葉県",
    })

for slug, (status, when, label) in EVAC.items():
    name = NAMES[slug]
    if status == "指示継続":
        title = f"県ポータル：{name}は避難指示が継続（{when}発表）"
        summary = f"{label}が継続と表示されている。対象区域の最新は県防災ポータルと市公式で確認すること。"
    else:
        title = f"県ポータル：{name}の避難情報は解除（{when}発表）"
        summary = "解除後も浸水・土砂の現場や増水した水路には近づかないこと。再発令の有無は公式で確認すること。"
    add({
        "id": f"evac-{slug}",
        "slug": slug,
        "occurred_at": f"2026-{when.replace(' ', 'T').replace('/', '-')}:00+09:00",
        "kind": "evacuation",
        "title": title,
        "summary": summary,
        "source_url": PORTAL,
        "source_type": "admin",
        "medium": "千葉県防災ポータル",
    })

for slug, (status, when) in SHELTER.items():
    name = NAMES[slug]
    title = f"県ポータル：{name}の避難所は{status}（{when}発表）"
    summary = (
        "開設中の施設名・対象は県ポータルと市公式の避難所一覧で確認すること。"
        if status == "開設"
        else "閉鎖と表示されている。再開や福祉避難所の扱いは市公式で確認すること。"
    )
    add({
        "id": f"shelter-{slug}",
        "slug": slug,
        "occurred_at": f"2026-{when.replace(' ', 'T').replace('/', '-')}:00+09:00",
        "kind": "shelter",
        "title": title,
        "summary": summary,
        "source_url": PORTAL,
        "source_type": "admin",
        "medium": "千葉県防災ポータル",
    })

add({
    "id": "nagareyama-not-l5",
    "slug": "nagareyama",
    "occurred_at": "2026-08-13T19:30:00+09:00",
    "kind": "warning",
    "title": "流山市はレベル5大雨特別警報の対象リストに含まれていない（報道）",
    "summary": "ウェザーニュースが伝えた22市町の対象に流山市は入っていない。県第3報の災害救助法適用市町にも含まれていない。避難所は県ポータル上14日9時11分発表で閉鎖。最新は市公式で確認すること。",
    "source_url": WNI_L5,
    "source_type": "news",
    "medium": "ウェザーニュース",
})

snapshots = {}
for slug, name in NAMES.items():
    ev = EVAC.get(slug)
    sh = SHELTER.get(slug)
    if slug in RELIEF_CHIBA_DIRECT:
        relief = "chiba_direct"
    elif slug in RELIEF_APPLIED:
        relief = "applied"
    else:
        relief = "none"
    snapshots[slug] = {
        "l5_rain": slug in L5_RAIN,
        "l5_landslide": slug in L5_LANDSLIDE,
        "disaster_relief": relief,
        "evacuation": None if not ev else {"status": ev[0], "at": ev[1], "label": ev[2]},
        "shelter": None if not sh else {"status": sh[0], "at": sh[1]},
    }

out = {
    "fetched_at": FETCHED,
    "method": "手動。許可リストの行政・報道から見出しと短い要約のみ。",
    "links": {
        "portal": PORTAL,
        "pref": PREF_HQ,
        "relief": RELIEF,
        "fdma": FDMA,
        "fdma8": FDMA8,
        "jma": JMA,
        "cao": CAO,
    },
    "snapshots": snapshots,
    "items": items,
}

path = Path(__file__).resolve().parents[1] / "site" / "data" / "collection.json"
path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {path} items={len(items)} snapshots={len(snapshots)}")
