# AI 启动说明

> **这是给执行本仓库的 AI 读的入口文件，不是给人看的教程。**
>
> 用户只需要说：
>
> “拉取 `https://github.com/creamlitchirind-afk/yuketang-skills.git`，读 `AI_START_HERE.md`，按里面的路由开始执行：【任务】。”
>
> 你收到这句话后，按本文件执行，不要先问“这个仓库是做什么的”。

## 0. 先判断这是什么

- 本仓库是**长江雨课堂学生端的技能与方法库**，不是安装包，也不是一键运行的程序。
- 它提供页面结构、接口、操作流程、验证方法和已知坑；实际执行需要宿主提供浏览器工具和已登录的雨课堂账号。
- 本仓库**不包含**账号、Cookie、Token 或任何人的课程数据。
- 默认**只读**。只有用户当轮明确点名“完成/提交某项任务”时，才按对应 reference 做写操作。
- 如果用户要的是完整 18 项能力菜单，那属于 `yuketang-capabilities` 能力台；本仓库负责具体执行细节。没有该能力台时，按本文件的“最小任务路由”直接做。

## 1. 拉取后的读取顺序

```bash
git clone https://github.com/creamlitchirind-afk/yuketang-skills.git
cd yuketang-skills
git log -1 --oneline
```

然后按顺序读，**不要一次加载所有 references**：

1. `README.md`
2. `AI_START_HERE.md`（本文件）
3. `yuketang-web-reverse/SKILL.md`
4. 按当前任务读对应 reference（见第 2 节）

记录当前分支和 commit。后续汇报时写清楚“在哪个 commit 上执行”，不要假设版本永远不变。

## 2. 最小任务路由

| 用户想做什么 | 先读 | 执行要点 |
|---|---|---|
| 查课程、查未完成、看还有哪些待办 | `yuketang-web-reverse/references/student-log-unfinished.md` | 先打开课程 `tab=log`，再点“未完成”；不要用 `actype=100` 接口判断 |
| 读 PPT / 推进阅读进度 / 做 PPT 内嵌题 | `references/ppt-reading-and-inline-quiz-bu.md`（云浏览器）或 `references/courseware-reading-and-report.md`（本机 Edge） | 以顶部“学习进度 N/M”为唯一判据；轻量页约 4 秒，密集页 15–45 秒；内嵌题选完必须点“提交” |
| 作业/课前测客观题选择与提交 | `references/answer-selection-and-submit.md` | 选完点底部“提交”= 交本题并自动下一题；不要提交后读“本题得分”误判失败 |
| 章节测试连续作答 | `references/chapter-test-sessions.md` | 先按 P0 浏览器内本卷字体渲染 + 分屏截图读题；放慢到每题 3–5 秒；遇风控交真人 |
| 主观题作业填写 | `yuketang-homework-auto-fill/SKILL.md` | 只写入 UEditor 并读回校验，**不提交**，把纯文本答案交用户自行提交 |
| 课件打印/导出 PDF | `references/print-and-export.md` | 按打印流程取页图；不要用截图冒充 PDF |
| 课堂报告取题 | `references/courseware-reading-and-report.md` | 从课堂记录进入，不要直连报告 URL |
| 接口、请求头、XTBZ、直达链接 | `references/api-and-request.md` | 部分接口需要 XTBZ；不要用 `requests` 替代浏览器会话 |
| DOM、Vue 组件、选择器 | `references/dom-and-vue.md` | 优先浏览器内 JS + 页面内 fetch，不靠屏幕坐标猜 |
| 运行环境、远控、PIP、DEVICE_OFFLINE | `references/automation-environment-and-pitfalls.md` | 先排查环境，不要反复重试同一调用 |
| 全量课程提取、成绩单口径、查重 | `docs/course-extraction.md` | 按文档的分区、类型矩阵和“未批改 ≠ 0 分”顺序读 |
| 影刀/RPA 环境与 JS | `references/rpa-tech-notes.md` | 注意 `execute_javascript` 的返回值和限流 |

### 最小能力清单

如果用户没有说具体编号，只说了自然语言，按下面映射：

- “还有啥没做完 / 查未完成” → 未完成页 + `student-log-unfinished.md`
- “读课件 / 把课件读完 / 做课件里的题” → PPT 阅读 reference
- “导出课件 PDF / 打印课件” → `print-and-export.md`
- “做作业 / 提交这道题 / 章节测试” → 客观题或章节测试 reference
- “写主观题 / 填作业答案” → `yuketang-homework-auto-fill/SKILL.md`
- “查接口 / 页面怎么点 / 报错排查” → API、DOM 或环境 reference
- “全量提取 / 查重 / 成绩口径” → `docs/course-extraction.md`

## 3. 拉取成功后的第一次回复

不要直接开始长任务。先给一个短确认，格式如下：

```text
已拉取 yuketang-skills@main（commit <短哈希>）。
已读：README / AI_START_HERE / yuketang-web-reverse/SKILL.md。
本次按 <reference 文件> 执行：<任务名>。
需要确认：<课程/任务范围/是否允许提交>。
```

如果用户已经在同一句话里给全了“课程 + 任务 + 产出”，可以省略确认，直接进入只读检查；但仍然要先报告路由。

## 4. 执行前检查

1. **浏览器**：优先用宿主提供的浏览器工具；没有浏览器工具就停下来要求用户提供，不要改用纯 HTTP 请求硬打。
2. **登录**：打开课程列表判断登录态。失效时走宿主的用户接管机制（如 `browserControl` / 人工确认），不要绕过验证码、扫码或安全校验。
3. **课程**：让用户给课程名或 `classroom_id`。没给就只查默认有内容的课程，不擅自全量。
4. **截止时间**：先看任务是否已截止。已截止/已关闭只记录原因，不再挂机；同一课程复查时，已截止项只在归档保留，不重复播报。
5. **产物**：写到用户指定目录；不要把账号、Cookie、Token、他人姓名/学号写进产物；截图对外分享前先裁掉个人信息。
6. **长任务**：分段执行，记录“做到哪一页/哪一题”，超时或中断后按进度续跑，不要从头重来。

## 5. 硬约束

- **只读优先**：不签到、不改分、不移出班级、不报告老师。
- **提交例外**：只有用户当轮明确点名“完成/提交某项任务”才做；只做被点名的项，逐题核对，交付里写清做了什么。
- **不代提交主观题**：主观题只填不交，由用户核对后自行提交。
- **验证码/风控**：遇到腾讯安全校验、滑块、扫码、设备验证，立即停手交用户，不尝试绕过。
- **不伪造结果**：以页面上的“学习进度 / 得分 / 状态 / 正确答案”为准；没有看到就说没有看到。
- **不修改仓库**：执行任务的 AI 不要改仓库文件、不要运行安装器、不要全局注册 Skill；除非用户明确要求维护仓库。
- **记录口径**：先按课程角色（学生 / 旁听）分，再按任务类型（作业 / 课件 / 课堂 / 考试）分栏。

## 6. 交付格式

每次执行完，至少给：

1. **做了什么**：课程、任务、页数/题数。
2. **结果**：进度、得分、状态；是否从待办消失。
3. **证据**：页面截图路径或链接（本地路径给完整绝对路径）。
4. **没做/做不了**：已截止、无权限、需要补签等，写平台原因，不要写“未做”。
5. **下一步**：还能做什么，需要用户确认什么。

示例：

```text
课程：传感器技术
任务：实验 5 阅读
结果：15/15，已从待办消失
证据：B:\...\截图_传感器_实验5_完成.png
未完成：无
```

## 7. 用户可直接复制的启动句

```text
拉取 https://github.com/creamlitchirind-afk/yuketang-skills.git，
读 AI_START_HERE.md，按里面的路由开始执行：
课程【课程名】，任务【具体任务】，产出【清单/PDF/Markdown/截图】。
```

如果只想先看能力：

```text
拉取 https://github.com/creamlitchirind-afk/yuketang-skills.git，
读 AI_START_HERE.md，先告诉我这个仓库能做什么，不要执行。
```

如果要完成具体任务：

```text
拉取 https://github.com/creamlitchirind-afk/yuketang-skills.git，
读 AI_START_HERE.md，执行【课程名】的【任务名】；
只做这一项，能补的都补，不能拿分的也完成，做完给我进度截图。
```
