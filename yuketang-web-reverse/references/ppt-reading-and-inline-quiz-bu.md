# PPT 阅读计时与内嵌题补完（云浏览器 `bu` 实战）

> 2026-11-17 实测：长江雨课堂「5. 离散时间信号与系统的时域分析-1」42 页，从 14/42 跑到 42/42；第 6、11、23 页内嵌题全部判对。环境为云浏览器 `bu`（`computer_use_tool`，`plane="bu"`），窗口约 746×678。

## 0. 一句话规则

**缩略图点一下不等于已读；必须让该页成为主视图的 active slide，并在该页停留约 4 秒，`学习进度` 才会 +1。内嵌题页不答会一直卡成"未读"；选完选项必须点底部「提交」，它交的是本题并自动进入下一题。**

## 1. 课件查看器结构

- 主容器：`.pptSwiper` → `.swiper-wrapper` → 42 个 `.swiper-slide`，类名含 `swiper-container-fade swiper-container-vertical`。
- 左侧大纲：`.pptThumbsSwiper`，每个缩略图外层 `.thumbImg-container`，未读页有「未读」角标。
- 当前页判定：`.pptSwiper .swiper-slide-active`；用 `Array.from(slide.parentElement.children).indexOf(slide)+1` 取页码。
- 顶部进度：页面文本 `学习进度：N/M`，这是唯一成功判据。

## 2. 翻页：真实垂直拖拽

1. 在正文区做**真实鼠标拖拽**：
   - 向上拖 = 下一页；向下拖 = 上一页。
   - 小幅度拖 140–160（归一化 0–1000 坐标）通常一次 1 页；一次大幅上拖可能直接跳 8 页（实测 1→9）。
2. 每翻一页回读 `.swiper-slide-active` 的页码，不要按固定次数推断到了哪页。
3. **不要**依赖这些方式：
   - 点左侧缩略图：只会让该页高亮/记已读，主视图可能仍停在原页；
   - `ArrowRight`：不翻页；
   - JS 改 slide 的 class / opacity / transform：会被 swiper 每帧回写；
   - 注入 `!important` CSS 强行切页：同样会被回写，还会留下 `z-index` 残留，把后面的页盖住。

## 3. 阅读计时：每页停约 4 秒

- 连续快速拖拽 24 页，进度只从 18 涨到 19；改为每页停留 4 秒逐页回退，进度稳定一页一涨到 40/42。
- 实操节奏：拖一页 → 等 4 秒 → 读 `学习进度`；涨了就继续，不涨先判断是不是内嵌题页。
- 不需要逐页从头读；已读页可以直接拖过，但新页必须让 active slide 停留计时。

## 4. 页面在后台：先置前，不要禁用过渡

- 页面 `visibilityState=hidden` 时，CSS 过渡被暂停：切页会停在两张幻灯片叠加的半透明状态，甚至新页 `opacity` 只有 0.12。
- 先执行：

```python
bu.cdp("Page.bringToFront", {})
```

  确认 `visibilityState=visible`、`hasFocus=true`，再等 1–2 秒；多数情况会自己渲染完成。
- **不要**全局禁用 transition/animation（`*{transition:none!important;animation:none!important}`）：实测主视图直接空白。
- 只对 `.pptSwiper .swiper-wrapper > .swiper-slide` 关过渡可以，但**绝不能覆盖 active slide 的 `transform`**：transform 负责把该页移到视口，覆盖后内容会跑到视口外，表现为空白。
- 如果之前手工给某页设过 `z-index:60/99`、`pointer-events:auto`，切走前必须 `removeProperty('z-index')`、`removeProperty('pointer-events')`，否则旧页会一直盖在新页上。

## 5. 内嵌题：识别、作答、提交

### 5.1 识别

- 页内出现 `.slide_layer MultipleChoice`（单选）或 `.slide_layer MultipleChoiceMA`（多选）。
- 选项是 `.problembullet`，底部按钮 `.submitButton`。
- 题干在 `.slide_layer` 的文本里；单选页头通常显示「单选题 N分」。

### 5.2 让题卡完整进入视口

侧栏占宽后，题卡右侧和提交按钮常被裁掉。用：

```javascript
document.body.style.zoom = '0.6';
```

746px 视口下，0.75 仍会裁掉右侧，0.6 才能让 900px 宽的题卡完整可见。

### 5.3 选选项

- 取选项 `.problembullet` 的 `getBoundingClientRect()` 中心，换算成 0–1000 归一化坐标，**真实鼠标点击**。
- 点中后 class 追加 `chosen`；回读每一项的 class，不要只看颜色。
- JS `element.click()` 可能只改样式或延迟写状态；只有回读到 `chosen` 才能认为选中。
- 多选题（`MultipleChoiceMA`）：逐个点击所有正确项，确认每一项都有 `chosen`，再统一提交一次。

### 5.4 点提交（用户明确规则）

1. 先 `submitButton.scrollIntoView({block:'center'})`；未滚动前 `elementFromPoint` 可能返回 `BODY`，说明按钮还没真正可点。
2. 重新取 rect 中心，真实点击。
3. 回读三件事：
   - 题干尾部出现「正确」或「错误」；
   - `学习进度` +1；
   - 该页「未读」角标消失。
4. **提交按钮交的是本题，不是整卷**；提交后平台自动进入下一题/下一页。

### 5.5 实测答案示例（仅作规则验证，不是通用答案）

- 第 6 页：`x[-n]` 反折等效于关于纵轴（n=0）对称 → A。
- 第 11 页：离散尺度变换要求缩放因子使变换后自变量取整数 → A。
- 第 23 页（多选）：`φ0/(2π)` 为有理数才周期 → A `2π/3`、B `π/5`、C `2π·3/7`，D `2π√2` 不选。

## 6. 已截止任务：先判断，不要挂机

- **作业/课前测**：打开 `iframe-exercise/{cid}/{exerciseId}?noLeftMenu=1&node_id=...`，底部显示「已截止」时只能看题与正确答案，选项不可作答，也没有重做入口。直接记录 0 分原因。
- **视频课件**：进入后弹窗「截止时间已到，完成情况已自动提交，继续观看进度将不会被记录」。点「我知道了」后即使播完也不会记进度，不要再挂机。
- 这两类不是"再试一次就能补"，交付里必须写成平台关闭，而不是"未做"。

## 7. 下一轮检查清单

- [ ] 先读顶部 `学习进度：N/M`，记录起点。
- [ ] 确认 `.pptSwiper` 存在，页面 `visible` + `hasFocus`；否则先 `Page.bringToFront`。
- [ ] 用真实拖拽翻页，每页停约 4 秒，逐页回读进度。
- [ ] 遇到 `MultipleChoice` / `MultipleChoiceMA` 页：缩放到 0.6 → 真实点选项 → 回读 `chosen` → `scrollIntoView` → 真实点提交 → 回读「正确」和进度 +1。
- [ ] 切走前清除手工设置的 `z-index` / `pointer-events` 残留。
- [ ] 超时任务先看「已截止」/视频弹窗；不能补就记录缺口，不重复尝试。
- [ ] 收尾复核课程总账（进度/得分/单元/待办）与未完成清单。
