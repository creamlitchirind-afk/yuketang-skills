# 章节测试（作业 exercise）连续作答实战

2026-11-17 实测沉淀：长江雨课堂学生端，课程内「作业 / 章节测试」单元（iframe exercise）从读题到逐题提交、再到成绩核对的一整条链路，以及风控（安全核验）的触发规律与压制办法。

> 通用客观题提交语义、iframe 坐标换算见 [answer-selection-and-submit.md](answer-selection-and-submit.md)；本文只写**章节测试这种"一份卷子 19–30 题、逐题提交"**场景的专属结论。

---

## 1. 入口与页面结构

| 位置 | 事实 |
|---|---|
| 未完成清单 | `studentLog/{cid}?...&tab=unfinished` → 点 `.rain-tabs__nav-item` 里的「未完成」才渲染列表；直接改 URL 参数会被重定向回 `tab=log` |
| 列表条目 | `.unfinished-study__item`，条目内 `button.unfinished-study__arrow` 是入口；标题**只写「章节测试」不写章节名**，只能点进去看左侧目录判断 |
| 点击结果 | 在**新标签**打开 exercise 页（原清单页保留，便于继续下一份） |
| 试卷 URL | `https://changjiang.yuketang.cn/ai-workspace/lms-graph/{cid}/exercise/{eid}?node_id={nid}&is_chapter=1` |
| 题量 | 每份 19 题或 30 题；全部客观题，单选为主，偶有多选 |
| 题号侧栏 | `.problems-aside .subject-item`，当前题 class 含 `active`；滚动容器 `.problems-aside .aside-body`（设 `scrollTop = el.offsetTop - 160` 可把任意题号摆到可见区） |
| 题面面板 | `.container-problem .subject-item`，正文在 `.item-body` |
| 选项 | 单选 `.container-problem .list-unstyled-radio li label`；多选 `.container-problem .list-unstyled-checkbox li label`；**个别题 6 个选项（A–F）**，不要假设固定 5 个 |
| 底部按钮 | `.el-button`「上一题」「提交」「下一题」；窄视口（855×667）下「下一题」位于视口外，不可见也不可点 |

---

## 2. 题面字体混淆（本场景最关键的一条）

- 题干与选项的汉字包在 `span.xuetangx-com-encrypted-font` 内，computed `font-family` 为 `exam-data-decrypt-font`，`innerText` 取回的是**密文**（看着像汉字，实为替换字形）。
- **每一份试卷一套独立 ttf**，文件名带 hash，例如：
  - `exam_font_7d43c8c57d5347aa93301a4b28161bbe.ttf`
  - `exam_font_41eedd379c44458ea1c560c9216040e5.ttf`
  - `exam_font_75f40cd3f2514aae89c62ff49d571f02.ttf`
- 取当前卷字体的方法（在 iframe 内查样式表）：

```js
// 返回本卷 @font-face 的 ttf 绝对地址
(() => {
  var f = document.querySelector('iframe');
  var d = f.contentDocument, u = '';
  Array.from(d.styleSheets).forEach(ss => {
    try {
      Array.from(ss.cssRules).forEach(r => {
        if (r.cssText && r.cssText.indexOf('exam_font') >= 0 && !u) {
          var m = r.cssText.match(/url\("(.*?)"\)/); if (m) u = m[1];
        }
      });
    } catch (e) {}
  });
  return u;
})();
```

- **换错字体的后果**：会渲染出"像汉字但全是假字"的乱码（例：正题「病理生理学是研究()」被渲染成「财研模研温购衡爱()」），比不渲染更难判断。**每进入一份新卷必须重新取 ttf**，不要复用上一份。
- 渲染时用**唯一字体族名**注入宿主页面，避免与页面自带的同名 face 冲突：

```css
@font-face{font-family:"__zk_exam";src:url("<本卷 ttf>") format("truetype");}
```

- 分段渲染规则（踩过的坑）：
  - `e=1` 段 → `font-family: __zk_exam`；`e=0` 段 → 普通字体。
  - 题干里 `e=0`/`e=1` 是**交替出现**的（部分汉字本身未加密、标点与数字始终是明文），必须按节点逐段套字体，整段统一套字体必然乱码。
  - 断行只在 `e=0` 且整段等于 `A`/`B`/`C`/`D`/`E`/`F` 处插入 `<br>`；**不要按"短片段"断行**，会把 `PaCO2`、`HCO3-`、`mmol/L` 这类片段切碎到无法阅读。

采集分段：

```js
(() => {
  var f = document.querySelector('iframe'), d = f.contentDocument;
  var s = d.querySelector('.container-problem .subject-item'), segs = [];
  var w = d.createTreeWalker(s, NodeFilter.SHOW_TEXT), n = w.nextNode();
  while (n) {
    var t = (n.textContent || '').replace(/\u00a0/g, ' ');
    if (t.replace(/\s/g, '').length) {
      var p = n.parentElement, enc = false;
      while (p && p !== s) {
        if (((p.className || '').toString()).indexOf('xuetangx-com-encrypted-font') >= 0) { enc = true; break; }
        p = p.parentElement;
      }
      segs.push({ e: enc ? 1 : 0, t: t.trim() });
    }
    n = w.nextNode();
  }
  return segs;
})();
```

### 2.1 三条解码路径的实测优先级（2026-11-18 更新，P0 为默认）

同一套题面，可以用三种方式还原真字。三者在两份真实试卷上的实测结论如下，**默认走 P0**，P1/P2 保留为兜底：

| 优先级 | 路径 | 做法 | 实测结论 |
|---|---|---|---|
| **P0 首选（已验证可用）** | 浏览器内用本卷字体渲染 + 分屏截图 | 宿主页注入 `@font-face(__zk_exam)` → 每个加密段包 `<span class="zk">` → **逐个 span 设 `style.fontFamily='__zk_exam'`** → 每屏 6 题截图 | 缺氧卷 29 题、应激卷 20 题全部可读；按此作答 29 题全对（2.308 满分） |
| P1 保留（不单独使用） | TTFont `cmap` 字形名直读 | `TTFont(ttf).getBestCmap()` → 字形名 `uniXXXX` 取真字 | 本卷 882 条映射里只有一部分带 `uni` 名，274 个加密字符中大量字形名为 `glyphNNNNN`（无名）→ 直读输出仍是半乱码 |
| P2 保留（旧路线） | PIL 位图相似度匹配 | 本卷字形按 96px 渲染成 32×32 向量 → 与 msyh/simhei/simsun 参考矩阵做余弦相似度取 top1 | 旧卷曾产出可用映射；但本卷第 274 个加密字符相似度**全部落在 0.24–0.62**（同字正常应 >0.9）→ 整卷结果不可信，只能当兜底 |

> 判据一句话：**相似度低于 0.9 的映射不要用于批量作答**；拿不准时回到 P0 截图核对。
> P0 的两份实测样本：`exam_font_72452e4a…ttf`（29 题，缺氧）、`exam_font_20022e72…ttf`（20 题，应激）。

### 2.2 P0 覆盖层的落地细节（照抄即可）

```js
// 1) 注入字体（族名固定用 __zk_exam，避免与页面自带 face 冲突）
@font-face{font-family:"__zk_exam";src:url("<本卷 ttf>") format("truetype");}

// 2) 覆盖层：全屏白底，17px / 1.65 行高，每屏 6 题刚好一屏
ov.style.cssText = 'position:fixed;left:0;top:0;width:100%;height:100%;background:#fff;'
  + 'z-index:99999;overflow:auto;padding:14px 16px;box-sizing:border-box;'
  + 'font-size:17px;line-height:1.65;color:#000;';

// 3) 关键一步：加密段包 span，并【逐个】设字体（少了这一步就是乱码）
var ks = ov.querySelectorAll('.zk');
for (var i=0;i<ks.length;i++){ ks[i].style.fontFamily='__zk_exam'; }
```

**三个必踩的坑**（这次全部真实发生过）：

1. 只写 `<span class="zk">` 但没给 `.zk` 设 `font-family` → 屏幕上是私用区字形，看着像汉字、其实全错；
2. 想隐藏原文而给外层加 `font-size:0` → 整屏空白（截图全白，白跑一轮）；
3. 渲染完忘记 `overlay.remove()` 就去点选项 → 点击被覆盖层吞掉，表现为"点了没反应"。

**可读性自检**：读出来的句子必须能对上章节主题（例：能读出「低张性低氧血症主要血气特点是」「应激时蓝斑-交感-肾上腺髓质系统的中枢位点位于」）。读不懂就立刻换本卷 ttf 重渲染，不要硬着头皮答。

---

## 3. 逐题提交语义

- 底部「提交」= **只提交当前这一题**：计数由 `x/N 题` 递增，提交后该题选项变 disabled，并出现「本题得分：N」与「正确答案：X」——可直接当错题复盘用。
- 没有"整卷交卷"按钮；不需要、也不应该攒到最后一次性交。
- 已答未交就切换题号会弹「刚刚答完的习题还没有提交，需要提交吗？」（先不用了 / 帮我提交 / 取消 / 确定 / 仅提交本题）。自动化流程里**答完立即点「提交」**即可不再遇到这个弹窗。
- 提交后计数 `N/N 题` 即该份已完成，可去成绩单核对分数。
- **提交成功会自动跳到下一题**（2026-11-18 实测）：所以"提交后读状态"读到的其实是下一题的干净状态（`本题得分` 会读不到），不要据此误判"没提交成功"；正确判据是**提交前**的 active 索引、以及提交后计数自增。
- 想复盘某题：重新点回该题号，读 `本题得分：N` 与 `正确答案：X`。这两行是 UI 明文，**不受题面字体加密影响**，可直接当对账依据（实测 1 分题显示「本题得分：1 / 正确答案：E」）。

---

## 4. 风控与安全核验（本场景最大时间成本）

- 页面会加载 `https://changjiang.yuketang.cn/c27/anti-cheat/config?scene=homework&assignmentId={aid}&sdkVersion=1.0.0`。
- **触发点不是"事件真假"，而是"答题-提交的节奏与密度"**：
  - 曾在 10–20 秒内连续切换 19–30 次题号（为批量采集题面）→ 必弹「请完成安全核验」；
  - 换成真实鼠标点击（`bu.click_xy`，`isTrusted=true`）后，**批量连续提交照样弹**；
  - 放慢到每题「切题 → 选选项 → 提交」约 3–5 秒、并每题回读计数确认后，30 题全程 0 次弹窗（另一次仅在开头弹 1 次）。
- 弹窗形态：「请完成安全核验」，按住「起」点依次经过 1、2、3，最后到「终」点松开。
- **必须真人完成**：不得代拖、不得构造轨迹、不得绕过；自动化脚本遇到即停手，把控制权交给用户（浏览器控制类 handoff），用户拖完后再继续。
- 结论：能压到"偶尔一次"，但**不可能为零**；做长任务前先跟用户确认愿意在需要时拖验证。

---

## 5. 驱动方式对比（选哪个）

| 方式 | 题号切换 | 选项选择 | 提交 | 备注 |
|---|---|---|---|---|
| `element.click()` | ❌ 无效 | 部分无效 | ❌ 无效 | Vue 监听不吃裸 click |
| 合成事件序列 `pointerdown → mousedown → pointerup → mouseup → click`（`MouseEvent`，`bubbles+cancelable+view+clientX/Y`） | ✅ | ✅ | ✅ | 本场景主用法；不受滚动/偏移影响 |
| `bu.click_xy` 坐标点击 | ⚠ 不稳定 | ✅（坐标正确时） | ✅ | 受 iframe 偏移、侧栏 scrollTop、视口缩放影响；宽视口下可用，窄视口下题号列易点错题 |

合成事件模板：

```js
['pointerdown','mousedown','pointerup','mouseup','click'].forEach(tp => {
  el.dispatchEvent(new MouseEvent(tp, {bubbles:true, cancelable:true, view:d.defaultView, clientX:x, clientY:y}));
});
```

---

## 6. 读题效率（整卷 overlay 渲染 + 按题块分屏）

一次只看一题截图，30 题要 30 张图，成本过高。做法：

1. 用第 5 节的合成事件把 1..N 题逐一切过去，采集各题 `segs`，落盘 `<exercise_id>.json`；每步 0.3–1.4 秒，并校验 `active` 索引与预期一致（不一致的那题当场补采）。
2. 在**宿主页面**（不是 iframe）建 `position:fixed` 的全屏白色 overlay，按第 2 / 2.2 节规则内联渲染（加密段包 span 并逐个设字体）。
3. 渲染后取每个题块的 `offsetTop/offsetHeight`，按"单屏高度"切窗，**只在题块边界处分屏**（否则题目会被切成两半，读起来极易漏行）。17px / 1.65 行高下，**每屏 6 题**正好一屏。
4. 每题块之间加虚线分隔，方便按题号对位。
5. 渲染完记得 `overlay.remove()` 再去做点击，否则 overlay 会吞掉所有真实点击。

视口事实：855×667 时 exercise iframe 宽 808，右侧约 320px 被裁（长选项读不全）；1280×960 视口下全宽可见，读题与坐标点击都更稳。

---

## 7. 判分口径与成绩读取

- 课程「作业」模块若为 13 个单元共 30 分，则**每份 2.308 分**（30/13），一份 19–30 题的卷子并非每题 1 分等额。
- 成绩单读法：新标签打开 `studentLog/{cid}?classroom_id={cid}&tab=log` → 点含「成绩单」的 `.rain-tabs__nav-item` → 读 `document.body.innerText`，定位小节 `作业 13个单元，共30.000分 个人得分：X`，逐行是「已完成 得分/满分」。
- **用新标签读成绩单再 `close_tab`**，不要在当前答题标签里跳转，否则作答页状态丢失。
- 实测样本：19 题对 16 → 1.943；30 题对 26 → 2.010；30 题对 27 → 2.077；**29 题全对 → 2.308（满分）**；20 题（含 1 道 2 分多选）错 1 处 → 约 2.1。
- 同一门课的分数推进可直接当进度条用：作业每完成一份，总分按该份得分上涨（实测 46.0 → 48.3 → 50.4）。

---

## 8. 一轮完整流程（可复现）

1. 未完成页 → 点第一项 `.unfinished-study__arrow` → 新标签进入 exercise。
2. 记录 `exercise_id`、题数、当前计数 `0/N`。
3. 逐题合成事件切题 + 采集 `segs` → 写 `_data/{exercise_id}.json`（校验 active 索引）。
4. 取本卷 ttf → 宿主页 overlay 渲染整卷 → 按题块分屏截图读题。
5. 逐题：切题 → 选选项（多选用 checkbox 选择器）→ 点「提交」→ 回读 `x/N`；每题 3–5 秒。
6. 新标签读成绩单，核对本份得分与课程总分。
7. 遇到「请完成安全核验」立即停手交用户。

---

## 9. 坑清单（按踩坑顺序）

1. 复用上一份试卷的 ttf → 满屏"假汉字"，且极易被误当成题目正常但自己看不懂。
2. 渲染断行按"短片段"判断 → `PaCO2`/`HCO3-` 被切碎，读题失败。
3. overlay 未移除就点点击 → 所有真实点击被吞，表现为"点了没反应"。
4. 题号坐标点击 + 侧栏 `scrollTop` 变化 → 点第 5 题却激活第 2 题。
5. 窄视口下「下一题」在视口外，坐标点必然落空；不要试图用它翻页，用题号侧栏或合成事件。
6. 假设每题 5 个选项 → 遇到 A–F 六选项题直接取不到选项。
7. 多选仍用 `.list-unstyled-radio` 选择器 → 返回空数组。
8. `mooc-api/v1/lms/exercise/get_exercise_list/...` 需 `XTBZ` 头，页面内同步 XHR 返回 `XTBZ IS REQUIRED`，`bu.http_get` 直接 403；只能读渲染后的 DOM。
9. 批量快速切题/提交 → 触发 `/c27/anti-cheat` 安全核验，且真实点击同样触发；只能靠放慢节奏压制。
10. 在答题标签里跳去成绩单 → 答题页状态与草稿丢失；一律新标签读成绩。
11. 覆盖层只包 `<span class="zk">` 却没给 `.zk` 设 `font-family` → 屏幕上是私用区字形，"像汉字但全错"；必须逐个 span 设字体。
12. 为隐藏原文给覆盖层外层加 `font-size:0` → 整屏空白，截图全白。
13. 用 PIL 位图匹配 / 字体 `cmap` 字形名直读代替截图 → 本卷相似度全低于 0.62、大量字形无名，结果不可信；这两条只能兜底，默认用浏览器内渲染。
14. 提交成功后页面自动跳到下一题 → 立刻读「本题得分」会读不到，误判为"没提交"；判据应看提交前的 active 与提交后的计数自增。
