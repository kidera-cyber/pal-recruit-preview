# 本番公開 TODO（WordPress 本番公開時）

現在の GitHub Pages（`https://kidera-cyber.github.io/pal-recruit-preview/`）は**制作確認用のプレビュー**。
本番 WordPress の正式URLが確定するまで、GitHub Pages のURLを本番 canonical として扱わない。

**本書が本番公開TODOの唯一の置き場所。**ここに書いた項目は、
プレビュー段階の「未解決問題」として毎回報告しない。

---

## A｜社内情報がないと進められないもの

| # | 項目 | 必要な情報 |
|---|---|---|
| A1 | **正式ENTRY URL（P0）** | 応募フォームのURL。確定まで応募CTAは非表示のまま（`tools/set_entry_cta.py off`）。`https://www.pal-style.co.jp/contact-service/` は BtoB サービスの問い合わせ窓口であり、採用応募には使わない。影響する求人は下表「A1 の対象求人」の11件 |
| A2 | 本番ドメイン | canonical・OGP・sitemap がこれに依存 |
| A3 | **従業員数の定義** | 「120名（アルバイト・パート含む約1,600名）」の120名が何を指すか（正社員のみか）と集計基準日。コーポレートサイトの会社概要（2026-10-22 確認）にも定義・基準日の記載がないため、採用サイトでも「正社員」と断定していない |
| A4 | **求人URLの命名統一（承認待ち）** | 正式な個別求人詳細のうち、`/jobs/dts/` と `/jobs/large-driver/` だけが `/jobs/openings/` 配下にない。`/jobs/openings/dts-route-driver/` `/jobs/openings/large-route-driver/` へ寄せる場合は、本番公開時に旧URLから301で転送する。**プレビュー段階では変更しない**（外部リンク・検索評価への影響を避けるため） |

### A1 の対象求人（正式応募先が決まるまで応募ボタンを出せない求人）

| # | 求人 | URL |
|---|---|---|
| 1 | 物流センター運営（アソシエイト・船橋） | `/jobs/openings/funabashi-associate/` |
| 2 | 物流センター運営（メンバー・厚木） | `/jobs/openings/atsugi-member/` |
| 3 | 物流センター運営（メンバー・東広島） | `/jobs/openings/higashihiroshima-member/` |
| 4 | 物流センター責任者候補（須磨） | `/jobs/openings/suma-manager/` |
| 5 | FDE（アソシエイト〜メンバー・大阪） | `/jobs/openings/fde-associate/` |
| 6 | FDE（メンバー・リーダー候補・大阪） | `/jobs/openings/fde-leader/` |
| 7 | 自社開発 Web・アプリエンジニア（大阪） | `/jobs/openings/system-engineer/` |
| 8 | エンゲージメント・新規営業（大阪） | `/jobs/openings/engagement-member/` |
| 9 | 法人営業（人材派遣）（大阪） | `/jobs/openings/staffing-sales-leader/` |
| 10 | 4tルート配送ドライバー（船橋） | `/jobs/dts/` |
| 11 | 10tドライバー（船橋） | `/jobs/large-driver/` |

人事（`/jobs/openings/hr/`）は募集予定のため、そもそも応募CTAを出さない。

**確定後の最小実装**（調査済み・コード変更は不要）

1. `tools/set_entry_cta.py` の `ENTRY`（現在は `(?:\.\./)*entry/`）が指す先を正式応募先に差し替える
2. `renewal/entry/index.html` の「エントリーフォームは準備中です」を正式フォームに置き換える
3. `python3 -I tools/set_entry_cta.py on` を実行（コメントアウトを外すだけ。11ファイルが戻る）
4. 求人ごとに応募先が異なる場合は、`data/jobs-openings.json` に `apply_url` を足し、
   `tools/build_jobs.py` の詳細ページ末尾のボタンから参照する

**使ってはいけない応募先**（調査結果）

| 候補 | 可否 | 理由 |
|---|---|---|
| `https://www.pal-style.co.jp/contact-service/` | ✕ | BtoBサービスの問い合わせ窓口。採用応募の受け口ではない |
| 求人媒体（Indeed 等）の応募画面 | 判断待ち | 媒体掲載の有無・正式な応募先URLが未確認 |
| 採用担当のメールアドレス | 判断待ち | 公開してよいアドレスが未確認 |
| ATS | 判断待ち | 利用中のシステムが未確認 |

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
| B12 | 保留求人の扱い | `manager-candidate-hold`（勤務地不一致）を公開するか判断。ドライバー2件は条件確定済みで公開中 |
| B13 | **募集終了求人の処理** | 終了した求人は `data/jobs-openings.json` の `status` を `open` 以外にする。ページを残す場合は JobPosting に `validThrough`（過去日）を入れ、一覧・HOMEのステータスは `tools/sync_role_status.py` が自動で追従する |

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
