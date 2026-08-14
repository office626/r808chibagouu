# 収集許可リスト（初版）

確定事項:

- **実行時刻:** 毎日 6:00（日本時間）。GitHub Actions の cron は `0 21 * * *`（UTC）
- **取り方:** 見出し・短い要約・元 URL のみ。全文転載しない
- **キーワード（報道・全国フィード）:** `千葉` を含み、かつ `豪雨|大雨|浸水|避難|特別警報|警戒レベル|罹災|災害救助|土砂` のいずれかを含むものに絞る
- **衝突:** 制度・受付状態は行政を優先する

Yahoo!ニュース RSS と NHK 公式 RSS は、個人利用・再配信禁止の利用条件があるため、**本サイトの自動収集には使わない。** 報道は各社の公式サイトを入口にする。

シートへ移すときは、本ファイルを正とし、[運用スプレッドシート](https://docs.google.com/spreadsheets/d/1_dHZHMLvTx6iTCzwvbw6U9cTHjTIH_6RlEob81Ng7KM/edit?usp=sharing) に反映する。シートはリンクを知っている人が閲覧可。URL は公開前に到達確認する。

---

## 1. 行政（国・県）

| ID | 媒体 | 区分 | 入口 URL | 取得 | 備考 |
|----|------|------|----------|------|------|
| A-JMA-EXTRA | 気象庁 | 行政 | https://www.data.jma.go.jp/developer/xml/feed/extra_l.xml | Atom（長期・随時。警報等） | 日次ジョブ向き。千葉県（コード 120000 付近）に絞る |
| A-JMA-WARN | 気象庁 警報・注意報 | 行政 | https://www.jma.go.jp/bosai/warning/#area_type=offices&area_code=120000 | HTML入口 | 県民への参照用。XML と併用 |
| A-FDMA | 総務省消防庁 災害情報 | 行政 | https://www.fdma.go.jp/disaster/info/index.xml | RSS | 公式 RSS |
| A-FDMA-TOP | 総務省消防庁 新着 | 行政 | https://www.fdma.go.jp/index.xml | RSS | 災害以外が混ざるのでキーワードで絞る |
| A-CAO | 内閣府 防災 | 行政 | https://www.bousai.go.jp/ | HTML入口 | 被災者支援制度の入口 |
| A-CAO-HISAI | 内閣府 被災者支援 | 行政 | https://www.bousai.go.jp/taisaku/hisaisyagyousei/ | HTML入口 | 制度ナビの国レイヤー |
| A-CHIBA-PORTAL | 千葉県防災ポータル | 行政 | https://www.bousai.pref.chiba.lg.jp/ | HTML入口 | 避難情報・本部設置の集約。RSSなし |
| A-CHIBA-PREF | 千葉県庁 | 行政 | https://www.pref.chiba.lg.jp/ | HTML新着 | 災害・支援の発表 |
| A-RIVER | 国土交通省 川の防災情報 | 行政 | https://www.river.go.jp/ | HTML入口 | 水位。ログのライフライン種別に使う |

---

## 2. 行政（初日ログ対象の市町村）

個別 RSS がない自治体がほとんどなので、公式ドメインの防災・新着を入口にする。ジョブは当該ドメイン内の新着見出しと URL を取る。

| ID | 市町村 | 公式サイト | 防災・災害の入口（判明分） |
|----|--------|------------|----------------------------|
| M-CHIBA | 千葉市 | https://www.city.chiba.jp/ | https://city-chiba.my.site.com/ |
| M-ICHIKAWA | 市川市 | https://www.city.ichikawa.lg.jp/ | https://www.city.ichikawa.lg.jp/page/4999.html |
| M-FUNABASHI | 船橋市 | https://www.city.funabashi.lg.jp/ | 公式の防災・新着 |
| M-MATSUDO | 松戸市 | https://www.city.matsudo.chiba.jp/ | 公式の防災・新着 |
| M-MOBARA | 茂原市 | https://www.city.mobara.chiba.jp/ | 公式の防災・新着 |
| M-SAKURA | 佐倉市 | https://www.city.sakura.lg.jp/ | 公式の防災・新着 |
| M-TOGANE | 東金市 | https://www.city.togane.lg.jp/ | 公式の防災・新着 |
| M-NARASHINO | 習志野市 | https://www.city.narashino.lg.jp/ | 公式の防災・新着 |
| M-KASHIWA | 柏市 | https://www.city.kashiwa.lg.jp/ | 公式の防災・新着 |
| M-ICHIHARA | 市原市 | https://www.city.ichihara.chiba.jp/ | 公式の防災・新着 |
| M-YACHIYO | 八千代市 | https://www.city.yachiyo.lg.jp/ | 公式の防災・新着 |
| M-ABIKO | 我孫子市 | https://www.city.abiko.chiba.jp/ | 公式の防災・新着 |
| M-KAMAGAYA | 鎌ケ谷市 | https://www.city.kamagaya.chiba.jp/ | 公式の防災・新着 |
| M-YOTSUKAIDO | 四街道市 | https://www.city.yotsukaido.chiba.jp/ | 公式の防災・新着 |
| M-YACHIMATA | 八街市 | https://www.city.yachimata.lg.jp/ | 公式の防災・新着 |
| M-INZAI | 印西市 | https://www.city.inzai.lg.jp/ | 公式の防災・新着 |
| M-SHIROI | 白井市 | https://www.city.shiroi.lg.jp/ | 公式の防災・新着 |
| M-SAMMU | 山武市 | https://www.city.sammu.lg.jp/ | 公式の防災・新着 |
| M-OAMISHIRASATO | 大網白里市 | https://www.city.oamishirasato.lg.jp/ | 公式の防災・新着 |
| M-KUJUKURI | 九十九里町 | https://www.town.kujukuri.chiba.jp/ | 公式の防災・新着 |
| M-SHIRAKO | 白子町 | https://www.town.shirako.lg.jp/ | 公式の防災・新着 |
| M-NAGARA | 長柄町 | https://www.town.nagara.chiba.jp/ | 公式の防災・新着 |
| M-NAGAREYAMA | 流山市 | https://www.city.nagareyama.chiba.jp/ | https://www.city.nagareyama.chiba.jp/life/1003604/index.html |

※ レベル5対象リストは気象庁確定で増減する。増えた市町村は同じ型で行を足す。

---

## 3. 報道（公式サイト。RSS 再配信は使わない）

| ID | 媒体 | 区分 | 入口 URL | 取得 | 備考 |
|----|------|------|----------|------|------|
| N-CHIBANIPPO | 千葉日報 | 報道 | https://www.chibanippo.co.jp/ | HTML新着 | 県内地方紙 |
| N-CHIBATOPI | ちばとぴ（千葉日報社） | 報道 | https://www.chibatopi.jp/ | HTML新着 | 到達しない場合は行を止める |
| N-CHIBATV | チバテレ | 報道 | https://www.chiba-tv.com/ | HTML新着 | |
| N-WNI | ウェザーニュース | 報道 | https://weathernews.jp/s/topics/ | HTML新着 | 警報・被害の速報。キーワードで千葉に絞る |
| N-NIKKEI | 日本経済新聞 | 報道 | https://www.nikkei.com/ | HTML新着（千葉・災害） | 有料記事は見出しとリンクのみ |
| N-NHK-CHIBA | NHK 千葉のニュース | 報道 | https://news.web.nhk/newsweb/area/120 | HTML入口 | **公式 RSS は使わない**（再配信禁止）。ページへのリンクと見出しに限定 |
| N-ASAHI | 朝日新聞デジタル | 報道 | https://www.asahi.com/ | HTML新着（千葉） | キーワードで絞る |
| N-YOMIURI | 読売新聞オンライン | 報道 | https://www.yomiuri.co.jp/ | HTML新着（千葉） | キーワードで絞る |
| N-MAINICHI | 毎日新聞 | 報道 | https://mainichi.jp/ | HTML新着（千葉） | キーワードで絞る |
| N-KYOTO | 共同通信 | 報道 | https://www.kyodo.co.jp/ | HTML新着 | キーワードで絞る |
| N-BONICHI | 房日新聞 | 報道 | https://www.bonichi.com/ | HTML新着 | 房総。到達しない場合は行を止める |

### 使わないもの（初版）

| 媒体 | 理由 |
|------|------|
| Yahoo!ニュース RSS（媒体社別・カテゴリ別） | サイトやアプリへの利用・再配信が利用条件で禁止 |
| NHK 公式 RSS（cat0.xml 等） | 個人利用のみ、プログラムによる再提供が禁止 |
| X / Facebook の個人投稿 | 伝聞と著作権。許可リスト外 |
| まとめサイト・転載ブログ | 一次情報ではない |

---

## 4. ジョブの動き（初版）

1. 毎日 6:00 JST に起動する
2. 上表のうち `取得` が Atom/RSS のものを読む
3. HTML入口は、許可ドメインの新着一覧から見出しと URL を取る（本文は取らない）
4. 報道・全国行政はキーワードで千葉の今回災害に絞る
5. 市町村公式は、その自治体ページに紐づける
6. 同一 URL は追加しない
7. 成功したらサイトを再生成する。失敗したら前回データを残し、最終取得日時は更新しない

実装時は `robots.txt` と各サイトの利用条件を再確認する。拒否された行はシートで止める。
