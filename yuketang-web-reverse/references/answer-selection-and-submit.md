# 客观题的选择与提交（作业 / 课件内嵌题）

2026-11-15 实盘沉淀。两类题型长得完全不同，但共用一条铁律：**能用真实鼠标点的，不要用 JS 点击**。JS `element.click()` 往往只改样式、不写答题状态，最容易得出"这题点不了"的错误结论。

## 0. 通用判定：什么时候算"选中/提交成功"

| 动作 | 成功判据 | 失败的样子 |
|---|---|---|
| 选中选项 | 选项元素 class 多出状态类（如 `chosen` / `is-checked`），或圆圈变实心 | 只是变蓝一下、class 不变；换页后状态丢失 |
| 提交本题 | 页面回显「本题得分」「正确答案」「正确/错误」 | 按钮点了没反应、页面只翻页 |
| 整卷提交 | 顶部计数从 `0/3 题` 变为 `3/3 题`，出现「提交成功」 | 计数不动 |

**不要**拿"看起来选中了"当成功；一定回读 class 或回显文本。

## 1. 作业 / 课前测（`iframe-exercise`）

入口：未完成列表 → 点任务箭头 → `ai-workspace/lms-graph/{cid}/exercise/{id}?node_id=...`，真正题目在 iframe `/v2/web/iframe-exercise/{cid}/{id}?noLeftMenu=1`。

### 1.1 读题

- iframe 内 `body.innerText` 是**字体加密乱码**（同一题每次渲染字形还会重排），不能用来做题。
- 题干与选项**只能截图读**；得分与正确答案是明文（`本题得分：\d`、`正确答案：\s*[A-D]`）。
- 截图前先把 iframe `scrollIntoView`，否则可能只拍到渐变背景。

### 1.2 坐标：iframe 偏移是最常见的"点了没反应"

iframe 内层文档视口（如 748×661）不等于它在页面里的位置。按内层 `getBoundingClientRect()` 直接点页面会整体偏移。正确算法：

```js
var fr = iframe.getBoundingClientRect();
var scale = fr.width / iframe.contentDocument.documentElement.clientWidth;
var pageX = fr.x + innerRect.x * scale + innerRect.width * scale / 2;
var pageY = fr.y + innerRect.y * scale + innerRect.height * scale / 2;
// bu.click_xy(pageX / innerWidth * 1000, pageY / innerHeight * 1000)
```

### 1.3 选择与提交（关键语义）

1. **每题选完点底部「提交」= 交本题并自动进下一题**，不是"交整卷"。
2. 顶部 `0/3 题` **不会**随勾选实时变化，提交后才更新。
3. 已答多题再切页，会弹「N 道已作答习题未提交，需要一起提交吗？」→ 选「帮我提交」一次交全。
4. 选项是 Element UI radio（`label.el-radio`）；**真实点击** label/圆圈，JS 点击可能只改高亮。
5. 未提交就切题会触发 `homework-problem-change-guard-dialog` 守卫弹窗；后台标签里它会卡在 `dialog-fade-leave`，合成点击无效——这是**必须真人处理**的检查点，走 `interaction.request_action`（`browserControl`）交用户，不要绕过。
6. 平台可能弹腾讯「安全校验」拖拽（按住起点依次经过 1、2、3 到终点），同样必须真人完成。

## 2. 课件里嵌的「课堂单选题」

PPT 查看器 `studentCards/{cid}/{course_id}/{card_id}/ppt` 里，个别页不是内容页，而是 `slide_layer MultipleChoice` 的随堂题：

- 选项：`.problembullet`（每页 A/B/C/D，四角圆圈）
- 提交：`.submitButton`（右下角）
- 症状：不答这页就一直标「未读」，整份课件的阅读进度会卡住（如 72 页卡在 69/72）。

正确顺序：

1. 左侧大纲 `thumbImg-container` 点目标页（第 n 页对应索引 n−1）。
2. **真实鼠标**点选项圆圈中心，确认 class 变成 `problembullet quizImg chosen`。
3. **真实鼠标**点 `.submitButton`。注意按钮可能被裁到可视区外（出现过 `pointer-events:none`、x≈938 贴边）；先把窗口/布局拉到完整宽度（如 1280 宽），确认按钮整块可见再点。
4. 成功判据：按钮旁回显 **「正确」**，该页「未读」消失，右上角学习进度 +1。

本轮实例：第 14/30/66 页分别答 C（极点 s=+2 → 不稳定）、B（m≤n 才能直接用 s 域模拟图/框图）、B（ROC 包含 jω 轴才能由 F(s) 得 F(jω)），进度 69/72 → **72/72**，未读清零。

## 3. 翻页读 PPT（内容页）

- 左侧缩略图逐个点最稳：`.thumbImg-container` 索引 i 对应第 i+1 页，每页停 1.1–1.5 秒。
- 键盘 `ArrowRight` 只在开头有效，连续快按会被节流（墙钟 1 分钟可能只前进 1–2 页）。
- 进度以右上角 `学习进度：n/N` 为准，不以"页面看起来换了"为准。

## 4. 防坑清单

1. **先真实点击，再下结论**：JS 点击不生效不代表元素不可点。
2. 元素在视口外/被裁时，先展开布局或滚动，再点；`pointer-events:none` 常是布局问题，不一定是禁用。
3. 每步都回读状态（class、计数、回显），不要连续盲点。
4. 遇到验证码、守卫弹窗、安全校验：停手交用户，不绕过、不伪造轨迹。
5. 只做用户当轮明确授权的题；提交前核对答案，交付里写清提交了什么。
