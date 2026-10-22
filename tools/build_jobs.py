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
import json, os, re, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import applycta   # ===== APPLY v1：応募ボタンは応募先データから作る（唯一の持ち主）

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f: return f.read()
def wr(p, s):
    os.makedirs(os.path.join(ROOT, os.path.dirname(p)), exist_ok=True)
    with open(os.path.join(ROOT, p), "w", encoding="utf-8") as f: f.write(s)
def e(x): return html.escape(str(x), quote=False)

D    = json.loads(rd("data/jobs-openings.json"))
CATS = {c["key"]: c for c in D["categories"]}
# ===== HRJOB v1：status は open（募集中）／upcoming（募集予定）／hold（非公開）の3種類。
# 一覧とフィルターには open と upcoming を出す。JobPosting は open だけに付ける。
OPEN = [o for o in D["openings"] if o["status"] in ("open", "upcoming")]
# ===== APPLY v1：応募先URLが未設定の求人があるあいだだけ、一覧に注記を出す。
# 応募先を入れてビルドし直すと、この行は自動的に消える。
APPLY_NOTE = ('<p class="jfil__apply">※ 応募先URLの設定前のため、応募ボタンは押せない状態で'
              '表示しています。この採用サイトは公開前の確認用で、応募の受け付けはまだ開始していません。</p>'
              if applycta.missing() else "")
PREF_SLUGS = D.get("pref_slugs", {})
def pref_slug(name):
    """表示名ではなく内部値で絞り込むためのスラッグ。未登録の都道府県も必ず値を持つ。"""
    return PREF_SLUGS.get(name) or ("pref-" + str(abs(hash(name)) % 100000))
PREFS = []
for o in OPEN:
    if o["pref"] and o["pref"] not in PREFS: PREFS.append(o["pref"])

# ===== JOBDETAIL v2 =====
# 求人詳細の共通テンプレート。"v1" は 01勤務地〜09社員の話の9セクション構成、
# "v2" は視認性を上げた6セクション構成（ヘッダー＋主要条件サマリー）。
# 比較プレビューの承認後に LAYOUT = "v2" にすると、全求人詳細が v2 で再生成される。
# 個別HTMLは手で直さない。求人データ（data/jobs-openings.json）は変更しない。
# ===== FLOW4 v1：選考の流れ。renewal/jobs/#selection・renewal/entry/・FAQ と同じ内容にそろえている。
# ===== DUTYCARD v1：「担当する業務」を箇条書きのままにする求人ID。
# ここに入っていない求人はカード型（.jdcards）で出力する。
DUTIES_LIST_ONLY = {"system-engineer"}

FLOW_TEXT = "応募 → 1次面接（部門責任者・原則WEB面接） → 2次面接（取締役・対面面接が基本） → 内定・オファー面談"

LAYOUT = "v2"   # 2026-10-21 承認：比較プレビューを全求人詳細へ展開

# 出力先の階層ごとの相対パス。
#   3 = renewal/jobs/openings/<id>/   （正式な求人詳細）
#   2 = renewal/jobs-detail-redesign-preview/ （比較プレビュー）
# shell は renewal/jobs/logistics-operation/（階層3）のheadとfooterを流用するための補正。
PATHS = {
    3: {"shell": lambda t: re.sub(r'(href|src)="\.\./\.\./', r'\1="../../../', t),
        "rn": "../../../", "jobs": "../../", "assets": "../../../../"},
    2: {"shell": lambda t: re.sub(r'(href|src)="\.\./\.\./', r'\1="../', t),
        "rn": "../", "jobs": "../jobs/", "assets": "../../"},
}

# ===== JOBSOPEN v1：給与の注記は求人データから組み立てる。
# 「いずれも固定残業代を含む」は、固定残業代のない求人（DTS／運送部のドライバー）が
# 一覧に入った時点で事実と合わなくなるため、該当件数で文面を切り替える。
_FIXOT = [o for o in OPEN
          if "固定残業" in (o.get("salary_month", "") or "") + (o.get("overtime", "") or "")]
if not _FIXOT:
    SALARY_NOTE = "※ 給与の内訳は各求人の募集要項に掲載しています。"
elif len(_FIXOT) == len(OPEN):
    SALARY_NOTE = "※ 給与はいずれも固定残業代を含む金額です。内訳は各求人の募集要項に掲載しています。"
else:
    SALARY_NOTE = "※ 給与に固定残業代を含む求人があります。固定残業代の有無と内訳は、各求人の募集要項に掲載しています。"

MARK = ("<!-- ===== JOBSOPEN v1：リクナビHRTechで承認済みの求人票9件（2026-10-20 時点）"
        "をもとに、\n     tools/build_jobs.py が data/jobs-openings.json から生成している。"
        "手で編集せず、\n     JSON を直してからビルドし直すこと。\n"
        "     ・条件・数値・勤務地・応募資格は、すべて求人票の記載と一致させている。\n"
        "     ・求人票にない項目（年間休日の内訳、転勤の有無が未記載のもの等）は補完していない。\n"
        "     ・求人票がない職種は『募集中』にしていない。\n"
        "     ・求人票にある『最先端』『市場価値が飛躍的に高まる』などの訴求表現は採用していない。 ===== -->")

# ===== SEOFIX v1：見出し階層を h1（ページ見出し）→ h2（職種グループ）→ h3（求人カード）に
# そろえた。従来は h1 → h3 → h4 と1段飛んでいた。CSSは .jgroup__h / .jcard__n の
# クラス指定のため、見た目は変わらない。
# ------------------------------------------------------------------ カード
# ===== JOBTITLE v1 =====
# 求人名と役職ラベルを必ず別要素で出す。
# ・見出し(<h1>/<h3>)には職種名だけを入れる。span を見出しの中に入れると、
#   表示は改行されていても、テキストとして取り出したときに
#   「4tルート配送ドライバーDTS / 運送部」のように結合して読まれる。
# ・level が title に含まれている求人（物流センター責任者候補＋責任者候補）は
#   役職を繰り返さず、勤務地だけを出す。職種名そのものは変更しない。
def sublabel(o):
    """求人名の下に出す「役職｜拠点」。重複する役職は落とす。"""
    lv, place = o.get("level", ""), o.get("place_short", "")
    if lv and lv in o["title"]:
        lv = ""
    return "｜".join(x for x in (lv, place) if x)


def card(o):
    c = CATS[o["cat"]]
    # 既存の正式募集要項がある求人（detail_url）は、そのURLを再利用する。
    # 新しい重複ページは作らない。
    detail = e(o["detail_url"]) if o.get("detail_url") else "openings/%s/" % e(o["id"])
    # ===== HRJOB v1：募集予定の求人は、正式な条件が無いため勤務地・給与・雇用形態の表を出さず、
    # 仕事を一言で示すリード文に置き換える。「未定」は並べない。
    if o.get("upcoming"):
        work = e(c["work_anchor"])   # 一覧は renewal/jobs/ 配下なので ../ のまま使う
        body = ('<h3 class="jcard__n">%s</h3>\n        <p class="jcard__lead">%s</p>'
                % (e(o["title"]), e(o["lead"])))
        foot = ('<p class="jcard__foot"><span class="jchip jchip--soon">募集予定</span>\n'
                '          <a class="jcard__cta" href="%s">募集要項を見る<i aria-hidden="true">&#8594;</i></a></p>\n'
                '        <p class="jcard__sub"><a class="textlink textlink--sm" href="%s">仕事内容を見る</a></p>'
                % (detail, work))
        loc = ""
    else:
        sub = sublabel(o)
        lv = ('\n        <p class="jcard__lv">%s</p>' % e(sub)) if sub else ""
        body = ('<h3 class="jcard__n">%s</h3>%s\n'
                '        <dl class="jcard__dl">\n'
                '          <dt>勤務地</dt><dd>%s%s</dd>\n'
                '          <dt>%s</dt><dd><b>%s</b></dd>\n'
                '          <dt>雇用形態</dt><dd>%s</dd>\n'
                '        </dl>'
                % (e(o["title"]), lv, e(o["pref"]), e(o["city"]),
                   e(o.get("salary_label", "想定年収")), e(o["salary_year"]),
                   e(o["employment"].split("（")[0])))
        # ===== APPLY v1：募集中の求人にだけ応募ボタンを置く。
        # 募集予定（upcoming）は上の分岐なので、ここには来ない。
        foot = ('<p class="jcard__foot"><span class="jchip">募集中</span>\n'
                '          <a class="jcard__cta" href="%s">募集要項を見る<i aria-hidden="true">&#8594;</i></a></p>\n'
                % detail) + applycta.card_button(applycta.url_of(D, o))
        loc = e(pref_slug(o["pref"]))
    return f'''      <li class="jcard" data-job-category="{e(o['cat'])}" data-location="{loc}">
        <p class="jcard__cat">{e(c['name'])}</p>
        {body}
        {foot}
      </li>'''

def group(key):
    c = CATS[key]
    hub = ('<a class="textlink textlink--sm" href="%s">%s</a>を見る。' % (e(c["hub"]), e(c["hub_label"]))) if c.get("hub") else ""
    items = [o for o in OPEN if o["cat"] == key]
    cards = "\n".join(card(o) for o in items)
    return f'''    <section class="jgroup" id="job-{e(key)}" data-group="{e(key)}">
      <h2 class="jgroup__h"><span class="jgroup__n">{e(c['name'])}</span><span class="jgroup__c en" data-total="{len(items)}">{len(items)} {"POSITION" if len(items)==1 else "POSITIONS"}</span></h2>
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
      {APPLY_NOTE}
    </div>
    <p class="jfil__none" id="jobnone" hidden>現在、この条件で募集中の求人はありません。</p>'''

# ------------------------------------------------------------------ 一覧
def build_index():
    S = rd("renewal/jobs/index.html")
    head = S[:S.index('<main id="top">')]
    tail = S[S.index('<section class="sec sec--navy sec--tight" id="selection">'):]
    # ===== JOBSOPEN v2：このスクリプトは自分の出力を土台にして組み直すため、
    # 前回追記した絞り込みJSを先に取り除く。取り除かないと実行のたびに積み上がる
    # （HEAD 時点で11個に増えていた）。
    tail = re.sub(r'<!-- ===== JOBSOPEN v2：.*?</script>\n?', '', tail, flags=re.S)

    title = "募集中の求人一覧｜物流センター運営・FDE・システム開発・営業｜株式会社PAL 採用"
    desc = ("株式会社PALが現在募集している求人の一覧です。物流センター運営（千葉・船橋／神奈川・厚木／"
            "広島・東広島／兵庫・須磨）、FDE（大阪本社）、"
            "システム / プロダクト開発（大阪本社）、エンゲージメント・新規営業と法人営業（人材派遣・大阪本社）、"
            "勤務地・給与・雇用形態・勤務時間・休日・応募条件を掲載しています。")
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
    <p class="note" style="margin-top:28px">{SALARY_NOTE}</p>
  </div>
</section>

<section class="sec sec--soft sec--tight" id="others">
  <div class="wrap">
    <div class="shead rv" style="margin-bottom:22px">
      <p class="slabel">Recruitment status</p>
      <h2 class="stitle" style="font-size:clamp(22px,2.6vw,30px)">現在の募集状況について</h2>
      <p class="slead">以下の職種は、現在募集中の求人一覧には掲載していません。募集状況は職種ごとにご確認ください。</p>
    </div>
    <!-- ===== RSTAT v1：3職種の表示をそろえた。コーポレートだけにあった社員インタビュー導線は、
         このセクションが募集状況を伝える場所であるため外している（PEOPLE・WORKは変更なし）。
         id は人を知るなどからのアンカーリンクで使われているため変えていない。 ===== -->
    <ul class="rstat rv">
      <li id="job-marketing"><span class="rstat__n"><b>Marketing / Content</b><span class="rstat__ja">マーケティング・コンテンツ制作</span></span><span class="rstat__s">募集条件を確認中</span></li>
      <li id="job-clean"><span class="rstat__n"><b>Cleanliness</b><span class="rstat__ja">クレンリネス</span></span><span class="rstat__s">現在募集していません</span></li>
      <!-- ===== JOBANCHOR v1：Corporate（人事）は HRJOB v1 で「今、募集している仕事」の
           人事 / HR グループへ移ったため、この節から削除。sync_role_status.py も
           出力から外しているが、公開しない文言をソースに残さないため行ごと削除する。
           PEOPLE からのリンクは #job-hr に付け替え済み。 ===== -->
    </ul>
    <p class="note rv">※ 募集状況は変更になる場合があります。最新の募集情報は、上部の<a class="textlink textlink--sm" href="#joblist">今、募集している仕事</a>をご確認ください。仕事の内容は<a class="textlink textlink--sm" href="../work/">仕事を知る</a>でご覧いただけます。</p>
    <p class="rv" style="margin-top:24px"><a class="btn btn--ghost" href="../entry/">応募・選考について<span class="btn__ico" aria-hidden="true">▶</span></a></p>
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
    # datePosted は求人票に記載がないため、値があるときだけ出力する。
    # 本番公開時に、その求人を本番サイトへ掲載した実日付を入れる。
    dp = o.get("date_posted") or D.get("date_posted")
    if dp: jp["datePosted"] = dp
    return ('<!-- ===== JOBSOPEN v1：この求人の JobPosting。値は求人票と一致。\n'
            '     datePosted は求人票に掲載開始日の記載がないため入れていない。\n'
            '     Google しごと検索へ出す場合は data/jobs-openings.json の date_posted を設定する。 ===== -->\n'
            '<script type="application/ld+json">%s</script>' % json.dumps(jp, ensure_ascii=False))

# ------------------------------------------------------------------ 求人詳細 v2
def spec2(rows):
    """勤務条件などの2カラム定義リスト。値が空の項目は行ごと出さない。"""
    r = [(k, v) for k, v in rows if v]
    if not r: return ""
    return ('<div class="jdspec"><dl>'
            + "".join('<dt>%s</dt><dd>%s</dd>' % (e(k), v) for k, v in r)
            + '</dl></div>')

def li2(items, cls="jdlist"):
    return '<ul class="%s">%s</ul>' % (cls, "".join('<li>%s</li>' % e(x) for x in items))

def jdsum(o):
    """求人ヘッダーの主要条件サマリー。原則4項目。
    求人票に記載のない項目（想定年収・年間休日など）は作らず、値が空なら項目ごと出さない。"""
    items = [
        (o.get("salary_label", "想定年収"), e(o["salary_year"]), True),
        ("勤務地", e(o["pref"]) + e(o["city"])
                 + ('<span class="jdsum__s">%s</span>' % e(o["office"]) if o.get("office") else ""), False),
        ("休日", e(o["holidays"]), False),
        ("雇用形態", e(o["employment"].split("（")[0]), False),
    ]
    cells = "".join(
        '<div class="jdsum__i"><dt>%s</dt><dd class="jdsum__v%s">%s</dd></div>'
        % (e(k), " jdsum__v--big" if big else "", v)
        for k, v, big in items if v)
    return '<dl class="jdsum rv">%s</dl>' % cells

def detail_body_v2(o, P, intro=""):
    c = CATS[o["cat"]]
    name = "%s（%s）｜%s" % (o["title"], o["level"], o["place_short"])
    mode = o.get("req_must_mode", "必須")
    extra = [(k, e(o[f])) for k, f in
             (("取扱商品", "goods"), ("働き方", "workstyle"), ("配属先", "team")) if o.get(f)]
    welcome = (('<p class="jdsub">歓迎する経験</p><p class="jdtag jdtag--w">歓迎</p>'
                + li2(o["req_welcome"])) if o.get("req_welcome") else "")
    lic = ('<p class="jdsub">資格</p>' + li2([o["license"]])) if o.get("license") else ""
    person = (('<p class="jdsub">求める人物像</p><p class="jdtext">' + e(o["req_person"]) + '</p>')
              if o.get("req_person") else "")
    # ===== FLOW4 v1：実際の面接体制（1次＝部門責任者・原則WEB／2次＝取締役・対面が基本）に合わせた。
    flow = (FLOW_TEXT
            + '<br><a class="textlink textlink--sm" href="' + P["jobs"] + '#selection">選考について</a>')
    salary = spec2([(o.get("salary_label", "想定年収"), "<b>%s</b>" % e(o["salary_year"])),
                    ("月給", e(o.get("salary_month", ""))), ("賞与", e(o.get("bonus", "")))])
    hours = spec2([("雇用形態", e(o["employment"])), ("試用期間", e(o["probation"])),
                   ("勤務シフト", e(o.get("shift", ""))),
                   ("勤務時間", e(o["work_hours"])), ("フレックスタイム制", e(o["flex"])),
                   ("残業", e(o["overtime"])), ("休日・休暇", e(o["holidays"])),
                   ("有給休暇", e(o["paid_leave"])), ("その他の休暇", e(o["holiday_other"]))])
    place = spec2([("事業所", e(o["office"])), ("所在地", e(o["location"])),
                   ("アクセス", "<br>".join(e(a) for a in o["access"])),
                   ("転勤", e(o["relocation"]))])
    # ===== HIRES-OFF v1：採用人数は求職者向けページに表示しない（応募の判断材料として
    # 誤解を招くため）。データは data/jobs-openings.json の hires に残している。
    # 再表示するときは下の行に ("採用人数", e(o["hires"])) を戻す。
    selection = spec2([("面接回数", e(o["interviews"])),
                       ("筆記試験", e(o["written_test"])), ("選考の流れ", flow)])
    # ===== DUTYCARD v1：担当する業務はカード型（.jdcards）。
    # システムエンジニアだけは従来の箇条書き（.jdlist）のままにする。
    # 文章・順番・項目数はどちらも求人データのままで、表示方法だけが違う。
    duties_cls = "jdlist" if o["id"] in DUTIES_LIST_ONLY else "jdcards"
    work_url = e(c["work_anchor"]).replace("../", P["rn"])
    people_url = e(c["people"]).replace("../", P["rn"])
    return f"""<nav class="crumb" aria-label="パンくず"><div class="wrap"><a href="{P["rn"]}">採用情報</a><a href="{P["jobs"]}">募集職種</a><span aria-current="page">{e(name)}</span></div></nav>

{MARK}
{intro}
<!-- ===== JOBDETAIL v2：01 求人ヘッダー（職種名＋主要条件サマリー）
     サマリーは給与・勤務地・休日・雇用形態の原則4項目。求人票に記載のない項目は
     作らず、値が空なら項目ごと出さない（jdsum）。 ===== -->
<section class="jdh">
  <div class="wrap">
    <p class="slabel">Jobs ／ {e(c['name'])}</p>
    <h1 class="jdh__t">{e(o['title'])}</h1>
    <p class="jdh__lv">{e(sublabel(o))}</p>
    {jdsum(o)}
  </div>
</section>

<section class="sec sec--tight">
  <div class="wrap">

    <!-- ===== JOBDETAIL v2：02 仕事内容 ===== -->
    <section class="jdsec">
      <h2 class="jdsec__h"><span class="en">02</span>どんな仕事をするのか</h2>
      <p class="jdtext rv">{e(o["about"])}</p>
      <p class="jdsub">担当する業務</p>
      {li2(o["duties"], duties_cls)}
      {spec2(extra)}
      <p class="note">※ 職種としての仕事の全体像は<a class="textlink textlink--sm" href="{work_url}">仕事を知る</a>をご覧ください。</p>
    </section>

    <!-- ===== JOBDETAIL v2：03 応募条件
         「必須」「いずれか必須」「歓迎」の区別は求人票のままで、まとめていない。 ===== -->
    <section class="jdsec">
      <h2 class="jdsec__h"><span class="en">03</span>応募条件</h2>
      <p class="jdtag">{e(mode)}</p>
      {li2(o["req_must"])}
      {welcome}
      {lic}
      {person}
    </section>

    <!-- ===== JOBDETAIL v2：04 勤務条件（給与／勤務時間・休日／勤務地） ===== -->
    <section class="jdsec">
      <h2 class="jdsec__h"><span class="en">04</span>勤務条件</h2>
      <p class="jdsub jdsub--first">給与</p>
      {salary}
      <p class="jdsub">勤務時間・休日</p>
      {hours}
      <p class="jdsub">勤務地</p>
      {place}
    </section>

    <!-- ===== JOBDETAIL v2：05 待遇・福利厚生 ===== -->
    <section class="jdsec">
      <h2 class="jdsec__h"><span class="en">05</span>待遇・福利厚生</h2>
      {li2(o["benefits"], "jdben")}
      {spec2([("退職金", e(o["retirement"])), ("寮・社宅", e(o["dormitory"]))])}
    </section>

    <!-- ===== JOBDETAIL v2：06 選考・関連導線 ===== -->
    <section class="jdsec">
      <h2 class="jdsec__h"><span class="en">06</span>選考・関連情報</h2>
      {selection}
      <p class="jdsub">この仕事をしている社員の話</p>
      <p class="jdtext">{e(c["people_label"])}を掲載しています。社員本人の経験とキャリアを紹介したもので、この求人の募集条件とは別の内容です。</p>
      <p class="jdrel">
        <a class="btn btn--ghost" href="{people_url}">この仕事をしている社員の話を見る<span class="btn__ico" aria-hidden="true">▶</span></a>
        <a class="btn btn--ghost" href="{P["jobs"]}">ほかの募集中の求人を見る<span class="btn__ico" aria-hidden="true">▶</span></a>
      </p>
    </section>

  </div>
</section>

<section class="entry">
  <div class="entry__media"><img src="{P["assets"]}assets/hero-bg.jpg" alt="" width="2752" height="1536" loading="lazy" aria-hidden="true"></div>
  <div class="entry__inner wrap--narrow">
    <p class="entry__label en">NEXT STEP</p>
    <h2>この求人に<br>応募する。</h2>
    <p>募集中の職種と条件は募集要項に掲載しています。選考時のWeb面接にも対応しています。</p>
{applycta.detail_block(o["id"], applycta.url_of(D, o), "    ")}
    <p class="entry__sec"><a href="{P["jobs"]}">ほかの募集中の求人を見る</a></p>
  </div>
</section>
"""

# ------------------------------------------------------------------ 募集予定の求人詳細
def detail_body_upcoming(o, P, intro=""):
    """===== HRJOB v1：正式求人票が確定していない「募集予定」の求人詳細。
    募集要項（給与・勤務地・勤務時間・休日・福利厚生・応募資格・選考条件）は
    値を持たないため、ブロックごと出さずに一文で案内する。「未定」を並べない。
    JobPosting は出さない（build_detail 側で upcoming のときは出力しない）。
    求人票が確定したら data/jobs-openings.json の upcoming を false にして
    各項目を埋めれば、通常の v2 レイアウトに切り替わる。"""
    c = CATS[o["cat"]]
    partners = "".join('<li>%s</li>' % e(x) for x in o.get("partners", []))
    work_url = e(c["work_anchor"]).replace("../", P["rn"])
    people_url = e(c["people"]).replace("../", P["rn"])
    return f"""<nav class="crumb" aria-label="パンくず"><div class="wrap"><a href="{P["rn"]}">採用情報</a><a href="{P["jobs"]}">募集職種</a><span aria-current="page">{e(o['title'])}</span></div></nav>

{MARK}
{intro}
<!-- ===== HRJOB v1：01 求人ヘッダー。正式求人票が未確定のため主要条件サマリーは出さず、
     「募集予定」であることだけを示す。 ===== -->
<section class="jdh">
  <div class="wrap">
    <p class="slabel">Jobs ／ {e(c['name'])}</p>
    <h1 class="jdh__t">{e(o['title'])}</h1>
    <p class="jdh__lv">{e(o['lead'])}</p>
    <p class="jdh__st"><span class="jchip jchip--soon">募集予定</span></p>
  </div>
</section>

<section class="sec sec--tight">
  <div class="wrap">

    <section class="jdsec">
      <h2 class="jdsec__h"><span class="en">02</span>この仕事について</h2>
      <p class="jdtext rv">{e(o["about"])}</p>
    </section>

    <section class="jdsec">
      <h2 class="jdsec__h"><span class="en">03</span>主な仕事内容</h2>
      {li2(o["duties"], "jdcards")}
    </section>

    <section class="jdsec">
      <h2 class="jdsec__h"><span class="en">04</span>この仕事の特徴</h2>
      <p class="jdtext rv">{e(o["feature"])}</p>
      <p class="jdsub">関わる相手</p>
      <ul class="jdben">{partners}</ul>
      <p class="note">※ 職種としての仕事の全体像は<a class="textlink textlink--sm" href="{work_url}">仕事を知る</a>をご覧ください。</p>
    </section>

    <section class="jdsec">
      <h2 class="jdsec__h"><span class="en">05</span>募集要項</h2>
      <p class="jdtext rv">雇用形態・勤務地・給与・勤務時間・休日・福利厚生・応募資格などの募集要項は、正式な募集開始にあわせて掲載します。</p>
    </section>

    <section class="jdsec">
      <h2 class="jdsec__h"><span class="en">06</span>選考・関連情報</h2>
      <p class="jdtext rv">選考は、ほかの職種と同じ流れです。応募いただいたあと、1次面接（部門責任者・原則WEB面接）、2次面接（取締役・対面面接が基本）を経て内定となります。内定後は必要に応じてオファー面談を実施しています。<br><a class="textlink textlink--sm" href="{P["jobs"]}#selection">選考について</a></p>
      <p class="jdrel">
        <a class="btn btn--ghost" href="{work_url}">人事を含むコーポレートの仕事内容を見る<span class="btn__ico" aria-hidden="true">▶</span></a>
        <a class="btn btn--ghost" href="{people_url}">コーポレートで働く社員の話を見る<span class="btn__ico" aria-hidden="true">▶</span></a>
        <a class="btn btn--ghost" href="{P["jobs"]}">ほかの募集中の求人を見る<span class="btn__ico" aria-hidden="true">▶</span></a>
      </p>
    </section>

  </div>
</section>
"""

def build_detail(o, layout=None, depth=3, outpath=None, intro=""):
    layout = layout or LAYOUT
    P = PATHS[depth]
    S = rd("renewal/jobs/logistics-operation/index.html")
    head = S[:S.index('<main id="top">')]
    tail = S[S.index('</main>'):]
    # 既存シェル（renewal/jobs/logistics-operation/）と出力先の階層差を相対パスで補正する。
    head, tail = P["shell"](head), P["shell"](tail)

    c = CATS[o["cat"]]
    if o.get("upcoming"):
        # ===== HRJOB v1：募集予定の求人は、職種名・レベル・勤務地・給与が空のため、
        # 条件を含まない title / description にする。「｜｜」のような空欄を出さない。
        name = o["title"]
        title = "%sの仕事内容｜募集予定｜株式会社PAL 採用" % o["title"]
        desc = ("株式会社PALの%s（募集予定）の仕事内容。%s募集要項は正式な募集開始にあわせて掲載します。"
                % (o["title"], o["about"]))
    else:
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
    # ===== ENTRY-CTA / NOINDEX：求人詳細は公開前の確認用のため常に検索対象外にする。
    # リンクはたどらせたいので nofollow ではなく follow。求人が増えても自動で付く。
    head = re.sub(r'<meta name="robots" content="[^"]*">',
                  '<meta name="robots" content="noindex,follow">', head, count=1)
    if 'name="robots"' not in head:
        head = head.replace('<link rel="canonical" href="./">',
                            '<link rel="canonical" href="./">\n<meta name="robots" content="noindex,follow">', 1)
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "採用情報", "item": P["rn"]},
        {"@type": "ListItem", "position": 2, "name": "募集職種", "item": P["jobs"]},
        {"@type": "ListItem", "position": 3, "name": name}]}
    head = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema\.org", "@type": "BreadcrumbList".*?</script>',
                  '<script type="application/ld+json">%s</script>%s' % (json.dumps(bc, ensure_ascii=False),
                      # ===== HRJOB v1：募集予定の求人には JobPosting を付けない（給与・勤務条件・
                      # 掲載日・応募先が未確定のため）。正式募集時に upcoming を外せば出るようになる。
                      '' if o.get("upcoming") else '\n' + jobposting(o)),
                  head, count=1, flags=re.S)

    extra = []
    if o.get("goods"):     extra.append(("取扱商品", e(o["goods"])))
    if o.get("shift"):     extra.append(("勤務シフト", e(o["shift"])))
    if o.get("workstyle"): extra.append(("働き方", e(o["workstyle"])))
    if o.get("team"):      extra.append(("配属先", e(o["team"])))

    mode = o.get("req_must_mode", "必須")
    groups_html = "\n".join(group(c["key"]) for c in D["categories"]
                            if any(o["cat"] == c["key"] for o in OPEN))
    body = f'''<nav class="crumb" aria-label="パンくず"><div class="wrap"><a href="{P["rn"]}">採用情報</a><a href="{P["jobs"]}">募集職種</a><span aria-current="page">{e(name)}</span></div></nav>

{MARK}
<section class="phead">
  <div class="wrap">
    <p class="slabel">Jobs ／ {e(c['name'])}</p>
    <h1 class="ptitle">{e(o['title'])}</h1>
    <p class="jdh__lv">{e(sublabel(o))}</p>
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
    <p class="note">※ 職種としての仕事の全体像は<a class="textlink textlink--sm" href="{e(c["work_anchor"]).replace("../", P["rn"])}">仕事を知る</a>をご覧ください。</p>

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
    {spec([("面接回数", e(o["interviews"])),
           ("筆記試験", e(o["written_test"])),
           ("選考の流れ", FLOW_TEXT + '<br><a class="textlink textlink--sm" href="' + P["jobs"] + '#selection">選考について</a>')])}

    <p class="role__h rv" style="margin-top:40px"><span class="en">09</span>この仕事をしている社員の話</p>
    <p class="jabout rv">{e(c["people_label"])}を掲載しています。社員本人の経験とキャリアを紹介したもので、この求人の募集条件とは別の内容です。</p>
    <p class="cmrel rv" style="margin-top:16px">
      <a class="btn btn--ghost" href="{e(c["people"]).replace("../", P["rn"])}">この仕事をしている社員の話を見る<span class="btn__ico" aria-hidden="true">▶</span></a>
      <a class="btn btn--ghost" href="{P["jobs"]}">ほかの募集中の求人を見る<span class="btn__ico" aria-hidden="true">▶</span></a>
    </p>
  </div>
</section>

<section class="entry">
  <div class="entry__media"><img src="{P["assets"]}assets/hero-bg.jpg" alt="" width="2752" height="1536" loading="lazy" aria-hidden="true"></div>
  <div class="entry__inner wrap--narrow">
    <p class="entry__label en">NEXT STEP</p>
    <h2>この求人に<br>応募する。</h2>
    <p>募集中の職種と条件は募集要項に掲載しています。選考時のWeb面接にも対応しています。</p>
{applycta.detail_block(o["id"], applycta.url_of(D, o), "    ")}
    <p class="entry__sec"><a href="{P["jobs"]}">ほかの募集中の求人を見る</a></p>
  </div>
</section>
'''
    if o.get("upcoming"):
        body = detail_body_upcoming(o, P, intro)
    elif layout == "v2":
        body = detail_body_v2(o, P, intro)
    wr(outpath or ("renewal/jobs/openings/%s/index.html" % o["id"]),
       head + '<main id="top">\n' + body + tail)

if __name__ == "__main__":
    build_index()
    made = 0
    for o in OPEN:
        if o.get("generate_detail") is False:
            continue          # 既存の募集要項ページを再利用する求人（例：renewal/jobs/dts/）
        build_detail(o); made += 1
    print("一覧 1件 ／ 求人詳細 %d件 を生成（既存ページを再利用 %d件 ／ 非公開 %d件）"
          % (made, len(OPEN) - made, len(D["openings"]) - len(OPEN)))
