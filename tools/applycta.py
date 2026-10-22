# -*- coding: utf-8 -*-
"""
===== APPLY v1 =====
求人ごとの応募ボタン（「この求人に応募する」）を、1か所のデータから作る。

応募先の管理場所は data/jobs-openings.json だけ。
  apply_urls.default_url … 全求人に共通の応募先
  openings[].apply_url   … その求人だけ別の応募先にしたいとき（default_url より優先）

状態は2つ。
  STATE 1（プレビュー）応募先が null  → 押せないボタン（<button disabled>）＋注記を出す
  STATE 2（応募受付中）応募先が URL   → その URL への <a> になる
求人ごとに判定するので、一部の求人だけ先に受付を始めることもできる。
仮のURLや架空のメールアドレスは入れない。応募先が無い求人は有効化されない。

使い方
  import applycta                        … ビルドスクリプトから部品として使う
  python3 -I tools/applycta.py           … マーカーのあるページを現在のデータに合わせる
  python3 -I tools/applycta.py --check   … 未設定の求人を一覧表示（本番公開前のチェック用）

直接編集で管理しているページ（renewal/jobs/dts/ など）は、
APPLY v1 のマーカーで応募ボタンを囲んでおけば、このスクリプトが中身を差し替える。
"""
import glob, io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABEL = "この求人に応募する"
NOTE = ("※ 応募先URLの設定前です。この採用サイトは公開前の確認用のため、"
        "応募の受け付けはまだ開始していません。")

S = "<!-- ===== APPLY v1 START job=%s：応募ボタン。応募先は data/jobs-openings.json\n" \
    "           （apply_urls.default_url ／ この求人の apply_url）で決まる。\n" \
    "           tools/applycta.py が状態を切り替えるため、手で書き換えない。 ===== -->\n"
E = "<!-- ===== APPLY v1 END ===== -->"
RE_BLK = re.compile(r"[ \t]*<!-- ===== APPLY v1 START job=([a-z0-9-]+)：.*?===== APPLY v1 END ===== -->", re.S)


def load():
    with io.open(os.path.join(ROOT, "data/jobs-openings.json"), encoding="utf-8") as f:
        return json.load(f)


def url_of(D, o):
    """この求人の応募先。未設定なら None。"""
    return o.get("apply_url") or D.get("apply_urls", {}).get("default_url") or None


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


# ---------------------------------------------------------------- 求人詳細の末尾
def detail_block(job_id, url, indent="      "):
    """求人詳細ページ末尾の応募ボタン。マーカーごと返す。"""
    i = indent
    head = i + S % job_id
    if url:
        body = (i + '<div class="entry__ctas">\n'
                + i + '  <a class="btn btn--red btn--lg" href="%s">%s'
                      '<span class="btn__ico" aria-hidden="true">▶</span></a>\n' % (esc(url), LABEL)
                + i + "</div>\n")
    else:
        body = (i + '<div class="entry__ctas">\n'
                + i + '  <button class="btn btn--red btn--lg btn--off" type="button" disabled\n'
                + i + '          aria-describedby="apply-note">%s</button>\n' % LABEL
                + i + "</div>\n"
                + i + '<p class="applynote" id="apply-note">%s</p>\n' % NOTE)
    return head + body + i + E


# ---------------------------------------------------------------- JOBS 一覧のカード
def card_button(url, indent="        "):
    """求人カードの応募ボタン。募集中の求人にだけ付ける。"""
    if url:
        return (indent + '<p class="jcard__applyrow"><a class="jcard__apply" href="%s">%s'
                         '<i aria-hidden="true">&#8594;</i></a></p>' % (esc(url), LABEL))
    return (indent + '<p class="jcard__applyrow"><button class="jcard__apply" type="button" disabled>'
                     '%s</button></p>' % LABEL)


# ---------------------------------------------------------------- 同期（直接編集ページ用）
def sync():
    D = load()
    by_id = {o["id"]: o for o in D["openings"]}
    n_file = n_blk = 0
    for ap in sorted(glob.glob(os.path.join(ROOT, "renewal/**/*.html"), recursive=True)):
        s = io.open(ap, encoding="utf-8").read()
        def one(m):
            nonlocal n_blk
            jid = m.group(1)
            o = by_id.get(jid)
            if o is None:
                raise SystemExit("APPLY v1：%s に無い求人ID '%s' が %s にあります" %
                                 ("data/jobs-openings.json", jid, ap))
            indent = re.match(r"[ \t]*", m.group(0)).group(0)
            n_blk += 1
            return detail_block(jid, url_of(D, o), indent)
        out = RE_BLK.sub(one, s)
        if out != s:
            io.open(ap, "w", encoding="utf-8").write(out)
            n_file += 1
    return n_file, n_blk


# ---------------------------------------------------------------- 公開前チェック
def missing():
    """応募先が未設定の「募集中」求人を返す。"""
    D = load()
    return [o for o in D["openings"] if o["status"] == "open" and not url_of(D, o)]


if __name__ == "__main__":
    if "--check" in sys.argv:
        ng = missing()
        if ng:
            print("応募先URLが未設定の求人 %d件：" % len(ng))
            for o in ng:
                print("  - %-26s %s" % (o["id"], o["title"]))
            print("data/jobs-openings.json の apply_urls.default_url "
                  "または各求人の apply_url に正式な応募先を入れてください。")
            sys.exit(1)
        print("応募先URL：募集中の求人すべてに設定済み")
    else:
        f, b = sync()
        ng = missing()
        print("応募ボタンを同期：%d ファイル／%d 箇所%s"
              % (f, b, ("　※ 応募先が未設定の求人 %d件は押せない状態で表示" % len(ng)) if ng else ""))
