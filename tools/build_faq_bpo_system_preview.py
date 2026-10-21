# -*- coding: utf-8 -*-
"""
===== FAQBPOSYS v1 =====
FAQ の「BPO・現場運営」「プロダクト企画・開発」2カテゴリだけを書き直した比較プレビュー。

  renewal/faq-bpo-system-preview/   （noindex,nofollow・承認前）

公開中の renewal/faq/（46問）を土台にし、上記2カテゴリの details ブロックだけ
差し替える。ほかの質問・カテゴリ・検索・アコーディオン・デザインは触らない。

根拠にした一次情報
  BPO   : data/jobs-openings.json の bpo 4求人（about / duties / req_must）、
          renewal/work/#role-bpo、renewal/people/bpo/、renewal/jobs/logistics-operation/
  システム: data/jobs-openings.json の system-engineer、renewal/work/#role-system、
          renewal/people/system/（本人回答）、添付PALの社内SE求人票

技術スタック（言語・フレームワーク・DB・クラウド）は PAL での使用を示す一次資料が
確認できなかったため、FAQ に技術名は書いていない。確認が取れるまで公開保留。

  python3 -I tools/build_faq_bpo_system_preview.py
"""
import os, re, json, html as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f: return f.read()
def wr(p, s):
    os.makedirs(os.path.join(ROOT, os.path.dirname(p)), exist_ok=True)
    with open(os.path.join(ROOT, p), "w", encoding="utf-8") as f: f.write(s)

W_BPO, W_SYS = "../work/#role-bpo", "../work/#role-system"
JOBS, CAREER = "../jobs/", "../career/#career"
P_BPO, P_SYS = "../people/bpo/", "../people/system/"
SE = "../jobs/openings/system-engineer/"

BPO = [
 ("PALの物流センター運営では、具体的にどのような仕事を担当しますか？",
  f'各拠点の稼働状況を確認し、その日の作業量に合わせて人員を配置します。あわせて作業の進捗・品質・安全の管理、'
  f'生産性と収支の確認、取引先との打ち合わせと現場確認、作業方法の見直しまでを担当します。拠点によって顧客の業態・'
  f'取扱商品・勤務シフトが異なり、担当する範囲は拠点と募集レベルによって変わります。'
  f'詳しくは<a href="{W_BPO}">BPO・現場運営の仕事内容</a>と'
  f'<a href="{P_BPO}">社員インタビュー</a>をご覧ください。'),
 ("センター長・責任者候補は、どのような役割を担いますか？",
  f'物流センターの運営管理に加えて、人員・作業・品質・数値の管理を担います。責任者候補では、クライアントとの'
  f'物量・単価・オペレーションの交渉を通じた拠点の収支改善も担当範囲に入ります。アソシエイト・メンバーとは'
  f'担当範囲が異なるため、職位ごとの条件は<a href="{JOBS}">各募集要項</a>をご確認ください。'
  f'その先の役割の広がりは<a href="{CAREER}">キャリアを知る</a>で紹介しています。'),
 ("物流センター運営では、DXや機械化にどのように関わりますか？",
  f'現場の稼働状況と作業の進め方を把握し、改善が必要な工程や運営上の課題を整理します。人を増やして対応するのではなく、'
  f'作業そのものを変えられないか、機械やシステムに置き換えられないかを検討し、社内のDX・システム部門と連携して'
  f'機械化・デジタル化を現場の運営に取り入れます。機械化の推進そのものが担当業務に含まれる拠点もあります。'),
 ("自動化・機械化が進むと、物流センター運営の仕事はどう変わりますか？",
  f'拠点によって機械化の進み方が異なるため、変わり方は一様ではありません。PALが現在募集している拠点では、'
  f'設備と人の役割分担を決めること、作業の進捗・品質・安全を確認すること、生産性と収支から次の改善を決めることを'
  f'担当範囲としています。定量データにもとづく提案や、新しく受託する拠点の立ち上げに関わることもあります。'),
 ("物流センター運営には、どのような経験が活かせますか？",
  f'拠点と募集レベルによって異なります。メンバークラスでは派遣・アルバイト・社員に対する何らかの取りまとめの経験、'
  f'責任者候補ではエリアマネージャー経験・店舗・施設・営業所等の運営管理経験・営業組織のマネジメント経験の'
  f'いずれかを必須としています。職務経験を問わない求人もあります。'
  f'求人ごとの必須条件と歓迎条件は<a href="{JOBS}">各募集要項</a>をご確認ください。'),
]

SYS = [
 ("PALでは、どのようなシステムやアプリを開発していますか？",
  f'物流センターの現場で使われるプロダクトを、自社で企画・開発しています。仕分け作業で使うAndroidアプリ、'
  f'バーコードの読取、カンバンのOCR読取、出荷日ごとの採番、仕分け状況のダッシュボードなどが対象です。'
  f'管理者向けのWebシステムと作業者向けのスマートフォンアプリが連動する仕組みや、倉庫管理・配送効率化に'
  f'関わるシステムも開発しています。詳しくは<a href="{W_SYS}">システム / プロダクト開発の仕事内容</a>をご覧ください。'),
 ("開発エンジニアは、どの工程を担当しますか？",
  f'現場ヒアリングと要件整理から、設計・実装、倉庫での実機確認、リリース後の改修までに関わります。一例として、'
  f'午前は担当機能の設計と開発、午後は現場との打ち合わせや倉庫での実機確認、改善対応という進め方があります。'
  f'担当する工程と範囲は案件と役割によって異なり、全員が全工程を一人で担当するわけではありません。'
  f'実際の進め方は<a href="{P_SYS}">DXプロダクト開発の社員インタビュー</a>に掲載しています。'),
 ("システム開発は、FDEや物流現場運営とどのように連携しますか？",
  f'FDEは現場の課題を技術要件へ整理し、各部門と連携して実装・改善につなぐ役割です。システム / プロダクト開発は'
  f'自社プロダクトそのものの企画・開発を担当し、同じ案件で連携します。日々の現場運営はBPO・現場運営が担います。'
  f'自社で物流センターを運営しているため、開発した機能が実際にどう使われるかを倉庫で確認し、'
  f'その結果を次の改修に反映できます。'),
 ("応募にはどのような開発経験が必要ですか？",
  f'何らかのWeb系システム開発の実務経験を必須としています。特定のプログラミング言語やフレームワークの'
  f'指定はありません。想定年収・勤務時間・休日・勤務地を含む応募条件は'
  f'<a href="{SE}">自社開発 Web・アプリエンジニアの募集要項</a>に掲載しています。'),
]

def details(items):
    return "\n".join(
        '      <details>\n'
        '        <summary><i>Q</i>%s<em aria-hidden="true">＋</em></summary>\n'
        '        <p>%s</p>\n'
        '      </details>' % (H.escape(q, quote=False), a) for q, a in items)

MARK = ('<!-- ===== FAQBPOSYS v1：BPO・現場運営とプロダクト企画・開発の2カテゴリを書き直した比較プレビュー。\n'
        '     ・BPO：抽象的な役割説明から、稼働確認・人員配置・進捗/品質/安全・生産性/収支・取引先調整・\n'
        '       業務改善という実務へ。DX・機械化との関わりを2問追加。拠点名と想定年収の列挙はJOBSへ移した。\n'
        '     ・システム：開発対象（Androidアプリ／バーコード／OCR／採番／ダッシュボード／管理者向けWeb／\n'
        '       作業者向けスマホアプリ／倉庫管理・配送効率化）と担当工程を具体化。FDE・現場運営との\n'
        '       役割分担を1問追加。古い「募集条件を確認中」とリンク切れ気味の導線を正式な募集要項へ。\n'
        '     ・プログラミング言語・フレームワーク・DB・クラウドは、PALでの使用を示す一次資料を確認\n'
        '       できなかったため掲載していない（技術スタックのFAQは公開保留）。\n'
        '     ほかのカテゴリ・質問・検索・アコーディオン・デザインは変更していない。 ===== -->')

INTRO = '''<section class="drvdraft">
  <div class="wrap">
    <p class="drvdraft__h">これはFAQ 2カテゴリの比較プレビューです（承認前）。</p>
    <p class="drvdraft__b">「BPO・現場運営」と「プロダクト企画・開発」の質問・回答だけを書き直しています。
      ほかの質問・カテゴリ・検索・アコーディオンは公開中のページと同じです。現在公開中のFAQは
      <a class="textlink textlink--sm" href="../faq/">こちら</a>です。</p>
    <ul class="drvdraft__l">
      <li><b>BPO</b>：4問 → 5問。稼働確認・人員配置・進捗/品質/安全・生産性/収支・取引先調整・業務改善という実務へ。DX・機械化との関わりを2問追加しました。</li>
      <li><b>システム</b>：4問 → 4問。開発対象と担当工程を具体化し、FDE・現場運営との役割分担を1問追加しました。</li>
      <li><b>技術スタック（言語・フレームワーク・DB・クラウド）は掲載していません。</b>PALでの使用を示す一次資料が確認できなかったため、公開保留としています。</li>
      <li>拠点名の列挙・想定年収は各募集要項へ移しました。</li>
    </ul>
  </div>
</section>
'''

def build():
    s = rd("renewal/faq/index.html")
    # ---- 2カテゴリの details だけ差し替える ----
    for cid, items in (("fq-bpo", BPO), ("fq-prod", SYS)):
        i = s.index('id="%s"' % cid)
        a = s.index('<details>', i)
        b = s.rindex('</details>', i, s.index('<div id="fq-', i + 10)) + len('</details>')
        s = s[:a] + details(items).lstrip() + s[b:]
    # ---- 一段深くなるので相対パスを1つ戻す（renewal/faq/ → renewal/faq-bpo-system-preview/ は同階層）----
    s = re.sub(r'<title>.*?</title>',
               '<title>【比較プレビュー】BPO・システム開発FAQ改訂案｜株式会社PAL 採用</title>', s, count=1, flags=re.S)
    s = re.sub(r'<meta name="robots" content="[^"]*">',
               '<meta name="robots" content="noindex,nofollow">', s, count=1)
    # ---- FAQPage 構造化データを表示から作り直す ----
    vis = [(H.unescape(re.sub(r'<[^>]+>', '', q)).strip(), H.unescape(re.sub(r'<[^>]+>', '', x)).strip())
           for q, x in re.findall(r'<summary><i>Q</i>(.*?)<em aria-hidden="true">＋</em></summary>\s*<p>(.*?)</p>', s, re.S)]
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in vis]}
    m = re.search(r'<script type="application/ld\+json">(\{"@context": "https://schema\.org", "@type": "FAQPage".*?)</script>', s, re.S)
    s = s[:m.start(1)] + json.dumps(ld, ensure_ascii=False) + s[m.end(1):]
    s = s.replace('<main id="top">', MARK + '\n<main id="top">\n' + INTRO, 1)
    wr("renewal/faq-bpo-system-preview/index.html", s)
    print("FAQ比較プレビューを生成：renewal/faq-bpo-system-preview/（全%d問 ／ BPO %d問・システム %d問）"
          % (len(vis), len(BPO), len(SYS)))

if __name__ == "__main__":
    build()
