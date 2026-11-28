# 学习通只读巡检 · 脚本轨道

配套 `xuexitong-capabilities/` 下的手动片段与页面地图；这里是可定时自跑的脚本线。与能力台的关系：能力台 = 手动片段与页面地图，脚本轨道 = 固定巡检线。

## 文件

| 文件 | 作用 |
|---|---|
| `scan_xt_bu.py` | 浏览器侧四模式：`health` / `discover` / `scan` / `scores` |
| `report_xt.py` | 本地汇总：增量比对、分课分节台账、写基线与存档 |
| `xt_state.json` | 本轮原始数据（课程、作业行、学习记录），运行时生成 |
| `baseline_xt.json` | 基线（每班次的未交作业标题、任务点进度），运行时生成 |
| `runs/` | 每轮结论存档 `*_script.md`，运行时生成 |

## 运行顺序

先指定运行时数据目录（不要放在仓库内，避免个人数据入库）：

```powershell
$env:XT_WATCH_DIR = "C:\path\to\xt_watch"
```

浏览器侧（`bu` cell 内，逐段跑，单段 < 2 分钟）：

```python
import aha_browser_use as bu
g = {'bu': bu, 'MODE': 'health', '__name__': '__main__'}
exec(open(r'<仓库路径>\xuexitong-capabilities\track\scan_xt_bu.py', encoding='utf-8').read(), g)
print(g['OUT'])
```

1. `MODE='health'` → 期望 `health ok cards=N courses=M`
2. `MODE='discover'` → `discover ok cards=N cids=N`
3. `MODE='scan', START=0, END=2` → 2 门一段，实测每门约 15 秒
4. 依次 `2-6`、`6-9`（班次数变化时按实际重算边界，每段 2–4 门）
5. 本地 `python report_xt.py --final` → 输出台账 + 写基线 + 存档

`scan` 会同时写 `scores`（学习记录里的任务点/出勤/积分/排名），所以**不需要再单独跑 scores**；`scores` 模式仅在只想刷新成绩时用。

## 输出样例（结构）

```text
共 N 门课（M 个班次）

**某课程**
- 章节任务点 x/y（未完成 z）
- 未交作业：某作业（新增）
- 签到 出勤 a / 缺勤 b（出勤率 c%）
```

## 与雨课堂脚本线的差别（重要）

- **登录**：学习通是扫码登录，`bu` 会话掉登录后只能由用户本人扫，脚本无法自愈。掉登录时 `health` 报 `login 失效（停在登录页）`。
- **入口是纯 li**：个人空间左栏「课程」不是 `<a>`，JS `click` 无效，必须 `bu.click('#tmp-menu-course')` 真点击，之后 `#frame_content` 才变成课程列表。
- **tab 靠 URL**：课程页 tab 是 `javascript:void(0)`，直接给课程 URL 追加 `&pageHeader=<n>` 就能加载对应 iframe（章节 1、资料 3、错题 4、自测 5、学习记录 6、作业 8、考试 9）。
- **作业没有截止时间**：`aria-label` 只有「标题 ; 状态」，平台不给日期。所以「未交」项只能列出、不能自动判过期；已知过期的项当轮需人工判断，不当作可做。
- **空课程正常**：章节/资料为空可能是课程本身没挂内容，不是抓取失败。

## 失效信号

- `health FAIL login 失效` → 需要用户扫码（`interaction_request_action(type="browserControl")`），不要代登录。
- `health FAIL 左栏找不到「课程」菜单项` → 个人空间改版，改 `JS_MARK_MENU`。
- `health FAIL 课程卡片 0 张` → 课程列表容器或卡片类名变了，改 `JS_CARDS`。
- `scan ok=0/N` → 课程页 iframe id 变了（`frame_content-zy` / `frame_content-cj`）。
- 任务点读到 `None`（报告里整节没有任务点行）→ 学习记录页文案变了，改 `_parse_study` 的正则。

## 只读约束

只读页面文本，不提交作业、不签到、不点答题、不进考试、不改任何学习数据。运行时 JSON/Markdown 只写 `XT_WATCH_DIR`，不写仓库。
