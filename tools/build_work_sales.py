# -*- coding: utf-8 -*-
"""
===== SALESMERGE v1 =====
WORK の職種再編：
  ・Engagement / Sales と BizDev を1タブへ統合（表示名 Engagement / Sales・BizDev）
  ・承認済み求人票にもとづく「人材派遣営業」を新規追加
  ・9職種のピル型タブ・詳細パネルのデザインは維持

ベース：renewal/work-all-roles-expanded-preview/（ROLEDEEP v1 の9職種拡充版）
出力  ：renewal/work-sales-restructured-preview/（noindex）

出典：WORK の既存パネル（Engagement / Sales・BizDev の原文）／
      承認済み求人票「【法人営業（人材派遣）】＠大阪：リーダー」（data/jobs-openings.json）／
      PEOPLE の社員インタビュー。確認できない業務は書かない。

  python3 -I tools/build_work_sales.py
"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f: return f.read()
def wr(p, s):
    os.makedirs(os.path.join(ROOT, os.path.dirname(p)), exist_ok=True)
    with open(os.path.join(ROOT, p), "w", encoding="utf-8") as f: f.write(s)

S = rd("renewal/work-all-roles-expanded-preview/index.html")

MERGED = '''<article class="rpanel" role="tabpanel" id="role-sales"
        aria-labelledby="rt-role-sales" tabindex="0">
        <!-- ===== SALESMERGE v1：Engagement / Sales と BizDev を1タブへ統合。
             BizDev の主な仕事・この仕事らしさ・関わる相手・募集職種との関係は削除せず、
             「営業と事業開発、それぞれの役割」として区別したまま残している。
             パネルIDは role-sales のまま。旧 #role-bizdev はタブJSの別名で開く。 ===== -->
        <div class="rpanel__top">
          <svg class="rpanel__ic" aria-hidden="true"><use href="#ic-meeting"></use></svg>
          <div>
            <p class="rpanel__en en">ENGAGEMENT / SALES &amp; BIZDEV</p>
            <h3 class="rpanel__n">Engagement / Sales・BizDev</h3>
            <p class="rpanel__one">営業・事業開発｜顧客課題を次の提案につなげる</p>
          </div>
        </div>
        <div class="rpanel__body">
          <div class="rpanel__main">
            <p class="rpanel__ch">主な仕事</p>
            <ul class="role-points"><li>既存顧客への定期的な連絡と、関係づくり</li>
            <li>新しい顧客との接点づくり</li>
            <li>現場見学・課題のヒアリングと整理</li>
            <li>新たな提案・事業機会づくり</li>
            <li>現場・組織の状態把握と、各部門との連携</li>
            <li>顧客課題と市場機会の整理</li>
            <li>新しい事業・サービスの可能性を形にする</li></ul>
          </div>
          <div class="rpanel__side">
            <p class="rpanel__ch">この仕事らしさ</p>
            <p class="rpanel__t">要望の裏にある、本当の課題を探すこと。一つの相談が、プロジェクトになります。顧客課題や市場機会をもとに、新しい事業・サービスの可能性を形にすることもあります。</p>
            <p class="rpanel__ch">関わる相手</p>
            <ul class="role-people"><li>顧客</li><li>センター長</li><li>FDE</li><li>BPO</li><li>システム / プロダクト</li><li>DTS</li><li>社内の各専門部門</li></ul>
          </div>
        </div>

        <div class="rdeep">
          <h4 class="rdeep__h">要望の裏にある、本当の課題を探す。</h4>
          <p class="rdeep__lead">顧客との接点をつくり、現場を見て課題を整理し、社内の専門部門へつなぐ仕事です。あわせて、顧客課題や市場機会をもとに新しい事業・サービスの可能性を検討する事業開発（BizDev）も、同じ枠組みのなかにあります。2つは同じ仕事ではなく、顧客の課題と事業機会という同じ入口から広がる別の役割です。</p>

          <p class="rpanel__ch">営業と事業開発、それぞれの役割</p>
          <ol class="rdeep__flow">
            <li><span class="en">SALES</span><b>Engagement / Sales</b>
              <p><span>担うこと</span>顧客との関係づくりと課題の把握、提案機会の創出を担当する。</p></li>
            <li><span class="en">BIZDEV</span><b>BizDev</b>
              <p><span>担うこと</span>顧客課題や市場機会をもとに、新しい事業・サービスの可能性を検討し、形にする。</p></li>
          </ol>

          <p class="rpanel__ch">仕事の進め方</p>
          <ol class="rdeep__flow">
            <li><span class="en">01</span><b>接点をつくる</b>
              <p><span>会う</span>会社紹介から始め、顧客を実際の現場に招く。</p>
              <p><span>掘り起こす</span>休眠顧客・潜在顧客へ訪問・面談でアプローチする。</p></li>
            <li><span class="en">02</span><b>現場を見て、課題を聞く</b>
              <p><span>見学する</span>現場見学をしながら課題をヒアリングする。</p></li>
            <li><span class="en">03</span><b>提案できる範囲を見極める</b>
              <p><span>特定する</span>PALが提案できる範疇を特定する。</p>
              <p><span>整理する</span>課題に必要なデータを分析し、初回提案の方向性を整理する。</p></li>
            <li><span class="en">04</span><b>社内へつなぐ</b>
              <p><span>トスアップする</span>設計部門や社内の提案専門組織へつなぐ。</p>
              <p><span>還元する</span>顧客の反応をマーケティング部門へ戻し、施策の精度を高める。</p></li>
          </ol>
          <p class="rdeep__note">提案から現場導入までは、FDE・BPO・システム / プロダクト・DTSと分担して進めます。</p>

          <p class="rpanel__ch">この仕事で大切にしていること</p>
          <ul class="rdeep__pts">
            <li><i>01</i><b>すぐ受注にならなくても、関係を続ける</b><p>長期的な視点でお客様との関係構築を続ける工夫を大切にしています。</p></li>
            <li><i>02</i><b>現場と経営の両方の視点で見る</b><p>現場の課題だけでなく、経営的な視点での課題も深く理解します。</p></li>
            <li><i>03</i><b>一次情報を社内へ戻す</b><p>現場で得た顧客の反応をマーケティング部門へ還元し、施策の精度を高めます。</p></li>
          </ul>
        </div>
          <div class="rpanel__foot">
            <a class="rcbtn rcbtn--main" href="../people/sales/">この仕事をしている社員の声を読む<i aria-hidden="true">&#8594;</i></a>
            <a class="rcbtn rcbtn--sub" href="../jobs/openings/engagement-member/">募集要項を見る<i aria-hidden="true">&#8594;</i></a>
          </div>
          <p class="rpanel__note">※ 募集職種は「エンゲージメント・新規営業」です。</p>
      </article>
'''

STAFFING = '''<article class="rpanel" role="tabpanel" id="role-staffing"
        aria-labelledby="rt-role-staffing" tabindex="0">
        <!-- ===== SALESMERGE v1：人材派遣営業を新規追加。
             出典は承認済み求人票「【法人営業（人材派遣）】＠大阪：リーダー」。
             求人票に書かれていない業務・制度は追加していない。
             営業担当自身がシステム開発や自動化設備の設計・導入を担うとは書いていない。 ===== -->
        <div class="rpanel__top">
          <svg class="rpanel__ic" aria-hidden="true"><use href="#ic-worker"></use></svg>
          <div>
            <p class="rpanel__en en">STAFFING SALES</p>
            <h3 class="rpanel__n">人材派遣営業</h3>
            <p class="rpanel__one">人材の提案から、物流現場の改善につなげる</p>
          </div>
        </div>
        <div class="rpanel__body">
          <div class="rpanel__main">
            <p class="rpanel__ch">主な仕事</p>
            <ul class="role-points"><li>求人を出している企業へのアプローチ</li>
            <li>既存顧客からの他拠点紹介</li>
            <li>欠員や業務ボトルネックのヒアリング</li>
            <li>物流倉庫への人材派遣の提案</li>
            <li>自社開発の勤怠管理システム・作業可視化システムの導入提案</li></ul>
          </div>
          <div class="rpanel__side">
            <p class="rpanel__ch">この仕事らしさ</p>
            <p class="rpanel__t">物流現場の人員課題に向き合いながら、勤怠管理や作業可視化の仕組みを活用し、自動化・省人化につながる提案にも関われること。</p>
            <p class="rpanel__ch">関わる相手</p>
            <ul class="role-people"><li>物流倉庫の顧客企業</li><li>既存顧客</li><li>営業事務</li></ul>
          </div>
        </div>

        <div class="rdeep">
          <h4 class="rdeep__h">人材の提案だけで、終わらない。</h4>
          <p class="rdeep__lead">物流倉庫への人材派遣の法人営業です。労働力の提供にとどまらず、顧客の課題に応じて、社内の専門部署と連携しながらシステムの活用や省人化につながる提案までを行います。求職者対応は営業事務4名が担当しているため、営業は企業への提案に時間を使えます。</p>

          <p class="rpanel__ch">仕事の進め方</p>
          <ol class="rdeep__flow">
            <li><span class="en">01</span><b>顧客との接点をつくる</b>
              <p><span>案件を獲得する</span>求人を出している企業へアプローチする。</p>
              <p><span>広げる</span>既存顧客から、ほかの拠点を紹介してもらう。</p></li>
            <li><span class="en">02</span><b>現場の課題を聞く</b>
              <p><span>欠員を確認する</span>人員の欠員状況を確認する。</p>
              <p><span>詰まりを探す</span>業務上のボトルネックをヒアリングする。</p></li>
            <li><span class="en">03</span><b>人材・仕組みを提案する</b>
              <p><span>人材を提案する</span>顧客の人員課題に応じた人材派遣を提案する。</p>
              <p><span>仕組みを提案する</span>課題に応じて、社内の専門部署と連携しながら、自社開発の勤怠管理や作業可視化のシステムを提案する。</p></li>
            <li><span class="en">04</span><b>営業活動を管理・改善する</b>
              <p><span>逆算する</span>目標から逆算した行動計画を立てる。</p>
              <p><span>見直す</span>営業行動の量と質を高め、プロセス管理を自ら実践する。</p></li>
          </ol>
          <p class="rdeep__note">4段階は仕事の流れを理解しやすくするための整理で、すべての案件がこの順に進むわけではありません。</p>

          <p class="rpanel__ch">この仕事で大切にしていること</p>
          <ul class="rdeep__pts">
            <li><i>01</i><b>人の課題を入口に、現場の課題を見る</b><p>欠員だけでなく、どこに時間がかかっているのかまで聞きにいきます。</p></li>
            <li><i>02</i><b>自社のシステムを提案に使う</b><p>作業可視化システムなどで現場の状況をデータにし、社内の専門部署とともに自動化・省人化につながる提案へつなげます。</p></li>
            <li><i>03</i><b>目標から逆算して動く</b><p>組織の営業行動量と質を高め、目標達成に向けたプロセス管理を自ら実践します。</p></li>
            <li><i>04</i><b>店舗運営・労務管理の経験が活きる</b><p>店長・副店長などで労務管理を経験した方が、その経験を活かして働いています。</p></li>
          </ul>
        </div>
          <div class="rpanel__foot">
            <a class="rcbtn rcbtn--main" href="../jobs/openings/staffing-sales-leader/">募集要項を見る<i aria-hidden="true">&#8594;</i></a>
          </div>
          <p class="rpanel__note">※ 応募条件・勤務地・給与は<a class="textlink textlink--sm" href="../jobs/openings/staffing-sales-leader/">募集要項</a>をご覧ください。</p>
      </article>
'''

def replace_panel(rid, new):
    global S
    m = re.search(r'<article class="rpanel[^"]*" role="tabpanel" id="%s".*?</article>\n' % rid, S, re.S)
    if not m: print("FAIL panel %s" % rid); sys.exit(1)
    S = S[:m.start()] + new + S[m.end():]

replace_panel("role-sales", MERGED)
replace_panel("role-bizdev", STAFFING)

# タブ：Engagement / Sales の表示名を変え、BizDev のタブを人材派遣営業に置き換える
OLD_TAB_SALES = '''<button class="rtab" type="button" role="tab" id="rt-role-sales" aria-controls="role-sales"
          aria-selected="false" tabindex="-1">
          <svg class="rtab__ic" aria-hidden="true"><use href="#ic-meeting"></use></svg>
          <b class="rtab__n">Engagement / Sales</b>
        </button>'''
NEW_TAB_SALES = '''<button class="rtab" type="button" role="tab" id="rt-role-sales" aria-controls="role-sales"
          aria-selected="false" tabindex="-1">
          <svg class="rtab__ic" aria-hidden="true"><use href="#ic-meeting"></use></svg>
          <b class="rtab__n">Engagement / Sales・BizDev</b>
        </button>'''
OLD_TAB_BIZ = '''<button class="rtab" type="button" role="tab" id="rt-role-bizdev" aria-controls="role-bizdev"
          aria-selected="false" tabindex="-1">
          <svg class="rtab__ic" aria-hidden="true"><use href="#ic2-improve"></use></svg>
          <b class="rtab__n">BizDev</b>
        </button>'''
NEW_TAB_STAFF = '''<button class="rtab" type="button" role="tab" id="rt-role-staffing" aria-controls="role-staffing"
          aria-selected="false" tabindex="-1">
          <svg class="rtab__ic" aria-hidden="true"><use href="#ic-worker"></use></svg>
          <b class="rtab__n">人材派遣営業</b>
        </button>'''
for a, b, lab in [(OLD_TAB_SALES, NEW_TAB_SALES, "sales tab"), (OLD_TAB_BIZ, NEW_TAB_STAFF, "bizdev→staffing tab")]:
    if S.count(a) != 1: print("FAIL %s" % lab); sys.exit(1)
    S = S.replace(a, b)

# HOW ROLES CONNECT のチップ
S = S.replace('<li><a href="#role-sales">Engagement / Sales</a></li>',
              '<li><a href="#role-sales">Engagement / Sales・BizDev</a></li>')
S = S.replace('<li><a href="#role-bizdev">BizDev</a></li>',
              '<li><a href="#role-staffing">人材派遣営業</a></li>')

# タブJS：旧 #role-bizdev で開いたときは統合後のタブを選ぶ
OLD_JS = '''  function indexOfId(id){
    for(var i=0;i<panels.length;i++){ if(panels[i].id===id) return i; }
    return -1;
  }'''
NEW_JS = '''  /* ===== SALESMERGE v1：旧タブIDの読み替え。
     BizDev は Engagement / Sales と統合したため、既存の #role-bizdev リンクは
     統合後のタブを開く。外部・内部のリンクを壊さないための対応。 ===== */
  var ALIAS={'role-bizdev':'role-sales'};
  function indexOfId(id){
    id = ALIAS[id] || id;
    for(var i=0;i<panels.length;i++){ if(panels[i].id===id) return i; }
    return -1;
  }'''
if S.count(OLD_JS) != 1: print("FAIL tab js"); sys.exit(1)
S = S.replace(OLD_JS, NEW_JS)

S = re.sub(r'[ \t]*<a href="(?:\.\./)*work/fde/">FDEという仕事</a>\n', '', S)
S = S.replace('<title>【比較プレビュー・9職種拡充版】', '<title>【比較プレビュー・営業再編版】', 1)
wr("renewal/work-sales-restructured-preview/index.html", S)

# 正式WORK：ヘッダー（canonical・title・description）とフッターは現行の正式ページのものを使い、
# <main> の中身だけを差し替える。プレビュー用の noindex は持ち込まない。
OFF = rd("renewal/work/index.html")
off_head = OFF[:OFF.index('<main id="main">')]
off_tail = OFF[OFF.index('</main>'):]
# 職種タブのJSは </main> より後ろにあるため、正式ページ側のJSにも別名を入れる
if "ALIAS" not in off_tail:
    if off_tail.count(OLD_JS) != 1:
        print("FAIL: 正式WORKのタブJSが見つからない"); sys.exit(1)
    off_tail = off_tail.replace(OLD_JS, NEW_JS)
pre_main = S[S.index('<main id="main">'):S.index('</main>')]
wr("renewal/work/index.html", off_head + pre_main + off_tail)
print("renewal/work-sales-restructured-preview/index.html と renewal/work/index.html を生成")
