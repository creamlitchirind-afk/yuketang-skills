# 单门课程未完成页结构

对象：`https://changjiang.yuketang.cn/v2/web/studentLog/{cid}?classroom_id={cid}&tab=unfinished`
根组件：`StudentLogView`；根容器：`.studentLog__view--unfinished`。

## 进入方式（重要：有重定向坑）

- 直接用 URL 访问 `tab=unfinished` 时，若该课程没有未完成任务，会被 **302 重定向到 `tab=log`**，从而误判"全部无未完成"。
- 可靠做法：
  1. 先打开 `.../studentLog/{cid}?classroom_id={cid}&tab=log`，等待加载；
  2. 再点击顶部"未完成"标签：`.rain-tabs__nav-item`（按文本"未完成"定位）；
  3. 即使没有任务，也会停在未完成页并显示空态，不会被重定向。

## 空态与列表（互斥）

- 空态容器：`.unfinished-study__state-empty`；空态文案：`.rain-empty__text`，文字"暂无未完成任务"。
- 列表容器：`.unfinished-study__list`（`ul`）；任务项：`li.unfinished-study__item`。
- 判断逻辑：先查空态元素是否存在；存在则该课程无任务，否则遍历 `li.unfinished-study__item`。

## 单个任务项内的选择器

| 信息 | 选择器 | 说明 |
|---|---|---|
| 标题 | `.unfinished-study__item-title` | 任务名称 |
| 类型 | `.unfinished-study__type-text` | 外层 `.unfinished-study__type-card`；如"课堂""试卷""课件" |
| 状态 | `.unfinished-study__item-status` | 如"0/60页""未开始""未签到" |
| 时间/截止 | `.unfinished-study__item-time` | 带修饰符如 `--deadline-far`；文本如"01-31 23:59 截止 (94天后)""已超时" |
| 是否计分 | `.unfinished-study__score-tag` | 该元素存在即计分 |
| 跳转按钮 | `.unfinished-study__arrow` | `aria-label` 为"去完成" |

## 页面上的三层筛选 + 计分开关

- 时间窗筛选：`.unfinished-study__range-tab`
- 状态筛选：`.unfinished-study__timeout-tab`
- 类型筛选：`.unfinished-study__type-tab`
- 仅看计分：`.unfinished-study__score-checkbox`
- 做全量采集时不要启用这些筛选，保持默认即可。

## Vue 源数据（StudentLogView.$data）

- 任务数组对应字段 `sourceData`，单条任务字段：
  - `type`：数字类型（如 2=课件，14=图谱/练习，19 等）。
  - `id`：任务 leaf id。
  - `courseware_id`：字符串，课件 id。
  - `title`：标题。
  - `create_time`：创建时间。
  - `end`：截止时间（毫秒时间戳，或 `null`）。
  - `count`：计数（如页数）。
  - `view`：完成情况，如 `{depth:1, done:false}`。
  - `has_mooc`：是否含 MOOC。
- 组件方法 `handleOpenUnfinishedLeaf(t)`：
  - 若 `t.link_url` 存在则 `location.assign` 跳转，否则提示不支持跳转。
  - `link_url` 封装在渲染闭包里，`$data` / `$props` / BFS 均取不到，因此无法直接从 sourceData 拿到每条任务的完整深链。

## 逐任务采集建议

- 用 DOM 遍历 `li.unfinished-study__item` 而非整列文本合并，保证每条任务独立成行。
- 每条读取：标题、类型、状态、时间文本、是否计分（元素存在性）。
- 链接优先用课程级未完成页链接（100% 可用）；逐任务深链的构造见 api-and-request.md。
