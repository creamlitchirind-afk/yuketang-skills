# 课程清单页 DOM 与 Vue 组件

对象：`https://changjiang.yuketang.cn/v2/web/index`，学生视图"我听的课"。

## 顶部视图切换

- 整个首页是 Element UI 的 `ElTabs`，两个主视图：我教的课 / 我听的课。
- 学生视图的 tab 项选择器：`#tab-student`；内容面板：`#pane-student`。
- 自动化进入后若不确定当前视图，先点一次 `#tab-student` 确保停在学生视图。

## 课程卡片 DOM

- 每张课程卡片是一个 `.el-card`（Element UI `ElCard`），由 `lessonCard-component` 渲染。
- 卡片在网格中通过 `ElRow` / `ElCol` 布局；卡片数量等于当前渲染课程数。
- 注意：卡片是数据驱动的，`.el-card` 数量随绑定数组变化，不能用"固定卡片数"假设。

## Vue 组件树（自顶向下）

```
IndexView
└─ ElTabs
   └─ ElTabPane (#pane-student)
      └─ TcardGroup-component   (prop: courseData / teachSearchKey / learnSearchKey)
         └─ lessonCard-component (每张卡片一个)
            └─ ElCard
```

### IndexView（页面根业务组件）

- `$data` 关键字段：
  - `tableData1` / `tableData2`：当前视图的课程数组（1=教师，2=学生）。
  - `originalTableData1` / `originalTableData2`：原始（未被搜索等操作修改的）数组。
  - `activeTab`、`archiveDialogVisible`、`joinClassDialog`、`lessonDialog` 等。
- 关键方法（实际构建中可能被压缩为 `[native code]`，无法直接 `toString`）：
  - `getList`：拉取课程列表并填充 tableData。
  - `SET_TABLE_DATA_2` / `SET_TABLE_DATA_1`：写入对应数组（对应 Vuex mutation）。
  - `opearteArchive`、`setTop`、`searchInListen`、`searchInTeach` 等。
- 关键 computed：`VUEX_TABLE_DATA_2`、`VUEX_TABLE_DATA_1`（映射 Vuex store）。

### TcardGroup-component

- props：`courseData`（要渲染的课程数组）、`teachSearchKey`、`learnSearchKey`。
- 方法：`updateList` 及一组图片预览相关方法（`initPreview`、`openPhotoSwipe` 等）。
- **`courseData` 是驱动真实渲染的权威数组**，其长度即页面卡片数；字段结构与 `courses/list` 接口项一致（见 api-and-request.md）。

## 从 DOM 拿到 Vue 实例

- 元素上的 `__vue__` 属性可拿到组件实例，例如：
  - `document.querySelector('#pane-student').__vue__` → 该面板的 `ElTabPane` 实例。
- 在组件树中按 `$options.name` 查找目标组件（BFS `$children`，用 `Set` 记录 `_uid` 防环）。
- 向上用 `$parent` 链，向下用 `$children`。

示例（查找 TcardGroup）：

```js
function getTcard() {
  const pane = document.querySelector('#pane-student');
  if (!pane || !pane.__vue__) return null;
  const seen = new Set();
  const q = [pane.__vue__];
  while (q.length) {
    const c = q.shift();
    if (!c || seen.has(c._uid)) continue;
    seen.add(c._uid);
    if (c.$options.name === 'TcardGroup-component') return c;
    c.$children.forEach(ch => q.push(ch));
  }
  return null;
}
```

## 我的归档对话框

- 入口：首页顶部 `.headerButtonGroup .text-btn`，按钮文本"我的归档"。
- 组件名：`archiveDialog-components`。
- 数据：`$data.classroomData` 为归档课程数组；归档项的课程 id 字段名为 `id`。
- 对话框内有"我教的课 / 我听的课"分组计数。
- 该对话框用于核对归档集合，但**归档集合不能等价刻画"当前在学清单"**：存在"未归档但已结束"的老课，因此判断是否在学仍以当前渲染数组为准。
