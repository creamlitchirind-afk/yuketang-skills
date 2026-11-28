# 学习通能力台（xuexitong-capabilities）

**触发词**：`调用我的学习通能力`、`学习通能力`、`打开学习通面板`、`学习通菜单`。

**首版**：2026-11-23｜15 项 · 4 组｜12 项已实测可用，3 项待验证。

**定位**：学习通网页版学生端的只读能力台。能力台负责“选功能、看页面结构、复制浏览器片段”；`track/` 负责“定时巡检、增量台账”。默认不提交作业、不签到、不答题、不改分。

## 先看什么

- 要选功能：读 [`capabilities-menu.md`](capabilities-menu.md)（15 项，含输入/产出/状态/路由）。
- 要查页面结构和坑：读 [`references/chaoxing-web-structure-20261123.md`](references/chaoxing-web-structure-20261123.md)。
- 要复用取数逻辑：`scripts/` 下是可直接放进云浏览器 `bu.js()` 的片段。
- 要图形化浏览：浏览器打开 [`capabilities-panel.html`](capabilities-panel.html)。
- 要定时巡检：读 [`track/README.md`](track/README.md)。

## 目录

- `capabilities-menu.md`：15 项菜单、路由表、常用套餐。
- `capabilities-panel.html`：离线可搜索面板，单文件。
- `references/chaoxing-web-structure-20261123.md`：登录、tab、iframe、资料 dataId、作业/学习记录/自测/考试页结构。
- `references/verification-20261123.md`：脱敏后的能力核验摘要。
- `scripts/`：课程、资料、章节、作业、考试、学习记录、自测、错题集片段 + PPT/PDF 转 PDF。
- `track/`：`scan_xt_bu.py` 四模式扫描 + `report_xt.py` 增量台账。
- `data/`：运行时快照目录，不入库；只保留说明文件。

## 底座与边界

- 只使用云浏览器 `bu`（真实桌面 Edge 与普通 `requests` 不保证带登录态）。
- **只读**：不提交作业、不签到、不改分、不移动课程、不发消息。
- 资料下载只下载用户已有权访问的课程文件；下载链接依赖当前登录 cookie。
- 页面结构会变；状态只写四档：✅ 可用 / ⚠ 半可用或待验证 / ⛔ 封存 / ⏸ 待批。
- 登录二维码只发给当前用户；二维码 uuid、Cookie、Token 不写入公开文档或截图台账。

## 数据与隐私

公开仓库不保存账号、姓名、学号、课程名、班级 ID、成绩、出勤、作业原文、课件原文件或登录二维码。`data/` 与 `track/` 的运行产物已由仓库 `.gitignore` 排除；需要留存时只写本地目录。
