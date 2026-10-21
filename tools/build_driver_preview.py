# -*- coding: utf-8 -*-
"""
===== DRVSEO v1 =====
4tルート配送ドライバーの採用強化（比較プレビュー）。正式ページは変更しない。

  renewal/jobs/dts-driver-seo-preview/   既存の募集要項（renewal/jobs/dts/）に
                                          冒頭サマリーと安全・品質の項目を足した改善案
  renewal/work-dts-driver-preview/        WORK の DTS パネルだけを補足した改善案

内容はすべて承認済み求人票（Indeed_ドライバー正社員.pdf）で確認できる範囲。
求人票にない条件（年間休日数・固定残業・転勤・副業・荷待ち時間など）は書かない。

  python3 -I tools/build_driver_preview.py
"""
import os, re, sys, html, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f: return f.read()
def wr(p, s):
    os.makedirs(os.path.join(ROOT, os.path.dirname(p)), exist_ok=True)
    with open(os.path.join(ROOT, p), "w", encoding="utf-8") as f: f.write(s)
def e(x): return html.escape(str(x), quote=False)

# ------------------------------------------------------------------
# 1) JOBS：ドライバー募集要項の改善案
# ------------------------------------------------------------------
DESC = ("株式会社PALの4tルート配送ドライバー求人。千葉県船橋市のafs船橋センターから、大手スーパーや外食チ"
        "ェーンへ食品を配送します。配送件数は1日3件程度、配送エリアは千葉県を中心とした一都三県で長距離運転はあ"
        "りません。カゴ車とパワーゲートを使うため手積み・手降ろしはなし。日勤と夜勤を選べる正社員の募集です。未経験も可。")

SUMMARY = '''    <!-- ===== DRVSEO v1：求職者が最初に確認する条件を、本文に入る前にまとめて示す。
         値はすべて承認済み求人票の記載どおり。求人票にない項目は置いていない。 ===== -->
    <div class="drvsum rv">
      <p class="drvsum__h">この求人のポイント</p>
      <dl class="drvsum__dl">
        <dt>勤務地</dt><dd>千葉県船橋市高瀬町24-6　afs船橋センター内<br><span>JR京葉線「南船橋駅」より徒歩30分／車・バイク・自転車通勤OK（駐車場完備）</span></dd>
        <dt>給与</dt><dd><b>月給36万円〜60万円</b><br><span>賞与 年1回（実績による）／昇給 年1回（4月）／残業・深夜・資格・早朝・無事故の各手当</span></dd>
        <dt>勤務時間</dt><dd>シフト制（日勤・夜勤を選べます）<br><span>日勤 8:00〜20:00／9:00〜21:00　夜勤 21:00〜翌9:00／24:00〜翌12:00／1:00〜13:00（いずれも実働8時間）</span></dd>
        <dt>休日</dt><dd>週休2日（シフト制）<br><span>※隔週2日休み（月6日〜）／希望休はできる限り優先します</span></dd>
        <dt>必要免許</dt><dd>中型自動車運転免許（8t）、または2007年（平成19年）6月1日以前に取得した普通自動車運転免許（AT限定可）<br><span>配送の経験は不問。同乗研修（OJT）があります</span></dd>
        <dt>配送内容</dt><dd>4tトラックで、大手スーパーや外食チェーンの各店舗へ食品を配送<br><span>1日3件程度／千葉県を中心に一都三県／手積み・手降ろしなし</span></dd>
        <dt>雇用形態</dt><dd>正社員（試用期間なし）</dd>
      </dl>
    </div>

'''

SAFETY = '''
    <p class="role__h rv" style="margin-top:40px"><span class="en">05</span>安全と品質のために行っていること</p>
    <!-- ===== DRVSEO v1：求人票に書かれている範囲のみ。これ以上の安全教育・研修制度は書かない。 ===== -->
    <ul class="drvlist">
      <li>出勤時のアルコールチェック</li>
      <li>乗務するトラックの点検</li>
      <li>専用端末での配送先の確認</li>
      <li>配送の実務経験がない方への同乗研修（OJT）</li>
    </ul>
    <p class="note">※ 上記は募集要項に記載のある内容です。これ以外の制度は確認でき次第お知らせします。</p>
'''

def build_jobs_preview():
    S = rd("renewal/jobs/dts/index.html")
    S = re.sub(r'<meta name="description" content="[^"]*">',
               '<meta name="description" content="%s">' % html.escape(DESC), S, count=1)
    S = re.sub(r'<meta property="og:description" content="[^"]*">',
               '<meta property="og:description" content="%s">' % html.escape(DESC), S, count=1)
    S = S.replace('<title>', '<title>【比較プレビュー】', 1)
    S = S.replace('<link rel="canonical" href="./">\n', '')
    S = re.sub(r'<meta name="robots" content="[^"]*">',
               '<meta name="robots" content="noindex,nofollow">', S, count=1)
    # 冒頭サマリーを「この仕事の特徴」セクションの先頭へ
    a = '    <div class="shead rv" style="margin-bottom:20px">\n      <p class="slabel">Points</p>'
    if S.count(a) != 1: print("FAIL: Points セクション"); sys.exit(1)
    S = S.replace(a, SUMMARY + a)
    # 安全と品質の項目を「1日の流れ」の前（募集要項セクションの直前）へ
    b = '\n<section class="sec sec--tight" id="day">'
    if S.count(b) != 1: print("FAIL: #day"); sys.exit(1)
    S = S.replace(b, '\n' + SAFETY.rstrip() + '\n  </div>\n</section>\n' + b, 1)
    # 直前のセクションを閉じ直したので、重複した閉じを戻す
    S = S.replace(SAFETY.rstrip() + '\n  </div>\n</section>\n\n<section class="sec sec--tight" id="day">',
                  SAFETY.rstrip() + '\n  </div>\n</section>\n\n<section class="sec sec--tight" id="day">')
    wr("renewal/jobs/dts-driver-seo-preview/index.html", S)
    return len(DESC)

# ------------------------------------------------------------------
# 2) WORK：DTS パネルの補足
# ------------------------------------------------------------------
ADD = '''
          <p class="rpanel__ch">安全と品質のために</p>
          <ul class="rdeep__pts">
            <li><i>01</i><b>出発前に確かめる</b><p>出勤時のアルコールチェックと、乗務するトラックの点検から1日が始まります。</p></li>
            <li><i>02</i><b>配送先は端末で確認する</b><p>専用端末で配送先を確認してから出発します。固定ルートの配送です。</p></li>
          </ul>
'''

def build_work_preview():
    S = rd("renewal/work/index.html")
    # タブとパネルの表示名を HOME に合わせる（DTS / ドライバー）
    S = S.replace('<b class="rtab__n">DTS / 運送・運行</b>', '<b class="rtab__n">DTS / ドライバー</b>')
    S = S.replace('<h3 class="rpanel__n">DTS / 運送・運行</h3>', '<h3 class="rpanel__n">DTS / ドライバー</h3>')
    # DTS パネルの「大切にしていること」の前に、安全・品質の2項目を足す
    m = re.search(r'(<article class="rpanel[^"]*" role="tabpanel" id="role-dts".*?)(\n          <p class="rpanel__ch">この仕事で大切にしていること</p>)', S, re.S)
    if not m: print("FAIL: role-dts パネル"); sys.exit(1)
    S = S[:m.end(1)] + ADD.rstrip("\n") + S[m.end(1):]
    # 募集要項への導線を明確にする
    S = S.replace('<a class="rcbtn rcbtn--sub" href="../jobs/dts/">配送ドライバーの募集要項を見る<i aria-hidden="true">&#8594;</i></a>',
                  '<a class="rcbtn rcbtn--sub" href="../jobs/dts/">4tルート配送ドライバーの募集要項を見る<i aria-hidden="true">&#8594;</i></a>')
    S = S.replace('<title>', '<title>【比較プレビュー】', 1)
    S = S.replace('<!-- SEO-BASE v1：相対自己参照canonical。本番ドメイン未確定のため絶対URLは使わない -->\n<link rel="canonical" href="./">\n', '')
    wr("renewal/work-dts-driver-preview/index.html", S)

if __name__ == "__main__":
    n = build_jobs_preview()
    print("JOBS ドライバー求人プレビュー：meta description %d文字 %s" % (n, "（ちょうど160文字）" if n == 160 else "★160文字ではありません"))
    build_work_preview()
    print("WORK DTSパネル プレビューを生成")
