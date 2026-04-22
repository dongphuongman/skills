# 条件过滤 rule 速查表

> **强制阅读规则：凡构建任何包含 `rule` 字段的条件对象（conditionsGroup、dataFilter 等），必须先查阅本文档，确认 rule 值合法。**

---

## ⚠️ 核心警告

**`rule` 必须使用字符串 code，不能使用运算符符号。**

| 错误写法 | 正确写法 |
|---------|---------|
| `"rule": "="` | `"rule": "eq"` |
| `"rule": "!="` | `"rule": "ne"` |
| `"rule": ">"` | `"rule": "gt"` |
| `"rule": ">="` | `"rule": "ge"` |
| `"rule": "<"` | `"rule": "lt"` |
| `"rule": "<="` | `"rule": "le"` |
| `"rule": "null"` | `"rule": "empty"` |
| `"rule": "not null"` | `"rule": "not_empty"` |
| `"rule": "not in"` | `"rule": "not_in"` |

写错的 rule 值会导致前端条件编辑器报 `TypeError: Cannot read properties of undefined (reading 'indexOf')`，且该错误不会在保存时提示，只在用户打开编辑界面时才爆出。

---

## rule 完整速查表（按字段类型）

| 字段类型 | 可用 rule 值 | 备注 |
|---------|------------|------|
| 文本类<br>`input` / `textarea` / `auto-number` 等（默认） | `like` `eq` `ne` `right_like` `left_like` `like_with_and` `in` `empty` `not_empty` | |
| 数值/时间类<br>`number` / `integer` / `money` / `rate` / `slider` / `formula` / `summary` / `date` / `datetime` / `datetime_s` / `time` / `year` / `month` | `eq` `ne` `gt` `ge` `lt` `le` `range` `empty` `not_empty` | `range` 时 `val` 传 `[min, max]` |
| 单选/省市区<br>`radio` / `area-linkage` | `eq` `ne` `in` `not_in` `empty` `not_empty` | |
| 多选/下拉<br>`checkbox` / `select` | `eq` `ne` `in` `not_in` `empty` `not_empty` | |
| 人员/部门/下拉树/表字典/组织角色<br>`select-user` / `select-depart` / `table-dict` / `select-tree` / `org-role` | `eq` `ne` `in` `not_in` `empty` `not_empty` | |
| 开关<br>`switch` | `eq` `ne` `empty` `not_empty` | |
| 关联记录<br>`link-record` | `eq` `ne` `in` `not_in` `empty` `not_empty` `linkage` | `linkage` = 查询工作表 |
| 子表 / 地图 / 图片 / 文件 / 手写签名<br>`sub-table-design` / `map` / `location` / `imgupload` / `file-upload` / `hand-sign` | `empty` `not_empty` | 仅支持判空 |
| 系统字段 `create_time` / `update_time` | 同数值/时间类 | |
| 系统字段 `create_by` / `update_by` | 同人员类 | |
| 系统字段 `bpm_status` | 同多选/下拉类 | |

---

## rule 含义说明

| `rule` 值 | 中文含义 |
|-----------|---------|
| `eq` | 等于 |
| `ne` | 不等于 |
| `like` | 包含（全模糊） |
| `right_like` | 以...开始（左前缀匹配） |
| `left_like` | 以...结尾（右后缀匹配） |
| `like_with_and` | 多词匹配（空格分隔多个关键词，全部命中） |
| `in` | 是其中一个（多值匹配） |
| `not_in` | 不是其中一个 |
| `gt` | 大于 |
| `ge` | 大于等于 |
| `lt` | 小于 |
| `le` | 小于等于 |
| `range` | 在范围内，`val` 传 `[min, max]` |
| `empty` | 为空（null 或空字符串） |
| `not_empty` | 不为空 |
| `linkage` | 查询工作表（仅 link-record 字段可用） |

---

## 条件项完整字段说明

以下字段说明同时适用于：
- 自定义按钮的 `conditionsGroup[].queryItems[]`
- 视图数据过滤的条件项
- 其他任何使用 `FilterItem` 结构的地方

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `field` | ✅ | string | 字段 model（如 `select_1775xxx`）或系统字段名（如 `create_time`） |
| `rule` | ✅ | string | 比较规则，必须是本文档中的合法 code |
| `val` | ✅ | string \| number \| array | 比较值；`empty`/`not_empty` 规则时传 `''`；`range` 时传 `[min, max]`；`in`/`not_in` 时可传数组 |
| `type` | ✅ | string | 字段控件类型（如 `input`、`select`、`number`、`date`） |
| `name` | — | string | 字段中文名（界面展示用，可省略） |
| `valText` | — | string | 值的展示文本；**传 `""` 而非 `null`**，否则部分 UI 渲染异常 |
| `timestamp` | — | boolean | 日期字段是否以时间戳形式传值 |

### conditionsGroup 分组字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `matchType` | ✅ | 组内条件关系：`'and'` / `'or'` |
| `queryItems` | ✅ | 条件项数组（见上表） |
| `showPop` | — | 固定传 `false`（UI 状态字段，后端忽略但前端依赖） |
