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
| A2 | **本番ドメイン** | canonical・OGP・sitemap・パンくずの item がこれに依存。**DOMAIN v1 で実装済み**：`data/site.json` の `production_origin` に入れて `bash tools/build_all.sh` を流すだけで全ページが切り替わる（下の「本番ドメインの切り替え」を参照） |
| A3 | **従業員数の定義** | 「120名（アルバイト・パート含む約1,600名）」の120名が何を指すか（正社員のみか）と集計基準日。コーポレートサイトの会社概要（2026-10-22 確認）にも定義・基準日の記載がないため、採用サイトでも「正社員」と断定していない |
| A4 | **求人URLの命名統一（判断待ち。現状維持でも問題なし）** | 下の「求人URLの整理案」を参照。**既存URLは変更していない。** 新しい求人で例外が増えないよう、ビルド時チェック（URLNAME v1）は導入済み |

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

**確定後の有効化手順**（APPLY v1／ENTRY-CTA v2 で実装済み。コード変更は不要）

応募ボタンのデザイン・配置は実装済みで、いまは押せない状態（STATE 1）で表示している。
正式な応募先が決まったら次の2つを行うだけで STATE 2（応募受付中）になる。

1. **求人ごとの応募ボタン**（求人詳細11件＋JOBS一覧カード11件）
   `data/jobs-openings.json` の `apply_urls.default_url` に正式な応募先を入れる。
   求人ごとに応募先が違う場合は、その求人の `apply_url` に入れる（default より優先）。
   → `bash tools/build_all.sh` で `<button disabled>` が `<a href="…">` に変わる。
     一覧と求人詳細は同じ値を見ているのでズレない。未設定の求人だけ押せないまま残る。
2. **サイト共通のCTA**（ヘッダー ENTRY／ドロワー／フッター／HOMEの「応募する」）
   `renewal/entry/index.html` の「エントリーフォームは準備中です」を正式フォームに置き換え、
   `tools/build_all.sh` の最終行を `set_entry_cta.py preview` → `on` に変える。
   → 押せないボタンと「応募先URLの設定前です」の注記が消え、元のリンクに戻る。

**公開前チェック**

- `python3 -I tools/applycta.py --check` … 応募先が未設定の募集中求人を一覧表示する
- `python3 -I tools/set_noindex.py off` … 未設定の求人があると**停止する**（B1 の前に必ず通る）
  どうしても先に公開する場合のみ `--allow-no-apply` を付ける

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

---

## 本番ドメインの切り替え（DOMAIN v1・実装済み）

ドメインを推測で入れないため、いまは `data/site.json` の `production_origin` を `null` にしている。
この状態では **GitHub Pages の見え方は変わらない**。

| | `production_origin` が null（いま） | 値を入れたあと |
|---|---|---|
| canonical | `./`（相対自己参照） | `https://…/jobs/openings/…/`（絶対） |
| og:url / og:image | 出さない | 絶対URLで出す |
| パンくずの `item` | `../../`（相対） | 絶対URL |
| sitemap.xml | 作らない | 30ページ分を生成（転送stub4本は除外） |
| robots.txt | `Disallow: /`（全ページ） | `Allow: /` ＋ `Sitemap:` 行 |

**手順**

1. `data/site.json` の `production_origin` に、スキーム付きのオリジンを入れる（末尾スラッシュなし）
   - オリジン直下でない場所に置く場合は `base_path` も入れる（例 `/recruit`）
2. `bash tools/build_all.sh`
3. `python3 -I tools/set_noindex.py off`（応募先URLが未設定だと止まる＝APPLY v1 のゲート）

`python3 -I tools/set_domain.py --status` で現在の状態を確認できる。
これにより旧 B5・B6・B7・B8・B9 は自動化された（手作業は不要）。

---

## 求人URLの整理案（URLNAME v1）

**現状の分類**

| 分類 | URL | JobPosting |
|---|---|---|
| A：正式な個別求人詳細（11） | `/jobs/openings/<id>/`（9） | あり |
| | `/jobs/dts/` `/jobs/large-driver/`（2・既存URL） | あり |
| B：職種紹介ページ（3） | `/jobs/fde/` `/jobs/logistics-operation/` `/jobs/product-engineer/` | なし（正しい） |
| C：転送ページ（2） | `/jobs/center-manager/` `/work/fde/` | なし |
| D：重複・不要 | なし | — |

**判断：既存URLは変更しない。**
A の2件だけ `/jobs/openings/` 配下にないが、URLが分かれていること自体は検索上の問題ではなく、
変更すると外部リンク・媒体掲載・検索評価を壊す可能性がある。
そのかわり、**新しい求人で例外が増えないようにビルド時チェックを入れた**
（`tools/build_jobs.py` の `URL_EXCEPTIONS`。`detail_url` を新しく書くとビルドが止まる）。

**それでも統一する場合（本番公開時のみ・承認が必要）**

| 旧URL | 新URL | 転送 |
|---|---|---|
| `/jobs/dts/` | `/jobs/openings/dts-route-driver/` | 301 |
| `/jobs/large-driver/` | `/jobs/openings/large-route-driver/` | 301 |

手順：`data/jobs-openings.json` から該当の `detail_url` を外す → `URL_EXCEPTIONS` から2件を削除
→ `bash tools/build_all.sh` → 旧URLに301転送を設定（本番サーバ側）→ sitemap を再生成。
GitHub Pages は301を返せないため、**プレビューでは実施しない。**

---

## 従業員数の表示（EMPNUM v1 / v2）

コーポレートサイトの会社概要（2026-10-22 確認）の表記は
「従業員数 120名（アルバイト・パート含む約1,600名）」で、**120名の定義も集計基準日も公表されていない**。
そのため採用サイトでは「正社員」と断定せず、数字の関係だけが分かる形にしている。

```
120名
アルバイト・パートを含めると約1,600名
```

定義（120名の対象範囲）と集計基準日が分かれば、ABOUT の数字セクションに1行足すだけで反映できる。

---

## 「人事」と「労務」の呼称（HRNAME v1）

確認できている事実と、サイト上の表記を次のようにそろえた。

| 場所 | 表記 | 根拠 |
|---|---|---|
| FAQ Q1 ／ WORK | コーポレートの4領域＝経理・総務・労務・法務 | 依頼元に確認済み |
| FAQ Q4 ／ WORK | 採用などの人事業務は**労務が担当** | 依頼元に確認済み |
| JOBS のグループ名 | 「人事 / HR」→ **「人事・労務」** | 4領域の言葉と求人の言葉を同じ場所に置く |
| 求人の職種名 | **「人事」のまま** | 求人票の業務が採用〜オンボーディングで、職種名と一致している |

人事の正式な募集要項（雇用形態・勤務地・給与・応募資格）が決まった段階で、
職種名を「人事」のままにするか、部門名を添える（例「人事（労務課）」）かを確認する。
