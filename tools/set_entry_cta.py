# -*- coding: utf-8 -*-
"""
===== ENTRY-CTA v2 =====
サイト共通の応募導線（ENTRY ページへ送るCTA）の表示状態を切り替える。

対象（renewal/ 配下すべて）：
  ・ヘッダーの ENTRY ボタン
  ・ドロワー（モバイルメニュー）の「エントリーする」
  ・フッターナビの「エントリー」
  ・ページ末尾 .entry の応募ボタン（entry/ へ向かうもの）
  ・職種紹介ページの「この職種に応募する」「この職種にエントリー」
  ・JOBS の「応募・選考について」
本文中の説明リンク（「カジュアル面談でお問い合わせください」など）は対象外。
求人ごとの「この求人に応募する」は tools/applycta.py が持つ（ここでは触らない）。

状態は3つ。どの状態でも元のマークアップは SRC コメントに残るので、行き来できる。

  off      ：何も表示しない（完全に隠す）
  preview  ：押せないボタンとして表示する ← 正式な応募先が決まるまでの既定
  on       ：元のリンクに戻す（正式な応募先が決まったら）

  python3 -I tools/set_entry_cta.py preview
  python3 -I tools/set_entry_cta.py on
  python3 -I tools/set_entry_cta.py off
"""
import glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 元のマークアップを保管するコメント。状態が変わってもこれは残る。
SRC_S = ("<!-- ===== ENTRY-CTA v2 SRC：応募CTAの元マークアップ。\n"
         "     表示状態は tools/set_entry_cta.py（off / preview / on）が切り替える。\n"
         "     ここを手で書き換えない。 =====\n")
SRC_E = "\n     ===== ENTRY-CTA v2 SRC ここまで ===== -->"
RE_SRC = re.compile(re.escape(SRC_S) + r"(.*?)" + re.escape(SRC_E), re.S)

# v1（OFF コメント）からの移行用。中身の取り出し方は同じ。
V1_S = ("<!-- ===== ENTRY-CTA v1 OFF：正式な応募先URLが未確定のため一時的に止めている。\n"
        "     tools/set_entry_cta.py on で元に戻す。 =====\n")
V1_E = "\n     ===== ENTRY-CTA v1 OFF ここまで ===== -->"
RE_V1 = re.compile(re.escape(V1_S) + r"(.*?)" + re.escape(V1_E), re.S)

# preview のときに SRC の直後へ置く、押せない表示。
RENDER_S = "<!-- ===== ENTRY-CTA v2 PREVIEW ここから ===== -->"
RENDER_E = "<!-- ===== ENTRY-CTA v2 PREVIEW ここまで ===== -->"
RE_RENDER = re.compile(r"\n?[ \t]*" + re.escape(RENDER_S) + r".*?" + re.escape(RENDER_E), re.S)

ENTRY = r'(?:\.\./)*entry/'
PATTERNS = [
    r'[ \t]*<a class="btn btn--red hdr__cta" href="' + ENTRY + r'">ENTRY.*?</a>\n',
    r'[ \t]*<a class="btn btn--red" href="' + ENTRY + r'">エントリーする.*?</a>\n',
    r'[ \t]*<a href="' + ENTRY + r'">エントリー</a>\n',
    r'[ \t]*<div class="entry__ctas"[^>]*>\s*<a class="btn[^"]*" href="' + ENTRY + r'">[^<]*<span class="btn__ico"[^>]*>▶</span></a>\s*</div>\n',
    r'[ \t]*<a class="btn btn--red btn--lg" href="' + ENTRY + r'">[^<]*<span class="btn__ico"[^>]*>▶</span></a>\n',
    r'[ \t]*<a class="btn btn--ghost btn--lg" href="' + ENTRY + r'">エントリーする<span class="btn__ico"[^>]*>▶</span></a>\n',
    r'[ \t]*<a class="btn btn--red" href="' + ENTRY + r'">この職種にエントリー<span class="btn__ico"[^>]*>▶</span></a>　?\n?',
    r'[ \t]*<p class="entry__sec"><a href="' + ENTRY + r'">応募する</a></p>\n',
]
# 対象にしないもの（応募の操作ではなく、選考の流れを読むための案内リンク）。
# ENTRY ページは「エントリーフォームは準備中です」と明示している案内ページなので、
# ここを止めると選考の流れを読めなくなる。応募できると誤認させるものでもない。
#   ・「応募・選考について」（JOBS・求人詳細）
#   ・「応募方法・選考の流れ」（FAQ）
#   ・「応募・選考について」（WORK の .entry__sec）

# 元のリンク1本を、押せない表示に置き換える。
RE_A = re.compile(r'<a\s+([^>]*?)href="' + ENTRY + r'"([^>]*)>(.*?)</a>', re.S)


def to_disabled(src):
    """SRC の中の <a href="…entry/"> を、押せない要素に変える。"""
    def one(m):
        attrs = (m.group(1) + " " + m.group(2)).strip()
        cls = re.search(r'class="([^"]*)"', attrs)
        # ボタン（.btn）は <button disabled>、それ以外のリンクは文字のまま無効表示にする
        label = re.sub(r"<span class=\"btn__ico\".*?</span>", "", m.group(3), flags=re.S).strip()
        if cls and "btn" in cls.group(1).split():
            return ('<button class="%s btn--off" type="button" disabled>%s</button>'
                    % (cls.group(1), label))
        return '<span class="applyoff">%s</span>' % label
    return RE_A.sub(one, src)


NOTE = ('<p class="applynote">※ 応募先URLの設定前です。この採用サイトは公開前の確認用のため、'
        '応募の受け付けはまだ開始していません。</p>')


def needs_note(src):
    """大きい赤の応募ボタン（ページ末尾のCTA）には、押せない理由を添える。
    ヘッダー・ドロワー・フッターの小さなCTAには付けない（同じ注記が何度も出るため）。"""
    return "btn--red" in src and "btn--lg" in src


def main(mode):
    if mode not in ("off", "preview", "on"):
        raise SystemExit("使い方：python3 -I tools/set_entry_cta.py [off|preview|on]")
    n = 0
    for ap in sorted(glob.glob(os.path.join(ROOT, "renewal/**/*.html"), recursive=True)):
        s = open(ap, encoding="utf-8").read()
        o = s
        # 1) いまの表示を外して、素の状態（SRC コメントだけ）に戻す
        s = RE_RENDER.sub("", s)
        s = RE_V1.sub(lambda m: SRC_S + m.group(1) + SRC_E, s)   # v1 → v2 へ移行
        if mode == "on":
            s = RE_SRC.sub(lambda m: m.group(1), s)
        else:
            # まだ包まれていない素のリンクを SRC で包む（on → preview/off のとき）
            s = RE_SRC.sub(lambda m: m.group(1), s)
            stash = []
            def wrap(m):
                nl = "\n" if m.group(0).endswith("\n") else ""
                stash.append(SRC_S + m.group(0).rstrip("\n") + SRC_E + nl)
                return "\x00%d\x00" % (len(stash) - 1)
            for pat in PATTERNS:
                s = re.sub(pat, wrap, s)
            s = re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], s)
            if mode == "preview":
                def render(m):
                    src = m.group(1)
                    ind = re.match(r"[ \t]*", src).group(0)
                    note = ("\n" + ind + NOTE) if needs_note(src) else ""
                    return (m.group(0) + "\n" + ind + RENDER_S + "\n"
                            + to_disabled(src) + note + "\n" + ind + RENDER_E)
                s = RE_SRC.sub(render, s)
        if s != o:
            open(ap, "w", encoding="utf-8").write(s)
            n += 1
    msg = {"off": "応募CTAを隠した", "preview": "応募CTAを押せない表示にした",
           "on": "応募CTAを有効にした"}[mode]
    print("%s：%d ファイル" % (msg, n))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "preview")
