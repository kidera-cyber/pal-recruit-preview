# -*- coding: utf-8 -*-
"""
===== FAQSEO v1 =====
FAQページを data/faq.json から組み立てる。

  比較プレビュー  renewal/faq-seo-aio-preview/   （既定）
  正式ページ      renewal/faq/                   （--official を付けたとき）

本文・カテゴリ・FAQPage 構造化データを同じデータから出すので、表示と構造化データが食い違わない。
質問の追加・修正は data/faq.json を直してビルドし直す。

  python3 -I tools/build_faq.py
  python3 -I tools/build_faq.py --official
"""
import json, os, re, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f: return f.read()
def wr(p, s):
    os.makedirs(os.path.join(ROOT, os.path.dirname(p)), exist_ok=True)
    with open(os.path.join(ROOT, p), "w", encoding="utf-8") as f: f.write(s)
def e(x): return html.escape(str(x), quote=False)
def plain(x): return re.sub(r"<[^>]+>", "", x)

D    = json.loads(rd("data/faq.json"))
CATS = D["categories"]
FAQS = D["faqs"]

TITLE = "採用FAQ｜FDE・物流DX・物流センター運営・システム開発・営業の仕事と応募条件｜株式会社PAL"
# meta description は日本語ちょうど160文字（ビルド時に検証する）
DESC = ("株式会社PALの採用に関するよくあるご質問。FDEと物流DX、システム・プロダクト開発、物流センター運営、"
        "営業・事業開発、人材派遣営業、配送ドライバーなど職種ごとの仕事内容と応募条件に加えて、勤務地・勤務時間・"
        "休日・リモート勤務・転勤といった働き方や、研修、選考の流れまで、応募前に確認しておきたいことをまとめています。")

def faq_block(f):
    links = "".join(
        '<a class="fq__link" href="%s">%s<i aria-hidden="true">&#8594;</i></a>' % (e(h), e(t))
        for h, t in f.get("links", [])[:2])
    links = ('\n            <p class="fq__links">%s</p>' % links) if links else ""
    kw = " ".join(f.get("keywords", []))
    return f'''          <details class="fq" id="q-{e(f['id'])}" data-cat="{e(f['cat'])}" data-kw="{e(kw)}">
            <summary class="fq__q"><i aria-hidden="true">Q</i><span>{e(f['q'])}</span><em aria-hidden="true">＋</em></summary>
            <div class="fq__a"><p>{f['a']}</p>{links}</div>
          </details>'''

def cat_block(c):
    items = [f for f in FAQS if f["cat"] == c["key"]]
    if not items: return ""
    qs = "\n".join(faq_block(f) for f in items)
    return f'''        <section class="fqgroup" data-cat="{e(c['key'])}">
          <h2 class="fqgroup__h" id="cat-{e(c['key'])}">{e(c['name'])}<span class="fqgroup__c en" data-total="{len(items)}">{len(items)}</span></h2>
          <p class="fqgroup__d">{e(c['desc'])}</p>
{qs}
        </section>'''

SEARCH_JS = '''<!-- ===== FAQSEO v1：カテゴリ絞り込みとページ内検索。このページだけで使う最小限のJS。
     ・質問文・回答本文・キーワードを対象に、入力した語を含むFAQだけを表示する
     ・カテゴリ選択と検索は組み合わせられる（AND条件）
     ・該当0件のときは案内を出す／検索はクリアできる
     ・質問と回答はすべてHTMLに入っているので、JavaScriptが無効でも全問読める
       （その場合は絞り込みUIを出さず、全カテゴリ・全問を表示する） ===== -->
<script>
(function(){
  var root=document.getElementById('faqroot'); if(!root) return;
  root.classList.add('is-js');
  var box=document.getElementById('faqq'), clear=document.getElementById('faqclear');
  var count=document.getElementById('faqcount'), none=document.getElementById('faqnone');
  var items=[].slice.call(root.querySelectorAll('.fq'));
  var groups=[].slice.call(root.querySelectorAll('.fqgroup'));
  var btns=[].slice.call(root.querySelectorAll('.fqcat'));
  var selected='all';

  var text=function(el){
    return (el.querySelector('.fq__q').textContent + ' ' +
            el.querySelector('.fq__a').textContent + ' ' +
            (el.getAttribute('data-kw')||'')).toLowerCase();
  };
  items.forEach(function(el){ el.__t=text(el); });

  function apply(){
    var q=(box.value||'').trim().toLowerCase();
    var words=q?q.split(/[\\s　]+/).filter(Boolean):[];
    var n=0;
    items.forEach(function(el){
      var catOK=(selected==='all')||(el.getAttribute('data-cat')===selected);
      var qOK=words.every(function(w){ return el.__t.indexOf(w)>=0; });
      var ok=catOK&&qOK;
      el.hidden=!ok;
      if(ok) n++;
    });
    groups.forEach(function(g){
      var vis=[].slice.call(g.querySelectorAll('.fq')).filter(function(x){return !x.hidden;}).length;
      g.hidden=(vis===0);
      var c=g.querySelector('.fqgroup__c');
      if(c) c.textContent=vis;
    });
    btns.forEach(function(b){
      var on=b.getAttribute('data-cat')===selected;
      b.setAttribute('aria-pressed',on?'true':'false');
      b.classList.toggle('is-active',on);
    });
    if(count) count.textContent=n;
    if(none) none.hidden=(n>0);
    if(clear) clear.hidden=!q;
  }

  btns.forEach(function(b){ b.addEventListener('click',function(){ selected=b.getAttribute('data-cat'); apply(); }); });
  box.addEventListener('input',apply);
  box.addEventListener('keydown',function(ev){ if(ev.key==='Enter') ev.preventDefault(); });
  if(clear) clear.addEventListener('click',function(){ box.value=''; box.focus(); apply(); });

  /* URLハッシュで特定の質問を開く（#q-xxxx） */
  function fromHash(){
    var id=(location.hash||'').replace('#','');
    if(id.indexOf('q-')!==0) return;
    var el=document.getElementById(id);
    if(!el) return;
    selected='all'; box.value=''; apply();
    el.open=true;
    el.scrollIntoView({behavior:'auto',block:'start'});
  }
  window.addEventListener('hashchange',fromHash);
  apply(); fromHash();
})();
</script>'''

def build(official=False):
    src = "renewal/faq/index.html"
    S = rd(src)
    head = S[:S.index('<main id="top">')] if '<main id="top">' in S else S[:S.index('<main')]
    tail = S[S.index('</main>'):]
    # ===== FAQSEO v1：このスクリプトは renewal/faq/ を土台にして組み直すため、
    # 前回追記した検索JSを先に取り除く。取り除かないと実行のたびに積み上がる
    # （プレビュー側で3個に増えていた）。
    tail = re.sub(r'<!-- ===== FAQSEO v1：カテゴリ絞り込みとページ内検索.*?</script>', '', tail, flags=re.S)

    head = re.sub(r'<title>.*?</title>', '<title>%s</title>' % e(TITLE), head, count=1, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">',
                  '<meta name="description" content="%s">' % html.escape(DESC), head, count=1)
    head = re.sub(r'<meta property="og:title" content="[^"]*">',
                  '<meta property="og:title" content="%s">' % html.escape(TITLE), head, count=1)
    head = re.sub(r'<meta property="og:description" content="[^"]*">',
                  '<meta property="og:description" content="%s">' % html.escape(DESC), head, count=1)
    if not official:
        head = head.replace('<link rel="canonical" href="./">\n', '')

    # FAQPage 構造化データは、表示している質問・回答そのものから生成する
    jsonld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f["q"],
         "acceptedAnswer": {"@type": "Answer", "text": plain(f["a"])}} for f in FAQS]}
    head = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema\.org", "@type": "FAQPage".*?</script>',
                  '<!-- ===== FAQSEO v1：FAQPage。表示している%d問と完全に同じ内容を data/faq.json から生成している。\n'
                  '     削除・統合した質問は残していない。なお一般企業の採用FAQでは、FAQPageを置いても\n'
                  '     Google検索でFAQリッチリザルトが出ることは通常期待できない。本文の品質・検索意図への\n'
                  '     適合・内部リンクを優先し、構造化データはあくまで内容の機械可読化として置いている。 ===== -->\n'
                  '<script type="application/ld+json">%s</script>'
                  % (len(FAQS), json.dumps(jsonld, ensure_ascii=False)),
                  head, count=1, flags=re.S)

    chips = '<button class="fqcat is-active" type="button" data-cat="all" aria-pressed="true">すべて</button>' + \
        "".join('<button class="fqcat" type="button" data-cat="%s" aria-pressed="false">%s</button>'
                % (e(c["key"]), e(c["name"])) for c in CATS)
    groups = "\n".join(cat_block(c) for c in CATS)

    body = f'''<nav class="crumb" aria-label="パンくず"><div class="wrap"><a href="../">採用情報</a><span aria-current="page">よくあるご質問</span></div></nav>

<!-- ===== FAQSEO v1：tools/build_faq.py が data/faq.json から生成している。
     手で編集せず、JSON を直してからビルドし直すこと。
     ・回答はすべて、WORK／PEOPLE／CAREER／JOBS と承認済み求人票で確認できる内容だけ。
     ・同じ検索意図の質問は1問に統合している（統合・見送りの記録は JSON の merged / dropped）。
     ・職種をまたいで一律に言えない条件は、断定せず求人ごとの募集要項へ案内している。 ===== -->
<section class="phead">
  <div class="wrap">
    <p class="slabel">FAQ</p>
    <h1 class="ptitle">よくあるご質問。</h1>
    <p class="plead">仕事内容から応募条件、働き方まで。気になることを、ここから確認できます。</p>
  </div>
</section>

<section class="sec sec--tight" id="faq">
  <div class="wrap" id="faqroot">
    <div class="fqtools">
      <div class="fqsearch">
        <label class="fqsearch__l" for="faqq">キーワードで探す</label>
        <div class="fqsearch__f">
          <input class="fqsearch__i" type="search" id="faqq" placeholder="例：FDE／未経験／勤務地／人材派遣" autocomplete="off">
          <button class="fqsearch__c" type="button" id="faqclear" hidden>クリア</button>
        </div>
      </div>
      <div class="fqcats" role="group" aria-label="カテゴリで絞り込む">{chips}</div>
      <p class="fqcount"><b id="faqcount">{len(FAQS)}</b> 件の質問を表示しています。</p>
    </div>
    <p class="fqnone" id="faqnone" hidden>該当する質問が見つかりませんでした。別のキーワードでお試しください。<br>
      <a class="textlink textlink--sm" href="../jobs/">募集中の求人一覧を見る</a>　<a class="textlink textlink--sm" href="../work/">9職種の仕事内容を見る</a></p>
    <div class="fqlist">
{groups}
    </div>
  </div>
</section>

<section class="sec sec--tight sec--soft" id="related">
  <div class="wrap">
    <div class="shead rv" style="margin-bottom:24px">
      <p class="slabel">Related</p>
      <h2 class="stitle" style="font-size:clamp(21px,2.5vw,29px)">もっと詳しく知りたい方へ。</h2>
    </div>
    <ul class="nextlinks nextlinks--3 rv">
      <li><a href="../work/"><small>WORK</small><b>仕事を知る</b><span>9職種の仕事内容と、進め方</span></a></li>
      <li><a href="../people/"><small>PEOPLE</small><b>人を知る</b><span>社員インタビューと1日の流れ</span></a></li>
      <li><a href="../jobs/"><small>JOBS</small><b>募集中の求人</b><span>勤務地・給与・応募条件</span></a></li>
    </ul>
    <p class="note rv" style="margin-top:22px">※ 入社後の役割やキャリアの広がりは<a class="textlink textlink--sm" href="../career/">キャリアを知る</a>、会社のことは<a class="textlink textlink--sm" href="../about/">PALを知る</a>をご覧ください。</p>
  </div>
</section>

'''
    out = "renewal/faq/index.html" if official else "renewal/faq-seo-aio-preview/index.html"
    main_tag = '<main id="top">' if '<main id="top">' in S else re.search(r'<main[^>]*>', S).group(0)
    wr(out, head + main_tag + "\n" + body + tail.replace('</main>', SEARCH_JS + '\n</main>', 1))
    return out

if __name__ == "__main__":
    n = len(DESC)
    print("meta description の文字数：%d 文字 %s" % (n, "（ちょうど160文字）" if n == 160 else "★160文字ではありません"))
    print("公開FAQ：%d問 ／ カテゴリ：%d" % (len(FAQS), len(CATS)))
    print("出力：", build("--official" in sys.argv))
