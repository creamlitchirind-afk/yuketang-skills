# 学习通能力台 · 菜单与调度说明

> 触发词：**「调用我的学习通能力」**（同义：学习通能力 / 打开学习通面板 / 学习通菜单）。
> 只报菜单时展开下面清单并等编号；已给编号、任务和课程时直接按路由表执行。
> 首版：2026-11-23｜15 项｜4 组

## 一、菜单

```
【学习通能力台】15 项 · 4 组    回复编号即可，可多选（如 A1、B1、D1）

A 资料与课件
 A1 课程清单            个人空间课程卡片→标题/教师/班级/进度(若有) 产出 data/course-list      ✅
 A2 资料清单+直链       资料页文件夹/文件→名称/大小/dataId      产出 data/materials-list   ✅
 A3 单文件下载          按 dataId 直链下载原文件                 产出 downloads/课程目录     ✅
 A4 PPT/PDF 转 PDF      PPT/PDF 课件转 PDF                     产出 data/pdf               ✅ 已实测
 A5 章节任务点          章节目录+已完成任务点                   产出 data/chapter-list      ✅

B 作业与考试
 B1 作业清单            作业列表→标题/状态/workId/answerId      产出 data/homework-list     ✅
 B2 考试清单            考试列表→标题/状态/时间                 产出 data/exam-list         ✅
 B3 学习记录/出勤       任务点/排名/积分/签到/出勤率             产出 data/study-record      ✅
 B4 成绩/积分明细       课程积分、作业得分、测验得分             产出 data/score-detail      ⚠ 待验证

C 题库与自测
 C1 错题集              错题列表与题目详情                      产出 data/wrong-questions   ⚠ 空页可读
 C2 自测/测验           自测记录、章节测验                      产出 data/self-test-list    ✅ 列表已实测

D 运维与情报
 D1 登录检查/二维码     扫码登录、登录态检查                    产出 二维码/登录状态         ✅
 D2 课程结构查询        tab/pageHeader/iframe/接口定位           直接答，不重跑               ✅
 D3 全量课程台账        当前账号全部课程卡片与班次               产出 data/course-list       ✅
 D4 增量快照/对比       与上次快照 diff                          产出 增量报告               ⚠ 未实现
```

## 二、路由表

| 编号 | 先读 | 再执行 | 关键输入 |
|---|---|---|---|
| A1 课程清单 | `references/chaoxing-web-structure-20261123.md` §2 | `scripts/course-list.js`，在个人空间课程 iframe 内执行 | 无 |
| A2 资料清单+直链 | 同上 §4 | `scripts/materials-list.js`，在课程“资料”页或其 iframe 内执行 | 课程名 / courseid / clazzid |
| A3 单文件下载 | 同上 §4 | 取 `download_url` 后 `bu.download()`；下载后核对 bytes/扩展名 | dataId 或资料链接 |
| A4 PPT/PDF→PDF | 同上 §4 | 先下载原文件，再走 `scripts/convert-ppt-to-pdf.ps1`（PowerPoint COM） | 课程 + 文件 |
| A5 章节任务点 | 同上 §3 | `scripts/chapter-list.js`；课程“章节”页执行，或把 `frame_content-zj` 的 src 当顶层打开 | 课程 |
| B1 作业清单 | 同上 §5 | `scripts/homework-list.js`；作业 iframe 跨域时先打开其 src 顶层 | 课程 |
| B2 考试清单 | 同上 §6 | `scripts/exam-list.js`；考试 iframe 跨域时先把 src 当顶层打开；当前只在单门课程验证到“暂无考试”，其余课程待逐课核验 | 课程 |
| B3 学习记录 | 同上 §7 | `scripts/study-record.js`；学习记录 iframe 跨域时打开 src 顶层 | 课程 |
| B4 成绩/积分明细 | 同上 §7 | 先查“课程积分/详情”，确认是否有可读明细 | 课程 |
| C1 错题集 | 同上 §8 | `scripts/wrong-questions.js`；空页可读，有题时先看结构再扩 | 课程 |
| C2 自测/测验 | 同上 §8 | `scripts/self-test-list.js`；只读标题/题量，不进入答题 | 课程 |
| D1 登录检查/二维码 | 同上 §1 | 打开登录页→取 `#quickCode` 图片→发二维码；需接管时交用户扫码 | 无 |
| D2 课程结构查询 | 整份 references | 直接回答 tab、pageHeader、iframe、资料 dataId | 问题 |
| D3 全量课程台账 | `data/` 最近一份课程清单 | 直接读；需要刷新才重抓 | 无 |
| D4 增量快照/对比 | `data/` 最近两份快照 | 对比课程/资料/作业新增、状态变化；当前尚未写 diff 脚本 | 基线日期 |

## 三、常用套餐

| 套餐 | 组成 | 用途 |
|---|---|---|
| **课程盘点** | A1 + D3 | 看这学期有哪些课、哪些班、进度多少 |
| **资料落地** | A2 → A3 → A4 | 把某门课的资料清单拉出来，下载原文件并转 PDF |
| **作业巡检** | B1 + B3 | 看未交/待批阅作业、任务点、出勤缺口 |
| **考前复习包** | A1 → A2 → A5 → B1 → B3 | 课程资料 + 章节任务 + 作业/出勤缺口 |
| **新课补料** | D4 → A2 → A3 | 只看新增或修订的资料 |

## 四、底座

- 云浏览器 `bu` 是唯一可靠入口；登录态来自用户扫码。
- 课程列表、资料页 iframe 通常同源，可直接 `contentDocument`；章节/作业/学习记录/考试/自测 iframe 可能跨域，需把 iframe 的 `src` 当顶层 URL 打开后再读。
- 课程页 `pageHeader`：0 任务、1 章节、2 讨论、3 资料、4 错题集、5 自测、6 学习记录、8 作业、9 考试、12 课程图谱（已实测）。
- 资料页文件行：`ul.dataBody_td`；文件名 `li.dataBody_name_stu`；下载链接 `a[href*="downloadData"]`，`dataId` 是稳定标识。
- 作业行：`li[onclick*="goTask"]`，`data` 属性是任务 URL，`aria-label` 带“标题 ; 状态”。
- 同名课程按 `clazzid` 区分；具体班次数随账号变化，不要写死。
- 2026-11-23 现场核验：A1/A2/A5/B1/B2/B3/C1（空页）/C2/D1 跑通；A1 状态字段已修复，课程清单已刷新。B4、C1 有题结构、D4 仍待验证。

## 五、新增一项的规则

1. 先在 `scripts/` 落一个可复用片段，不把逻辑留在临时对话里；
2. 在本文件加一行（编号 + 一句话 + 产出 + 状态）；
3. 同步更新 `capabilities-panel.html` 的 `DATA` 数组；
4. 新发现的页面结构/坑写入 `references/chaoxing-web-structure-20261123.md`，带日期。
5. 公开仓库只写方法，不写账号、课程名、班级 ID、成绩、出勤、Cookie、Token。
