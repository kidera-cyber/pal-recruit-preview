# -*- coding: utf-8 -*-
"""
===== SEJOB v1 =====
自社開発 Web・アプリエンジニア（system-engineer）の募集要項の改訂案を、
比較プレビューとして出す。

  renewal/jobs-system-engineer-preview/   （noindex,follow・承認前）

求人データ（data/jobs-openings.json）はまだ変更していない。このスクリプトが
レコードを複製したうえで仕事内容まわりだけ差し替え、既存の共通テンプレート
（tools/build_jobs.py の detail_body_v2）で組み立てている。承認後に JSON を
直せば、正式ページ renewal/jobs/openings/system-engineer/ に同じ内容が出る。

変えたもの：about（開発対象と現場との接点を具体化）／duties（工程を明記）／
            req_person（開発業務の特徴を about へ移し、人物要件とキャリアを整理）
変えていないもの：title・meta description・canonical・robots・JobPosting・求人ID・
            URL・募集状態・給与・勤務時間・休日・勤務地・応募条件（必須/歓迎）・
            採用人数・面接回数・デザイン

技術スタック（言語・フレームワーク・DB・クラウド）は、PALでの使用を示す一次資料が
確認できなかったため掲載していない。

  python3 -I tools/build_system_engineer_preview.py
"""
import copy, importlib.util, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = "renewal/jobs-system-engineer-preview/index.html"

ABOUT = ("自社の物流DXプロダクトの開発です。管理者向けのWebシステムと作業者向けの"
         "スマートフォンアプリが連動する仕組みを、倉庫内作業の生産性向上や配送効率化を目的につくります。"
         "PMの指示のもとで、既存プロダクトの機能改善や新規開発に携わります。"
         "自社で物流センターを運営しているため、開発した機能が現場でどう使われるかを倉庫で確認し、"
         "その結果を次の改修に反映できます。")

DUTIES = [
 "管理者向けWebシステムの開発",
 "作業者向けスマートフォンアプリの開発",
 "倉庫管理・配送効率化に関するシステムの開発",
 "既存プロダクトの機能改善と、新規開発",
 "AGVなどのIoT機器との連携",
 "作業実績・業務データの収集と、導入効果の分析",
 "社内インフラの整備",
 "要件整理から設計・実装・テスト、倉庫での実機確認、リリース後の改修まで（担当する工程と範囲は案件と役割によって異なります）",
]

REQ_PERSON = ("自分が組んだロジックの成果や、使っている人の声を確かめながら進めたい方。"
              "技術の習得に前向きな方を、チームで支えます。"
              "将来の役割として、開発リーダー、パートナー企業との共同開発、現場改善スペシャリストなどがあります"
              "（いずれも昇格や役割の変更を保証するものではありません）。")

INTRO = '''<section class="drvdraft">
  <div class="wrap">
    <p class="drvdraft__h">これは募集要項の比較プレビューです（承認前）。</p>
    <p class="drvdraft__b">給与・勤務時間・休日・勤務地・応募条件・採用人数・面接回数は公開中のページと同じです。
      仕事内容の文章と箇条書き、求める人物像だけを書き直しています。現在公開中のページは
      <a class="textlink textlink--sm" href="../jobs/openings/system-engineer/">こちら</a>です。</p>
    <ul class="drvdraft__l">
      <li><b>開発対象</b>を「管理者向けWebシステム／作業者向けスマートフォンアプリ／倉庫管理・配送効率化」と書き分けました。</li>
      <li><b>担当工程</b>（要件整理・設計・実装・テスト・倉庫での実機確認・リリース後の改修）を明記し、全工程を一人で担当するわけではない旨を添えました。</li>
      <li><b>自社で物流センターを運営していること</b>と開発業務のつながりを概要文に入れました。</li>
      <li><b>求める人物像</b>から開発業務の特徴を概要文へ移し、人物要件とキャリアに整理しました。</li>
      <li><b>使用技術（言語・フレームワーク・DB・クラウド）は掲載していません。</b>PALでの使用を示す一次資料が確認できなかったため、公開保留としています。</li>
      <li>「PMの指示のもとで」は正式な職務要件の可能性があるため、残しています（要確認）。</li>
    </ul>
  </div>
</section>
'''

if __name__ == "__main__":
    sp = importlib.util.spec_from_file_location("bj", os.path.join(ROOT, "tools/build_jobs.py"))
    bj = importlib.util.module_from_spec(sp); sp.loader.exec_module(bj)
    o = copy.deepcopy(next(x for x in bj.OPEN if x["id"] == "system-engineer"))
    o["about"], o["duties"], o["req_person"] = ABOUT, DUTIES, REQ_PERSON
    bj.build_detail(o, layout="v2", depth=2, outpath=OUT, intro=INTRO)
    print("システムエンジニア募集要項の比較プレビューを生成：%s" % OUT)
