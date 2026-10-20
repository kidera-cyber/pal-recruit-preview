# -*- coding: utf-8 -*-
"""
===== ENTRY-CTA v1 =====
正式な応募先URLが確定するまで、応募CTA（エントリー導線）を一時的に止める。

止める対象（renewal/ 配下すべて）：
  ・ヘッダーの ENTRY ボタン
  ・ドロワーの「エントリーする」
  ・フッターナビの「エントリー」
  ・ページ末尾 .entry の応募ボタン（entry/ へ向かうもの）
  ・求人カード／募集要項の「この求人に応募する」「この職種にエントリー」
  ・JOBS の「カジュアル面談・エントリーについて」

止め方は削除ではなくコメントアウト（マーカー付き）なので、
正式な応募先が決まったら off → on のコマンド1つで元に戻せる。
本文中の説明リンク（「カジュアル面談でお問い合わせください」など）は対象外。

  止める：python3 -I tools/set_entry_cta.py off
  戻す  ：python3 -I tools/set_entry_cta.py on      ← 正式な応募先が決まったら
"""
import glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S, E = "<!-- ===== ENTRY-CTA v1 OFF：正式な応募先URLが未確定のため一時的に止めている。\n     tools/set_entry_cta.py on で元に戻す。 =====\n", "\n     ===== ENTRY-CTA v1 OFF ここまで ===== -->"
RE_OFF = re.compile(re.escape(S) + r"(.*?)" + re.escape(E), re.S)

ENTRY = r'(?:\.\./)*entry/'
PATTERNS = [
    # ヘッダーCTA / ドロワー / フッターナビ
    r'[ \t]*<a class="btn btn--red hdr__cta" href="' + ENTRY + r'">ENTRY.*?</a>\n',
    r'[ \t]*<a class="btn btn--red" href="' + ENTRY + r'">エントリーする.*?</a>\n',
    r'[ \t]*<a href="' + ENTRY + r'">エントリー</a>\n',
    # ページ末尾の応募ボタン群（中のリンクがすべて entry/ のとき丸ごと）
    r'[ \t]*<div class="entry__ctas"[^>]*>\s*<a class="btn[^"]*" href="' + ENTRY + r'">[^<]*<span class="btn__ico"[^>]*>▶</span></a>\s*</div>\n',
    # 個別の応募ボタン
    r'[ \t]*<a class="btn btn--red btn--lg" href="' + ENTRY + r'">[^<]*<span class="btn__ico"[^>]*>▶</span></a>\n',
    r'[ \t]*<a class="btn btn--ghost btn--lg" href="' + ENTRY + r'">エントリーする<span class="btn__ico"[^>]*>▶</span></a>\n',
    r'[ \t]*<a class="btn btn--red" href="' + ENTRY + r'">この職種にエントリー<span class="btn__ico"[^>]*>▶</span></a>　?\n?',
    r'[ \t]*<a class="btn btn--ghost" href="' + ENTRY + r'">カジュアル面談・エントリーについて<span class="btn__ico"[^>]*>▶</span></a>\n',
    r'[ \t]*<p class="rv"[^>]*><a class="btn btn--ghost" href="' + ENTRY + r'">カジュアル面談・エントリーについて<span class="btn__ico"[^>]*>▶</span></a></p>\n',
    # ページ末尾の副導線（応募する／応募方法・選考の流れ）
    r'[ \t]*<p class="entry__sec"><a href="' + ENTRY + r'">[^<]*</a></p>\n',
    r'　<a class="btn btn--ghost" href="' + ENTRY + r'">応募方法・選考の流れ<span class="btn__ico"[^>]*>▶</span></a>',
]

def main(mode):
    n = 0
    for ap in glob.glob(os.path.join(ROOT, "renewal/**/*.html"), recursive=True):
        s = open(ap, encoding="utf-8").read(); o = s
        if mode == "on":
            s = RE_OFF.sub(lambda m: m.group(1), s)
        else:
            s = RE_OFF.sub(lambda m: m.group(1), s)   # 二重に包まないよう、一度戻してから包む
            # 包んだ箇所はいったん退避し、別のパターンが入れ子で包まないようにする
            stash = []
            def wrap(m):
                stash.append(S + m.group(0).rstrip("\n") + E + "\n")
                return "\x00%d\x00\n" % (len(stash) - 1)
            for pat in PATTERNS:
                s = re.sub(pat, wrap, s)
            s = re.sub(r"\x00(\d+)\x00\n", lambda m: stash[int(m.group(1))], s)
        if s != o:
            open(ap, "w", encoding="utf-8").write(s); n += 1
    print("%s：%d ファイル" % ("応募CTAを止めた" if mode == "off" else "応募CTAを戻した", n))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "off")
