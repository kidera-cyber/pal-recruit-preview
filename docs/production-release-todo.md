# 本番公開 TODO（WordPress 本番公開時）

現在の GitHub Pages（`https://kidera-cyber.github.io/pal-recruit-preview/`）は**制作確認用のプレビュー**。
本番 WordPress の正式URLが確定するまで、GitHub Pages のURLを本番 canonical として扱わない。

**本書が本番公開TODOの唯一の置き場所。**ここに書いた項目は、
プレビュー段階の「未解決問題」として毎回報告しない。

---

## A｜社内情報がないと進められないもの

| # | 項目 | 必要な情報 |
|---|---|---|
| A1 | **正式ENTRY URL** | 応募フォームのURL。確定まで応募CTAは非表示のまま（`tools/set_entry_cta.py off`）。`https://www.pal-style.co.jp/contact-service/` は BtoB サービスの問い合わせ窓口であり、採用応募には使わない |
| A2 | **ドライバー求人の正式条件** | 休日・休憩時間・車両トン数。`docs/driver-open-items.md` 参照 |
| A3 | 本番ドメイン | canonical・OGP・sitemap がこれに依存 |

## B｜本番公開時に実施する作業

| # | 作業 | 内容 |
|---|---|---|
| B1 | **noindex 解除** | `python3 -I tools/set_noindex.py off`（全33ページ） |
| B2 | **正式ENTRY URL の設定** | `tools/set_entry_cta.py` の `ENTRY` を正式URLに変え、`on` で応募CTAを戻す |
| B3 | **datePosted の設定** | `data/jobs-openings.json` の `date_posted` に、本番で求人を正式公開した日を入れる。求人票に掲載日がないため、プレビューでは `null` のままでよい |
| B4 | **validThrough の設定** | 募集終了予定日が決まっている求人のみ。未定の求人には入れない |
| B5 | **canonical を本番ドメインの絶対URLへ** | 現在は全ページ `./`（相対自己参照）。一括置換できる形になっている。転送stub4本（`culture/` `after-joining/` `jobs/center-manager/` `work/fde/`）は canonical を置かない方針を維持 |
| B6 | パンくず構造化データの `item` を絶対URLへ | 全ページ |
| B7 | **OGP** | `og:image` を本番ドメインの絶対URLで追加（現在は全ページ未設定）。`og:url` も同様 |
| B8 | **sitemap.xml** | 正式ページのみ。転送stub4本は除外 |
| B9 | **robots.txt** | sitemap の場所を記載 |
| B10 | **JobPosting 最終確認** | 全求人で title・勤務地・給与・雇用形態・勤務時間・休日・必須/歓迎資格・募集状態が本文と一致すること。リッチリザルトテストでエラー0 |
| B11 | 内部リンクの最終確認 | 相対リンクが本番で解決すること・転送stub4本の遷移先 |
| B12 | 保留求人の扱い | `manager-candidate-hold`（勤務地不一致）、ドライバー2件を公開するか判断 |

## C｜本番公開後に実施する検証

| # | 項目 |
|---|---|
| C1 | **Search Console** の登録とサイトマップ送信 |
| C2 | インデックス状況の確認（転送stub4本が `noindex` のままであること） |
| C3 | **リッチリザルトテスト**で JobPosting の検証（`datePosted` があること） |
| C4 | パンくず・FAQ・Organization・ProfilePage の構造化データ検証 |
| C5 | **GA4** の計測開始（測定IDの設置、応募ボタンのクリックをイベント化） |
| C6 | **応募フォームのテスト**（実際に1件通して受信まで確認） |
| C7 | 検索クエリの実測（Search Console の検索パフォーマンス） |
| C8 | Core Web Vitals / モバイルユーザビリティ |

---

## プレビュー段階で対応済み（本番TODOではない）

- 全ページ `noindex`（プレビューURLを検索対象にしない）
- 応募CTAの非表示（正式URL未確定のため）
- canonical の整理（転送stub4本から不適切な canonical を削除）
- 見出し階層の整理（JOBS・職種ハブ）
- 求人情報と本文・JobPosting の整合
- 壊れた内部リンク 0件
- レスポンシブ確認（1440〜320px）
- 比較プレビューの削除（サイト内に preview / test / demo / 仮案 を残さない）
