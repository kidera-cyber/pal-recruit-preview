# Handoff: PAL 採用サイト リデザイン

## Overview

株式会社PAL（ロジテックインテグレーター）の採用サイトのフルリデザイン。「物流をコストから、戦略資産に。」を掲げるスローガンを、テック × 未来感のダーク基調ビジュアルで表現しています。新卒・キャリア採用の入口となる、Hero〜Entryまでの1ページ完結型サイト。

主な目的:
- FDE（Field Deployed Engineer）というPAL独自の中核職種の魅力訴求
- 8職種のキャリア紹介と募集要項の公開
- ミッション・バリュー・数字でのブランディング
- カジュアル面談〜エントリーまでの導線設計

## About the Design Files

本バンドルに含まれるHTML/CSS/JSファイルは **HTMLで作成されたデザインリファレンス（プロトタイプ）** です。見た目と挙動を示すためのものであり、そのまま本番環境にコピー＆ペーストすることを想定していません。

開発時のタスクは:
- **既存の実装環境がある場合**: そのコードベースが採用しているフレームワーク（Next.js / Nuxt / SvelteKit / WordPress など）と既存のコンポーネント・デザインシステムを使って **本デザインを忠実に再構築** してください。
- **新規プロジェクトの場合**: 静的サイトジェネレータ（Astro / Next.js Static / 11ty など）または CMS 連携（headlessWP / microCMS など）を推奨。SEO・OGP・パフォーマンスを重視できる構成を選定してください。

## Fidelity

**High-fidelity（ハイファイ）** です。
- 最終的な配色・タイポグラフィ・余白・角丸・シャドウが確定
- インタラクション（scroll reveal / カウントアップ / タブ切替 / アコーディオン / パーティクル）も本番仕様
- レスポンシブは 3ブレークポイント（>960 / 520-960 / <520）で設計済み

そのままの見た目・挙動をピクセルレベルで再現してください。

## Screens / Views

本サイトは1ページ完結のスクロール型です。以下、上から順に各セクションの仕様。

---

### 1. Global Navigation（`header#hdr`）

**Purpose:** サイト内主要セクションへの導線とエントリーCTA。

**Layout:**
- `position: fixed`、全画面幅、高さ 76px
- 内側 `.wrap` は `max-width: 1200px` / 左右 padding 28px
- flex: ロゴ（左） / ナビリンク（中央〜） / エントリーボタン（右）

**States:**
- 初期状態（Hero上）: 背景透明、テキスト白
- スクロール40px以降: `.scrolled` クラス付与 → `background: rgba(255,255,255,.9)` + `backdrop-filter: blur(18px)`、テキストは navy に切替

**Components:**
- **ロゴ:** グラデ角丸マーク（36px, radius 10px, `linear-gradient(120deg, #3b5bff → #00d4c8)`）+ "PAL" / small "RECRUIT 2027"
- **ナビリンク:** 8項目、`font-size: 13.5px / weight: 500`、hover時に下線がグラデでスケール
- **エントリーボタン:** `.btn.btn-primary`（詳細は後述の共通ボタン参照）
- **モバイルハンバーガー:** 44×44px、開くと `.nav-links.open` でドロワー表示

---

### 2. Hero（`section.hero#top`）

**Purpose:** 第一印象とキャッチコピーの提示、エントリーCTAへの誘導。

**Layout:**
- `min-height: 100vh`, `display: flex; align-items: center`
- 背景: 深いネイビー `#171930` + AI生成画像（`assets/hero-bg.jpg`）を 50% opacity で重ね、その上に放射グラデーションのヴェールと 64×64px グリッドライン
- 追加レイヤー: ブラーorb（青 400×400px 右上 / ティール 340×340px 左下）が 14秒でふわふわfloat
- Canvas `<canvas.hero-particles>` で 90点のパーティクル網（ノード＋距離130px以内の接続線）

**Components:**
- **ヒーロータグ（.hero-tag）:** `● 新卒・キャリア採用 通年エントリー受付中` — 丸バッジ、border 1px `rgba(255,255,255,.28)`、パルスドット（ティール #00d4c8）
- **見出し h1:** `font-family: Outfit; font-weight: 900; font-size: clamp(42px, 7.2vw, 92px); line-height: 1.06`
  - 3行構成: `現場に立ち、` / `自分の手で、` （グラデーション：`linear-gradient(100deg, #8fa6ff → #00e6d8 → #8fa6ff)`, 8秒でシフト） / `変えていく。`
- **サブコピー:** `max-width: 580px; color: rgba(255,255,255,.82); font-size: clamp(15px, 1.6vw, 19px)`
- **CTA:** primary "エントリーする" + ghost "PALを知る"
- **スクロールインジケーター（.hero-scroll）:** 画面下中央、1pxの線がドロップアニメーション
- **マーキー:** `DIGITAL LOGISTICS ◆ FIELD DEPLOYED ENGINEER ◆ …` を 30秒で無限スクロール。◆ はティール色

**Interactions:**
- スクロールでヒーロー画像が Y方向 15% パララックス
- reveal 要素は Intersection Observer で `.in` を付与、`opacity + translateY(28px)` から復帰

---

### 3. Stats（`.stats`）

**Purpose:** 会社規模の即時アピール。

**Layout:**
- 白背景、`.stats-inner` は 4カラム grid、パディング 64px 縦
- 各 stat 間に 1px の縦罫線 `var(--line)`

**Components（4枚）:**
- 2000（創業）/ 1600+（グループ従業員数）/ 7＋（自社DXプロダクト）/ 70%（業務工数削減実績）
- 数字: `font-family: Outfit; font-weight: 800; font-size: clamp(36px, 4.8vw, 60px)`, color navy
- サフィックス（`+`, `%` など）: 数字の 0.42em、青 `#3b5bff`

**Behavior:**
- ビューポート50%可視で `animateCount` 発火（1600ms, easeOutCubic）

---

### 4. Why now（`section.why#why`）

**Purpose:** 業界の転換期・PALのポジションの必要性を示す。

**Layout:**
- 2カラム grid、gap 72px
- 左: eyebrow + 見出し + 引用文（ハイライト付き）+ リード文
- 右: `.why-visual` — 460px min-height の navy カード、内側に 4つのフローステップが縦積み

**Components:**
- **quote:** `font-size: clamp(22px, 2.6vw, 32px)`, navy, `.hl` は `background: linear-gradient(transparent 62%, rgba(0,212,200,.32) 0)`（マーカー風）
- **flow-step ×4:** 受注→ピッキング→配送→統合。番号（ティール色）+ タイトル + タグ（DATA/OPS/REAL/STRATEGY）
- **flow-conn:** ステップ間の 2×18px ティールグラデ線
- ステップは初期非表示、可視化後 140msずつ順にfadeIn

---

### 5. Mission（`section.mission.dark#mission`）

**Purpose:** PALのミッションと3つのVALUEを提示。

**Layout:**
- 背景: navy + 放射グラデ + 80×80px ドットグリッド（マスクで中央フェード）
- ステートメント：`font-size: clamp(26px, 3.6vw, 44px); max-width: 940px`
- Values: 3カラム grid, gap 22px

**Components:**
- **VALUE cards:** `padding: 40px 32px`, `background: rgba(255,255,255,.045)`, border 1px `rgba(255,255,255,.1)`
- 各カードに `.vbg`（右下に薄い 140px の連番）
- Hover: `translateY(-6px)` + ボーダーがティール系に

---

### 6. Position（`.position`）

**Purpose:** 「技術 × 現場」の唯一無二ポジションの表現。

**Layout:** 3カラム grid, gap 22px。3枚目がハイライト（navyグラデーション背景 + `.badge` "PAL"）。

**Components:**
- カード: 白背景、border-radius 20px、padding 36px 30px
- `.pt`: Outfit / weight 800 / letter-spacing .16em の小ラベル
- ハイライトカード: `background: linear-gradient(160deg, #20233f, #171930)`, テキスト白

---

### 7. FDE（`.fde#fde`）

**Purpose:** PAL独自職種「FDE」の詳細訴求。

**Layout:**
- 全幅カード（`padding: 72px 64px`）にリード文と 2×2 の point グリッド
- カード右上に薄い `FDE` の巨大タイポ（240px, opacity .06）を装飾配置

**Components:**
- **fde-badge:** グラデ丸バッジ "FDE ＝ 現場 × システムの橋渡し"
- **fde-point ×4:** 白カード、青チェックマークSVG + 太字タイトル + smallキャプション
- Hover: `translateY(-2px)` + border 青

---

### 8. Jobs（`.jobs#jobs`）

**Purpose:** 8職種の一覧提示、詳細への導線。

**Layout:** 3カラム grid, gap 22px（960px以下で 1カラム）

**Components:**
- 各 job カード: 白背景 / border 1px / padding 36px 30px
- Icon container: 54×54px, radius 14px, `background: var(--grad-soft)`、SVGアイコン
- Hover: `translateY(-8px)` + シャドウ + `.ic` がグラデ塗り + 左辺 4px グラデバーが `scaleY(1)`

**8職種:**
1. センター長／候補（BPO / 現場運営）
2. FDE（現場実装エンジニア）
3. プロダクト企画・開発エンジニア（Product Engineer）
4. 運行管理・所長（DTS / 運行管理）
5. 既存顧客深耕（Sales / 既存深耕）
6. 新規営業（BizDev / 新規営業）
7. マーケティング（Marketing）
8. コーポレート部門（Corporate）

---

### 9. Products（`.prods`）

**Purpose:** 自社DXプロダクト群の紹介。

**Layout:** 4カラム grid, gap 16px。1枚目 "Core First" が `grid-column: span 2` で navy背景ワイドカード。

**Components（7点）:**
- Core First（ワイド）/ ロジテックBPO / DTS / Core Mate / Core GX / Core Zero / ロジテックインテグレーション

---

### 10. Career Path（`.career#career`）

**Purpose:** 職種別キャリア段階と、職種間クロスオーバーの提示。

**Layout:**
- **Track ×4:** grid `220px 1fr` の 2カラム。左に職種名（en+jp+説明）、右に4ステージのタイムライン
- ステージ間: 疑似要素 `::before` で薄い横線
- **Crossover:** navy カード（padding 64px 56px、radius 28px）内に SVG マップ + 3枚のクロスカード

**Components:**
- **SVG map:** `viewBox="0 0 1000 470"`、4レーン（BPO / FDE / エンジニア / コンサル）とパスカーブ、中央にFDEハブ（グラデ塗り、リング付き）
- lane線: `stroke-dasharray: 4 6`, `stroke: rgba(255,255,255,.12)`
- クロスカード: 3枚 grid, hover でティール系ボーダー + 4px 浮上

---

### 11. A Day in the Life（`.day#day`）

**Purpose:** 3職種（FDE / BPO / エンジニア）の1日の流れをタブで切替表示。

**Layout:**
- ピル型タブ（padding 6px の丸トラック、アクティブ時 navy 塗り）
- タイムライン: 3カラム grid, gap 18px
- 各 tl-item: パディング 24px、`background: linear-gradient(160deg, #f8fafd, #eef1fb)`

**Behavior:**
- タブクリックで対応パネル表示、`.tl-item` を 80msずつ順に `.in` 付与
- 初回スクロール到達時にもリビール発火

**Content:** 各 6タイムポイント（時刻 + 見出し + 詳細）

---

### 12. Movie（`.movie.dark#movie`）

**Purpose:** YouTubeの採用ムービー埋め込み。

**Layout:** 2カラム（1fr .8fr、gap 60px）。左にコピー・CTA、右に縦型スマホフレーム内で YouTube Shorts を埋め込み。

**Components:**
- **Phone frame:** `aspect-ratio: 9/16`, max-width 340px、`border: 8px solid #1a1c34`, radius 32px
- YouTube iframe URL: `https://www.youtube.com/embed/MTsZZ7EFoKY`

---

### 13. Reasons（`.reasons`）

**Purpose:** PALの大切にする3つのことの詳細版。

**Layout:** 3カラム grid, gap 22px。各カードは白グラデ背景 + border。

**Components:**
- 大きな連番（80px, Outfit-900, グラデテキスト）+ 見出し + 説明

---

### 14. Persona（`.persona#persona`）

**Purpose:** 求める人物像（SKILL 3点 + CHARACTER 6点）。

**Layout:**
- 上部にnavy `.persona-banner`（前提: "可能性を信じる"）
- 3カラム grid × 2グループ（SKILL / CHARACTER）
- 下部に青ボーダー付きnote

**Components:**
- **p-card:** 白背景、tag（skill=青系グラデソフト / char=ティール系）+ 見出し + 説明
- Hover: `translateY(-4px)` + シャドウ

---

### 15. Figures（`.figures#figures`）

**Purpose:** 数字で見るPAL（8枚）。

**Layout:** 4カラム grid, gap 16px。

**Components:**
- 各 fig: パディング 32px 26px、青系グラデ背景
- 数字: `font-size: clamp(30px, 3.4vw, 42px)`, navy, サフィックス（→230名 など）は青

**8指標:**
120→230名 / 2000年 / 1600名 / 7＋ / 6：4 / 2拠点 / 70% / 100%

---

### 16. People（`.people#people`）

**Purpose:** 3名の社員インタビューカード。

**Layout:** 3カラム grid, gap 24px。

**Components:**
- **写真エリア（.ph）:** `aspect-ratio: 4/5`, AI生成ポートレイト、下部にグラデシャドウ + ロール表示
- **本体:** 見出し + 引用文 + `INTERVIEW →` CTA
- Hover: `translateY(-8px)` + 大きめシャドウ + 画像 `scale(1.06)`

**社員（AI生成画像を使用）:**
1. FDE / 2021 中途入社（`assets/person-fde.jpg`）
2. Engineer / 2023 新卒入社（`assets/person-eng.jpg`）
3. Consultant / 2019 中途入社（`assets/person-consultant.jpg`）

---

### 17. Selection Flow（`.flow-sec.dark#flow`）

**Purpose:** 選考ステップ5段階。

**Layout:** 5カラム grid, gap 14px。各ステップの右端に矢印SVGを絶対配置。

**Components:**
- 5ステップ: エントリー / カジュアル面談 / 選考面接 / 最終面接 / 内定
- カード背景: `rgba(255,255,255,.05)` + border 1px `rgba(255,255,255,.12)`

---

### 18. Recruit（`.recruit#recruit`）

**Purpose:** 職種別の詳細募集要項（アコーディオン式）。

**Layout:** 4件のアコーディオン。

**Components:**
- **acc-head:** ジョブタグ + 見出し + `.plus`（開閉インジケーター、開くとティール塗り + rotate 180deg）
- **acc-body:** `max-height: 0 → scrollHeight px` トランジションで開閉
- **spec dl:** grid `140px 1fr`, `dt` は青 weight-700、`dd` は本文カラー

**掲載職種:** FDE / センター長 / プロダクトエンジニア / DTS運行管理

---

### 19. FAQ（`.faq#faq`）

**Purpose:** よくある質問（現状4件）。

**Components:**
- Q/Aマーカー（28×28px、Q はグラデ塗り、A はソフト背景）
- カード hover で青ボーダー + シャドウ

---

### 20. CTA / Entry（`.cta#entry`）

**Purpose:** サイト末尾の大型エントリー誘導。

**Layout:**
- 幅いっぱいの navy カード（radius 32px, padding 80px 60px, テキスト中央揃え）
- 内部にグリッドライン + 放射グラデ

**Components:**
- 見出し: "次の未来を、一緒につくろう。"（`.grad` でティール系グラデテキスト）
- CTA 2つ: primary "新卒採用エントリー" / ghost "キャリア採用エントリー"

---

### 21. Footer

**Layout:** 3カラム grid `1.4fr .8fr .8fr`, gap 60px。

**Components:**
- 左: フッターロゴ + 会社概要文 + `.company-info`（key/value grid）
- 中: RECRUIT リンク集
- 右: COMPANY リンク集
- Copyright: 下部センター

---

## Interactions & Behavior

### Global
- **Smooth scroll:** `html { scroll-behavior: smooth }`, `scroll-padding-top: 80px`
- **Reveal:** Intersection Observer, threshold 0.14, rootMargin `0px 0px -40px 0px`。`.reveal.d1` `.reveal.d2` … で 80ms刻みディレイ
- **Reduced motion:** `@media (prefers-reduced-motion: reduce)` で全アニメーション無効化、カウントアップも即座に最終値表示

### Nav
- スクロール40px超で `.scrolled` クラス付与
- モバイル: ハンバーガーで `.nav-links.open` トグル、リンククリックで閉じる

### Hero
- パーティクル: Canvas、90点（画面幅で 40-90 に可変）、距離130px以内で線描画
- 画像パララックス: 縦スクロールに応じて `scale(1.05) translateY(y*0.15px)`

### Counters
- ビューポート50%可視時に発火、1600ms easeOutCubic、`toLocaleString('en-US')` で桁区切り

### Day Tabs
- クリックで `.active` 差替、パネルの各 `.tl-item` を 60ms + i*80ms で順にリビール

### Accordion
- `head.click` で `.open` トグル、`body.style.maxHeight = scrollHeight + 'px'` で開閉（transition 500ms cubic-bezier）
- `.plus` は 180deg 回転 + 縦線を `scaleY(0)`

### Career SVG
- 静的描画。将来 hover 時にパスをアニメさせる余地あり（現状は静止）

---

## State Management

シンプルな DOM 状態のみ、外部ストアや API 通信は不要:
- Nav scrolled state（scrollYで判定）
- Mobile menu open state（`.open` class）
- Day tab active（`.active` class）
- Accordion open state（`.open` class）
- Reveal in-view state（`.in` class、一度だけ付与）

将来的な拡張候補:
- エントリーCTA → 応募フォーム / マイページログイン（ATSサービス連携）
- People セクション → インタビュー詳細ページ（動的ルート）
- Recruit セクション → CMSからの動的読込

---

## Design Tokens

### Colors

```css
--navy:      #20233f;   /* 主背景（dark section） */
--navy-2:    #171930;   /* 深いnavy（グラデ用） */
--navy-3:    #0f1124;   /* footer背景 */
--ink:       #22243a;   /* 本文 */
--ink-2:     #3a3d55;   /* 本文セカンダリ */
--muted-2:   #6b6d81;   /* 補助テキスト */
--line:      #e7e9f3;   /* ライトボーダー */
--lav:       #dae1f2;   /* ラベンダー */
--lav-2:     #eef1fb;   /* 薄ラベンダー背景 */
--lav-3:     #f2f4fb;   /* さらに薄い背景 */
--bg:        #f6f7fc;   /* ページベース背景 */
--white:     #ffffff;
--accent:    #3b5bff;   /* プライマリブルー */
--accent-2:  #00d4c8;   /* ティール */
--accent-3:  #8fa6ff;   /* ライトブルー（グラデ端） */
```

### Gradients

```css
--grad:      linear-gradient(120deg, #3b5bff 0%, #5b7cfa 45%, #00d4c8 100%);
--grad-2:    linear-gradient(120deg, #8fa6ff 0%, #00e6d8 100%);   /* dark背景用テキストグラデ */
--grad-soft: linear-gradient(120deg, rgba(59,91,255,.14), rgba(0,212,200,.14));
--grad-dark: linear-gradient(160deg, #1a1c34 0%, #20233f 55%, #171930 100%);
```

### Typography

- **本文（Noto Sans JP）:** 400 / 500 / 700 / 900
- **見出し・欧文（Outfit）:** 400 / 600 / 700 / 800 / 900
- Base `line-height: 1.85`、`letter-spacing: -.01em` for headings
- サイズは clamp() で自動スケール:
  - `h1 (hero)`: `clamp(42px, 7.2vw, 92px)`
  - `.sec-title`: `clamp(30px, 4.8vw, 52px)`
  - `.mission-statement`: `clamp(26px, 3.6vw, 44px)`
  - `.fde-card h3`: `clamp(24px, 3.2vw, 38px)`
  - `.stat .num`: `clamp(36px, 4.8vw, 60px)`
  - lead: `16px`
  - body: `13-15.5px`

### Spacing

- Section vertical padding: `120px` (`>960px`) / `80px` (`≤960px`)
- Wrap: `max-width: 1200px; padding: 0 28px`（モバイル 20px）
- Grid gaps: 主に 14 / 16 / 18 / 22 / 24 / 60 / 72px

### Radius

```
--radius:      20px;   /* カード全般 */
--radius-lg:   28px;   /* 大型カード / CTAブロック */
その他: 10px（ロゴマーク）, 14-16px（内部要素）, 100px（ピル / バッジ）, 32px（phone frame / CTA-box）
```

### Shadow

```
--shadow:     0 24px 60px -30px rgba(30,40,90,.45);
--shadow-lg:  0 40px 90px -40px rgba(30,40,90,.55);
buttons: 0 14px 30px -12px rgba(59,91,255,.65)
```

---

## Assets

すべて `assets/` フォルダに含まれます。

| ファイル | 用途 | 生成方式 |
|---|---|---|
| `assets/hero-bg.jpg` | Hero背景の未来型物流倉庫 | AI生成（nano-banana-2、2K、16:9） |
| `assets/person-fde.jpg` | Peopleセクション FDE社員 | AI生成（3:4） |
| `assets/person-eng.jpg` | Peopleセクション エンジニア社員 | AI生成（3:4） |
| `assets/person-consultant.jpg` | Peopleセクション コンサル社員 | AI生成（3:4） |
| `assets/warehouse-dx.jpg` | 予備（未使用） | AI生成（16:9） |
| `assets/office.jpg` | 予備（未使用） | AI生成（16:9） |

**注意:** これらのAI画像は本番公開前に、実際の社員ポートレイトや自社倉庫写真に差し替えることを推奨します。

**その他:**
- Fonts: Google Fonts CDN（Noto Sans JP + Outfit）
- Icons: SVGインラインで記述、外部ライブラリ不使用
- YouTube埋込: `https://www.youtube.com/embed/MTsZZ7EFoKY`

---

## Responsive Behavior

3つのブレークポイント:

### `>960px` — Desktop
- 記載の grid カラム数（3〜5）そのまま
- Hero は 100vh 全画面

### `520-960px` — Tablet / Mobile
- Nav: ハンバーガー表示、ドロワー展開
- Stats: 4→2カラム
- Why/Movie: 2→1カラム
- Values/Reasons/Persona/People: 3→1カラム
- Jobs: 3→1カラム
- Products: 4→2カラム（wide は span 2 継続）
- Career track: 左右2カラム→縦積み
- Steps: 5→1カラム、矢印非表示
- Section padding: 120→80px

### `<520px` — Small mobile
- Stats: 1カラム
- Products / Figures: 1カラム
- Career stages: 2→1カラム

### Reduced motion
- 全アニメーション/トランジション無効化
- reveal 即時表示、カウンター即最終値表示、パーティクル停止

---

## Files

本ハンドオフバンドルに含まれるファイル:

```
design_handoff_pal_recruit/
├── README.md              ← このファイル
├── PAL Recruit.html       ← メインHTML（プロトタイプ）
├── assets/
│   ├── style.css          ← 全スタイル（変数、コンポーネント、レスポンシブ）
│   ├── app.js             ← インタラクション（reveal, tabs, accordion, particles, counter）
│   ├── hero-bg.jpg
│   ├── person-fde.jpg
│   ├── person-eng.jpg
│   ├── person-consultant.jpg
│   ├── warehouse-dx.jpg
│   └── office.jpg
└── reference/
    └── pal-recruit_2.html ← リデザイン元となった参考HTML
```

**参考: プロジェクト内の元ファイル**
- `PAL Recruit.html` — メインHTML
- `assets/style.css` — CSS
- `assets/app.js` — JS
- `reference/pal-recruit_2.html` — オリジナル参考HTML

---

## Implementation Notes for Developers

### 推奨フレームワーク（新規実装の場合）
- **Astro** or **Next.js (App Router, Static Export)** — 静的サイト前提でパフォーマンス最適
- **Tailwind CSS** or **CSS Modules** — 現在のCSS変数はそのまま `:root` に移植可
- **画像最適化:** `next/image` or `astro:assets` で自動 WebP/AVIF 化、遅延読込
- **フォント最適化:** `next/font/google` 経由で self-host + `font-display: swap`

### 既存WordPress等への実装
- カスタムテーマ、または functions.php + カスタムテンプレート
- 各セクションを ACF or Blocks 化して編集可能に
- Recruit / FAQ / People は投稿タイプ化を推奨

### 必要なJSライブラリ
- 現状 **バニラJSのみ** で完結。追加ライブラリ不要
- 移植先が React/Vue の場合は Intersection Observer と Canvas ロジックをコンポーネント化してください

### SEO / メタタグ
- `<title>`, `<meta description>`, OGP, Twitter Card は元HTMLから継承推奨
- `structured data` として JobPosting schema.org を各職種に付与すると求人検索に強い

### Accessibility
- 全ボタン・リンクにフォーカスリング（現状は既定のブラウザ挙動）
- Accordion は `aria-expanded` を実装済み、`aria-controls` の付与を推奨
- パーティクルcanvasは装飾のみ、`aria-hidden="true"` を追加推奨
- カラーコントラスト: navy(#20233f) 上の白テキストで AAA、青(#3b5bff) 上の白で AA

### パフォーマンス
- Hero画像は 2K PNG → 本番では最適化された WebP (60-80% quality) を推奨（〜300KB以内目標）
- ポートレイト3枚も同様に圧縮
- Canvas パーティクルはモバイルで負荷になる可能性あり → `window.innerWidth < 640` で無効化する分岐を追加推奨

### コンテンツ差し替え箇所（公開前チェックリスト）
- [ ] AI生成の社員写真 → 実際の社員ポートレイトへ
- [ ] Hero背景 → 自社倉庫の実写 or 実写＋グラデ合成
- [ ] Stats/Figures の数値 → 最新の実データへ（120→230名 の増員計画は戦略値）
- [ ] 会社情報（住所、代表者、資本金） → 最新公開情報へ
- [ ] YouTube動画URL → 最新の採用ムービーへ
- [ ] エントリーCTAリンク → 実際のATS / マイページURLへ
- [ ] 募集要項の給与レンジ・条件 → 実際の労働条件へ
