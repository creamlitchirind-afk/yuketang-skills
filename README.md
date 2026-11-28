# 雨课堂（长江雨课堂）与学习通（超星）自动化技能包

面向长江雨课堂学生端（`changjiang.yuketang.cn`）的三个可复用技能，以及学习通网页版（`chaoxing.com`）的只读能力台，按 `SKILL.md` 规范组织，可被支持该规范的 Agent 直接加载。

> **给 AI：首次拉取本仓库，先读 [AI_START_HERE.md](AI_START_HERE.md)。**

## AI 启动说明

如果用户说“拉取 GitHub 上的雨课堂能力库并开始执行”，先读 [`AI_START_HERE.md`](AI_START_HERE.md)。里面有：

- 拉取后的读取顺序（README → AI_START_HERE → SKILL.md → 对应 reference）
- 任务类型 → reference 的路由表
- 拉取成功后的首次回复格式
- 只读默认、提交例外、验证码交接、记录按角色/类型分栏等硬约束

用户可直接复制：

```text
拉取 https://github.com/creamlitchirind-afk/yuketang-skills.git，
读 AI_START_HERE.md，按里面的路由开始执行：
课程【课程名】，任务【具体任务】，产出【清单/PDF/Markdown/截图】。
```


| 技能 | 用途 |
|---|---|
| [`yuketang-web-reverse`](yuketang-web-reverse/SKILL.md) | 学生端网页与接口结构拆解：课程清单接口、单门课程未完成扫描、课件逐页阅读推进（PageDown 翻页、每页停留计页、**内嵌选择题作答**）、课堂报告取题、课件打印导出、**客观题选择与提交（作业逐题提交 / PPT 内嵌单选题真实点击法 / 云浏览器下的拖拽翻页与阅读计时）**；含运行环境与故障排查（远控禁切虚拟桌面、PIP 切换失败、DEVICE_OFFLINE 等） |
| [`yuketang-homework-auto-fill`](yuketang-homework-auto-fill/SKILL.md) | 主观题作业自动填写：定位 UEditor → 官方 API 写入 → 读回校验 → **不提交**，把纯文本答案交给用户自行提交 |
| [`yuketang-unfinished-watch`](yuketang-unfinished-watch/SKILL.md) | 未完成待办巡检与汇报：每轮自动发现全部课程、按课程名归并同名班次报「N 门课（M 个班次）」、只读扫描未完成、剔除已超时/已截止/未签到/上课中等不可做项、与基线比对新增、可选 Qmsg 推送，按“分课分节”版式汇报，全无待办时改报成绩构成 |
| [`xuexitong-capabilities`](xuexitong-capabilities/SKILL.md) | 学习通（超星）网页版只读能力台：登录检查、课程清单、资料清单与 dataId 下载、章节任务点、作业/考试清单、学习记录与出勤、自测/错题集、PPT→PDF，以及云浏览器 `bu` 下的两段式巡检脚本；默认不提交、不签到、不改分 |

## 目录结构

```
AI_START_HERE.md                        # 给执行本仓库的 AI 的启动说明
yuketang-web-reverse/
├── SKILL.md
└── references/
    ├── dom-and-vue.md                     # 课程清单页 DOM 与 Vue 组件树
    ├── student-log-unfinished.md          # 未完成页选择器与数据字段
    ├── api-and-request.md                 # 接口、请求头、XTBZ、直达链接
    ├── rpa-tech-notes.md                  # 影刀 web 环境与 execute_javascript
    ├── print-and-export.md                # 课件打印导出 PDF 全流程
    ├── courseware-reading-and-report.md   # 课件逐页阅读与课堂报告取题
    ├── answer-selection-and-submit.md     # 客观题选择与提交（作业 / PPT 内嵌题）
    ├── chapter-test-sessions.md           # 章节测试连续作答实战（按卷字体解码、逐题提交、风控节奏）
    ├── ppt-reading-and-inline-quiz-bu.md  # 云浏览器 PPT 阅读计时与内嵌题补完
    ├── ai-companion-and-open-assignment.md # AI 学伴计分与开放型作业写入
    └── automation-environment-and-pitfalls.md  # 运行环境与已知故障
yuketang-homework-auto-fill/
└── SKILL.md
yuketang-unfinished-watch/
└── SKILL.md                            # 未完成巡检、归并课程数、基线比对与汇报版式
xuexitong-capabilities/
├── SKILL.md                            # 学习通只读能力台入口
├── capabilities-menu.md                # 15 项菜单与路由
├── capabilities-panel.html             # 离线可搜索面板
├── references/
│   ├── chaoxing-web-structure-20261123.md  # 登录、tab、iframe、dataId、各页结构
│   └── verification-20261123.md        # 脱敏后的能力核验摘要
├── scripts/                            # 浏览器内只读片段与 PPT→PDF
├── track/                              # 两段式巡检脚本
└── data/                               # 运行时数据目录（不入库）
```

## 学习通能力台

学习通部分与雨课堂技能共用同一套“只读优先”约定，但入口与页面结构不同：登录走学习通 App 扫码，课程入口在个人空间，作业/学习记录/考试等 iframe 多数跨域，需要把 iframe 的 `src` 当顶层 URL 打开后再读。

- 能力菜单：`xuexitong-capabilities/capabilities-menu.md`
- 页面结构：`xuexitong-capabilities/references/chaoxing-web-structure-20261123.md`
- 核验摘要：`xuexitong-capabilities/references/verification-20261123.md`
- 巡检脚本：`xuexitong-capabilities/track/README.md`
- 数据目录：`xuexitong-capabilities/data/` 只保留说明；运行数据在仓库外生成，避免个人课程/成绩入库。

## 方法文档

| 文档 | 内容 |
|---|---|
| [`docs/course-extraction.md`](docs/course-extraction.md) | 课程全量提取方法（2026-11 实战沉淀）：三层结构落点、`logs/learn` 分区与类型矩阵、作业两套链路（试卷 type 4 / 作业 type 19）、题面字体混淆与截图取证、课件进度与正文接口、成绩单模块口径、**"未批改 ≠ 0 分"的分数判读顺序**、批量提取的标签页与进程卫生、查重与落盘结构、8 条常见坑、13 项检查清单 |
| [`yuketang-web-reverse/references/chapter-test-sessions.md`](yuketang-web-reverse/references/chapter-test-sessions.md) | 章节测试连续作答实战（2026-11-17 初版 / 2026-11-18 补充实测）：**题面解码方法优先级（P0 浏览器内本卷字体渲染 + 分屏截图，实测 29 题全对拿满 2.308；P1 字体 `cmap` 字形名 / P2 PIL 位图匹配仅兜底，本卷相似度全 <0.62）**、每份试卷一套独立 `exam_font_*.ttf`、加密段必须逐个 span 设字体（漏设/`font-size:0` 都会得到假汉字或空白）、底部「提交」= **逐题提交、提交后自动跳下一题**、`c27/anti-cheat` 安全核验触发规律与压制（放慢到每题 3–5 秒，遇弹必交真人）、合成事件 vs 坐标点击取舍、整卷 overlay 每屏 6 题 + 按题块分屏、13×2.308 分口径与成绩单新标签读法、14 条坑 |
| [`yuketang-web-reverse/references/ppt-reading-and-inline-quiz-bu.md`](yuketang-web-reverse/references/ppt-reading-and-inline-quiz-bu.md) | 云浏览器 `bu` 下的 PPT 阅读计时与内嵌题补完（2026-11-17 初版 / 2026-11-18 传感器四实验补充）：缩略图不切主视图、真实拖拽翻页、**轻量页约 4 秒、密集页 15–45 秒才计页（进度可能批量 +2）**、后台过渡卡住与 z-index 残留处理、0.6 缩放、单选/多选真实点选 + 「提交」回读、已截止作业/视频判断、**按角色/任务类型分栏记录且已截止项复查不重复播报** |
| [`yuketang-web-reverse/references/ai-companion-and-open-assignment.md`](yuketang-web-reverse/references/ai-companion-and-open-assignment.md) | AI 学伴计分与开放型作业写入（2026-11-23 实战）：AI学伴**按对话次数区间计分**（0–24=0 / 25–49=25 / 50–99=50 / ≥100=100，成绩单按 10 分折算；实测 82 次 5/10 → 101 次 10/10）、面板 iframe（`chatbot-window?chat_window_id=…`）定位与计数核对节奏；开放型作业 UEditor **无 `UE.instants`** 时走 `.edui-editor-iframeholder iframe` + `execCommand('insertHTML')` 分段写入 + 字数读回校验、**只写不代提交**、「已完成 0.000」= 待批改而非空交；含成绩单总分/模块正则与读数联动 |

## 使用约定（重要）

- **只读优先**：默认只做读取与统计，不提交作业、不签到、不退出课程；学习通部分同样只读。
- **不代提交**：作业填写完成后由用户自行核对并提交。
- **提交例外**：仅当用户当轮明确点名要完成某份作业/某个课件题时，才按 [`answer-selection-and-submit.md`](yuketang-web-reverse/references/answer-selection-and-submit.md) 作答并提交；逐题核对答案，交付里写清提交了什么；遇验证码/守卫弹窗立即停手交用户。
- **合规使用**：仅在本人账号、本人课程范围内使用，遵守学校与平台规定。
- **数据不入库**：账号、Cookie、Token、二维码 uuid、课程名、班级 ID、成绩、出勤、作业原文与课件原文件都不写入公开仓库；学习通运行数据写到仓库外的 `XT_WATCH_DIR`。
- 文中出现的课程 id、班级 id 仅为格式示例，不代表任何固定课程。

## 安装

把整个目录复制到 Agent 的 skills 目录即可，例如：

```bash
cp -r yuketang-web-reverse yuketang-homework-auto-fill yuketang-unfinished-watch xuexitong-capabilities ~/.doubao/agent_mode/workspace/.skills/
```

## 许可

MIT，见 [LICENSE](LICENSE)。
