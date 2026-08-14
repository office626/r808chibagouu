# -*- coding: utf-8 -*-
"""市町村公式の支援策リンク（罹災証明など）。全文転載しない。"""
import json
from pathlib import Path

NOTE = (
    "各市町村公式の申請案内へのリンク。今回の大雨専用ページでない場合もある。"
    "受付の有無・対象は必ず公式で確認すること。"
)

# kind: risai=罹災証明, support=支援まとめ, home=公式トップ（個別ページ未確認）
PAGES = {
    "chiba": [
        ("risai", "罹災証明書・被災証明書の交付", "https://www.city.chiba.jp/sogoseisaku/kikikanri/kikikanri/sinnrisaishomei.html"),
        ("support", "被災者生活再建支援金（国制度）", "https://www.city.chiba.jp/hokenfukushi/kenkofukushi/chiikifukushi/hisaisha-shien_gov.html"),
        ("support", "被災者生活再建支援金（千葉県制度）", "https://www.city.chiba.jp/hokenfukushi/kenkofukushi/chiikifukushi/hisaisha-shien_chiba-pref.html"),
    ],
    "ichikawa": [
        ("risai", "罹災証明書等の申請（地震等・風水害）", "https://www.city.ichikawa.lg.jp/page/7339.html"),
    ],
    "funabashi": [
        ("support", "自然災害の被害に遭われた市民の方へ（支援制度）", "https://www.city.funabashi.lg.jp/bousai/003/risai/p084061.html"),
        ("risai", "罹災証明書・被災（届出）証明書", "https://www.city.funabashi.lg.jp/bousai/003/risai/p020912.html"),
    ],
    "matsudo": [
        ("risai", "罹災証明書・罹災届出証明書の発行", "https://www.city.matsudo.chiba.jp/kurashi/todokede/shoumeisho/aaa.html"),
    ],
    "mobara": [
        ("risai", "罹災証明書・被災証明書", "https://www.city.mobara.chiba.jp/0000000787.html"),
    ],
    "sakura": [
        ("risai", "罹災証明書・被災証明書の発行", "https://www.city.sakura.lg.jp/soshiki/kikikanrika/112/risai/4872.html"),
    ],
    "togane": [
        ("risai", "罹災証明書・被災届出証明書", "https://www.city.togane.chiba.jp/0000001068.html"),
    ],
    "narashino": [
        ("risai", "り災証明書、被災証明書の発行", "https://www.city.narashino.lg.jp/soshiki/kikikanri/gyomu/bosaibohan/hisaisyasien/risaisyoumei_hisaisyoumei.html"),
    ],
    "kashiwa": [
        ("risai", "罹災証明書及び被災届出証明書の申請・発行", "https://www.city.kashiwa.lg.jp/shisanzei/shiseijoho/forms/kojin/risai.html"),
    ],
    "ichihara": [
        ("risai", "「罹災証明書」「被災証明書」をとりたい（8月13日大雨の受付案内あり）", "https://www.city.ichihara.chiba.jp/article?articleId=60237e61ece4651c88c190e7"),
    ],
    "yachiyo": [
        ("risai", "罹災証明書・被害届出証明書の発行", "https://www.city.yachiyo.lg.jp/soshiki/11/2167.html"),
    ],
    "abiko": [
        ("risai", "り災証明書・被災証明書・り災届出証明書", "https://www.city.abiko.chiba.jp/anshin/bousai/hisaichifukko/risaishomeisho.html"),
    ],
    "kamagaya": [
        ("risai", "罹災証明書等の交付", "https://www.city.kamagaya.chiba.jp/anzen_anshin/bousai/hisaishoumeisho.html"),
    ],
    "yotsukaido": [
        ("risai", "罹災証明書及び罹災届出証明書の発行", "https://www.city.yotsukaido.chiba.jp/kurashi/bohan/bosai/saigai-hassei/risaishomei.html"),
    ],
    "yachimata": [
        ("risai", "り災証明書及び被災証明書の発行", "https://www.city.yachimata.lg.jp/soshiki/8/44368.html"),
    ],
    "inzai": [
        ("risai", "り災証明書の交付", "https://www.city.inzai.lg.jp/bousaiportal/0000008733.html"),
    ],
    "shiroi": [
        ("risai", "罹災証明書等の交付", "https://www.city.shiroi.chiba.jp/kurashi/bosai/b02/1472018650409.html"),
    ],
    "sammu": [
        ("risai", "罹災証明書の発行", "https://www.city.sammu.lg.jp/bousai-syobo/bousai/taifu13/page000827.html"),
    ],
    "oamishirasato": [
        ("risai", "罹災証明書・被災証明書", "https://www.city.oamishirasato.lg.jp/0000013209.html"),
    ],
    "kujukuri": [
        ("risai", "罹災証明書・被災証明書", "https://www.town.kujukuri.chiba.jp/0000001345.html"),
    ],
    "shirako": [
        ("risai", "り災証明書の発行", "https://www.town.shirako.lg.jp/0000001936.html"),
    ],
    "nagara": [
        ("risai", "罹災証明書等の発行申請", "https://www.town.nagara.chiba.jp/soshiki/1/12166.html"),
    ],
    "nagareyama": [
        ("risai", "罹災証明書・被災証明書の発行", "https://www.city.nagareyama.chiba.jp/life/1003604/1027795/1023527.html"),
    ],
    "choshi": [
        ("risai", "罹災証明書", "https://www.city.choshi.chiba.jp/kurashi/page040031.html"),
    ],
    "tateyama": [
        ("risai", "り災証明書・被災届出証明書の発行", "https://www.city.tateyama.chiba.jp/zeimu/page100071.html"),
    ],
    "kisarazu": [
        ("risai", "り災証明書・り災届出証明書", "https://www.city.kisarazu.lg.jp/soshiki/somu/kikikanri/1/941.html"),
    ],
    "noda": [
        ("risai", "罹災証明書・罹災届出証明書（地震、風水害等）", "https://www.city.noda.chiba.jp/kurashi/anzen/bousai/1008712.html"),
    ],
    "narita": [
        ("risai", "罹災証明書・罹災届出証明書", "https://www.city.narita.chiba.jp/anshin/page071200_00001.html"),
    ],
    "asahi": [
        ("risai", "罹災（被災）証明書の発行", "https://www.city.asahi.lg.jp/soshiki/6/2620.html"),
    ],
    "katsuura": [
        ("risai", "罹災証明書等の交付", "https://www.city.katsuura.lg.jp/site/bousai/1451.html"),
    ],
    "kamogawa": [
        ("risai", "罹災証明書・被災届出証明書", "https://www.city.kamogawa.lg.jp/site/bousai/7703.html"),
    ],
    "kimitsu": [
        ("risai", "り災証明書等の発行申請", "https://www.city.kimitsu.lg.jp/soshiki/6/1142.html"),
    ],
    "futtsu": [
        ("risai", "り災証明書・被災届出証明書の発行", "https://www.city.futtsu.lg.jp/0000001482.html"),
    ],
    "urayasu": [
        ("risai", "り災証明書・り災届出証明書", "https://www.city.urayasu.lg.jp/todokede/anzen/bousai/1030674/1027478.html"),
    ],
    "sodegaura": [
        ("risai", "罹災証明書及び被災届出証明書の発行", "https://www.city.sodegaura.lg.jp/soshiki/chiiki/risaisyoumeisyo.html"),
    ],
    "tomisato": [
        ("risai", "罹災証明書（罹災届出証明書）の申請方法", "https://www.city.tomisato.lg.jp/0000013819.html"),
    ],
    "minamiboso": [
        ("risai", "罹災証明書等の交付", "https://www.city.minamiboso.chiba.jp/bousai/0000019689.html"),
    ],
    "sosa": [
        ("risai", "罹災証明書、被害届出証明の交付", "https://www.city.sosa.lg.jp/page/page000398.html"),
    ],
    "katori": [
        ("risai", "り災証明書", "https://www.city.katori.lg.jp/download/other/somu001.html"),
    ],
    "shisui": [
        ("risai", "罹災証明書及び被災証明書", "https://www.town.shisui.chiba.jp/docs/2021040900042/"),
    ],
    "sakae": [
        ("risai", "り災証明交付申請書（自然災害）", "https://www.town.sakae.chiba.jp/kurashi/emergency/disaster-about/page004412.html"),
    ],
    "shibayama": [
        ("risai", "罹災証明書の発行", "https://www.town.shibayama.lg.jp/0000001165.html"),
    ],
    "tako": [
        ("risai", "罹災証明書等の申請", "https://www.town.tako.chiba.jp/docs/2020081300026/"),
    ],
    "tonosho": [
        ("risai", "罹災証明書の発行", "https://www.town.tohnosho.chiba.jp/soshiki/chominka/koteishisanzei_kakari/shinseisho_shoshikidownlord/20/6730.html"),
    ],
    "yokoshibahikari": [
        ("risai", "り災・被災証明書の発行", "https://www.town.yokoshibahikari.chiba.jp/soshiki/6/1038.html"),
    ],
    "mutsuzawa": [
        ("risai", "罹災証明書・被災証明書の発行", "https://www.town.mutsuzawa.chiba.jp/kurashi/osirase/risaihisai.html"),
    ],
    "chosei": [
        ("risai", "罹災証明書の発行", "https://www.vill.chosei.chiba.jp/0000000513.html"),
    ],
    "chonan": [
        ("risai", "罹災証明書・被災証明書の発行", "https://www.town.chonan.chiba.jp/osirase/21004/"),
    ],
    "otaki": [
        ("risai", "り災証明書等の交付", "https://www.town.otaki.chiba.jp/kurashi/todoke/1/1075.html"),
    ],
    "onjuku": [
        ("risai", "り災証明書の発行", "https://www.town.onjuku.chiba.jp/sub1/1/34.html"),
    ],
}

KIND_LABEL = {"risai": "罹災証明", "support": "支援策", "home": "公式"}

root = Path(__file__).resolve().parents[1]
munis = json.loads((root / "site" / "data" / "municipalities.json").read_text(encoding="utf-8"))
by_slug = {}
for m in munis:
    slug = m["slug"]
    rows = []
    for kind, title, url in PAGES.get(slug, []):
        rows.append({"kind": kind, "kind_label": KIND_LABEL[kind], "title": title, "url": url})
    if not rows:
        rows.append({
            "kind": "home",
            "kind_label": "公式",
            "title": m["name"] + "公式サイトで罹災証明・支援窓口を検索",
            "url": m["url"],
        })
    by_slug[slug] = rows

out = {"note": NOTE, "by_slug": by_slug}
path = root / "site" / "data" / "supports.json"
path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
found = sum(1 for s, rows in by_slug.items() if rows and rows[0]["kind"] != "home")
print(f"wrote {path} dedicated={found} fallback={len(by_slug) - found}")
