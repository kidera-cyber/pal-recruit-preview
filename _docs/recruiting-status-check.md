# 募集状況・職種名の要確認一覧（管理用）

最終更新：2026-10-19（HOMEJOBS-OFF v1）
突合対象：HOME「FIND YOUR FIELD」9職種 ／ WORK 9職種カード ／ JOBS 一覧・職種詳細4ページ

HOMEから OUR JOBS（職種カード8枚）を削除したため、**HOMEで募集状況を表示しているのは
FIND YOUR FIELD の9チップだけ**になりました。この一覧はその表示根拠の管理簿です。

---

## 1. 突合結果（9職種）

| ID | HOME 分野名 | 表示 | JOBS の募集要項 | 判定 |
|---|---|---|---|---|
| role-bpo | BPO / 現場運営 | 募集中 | センター長／候補（現場運営）<br>`jobs/center-manager/` ＋ `#job-bpo` | ○ |
| role-clean | Cleanliness / クレンリネス | **募集中** | **なし** | **★要確認** |
| role-fde | FDE | 募集中 | FDE（Forward Deployed Engineer）<br>`jobs/fde/` ＋ `#job-fde` | ○ |
| role-system | System / Product | 募集中 | プロダクト企画・開発エンジニア<br>`jobs/product-engineer/` ＋ `#job-engineer` | ○ |
| role-dts | DTS / 運送・運行 | 募集中 | 配送ドライバー（DTS）<br>`jobs/dts/` ＋ `#job-dts` | ○ |
| role-sales | Engagement / Sales | 募集中 | エンゲージメント・新規営業<br>`#job-sales`（**詳細ページなし**） | △ |
| role-mkt | Marketing / Content | 募集中 | マーケティング・コンテンツ制作<br>`#others`（**条件は準備中**） | △ |
| role-bizdev | BizDev | **確認中** | なし | ○（表示が実態と一致） |
| role-corp | Corporate | 募集中 | コーポレート<br>`#others`（**条件は準備中**） | △ |

---

## 2. ★要確認（最優先）

### A. クレンリネス（Cleanliness）の募集状況

HOMEの FIND YOUR FIELD では **「募集中」** と表示していますが、
JOBS 一覧にも `#others` にも**募集要項がありません**。応募できるページが存在しない状態です。

削除前の OUR JOBS では、クレンリネスのタイルだけ「募集中」ラベルも「募集要項を見る」ボタンも
付いていませんでした。その差が、OUR JOBS の削除によって**見えなくなりました**。

「未確認の募集状況を推測で変更しない」というご指示に従い、**表示は変更していません。**
ご確認のうえ、どちらかをご指示ください。

- **募集している** → JOBS `#others` にクレンリネスを追加する（マーケ・コーポレートと同じ扱い）
- **募集していない／確認中** → FIND YOUR FIELD の表示を「確認中」へ

```bash
# 「確認中」に変える場合（1コマンド）
cd ~/Desktop/pal-recruit-preview && python3 -I -c "
import re,io
for p in ['renewal/index.html','renewal/home-recruit-preview/index.html']:
    s=open(p).read()
    s=re.sub(r'(href=\"(?:\.\./)?work/#role-clean\">(?:(?!</a>).)*?)<span class=\"fchip__st\"><b>募集中</b></span>',
             r'\1<span class=\"fchip__st fchip__st--tbd\"><b>確認中</b></span>', s, flags=re.S)
    open(p,'w').write(s)
print('done')"
```

### B. エンゲージメント・新規営業 ― 募集要項の体裁

`#job-sales` に節はありますが、**専用の詳細ページがなく**、節内の2本のリンクが
どちらも `people/sales/`（社員インタビュー）を指しています。募集要項への導線が実質ありません。

- 勤務地：HOME（削除前のタイル）「配属先による」／ JOBS「確認中」で**不一致**でした

### C. マーケティング・コーポレート ― 条件が「準備中」

`#others` に「下記も通年で募集しています。個別の募集要項は準備中です。」とあり、
雇用形態・給与・勤務地などの条件が未掲載です。FIND YOUR FIELD では「募集中」と表示しています。

### D. 配送ドライバー（DTS）― 募集条件12項目が確認中

`jobs/dts/` のリードに「募集条件は社内で確認中です」と明記。勤務地も「確認中」。

### E. 「通年募集」の表記3箇所

`jobs/#others`「下記も通年で募集しています」／ `entry/`「新卒・キャリアともに通年で募集中」／
FAQ「いずれも通年で募集しています」。受付体制の裏づけが未確認です。

### F. 応募窓口が仮設定（別件・最優先）

`entry/` のエントリーボタン2本が `https://www.pal-style.co.jp/contact-service/`（B2Bの営業問い合わせ
フォーム）を指しています。正しい窓口は `https://www.pal-style.co.jp/contact-recruitment/` です。
詳細は前回の報告を参照。

---

## 3. 職種名の整理（分野名と募集職種名の区別）

**FIND YOUR FIELD と WORK の職種名は9件すべて一致**しています（分野名）。
JOBS 側は募集職種名で、意図的に別の名前です。混同しないよう対応表を残します。

| 分野名（FIND YOUR FIELD・WORK） | 募集職種名（JOBS） |
|---|---|
| BPO / 現場運営 | センター長／候補（現場運営） |
| Cleanliness / クレンリネス | （なし） |
| FDE | FDE（Forward Deployed Engineer） |
| System / Product | プロダクト企画・開発エンジニア |
| **DTS / 運送・運行** | **配送ドライバー（DTS）** |
| Engagement / Sales | エンゲージメント・新規営業 |
| Marketing / Content | マーケティング・コンテンツ制作 |
| BizDev | （なし） |
| Corporate | コーポレート |

### DTS の区別（厳守事項）

| | 表記 | 内容 |
|---|---|---|
| 事業分野 | **DTS / 運送・運行** | 輸送・運行に関わる領域。FIND YOUR FIELD・WORK で使用 |
| 募集職種 | **配送ドライバー（DTS）** | 現在の募集ポジション。JOBS で使用 |
| 社員インタビュー | DTS / 運送 | K.Y（千葉営業所 所長）。**配送ドライバーの募集とは別** |
| 1日の流れ | **DTSドライバーの1日。** | アンカー `people/dts/#a-day`。所長の1日ではない |

`people/dts/` のリードに「K.Yが現在担当している営業所長の仕事とは異なります」と明記済みです。
