# 令和8年8月千葉豪雨 — CTZC 復興支援ポータル（要件）

CivicTechZenChiba（CTZC）として、令和8年8月千葉豪雨の復興・災害対策のために検討しているポータルサイトの**要件定義**です。実装はまだありません。

検証・添削・協働編集を歓迎します。Issue や Pull Request で指摘してください。

## このリポジトリで見ること

要件の本体は [`docs/input/`](./docs/input/) です。

| ファイル | 内容 |
|----------|------|
| [docs/input/README.md](./docs/input/README.md) | プロジェクト概要 |
| [docs/input/business-requirements.md](./docs/input/business-requirements.md) | ビジネス要件 |
| [docs/input/user-personas.md](./docs/input/user-personas.md) | ターゲットユーザー |
| [docs/input/product-requirements.md](./docs/input/product-requirements.md) | プロダクト要件 |
| [docs/input/user-flows.md](./docs/input/user-flows.md) | ユーザーフロー |
| [docs/input/feature-list.md](./docs/input/feature-list.md) | 機能一覧 |
| [docs/input/mvp-scope.md](./docs/input/mvp-scope.md) | MVP範囲 |
| [docs/input/ui-ux-direction.md](./docs/input/ui-ux-direction.md) | UI/UX方針 |

`docs/prompts/` と `docs/template/` は、要件を引き出すためのプロンプトとテンプレートです。

## プロダクトの骨格（要約）

一つのサイトに二つの入口を持つ。

1. **県民向け** — 市町村ごとの被害状況ログ（過去〜現在）と、いま受けられる支援策
2. **支援者向け** — 有志が集まり、行政情報の収集と伝達拡散を分担する場

先行事例として [シビックテック袖ケ浦の災害支援ナビゲーター](https://civictechsodegaura.org/) を県全域・市町村別に広げる。現地の行政プロセスはシビックテックもばら篠田さんの状況報告を参考にしている。

## 検証してほしいこと

- 県民入口と支援者入口の切り分けは分かりそうか
- 市町村ページのテンプレート（ログ／いまの支援策／生活再建の段取り）に足りない欄はないか
- MVP の切り方（枠は全市町村、中身は優先市町村から）は現場で回るか
- 公式情報の扱いに危うい断定がないか（金額・日数は裏取り前に断定しない方針）
- 既存の行政・社協・他団体の取り組みと重複していないか

## 注意

- 本資料は有志の検討用であり、行政の公式発表ではない
- 制度の金額・所要日数・適用可否は各実施機関の判断。公開前に公式で確認する
- `[仮]` や `[要公式確認]` が付いた項目は未確定

## 連絡

CTZC Slack: https://civictechzenchiba.slack.com/archives/C0BPSMN4L5D
