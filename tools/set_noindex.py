# -*- coding: utf-8 -*-
"""
===== NOINDEX v1 =====
このプレビュー環境（GitHub Pages）を検索インデックスさせないための一括設定。

本番公開前は、求人詳細の JobPosting を含めて検索結果に出す必要がないため、
renewal/ 配下のすべてのHTMLに <meta name="robots" content="noindex,nofollow"> を入れる。
構造化データ・canonical・本文はそのまま残すので、実装の確認には影響しない。

  付ける：python3 -I tools/set_noindex.py on
  外す  ：python3 -I tools/set_noindex.py off     ← 本番公開時はこれ

すでに robots メタを持つページ（旧URLの転送ページ：noindex,follow）は触らない。
"""
import glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = ('<!-- ===== NOINDEX v1：公開前の確認用サイトのため検索インデックスさせない。\n'
       '     本番公開時に tools/set_noindex.py off で一括削除する。 ===== -->\n'
       '<meta name="robots" content="noindex,nofollow">\n')
RE_TAG = re.compile(r'<!-- ===== NOINDEX v1：.*?===== -->\n<meta name="robots" content="noindex,nofollow">\n', re.S)

def main(mode):
    n = 0
    for ap in glob.glob(os.path.join(ROOT, "renewal/**/*.html"), recursive=True):
        s = open(ap, encoding="utf-8").read(); o = s
        if "/jobs/openings/" in ap.replace("\\", "/"):
            continue                          # 求人詳細はビルド側で noindex,follow を出力する
        if mode == "off":
            s = RE_TAG.sub("", s)
        else:
            if RE_TAG.search(s) or 'name="robots"' in s:
                continue                      # 既に指定済み（転送ページ等）は触らない
            m = re.search(r'<link rel="canonical"[^>]*>\n', s)
            if m:
                s = s[:m.end()] + TAG + s[m.end():]
            else:
                m2 = re.search(r'<meta name="viewport"[^>]*>\n', s)
                if not m2: continue
                s = s[:m2.end()] + TAG + s[m2.end():]
        if s != o:
            open(ap, "w", encoding="utf-8").write(s); n += 1
    print("%s：%d ファイル" % ("noindex を付与" if mode == "on" else "noindex を削除", n))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "on")
