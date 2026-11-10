---
name: yuketang-homework-auto-fill
description: 长江雨课堂主观题作业自动填写。当用户提供雨课堂作业链接（yuketang.cn/.../exercise/...），要求"帮我写作业/填主观题"时使用。流程：云浏览器打开作业 → 定位UEditor编辑器 → 通过UE官方API写入内容（不直接改iframe DOM）→ 校验getContent()非空 → 不提交 → 把完整答案纯文本输出给用户，由用户自己在雨课堂点提交。
---

# 雨课堂主观题自动填写（不提交版）

## 核心硬约束（必须遵守）

1. **绝对不提交**。填完即止，最后一步是把完整答案纯文本输出给用户，由用户自己在雨课堂里点"提交"。
2. **绝对不能直接改 UEditor 嵌套 iframe 的 body.innerHTML**。这是 2026-10-26 翻车的根因：DOM 视觉上显示了文字，但 UEditor 内部 content model 没更新，提交上去是空白。必须用 UEditor 官方 API。
3. 每次写入后必须用 `editor.getContent()` 读回验证非空，再告诉用户"已填好"。
4. 答案草稿先给用户过目，用户确认后再 setContent。
5. **运行平面（2026-11-10 更新）**：用户已明确禁用云浏览器（`plane="bu"`），且 UU远程远控期间禁止切换虚拟桌面。默认用本机 Edge（`plane="cu"`）操作；确需 bu 必须先取得用户明确同意。`cu` 不能执行 JS，此时改用"剪贴板粘贴"：打开作业页 → 选中 UEditor 编辑区 → `cu.set_clipboard(答案纯文本)` → `cu.hotkey("ctrl","v")` → 截图目视确认 → 由用户自行提交。视觉核对比 API 校验弱，必须在回复里说明这一限制。

## 作业页面结构（已实测，2026-10-26）

- 主页面 URL 形如 `https://changjiang.yuketang.cn/ai-workspace/lms-graph/<classroom_id>/exercise/<exercise_id>?node_id=<node_id>`
- 题目区域在主页面里的 **第一个 iframe** 中，src 形如 `https://changjiang.yuketang.cn/v2/web/iframe-exercise/<classroom_id>/<exercise_id>?noLeftMe=1`
- 富文本编辑器是**百度 UEditor**（class 含 `edui-editor`），正文在**嵌套的第三个 iframe** 里（`.edui-editor-iframeholder iframe`）
- 提交按钮文字是"提交"/"已提交"，在作业 iframe 内（不是主文档）
- 云浏览器操作使用 `computer_use_tool(plane="bu")`，内部模块是 `seed_browser_use`（不是文档写的 aha_browser_use）

## 执行流程

### 步骤 1：云浏览器打开作业页

```python
import seed_browser_use as bu
bu.navigate("<用户给的作业URL>")
bu.wait(6)
print(bu.screenshot().path)
```

如果跳登录页，调用 `interaction.request_action(type="browserControl")` 让用户扫码。

### 步骤 2：读取题目

```python
js = """
(() => {
  const f = document.querySelector('iframe[src*=iframe-exercise]');
  const doc = f.contentDocument;
  return doc.body.innerText.slice(0, 2000);
})()
"""
print(bu.js(js))
```

根据题目要求和用户之前的学习内容，撰写 500-800 字主观题答案（HTML 格式），先给用户过目。

### 步骤 3：定位 UEditor 实例

```python
js = """
(() => {
  const f = document.querySelector('iframe[src*=iframe-exercise]');
  const win = f.contentWindow;
  if(!win.UE) return 'no UE in window';
  const keys = win.UE.instants ? Object.keys(win.UE.instants) : [];
  return {hasUE: true, editorKeys: keys};
})()
"""
```

如果 `UE.instants` 为空，遍历作业 iframe 内所有嵌套 window 找 `UE`。

### 步骤 4：用官方 API 写入内容（关键）

```python
answer_html = "<p>...</p>..."  # 用户确认过的答案

js = f"""
(() => {{
  const f = document.querySelector('iframe[src*=iframe-exercise]');
  const win = f.contentWindow;
  const ed = win.UE.instants[Object.keys(win.UE.instants)[0]];
  ed.setContent({repr(answer_html)});
  const content = ed.getContent();
  const txt = ed.getContentTxt();
  return {{
    ok: txt.length > 50,
    htmlLength: content.length,
    txtLength: txt.length,
    preview: txt.slice(0, 80)
  }};
}})()
"""
print(bu.js(js))
```

**校验必须返回 `ok: true`**。如果 `txtLength` 很短或为 0，说明 setContent 没生效，换嵌套 iframe 找 UE 实例重试。

### 步骤 5：截图给用户看填好的效果

```python
print(bu.screenshot().path)
```

读图确认编辑器区域确实显示了完整答案。

### 步骤 6：输出纯文本答案给用户（最后一步）

把 `ed.getContentTxt()` 的完整纯文本贴在对话里，告诉用户：

- 内容已经填进云浏览器的答题框
- 我**没有点提交**，请你自己打开雨课堂检查后点"提交"
- 下面是完整文本，你也可以直接复制粘贴

## 绝对禁止

- ❌ 不要调用任何"提交"按钮的 click
- ❌ 不要用 `iframe.contentDocument.body.innerHTML = ...`
- ❌ 不要在 `getUEditor().getContentTxt()` 返回空时就告诉用户"填好了"
- ❌ 不要替用户按 Enter 或点发送

## 常见坑

| 现象 | 原因 | 解决 |
|---|---|---|
| setContent 后 getContent() 仍空 | UE 实例找错了（在嵌套 iframe 里） | 遍历所有 window 找 UE.instants |
| 视觉上看到文字但提交是空白 | 直接改了 body.innerHTML | 永远用 setContent |
| 提交按钮找不到 | 按钮在作业 iframe 内 | 在 iframe 内 querySelector |
| 云浏览器报 no active page | 页面失焦 | bu.resync() 后重试 |
| bu.type / bu.css 报参数错 | 该库实际 API 与文档不符 | 用 bu.js() 直接操作 DOM |

## 答案撰写规范

用户给链接后：
1. 先读题目（作业 iframe body.innerText）
2. 根据题目要求撰写 500-800 字主观题答案，结构：
   - 学了哪些知识点（分点）
   - 深入探讨过的问题（举 1-2 个具体例子）
   - 尚存问题/后续计划
3. 写完先给用户过目，用户确认后再 setContent
4. 填完不提交，把纯文本输出给用户
