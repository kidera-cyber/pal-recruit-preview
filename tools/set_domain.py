# -*- coding: utf-8 -*-
"""
===== DOMAIN v1 =====
本番ドメインに依存する設定を1か所から切り替える。

ドメインが決まるまで（data/site.json の production_origin が null）は、
いまの GitHub Pages の見え方を変えない。
  canonical       … 相対自己参照（./）のまま
  og:url / og:image … 出さない（絶対URLが必要なため）
  パンくずの item  … 入れない
  sitemap.xml     … 作らない（絶対URLが必要なため）
  robots.txt      … プレビュー用（全ページ Disallow）を置く

本番ドメインが決まったら data/site.json の production_origin に入れて
tools/build_all.sh を流すだけで、上のすべてが本番用に切り替わる。
ドメインを推測で入れないこと。

  python3 -I tools/set_domain.py          … site.json の設定どおりに反映
  python3 -I tools/set_domain.py --status … いまの状態を表示するだけ
"""
import glob, io, json, os, posixpath, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK_S = "<!-- ===== DOMAIN v1 START：本番ドメインに依存するメタ。tools/set_domain.py が作る。 ===== -->"
MARK_E = "<!-- ===== DOMAIN v1 END ===== -->"
RE_MARK = re.compile(r"\n?[ \t]*" + re.escape(MARK_S) + r".*?" + re.escape(MARK_E), re.S)

ROBOTS_PREVIEW = """# 公開前の確認用サイト（GitHub Pages）。検索エンジンには見せない。
# 本番ドメインが決まったら data/site.json の production_origin を入れて
# tools/build_all.sh を流すと、本番用の robots.txt に置き換わる。
User-agent: *
Disallow: /
"""


def load():
    with io.open(os.path.join(ROOT, "data/site.json"), encoding="utf-8") as f:
        return json.load(f)


def page_path(ap):
    """renewal/jobs/index.html → /jobs/ のような、サイト内の公開パス。"""
    rel = os.path.relpath(ap, ROOT).replace("\\", "/")
    rel = rel[len("renewal"):] if rel.startswith("renewal") else "/" + rel
    return rel[: -len("index.html")] if rel.endswith("index.html") else rel


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")


def main(status_only=False):
    C = load()
    origin = C.get("production_origin")
    base = (C.get("base_path") or "").rstrip("/")
    if status_only:
        print("production_origin:", origin if origin else "未設定（プレビューのまま）")
        return

    pages, n = [], 0
    for ap in sorted(glob.glob(os.path.join(ROOT, "renewal/**/*.html"), recursive=True)):
        s = io.open(ap, encoding="utf-8").read()
        o = s
        s = RE_MARK.sub("", s)                      # 前回の出力を外す
        if origin:
            url = origin + base + page_path(ap)
            title = re.search(r"<title>(.*?)</title>", s, re.S)
            desc = re.search(r'<meta name="description" content="(.*?)">', s, re.S)
            img = origin + base + "/" + (C.get("og_image") or "assets/hero-bg.jpg").lstrip("/")
            blk = ("\n" + MARK_S
                   + '\n<meta property="og:url" content="%s">' % esc(url)
                   + '\n<meta property="og:image" content="%s">' % esc(img)
                   + '\n<meta name="twitter:image" content="%s">' % esc(img)
                   + "\n" + MARK_E)
            # canonical を絶対URLにする（転送ページは canonical を置かない方針なので触らない）
            s = re.sub(r'<link rel="canonical" href="\./">',
                       '<link rel="canonical" href="%s">' % esc(url), s, count=1)
            # パンくず（BreadcrumbList）の item を絶対URLにする。
            # Google は item に絶対URLを求めるが、プレビューでは相対（"../../"）で出している。
            here = page_path(ap)
            def abs_item(mo):
                rel = mo.group(1)
                if rel.startswith(("http://", "https://")):
                    return mo.group(0)
                p2 = posixpath.normpath(posixpath.join(here, rel))
                if not p2.endswith("/"):
                    p2 += "/"
                return '"item": "%s"' % esc(origin + base + p2)
            s = re.sub(r'"item":\s*"([^"]+)"', abs_item, s)
            s = s.replace("</head>", blk + "\n</head>", 1) if "</head>" in s else s
            if title and desc:
                pages.append(url)
        if s != o:
            io.open(ap, "w", encoding="utf-8").write(s)
            n += 1

    # robots.txt
    rp = os.path.join(ROOT, "robots.txt")
    if origin:
        body = ("User-agent: *\nAllow: /\n\nSitemap: %s%s/sitemap.xml\n" % (origin, base))
    else:
        body = ROBOTS_PREVIEW
    io.open(rp, "w", encoding="utf-8").write(body)

    # sitemap.xml（本番ドメインが決まってから作る）
    sp = os.path.join(ROOT, "sitemap.xml")
    if origin:
        ex = set(C.get("sitemap_exclude") or [])
        urls = []
        for ap in sorted(glob.glob(os.path.join(ROOT, "renewal/**/*.html"), recursive=True)):
            rel = os.path.relpath(ap, ROOT).replace("\\", "/")
            if rel in ex:
                continue
            urls.append(origin + base + page_path(ap))
        xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "".join("  <url><loc>%s</loc></url>\n" % esc(u) for u in urls)
               + "</urlset>\n")
        io.open(sp, "w", encoding="utf-8").write(xml)
        print("本番ドメイン %s を反映：%d ファイル／sitemap.xml %d件／robots.txt（本番用）"
              % (origin, n, len(urls)))
    else:
        if os.path.exists(sp):
            os.remove(sp)
        print("本番ドメイン未設定：canonical は相対のまま／og:url・og:image なし／"
              "sitemap.xml は作らない／robots.txt はプレビュー用（%d ファイルを整理）" % n)


if __name__ == "__main__":
    main("--status" in sys.argv)
