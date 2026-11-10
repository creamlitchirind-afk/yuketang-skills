# 接口、请求头与直达链接

## 课程列表接口（权威）

- 方法与 URL：`GET https://changjiang.yuketang.cn/v2/api/web/courses/list?identity=2`
- 无其他必需参数；在已登录页面会话内用 `fetch(..., {credentials:'include'})` 即可，**不需要 XTBZ 签名**。
- 响应结构：数组位于 `data.list`（即 `j.data.list`）。

### 单条课程字段

| 字段 | 含义 |
|---|---|
| `classroom_id` | 课程/班级 id（核心标识） |
| `course` | 对象，课程名取 `course.name` |
| `teacher` | 对象，老师名取 `teacher.name` |
| `name` | 班级名（可能含多个班，用分号连接） |
| `term` | 学期（如 `202601`） |
| `short_name` | 简称 |
| `time` / `create_time` / `top_time` | 时间相关字段 |
| `students_count` | 学生数 |
| `role` | 身份角色 |
| `project_type` / `ways_of_operation` / `color_code` | 项目类型/开课方式/颜色 |
| `published_kg_id` / `agent_id` / `university_course_series_id` | 其他关联 id |

## 页面自身 XHR（axios）的请求头

页面原生请求常见头，复刻请求时可参考：

- `Accept`
- `X-CSRFToken`：取自 cookie 中的 `csrftoken`
- `X-Client: web`
- `Xt-Agent: web`
- `university-id: 0`
- `uv-id: 0`
- `xtbz: ykt`

## XTBZ 反爬

- 多数后端 API 直连会返回 `XTBZ IS REQUIRED`，需要带签名头。
- 但 `courses/list` 等少数接口在页面同源会话内不强制；优先复用页面会话而非自行实现签名。
- 页面 cookie 中可能存在名为 `xtbz` 的 cookie（值是短字符串如 `ykt`），它与接口签名不是一回事；删除该 cookie 后课程列表接口仍可正常返回。

## 会话存储要点

- 关键 cookie：`csrftoken`、`django_language`、`xtbz`、`platform_type`。
- `localStorage` 含 `UserID`、`Auth`、`vuex` 等；`localStorage.vuex` 的持久化内容**不包含课程列表**（课程列表不持久化，每次进入页面重新拉取）。
- 无 Service Worker。

## 直达链接规律

### 课程级未完成页（推荐，100% 可用）

```
https://changjiang.yuketang.cn/v2/web/studentLog/{classroom_id}?classroom_id={classroom_id}&tab=unfinished
```

### 课件深链（type=2，已验证）

```
https://changjiang.yuketang.cn/v2/web/studentCards/{classroom_id}/{courseware_id}/{id}/ppt
```

其中 `courseware_id` 与 `id` 取自未完成页 `sourceData` 对应字段。

### 图谱/练习（type=14，无法仅靠 sourceData 构造）

- 实际跳转形如：
  `https://changjiang.yuketang.cn/ai-workspace/lms-graph/{classroom_id}/exercise/{exercise_id}?node_id={node_id}`
- `exercise_id` 与 `node_id` 不在已抓取的 sourceData 字段中，因此无法从列表数据直接拼出，需要点击时由页面路由生成。

### 其他类型

- 如 type=19 的深链规律尚未确认。
- 在未确认前，统一输出课程级未完成页链接，避免给出失效链接。

## 环境差异提示

- 不同浏览器/自动化环境调用同一 `courses/list` 可能返回不同结果（数量与个别课程存在差异），且用 no-store、时间戳、完整请求头都无法消除。
- 因此对"当前在学清单"有确定性要求时，应以页面真实渲染数组（`TcardGroup.courseData`）为准，或在调用方维护显式白名单，而不是无条件信任某次接口返回。
