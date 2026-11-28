# 学习通网页结构（实测版）

- 实测日期：2026-11-23
- 站点：`chaoxing.com`（学习通网页版学生端）
- 用途：给“学习通能力台”的脚本与排错提供页面地图；不是学习内容。
- 说明：本文已脱敏，不含账号、课程名、班级 ID、成绩、Cookie、Token、二维码 uuid。

## 1. 登录与二维码

- 登录页：`https://passport2.chaoxing.com/login?fid=&newversion=true&refer=https%3A%2F%2Fi.chaoxing.com`
- 二维码图片：`document.querySelector('#quickCode')`
  - `src` 形如 `https://passport2.chaoxing.com/createqr?uuid=<uuid>&fid=-1`
  - 原图约 270×270；可直接 `bu.download(src)` 下载，再放大并加白边发给用户。
- 扫码确认后落地：`https://i.chaoxing.com/base?ws=1`
- 登录检查：个人空间出现“课程”入口和课程卡片，即已登录；不要依赖账号昵称判断。
- 二维码是登录态入口：只发给当前用户；不要在公开文档或截图台账里保留 uuid。

## 2. 个人空间与课程清单

- 入口：`https://i.chaoxing.com/base?ws=1`
- 左侧菜单“课程”点击后，内容 iframe 变为：
  `https://mooc2-ans.chaoxing.com/visit/interaction?s=<session>`
- iframe `id="frame_content"`，同源，可直接 `contentDocument`。
- 课程卡片：`div.course.learnCourse`，含：
  - `input.courseId`、`input.clazzId`、`input.curPersonId`
  - `h3 a` 的课程名（`span.course-name`）
  - `p.line2.color3` 的教师名
  - 课程链接：`a[href*="stucoursemiddle"]`
- 课程链接形如：
  `https://mooc1.chaoxing.com/visit/stucoursemiddle?courseid=<courseid>&clazzid=<clazzid>&cpi=<cpi>&ismooc2=1&v=2`
- 同名课程必须按 `clazzid` 区分；同一门课可能有多个班次，具体数量随账号变化，不要写死。
- 课程进度：部分卡片 `.btm-cover` 有“任务点进度: x/y z%”，部分卡片可能无该块；脚本返回 `progress` 可能为空，不能把“无进度”当成 0。

## 3. 课程主页与 tab

- 课程主页（重定向后）：
  `https://mooc2-ans.chaoxing.com/mooc2-ans/mycourse/stu?courseid=<courseid>&clazzid=<clazzid>&cpi=<cpi>&enc=<enc>&pageHeader=<n>&v=2`
- 已实测 `pageHeader`：
  | tab | pageHeader |
  |---|---:|
  | 任务 | 0 |
  | 章节 | 1 |
  | 讨论 | 2 |
  | 资料 | 3 |
  | 错题集 | 4 |
  | 自测 | 5 |
  | 学习记录 | 6 |
  | 作业 | 8 |
  | 考试 | 9 |
  | 课程图谱 | 12 |
- 顶部 tab 是普通链接；点击后只换中部 iframe，不整页刷新。
- 章节页 iframe id：`frame_content-zj`，src 形如 `https://mooc2-ans.chaoxing.com/mooc2-ans/mycourse/studentcourse?...&stuenc=<token>`；父页里可能拿不到 `contentDocument`，直接把 src 当顶层 URL 打开即可读 `已完成任务点: x / y`、目录与任务点。
- 若某门课程章节为空（“暂无章节内容”），可能是课程本身未挂章节，不是抓取失败。

## 4. 资料页（最重要）

- 资料页 iframe id：`frame_content-zl`
- src 形如：
  `https://mooc2-ans.chaoxing.com/mooc2-ans/coursedata/stu-datalist?courseid=<...>&clazzid=<...>&cpi=<...>&ut=s&t=<...>&stuenc=<...>`
- 同源，可直接 `contentDocument`；也可以把 src 当顶层 URL 打开。
- 文件行：`ul.dataBody_td`
  - 文件名：`li.dataBody_name_stu`（第一行）
  - 大小/教师/日期：同一行的文本
  - 下载链接：`a[href*="downloadData"]`
  - `downloadData?dataId=<id>&classId=<clazzid>&cpi=<cpi>&courseId=<courseid>&ut=s`
  - `dataId` 是稳定标识；下载需要当前登录 cookie。
- 文件夹：行内 `[onclick]` 调用 `toOpen(...)`，没有直接下载链接；点击后进入下一层，再重新抓行。
- 已实测下载：`.doc` 45KB → 46,080 B；`.pptx` 6MB → 6,354,300 B。
- 已实测转 PDF：`scripts/convert-ppt-to-pdf.ps1` 用 PowerPoint COM（`ppSaveAsPDF=32`），一份 122 页课件转成约 3.89 MB PDF；转换不修改原件。
- 注意：“教师课件”文件夹是 `toCourseware()`，不是普通 `toOpen` 文件夹；它可能跳到课程课件/立体化教材，需要单独处理。

## 5. 作业页

- 作业 tab iframe id：`frame_content-zy`，src 在 `mooc1.chaoxing.com`，与父页 `mooc2-ans.chaoxing.com` **跨域**；`contentDocument` 为 null。
- 解法：取 iframe 的 `src`，用 `bu.navigate()` 当顶层 URL 打开，再读 DOM。
- 作业行：`li[onclick*="goTask"]`
  - `aria-label`：`标题 ; 状态`（如“某作业 ; 待批阅”）
  - `data`：`https://mooc1.chaoxing.com/mooc-ans/mooc2/work/task?...&workId=<id>&answerId=<id>&enc=<token>`
  - 状态：未交 / 待批阅 / 已完成
- 进度：`.work-progress-box` 文本如 `4/5`。
- 作业页只读；不要点“提交”或“保存”。

## 6. 考试页

- 考试 tab `pageHeader=9`；iframe id `frame_content-ks`，src 指向 `mooc1.chaoxing.com/exam-ans/mooc2/exam/exam-list?...`，与父页跨域；把 src 当顶层 URL 打开后读。
- 某门课程可能显示“暂无考试”；这是课程状态，不是抓取失败。
- 其他课程若存在考试，按标题/状态/时间读取；未验证具体 DOM 前标记 ⚠。

## 7. 学习记录页

- 学习记录 tab `pageHeader=6`；iframe id `frame_content-cj`，src：
  `https://stat2-ans.chaoxing.com/study-data/index?courseid=<...>&clazzid=<...>&cpi=<...>&ut=s&t=<...>&stuenc=<...>`
- 与父页跨域；把 src 当顶层 URL 打开。
- 可读字段：
  - 章节任务点：`x / y 个`、完成进度 `z%`
  - 当前排名：`n 名`
  - 在线学习：`n 次` 章节学习次数
  - 课程积分：`n 分`
  - 签到：出勤、缺勤、已过期/早退/迟到/病假/事假/公假、出勤率
  - 学习任务：章节测验、在线考试、课程作业、AI 实践、互动测验、分组任务
  - 讨论：发帖/回帖/获赞
  - 自测：次数/题目数量
- 平台会给出“出勤率较低”等智能提醒；只记录，不替用户做判断。

## 8. 错题集与自测

- 错题集 `pageHeader=4`；iframe id `frame_content-ctj`，src：
  `https://mooc2-ans.chaoxing.com/mooc2-ans/wrongque/page?...&stuenc=<token>`
  - 空页文本：`选择题型 / 选择知识点 / 暂无错题`。
  - 有题时的行结构尚未实测；脚本 `scripts/wrong-questions.js` 只在空页返回 `rows: []`，有题时先观察再扩。
- 自测 `pageHeader=5`；iframe id `frame_content-zc`，src：
  `https://mooc1.chaoxing.com/mooc2/exam/exam-list?courseid=<...>&clazzid=<...>&cpi=<...>&type=1`
  - 列表项：`li`；标题 `.right-content .overHidden2`；题量 `.status`；点击 `goTest(...)`。
  - 自测列表可能同时含复习模板与历史记录，题量从个位数到上百不等。
  - `scripts/self-test-list.js` 只读标题/题量，不进入答题。
- 课程图谱 `pageHeader=12`、讨论 `pageHeader=2` 已确认入口；内容结构未验证。

## 9. 已踩过的坑

1. 学习通大量使用 iframe，且 iframe 可能跨域；不要直接对子 iframe 做 `contentDocument`。
2. 作业、学习记录、章节、考试、自测的 iframe 都可能跨域；把 `src` 当顶层 URL 打开后再读，不要直接对子 iframe 做 `contentDocument`。
3. 资料页文件夹没有直接下载链接，必须点进下一层再抓。
4. 同名课程不是重复卡片，先看 `clazzid`；不要按标题去重。
5. 课程页刚点击 tab 时 iframe 还没加载，先 `wait_for_load` 或检查 `contentDocument`。
6. 资料下载链接依赖登录 cookie，不能复制到无登录的 HTTP 客户端直接请求。
7. 课程进度可能在卡片相邻块，抓课程卡片时不要假设 `div.course` 内含全部字段。
8. 二维码 uuid 只用于当前登录会话，不写入公开台账。

## 10. 实测边界

- 已实测单门课程的章节任务点、资料根目录、作业清单、学习记录、错题空页、自测列表；具体课程名与数字不写入公开文档。
- 已实测另一门课程章节为空、资料“教师课件”暂无文件；说明不同课程挂载差异很大，空内容不一定是抓取失败。
- 未验证：有错题时的行结构、逐项成绩/积分明细、全课程考试覆盖、增量 diff 脚本。
