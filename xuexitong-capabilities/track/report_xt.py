# -*- coding: utf-8 -*-
"""学习通巡检汇总（本地，不接浏览器）。

用法：
  python report_xt.py           只打印，不写基线
  python report_xt.py --final   写 baseline_xt.json / 存档 runs/ / 写 last_report_xt.md

输出：学习通版「分课分节」台账 + 增量标记。
"""
import json
import os
import sys
import time

BASE = os.environ.get("XT_WATCH_DIR") or os.path.join(os.path.expanduser("~"), "xt_watch")
STATE = os.path.join(BASE, "xt_state.json")
BASE_FILE = os.path.join(BASE, "baseline_xt.json")
RUNS = os.path.join(BASE, "runs")
LASTREP = os.path.join(BASE, "last_report_xt.md")


def load(p, default=None):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}


def pick_classes(courses):
    """同标题多班次归并；返回 (分组统计, 每组班次列表)。已结束课程不展示。"""
    groups = {}
    for c in courses:
        if (c.get("status") or "") == "已结束":
            continue
        groups.setdefault(c.get("title") or c.get("clazzid"), []).append(c)
    return groups, list(groups.values())


def score_of(cid, scan, scores):
    sc = scores.get(cid) or {}
    sk = scan.get(cid) or {}
    ch = sk.get("chapter") or {}
    st = sk.get("study") or {}
    wk = sk.get("work") or {}
    task = st.get("task") or sc.get("task")
    return {
        "done": ch.get("done") if ch.get("done") is not None else (task[0] if task else None),
        "total": ch.get("total") if ch.get("total") is not None else (task[1] if task else None),
        "work_pr": wk.get("progress") or "",
        "work_rows": wk.get("rows") or [],
        "unsub": wk.get("unsub") or [],
        "task": task,
        "att": sc.get("attendance"),
        "rate": sc.get("rate") or "",
        "rank": sc.get("rank") or "",
        "points": sc.get("points"),
        "online": sc.get("online"),
    }


def best_of(arr, scan, scores):
    """同一门课多个班次时，选信息量最大的那个班次展示。"""
    best, best_weight = None, -1
    for c in arr:
        d = score_of(c["clazzid"], scan, scores)
        w = 0
        if d["done"] is not None:
            w += (d["done"] or 0) * 10 + 1
        w += len(d["work_rows"])
        if d["task"]:
            w += d["task"][0]
        if w > best_weight:
            best, best_weight = (c, d), w
    return best


def main(final=False):
    st = load(STATE)
    base = load(BASE_FILE)
    courses = st.get("courses") or []
    scan = st.get("scan") or {}
    scores = st.get("scores") or {}
    old = (base.get("items") or {})
    groups, reps = pick_classes(courses)
    stamp = time.strftime("%Y%m%d_%H%M")

    n_cls = sum(len(v) for v in groups.values())
    lines = ["共 %d 门课（%d 个班次）" % (len(groups), n_cls)]
    new_rows = []
    store = {}
    any_gap = False

    for arr in reps:
        title = arr[0].get("title")
        c, d = best_of(arr, scan, scores)
        cid = c["clazzid"]
        store[cid] = {"unsub": d["unsub"], "done": d["done"], "total": d["total"]}
        old_unsub = set((old.get(cid) or {}).get("unsub") or [])
        fresh = [t for t in d["unsub"] if t not in old_unsub]
        bullets = []
        if d["done"] is not None and d["total"]:
            gap = d["total"] - d["done"]
            if gap > 0:
                any_gap = True
            bullets.append("章节任务点 %s/%s（未完成 %d）" % (d["done"], d["total"], gap))
        if d["unsub"]:
            bullets.append("未交作业：%s%s" % ("、".join(d["unsub"]), "（新增）" if fresh else ""))
        elif d["work_pr"] and not d["work_pr"].startswith("0/0"):
            bullets.append("作业 %s" % d["work_pr"])
        if d["att"] and sum(d["att"]) > 0:
            bullets.append("签到 出勤 %d / 缺勤 %d（出勤率 %s）" % (d["att"][0], d["att"][1], d["rate"] or "-"))
        if fresh:
            new_rows.append((title, fresh))
        if bullets:
            lines.append("")
            lines.append("**%s**" % title)
            lines.extend("- " + b for b in bullets)

    if not any_gap and not new_rows:
        lines = ["共 %d 门课（%d 个班次）" % (len(groups), n_cls)]
        if not scores:
            lines.append("NEED_SCORES")
        for arr in reps:
            title = arr[0].get("title")
            c, d = best_of(arr, scan, scores)
            bits = []
            if d["task"]:
                bits.append("任务点 %d/%d" % (d["task"][0], d["task"][1]))
            if d["points"] is not None:
                bits.append("积分 %g" % d["points"])
            if d["rank"]:
                bits.append("排名 %s" % d["rank"])
            if d["rate"]:
                bits.append("出勤率 %s" % d["rate"])
            if d["online"] is not None:
                bits.append("在线学习 %d 次" % d["online"])
            if bits:
                lines.append("- %s：%s" % (title, "、".join(bits)))
            elif d["done"] is not None:
                lines.append("- %s：任务点 %s/%s" % (title, d["done"], d["total"]))

    text = "\n".join(lines)
    print(text)
    if not final:
        return lines

    base.update({
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:00+08:00"),
        "scope": [c["clazzid"] for c in courses],
        "course_names": {c["clazzid"]: c.get("title") for c in courses},
        "items": store,
    })
    with open(BASE_FILE, "w", encoding="utf-8") as f:
        json.dump(base, f, ensure_ascii=False, indent=2)

    os.makedirs(RUNS, exist_ok=True)
    with open(os.path.join(RUNS, stamp + "_script.md"), "w", encoding="utf-8") as f:
        f.write(text + "\n")
    with open(os.path.join(BASE, "last_run_xt_%s.md" % stamp), "w", encoding="utf-8") as f:
        f.write(text + "\n")
    with open(LASTREP, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    return lines


if __name__ == "__main__":
    main("--final" in sys.argv)
