# JobPosting 構造化データ（実装待ち・要承認）

作成日：2026-10-16　状態：**未実装**

## なぜ未実装か

`datePosted` は JobPosting の必須プロパティだが、**求人の掲載開始日が未確定**のため、
推測で値を入れると事実と異なる構造化データになる。また Google の JobPosting は
「実在し、公開中で、応募を受け付けている求人ページ」が対象であり、現在の GitHub Pages は
制作・確認用プレビューであるため、公開前の実装は要件を満たさない。

## 実装の条件（すべて満たしたら貼り付ける）

1. 本番公開日が確定し、`datePosted` に実際の掲載開始日（ISO 8601 / 例 `2026-10-31`）を入れられる
2. 掲載期限が決まっていれば `validThrough` を追加（決まっていなければ省略してよい）
3. 応募フローが確定している（現在は ENTRY のCTAが新卒・キャリアとも
   `https://www.pal-style.co.jp/contact-service/` で、ページ内に「仮設定」と明記されている）。
   自社サイト内で応募が完結する場合のみ `directApply: true` を付与する
4. `hiringOrganization.sameAs` と `jobLocation` の住所は、公開時点の会社概要と一致していること

## 貼り付け先

各ページの `</head>` 直前に `<script type="application/ld+json">…</script>` として追加する。

| ファイル | 職種 |
|---|---|
| `renewal/jobs/fde/index.html` | FDE（Forward Deployed Engineer） |
| `renewal/jobs/center-manager/index.html` | センター長／候補（現場運営） |
| `renewal/jobs/product-engineer/index.html` | プロダクト企画・開発エンジニア |
| `renewal/jobs/dts/index.html` | 運行管理・所長（DTS） |

## 値の出典

すべて各募集要項ページに掲載済みの記載をそのまま使用している（推測値なし）。
`baseSalary` は「想定年収」欄の下限・上限。`employmentType` は「雇用形態＝正社員」から `FULL_TIME`。

### FDE（Forward Deployed Engineer）（`renewal/jobs/fde/index.html`）

```html
<script type="application/ld+json">{
  "@context": "https://schema.org",
  "@type": "JobPosting",
  "title": "FDE（Forward Deployed Engineer）",
  "description": "顧客の現場に入り込み、DXを実装して現場を変える仕事です（現場の課題把握→仮説検証→改善提案→現場実装→活用推進）。技術力より人物面を最優先しており、現場好き・課題解決意欲があれば、SE・データ・物流の知識は入社後に習得していく前提です（未経験・新卒可）。勤務時間は9:00〜18:00のフレックスタイム制（標準労働8時間）、完全週休2日（土日祝）。選考はエントリー→カジュアル面談→面接（複数回）→最終面接→内定（Web面接可）です。",
  "datePosted": "★★★ 公開日を入れる（例 2026-10-31）★★★",
  "employmentType": "FULL_TIME",
  "hiringOrganization": {
    "@type": "Organization",
    "name": "株式会社PAL",
    "sameAs": "https://www.pal-style.co.jp/"
  },
  "jobLocation": [
    {
      "@type": "Place",
      "address": {
        "@type": "PostalAddress",
        "addressCountry": "JP",
        "addressRegion": "大阪府",
        "addressLocality": "大阪市西区",
        "streetAddress": "新町"
      }
    },
    {
      "@type": "Place",
      "address": {
        "@type": "PostalAddress",
        "addressCountry": "JP",
        "addressRegion": "東京都",
        "addressLocality": "千代田区",
        "streetAddress": "神田小川町"
      }
    }
  ],
  "applicantLocationRequirements": {
    "@type": "Country",
    "name": "JP"
  },
  "baseSalary": {
    "@type": "MonetaryAmount",
    "currency": "JPY",
    "value": {
      "@type": "QuantitativeValue",
      "minValue": 4500000,
      "maxValue": 7500000,
      "unitText": "YEAR"
    }
  }
}</script>
```

> 勤務地欄に「リモート相談可」とあるが、常時フルリモートではないため `jobLocationType: TELECOMMUTE` は付けない（Google はフルリモート求人にのみ使用を認めている）。

### センター長／候補（現場運営）（`renewal/jobs/center-manager/index.html`）

```html
<script type="application/ld+json">{
  "@context": "https://schema.org",
  "@type": "JobPosting",
  "title": "センター長／候補（現場運営）",
  "description": "現場が自律的に回り、成果を生み続ける状態をつくる仕事です。現場マネジメント・オペレーション改善・数値管理の経験者歓迎。現場とデジタルの両方を楽しめる方を求めています（未経験・新卒可）。勤務は実働8時間（拠点によりシフト制）、完全週休2日（土日祝）。選考はエントリー→カジュアル面談→面接（複数回）→最終面接→内定（Web面接可）です。",
  "datePosted": "★★★ 公開日を入れる（例 2026-10-31）★★★",
  "employmentType": "FULL_TIME",
  "hiringOrganization": {
    "@type": "Organization",
    "name": "株式会社PAL",
    "sameAs": "https://www.pal-style.co.jp/"
  },
  "jobLocation": [
    {
      "@type": "Place",
      "address": {
        "@type": "PostalAddress",
        "addressCountry": "JP",
        "addressRegion": "大阪府",
        "addressLocality": "大阪市",
        "streetAddress": ""
      }
    },
    {
      "@type": "Place",
      "address": {
        "@type": "PostalAddress",
        "addressCountry": "JP",
        "addressRegion": "東京都",
        "addressLocality": "",
        "streetAddress": ""
      }
    }
  ],
  "applicantLocationRequirements": {
    "@type": "Country",
    "name": "JP"
  },
  "baseSalary": {
    "@type": "MonetaryAmount",
    "currency": "JPY",
    "value": {
      "@type": "QuantitativeValue",
      "minValue": 3500000,
      "maxValue": 7000000,
      "unitText": "YEAR"
    }
  }
}</script>
```

### プロダクト企画・開発エンジニア（`renewal/jobs/product-engineer/index.html`）

```html
<script type="application/ld+json">{
  "@context": "https://schema.org",
  "@type": "JobPosting",
  "title": "プロダクト企画・開発エンジニア",
  "description": "現場で使われ、成果につながるプロダクトを生み出す仕事です（現場起点でのプロダクト企画・開発／現場フィードバックの反映／活用推進）。React／TypeScriptでのWeb開発経験が必須。勤務時間は9:00〜18:00のフレックスタイム制、完全週休2日（土日祝）。選考はエントリー→カジュアル面談→面接（複数回）→最終面接→内定（Web面接可）です。",
  "datePosted": "★★★ 公開日を入れる（例 2026-10-31）★★★",
  "employmentType": "FULL_TIME",
  "hiringOrganization": {
    "@type": "Organization",
    "name": "株式会社PAL",
    "sameAs": "https://www.pal-style.co.jp/"
  },
  "jobLocation": [
    {
      "@type": "Place",
      "address": {
        "@type": "PostalAddress",
        "addressCountry": "JP",
        "addressRegion": "大阪府",
        "addressLocality": "大阪市西区",
        "streetAddress": "新町"
      }
    },
    {
      "@type": "Place",
      "address": {
        "@type": "PostalAddress",
        "addressCountry": "JP",
        "addressRegion": "東京都",
        "addressLocality": "千代田区",
        "streetAddress": "神田小川町"
      }
    }
  ],
  "applicantLocationRequirements": {
    "@type": "Country",
    "name": "JP"
  },
  "baseSalary": {
    "@type": "MonetaryAmount",
    "currency": "JPY",
    "value": {
      "@type": "QuantitativeValue",
      "minValue": 5000000,
      "maxValue": 9000000,
      "unitText": "YEAR"
    }
  }
}</script>
```

> 勤務地欄に「リモート相談可」とあるが、常時フルリモートではないため `jobLocationType: TELECOMMUTE` は付けない（Google はフルリモート求人にのみ使用を認めている）。

### 運行管理・所長（DTS）（`renewal/jobs/dts/index.html`）

```html
<script type="application/ld+json">{
  "@context": "https://schema.org",
  "@type": "JobPosting",
  "title": "運行管理・所長（DTS）",
  "description": "安全な運行を土台に、データで現場を進化させる仕事です（配車・運行の管理／データに基づく業務改善・標準化の提案／安全管理）。配車・運行管理の経験者歓迎。勤務は実働8時間（拠点によりシフト制）、シフトによる週休2日。選考はエントリー→カジュアル面談→面接（複数回）→最終面接→内定（Web面接可）です。",
  "datePosted": "★★★ 公開日を入れる（例 2026-10-31）★★★",
  "employmentType": "FULL_TIME",
  "hiringOrganization": {
    "@type": "Organization",
    "name": "株式会社PAL",
    "sameAs": "https://www.pal-style.co.jp/"
  },
  "jobLocation": [
    {
      "@type": "Place",
      "address": {
        "@type": "PostalAddress",
        "addressCountry": "JP",
        "addressRegion": "大阪府",
        "addressLocality": "",
        "streetAddress": ""
      }
    },
    {
      "@type": "Place",
      "address": {
        "@type": "PostalAddress",
        "addressCountry": "JP",
        "addressRegion": "東京都",
        "addressLocality": "",
        "streetAddress": ""
      }
    }
  ],
  "applicantLocationRequirements": {
    "@type": "Country",
    "name": "JP"
  },
  "baseSalary": {
    "@type": "MonetaryAmount",
    "currency": "JPY",
    "value": {
      "@type": "QuantitativeValue",
      "minValue": 4000000,
      "maxValue": 7000000,
      "unitText": "YEAR"
    }
  }
}</script>
```
