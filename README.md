# 雨课堂（长江雨课堂）自动化技能包

面向长江雨课堂学生端（`changjiang.yuketang.cn`）的两个可复用技能（Skill），按 `SKILL.md` 规范组织，可被支持该规范的 Agent 直接加载。

| 技能 | 用途 |
|---|---|
| [`yuketang-web-reverse`](yuketang-web-reverse/SKILL.md) | 学生端网页与接口结构拆解：课程清单接口、单门课程未完成扫描、课件逐页阅读推进（PageDown 翻页、每页停留计页、**内嵌选择题作答**）、课堂报告取题、课件打印导出；含运行环境与故障排查（远控禁切虚拟桌面、PIP 切换失败、DEVICE_OFFLINE 等） |
| [`yuketang-homework-auto-fill`](yuketang-homework-auto-fill/SKILL.md) | 主观题作业自动填写：定位 UEditor → 官方 API 写入 → 读回校验 → **不提交**，把纯文本答案交给用户自行提交 |

## 目录结构

```
yuketang-web-reverse/
├── SKILL.md
└── references/
    ├── dom-and-vue.md                     # 课程清单页 DOM 与 Vue 组件树
    ├── student-log-unfinished.md          # 未完成页选择器与数据字段
    ├── api-and-request.md                 # 接口、请求头、XTBZ、直达链接
    ├── rpa-tech-notes.md                  # 影刀 web 环境与 execute_javascript
    ├── print-and-export.md                # 课件打印导出 PDF 全流程
    ├── courseware-reading-and-report.md   # 课件逐页阅读与课堂报告取题
    └── automation-environment-and-pitfalls.md  # 运行环境与已知故障
yuketang-homework-auto-fill/
└── SKILL.md
```

## 方法文档

| 文档 | 内容 |
|---|---|
| [`docs/course-extraction.md`](docs/course-extraction.md) | 课程全量提取方法（2026-11 实战沉淀）：三层结构落点、`logs/learn` 分区与类型矩阵、作业两套链路（试卷 type 4 / 作业 type 19）、题面字体混淆与截图取证、课件进度与正文接口、成绩单模块口径、**"未批改 ≠ 0 分"的分数判读顺序**、批量提取的标签页与进程卫生、查重与落盘结构、8 条常见坑、13 项检查清单 |

## 使用约定（重要）

- **只读优先**：默认只做读取与统计，不提交作业、不签到、不退出课程。
- **不代提交**：作业填写完成后由用户自行核对并提交。
- **合规使用**：仅在本人账号、本人课程范围内使用，遵守学校与平台规定。
- 文中出现的课程 id、班级 id 仅为格式示例，不代表任何固定课程。

## 安装

把整个目录复制到 Agent 的 skills 目录即可，例如：

```bash
cp -r yuketang-web-reverse yuketang-homework-auto-fill ~/.doubao/agent_mode/workspace/.skills/
```

## 许可

MIT，见 [LICENSE](LICENSE)。
