# 学习通运行时数据目录（不入库）

本目录只保留这份说明。实际运行时快照写到本地 `XT_WATCH_DIR` 或本机个人目录，不提交到 Git。

## 预期产物

| 文件 | 内容 |
|---|---|
| `course-list-<date>.json/.md` | 课程卡片：课程 ID、班级 ID、教师、状态、任务点进度（运行时生成） |
| `materials-list-<date>.json/.md` | 某课程资料根目录与子目录文件，含 `dataId`/下载链接 |
| `homework-list-<date>.json/.md` | 作业标题、状态、workId/answerId |
| `study-record-<date>.json/.md` | 任务点、排名、积分、签到/出勤、作业计数 |
| `exam-list-<date>.json` | 考试列表；可能为空 |
| `self-test-list-<date>.json/.md` | 自测列表项、题量、examId/testId |
| `wrong-questions-<date>.json/.md` | 错题集；空页为 `rows: []` |
| `pdf/<courseware>.pdf` | PPT/PDF 转换样例 |

## 口径

- 课程清单来自个人空间课程卡片；同名课程按 `clazzid` 区分。
- 资料清单的 `dataId` 是下载稳定标识；下载需要当前登录 cookie。
- 作业状态原样记录“未交 / 待批阅 / 已完成”，不推断分数。
- 学习记录只记录页面数字；不替用户判断成绩或补做。
- 任何账号、姓名、学号、课程名、班级 ID、成绩、出勤、Cookie、Token、二维码 uuid 都不写入公开仓库。
