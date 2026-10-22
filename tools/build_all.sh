#!/bin/sh
# 生成物をまとめて作り直す。ビルド後は必ず noindex を付け直す。
# （公開前の確認用サイトのため。本番公開時は最後の行を set_noindex.py off に変える）
set -e
cd "$(dirname "$0")/.."
python3 -I tools/build_logistics_operation.py   # LEVEL 02：物流センター運営の仕事
python3 -I tools/build_jobs.py                  # LEVEL 01/03：求人一覧・求人詳細
python3 -I tools/build_large_driver.py          # 10tドライバーの募集要項
# FAQ（renewal/faq/）は直接編集して管理する。data/faq.json と tools/build_faq.py は
# 50問への再設計案の記録として残している（--official を付けない限り公開FAQは上書きしない）。
# WORK（renewal/work/）は比較プレビューからの移行が完了したため、直接編集して管理する。
# 文章の記録は tools/build_work_roles.py と tools/build_work_sales.py に残している。
python3 -I tools/sync_role_status.py           # 募集ステータス（募集中／募集なし）をHOMEとJOBSで同期
python3 -I tools/applycta.py                   # 応募ボタンを data/jobs-openings.json の応募先に合わせる
python3 -I tools/set_domain.py                   # 本番ドメイン依存のメタ（canonical/OGP/sitemap/robots）
python3 -I tools/set_noindex.py on
# 共通の応募CTA（ヘッダー／ドロワー／フッター／ページ末尾）の表示状態。
# preview＝押せないボタンとして表示（正式な応募先が決まるまで）／on＝有効化／off＝非表示
python3 -I tools/set_entry_cta.py preview
