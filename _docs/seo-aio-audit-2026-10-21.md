# 採用サイト SEO・AIO・信頼性 監査（2026-10-21）

対象：`renewal/` 配下の正式ページ **33ページ**（比較プレビューは対象外）
基準：GitHubリポジトリの最新状態（コミット `781c557` 時点）

---

## 1. 総合評価

公開前の検証サイトとして、技術的な土台は整っている。

- title の重複 **0件**／H1 が 0個または2個以上のページ **0件**／`alt` 欠落 **0件**
- 壊れた内部リンク **0件**／全33ページに `robots: noindex` が入っている
- 求人詳細11件すべてに JobPosting、全ページに BreadcrumbList、社員インタビュー7件に ProfilePage、
  HOMEに Organization、FAQに FAQPage
- JobPosting の値は承認済み求人票と一致（前回までの検証で確認済み）

残る課題は **技術面よりも「応募できない」こと**に集中している。
正式な応募先URLと `datePosted` が未確定であるかぎり、Google しごと検索には載らず、
応募もできない。これが最大の公開前課題。

---

## 2. 優先度つき監査結果

| ページ | 問題点 | 影響 | 優先度 | 修正内容 | 確認の要否 |
|---|---|---|---|---|---|
| 全求人詳細11件 | 正式な応募先URLが未確定。応募CTAを停止中 | 応募できない | **P0** | 応募先URL確定後にCTAを戻す | 要確認 |
| 全求人詳細11件 | JobPosting に `datePosted` がない | Google しごと検索の必須項目。掲載されない | **P0** | 本番掲載日を確定後に設定 | 要確認 |
| `culture/` | canonical が検証用GitHub Pagesの絶対URL固定。noindex と併用 | 本番移行時に検証環境を指す | **P1** | canonical を外す（ほか2stubと同方針） | 不要（A） |
| `after-joining/` | canonical が別ページ（`../career/`）。noindex と併用 | 指示の矛盾・方針不統一 | **P1** | canonical を外す | 不要（A） |
| `jobs/` | 見出しが h1 → h3 → h4 と1段飛び | 構造の読み取りづらさ | **P1** | h2 → h3 へ昇格（CSSはクラス指定のため見た目は不変） | 不要（A） |
| `about/` `career/` | 「プロダクト企画・開発エンジニアは React／TypeScript での Web 開発経験を必須」 | 承認済み求人票（必須は「何らかのWeb系システム開発の実務経験」）と矛盾 | **P1** | 求人票に合わせて書き換え | **要確認** |
| `jobs/product-engineer/` `jobs/fde/` | `openings/system-engineer/` `openings/fde-*` と同一職種の重複ページ | 求人ページの重複・導線の分散 | **P1** | 統合または転送 | **要確認** |
| 全ページ フッター | 「お問い合わせ」が BtoB 営業の `contact-service/` を指す | 応募フォーム非公開のため求職者が流入しうる | **P1** | ラベルを「お問い合わせ（サービスについて）」にする等 | **要確認** |
| `jobs/dts/` `jobs/large-driver/` | 休日が「週休2日（シフト制）」と「隔週2日休み（月6日〜）」の併記 | 応募者が実際の休日数を判断できない | **P1** | 求人票の確認後に統一 | **要確認** |
| `career/` | 「エンゲージメント・新規営業キャリア 仮案（社内確認中）」 | 公開時に未確定と明示されている状態 | **P2** | 正式内容の確認後に差し替え | **要確認** |
| 全33ページ | `og:image` がない | SNS共有時のカード画像が出ない | **P2** | 本番ドメイン確定後に絶対URLで設定 | 本番公開時 |
| サイト全体 | `sitemap.xml` / `robots.txt` がない | 公開後のクロール効率 | **P2** | 本番公開時に作成 | 本番公開時 |
| `jobs/fde/` `jobs/product-engineer/` | 見出しが h1 → h3 | 構造の読み取りづらさ | **P2** | 重複ページの統合と同時に対応 | **要確認** |
| 全ページ | パンくず構造化データの `item` が相対URL | 本番では絶対URLが望ましい | **P3** | 本番ドメイン確定後 | 本番公開時 |
| 全ページ | `robots: noindex` | 検証サイトのため意図どおり | **P3** | 本番公開時に `set_noindex.py off` | 本番公開時 |

---

## 3. 職種別の検索意図と既存ページの対応

新しいページは作らず、既存ページの役割に振り分けている。

| 職種 | 想定クエリ（検索意図の仮説） | 対応ページ | 現状 |
|---|---|---|---|
| 物流センター運営・センター長 | 物流センター長 仕事内容／センター長候補 未経験／物流センター 業務改善 | `work/#role-bpo` `jobs/openings/*` `people/bpo/` | 仕事内容・必須経験・拠点別条件を掲載済み |
| FDE | Forward Deployed Engineer とは／FDE SE 違い／物流DX エンジニア | `work/#role-fde` `faq/#fq-fde` `jobs/openings/fde-*` | 職種説明・SEとの違い・必要経験を掲載済み |
| システム・プロダクト開発 | 物流システム開発 求人／倉庫管理システム 開発／物流 Androidアプリ | `work/#role-system` `jobs/openings/system-engineer/` `people/system/` | 開発対象は掲載済み。**使用技術は未確認のため未掲載** |
| 営業・BizDev | 物流DX 営業／BizDev 事業開発 違い | `work/#role-sales` `jobs/openings/engagement-member/` | 掲載済み |
| 人材派遣営業 | 人材派遣 法人営業 求人 大阪 | `work/#role-staffing` `jobs/openings/staffing-sales-leader/` | 掲載済み |
| ドライバー | ルート配送 求人 船橋／大型ドライバー 千葉／手積みなし 配送 | `jobs/dts/` `jobs/large-driver/` `faq/#fq-dts` | 掲載済み |

### 市場調査でわかったこと（出典つき）

- **物流DXエンジニアは大手が参入**：日立製作所（配送最適化・倉庫管理システム導入のPM）、
  ロジスティードソリューションズ（物流DXエンジニア／コンサルタント）など。
  PALの差別化は「自社で物流センターを運営しており、開発した機能を現場で検証できる」点で、
  これは既に `work/#role-system` と求人詳細に書かれている。
- **センター長候補の競合求人は「未経験可」を打ち出す一方、年収は非公開が多い**。
  PALは拠点別に想定年収を明示しており、この点は現状のままで優位。
- **PALはすでに Green Japan に求人が掲載されている**（社名検索での競合は自社の媒体掲載）。
- 月間検索数・競合難易度・検索順位は取得していない。Search Console・GA4・キーワードツールは未接続のため、
  上表の「想定クエリ」は検索意図の仮説であり、実測値ではない。

---

## 4. 今回修正する箇所（A＝既存情報だけで直せるもの）

比較プレビュー `renewal/seo-fix-preview/` に3点だけ当てている。

| 対象 | 変更前 | 変更後 |
|---|---|---|
| `culture/` | `<link rel="canonical" href="https://kidera-cyber.github.io/pal-recruit-preview/renewal/people/">` | canonical を削除（転送は meta refresh に任せる） |
| `after-joining/` | `<link rel="canonical" href="../career/">` | canonical を削除 |
| `jobs/` | h1 → **h3**（職種グループ）→ **h4**（求人カード） | h1 → **h2** → **h3** |

本文・デザイン・求人条件・title・meta description・robots は変更していない。
見出しのCSSは `.jgroup__h` / `.jcard__n` のクラス指定のため、見た目も変わらない。

## 5. 今回修正しない箇所（C）

- ページ構成・セクション順・デザイン・FVコピー・社員インタビュー
- `og:image`／`sitemap.xml`／`robots.txt`／絶対canonical（本番ドメイン確定後）
- `renewal/jobs/fde/` と `renewal/jobs/product-engineer/` の見出し階層（重複ページの統合と同時に判断すべきため）
- meta description の文面（33ページすべてで重複なし・本文と矛盾なしのため修正不要と判定）

---

## 6. 本番公開時の必須確認事項

1. `tools/set_noindex.py off` で全ページの `noindex` を外す
2. 正式な応募先URLを確定し、`tools/set_entry_cta.py on` で応募CTAを戻す
3. `data/jobs-openings.json` の `date_posted` に本番掲載日を設定（Google しごと検索の必須項目）
4. canonical を本番ドメインの絶対URLへ置換
5. パンくず構造化データの `item` を絶対URLへ置換
6. `og:image` を本番ドメインの絶対URLで追加
7. `sitemap.xml` と `robots.txt` を作成
8. 比較プレビュー（`*-preview/`）を本番から除外、または削除
