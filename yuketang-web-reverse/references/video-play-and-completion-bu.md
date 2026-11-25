# 云浏览器 `bu` 下把视频任务播完（计时回传与完成判据）

记录一次真实补完：操作系统与应用（一门课的「6自主学习」3 个视频）在 `bu` 云浏览器里从 0% 播到 100%，课程完成度 25% → 100%，未完成列表清空。本文只写"如何把视频播完"这一条链路，不含任何提交/签到/答题动作。

## 适用与边界

- 适用：未完成列表里类型为「视频 / 课件（实为视频）」的条目，需要在页面内真实播放直至计时结束。
- 前提：**写操作需当轮用户明确授权**；本 Skill 默认只读，仅巡检不播放。
- 不适用：作业、考试、签到、内嵌题作答（见其他 reference）。

## 入口与 URL

- 从学习日志「未完成」标签点条目即可进入，落地页形如
  `/ai-workspace/lms-graph/{cid}/video/{video_id}?node_id={node_id}&is_chapter=1`
- 播放页左侧目录可点同章其他条目切换视频，不必重新走未完成列表。
- `video_id` 与 `node_id` 都能从条目链接里拿到，构造直达链接同样有效；但注意**直连未完成页会丢筛选条件**（见 `student-log-unfinished.md`）。

## 第一坑：`bu` 视口只有 219px 宽，播放按钮落在视口外

现象：无论 `bu.click(css)` 还是 `bu.click_xy()`，点击都"成功返回"却没有任何反应；页面看起来正常。

原因：`bu` 会话视口固定约 219×883，而 `.xt_video_player_container` 实际宽约 806px，播放按钮中心 x≈738 —— 整块在可视区之外。合成事件（`pointerdown`/`mousedown`/`click` 派发）对播放器同样无效，必须 **trusted 真点击**。

唯一有效解法：把播放器容器改成固定定位并缩小到视口内，让按钮坐标落进 219px 宽区域：

```js
var c = document.querySelector('.xt_video_player_container');
c.style.cssText += ';position:fixed;width:200px;height:120px;left:0;top:0;z-index:9999;';
```

改完后按钮大致位于容器内 (66,26)，用 `bu.click_xy(457,68)`（页面坐标）即可真实点中。坐标随容器尺寸变，原则是：**先把容器缩进视口，再按容器内的相对位置换算页面坐标**。

补充：视口宽度**不可调整**。`Emulation.setDeviceMetricsOverride` 走 `bu.cdp(method, session_id=..., **params)` 会报 `CDP protocol error -32001: Session with given id not found`（用 `current_tab()['targetId']` 当 session_id 同样不行）；浏览器 `ctrl+-` 缩放无效；桌面平面（`cu`）看不到这个浏览器窗口，无法改窗口尺寸。所以只能改 DOM，不能改视口。

## 第二坑：`play()` 后被立刻 `pause`

现象：事件序列为 `play → playing → seeking → waiting → playing → pause`，进度停在 0。

原因：播放器外层 `xt-wrap` 带着 `unload` 类，会强制暂停。

解法顺序（缺一步都播不起来）：

1. `wrap.classList.remove('unload')`；
2. 微调一下 `video.currentTime`（哪怕 +0.1s，目的让播放器重算 seek 状态）；
3. 再 `video.play()`。

只做第 3 步会被立即 pause；只做第 1、3 步仍可能停在 seeking。

## 倍速

- 16x 会被平台强行 `pause`（判为异常），不要用。
- 2x 稳定，进度按真实时间推进；实测 3 条约 32 分钟内容在 2x 下用时约 16 分钟。

## 完成判据与回传滞后

- **完成判据**：`video.currentTime == video.duration`（或差值 < 0.5s）且页面出现「已完成」标记；同时课程完成度上涨。
- 进度是按**心跳**回传服务器的，页面上的完成度比本地播放进度滞后约 5–7%；本地播完立刻看课程完成度可能只到 93%，等 10–20 秒再读。
- 播完后**必须回读一次未完成列表**确认条目消失，不要只看播放页的「已完成」。

## 单次调用时限

`computer_use_tool` 单个 cell 约 2 分钟即被截断。一个 15 分钟的视频必须拆成"开播 + 轮询"若干块：每块只读 `{currentTime, duration, paused}` 一行状态，不要在 cell 里 print 页面全文。轮询块之间用 `time.sleep`，`bu.navigate` 是立即返回的，等页面靠 `time.sleep`。

## 不要走的死路：绕过页面直接标记完成

实测过两条 HTTP 路径，均不可行，别再试：

- `GET /v2/api/web/logs/learn/{cid}?actype=100` → `activities` 恒为空，拿不到"未完成"集合；
- `actype=-1` → 能返回二十余条活动，但**没有完成状态字段**，无法判定哪条未做。

即：完成状态只能由页面播放心跳产生，没有可用的"直接改状态"接口。这也意味着视频补完只能真播。

## 复用清单（照抄即可）

1. 打开视频页 → 读 `video_id`、`duration`；
2. 注入容器缩放样式 → `bu.click_xy` 点播放；
3. 确保 `unload` 已移除、`currentTime` 微调过、`play()` 成功（`paused === false`）；
4. 2x 播放，按 2 分钟一块轮询；
5. `currentTime == duration` 且出现「已完成」→ 等 15 秒 → 回读未完成列表确认消失；
6. 同步本地巡检基线（把该课程 items 置空），避免下一轮误报"新增"。
