# -*- coding: utf-8 -*-
"""学习通（chaoxing）只读巡检 —— 浏览器侧脚本。

四模式：
  health     登录态 + 课程入口 + 课程卡片自检
  discover   课程清单 -> xt_state.json['courses']
  scan       每门课：章节任务点进度 + 作业清单（标题/状态）
  scores     每门课：学习记录（任务点、排名、积分、签到出勤、作业计数）

调用（在 bu cell 内，单块 < 2 分钟）：
    import aha_browser_use as bu
    g={'bu':bu,'MODE':'health','__name__':'__main__'}
    exec(open(r'<仓库路径>\\xuexitong-capabilities\\track\\scan_xt_bu.py',encoding='utf-8').read(), g); print(g['OUT'])

只读：不提交作业、不签到、不点答题、不进考试。
"""
import json
import os
import re
import time

BASE = os.environ.get("XT_WATCH_DIR") or os.path.join(os.path.expanduser("~"), "xt_watch")
STATE = os.path.join(BASE, "xt_state.json")
LAST = os.path.join(BASE, "scan_last_out.txt")

INDEX = "https://i.chaoxing.com/base?ws=1"

JS_MENU = ("(function(){var a=[].slice.call(document.querySelectorAll('a')).filter(function(x)"
           "{return (x.href||'').indexOf('visit/interaction')>=0;});return a.length?a[0].href:'';})()")

JS_MARK_MENU = ("(function(){var t=null;document.querySelectorAll('li').forEach(function(x){"
                "var s=(x.innerText||'').trim().replace(/\\s+/g,'');if(s==='课程'){t=x;}});"
                "if(!t)return '';t.id='tmp-menu-course';return 'ok';})()")

JS_FRAME_SRC = ("(function(){var f=document.querySelector('#frame_content');return f?(f.src||''):'';})()")

JS_CARDS = ("(function(){var out=[];document.querySelectorAll('div.course.learnCourse').forEach(function(c){"
            "var a=c.querySelector('a[href*=\"stucoursemiddle\"]');if(!a)return;"
            "var nmEl=c.querySelector('.course-name');"
            "var nm=((nmEl&&(nmEl.getAttribute('title')||nmEl.innerText))||'').trim().split('\\n')[0];"
            "var teEl=c.querySelector('p.line2.color3');var te=teEl?teEl.innerText.trim():'';"
            "var q={courseid:'',clazzid:'',cpi:''};try{var u=new URL(a.href);['courseid','clazzid','cpi'].forEach(function(k){q[k]=u.searchParams.get(k)||'';});}catch(e){}"
            "var pvEl=c.querySelector('.btm-cover');var pr=pvEl?pvEl.innerText.replace(/\\s+/g,' '):'';"
            "var txt=(c.innerText||'').replace(/\\s+/g,' ');"
            "out.push({title:nm,teacher:te.replace(/^置顶\\s*/,''),courseid:q.courseid,clazzid:q.clazzid,cpi:q.cpi,"
            "progress:pr,status:/(课程已结束|已结束)/.test(txt)?'已结束':'进行中',full:txt.slice(0,120)});});return out;})()")

JS_IFR = ("(function(){var o={};document.querySelectorAll('iframe').forEach(function(f){"
          "var k=f.id||f.getAttribute('name')||'x';o[k]=f.src||'';});return o;})()")

JS_WORK = ("(function(){var rows=[];document.querySelectorAll('li[onclick*=goTask]').forEach(function(li){"
           "var lb=li.getAttribute('aria-label')||'';var ps=lb.split(';');var t='',st='';"
           "if(ps.length>=2){t=ps[0].trim();st=ps[1].trim();}"
           "else{var p=li.querySelector('p');t=p?p.innerText.trim():'';}"
           "rows.push({t:t,s:st});});"
           "var b=document.querySelector('.work-progress-box');"
           "var pr=b?b.innerText.replace(/\\s+/g,' '):'';return {pr:pr,rows:rows};})()")

JS_TEXT3K = "((document.body&&document.body.innerText)||'').slice(0,3000)"
JS_TEXT4K = "((document.body&&document.body.innerText)||'').slice(0,4000)"


def _bu():
    return globals().get("BU")


def _set_out(mode, ok, msg):
    global OUT
    OUT = "%s %s %s" % (mode, "ok" if ok else "FAIL", msg)
    try:
        with open(LAST, "w", encoding="utf-8") as f:
            f.write(OUT)
    except Exception:
        pass


def _load():
    try:
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(st):
    st["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)


def _nav(url, wait=3.0):
    BU.navigate(url)
    time.sleep(wait)


def _url():
    try:
        return BU.current_tab().get("url", "") or ""
    except Exception:
        return ""


def _open_courses():
    """从个人空间进入课程列表；返回卡片数组，失败抛异常。"""
    _nav(INDEX, 3)
    u = _url()
    if "passport2" in u or "/login" in u:
        raise RuntimeError("login 失效（停在登录页）")
    href = BU.js(JS_MENU)
    if not href:
        # 左栏「课程」是纯 li，需要真点击
        if BU.js(JS_MARK_MENU) != "ok":
            raise RuntimeError("左栏找不到「课程」菜单项")
        BU.click("#tmp-menu-course")
        time.sleep(4)
        href = BU.js(JS_FRAME_SRC)
    if not href:
        raise RuntimeError("课程入口 iframe 未出现")
    _nav(href, 4)
    cards = BU.js(JS_CARDS) or []
    if not cards:
        raise RuntimeError("课程卡片 0 张")
    return cards


def mode_health():
    cards = _open_courses()
    bad = [c for c in cards if not c.get("clazzid")]
    if bad:
        _set_out("health", False, "cards=%d 但 %d 张缺 clazzid（卡片结构变化）" % (len(cards), len(bad)))
        return
    _set_out("health", True, "cards=%d courses=%d" % (len(cards), len({c["title"] for c in cards})))


def mode_discover():
    cards = _open_courses()
    st = _load()
    st["courses"] = cards
    st.setdefault("scan", {})
    st.setdefault("scores", {})
    _save(st)
    _set_out("discover", True, "cards=%d cids=%d" % (len(cards), len({c["clazzid"] for c in cards})))


def _chapter_of(src):
    _nav(src, 3.5)
    text = BU.js(JS_TEXT3K) or ""
    m = re.search(r"已完成任务点[^0-9]{0,12}(\d+)\s*/\s*(\d+)", text) or \
        re.search(r"(\d+)\s*/\s*(\d+)\s*(?:个)?\s*任务点", text)
    done = int(m.group(1)) if m else None
    total = int(m.group(2)) if m else None
    return {"done": done, "total": total, "head": text[:600].replace("\n", " ")}


def _work_of(src):
    _nav(src, 3.5)
    data = BU.js(JS_WORK) or {}
    rows = [r for r in (data.get("rows") or []) if r.get("t")]
    unsub = [r["t"] for r in rows if "未交" in (r.get("s") or "")]
    return {"progress": (data.get("pr") or "").strip(), "rows": rows, "unsub": unsub}


def _course_base(c):
    _nav("https://mooc1.chaoxing.com/visit/stucoursemiddle?courseid=%s&clazzid=%s&cpi=%s&ismooc2=1&v=2"
         % (c["courseid"], c["clazzid"], c["cpi"]), 3.5)
    u = _url()
    base = re.sub(r"[&?]pageHeader=\d+", "", u)
    return base


def _tab_src(base, header, frame_id, wait=3.5):
    sep = "&" if "?" in base else "?"
    _nav("%s%s&pageHeader=%d" % (base, sep, header), wait)
    srcs = BU.js(JS_IFR) or {}
    return srcs.get(frame_id)


def _parse_study(text):
    task = re.search(r"章节任务点[\s\S]{0,60}?(\d+)\s*/\s*(\d+)", text)
    att = re.search(r"(\d+)\s*出勤\s*(\d+)\s*缺勤", text)
    rate = re.search(r"出勤率\s*([\d.]+%)", text)
    rank = re.search(r"(\d+)\s*名\s*当前排名", text) or re.search(r"当前排名[^0-9]{0,6}(\d+)", text)
    pts = re.search(r"课程积分[^0-9]{0,8}(\d+(?:\.\d+)?)\s*分", text)
    onl = re.search(r"在线学习[^0-9]{0,6}(\d+)\s*次", text)
    return {
        "task": [int(task.group(1)), int(task.group(2))] if task else None,
        "attendance": [int(att.group(1)), int(att.group(2))] if att else None,
        "rate": rate.group(1) if rate else "",
        "rank": rank.group(1) if rank else "",
        "points": float(pts.group(1)) if pts else None,
        "online": int(onl.group(1)) if onl else None,
        "head": text[:200].replace("\n", " "),
    }


def mode_scan(start, end):
    courses = [c for c in (_load().get("courses") or []) if not c.get("status") == "已结束"]
    todo = courses[start:end]
    st = _load()
    st.setdefault("scan", {})
    st.setdefault("scores", {})
    okn = 0
    parts = []
    for c in todo:
        cid = c["clazzid"]
        try:
            base = _course_base(c)
            rec = {}
            study = None
            zy = _tab_src(base, 8, "frame_content-zy")
            if zy:
                rec["work"] = _work_of(zy)
            cj = _tab_src(base, 6, "frame_content-cj", 4)
            if cj:
                _nav(cj, 4)
                study = _parse_study(BU.js(JS_TEXT4K) or "")
                st["scores"][cid] = study
                rec["study"] = {"task": study["task"], "rate": study["rate"]}
            st["scan"][cid] = rec
            okn += 1
            tk = "t%s/%s" % tuple(study["task"]) if rec.get("study", {}).get("task") else "t?"
            wk = "w%s" % ((rec.get("work") or {}).get("progress") or "?")
            parts.append("%s:%s,%s" % (cid, tk, wk))
        except Exception as e:
            parts.append("%s:ERR(%s)" % (cid, type(e).__name__))
    _save(st)
    _set_out("scan", okn > 0, "%d-%d ok=%d/%d %s" % (start, end, okn, len(todo), ",".join(parts)))


def mode_scores(start, end):
    courses = [c for c in (_load().get("courses") or []) if not c.get("status") == "已结束"]
    todo = courses[start:end]
    st = _load()
    st.setdefault("scores", {})
    okn = 0
    parts = []
    for c in todo:
        cid = c["clazzid"]
        try:
            base = _course_base(c)
            cj = _tab_src(base, 6, "frame_content-cj", 4)
            if not cj:
                raise RuntimeError("无学习记录 iframe")
            _nav(cj, 4)
            st["scores"][cid] = _parse_study(BU.js(JS_TEXT4K) or "")
            okn += 1
            t = st["scores"][cid]["task"]
            parts.append("%s:%s" % (cid, t[0] if t else "?"))
        except Exception as e:
            parts.append("%s:ERR(%s)" % (cid, type(e).__name__))
    _save(st)
    _set_out("scores", okn > 0, "%d-%d ok=%d/%d %s" % (start, end, okn, len(todo), ",".join(parts)))


try:
    BU = globals()["bu"]
    MODE = globals().get("MODE", "health")
    if MODE == "health":
        mode_health()
    elif MODE == "discover":
        mode_discover()
    elif MODE == "scan":
        mode_scan(int(globals().get("START", 0)), int(globals().get("END", 5)))
    elif MODE == "scores":
        mode_scores(int(globals().get("START", 0)), int(globals().get("END", 5)))
    else:
        _set_out(MODE, False, "未知模式")
except Exception as e:
    _set_out(globals().get("MODE", "?"), False, "%s: %s" % (type(e).__name__, str(e)[:160]))
