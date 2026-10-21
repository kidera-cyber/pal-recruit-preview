# -*- coding: utf-8 -*-
"""
===== LRGDRV v1 =====
大型ルート配送ドライバー（Indeed_大型ドライバー②.pdf）の募集要項を組み立てる。

  renewal/jobs/large-driver/

4t求人（renewal/jobs/dts/）と同じ構成・同じシェルを使い、本文だけこの求人票の
内容に差し替えている。求人データは data/jobs-openings.json の large-route-driver。

・掲載している条件・数値・時間・エリアは、すべて求人票の記載と一致させている。
・求人票に無い項目（年間休日数／残業時間／固定残業代／賞与／昇給／退職金／
  転勤／寮／住宅手当／手当の金額／採用人数／面接回数）は補完していない。
  4t求人にある賞与・昇給・早朝手当・退職金は、この求人票には記載がないため
  持ち込んでいない。
・車両トン数は求人票のタイトル（8トン）と本文（10トン）で記載が異なるため、
  職種名・本文・構造化データのいずれでもトン数を断定していない。
  勤務時間・休日も求人票にある記載をそのまま載せ、推測で一方に寄せていない。
  社内確認事項は docs/large-driver-open-items.md を参照。
・求人票の訴求表現（「業界でも注目」「物流と運送のデジタル化を牽引」
  「男女ともに大歓迎」「ガンガン稼ぎたい」「新車に乗れます」「年齢不問」）は
  採用していない。

  python3 -I tools/build_large_driver.py
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f: return f.read()
def wr(p, s):
    os.makedirs(os.path.join(ROOT, os.path.dirname(p)), exist_ok=True)
    with open(os.path.join(ROOT, p), "w", encoding="utf-8") as f: f.write(s)

JOBPOSTING = True       # 正式掲載（2026-10-21）

TITLE = "大型ルート配送ドライバー求人｜千葉県船橋市｜株式会社PAL"
DESC  = ("株式会社PAL（DTS／運送部）の大型ルート配送ドライバー求人。千葉県船橋市・afs船橋センター、"
         "正社員、月給36万円〜60万円。大手スーパーや外食チェーンへの食品ルート配送で、カゴ車と"
         "パワーゲートを使うため手積み・手降ろしはありません。千葉県を中心に一都三県、1日3件程度。"
         "大型自動車運転免許が必須の正社員の募集です。")
assert len(DESC) == 160, "meta description は160文字ちょうどにする（現在 %d 文字）" % len(DESC)

NOTE = ('<!-- ===== LRGDRV v1：この求人は「下書き」である。\n'
        '     求人票（Indeed_大型ドライバー②.pdf）に未解決の不一致が4点あるため、\n'
        '     公開中の JOBS 一覧（renewal/jobs/）には掲載していない。\n'
        '       ① 車両トン数：タイトル「8トン」／本文「10トン」\n'
        '       ② 勤務時間：拘束12時間（8:00〜20:00 等）／記載は「実働8時間」\n'
        '       ③ 休日：「週休2日（シフト制）」／「隔週2日休み（月6日〜）」\n'
        '          （平均所定168時間＝月21日稼働とも整合しない）\n'
        '       ④ 応募方法：Indeed設定「メールで受付」／本文「Webにてご応募」\n'
        '     ①は職種名・本文から車両トン数を外して回避、②③は求人票の記載どおり\n'
        '     両方を併記し、推測で一方に寄せていない。詳細は docs/large-driver-open-items.md。 ===== -->')

# ------------------------------------------------------------------ 募集要項（下書き）
def build_detail():
    S = rd("renewal/jobs/dts/index.html")
    head = S[:S.index('<main id="top">')]
    tail = S[S.index('</main>'):]

    # 4t求人のhead（title / description / og / パンくず / JobPosting）を差し替える
    head = re.sub(r"<title>.*?</title>", "<title>%s</title>" % html.escape(TITLE, quote=False), head, flags=re.S)
    head = re.sub(r'(<meta name="description" content=")[^"]*(">)', lambda m: m.group(1)+html.escape(DESC)+m.group(2), head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*(">)', lambda m: m.group(1)+html.escape(TITLE)+m.group(2), head)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*(">)', lambda m: m.group(1)+html.escape(DESC)+m.group(2), head)
    crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "採用情報", "item": "../../"},
        {"@type": "ListItem", "position": 2, "name": "募集職種", "item": "../../jobs/"},
        {"@type": "ListItem", "position": 3, "name": "大型ルート配送ドライバー"}]}
    head = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema\.org", "@type": "BreadcrumbList".*?</script>',
                  '<script type="application/ld+json">%s</script>' % json.dumps(crumb, ensure_ascii=False), head, flags=re.S)
    # 4t求人の JobPosting を、この求人の内容に差し替える
    i = head.index("<!-- ===== DRVJOB v1：JobPosting")
    j = head.index("</script>", head.index('<script type="application/ld+json">{"@context":"https://schema.org","@type":"JobPosting"', i)) + len("</script>")
    jp = {
        "@context": "https://schema.org", "@type": "JobPosting",
        "title": "大型ルート配送ドライバー",
        "description": ("大型トラックを使用し、大手スーパーや外食チェーンの各店舗へ食品を配送する"
                        "ルート配送業務です。配送件数は1日3件程度、配送エリアは千葉県を中心に一都三県で、"
                        "近距離・日帰りのみです。全車両にパワーゲートを搭載し、積み降ろしにはカゴ車を"
                        "使用するため、手積み・手降ろしはありません。"),
        "employmentType": "FULL_TIME",
        "hiringOrganization": {"@type": "Organization", "name": "株式会社PAL",
                               "sameAs": "https://www.pal-style.co.jp/"},
        "jobLocation": {"@type": "Place", "address": {
            "@type": "PostalAddress", "addressCountry": "JP", "addressRegion": "千葉県",
            "addressLocality": "船橋市", "streetAddress": "高瀬町24-6 afs船橋センター内"}},
        "baseSalary": {"@type": "MonetaryAmount", "currency": "JPY",
                       "value": {"@type": "QuantitativeValue", "minValue": 360000,
                                 "maxValue": 600000, "unitText": "MONTH"}},
        "qualifications": "大型自動車運転免許",
        "experienceRequirements": "経験不問。配送の実務経験がなくても同乗研修（OJT）で学べます。",
        "workHours": ("シフト制。日勤 8:00〜20:00／9:00〜21:00、夜勤 21:00〜翌9:00／24:00〜翌12:00／"
                      "1:00〜13:00（いずれも実働8時間）。平均所定労働時間は1か月あたり168時間。"),
        "jobBenefits": ("社会保険完備（健康保険・雇用保険・労災保険・厚生年金）、有給休暇、"
                        "通勤手当あり（月5万円まで）、免許取得支援制度あり、制服貸与、同乗研修（OJT）あり"),
    }
    jp_note = ('<!-- ===== LRGDRV v1：JobPosting 構造化データ。\n'
               '     値はすべて求人票（Indeed_大型ドライバー②.pdf）の記載と一致させている。\n'
               '     車両トン数は求人票のタイトル（8トン）と本文（10トン）で記載が異なるため、\n'
               '     構造化データでもトン数を断定していない。\n'
               '     datePosted は求人票に掲載開始日の記載がないため入れていない。\n'
               '     Google しごと検索へ出す場合は、本番掲載日が確定してから追記する。 ===== -->\n'
               '<script type="application/ld+json">%s</script>' % json.dumps(jp, ensure_ascii=False))
    head = head[:i] + (jp_note if JOBPOSTING else "") + head[j:]

    body = '''<nav class="crumb" aria-label="パンくず"><div class="wrap"><a href="../../">採用情報</a><a href="../../jobs/">募集職種</a><span aria-current="page">大型ルート配送ドライバー</span></div></nav>

''' + NOTE + '''
<section class="phead">
  <div class="wrap">
    <p class="slabel">Jobs ／ DTS・運送部</p>
    <h1 class="ptitle">大型ルート配送ドライバー</h1>
    <p class="plead">千葉県船橋市・正社員・月給36万円〜60万円｜大型免許を活かす近距離・日帰りのルート配送</p>
  </div>
</section>

<section class="sec sec--tight" id="points">
  <div class="wrap">
    <div class="shead rv" style="margin-bottom:20px">
      <p class="slabel">Points</p>
      <h2 class="stitle" style="font-size:clamp(21px,2.5vw,29px)"><span class="nw">この仕事の、</span><span class="nw">4つの特徴。</span></h2>
    </div>
    <ul class="drvpts rv">
      <li class="drvpt"><span class="en">01</span><b>手積み・手降ろしなし</b><p>積み降ろしにはカゴ車を使用します。全車両にパワーゲートを搭載しています。</p></li>
      <li class="drvpt"><span class="en">02</span><b>近距離・日帰りのみ</b><p>千葉県を中心とした一都三県への配送です。長距離・泊まりの運行はありません。</p></li>
      <li class="drvpt"><span class="en">03</span><b>配送件数は1日3件程度</b><p>固定ルートで、1日に回る配送件数は3件程度です。</p></li>
      <li class="drvpt"><span class="en">04</span><b>日勤・夜勤を選べます</b><p>シフト制で、日勤2パターン・夜勤3パターンから選べます。</p></li>
    </ul>
  </div>
</section>

<section class="sec sec--tight" id="work">
  <div class="wrap">
    <div class="shead rv" style="margin-bottom:20px">
      <p class="slabel">Work</p>
      <h2 class="stitle" style="font-size:clamp(21px,2.5vw,29px)"><span class="nw">大型トラックで、</span><span class="nw">スーパーや外食チェーンへ</span><span class="nw">食品を届ける。</span></h2>
      <p class="slead">大型自動車運転免許をお持ちの方を対象とした、近距離ルート配送ドライバーの募集です。大型トラックを使用し、大手スーパーや外食チェーンの各店舗へ食品を配送するルート配送業務をお願いします。</p>
    </div>
    <!-- ===== DUTYCARD v1：仕事内容をカード型（.jdcards）に。文章・順番は変更していない。 ===== -->
    <ul class="jdcards rv">
      <li>大型トラックでの食品配送（固定ルート）</li>
      <li>配送件数は1日3件程度</li>
      <li>配送エリアは千葉県を中心に一都三県（近距離・日帰りのみ）</li>
      <li>全車両にパワーゲートを搭載</li>
      <li>積み降ろしにはカゴ車を使用するため、手積み・手降ろしはありません</li>
      <li>配送の実務経験がなくても、同乗研修（OJT）で学べます</li>
    </ul>
  </div>
</section>

<section class="sec sec--tight" id="day">
  <div class="wrap">
    <div class="shead rv" style="margin-bottom:20px">
      <p class="slabel">A Day</p>
      <h2 class="stitle" style="font-size:clamp(21px,2.5vw,29px)">1日の流れ。</h2>
    </div>
    <ol class="drvflow rv">
      <li><span class="en">01</span><b>出勤・出発準備</b>
        <ul><li>船橋営業所に出勤</li><li>アルコールチェック</li><li>乗務するトラックの点検</li></ul></li>
      <li><span class="en">02</span><b>積み込み・確認</b>
        <ul><li>出荷先に移動</li><li>事前に用意されたカゴ車を確認</li><li>専用端末で配送先を確認</li><li>カゴ車をトラックに積み込み、配送先へ出発</li></ul></li>
      <li><span class="en">03</span><b>店舗へ配送</b>
        <ul><li>店舗に到着</li><li>パワーゲートを使ってカゴ車を降ろす</li></ul></li>
      <li><span class="en">04</span><b>回収</b>
        <ul><li>納品が完了したら、コンテナやカゴ車を回収</li></ul></li>
      <li><span class="en">05</span><b>帰庫</b>
        <ul><li>すべてのルートを回り終えたら営業所に戻る</li><li>片付けを済ませて退勤</li></ul></li>
    </ol>
  </div>
</section>

<section class="sec sec--tight" id="spec">
  <div class="wrap">
    <div class="shead rv" style="margin-bottom:20px">
      <p class="slabel">Requirements</p>
      <h2 class="stitle" style="font-size:clamp(21px,2.5vw,29px)">募集要項。</h2>
    </div>
    <div class="drvboxes rv">
      <section class="drvbox">
        <h3 class="drvbox__h"><span class="en">01</span>勤務条件</h3>
        <div class="spec"><dl>
          <dt>雇用形態</dt><dd>正社員（試用期間なし）</dd>
          <dt>給与</dt><dd>月給36万円〜60万円</dd>
          <dt>手当</dt><dd>残業手当／深夜手当／資格手当／無事故手当</dd>
          <dt>勤務時間</dt><dd>日勤・夜勤からお選びいただけます。<br><b>日勤</b>　8:00〜20:00／9:00〜21:00<br><b>夜勤</b>　21:00〜翌9:00／24:00〜翌12:00／1:00〜13:00<br>※いずれも実働8時間です。</dd>
          <dt>勤務形態</dt><dd>シフト制<br>平均所定労働時間：1か月あたり168時間</dd>
          <dt>休日・休暇</dt><dd>週休2日（シフト制）<br>※隔週2日休み（月6日〜）<br>希望休はできる限り優先します。</dd>
        </dl></div>
      </section>

      <section class="drvbox">
        <h3 class="drvbox__h"><span class="en">02</span>応募条件</h3>
        <div class="spec"><dl>
          <dt>必須</dt><dd>大型自動車運転免許</dd>
          <dt>経験</dt><dd>経験不問／配送の実務経験がなくても応募できます。</dd>
          <dt>研修</dt><dd>同乗研修（OJT）あり</dd>
        </dl></div>
        <h3 class="drvbox__h" style="margin-top:28px"><span class="en">03</span>勤務地</h3>
        <div class="spec"><dl>
          <dt>勤務地</dt><dd>千葉県船橋市高瀬町24-6　afs船橋センター内</dd>
          <dt>アクセス</dt><dd>JR京葉線「南船橋駅」より徒歩30分</dd>
          <dt>通勤</dt><dd>車通勤OK（駐車場完備）／バイク・自転車通勤OK<br>交通費（ガソリン代も規定支給）</dd>
        </dl></div>
      </section>

      <section class="drvbox drvbox--wide">
        <h3 class="drvbox__h"><span class="en">04</span>待遇・福利厚生</h3>
        <div class="spec"><dl>
          <dt>社会保険</dt><dd>社会保険完備（健康保険／雇用保険／労災保険／厚生年金）</dd>
          <dt>休暇</dt><dd>有給休暇</dd>
          <dt>制度・手当</dt><dd>通勤手当あり（月5万円まで）<br>免許取得支援制度あり<br>制服貸与<br>同乗研修（OJT）あり</dd>
        </dl></div>
      </section>
    </div>
    <p class="note" style="margin-top:20px">※ ご応募はWebから受け付けています（電話応募は受け付けておりません）。面接の際は履歴書（写真貼付）をご持参ください。自社サイトからの応募フォームは準備中です。</p>
    <p class="note">※ 掲載している条件は、この求人の募集内容です。同じ船橋の<a class="textlink textlink--sm" href="../dts/">4tルート配送ドライバー</a>とは必要な免許・車両が異なります。</p>
  </div>
</section>

<section class="sec sec--tight" id="compare">
  <div class="wrap">
    <div class="shead rv" style="margin-bottom:18px">
      <p class="slabel">Compare</p>
      <h2 class="stitle" style="font-size:clamp(21px,2.5vw,29px)">4tルート配送ドライバーとの違い。</h2>
      <p class="slead">同じafs船橋センターでの食品ルート配送ですが、必要な免許と車両が異なります。勤務地・給与・勤務時間・休日は求人票上は同じ条件です。</p>
    </div>
    <div class="spec rv"><dl class="drvcmp">
      <dt>必須免許</dt><dd><b>大型</b>：大型自動車運転免許<br><b>4t</b>：中型自動車運転免許（8t）または2007年6月1日以前取得の普通自動車運転免許</dd>
      <dt>車両</dt><dd><b>大型</b>：大型トラック<br><b>4t</b>：4tトラック</dd>
      <dt>手当</dt><dd><b>大型</b>：残業／深夜／資格／無事故<br><b>4t</b>：残業／深夜／資格／早朝／無事故</dd>
      <dt>賞与・昇給・退職金</dt><dd><b>大型</b>：求人票に記載がありません<br><b>4t</b>：賞与 年1回（実績による）／昇給 年1回（4月）／退職金あり（勤務3年以上）</dd>
    </dl></div>
    <p class="rv" style="margin-top:22px"><a class="btn btn--ghost" href="../dts/">4tルート配送ドライバーの募集要項を見る<span class="btn__ico" aria-hidden="true">▶</span></a></p>
  </div>
</section>

<section class="sec sec--tight" id="voice">
  <div class="wrap">
    <div class="shead rv" style="margin-bottom:18px">
      <p class="slabel">People</p>
      <h2 class="stitle" style="font-size:clamp(21px,2.5vw,29px)">実際に働く人の話を見る。</h2>
      <p class="slead">DTS／運送部で働く社員のインタビューを掲載しています。本人の経験とキャリアを紹介したもので、この求人の募集条件とは別の内容です。</p>
    </div>
    <p class="rv"><a class="btn btn--ghost" href="../../people/dts/">DTS社員インタビューを見る<span class="btn__ico" aria-hidden="true">▶</span></a></p>
  </div>
</section>
'''
    wr("renewal/jobs/large-driver/index.html",
       head + '<main id="top">\n' + body + '</main>\n' + tail[len('</main>'):].lstrip("\n"))

if __name__ == "__main__":
    build_detail()
    print("大型ルート配送ドライバーの募集要項を生成： renewal/jobs/large-driver/")
