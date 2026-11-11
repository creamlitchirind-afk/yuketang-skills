---
name: yuketang-web-reverse
description: 长江雨课堂（changjiang.yuketang.cn）学生端网页与接口结构拆解，用于设计 RPA / 浏览器自动化（课程清单、未完成任务扫描、归档/恢复、任务跳转链接），以及课件逐页阅读推进（PageDown 翻页、每页停留计页、内嵌选择题页作答）与课堂报告取题（报告页导航链）。涵盖 DOM 选择器、Vue 组件树、courses/list 接口、XTBZ 反爬与请求头、影刀 web 环境配置、execute_javascript 取值要点与限流坑。需要在雨课堂上"读数据/做自动化"而不是"写主观题"时使用；写主观题另见 yuketang-homework-auto-fill。
---

# 雨课堂网页结构拆解（自动化设计参考）

本 Skill 沉淀长江雨课堂学生端（"我听的课"）的页面、Vue 组件与后端接口结构，供后续设计雨课堂相关自动化时直接引用，避免重复逆向。所有选择器、组件名、字段均经过真实页面实测；文中出现的具体数字 id 仅为格式示例，不代表任何固定课程。

## 适用范围与边界

- 适用：课程清单读取、单门课程未完成任务扫描、我的归档/恢复、任务直达链接构造、只读型数据采集。
- 不适用：主观题作答（用 `yuketang-homework-auto-fill`）、任何提交/签到/退出课程等写操作。
- 雨课堂是 **Vue 2 + Element UI** 单页应用，课程卡片、任务列表均为数据驱动渲染；优先走"浏览器内 JS 执行 + 页面内 fetch"，而非屏幕坐标点击。

## 关键事实速查

| 主题 | 结论 |
|---|---|
| 站点 | `https://changjiang.yuketang.cn`，学生端首页 `/v2/web/index` |
| 课程列表接口 | `GET /v2/api/web/courses/list?identity=2`，页面内 fetch 同源带 cookie 即可，**无需 XTBZ 签名** |
| 列表数据位置 | 响应体 `data.list`（数组）；课程名 `course.name`、老师 `teacher.name`、班级名 `name`、课程 id `classroom_id` |
| 视图身份 | `identity=2` 表示学生（"我听的课"）；另有教师视图 |
| 课程内身份 | 2026-11-01 现场验证：列表 `role=6` 对应卡片「旁听」，普通学生 `role=5`；不能把无权限页直接当旁听 |
| 反爬 | 多数后端 API 要求 XTBZ，直调返回 `XTBZ IS REQUIRED`；但课程列表等少数接口在页面会话内不强制 |
| 单门未完成页 | `/v2/web/studentLog/{cid}?classroom_id={cid}&tab=unfinished` |
| 学习内容页 / 公告页 | `studentLog/{cid}?...&tab=content`（学习内容）/ `tab=notify`（公告） |
| 课件查看器 | `studentCards/{cid}/{course_id}/{card_id}/ppt?...`；「打印课件」按钮进入 `/web/print` |
| 课件逐页阅读 | **优先用键盘 PageDown/PageUp 一次翻 1 页，单页停留 ≥4 秒即计页**（`keybd_event` VK_NEXT `0x22` / VK_PRIOR `0x21`）；正文区滚轮不稳定（可能不翻或一次跳 3 页，跳过的页不计页）；点大纲缩略图能换页但**不计页**。以顶部「学习进度：N/M」为唯一成功判据 |
| 课件内嵌选择题页 | PageDown 会在此页停住、页头显示「单选题 N分」+A/B/C/D+「提交」。**必须作答**：点选项（圆圈或文字）→ 点「提交」→ 自动前进、进度 +1。这类页可由自动化直接完成；点击无效时按"残留控制台遮挡 / 未最大化未前台 / 坐标过期"顺序排查后重试 |
| 课堂回顾页 | `student-lesson-report/{cid}/{lesson_id}/{card_id}`，**非课件**，勿在其中找打印课件，也无 PPT 翻页 |
| 课堂报告入口 | 必须 `studentLog/{cid}?tab=log` → 筛选「课堂」→ 点课堂记录进入；**直连报告 URL 会返回 errpage**（易误判为内容被删） |
| 课件打印导出 PDF | 本机 Edge 打印流程、坐标、坑见 [references/print-and-export.md](references/print-and-export.md) |
| 归档入口 | 首页 `.headerButtonGroup .text-btn`（文本"我的归档"），归档组件 `archiveDialog-components` |
| 登录方式 | 登录页 `/web?next=/v2/web/index&type=3`；勾选协议后点「微信快捷登录」文本链接 → 授权卡片绿色按钮，全程网页内完成，无需打开微信/扫码（详见下文「登录机制」） |
| 运行环境 | 用户用 **UU远程（GameViewer）** 远控本机；远控期间**禁止切 PIP**，只在当前主桌面操作（判据与排查见 [references/automation-environment-and-pitfalls.md](references/automation-environment-and-pitfalls.md)） |

## 页面与组件总览

- 首页顶部是 Element UI 的 `ElTabs`，学生视图项 id 为 `#tab-student`（"我听的课"），内容面板 `#pane-student`。
- 课程卡片组件链（自顶向下）：
  - `IndexView`（页面根业务组件，持有 `tableData1/tableData2`、`originalTableData1/2`）
  - `ElTabs` → `ElTabPane`（`#pane-student`）
  - `TcardGroup-component`（卡片组，prop `courseData` 即当前要渲染的课程数组）
  - `lessonCard-component`（单张课程卡片，外层是 `ElCard`，DOM 上表现为 `.el-card`）
- 单门课程的未完成页根组件名为 `StudentLogView`，根容器 `.studentLog__view--unfinished`。

## 登录机制（微信快捷登录）

学生端登录页为 `/web?next=/v2/web/index&type=3`（登录后重定向至 `/v2/web/index`），无需账密或扫码，可直接走微信快捷登录：

1. 先勾选「我已阅读并接受雨课堂用户协议、隐私政策」复选框，再点击文本链接「微信快捷登录」。
2. 页面检测到本地已安装且登录的微信后，弹出授权卡片：显示本地微信头像与昵称、绿色实心「微信快捷登录」按钮，另有「使用其他头像、昵称或账号」入口。
3. 点击绿色按钮后网页自行完成授权（状态短暂显示「登录中...」），随后跳转课程列表页；全程不打开微信客户端、无需扫码。
4. 若点击后未跳转，等待数秒再在网页内点一次即可；不要去碰本地微信。

要点：授权完全在网页内完成（浏览器拉起本地微信授权通道）。自动化时禁止 `launch_app` 打开微信客户端、禁止点击任务栏微信；登录页的「微信快捷登录」文本链接与授权卡片绿色按钮是两级入口，先点前者、再点后者。

补充（2026-11-02 本机虚拟桌面实测）：在本机 Edge（cu 操作的真实桌面）打开登录页，点「微信快捷登录」后**等待 3–4 秒**，页面会自动出现「已验证，可直接快捷登录」按钮（本机微信已登录且浏览器已检测到），点击即完成登录，**无需扫码**；若未出现再检查本机微信是否在线。

## 参考文档

按任务需要读取，不必全部加载：

1. [references/dom-and-vue.md](references/dom-and-vue.md) — 课程清单页 DOM、Vue 组件树与取值方法。
2. [references/student-log-unfinished.md](references/student-log-unfinished.md) — 未完成页完整选择器、空态/列表/任务项结构、Vue 源数据字段。
3. [references/api-and-request.md](references/api-and-request.md) — 接口清单、请求头、XTBZ、响应字段与直达链接规律。
4. [references/rpa-tech-notes.md](references/rpa-tech-notes.md) — 影刀 web 环境、execute_javascript 取值、轮询/限流/缓存等工程坑。
5. [references/print-and-export.md](references/print-and-export.md) — 课件打印导出 PDF 全流程（学习内容页/课件查看器 URL、打印按钮坐标、另存为操作、本机 Edge 登录与地址栏坑、bu CDP 打印不可用等教训）。
6. [references/courseware-reading-and-report.md](references/courseware-reading-and-report.md) — 课件逐页阅读推进（PageDown 翻页法、滚轮/大纲的局限、每页停留计页、**内嵌选择题页的识别与作答**、点击无效时的排查顺序）与课堂报告取题（入口链路、题目弹窗、P 几页码对照）；含长任务分段推进与会话中断恢复策略。
7. [references/automation-environment-and-pitfalls.md](references/automation-environment-and-pitfalls.md) — 运行环境与已知故障：UU远程（GameViewer）远控下的桌面切换禁令、PIP 切换失败、DEVICE_OFFLINE 与云主机不可用、未完成全量扫描标准流程、进度以页面为准。

## 通用硬约束

1. 默认**只读不写**：不提交作业、不签到、不回答、不退出课程；写操作前先 dry-run、白名单保护并导出基线。
2. 操作间隔约 1.5–2 秒，快速连续导航会触发 `/v2/web/forbidden`。
3. 已归档/历史课程不检测未完成；当前实际在学清单以页面真实渲染（`TcardGroup.courseData`）为准。
4. 不要把加载中间态的数组当成最终结果（见 references/rpa-tech-notes 的"数据时序"问题）。
5. 当前用户要求旁听课也归档且不扫描，优先于最后活跃时间规则。归档列表不返回 role，需保存已确认旁听 ID 并排除自动恢复，防止近期活跃旁听被恢复。当前实例识别记录为 `B:/05_生活文档/知识库/雨课堂旁听课程识别记录.json`；不要凭名称、旧配置或无权限页推定身份。课程清单必须来自真实列表，不得用硬编码 FALLBACK 补入缺失课程。
6. 课件逐页阅读是长任务，必须**分段推进 + 每段记录进度数字**（如每 10 页一段），中断后从记录页续读；不要把几十页翻页塞进单次调用，也不要从头重读。翻到某页停住不动时先判断是不是内嵌选择题页（见 references/courseware-reading-and-report.md 第 2 节）。
7. 虚拟桌面（PIP）断连后 `cu.switch_desktop("pip")` 重连实测经常连续失败；最多试 2 次，仍失败就停下说明现状并等用户处理，不要空转重试，更不要把"重连成功"当前提假设。
8. 用户通过 UU远程（网易 GameViewer）远控本机时**禁止切换虚拟桌面**：本机只有一个交互会话，切 PIP 会替换该会话的活动桌面，远控端画面直接变成空白桌面（窗口与进程并未移动）。此时只在当前主桌面操作；操作会占用用户鼠标键盘，开始前告知、结束即释放。判定特征与排查命令见 `references/automation-environment-and-pitfalls.md`。
9. 环境列表显示 online 不代表真能连接（曾出现列表 online、切换返回 DEVICE_OFFLINE、工具报"环境未就绪"）；遇到时先 `manage_environment` 查询并等待重连，不要反复重试同一调用。云主机（Linux）不支持 `plane="cu"`（返回 40003），`bu` 云浏览器已被用户禁用，云端不能替代本机 Edge。
10. 未完成扫描一律走"首页 → 课程 → 点未完成标签"的页面路径，全量逐课统计，并按当天日期标注已过截止项；不要把上一次的清单直接当当前结论。
