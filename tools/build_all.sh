#!/bin/sh
# 生成物をまとめて作り直す。ビルド後は必ず noindex を付け直す。
# （公開前の確認用サイトのため。本番公開時は最後の行を set_noindex.py off に変える）
set -e
cd "$(dirname "$0")/.."
python3 -I tools/build_logistics_operation.py   # LEVEL 02：物流センター運営の仕事
python3 -I tools/build_jobs.py                  # LEVEL 01/03：求人一覧・求人詳細
python3 -I tools/build_faq.py                   # FAQ 比較プレビュー
python3 -I tools/build_driver_preview.py        # 4tドライバー SEO/AIO 比較プレビュー
python3 -I tools/build_large_driver_preview.py  # 大型ドライバー（下書き）比較プレビュー
python3 -I tools/build_jobs_detail_preview.py   # 求人詳細デザイン改善の比較プレビュー
# 比較プレビューは set_noindex / set_entry_cta より前に作ること。
# あとから作ると noindex と応募CTA停止が当たらない。
# WORK（renewal/work/）は比較プレビューからの移行が完了したため、直接編集して管理する。
# 文章の記録は tools/build_work_roles.py と tools/build_work_sales.py に残している。
python3 -I tools/set_noindex.py on
python3 -I tools/set_entry_cta.py off   # 正式な応募先が決まったら off → on
