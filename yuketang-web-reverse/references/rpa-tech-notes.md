# 影刀 Web 自动化工程要点

## 浏览器环境配置（set_user_environment）

- 复用本机 Edge 登录态时关键参数：
  - `specified_userdata = true`
  - `env_name = Default`
  - `profile_name = Default`
  - `user_data_dir = C:\Users\<用户>\AppData\Local\Microsoft\Edge\User Data`
- 之后用 `web.create` 启动浏览器，与手动双击打开的 Edge 是不同会话：手动启动的 Edge 可能停在二维码登录页，不能据此推断流程运行时的登录状态。

## execute_javascript 取值规则

- 必须用**显式命名的 `function(){...}`** 并在 **MAIN world** 执行，才能拿到返回值。
  - 裸 IIFE（立即执行函数）会返回 `None`。
  - ISOLATED world 会报 `_uia_temp_function is not a function`。
- `async` 函数可被自动 await；间隔用 `await new Promise(r => setTimeout(r, ms))`。
- 云浏览器 JS 通道对匿名 `async function()` 语句可能报"require a function name"，用 IIFE 包裹即可；对象字面量简写偶发 ReferenceError，建议显式写属性名。

## 数据时序（加载中间态）

- 课程数组在加载过程中会变化，直接读取可能拿到中间长度而非最终结果。
- 仅靠"等待数组长度稳定"无法保证正确：渲染是数据驱动的，当绑定数组暂时等于某个中间值时，卡片数也会与之相等，稳定条件照样成立。
- 可靠做法：
  - 以页面真实渲染数组 `TcardGroup.courseData` 为权威；
  - 或在调用方用显式白名单/学期字段过滤，保证结果与环境无关。

## 循环与导航块

- 遍历用 `workflow.forin`（输出槽 `loop_item` / `loop_index`），配对 `workflow.endloop`。
- 导航用 `web.browser.navigate`。
- 流程内变量在循环前初始化为空数组，再在循环中 `.clear()` / 追加。

## 限流与缓存

- 快速连续导航会触发 `/v2/web/forbidden`，操作间隔保持 1.5–2 秒。
- 绕缓存可加 `_t=Date.now()` 并配 `cache:'no-store'`；但这只能排除缓存，不能解决服务端/环境本身返回不同数据的问题。
- 长任务不要塞进单次 JS 调用：单次云浏览器 JS 长耗时（约 8 秒以上）可能 `GAC pipe read timed out`。应把进度挂到 `window`，拆成多次短调用。

## 命令行/脚本环境坑

- Windows PowerShell 5.1 不支持 `&&`（PowerShell 7 可用）；嵌套过多 `if`/花括号的长命令易被包装脚本解析失败，拆成独立步骤。
- CLI 的 `@参数文件` 与 here-string 可能冲突，改用 `Get-Content -Raw` 读入变量再传参。
- 脚本核对结果建议写入文件再读取，避免 stdout 被吞导致误判。
- 工具通道间歇无输出时，用简单 `print` 探活，或 `bu.resync()` 重连后重试。

## 安全与可回滚

- 默认只读；写操作前先 dry-run + 白名单，跑前导出基线（当前在学/归档两份）。
- 任何会改变课程状态的动作，先列出受影响对象再执行，确保可复原。
