---
name: xuexitong-capabilities
description: 学习通（超星 / chaoxing.com）网页版学生端只读能力台，覆盖登录检查、课程清单、资料清单与下载、章节任务点、作业/考试清单、学习记录与出勤、自测/错题集、PPT/PDF 转 PDF，以及云浏览器 bu 下的两段式巡检脚本。用于在本人账号范围内读取课程数据；默认不提交作业、不签到、不改分。包含 iframe 跨域处理、pageHeader 路由、dataId 下载、只读脚本与隐私边界。
---

# 学习通能力台（xuexitong-capabilities）

面向学习通网页版学生端的只读能力台。它把“页面结构、浏览器片段、巡检脚本、能力菜单”集中到一个可复用 Skill，避免每次从零定位 iframe、tab 和下载链接。

## 适用范围与边界

- 适用：本人账号的课程清单、资料清单与下载、章节任务点、作业/考试清单、学习记录与出勤、自测/错题集、登录检查、PPT/PDF 转 PDF。
- 不适用：代提交作业、签到、答题、改分、移出班级、发消息等写操作。
- 底座：云浏览器 `bu`（真实桌面 Edge 与普通 HTTP 客户端不保证带登录态）。
- 登录：学习通 App 扫码；二维码是登录态入口，只发给当前用户，不写入公开台账。
- 页面结构会变；能力状态只写四档：✅ 可用 / ⚠ 半可用或待验证 / ⛔ 封存 / ⏸ 待批。

## 快速路由

| 任务 | 先读 | 执行入口 |
|---|---|---|
| 选功能 / 看 15 项菜单 | [`capabilities-menu.md`](capabilities-menu.md) | 按编号路由 |
| 课程清单 | [`references/chaoxing-web-structure-20261123.md`](references/chaoxing-web-structure-20261123.md) §2 | `scripts/course-list.js` |
| 资料清单 / 下载 | 同上 §4 | `scripts/materials-list.js` + `bu.download()` |
| 章节任务点 | 同上 §3 | `scripts/chapter-list.js` |
| 作业 / 考试清单 | 同上 §5–6 | `scripts/homework-list.js` / `scripts/exam-list.js` |
| 学习记录 / 出勤 | 同上 §7 | `scripts/study-record.js` |
| 自测 / 错题集 | 同上 §8 | `scripts/self-test-list.js` / `scripts/wrong-questions.js` |
| 登录检查 / 二维码 | 同上 §1 | `#quickCode` + 用户接管 |
| 定时巡检 / 增量台账 | [`track/README.md`](track/README.md) | `track/scan_xt_bu.py` + `track/report_xt.py` |
| PPT/PDF 转 PDF | [`scripts/README.md`](scripts/README.md) | `scripts/convert-ppt-to-pdf.ps1` |

## 目录

```
xuexitong-capabilities/
├── SKILL.md
├── README.md
├── capabilities-menu.md          # 15 项菜单与路由
├── capabilities-panel.html       # 离线可搜索面板
├── references/
│   ├── chaoxing-web-structure-20261123.md
│   └── verification-20261123.md
├── scripts/                      # 浏览器内只读片段
├── track/                        # 两段式巡检脚本
└── data/                         # 运行时数据（不入库）
```

## 关键原则

1. **只读优先**：默认只读取页面文本与列表，不提交、不签到、不答题、不改分。
2. **跨域 iframe 不硬读**：作业、考试、学习记录、章节、自测的 iframe 可能跨域；把 iframe 的 `src` 当顶层 URL 打开后再读。
3. **同名课程按 `clazzid` 区分**：不要按标题去重；班次数随账号变化。
4. **下载链接依赖登录 cookie**：`dataId` 可复用，但下载必须带当前会话。
5. **数据不公开**：课程名、班级 ID、成绩、出勤、Cookie、Token、二维码 uuid 都不写入公开文档或截图台账。

## 隐私与数据

`data/` 只放运行时快照，已在仓库 `.gitignore` 中排除。公开仓库只保留页面结构、脚本与脱敏后的核验摘要；不要把个人课程数据、成绩单、课件原文件或登录二维码提交到 Git。
