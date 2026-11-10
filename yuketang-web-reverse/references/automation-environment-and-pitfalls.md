# 自动化运行环境与已知故障（2026-11-10 本机实测）

本文件记录"在哪台机器上跑、用什么桌面、遇到哪些失败"的经验。做雨课堂自动化前先读这一页，可以避免重踩同一批坑。

## 一、桌面与远控约束（最高优先级）

用户通过 **UU远程（网易 GameViewer）** 远程控屏使用本机 LAPTOP-MDHIVKSV。

- 判定特征：`GameViewer` / `GameViewerServer` / `GameViewerHealthd` 进程位于 session 1；`Win32_VideoController` 中存在 `GameViewer Virtual Display Adapter`。
- 机制：本机只有一个交互式会话（session 1）。`cu.switch_desktop("pip")` 切换的是**该会话的活动桌面**，远控软件采集跟随活动桌面推流，因此远控端画面立刻变成空白虚拟桌面；窗口、进程、文件实际上都没有移动。
- 规则：
  1. 用户正在远程看屏时**禁止** `switch_desktop("pip")`；一律在当前主桌面（main）操作。
  2. 在主桌面操作会占用用户的鼠标与键盘，开始前一句话告知，完成后立即停手释放。
  3. 想做到"我操作、用户也能同时用"，需要第二个登录会话（RDP 多会话或另一台机器），本机不具备。

只读排查命令：

```powershell
(Get-Process -Id $PID).SessionId
Get-Process -Name GameViewer,GameViewerServer,SunloginClient,ToDesk,AnyDesk -ErrorAction Ignore | Select-Object Name,Id,SessionId
Get-CimInstance Win32_VideoController | Select-Object Name,CurrentHorizontalResolution,CurrentVerticalResolution
```

## 二、PIP 切换本身不可靠

- 本机多次 `cu.switch_desktop("pip")` 返回 None，或报 `COMPUTER_USE_TOOL_RUNTIME_FAILED: Unable to switch the Computer Use desktop`，随后截图仍是主桌面。
- 最多尝试 1–2 次，失败就停止并说明现状；连续用同一参数重试会触发 stuck-loop 告警，也不会成功。
- 失败后不要假设"已经在 PIP"，后续坐标一律按当前实际桌面重取。

## 三、多环境不可用的表现

- 多环境列表显示本机 `online`，但 `manage_environment switch` 返回 `DEVICE_OFFLINE`，`computer_use_tool` / `PowerShell` 报"当前执行环境无法确认或尚未就绪"。列表状态存在滞后，不可直接当真。
- 处理：先 `manage_environment list` / `get_current`，再等待设备重连（实测 1–3 分钟内会自行恢复，恢复前不要反复调用工具）。
- 云主机（Linux）：`computer_use_tool` 的 `plane="cu"` 不支持，返回 `error_code 40003 computer_use_tool method not supported for plane cu`；`bu` 云浏览器已被用户明确禁用。因此云端**不能**替代本机 Edge 完成雨课堂操作（还缺微信登录态）。

## 四、未完成扫描的标准流程（全量 9 门课）

1. 回首页 `https://changjiang.yuketang.cn/v2/web/index`，逐门点课程卡片进入 `studentLog/{cid}`；**不要**直接堆 `tab=unfinished`（无任务课程会 302 到 `tab=log`，造成误判）。
2. 进课程后点顶部"未完成"标签（`.rain-tabs__nav-item`，窗口非最大化时约 (440,232) 千分比）。
3. 先查空态 `.unfinished-study__state-empty`，再遍历 `li.unfinished-study__item`。
4. 每门课记录：课程名、`classroom_id`、未完成计数；逐条记录标题、类型、状态、截止、是否计分。
5. 汇总分三类：①计分作业/课前测（必须提交）②课件未读完（页数进度）③课堂签到（过期不可补）。
6. 用当天日期比对截止时间，已过期的明确标注"已过截止"，不要沿用旧结论。

首页课程卡片坐标（窗口非最大化、千分比）：左列 x≈322、右列 x≈522；行 y≈262 / 410 / 580 / 750 / 900。

## 五、进度以页面为准

- 课件阅读进度可能由服务端记录推进：本地读到 24/46，重新登录后页面显示 40/46。每次以页面右上角进度数字为准，不要用本地记忆覆盖页面。
- 阅读任务是长任务，分段推进并每段记录进度数字，中断后从记录页续读。

## 六、常见误判清单

- 直连 `tab=unfinished` 被 302 → 误判"所有课程都无未完成"。
- 窗口未最大化时坐标错位，点选项/按钮无反应；先双击标题栏最大化再取坐标。
- 误点窗口顶部工具栏（约 885,50）会弹出浏览器扩展面板，点内容区空白可关闭。
- 环境列表 `online` ≠ 真能连接，以实际工具调用为准。
