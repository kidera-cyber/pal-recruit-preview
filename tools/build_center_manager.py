# -*- coding: utf-8 -*-
"""
===== CMJOB v1 =====
センター長・センター長候補の3階層ページを data/center-manager-jobs.json から組み立てる。

  LEVEL 01  renewal/jobs-preview/                            （JOBS一覧の導線修正プレビュー）
  LEVEL 02  renewal/jobs/center-manager-preview/             （共通紹介）
  LEVEL 03  renewal/jobs/center-manager-template-preview/    （拠点別募集要項テンプレート）

拠点を追加・変更するときは JSON を編集してこのスクリプトを実行するだけでよい。
出力は静的HTMLなので、JavaScriptが無効でも求人情報はすべて読める。

  python3 -I tools/build_center_manager.py
"""
import json, os, re, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f: return f.read()
def wr(p, s):
    os.makedirs(os.path.join(ROOT, os.path.dirname(p)), exist_ok=True)
    with open(os.path.join(ROOT, p), "w", encoding="utf-8") as f: f.write(s)
def e(x): return html.escape(str(x), quote=False)

DATA = json.loads(rd("data/center-manager-jobs.json"))
POS  = DATA["positions"]
CONFIRMED = [p for p in POS if p["status"] == "confirmed"]
DEMO      = [p for p in POS if p["status"] == "demo"]
VISIBLE   = [p for p in POS if p["status"] in ("confirmed", "tbd", "demo")]

STATUS_LABEL = {"confirmed": ("募集中", "cmchip--open"),
                "tbd":       ("確認中", "cmchip--tbd"),
                "closed":    ("募集終了", "cmchip--closed"),
                "demo":      ("デモデータ", "cmchip--demo")}

# ------------------------------------------------------------------
# 共通シェル（ヘッダー・フッター）は既存ページから取り出して使い回す
# ------------------------------------------------------------------
def shell(src):
    s = rd(src)
    head = s[:s.index('<main id="top">')]
    foot = s[s.index('</main>'):]
    return head, foot

def set_head(head, title, desc, crumb_name, crumb_items, noindex=True):
    head = re.sub(r'<title>.*?</title>', '<title>%s</title>' % e(title), head, count=1, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">',
                  '<meta name="description" content="%s">' % html.escape(desc), head, count=1)
    head = re.sub(r'<meta property="og:title" content="[^"]*">',
                  '<meta property="og:title" content="%s">' % html.escape(title), head, count=1)
    head = re.sub(r'<meta property="og:description" content="[^"]*">',
                  '<meta property="og:description" content="%s">' % html.escape(desc), head, count=1)
    if noindex:
        head = re.sub(r'<!-- SEO-BASE v1[^>]*-->\n<link rel="canonical" href="\./">\n',
                      '<!-- 比較プレビュー：canonicalは置かず、noindex,nofollow を指定 -->\n'
                      '<meta name="robots" content="noindex,nofollow">\n', head, count=1)
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList",
          "itemListElement": crumb_items}
    head = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema\.org", "@type": "BreadcrumbList".*?</script>',
                  '<script type="application/ld+json">%s</script>' % json.dumps(bc, ensure_ascii=False),
                  head, count=1, flags=re.S)
    return head

DEMO_BANNER = '''<!-- ===== CMJOB v1：デモデータの明示（STEP 15）。
     正式な拠点データが確定するまで、レイアウト確認用の仮データを表示している。 ===== -->
<div class="cmdemo" role="note">
  <p class="cmdemo__h">このページの拠点情報は、レイアウト確認用の<b>デモデータ</b>です。</p>
  <p class="cmdemo__t">実在する募集拠点・勤務条件ではありません。拠点名・勤務地・給与・勤務時間・休日はすべて仮の値（◯◯・00）で、正式な募集情報ではありません。本番公開時には、社内で確認した拠点データに差し替えます。</p>
</div>'''

# ------------------------------------------------------------------
# LEVEL 02：共通紹介ページ
# ------------------------------------------------------------------
def industries():
    seen, out = set(), []
    for p in VISIBLE:
        k = p["industry"]
        if not k or k in seen: continue
        seen.add(k)
        out.append((k, [q for q in VISIBLE if q["industry"] == k]))
    return out

def card(p, base, single_template=False):
    lab, cls = STATUS_LABEL[p["status"]]
    name = p["site_name"] if p.get("site_name_public") else "%s（拠点名は非公開）" % p["area"]
    rows = [("業態", p["industry"]), ("勤務地", p["location"]),
            ("募集職種", "／".join(p["open_positions"])),
            ("勤務時間", p["work_hours"]), ("休日", p["holidays"]), ("給与", p["salary"])]
    dl = "".join('<dt>%s</dt><dd>%s</dd>' % (e(k), e(v) if v else '<span class="cmtbd">確認中</span>')
                 for k, v in rows)
    if p["status"] in ("confirmed", "demo"):
        href = base if single_template else "./%s/" % p["slug"]
        cta = '<a class="cmcard__cta" href="%s">募集要項を見る<i aria-hidden="true">&#8594;</i></a>' % href
    else:
        cta = '<p class="cmcard__none">正式な募集条件を確認中のため、募集要項は掲載していません。</p>'
    return ('<li class="cmcard">\n'
            '  <p class="cmcard__top"><span class="cmchip %s">%s</span><span class="cmcard__id en">%s</span></p>\n'
            '  <h3 class="cmcard__n">%s</h3>\n'
            '  <dl class="cmcard__dl">%s</dl>\n'
            '  %s\n</li>' % (cls, lab, e(p["job_id"]), e(name), dl, cta))

def level2(preview=True):
    head, foot = shell("renewal/jobs/center-manager/index.html")
    # プレビューでは拠点別ページを1枚のテンプレートで代表させる。
    # 正式公開時（preview=False）は ./<slug>/ の個別ページへリンクする。
    base = "../center-manager-template-preview/"
    title = "物流センター長・センター長候補の仕事と募集拠点｜BPO・現場運営｜株式会社PAL"
    desc  = ("株式会社PALのセンター長・センター長候補（BPO・現場運営）の仕事内容と募集拠点。"
             "物流拠点の運営、人員配置、作業進捗・品質・安全の管理、生産性・収支の確認と業務改善、"
             "取引先との調整までを担います。PALは複数の物流拠点を運営しており、拠点によって現場の業務や"
             "勤務条件が異なります。拠点ごとの募集要項から、希望する勤務地・業態を選べます。")
    if preview: title = "【比較プレビュー】" + title
    head = set_head(head, title, desc, "センター長・センター長候補",
        [{"@type":"ListItem","position":1,"name":"採用情報","item":"../../"},
         {"@type":"ListItem","position":2,"name":"募集職種","item":"../../jobs/"},
         {"@type":"ListItem","position":3,"name":"センター長・センター長候補"}], noindex=preview)

    envs = "".join(
      '<li class="cmenv"><p class="cmenv__k en">%02d</p><b>%s</b>'
      '<p class="cmenv__t">%s</p>'
      '<p class="cmenv__n">対応する募集拠点：%s</p></li>' % (
        i+1, e(k),
        e(v[0]["logistics_work"][0]) if v[0].get("logistics_work") else "取り扱う物流業務は確認中です。",
        e("／".join((q["site_name"] if q.get("site_name_public") else q["area"]) for q in v)))
      for i,(k,v) in enumerate(industries()))

    cards = "\n".join(card(p, base, single_template=preview) for p in VISIBLE) if VISIBLE else \
      '<li class="cmcard cmcard--empty"><p>現在、拠点別の募集要項は掲載していません。募集拠点が確定しだい掲載します。</p></li>'

    body = f'''<nav class="crumb" aria-label="パンくず"><div class="wrap"><a href="../../">採用情報</a><a href="../../jobs/">募集職種</a><span aria-current="page">センター長・センター長候補</span></div></nav>

<!-- ===== CMJOB v1：LEVEL 02（センター長・センター長候補 共通紹介）。
     このページは tools/build_center_manager.py が data/center-manager-jobs.json から生成している。
     手で編集せず、JSON を直してからビルドし直すこと。
     ・仕事内容は WORK の BPO パネルと JOBS の既存募集要項で確認できる項目だけを使用。
     ・勤務地・給与・勤務時間・休日は拠点ごとに異なるため、このページには載せず LEVEL 03 に置く。
     ・社員インタビューは people/bpo/ の記載から引用のみ。原文は変更していない。 ===== -->
<section class="phead">
  <div class="wrap">
    <p class="slabel">Center Manager / BPO</p>
    <h1 class="ptitle"><span class="nw">物流現場を動かす。</span><span class="nw">その先の改善まで。</span></h1>
    <p class="plead">センター長・センター長候補は、物流拠点の運営を担いながら、人員・作業進捗・品質・安全・生産性と、その先の業務改善に関わる仕事です。PALは複数の物流拠点を運営していて、拠点によって現場の業務や勤務条件が異なります。</p>
  </div>
</section>

<section class="sec sec--tight" id="role">
  <div class="wrap">
    <div class="shead rv" style="margin-bottom:20px">
      <p class="slabel">The Role</p>
      <h2 class="stitle" style="font-size:clamp(21px,2.5vw,29px)"><span class="nw">センター長は、</span><span class="nw">どんな仕事をするのか。</span></h2>
      <p class="slead">現場が自律的に回り、成果を生み続ける状態をつくることが、この仕事のあるべき姿です。拠点をまたいで共通する仕事は、次の6つです。</p>
    </div>
    <ul class="cmrole rv">
      <li><span class="en">01</span><b>日々の現場運営</b><p>各拠点の稼働状況を確認し、現場を止めないための判断をします。</p></li>
      <li><span class="en">02</span><b>人員配置・スタッフ管理</b><p>その日の作業量に合わせて人員を配置し、現場で働くメンバーと向き合います。</p></li>
      <li><span class="en">03</span><b>作業進捗・生産性の管理</b><p>作業の進み方と生産性を見ながら、滞りがあれば手を打ちます。</p></li>
      <li><span class="en">04</span><b>品質・安全の管理</b><p>作業品質と安全を保つための確認と、仕組みづくりを行います。</p></li>
      <li><span class="en">05</span><b>数値・収支の管理</b><p>生産性と収支を確認し、数字をもとに改善の優先順位を決めます。</p></li>
      <li><span class="en">06</span><b>業務改善と顧客との調整</b><p>取引先との打ち合わせや現場確認を重ね、改善を進めます。拠点間の調整と、改善施策の横展開も担当します。</p></li>
    </ul>
    <!-- ===== CMJOB v1：センター長とセンター長候補の役割の違いは、社内で確認できた
         資料がないため、共通紹介ページでは断定していない（STEP 5）。 ===== -->
    <div class="cmnote rv">
      <p class="cmnote__h">センター長と、センター長候補の違いについて</p>
      <p>現在の募集は「センター長／候補（現場運営）」としてひとつにまとめられており、<b>両者で担当範囲・責任・応募条件がどう異なるかは社内で確認中</b>です。候補として入社した方が初日からセンター長と同じ責任を担うわけではありません。拠点ごとに募集しているポジションと応募条件は、下の募集拠点一覧からご確認ください。</p>
      <p class="cmnote__s">※ 応募にあたっての経験は、現場マネジメント・オペレーション改善・数値管理の経験者を歓迎しています。未経験・新卒の方も応募いただけます（<a class="textlink textlink--sm" href="../../faq/">FAQ</a>）。</p>
    </div>
  </div>
</section>

<section class="sec sec--tight sec--soft" id="environments">
  <div class="wrap">
    <div class="shead rv" style="margin-bottom:20px">
      <p class="slabel">Working Environments</p>
      <h2 class="stitle" style="font-size:clamp(21px,2.5vw,29px)"><span class="nw">同じセンター運営でも、</span><span class="nw">現場はそれぞれ違う。</span></h2>
      <p class="slead">顧客の業態によって、扱う荷物も、求められる管理も変わります。下の一覧は、募集拠点のデータから業態ごとにまとめたものです。</p>
    </div>
    {DEMO_BANNER if DEMO else ''}
    <ul class="cmenvs rv">
      {envs}
    </ul>
  </div>
</section>

<section class="sec sec--tight" id="voices">
  <div class="wrap">
    <div class="shead rv" style="margin-bottom:20px">
      <p class="slabel">Real Voices</p>
      <h2 class="stitle" style="font-size:clamp(21px,2.5vw,29px)">実際に現場を担う社員の声。</h2>
    </div>
    <div class="cmvoice rv">
      <div class="cmvoice__head">
        <p class="cmvoice__role">BPO事業部 Productivity推進部</p>
        <p class="cmvoice__name">I.N</p>
        <p class="cmvoice__meta">2005年 PALへ転籍／2015年 正社員登用<br>前職：物流センターのパートスタッフ</p>
      </div>
      <div class="cmvoice__body">
        <p class="cmvoice__q">現在の仕事</p>
        <p class="cmvoice__t">複数の物流センターの運営・改善に携わっています。日々の運営では、人員配置や作業進捗、品質・安全、生産性、収支、取引先への対応など、現場を止めないための仕事を見ています。</p>
        <p class="cmvoice__q">仕事で大切にしていること</p>
        <p class="cmvoice__t">現場を安定して運営する。そのうえで、今のやり方を疑ってみる。</p>
        <p class="cmvoice__n">※ 掲載しているのは本人の経験とキャリアです。センター長に共通する昇進の道すじを示したものではありません。</p>
        <p class="cmvoice__cta"><a class="btn btn--ghost" href="../../people/bpo/">BPO・現場運営の社員インタビューを読む<span class="btn__ico" aria-hidden="true">▶</span></a></p>
      </div>
    </div>
  </div>
</section>

<section class="sec sec--tight sec--soft" id="positions">
  <div class="wrap">
    <div class="shead rv" style="margin-bottom:20px">
      <p class="slabel">Open Positions</p>
      <h2 class="stitle" style="font-size:clamp(21px,2.5vw,29px)"><span class="nw">希望する拠点・働き方</span><span class="nw">から探す。</span></h2>
      <p class="slead">勤務地・勤務時間・休日・給与は拠点によって異なります。気になる拠点の募集要項でご確認ください。</p>
    </div>
    {DEMO_BANNER if DEMO else ''}
    <ul class="cmlist rv">
{cards}
    </ul>
    <p class="note" style="margin-top:20px">※ 「確認中」の拠点は、正式な募集条件を社内で確認している段階です。募集中の拠点として掲載しているものではありません。</p>
    <p class="note">※ BPO・現場運営という職種の全体像は<a class="textlink textlink--sm" href="../../work/#role-bpo">仕事を知る</a>、入社後のキャリアは<a class="textlink textlink--sm" href="../../career/#career">キャリアを知る</a>をご覧ください。</p>
  </div>
</section>
'''
    entry = '''
<section class="entry">
  <div class="entry__media"><img src="../../../assets/hero-bg.jpg" alt="" width="2752" height="1536" loading="lazy" aria-hidden="true"></div>
  <div class="entry__inner wrap--narrow">
    <p class="entry__label en">NEXT STEP</p>
    <h2>働きたい拠点を選んで、<br>募集要項を見る。</h2>
    <p>選考の前に、会社説明やカジュアル面談だけの参加も歓迎しています。</p>
    <div class="entry__ctas">
      <a class="btn btn--red btn--lg" href="#positions">募集拠点の一覧を見る<span class="btn__ico" aria-hidden="true">▶</span></a>
      <a class="btn btn--ghost btn--lg" href="../../entry/">エントリーする<span class="btn__ico" aria-hidden="true">▶</span></a>
    </div>
    <p class="entry__sec"><a href="../">ほかの募集職種を見る</a></p>
  </div>
</section>
'''
    out = "renewal/jobs/center-manager-preview/index.html" if preview else "renewal/jobs/center-manager/index.html"
    wr(out, head + '<main id="top">\n' + body + entry + foot)
    return out



# ------------------------------------------------------------------
# LEVEL 03：拠点別募集要項（テンプレート）
# ------------------------------------------------------------------
def dl(rows):
    return '<div class="spec"><dl>' + "".join(
        '<dt>%s</dt><dd>%s</dd>' % (e(k), (e(v) if v else '<span class="cmtbd">確認中</span>'))
        for k, v in rows) + '</dl></div>'

def ul(items, empty="確認中です。"):
    if not items: return '<p class="cmtbd">%s</p>' % e(empty)
    return '<ul class="drvlist">' + "".join('<li>%s</li>' % e(x) for x in items) + '</ul>'

def level3(p, preview=True):
    head, foot = shell("renewal/jobs/center-manager/index.html")
    name = p["site_name"] if p.get("site_name_public") else "%s（拠点名は非公開）" % p["area"]
    pos  = "／".join(p["open_positions"])
    # title・description はページごとに固有にする。デモ印は先頭に一度だけ付ける。
    plain = lambda x: x.replace("【デモ】", "")
    title = "物流センター長・候補の求人｜%s %s｜株式会社PAL" % (plain(p["area"]), plain(p["industry"]))
    desc  = ("株式会社PALの%s（%s）における%sの募集要項。勤務地、取り扱う物流業務、仕事内容、"
             "雇用形態・給与・勤務時間・休日などの勤務条件、応募資格、選考の流れを掲載しています。"
             % (plain(name), plain(p["industry"]), pos))
    if preview:
        title = "【比較プレビュー・デモ】" + title
    head = set_head(head, title, desc, name,
        [{"@type":"ListItem","position":1,"name":"採用情報","item":"../../"},
         {"@type":"ListItem","position":2,"name":"募集職種","item":"../../jobs/"},
         {"@type":"ListItem","position":3,"name":"センター長・センター長候補","item":"../center-manager/"},
         {"@type":"ListItem","position":4,"name":name}], noindex=preview)

    jp = ''
    if p["status"] == "confirmed":
        jp = "（この拠点は確認済みのため、ビルド時に JobPosting 構造化データを出力します）"
    body = f'''<nav class="crumb" aria-label="パンくず"><div class="wrap"><a href="../../">採用情報</a><a href="../../jobs/">募集職種</a><a href="../center-manager-preview/">センター長・センター長候補</a><span aria-current="page">{e(name)}</span></div></nav>

<!-- ===== CMJOB v1：LEVEL 03（拠点別募集要項）のテンプレート。
     tools/build_center_manager.py が data/center-manager-jobs.json の1レコードから生成する。
     拠点が増えても、このテンプレートは変更せずJSONを足すだけでよい。
     JobPosting 構造化データは status が confirmed のレコードにだけ出力する。
     仮条件・デモデータの求人には出力しない（STEP 12）。 ===== -->
<section class="phead">
  <div class="wrap">
    <p class="slabel">Jobs ／ Center Manager</p>
    <h1 class="ptitle">物流センター長・候補<br>｜{e(p["area"])} {e(p["industry"])}</h1>
    <p class="plead">{e(name)}｜募集ポジション：{e(pos)}</p>
  </div>
</section>

<section class="sec sec--tight">
  <div class="wrap">
    {DEMO_BANNER if p["status"] == "demo" else ''}

    <p class="role__h rv"><span class="en">01</span>募集拠点について</p>
    {dl([("拠点名", name), ("勤務地", p["location"]), ("アクセス", p.get("access","")),
          ("顧客業態", p["industry"]), ("募集ポジション", pos)])}
    <p class="role__h rv" style="margin-top:40px"><span class="en">02</span>取り扱う物流業務</p>
    {ul(p.get("logistics_work", []))}

    <p class="role__h rv" style="margin-top:40px"><span class="en">03</span>この拠点での仕事内容</p>
    <p class="cmsub">拠点をまたいで共通する仕事</p>
    <ul class="drvlist"><li>日々の現場運営と、各拠点の稼働状況の確認</li><li>人員配置・スタッフ管理</li><li>作業進捗・生産性の管理</li><li>品質・安全の管理</li><li>数値・収支の管理</li><li>業務改善と、取引先との打ち合わせ・現場確認</li></ul>
    <p class="cmsub" style="margin-top:24px">この拠点ならではの仕事</p>
    {ul(p.get("duties_site", []))}
    <p class="note">※ 共通する仕事は<a class="textlink textlink--sm" href="../center-manager-preview/#role">センター長の仕事</a>で詳しく紹介しています。</p>

    <p class="role__h rv" style="margin-top:40px"><span class="en">04</span>勤務条件</p>
    {dl([("雇用形態", p.get("employment_type","")), ("給与・想定年収", p.get("salary","")),
          ("勤務時間", p.get("work_hours","")), ("休憩時間", p.get("break_time","")),
          ("休日・休暇", p.get("holidays","")), ("シフト", p.get("shift","")),
          ("時間外勤務", p.get("overtime","")), ("勤務地・転勤", p.get("relocation","")),
          ("試用期間", p.get("probation","")), ("福利厚生", p.get("benefits",""))])}

    <p class="role__h rv" style="margin-top:40px"><span class="en">05</span>応募条件</p>
    <div class="cmsplit">
      <div><p class="cmsub">センター長｜必須</p>{ul(p.get("req_manager", []), "この拠点ではセンター長の募集はありません（または条件を確認中です）。")}</div>
      <div><p class="cmsub">センター長候補｜必須</p>{ul(p.get("req_candidate", []), "この拠点ではセンター長候補の募集はありません（または条件を確認中です）。")}</div>
    </div>
    <p class="cmsub" style="margin-top:24px">歓迎する経験</p>
    {ul(p.get("req_welcome", []))}
    <p class="cmsub" style="margin-top:24px">求める人物像</p>
    {ul(p.get("req_person", []))}
    <p class="note">※ センター長とセンター長候補では応募条件が異なります。応募されるポジションの条件をご確認ください。</p>

    <p class="role__h rv" style="margin-top:40px"><span class="en">06</span>応募・選考</p>
    {dl([("応募方法", "採用サイトのエントリーフォームから応募いただけます。"),
          ("選考フロー", "エントリー→カジュアル面談→面接（複数回）→最終面接→内定（Web面接可）"),
          ("問い合わせ先", p.get("contact","")),
          ("求人ID", p["job_id"]), ("更新日", p.get("updated_at",""))])}
    <p class="job__foot"><a class="btn btn--red" href="{e(p["apply_url"]) if p.get("apply_url") else "../../entry/"}">この拠点に応募する<span class="btn__ico" aria-hidden="true">▶</span></a></p>

    <p class="role__h rv" style="margin-top:40px"><span class="en">07</span>あわせて見る</p>
    <p class="cmrel rv">
      <a class="btn btn--ghost" href="../center-manager-preview/">センター長の仕事を見る<span class="btn__ico" aria-hidden="true">▶</span></a>
      <a class="btn btn--ghost" href="../../people/bpo/">BPO・現場運営の社員インタビューを見る<span class="btn__ico" aria-hidden="true">▶</span></a>
      <a class="btn btn--ghost" href="../center-manager-preview/#positions">ほかの募集拠点を見る<span class="btn__ico" aria-hidden="true">▶</span></a>
    </p>
    {('<p class="note">' + jp + '</p>') if jp else ''}
  </div>
</section>
'''
    entry = '''
<section class="entry">
  <div class="entry__media"><img src="../../../assets/hero-bg.jpg" alt="" width="2752" height="1536" loading="lazy" aria-hidden="true"></div>
  <div class="entry__inner wrap--narrow">
    <p class="entry__label en">NEXT STEP</p>
    <h2>この拠点に<br>興味を持った方へ。</h2>
    <p>選考の前に、会社説明やカジュアル面談だけの参加も歓迎しています。</p>
    <div class="entry__ctas">
      <a class="btn btn--red btn--lg" href="../../entry/">この拠点に応募する<span class="btn__ico" aria-hidden="true">▶</span></a>
    </div>
    <p class="entry__sec"><a href="../center-manager-preview/#positions">ほかの募集拠点を見る</a></p>
  </div>
</section>
'''
    out = ("renewal/jobs/center-manager-template-preview/index.html" if preview
           else "renewal/jobs/center-manager/%s/index.html" % p["slug"])
    wr(out, head + '<main id="top">\n' + body + entry + foot)
    return out

# ------------------------------------------------------------------
# LEVEL 01：JOBS一覧の導線修正プレビュー
# ------------------------------------------------------------------
def level1(preview=True):
    S = rd("renewal/jobs/index.html")
    if preview:
        S = S.replace('<!-- SEO-BASE v1：相対自己参照canonical。本番ドメイン未確定のため絶対URLは使わない -->\n<link rel="canonical" href="./">\n',
                      '<!-- 比較プレビュー：canonicalは置かず、noindex,nofollow を指定 -->\n<meta name="robots" content="noindex,nofollow">\n', 1)
        S = S.replace('<title>', '<title>【比較プレビュー】', 1)
    cm = "../jobs/center-manager-preview/" if preview else "center-manager/"

    old_head = '''        <h2 class="role__title">センター長／候補（現場運営）</h2>
        <p class="role__lead">現場が自律的に回り、成果を生み続ける状態をつくる。</p>'''
    new_head = '''        <h2 class="role__title">センター長・センター長候補</h2>
        <p class="role__lead">物流拠点の運営・品質・安全・人員管理を担い、日々の業務改善に取り組む仕事。</p>'''
    assert S.count(old_head) == 1
    S = S.replace(old_head, new_head)

    old_note = '''      <p class="note">※ 選考の流れは<a class="textlink textlink--sm" href="#selection">選考について</a>をご覧ください。この職種だけの募集要項ページは<a class="textlink textlink--sm" href="center-manager/">こちら</a>です。</p>'''
    new_note = ('''      <!-- ===== CMJOB v1：拠点ごとに勤務地・勤務時間・休日・給与が異なるため、
           上の表は「共通の目安」であることを明示し、正式な条件は拠点別の募集要項へ誘導する。
           拠点別の求人カードはJOBS一覧には並べない（STEP 3）。 ===== -->
      <p class="note">※ <b>勤務地・勤務時間・休日・給与は拠点によって異なります。</b>上の表は現在掲載している共通の目安で、拠点ごとの正式な条件は確認中です。拠点別の募集要項は「センター長の仕事と募集拠点」のページに掲載しています。</p>
      <p class="note">※ 選考の流れは<a class="textlink textlink--sm" href="#selection">選考について</a>をご覧ください。</p>''')
    assert S.count(old_note) == 1
    S = S.replace(old_note, new_note)

    S = S.replace('''      <p class="role__h"><span class="en">02</span>募集要項</p>
      <div class="spec">
        <dl>
          <dt>雇用形態</dt><dd>正社員（試用期間3ヶ月）</dd>''',
'''      <p class="role__h"><span class="en">02</span>共通の募集条件（目安）</p>
      <div class="spec">
        <dl>
          <dt>雇用形態</dt><dd>正社員（試用期間3ヶ月）</dd>''', 1)

    old_cta = '''        <a class="btn btn--red btn--lg" href="../entry/">この職種に応募する<span class="btn__ico" aria-hidden="true">▶</span></a>
        <a class="btn btn--ghost" href="../work/">仕事を知る<span class="btn__ico" aria-hidden="true">▶</span></a>
        <a class="textlink" href="../people/bpo/">BPO / 現場運営の社員インタビュー</a>'''
    new_cta = '''        <a class="btn btn--red btn--lg" href="%s">センター長の仕事と募集拠点を見る<span class="btn__ico" aria-hidden="true">▶</span></a>
        <a class="btn btn--ghost" href="../work/#role-bpo">BPO・現場運営の仕事内容を見る<span class="btn__ico" aria-hidden="true">▶</span></a>
        <a class="textlink" href="../people/bpo/">BPO / 現場運営の社員インタビュー</a>''' % cm
    assert S.count(old_cta) == 1
    S = S.replace(old_cta, new_cta)

    S = S.replace('<span class="rolenav__cat">BPO / 現場運営</span><b>現場を動かし、改善する</b>',
                  '<span class="rolenav__cat">BPO / 現場運営</span><b>センター長・センター長候補</b>', 1)

    if preview:
        # 同階層（renewal/jobs/ 配下）を指していた相対リンクを付け替える。
        # ../ や # や絶対URLで始まるものは対象外。
        S = re.sub(r'href="(?!\.\./|#|https?:|/|mailto:)([^"]+)"', r'href="../jobs/\1"', S)
    out = "renewal/jobs-preview/index.html" if preview else "renewal/jobs/index.html"
    wr(out, S)
    return out

if __name__ == "__main__":
    # LEVEL 01（JOBS一覧）は JOBSOPEN v1（tools/build_jobs.py）へ移行済みのため生成しない。
    # renewal/jobs-preview/ は検討の記録として残しているが、条件は古い。
    print("LEVEL 02 ->", level2(preview=True))
    print("LEVEL 03 ->", level3(POS[0], preview=True))
    print("confirmed=%d / tbd=%d / demo=%d"
          % (len(CONFIRMED), len([p for p in POS if p["status"]=="tbd"]), len(DEMO)))
