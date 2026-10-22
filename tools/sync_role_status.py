# -*- coding: utf-8 -*-
"""
===== ROLESTAT v1 =====
公開画面の募集ステータスを「募集中」「募集なし」の2種類だけにそろえ、
HOME の職種カードと JOBS の求人データを同期する。

  renewal/index.html   FIND YOUR FIELD の職種カード9件
  renewal/jobs/        「現在の募集状況について」の3職種

判定はすべて data/jobs-openings.json。
  その職種に status="open" の求人が1件でもある     → 募集中（募集要項を見るCTAあり）
  status="upcoming" の求人だけがある               → 募集予定（募集要項を見るCTAあり）
  どちらも無い                                     → 募集なし（CTAなし）

内部で確認中でも公開画面は「募集なし」。「確認中」「募集確認中」「通年募集」などは使わない。
求人が追加・終了したら、このスクリプトを流すだけで HOME と JOBS の表示がそろう。

  python3 -I tools/sync_role_status.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f: return f.read()
def wr(p, s):
    with open(os.path.join(ROOT, p), "w", encoding="utf-8") as f: f.write(s)

# HOME の職種カード（work/#role-xxx）→ その職種に対応する求人ID
# 求人を増やしたら、ここにも登録する。登録のない職種は常に「募集なし」。
ROLE_JOBS = {
    "role-bpo":      ["funabashi-associate", "atsugi-member", "higashihiroshima-member", "suma-manager"],
    "role-clean":    [],
    "role-fde":      ["fde-associate", "fde-leader"],
    "role-system":   ["system-engineer"],
    "role-dts":      ["dts-route-driver", "large-route-driver"],
    "role-sales":    ["engagement-member"],
    "role-mkt":      [],
    "role-staffing": ["staffing-sales-leader"],
    "role-corp":     ["hr"],
}
# 募集中のとき「募集要項を見る」が指す先（JOBS の職種グループ）
# ===== JOBLINK v1 =====
# 人材派遣営業は、JOBS では「営業」グループ（#job-sales）の中に
# エンゲージメント・新規営業と並んで載っている。#job-sales を指すと
# 一般営業の求人が先に目に入るため、該当する募集要項へ直接送る。
# 求人が増えたときに黙って古いリンクが残らないよう、
# 直リンクの職種は「公開中の求人が1件」であることを下で検証している。
ROLE_ANCHOR = {"role-bpo": "#job-bpo", "role-fde": "#job-fde", "role-system": "#job-system",
               "role-dts": "#job-driver", "role-sales": "#job-sales",
               "role-staffing": "openings/staffing-sales-leader/",
               "role-corp": "#job-hr"}
# 「グループではなく個別の募集要項」へ送る職種。求人が2件以上になったら止める。
ROLE_DIRECT = {"role-staffing"}
# 募集予定のときにカードへ出すCTAの文言（Corporate は人事だけが募集予定のため職種名を添える）
ROLE_CTA = {"role-corp": "人事の募集要項を見る"}

# JOBS「現在の募集状況について」に残す職種 → 求人ID（いずれも求人なし）
# ===== HRJOB v1：Corporate は人事が募集予定になったため、この節から外して
# 「今、募集している仕事」側（人事 / HR グループ）へ移した。
RSTAT_JOBS = {"job-marketing": [], "job-clean": []}

OPEN_LABEL, SOON_LABEL, OFF_LABEL = "募集中", "募集予定", "募集なし"

def open_ids(D):
    return {o["id"] for o in D["openings"] if o["status"] == "open"}

def soon_ids(D):
    return {o["id"] for o in D["openings"] if o["status"] == "upcoming"}

def sync_home(D):
    p = "renewal/index.html"
    s = rd(p); live = open_ids(D); soon = soon_ids(D); n_open = n_soon = n_off = 0

    def one(m):
        nonlocal n_open, n_soon, n_off
        li = m.group(0)
        role = re.search(r'href="work/#(role-[a-z]+)"', li)
        if not role: return li
        key = role.group(1)
        ids = set(ROLE_JOBS.get(key, []))
        if ids & live:   state, label, cls = "open", OPEN_LABEL, "fchip__st"
        elif ids & soon: state, label, cls = "soon", SOON_LABEL, "fchip__st fchip__st--soon"
        else:            state, label, cls = "off",  OFF_LABEL,  "fchip__st fchip__st--off"
        hiring = state in ("open", "soon")
        if key in ROLE_DIRECT and len(ids & (live | soon)) > 1:
            raise SystemExit(
                "%s の求人が %d 件になりました。ROLE_ANCHOR の直リンクをグループの"
                "アンカーに戻すか、送り先を選び直してください。" % (key, len(ids & (live | soon))))
        li = re.sub(r'<span class="fchip__st[^"]*"><b>[^<]*</b></span>',
                    '<span class="%s"><b>%s</b></span>' % (cls, label), li, count=1)
        # 募集要項を見るCTA：募集中・募集予定のときだけ置く。募集要項のページが無いのにリンクを残さない。
        li = re.sub(r'\s*<p class="role-chip__cta">.*?</p>', "", li, flags=re.S)
        if hiring:
            cta = ('\n          <p class="role-chip__cta"><a href="jobs/%s">%s'
                   '<i aria-hidden="true">&#8594;</i></a></p>'
                   % (ROLE_ANCHOR.get(key, ""), ROLE_CTA.get(key, "募集要項を見る")))
            # CTAを外したあとの改行・字下げも吸収して、何度流しても同じ形になるようにする
            li = re.sub(r"</a>\s*</li>\s*$", "</a>" + cta + "\n        </li>", li)
            n_open += 1 if state == "open" else 0
            n_soon += 1 if state == "soon" else 0
        else:
            li = re.sub(r"</a>\s*</li>\s*$", "</a></li>", li)
            n_off += 1
        return li

    i = s.index('<ul class="role-chips'); j = s.index("</ul>", i)
    s = s[:i] + re.sub(r"<li[^>]*>.*?</li>", one, s[i:j], flags=re.S) + s[j:]
    wr(p, s)
    return n_open, n_soon, n_off

def sync_rstat(D):
    p = "renewal/jobs/index.html"
    s = rd(p); live = open_ids(D); n = 0
    drop = []
    def one(m):
        nonlocal n
        li = m.group(0)
        key = re.search(r'id="(job-[a-z]+)"', li).group(1)
        if key not in RSTAT_JOBS:
            drop.append(key)
            return ""   # 募集予定・募集中になった職種はこの節から外す
        hiring = bool(set(RSTAT_JOBS[key]) & live)
        li = re.sub(r'<span class="rstat__s[^"]*">[^<]*</span>',
                    '<span class="rstat__s%s">%s</span>' % ("" if hiring else " rstat__s--off",
                                                            OPEN_LABEL if hiring else OFF_LABEL), li, count=1)
        n += 1
        return li
    i = s.index('<ul class="rstat'); j = s.index("</ul>", i)
    s = s[:i] + re.sub(r"[ \t]*<li id=.*?</li>\n?", one, s[i:j], flags=re.S) + s[j:]
    wr(p, s)
    return n, drop

if __name__ == "__main__":
    D = json.loads(rd("data/jobs-openings.json"))
    a, b, c = sync_home(D)
    d, drop = sync_rstat(D)
    print("募集ステータスを同期：HOME 募集中 %d件／募集予定 %d件／募集なし %d件"
          " ／ JOBS 現在の募集状況 %d件%s" % (a, b, c, d, ("（%s を除外）" % "・".join(drop)) if drop else ""))
