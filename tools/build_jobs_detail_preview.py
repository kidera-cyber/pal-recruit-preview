# -*- coding: utf-8 -*-
"""
===== JOBDETAIL v2（比較プレビュー） =====
求人詳細ページの視認性改善版を、承認前の比較プレビューとして1件だけ出す。

  renewal/jobs-detail-redesign-preview/   船橋アソシエイト（funabashi-associate）

テンプレート本体は tools/build_jobs.py の detail_body_v2()。このスクリプトは
同じ関数を階層2・layout="v2" で呼ぶだけで、個別HTMLは手で編集していない。
承認後は tools/build_jobs.py の LAYOUT を "v2" にすれば全求人詳細に展開される。

維持しているもの（公開中の求人詳細と同じ）：
  title / meta description / canonical / robots(noindex,follow) /
  JobPosting・BreadcrumbList 構造化データ / 求人ID / 募集状態 /
  給与・勤務条件の値 / 「必須」「いずれか必須」「歓迎」の区別 / 内部リンク
変えたもの：見出し構成（9→6セクション）、文字サイズ、2カラムの定義リスト、
  主要条件サマリー、福利厚生の2列表示。求人データは変更していない。

  python3 -I tools/build_jobs_detail_preview.py
"""
import importlib.util, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = "funabashi-associate"
OUT = "renewal/jobs-detail-redesign-preview/index.html"

INTRO = '''<section class="drvdraft">
  <div class="wrap">
    <p class="drvdraft__h">これは求人詳細ページの比較プレビューです（デザイン改善版）。</p>
    <p class="drvdraft__b">掲載している条件・数値は公開中のページと同じで、見出しの構成と文字サイズ、
      表の組み方だけを変えています。現在公開中のページは
      <a class="textlink textlink--sm" href="../jobs/openings/funabashi-associate/">こちら</a>です。</p>
    <ul class="drvdraft__l">
      <li><b>求人ヘッダー</b>に給与・勤務地・休日・雇用形態の主要条件サマリーを追加しました。</li>
      <li><b>セクションを9つから6つ</b>に整理しました（仕事内容／応募条件／勤務条件／待遇／選考）。</li>
      <li><b>勤務条件</b>はPCで項目名28%・内容72%の2カラム、スマートフォンでは項目名を上に置いています。</li>
      <li><b>待遇・福利厚生</b>はPCで2列、スマートフォンで1列に並べています。</li>
      <li>本文16.5px・項目名16px・セクション見出し22〜26pxに上げ、11〜12pxの本文は使っていません。</li>
    </ul>
  </div>
</section>
'''

if __name__ == "__main__":
    sp = importlib.util.spec_from_file_location("bj", os.path.join(ROOT, "tools/build_jobs.py"))
    bj = importlib.util.module_from_spec(sp); sp.loader.exec_module(bj)
    o = next(x for x in bj.OPEN if x["id"] == TARGET)
    bj.build_detail(o, layout="v2", depth=2, outpath=OUT, intro=INTRO)
    print("求人詳細デザイン改善の比較プレビューを生成： %s（%s）" % (OUT, o["title"]))
