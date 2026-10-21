# -*- coding: utf-8 -*-
"""
===== LOGIOPS v1（旧 CMJOB v2）=====
「物流センター運営」という仕事の紹介ページ（LEVEL 02）を組み立てる。
募集レベル（アソシエイト／メンバー／責任者候補）の違いを見せる役割を持つ。

  LEVEL 01  renewal/jobs/                      募集中の求人を探す（tools/build_jobs.py）
  LEVEL 02  renewal/jobs/logistics-operation/  この仕事を知る（このスクリプト）
  LEVEL 03  renewal/jobs/openings/<id>/        拠点ごとの正式な募集要項（tools/build_jobs.py）

v1 ではデモデータを使っていたが、承認済み求人票4件（船橋・厚木・東広島・須磨）が
そろったため、data/jobs-openings.json の実データだけで組み立てる。
拠点が増減したときは JSON を直してこのスクリプトを実行するだけでよい。

  python3 -I tools/build_logistics_operation.py
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
BPO  = [o for o in D["openings"] if o["cat"] == "bpo" and o["status"] == "open"]
HOLD = [o for o in D["openings"] if o["cat"] == "bpo" and o["status"] == "hold"]

def card(o):
    rows = [("業態・取扱商品", o["goods"]), ("勤務地", "%s%s" % (o["pref"], o["city"])),
            ("募集職種", "%s（%s）" % (o["title"], o["level"])),
            ("勤務シフト", o["shift"]), ("休日", o["holidays"].split("／")[0]),
            ("想定年収", "<b>%s</b>" % e(o["salary_year"]))]
    dl = "".join('<dt>%s</dt><dd>%s</dd>' % (e(k), v if k == "想定年収" else e(v))
                 for k, v in rows if v)
    return ('<li class="cmcard">\n'
            '  <p class="cmcard__top"><span class="cmchip cmchip--open">募集中</span>'
            '<span class="cmcard__id en">%s</span></p>\n'
            '  <h3 class="cmcard__n">%s</h3>\n'
            '  <dl class="cmcard__dl">%s</dl>\n'
            '  <a class="cmcard__cta" href="../openings/%s/">募集要項を見る<i aria-hidden="true">&#8594;</i></a>\n'
            '</li>' % (e(o["id"].upper()), e(o["office"]), dl, e(o["id"])))

def industries():
    seen, out = [], []
    for o in BPO:
        if o["goods"] not in seen:
            seen.append(o["goods"])
            out.append((o["goods"], [q for q in BPO if q["goods"] == o["goods"]]))
    return out

def build():
    S = rd("renewal/jobs/logistics-operation/index.html")
    head = S[:S.index('<main id="top">')]
    foot = S[S.index('</main>'):]

    title = "物流センター運営の仕事｜募集レベルと募集拠点｜株式会社PAL"
    desc  = ("株式会社PALの物流センター運営の仕事内容と、募集レベル・募集拠点。物流拠点の運営、人員配置、"
             "作業進捗・品質・安全の管理、生産性・収支の確認と業務改善、取引先との調整までを担います。"
             "アソシエイト・メンバー・責任者候補の3つの募集レベルがあります。千葉県船橋市、神奈川県厚木市、"
             "広島県東広島市、兵庫県神戸市須磨区の4拠点で募集しており、拠点によって取扱商品・勤務シフト・"
             "想定年収・応募条件が異なります。")
    head = re.sub(r'<title>.*?</title>', '<title>%s</title>' % e(title), head, count=1, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">',
                  '<meta name="description" content="%s">' % html.escape(desc), head, count=1)
    head = re.sub(r'<meta property="og:title" content="[^"]*">',
                  '<meta property="og:title" content="%s">' % html.escape(title), head, count=1)
    head = re.sub(r'<meta property="og:description" content="[^"]*">',
                  '<meta property="og:description" content="%s">' % html.escape(desc), head, count=1)

    envs = "".join(
      '<li class="cmenv"><p class="cmenv__k en">%02d</p><b>%s</b>'
      '<p class="cmenv__t">勤務シフトは%s。%s</p>'
      '<p class="cmenv__n">対応する募集拠点：%s</p></li>' % (
        i+1, e(k), e("／".join(sorted({q["shift"] for q in v}))),
        e("／".join(sorted({q["title"] for q in v}))) + "を募集しています。",
        e("／".join(q["office"] for q in v)))
      for i, (k, v) in enumerate(industries()))

    cards = "\n".join(card(o) for o in BPO)
    # 社内で確認中の求人は、公開画面には一切出さない（制作管理側のみで保留する）
    holdnote = ""

    body = f'''<nav class="crumb" aria-label="パンくず"><div class="wrap"><a href="../../">採用情報</a><a href="../../jobs/">募集職種</a><span aria-current="page">物流センター運営の仕事</span></div></nav>

<!-- ===== CMJOB v2：LEVEL 02（物流センター運営・責任者候補の共通紹介）。
     tools/build_logistics_operation.py が data/jobs-openings.json から生成している。
     手で編集せず、JSON を直してからビルドし直すこと。
     ・仕事内容は WORK の BPO パネルと承認済み求人票4件で確認できる項目だけを使用。
     ・勤務地・給与・勤務時間・休日は拠点ごとに異なるため、拠点別の募集要項に置く。
     ・社員インタビューは people/bpo/ の記載から引用のみ。原文は変更していない。 ===== -->
<section class="phead">
  <div class="wrap">
    <p class="slabel">Logistics Operation / BPO</p>
    <h1 class="ptitle"><span class="nw">物流現場を動かす。</span><span class="nw">その先の改善まで。</span></h1>
    <p class="plead">物流拠点の運営を担いながら、人員・作業進捗・品質・安全・生産性と、その先の業務改善に関わる仕事です。現在は4つの拠点で募集していて、拠点によって取り扱う商品、勤務シフト、求める経験が異なります。</p>
  </div>
</section>

<section class="sec sec--tight" id="role">
  <div class="wrap">
    <div class="shead rv" style="margin-bottom:20px">
      <p class="slabel">The Role</p>
      <h2 class="stitle" style="font-size:clamp(21px,2.5vw,29px)"><span class="nw">物流センター運営は、</span><span class="nw">どんな仕事をするのか。</span></h2>
      <p class="slead">現場が自律的に回り、成果を生み続ける状態をつくることが、この仕事のあるべき姿です。拠点をまたいで共通する仕事は、次の6つです。</p>
    </div>
    <ul class="cmrole rv">
      <li><span class="en">01</span><b>日々の現場運営</b><p>各拠点の稼働状況を確認し、現場を止めないための判断をします。</p></li>
      <li><span class="en">02</span><b>人員配置・スタッフ管理</b><p>その日の作業量に合わせて人員を配置し、現場で働くメンバーと向き合います。</p></li>
      <li><span class="en">03</span><b>作業進捗・生産性の管理</b><p>作業の進み方と生産性を見ながら、滞りがあれば手を打ちます。</p></li>
      <li><span class="en">04</span><b>品質・安全の管理</b><p>作業品質と安全を保つための確認と、仕組みづくりを行います。</p></li>
      <li><span class="en">05</span><b>数値・収支の管理</b><p>売上・原価の予算管理を行い、数字をもとに改善の優先順位を決めます。</p></li>
      <li><span class="en">06</span><b>業務改善と顧客との調整</b><p>取引先との折衝や現場確認を重ね、改善提案につなげます。機械化の推進も進めます。</p></li>
    </ul>
    <div class="cmnote rv">
      <p class="cmnote__h">アソシエイト → メンバー → 責任者候補</p>
      <p><b>アソシエイト</b>（船橋）は、まず現場業務を習得しながら機械化推進に向けた情報収集を担当し、その後スタッフの育成・管理・教育やIT部門との連携へ広げていきます。職務経験は問いません。</p>
      <p><b>メンバー</b>（厚木・東広島）は、倉庫内の運営管理を中心に、人材配置・育成・業務標準化・品質管理を担当します。派遣・アルバイト・社員に対する何らかの取りまとめの経験が必要です。</p>
      <p><b>責任者候補</b>（須磨）は、運営管理に加えて、クライアントとの物量・価格・オペレーション交渉などの収益改善を主導します。エリアマネージャー経験、店舗・施設・営業所等の運営管理経験、営業組織のマネジメント経験のいずれかが必要です。</p>
      <p class="cmnote__s">※ 店長や副店長など責任者としてのマネジメント経験は、メンバーの必須条件ではありません。応募条件は拠点ごとに異なるため、各募集要項でご確認ください。</p>
    </div>
  </div>
</section>

<section class="sec sec--tight sec--soft" id="environments">
  <div class="wrap">
    <div class="shead rv" style="margin-bottom:20px">
      <p class="slabel">Working Environments</p>
      <h2 class="stitle" style="font-size:clamp(21px,2.5vw,29px)"><span class="nw">同じセンター運営でも、</span><span class="nw">現場はそれぞれ違う。</span></h2>
      <p class="slead">取り扱う商品によって、現場の動き方も勤務シフトも変わります。下の一覧は、現在募集している拠点の求人票から整理したものです。</p>
    </div>
    <ul class="cmenvs rv">
      {envs}
    </ul>
    <p class="note" style="margin-top:20px">※ 東広島流通センターは、新たに当社が委託を受ける拠点のため、ゼロからの立ち上げに関わります。</p>
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
        <p class="cmvoice__n">※ 掲載しているのは本人の経験とキャリアです。物流センター運営に共通する昇進の道すじを示したものではありません。</p>
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
      <p class="slead">勤務地・勤務時間・休日・給与・応募条件は拠点によって異なります。気になる拠点の募集要項でご確認ください。</p>
    </div>
    <ul class="cmlist rv">
{cards}
    </ul>
    {holdnote}
    <p class="note">※ BPO・現場運営という職種の全体像は<a class="textlink textlink--sm" href="../../work/#role-bpo">仕事を知る</a>、入社後のキャリアは<a class="textlink textlink--sm" href="../../career/#career">キャリアを知る</a>、ほかの職種の求人は<a class="textlink textlink--sm" href="../">募集中の求人一覧</a>をご覧ください。</p>
  </div>
</section>

<section class="entry">
  <div class="entry__media"><img src="../../../assets/hero-bg.jpg" alt="" width="2752" height="1536" loading="lazy" aria-hidden="true"></div>
  <div class="entry__inner wrap--narrow">
    <p class="entry__label en">NEXT STEP</p>
    <h2>働きたい拠点を選んで、<br>募集要項を見る。</h2>
    <p>募集中の職種と条件は募集要項に掲載しています。選考時のWeb面接にも対応しています。</p>
    <div class="entry__ctas">
      <a class="btn btn--red btn--lg" href="#positions">募集拠点の一覧を見る<span class="btn__ico" aria-hidden="true">▶</span></a>
      <a class="btn btn--ghost btn--lg" href="../../entry/">エントリーする<span class="btn__ico" aria-hidden="true">▶</span></a>
    </div>
    <p class="entry__sec"><a href="../">ほかの募集中の求人を見る</a></p>
  </div>
</section>
'''
    wr("renewal/jobs/logistics-operation/index.html", head + '<main id="top">\n' + body + foot)
    print("LEVEL 02 を生成：募集中 %d拠点 ／ 公開前確認 %d件" % (len(BPO), len(HOLD)))

if __name__ == "__main__":
    build()
