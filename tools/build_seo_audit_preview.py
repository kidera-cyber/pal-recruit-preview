# -*- coding: utf-8 -*-
"""
===== SEOFIX v1 =====
SEO・AIO監査で「A＝既存情報だけで正しく直せる」と判定した3点だけを当てた
最小修正の比較プレビュー。

  renewal/seo-fix-preview/jobs/      JOBS一覧（見出し階層）
  renewal/seo-fix-preview/culture/   廃止ページの転送stub（canonical）
  renewal/seo-fix-preview/after-joining/

修正内容
  ① renewal/culture/ の canonical が検証用GitHub Pagesの絶対URL
     （https://kidera-cyber.github.io/.../renewal/people/）で固定されていた。
     本番ドメインへ移しても検証環境を指し続けるうえ、noindex と canonical を
     同時に出すと検索エンジンへの指示が矛盾する。ほかの転送stub2本
     （jobs/center-manager/・work/fde/）は「canonical を置かない」方針で
     統一されているため、同じ扱いにそろえる。
  ② renewal/after-joining/ の canonical が ../career/（別ページ）を指していた。
     ①と同じ理由で外す。転送は meta refresh と本文のリンクに任せる。
  ③ renewal/jobs/ の見出しが h1 → h3 → h4 と1段飛んでいた。
     職種グループを h2、求人カード名を h3 にして階層をそろえる。
     CSSは .jgroup__h / .jcard__n のクラス指定のため、見た目は変わらない。

本文・デザイン・求人条件・title・meta description・robots は変更していない。

  python3 -I tools/build_seo_audit_preview.py
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f: return f.read()
def wr(p, s):
    os.makedirs(os.path.join(ROOT, os.path.dirname(p)), exist_ok=True)
    with open(os.path.join(ROOT, p), "w", encoding="utf-8") as f: f.write(s)

NOTE = ('<!-- ===== SEOFIX v1：SEO監査で判定した「A＝既存情報だけで直せる」項目の\n'
        '     最小修正プレビュー。承認後に正式ページへ反映する。\n'
        '     本文・デザイン・求人条件・title・meta description・robots は変更していない。 ===== -->\n')

def deeper(t, n=1):
    """renewal/<page>/ → renewal/seo-fix-preview/<page>/ の1階層ぶん相対パスを足す。"""
    return re.sub(r'(href|src)="((?:\.\./)+)', lambda m: '%s="%s' % (m.group(1), "../" * (m.group(2).count("../") + n)), t)

def build():
    # ---- ① culture：絶対canonicalを外す ----
    s = rd("renewal/culture/index.html")
    old = '<link rel="canonical" href="https://kidera-cyber.github.io/pal-recruit-preview/renewal/people/">'
    assert old in s, "culture の canonical が見つからない"
    s = s.replace(old,
        '<!-- ===== SEOFIX v1：canonical を外した。検証用ドメインの絶対URLが固定されていたうえ、\n'
        '     noindex と canonical を同時に出すと指示が矛盾する。転送は meta refresh に任せる\n'
        '     （jobs/center-manager/・work/fde/ と同じ方針）。 ===== -->', 1)
    wr("renewal/seo-fix-preview/culture/index.html", NOTE + deeper(s))

    # ---- ② after-joining：別ページを指す canonical を外す ----
    s = rd("renewal/after-joining/index.html")
    old = '<link rel="canonical" href="../career/">'
    assert old in s, "after-joining の canonical が見つからない"
    s = s.replace(old,
        '<!-- ===== SEOFIX v1：canonical を外した。noindex のページから別ページを正規URLとして\n'
        '     指しており、ほかの転送stubの方針と不統一だった。 ===== -->', 1)
    wr("renewal/seo-fix-preview/after-joining/index.html", NOTE + deeper(s))

    # ---- ③ JOBS：見出し階層 h1 → h2 → h3 ----
    s = rd("renewal/jobs/index.html")
    n3 = len(re.findall(r'<h3 class="jgroup__h">', s))
    n4 = len(re.findall(r'<h4 class="jcard__n">', s))
    assert n3 and n4, "JOBS の見出しが見つからない"
    s = s.replace('<h3 class="jgroup__h">', '<h2 class="jgroup__h">').replace('</h3>\n', '</h2>\n')
    s = re.sub(r'<h4 class="jcard__n">(.*?)</h4>', r'<h3 class="jcard__n">\1</h3>', s, flags=re.S)
    s = deeper(s)
    # renewal/jobs/ 配下を指している相対リンク（openings/… dts/ など）を ../../jobs/ 起点に直す
    s = re.sub(r'(href|src)="(?!\.\./|#|https?:|/|mailto:|tel:|data:)([^"]+)"',
               lambda m: '%s="../../jobs/%s"' % (m.group(1), m.group(2)), s)
    wr("renewal/seo-fix-preview/jobs/index.html", NOTE + s)
    print("SEO最小修正プレビューを生成：renewal/seo-fix-preview/"
          "（culture / after-joining / jobs：職種グループ %d個・求人カード %d件を昇格）" % (n3, n4))

if __name__ == "__main__":
    build()
