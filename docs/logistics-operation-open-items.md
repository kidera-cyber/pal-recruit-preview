# 物流センター運営（LEVEL 02）と保留求人の管理メモ（LOGIOPS v1）

最終更新：2026-10-20

## 1. URL変更

| 旧 | 新 |
|---|---|
| `renewal/jobs/center-manager/` | **`renewal/jobs/logistics-operation/`** |

募集しているのは **アソシエイト（船橋）／メンバー（厚木・東広島）／責任者候補（須磨）** であり、
全員が「センター長」「センター長候補」ではないため、「物流センター運営」を中心とした名称へ改めた。

- ページタイトル：**物流センター運営の仕事｜募集レベルと募集拠点｜株式会社PAL**
- 旧URLは転送専用HTML（`noindex,follow` ＋ meta refresh ＋ JS）として残置。
  本番WordPress移行時に **HTTP 301** へ置き換える
- 生成スクリプトも `tools/build_center_manager.py` → `tools/build_logistics_operation.py` に改名

### 3階層

| | URL | 役割 |
|---|---|---|
| LEVEL 01 | `jobs/` | 現在の求人を探す |
| LEVEL 02 | `jobs/logistics-operation/` | 物流センター運営という仕事・募集レベルを知る |
| LEVEL 03 | `jobs/openings/<id>/` | 各勤務地の正式な募集条件 |

---

## 2. 公開していない求人（制作管理側のみ）

**ファイル名：`物流運営（責任者候補）＠船橋.pdf`**

| 項目 | ファイル名 | 求人票の本文 |
|---|---|---|
| 勤務地 | 船橋 | **厚木** |
| 求人タイトル | — | 物流センター責任者候補 / 厚木 |
| 事業所名 | — | 厚木センター |
| 所在地 | — | 神奈川県厚木市上依知 字上ノ原3007-9 |

本文の条件：想定年収504万円〜600万円／月給42万円〜50万円／取扱商品 食品／日勤・夜勤（22時以降あり）。
応募条件は須磨の責任者候補と同じ。

**公開画面には一切出していない**（件数にも含めず、「確認中の求人があります」という表示も出さない）。
`data/jobs-openings.json` の `status: "hold"` で保留中。
正式な勤務地が確定したら `status` を `open` にして `sh tools/build_all.sh` を実行すれば公開される。

---

## 3. 検索インデックス（NOINDEX v1）

公開前の確認用サイトのため、`renewal/` 配下の全HTMLに
`<meta name="robots" content="noindex,nofollow">` を入れている（旧URLの転送ページのみ `noindex,follow`）。

```
付ける：python3 -I tools/set_noindex.py on
外す  ：python3 -I tools/set_noindex.py off     ← 本番公開時
```

JobPosting のJSON-LD・canonical・構造化データ・本文はそのまま残しているため、実装の確認には影響しない。
`sh tools/build_all.sh` はビルドの最後に `set_noindex.py on` を実行する。

### 本番公開時に切り替えるもの

1. `tools/set_noindex.py off`（noindex 解除）
2. `data/jobs-openings.json` の `date_posted`（掲載開始日。**求人票に記載がないため推測で入れない**）
3. `validThrough`（掲載期限。決まっていなければ省略可）
4. 正式な応募URL（下記）
5. 募集状態（`status`）の最終確認

---

## 4. ENTRY の応募先（ENTRY-URL v1）

`renewal/entry/` のエントリーボタン2つが
`https://www.pal-style.co.jp/contact-service/`（**BtoB営業のお問い合わせフォーム**）を指していたため、
**リンクを外した**。応募者を誤ったフォームへ誘導しないための対応。

現在は「エントリーフォームは準備中です」という案内のみ。
**正式な応募先URLが確定するまで、推測で別のURLは置かない。**
確定後、`renewal/entry/index.html` の該当ブロックを2つのボタン（新卒採用／キャリア採用）へ戻す。
旧記載は git 履歴から参照できる。

なお、フッター COMPANY 欄の「お問い合わせ」は会社への問い合わせ導線のため、そのまま残している。
