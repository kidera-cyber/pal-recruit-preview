# -*- coding: utf-8 -*-
"""
===== JOBSOPEN v1 =====
現在募集中の求人（data/jobs-openings.json）から JOBS ページ一式を組み立てる。

  一覧   renewal/jobs/index.html
  求人詳細 renewal/jobs/openings/<id>/index.html   ※ status が open のものだけ

値はすべて求人票の記載どおりで、スクリプト側では補完も一般化もしない。
JobPosting 構造化データは status=open の求人詳細ページにだけ出力する。
絞り込みはJavaScriptだが、9件すべてのカードと本文はHTMLに入っているので
JavaScriptが無効でも全求人を読める。

  python3 -I tools/build_jobs.py
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f: return f.read()
def wr(p, s):
    os.makedirs(os.path.join(ROOT, os.path.dirname(p)), exist_ok=True)
    with open(os.path.join(ROOT, p), "w", encoding="utf-8") as f: f.write(s)
def e(x): return html.escape(str(x), quote=False)

D    = json.loads(rd("data/jobs-openings.json"))
CATS = {c["key"]: c for c in D["categories"]}
OPEN = [o for o in D["openings"] if o["status"] == "open"]
PREF_SLUGS = D.get("pref_slugs", {})
def pref_slug(name):
    """表示名ではなく内部値で絞り込むためのスラッグ。未登録の都道府県も必ず値を持つ。"""
    return PREF_SLUGS.get(name) or ("pref-" + str(abs(hash(name)) % 100000))
PREFS = []
for o in OPEN:
    if o["pref"] and o["pref"] not in PREFS: PREFS.append(o["pref"])

MARK = ("<!-- ===== JOBSOPEN v1：リクナビHRTechで承認済みの求人票9件（2026-10-20 時点）"
        "をもとに、\n     tools/build_jobs.py が data/jobs-openings.json から生成している。"
        "手で編集せず、\n     JSON を直してからビルドし直すこと。\n"
        "     ・条件・数値・勤務地・応募資格は、すべて求人票の記載と一致させている。\n"
        "     ・求人票にない項目（年間休日の内訳、転勤の有無が未記載のもの等）は補完していない。\n"
        "     ・求人票がない職種は『募集中』にしていない。\n"
        "     ・求人票にある『最先端』『市場価値が飛躍的に高まる』などの訴求表現は採用していない。 ===== -->")

# ------------------------------------------------------------------ カード
def card(o):
    c = CATS[o["cat"]]
    return f'''      <li class="jcard" data-job-category="{e(o['cat'])}" data-location="{e(pref_slug(o['pref']))}">
        <p class="jcard__cat">{e(c['name'])}</p>
        <h4 class="jcard__n">{e(o['title'])}<span class="jcard__lv">{e(o['level'])}｜{e(o['place_short'])}</span></h4>
        <dl class="jcard__dl">
          <dt>勤務地</dt><dd>{e(o['pref'])}{e(o['city'])}</dd>
          <dt>想定年収</dt><dd><b>{e(o['salary_year'])}</b></dd>
          <dt>雇用形態</dt><dd>{e(o['employment'].split('（')[0])}</dd>
        </dl>
        <p class="jcard__foot"><span class="jchip">募集中</span>
          <a class="jcard__cta" href="openings/{e(o['id'])}/">募集要項を見る<i aria-hidden="true">&#8594;</i></a></p>
      </li>'''

def group(key):
    c = CATS[key]
    hub = ('<a class="textlink textlink--sm" href="%s">%s</a>を見る。' % (e(c["hub"]), e(c["hub_label"]))) if c.get("hub") else ""
    items = [o for o in OPEN if o["cat"] == key]
    cards = "\n".join(card(o) for o in items)
    return f'''    <section class="jgroup" data-group="{e(key)}">
      <h3 class="jgroup__h"><span class="jgroup__n">{e(c['name'])}</span><span class="jgroup__c en" data-total="{len(items)}">{len(items)} {"POSITION" if len(items)==1 else "POSITIONS"}</span></h3>
      <p class="jgroup__lead">{hub}仕事の内容をくわしく知りたい方は<a class="textlink textlink--sm" href="{e(c['work_anchor'])}">仕事内容を見る</a>、働いている人の話は<a class="textlink textlink--sm" href="{e(c['people'])}">{e(c['people_label'])}</a>をご覧ください。</p>
      <ul class="jcards">
{cards}
      </ul>
    </section>'''

FILTER_JS = '''<!-- ===== JOBSOPEN v2：職種・勤務地の絞り込み。このページだけで使う最小限のJS。
     ・判定は表示テキストではなく data-job-category / data-location の内部値で行う。
     ・職種と勤務地はAND条件。どちらかに条件が入っていれば必ず絞り込む。
     ・総件数・グループ件数・0件メッセージは、いつも表示中のカード数と一致させる。
     ・求人が増えてもJSは変更不要。カードに data 属性を付けるだけで動く。
     ・カードと本文はすべてHTMLに入っているため、JavaScriptが無効でも全求人を読める
       （その場合は絞り込みUIを出さず、すべての求人を表示する）。 ===== -->
<script>
(function(){
  var root=document.getElementById('joblist'); if(!root) return;
  root.classList.add('is-js');
  var cards=[].slice.call(root.querySelectorAll('.jcard'));
  var groups=[].slice.call(root.querySelectorAll('.jgroup'));
  var total=document.getElementById('jobcount');
  var none=document.getElementById('jobnone');
  var selectedCategory='all', selectedLocation='all';

  function apply(){
    var shown=0;
    cards.forEach(function(card){
      var categoryMatch=(selectedCategory==='all')||(card.getAttribute('data-job-category')===selectedCategory);
      var locationMatch=(selectedLocation==='all')||(card.getAttribute('data-location')===selectedLocation);
      var ok=categoryMatch&&locationMatch;
      card.hidden=!ok;
      if(ok) shown++;
    });
    groups.forEach(function(g){
      var vis=[].slice.call(g.querySelectorAll('.jcard')).filter(function(c){return !c.hidden;}).length;
      g.hidden=(vis===0);
      var c=g.querySelector('.jgroup__c');
      if(c) c.textContent=vis+' '+(vis===1?'POSITION':'POSITIONS');
    });
    [].slice.call(root.querySelectorAll('.jfil__b')).forEach(function(b){
      var on=(b.hasAttribute('data-filter-category')
                ? b.getAttribute('data-filter-category')===selectedCategory
                : b.getAttribute('data-filter-location')===selectedLocation);
      b.setAttribute('aria-pressed', on?'true':'false');
      b.classList.toggle('is-active', on);
    });
    if(total) total.textContent=shown;
    if(none) none.hidden=(shown>0);
  }

  [].slice.call(root.querySelectorAll('.jfil__b')).forEach(function(b){
    b.addEventListener('click',function(){
      if(b.hasAttribute('data-filter-category')) selectedCategory=b.getAttribute('data-filter-category');
      else selectedLocation=b.getAttribute('data-filter-location');
      apply();
    });
  });
  apply();
})();
</script>'''


def filters():
    cat_b = '<button class="jfil__b is-active" type="button" data-filter-category="all" aria-pressed="true">すべて</button>' + \
        "".join('<button class="jfil__b" type="button" data-filter-category="%s" aria-pressed="false">%s</button>'
                % (e(c["key"]), e(c["name"])) for c in D["categories"]
                if any(o["cat"] == c["key"] for o in OPEN))
    pref_b = '<button class="jfil__b is-active" type="button" data-filter-location="all" aria-pressed="true">すべて</button>' + \
        "".join('<button class="jfil__b" type="button" data-filter-location="%s" aria-pressed="false">%s</button>'
                % (e(pref_slug(p)), e(p)) for p in PREFS)
    return f'''    <div class="jfil">
      <div class="jfil__row"><p class="jfil__k">職種</p><div class="jfil__bs">{cat_b}</div></div>
      <div class="jfil__row"><p class="jfil__k">勤務地</p><div class="jfil__bs">{pref_b}</div></div>
      <p class="jfil__n">現在 <b id="jobcount">{len(OPEN)}</b> 件の求人を掲載しています。</p>
    </div>
    <p class="jfil__none" id="jobnone" hidden>現在、この条件で募集中の求人はありません。</p>'''

# ------------------------------------------------------------------ 一覧
def build_index():
    S = rd("renewal/jobs/index.html")
    head = S[:S.index('<main id="top">')]
    tail = S[S.index('<section class="sec sec--navy sec--tight" id="selection">'):]

    title = "募集中の求人一覧｜物流センター運営・FDE・システム開発・営業｜株式会社PAL 採用"
    desc = ("株式会社PALが現在募集している求人の一覧です。物流センター運営（千葉・船橋／神奈川・厚木／"
            "広島・東広島／兵庫・須磨）、FDE（大阪本社）、"
            "システム / プロダクト開発（大阪本社）、エンゲージメント・新規営業と法人営業（人材派遣・大阪本社）の"
            "求人について、勤務地・想定年収・雇用形態・勤務時間・休日・応募条件を掲載しています。")
    head = re.sub(r'<title>.*?</title>', '<title>%s</title>' % e(title), head, count=1, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % html.escape(desc), head, count=1)
    head = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="%s">' % html.escape(title), head, count=1)
    head = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="%s">' % html.escape(desc), head, count=1)

    groups_html = "\n".join(group(c["key"]) for c in D["categories"]
                            if any(o["cat"] == c["key"] for o in OPEN))
    body = f'''<nav class="crumb" aria-label="パンくず"><div class="wrap"><a href="../">採用情報</a><span aria-current="page">募集職種</span></div></nav>

{MARK}
<section class="phead">
  <div class="wrap">
    <p class="slabel">Jobs</p>
    <h1 class="ptitle">今、募集している仕事。</h1>
    <p class="plead">勤務地・職種から、現在募集中の求人を探せます。掲載しているのは、応募を受け付けている求人の正式な条件です。</p>
  </div>
</section>

<section class="sec sec--tight" id="openings">
  <div class="wrap" id="joblist">
{filters()}
{groups_html}
    <p class="note" style="margin-top:28px">※ 給与はいずれも固定残業代を含む金額です。内訳は各求人の募集要項に掲載しています。</p>
  </div>
</section>

<section class="sec sec--soft sec--tight" id="others">
  <div class="wrap">
    <div class="shead rv" style="margin-bottom:22px">
      <p class="slabel">Other roles</p>
      <h2 class="stitle" style="font-size:clamp(22px,2.6vw,30px)">そのほかの募集・職種。</h2>
    </div>
    <ul class="others rv">
      <li id="job-dts"><b>4tルート配送ドライバー（DTS / 運送部）</b><a class="textlink textlink--sm" href="dts/">募集要項を見る</a></li>
      <li id="job-marketing"><b>Marketing / Content（マーケティング・コンテンツ制作）</b><span class="others__none">募集条件を確認中です</span></li>
      <li id="job-corporate"><b>Corporate（コーポレート）</b><a class="textlink textlink--sm" href="../people/corporate/">コーポレートの社員インタビュー</a></li>
      <li id="job-clean"><b>Cleanliness（クレンリネス）</b><span class="others__none">募集条件を確認中です</span></li>
    </ul>
    <p class="note rv">※ 4tルート配送ドライバーには正式な募集要項があります。ほかの職種は募集条件を確認中のため、「募集中」として掲載していません。仕事の内容は<a class="textlink textlink--sm" href="../work/">仕事を知る</a>でご覧いただけます。</p>
    <p class="rv" style="margin-top:24px"><a class="btn btn--ghost" href="../entry/">カジュアル面談・エントリーについて<span class="btn__ico" aria-hidden="true">▶</span></a></p>
  </div>
</section>

'''
    wr("renewal/jobs/index.html", head + '<main id="top">\n' + body + tail.replace('</main>', FILTER_JS + '\n</main>', 1))

# ------------------------------------------------------------------ 求人詳細
def spec(rows):
    return '<div class="spec"><dl>' + "".join(
        '<dt>%s</dt><dd>%s</dd>' % (e(k), v) for k, v in rows if v) + '</dl></div>'

def li(items):
    return '<ul class="drvlist">' + "".join('<li>%s</li>' % e(x) for x in items) + '</ul>'

def jobposting(o):
    jp = {
        "@context": "https://schema.org", "@type": "JobPosting",
        "title": "%s（%s）" % (o["title"], o["level"]),
        "description": o["about"] + "【主な仕事内容】" + "／".join(o["duties"]),
        "employmentType": "FULL_TIME",
        "hiringOrganization": {"@type": "Organization", "name": "株式会社PAL",
                               "sameAs": "https://www.pal-style.co.jp/"},
        "jobLocation": {"@type": "Place", "address": {
            "@type": "PostalAddress", "addressCountry": "JP",
            "addressRegion": o["pref"], "addressLocality": o["city"],
            "streetAddress": o["street"]}},
        "baseSalary": {"@type": "MonetaryAmount", "currency": "JPY",
                       "value": {"@type": "QuantitativeValue",
                                 "minValue": o["salary_min"], "maxValue": o["salary_max"],
                                 "unitText": "YEAR"}},
        "qualifications": ("【%s】" % o.get("req_must_mode", "必須")) + "／".join(o["req_must"]),
        "workHours": o["work_hours"] + ("／フレックスタイム制：" + o["flex"] if o["flex"] else ""),
        "jobBenefits": "／".join(o["benefits"]),
    }
    if o.get("req_welcome"): jp["experienceRequirements"] = "【歓迎】" + "／".join(o["req_welcome"])
    if D.get("date_posted"): jp["datePosted"] = D["date_posted"]
    return ('<!-- ===== JOBSOPEN v1：この求人の JobPosting。値は求人票と一致。\n'
            '     datePosted は求人票に掲載開始日の記載がないため入れていない。\n'
            '     Google しごと検索へ出す場合は data/jobs-openings.json の date_posted を設定する。 ===== -->\n'
            '<script type="application/ld+json">%s</script>' % json.dumps(jp, ensure_ascii=False))

def build_detail(o):
    S = rd("renewal/jobs/center-manager/index.html")
    head = S[:S.index('<main id="top">')]
    tail = S[S.index('</main>'):]
    # renewal/jobs/center-manager/ より1階層深い renewal/jobs/openings/<id>/ に置くため、
    # 既存シェルの相対パスに ../ を1つ足す。
    up = lambda t: re.sub(r'(href|src)="\.\./\.\./', r'\1="../../../', t)
    head, tail = up(head), up(tail)

    c = CATS[o["cat"]]
    name = "%s（%s）｜%s" % (o["title"], o["level"], o["place_short"])
    # レベル名が職種名に含まれるときは重ねない
    lv = "" if (not o["level"] or o["level"] in o["title"]) else o["level"] + "・"
    title = "%sの求人｜%s%s%s｜株式会社PAL" % (o["title"], lv, o["pref"], o["city"])
    desc = ("株式会社PALの%s（%s）の募集要項。勤務地は%s。想定年収%s、%s。%s"
            % (o["title"], o["level"], o["location"], o["salary_year"],
               o["employment"].split("（")[0], o["about"][:70]))
    head = re.sub(r'<title>.*?</title>', '<title>%s</title>' % e(title), head, count=1, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % html.escape(desc), head, count=1)
    head = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="%s">' % html.escape(title), head, count=1)
    head = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="%s">' % html.escape(desc), head, count=1)
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "採用情報", "item": "../../../"},
        {"@type": "ListItem", "position": 2, "name": "募集職種", "item": "../../"},
        {"@type": "ListItem", "position": 3, "name": name}]}
    head = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema\.org", "@type": "BreadcrumbList".*?</script>',
                  '<script type="application/ld+json">%s</script>\n%s' % (json.dumps(bc, ensure_ascii=False), jobposting(o)),
                  head, count=1, flags=re.S)

    extra = []
    if o.get("goods"):     extra.append(("取扱商品", e(o["goods"])))
    if o.get("shift"):     extra.append(("勤務シフト", e(o["shift"])))
    if o.get("workstyle"): extra.append(("働き方", e(o["workstyle"])))
    if o.get("team"):      extra.append(("配属先", e(o["team"])))

    mode = o.get("req_must_mode", "必須")
    groups_html = "\n".join(group(c["key"]) for c in D["categories"]
                            if any(o["cat"] == c["key"] for o in OPEN))
    body = f'''<nav class="crumb" aria-label="パンくず"><div class="wrap"><a href="../../../">採用情報</a><a href="../../">募集職種</a><span aria-current="page">{e(name)}</span></div></nav>

{MARK}
<section class="phead">
  <div class="wrap">
    <p class="slabel">Jobs ／ {e(c['name'])}</p>
    <h1 class="ptitle">{e(o['title'])}<br>{e(o['level'])}｜{e(o['place_short'])}</h1>
    <p class="plead">{e(o['pref'])}{e(o['city'])}・{e(o['employment'].split('（')[0])}・想定年収 {e(o['salary_year'])}</p>
  </div>
</section>

<section class="sec sec--tight">
  <div class="wrap">
    <p class="role__h rv"><span class="en">01</span>勤務地</p>
    {spec([("事業所", e(o["office"])), ("所在地", e(o["location"])),
           ("アクセス", "<br>".join(e(a) for a in o["access"]))])}

    <p class="role__h rv" style="margin-top:40px"><span class="en">02</span>給与・想定年収</p>
    {spec([("想定年収", "<b>%s</b>" % e(o["salary_year"])), ("月給", e(o["salary_month"])),
           ("賞与", e(o["bonus"]))])}

    <p class="role__h rv" style="margin-top:40px"><span class="en">03</span>この仕事について</p>
    <p class="jabout rv">{e(o["about"])}</p>
    {spec(extra) if extra else ""}

    <p class="role__h rv" style="margin-top:40px"><span class="en">04</span>主な仕事内容</p>
    {li(o["duties"])}
    <p class="note">※ 職種としての仕事の全体像は<a class="textlink textlink--sm" href="{e(c["work_anchor"]).replace("../", "../../../")}">仕事を知る</a>をご覧ください。</p>

    <p class="role__h rv" style="margin-top:40px"><span class="en">05</span>応募条件</p>
    <p class="cmsub">{e(mode)}</p>
    {li(o["req_must"])}
    {('<p class="cmsub" style="margin-top:22px">歓迎する経験</p>' + li(o["req_welcome"])) if o.get("req_welcome") else ""}
    {('<p class="cmsub" style="margin-top:22px">資格</p>' + li([o["license"]])) if o.get("license") else ""}
    {('<p class="cmsub" style="margin-top:22px">求める人物像</p><p class="jabout">' + e(o["req_person"]) + "</p>") if o.get("req_person") else ""}

    <p class="role__h rv" style="margin-top:40px"><span class="en">06</span>勤務条件</p>
    {spec([("雇用形態", e(o["employment"])), ("試用期間", e(o["probation"])),
           ("勤務時間", e(o["work_hours"])), ("フレックスタイム制", e(o["flex"])),
           ("残業", e(o["overtime"])), ("休日・休暇", e(o["holidays"])),
           ("有給休暇", e(o["paid_leave"])), ("その他の休暇", e(o["holiday_other"])),
           ("転勤", e(o["relocation"]))])}

    <p class="role__h rv" style="margin-top:40px"><span class="en">07</span>待遇・福利厚生</p>
    {li(o["benefits"])}
    {spec([("退職金", e(o["retirement"])), ("寮・社宅", e(o["dormitory"]))])}

    <p class="role__h rv" style="margin-top:40px"><span class="en">08</span>選考</p>
    {spec([("採用人数", e(o["hires"])), ("面接回数", e(o["interviews"])),
           ("筆記試験", e(o["written_test"])),
           ("選考の流れ", 'エントリー→会社説明／カジュアル面談→選考面接→最終面接→内定（Web面接可）<br><a class="textlink textlink--sm" href="../../#selection">選考について</a>')])}

    <p class="role__h rv" style="margin-top:40px"><span class="en">09</span>この仕事をしている社員の話</p>
    <p class="jabout rv">{e(c["people_label"])}を掲載しています。社員本人の経験とキャリアを紹介したもので、この求人の募集条件とは別の内容です。</p>
    <p class="cmrel rv" style="margin-top:16px">
      <a class="btn btn--ghost" href="{e(c["people"]).replace("../", "../../../")}">この仕事をしている社員の話を見る<span class="btn__ico" aria-hidden="true">▶</span></a>
      <a class="btn btn--ghost" href="../../">ほかの募集中の求人を見る<span class="btn__ico" aria-hidden="true">▶</span></a>
    </p>
  </div>
</section>

<section class="entry">
  <div class="entry__media"><img src="../../../../assets/hero-bg.jpg" alt="" width="2752" height="1536" loading="lazy" aria-hidden="true"></div>
  <div class="entry__inner wrap--narrow">
    <p class="entry__label en">NEXT STEP</p>
    <h2>この求人に<br>応募する。</h2>
    <p>選考の前に、会社説明やカジュアル面談だけの参加も歓迎しています。</p>
    <div class="entry__ctas">
      <a class="btn btn--red btn--lg" href="../../../entry/">この求人に応募する<span class="btn__ico" aria-hidden="true">▶</span></a>
    </div>
    <p class="entry__sec"><a href="../../">ほかの募集中の求人を見る</a></p>
  </div>
</section>
'''
    wr("renewal/jobs/openings/%s/index.html" % o["id"], head + '<main id="top">\n' + body + tail)

if __name__ == "__main__":
    build_index()
    for o in OPEN: build_detail(o)
    print("一覧 1件 ／ 求人詳細 %d件 を生成（非公開 %d件）"
          % (len(OPEN), len(D["openings"]) - len(OPEN)))
