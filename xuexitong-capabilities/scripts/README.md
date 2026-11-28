# scripts 使用说明

- `*.js` 是浏览器片段，不是 Node 脚本。用法：在 `computer_use_tool(plane="bu")` 的 cell 内读取文件内容，再 `bu.js(code)`。
- `course-list.js`：个人空间“课程”页执行，读课程卡片基础字段。
- `materials-list.js`：课程“资料”页执行，读文件/文件夹行与 `dataId`。
- `chapter-list.js`：课程“章节”页执行，或把 `frame_content-zj` 的 src 当顶层页执行。
- `homework-list.js`：作业列表页执行；跨域时先把 iframe 的 src 当顶层 URL 打开。
- `exam-list.js`：考试列表页执行；当前只做通用读取，具体字段待逐课验证。
- `study-record.js`：学习记录页执行；跨域时先把 iframe 的 src 当顶层 URL 打开。
- `self-test-list.js`：课程“自测”页执行；只读标题/题量，不触发 `goTest()`。
- `wrong-questions.js`：课程“错题集”页执行；空页返回 `rows: []`。
- `iframe-diagnose.js`：任意学习通页面执行，输出 iframe 拓扑与跨域状态。
- `convert-ppt-to-pdf.ps1`：本机 PowerPoint COM 转 PDF；默认输出到模块的 `data/pdf`，不修改原件。

所有片段只读；不包含提交作业、签到、改分、进入答题等写操作。

输出中的 `enc`、`stuenc` 等会话令牌不要写入公开文档或截图台账。
