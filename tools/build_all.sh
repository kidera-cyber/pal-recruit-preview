#!/bin/sh
# 生成物をまとめて作り直す。ビルド後は必ず noindex を付け直す。
# （公開前の確認用サイトのため。本番公開時は最後の行を set_noindex.py off に変える）
set -e
cd "$(dirname "$0")/.."
python3 -I tools/build_logistics_operation.py   # LEVEL 02：物流センター運営の仕事
python3 -I tools/build_jobs.py                  # LEVEL 01/03：求人一覧・求人詳細
python3 -I tools/build_work_roles.py            # WORK 9職種の拡充（比較プレビュー）
python3 -I tools/build_work_sales.py            # WORK 営業再編（比較プレビュー＋正式WORK）
python3 -I tools/set_noindex.py on
python3 -I tools/set_entry_cta.py off   # 正式な応募先が決まったら off → on
