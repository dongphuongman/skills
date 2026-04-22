# 列表视图完整指南

列表视图控制的是**数据记录如何在列表页展示**，与表单视图（控制填报界面的字段布局）完全独立。

> **创建表单时系统会自动生成一个默认的表格列表视图，无需主动调用视图创建方法。只有用户明确要求创建其他类型的列表视图时，才需要进行操作。**

> **返回值说明：** 所有 `add_list_view_*` 函数成功时返回新建视图的 ID（字符串），如 `"2039669254511738881"`，即接口响应的 `result` 字段。

## 函数速查表

| 函数 | 适用场景 |
|------|---------|
| **视图生命周期** | |
| `add_list_view_table(code, name)` | 创建表格视图（系统已自动创建，按需调用） |
| `add_list_view_board(code, group_field, ...)` | 创建看板视图 |
| `add_list_view_calendar(code, date_columns, ...)` | 创建日历视图 |
| `add_list_view_gantt(code, start_field, end_field, ...)` | 创建甘特图视图 |
| `query_list_views(code)` | 查询表单下所有列表视图 |
| `query_list_view_by_id(view_id)` | 查询视图完整配置 |
| `delete_list_view(view_id)` | 删除列表视图 |
| `sort_list_view(view_id, after)` | 将视图移到指定位置 |
| `reset_list_view_order(view_ids)` | 完全重排视图顺序 |
| **表格视图配置** | |
| `config_table_base(view_id, ...)` | 配置行高/自动刷新/列显隐/冻结列等基础设置 |
| `config_table_system_columns(view_id, show_fields)` | 配置系统字段显隐（default模式） |
| `config_table_sort(view_id, orders)` | 配置默认排序规则 |
| `config_table_quick_filter(view_id, query_list, ...)` | 配置快速筛选栏 |
| `config_table_left_filter(view_id, ...)` | 配置左侧分组筛选栏 |
| `config_view_data_filter(view_id, conditions, ...)` | 配置视图数据过滤条件 |

---

## 查询列表视图

### 查询表单下所有视图（精简）

`query_list_views(code)` 返回表单下所有列表视图的精简信息（id、name、type、seq）。

```python
from desform_utils import init_api, query_list_views
init_api('<api_base>', '<token>')

views = query_list_views('<form_code>')
# 返回示例：
# [
#   {"id": "2039669254511738881", "name": "默认表格", "type": "base", "seq": 0},
#   {"id": "2039961002911772674", "name": "项目看板", "type": "card", "seq": 1},
# ]
```

### 根据 ID 查询视图完整配置

`query_list_view_by_id(view_id)` 返回单个视图的所有配置字段。

```python
from desform_utils import init_api, query_list_view_by_id
init_api('<api_base>', '<token>')

view = query_list_view_by_id('2039961002911772674')
# 返回该视图的完整配置 dict
```

> 通常先调用 `query_list_views` 获取 view_id，再按需调用 `query_list_view_by_id` 获取完整配置。

---

## 删除列表视图

`delete_list_view(view_id)` 删除指定的列表视图。

```python
from desform_utils import init_api, delete_list_view
init_api('<api_base>', '<token>')

delete_list_view('2039669254511738881')
```

> 删除操作不可恢复，请确认 view_id 正确后再执行。

---

## 排序列表视图

### 简单排序

`sort_list_view(view_id, after)` 将指定视图移动到某视图之后。

```python
from desform_utils import init_api, sort_list_view
init_api('<api_base>', '<token>')

# 移到某视图之后
sort_list_view('2039961002911772674', after='2039367322597408771')

# 移到最前面
sort_list_view('2039961002911772674', after='first')
```

| 参数 | 说明 |
|------|------|
| `view_id` | 要移动的视图 ID |
| `after` | 排在哪个视图之后；传 `"first"` 则移到最前面 |

### 完全重排序

`reset_list_view_order(view_ids)` 按传入顺序完整重置所有视图的排列。需先查询出所有视图 ID，再按期望顺序传入。

```python
from desform_utils import init_api, query_list_views, reset_list_view_order
init_api('<api_base>', '<token>')

# 1. 查询当前所有视图
views = query_list_views('<form_code>')

# 2. 按期望顺序整理 ID 列表
ids = [v['id'] for v in views]   # 当前顺序
ids.insert(0, ids.pop(2))        # 例：把第3个移到最前

# 3. 提交重排序
reset_list_view_order(ids)
```

> `seq` 由函数自动从 1 开始分配，无需手动传入。

---

## 更新列表视图

`update_list_view(view_id, **fields)` 是通用更新接口，可修改视图的任意字段。

```python
from desform_utils import init_api, update_list_view
init_api('<api_base>', '<token>')

# 只改名称
update_list_view('2039961002911772674', name='项目看板')

# 同时改多个字段
update_list_view('2039961002911772674', name='计划视图', groupField='select_xxx')
```

> `view_id` 由 `add_list_view_*` 创建时返回，或通过查询接口获得。可传入任意视图支持的字段作为关键字参数。

## 列表视图类型

| 类型 | 说明 |
|------|------|
| **表格** | 最常规的列表视图，以 Table 组件逐行展示数据记录 |
| **看板** | 也称卡片视图，按指定分组字段将数据分列展示，适合状态流转类数据 |
| **日历** | 将数据挂载到日历上显示，需指定日期类型字段 |
| **甘特图** | 以甘特图形式展示任务/项目时间线，需指定开始和结束日期字段 |

---

## 表格（table）

最常规的列表视图。无需额外配置字段，直接显示表单的字段列表。

> **注意：创建表单时系统自动生成默认表格视图，通常无需手动创建。**

### 创建方式

```python
from desform_utils import init_api, add_list_view_table
init_api('<api_base>', '<token>')

add_list_view_table('<form_code>')                    # 后台自动命名
add_list_view_table('<form_code>', name='我的表格')   # 用户指定名称时传入
```

---

## 看板（board）

> **别名：** 卡片视图

数据按指定**分组字段**的字段值拆分成列，每列展示该值下的所有记录卡片。

### 分组字段限制

并非所有字段都可作为看板分组字段，仅支持以下类型：

| 支持的控件类型 | 说明 |
|--------------|------|
| `radio`（单选） | 按选项值分组 |
| `select`（下拉框） | 按选项值分组 |
| `switch`（开关） | 按开/关分组 |
| 人员字段（`select-user`，含创建人 `create_by`、修改人 `update_by`） | 按人员分组，存储 username |
| `table-dict`（表字典） | 按字典项分组 |
| `link-record`（关联表记录，**仅单条模式**） | 按关联记录分组 |

> **注意：** 多选字段（`checkbox`）、子表字段、文本字段等**不支持**作为分组字段。`link-record` 仅在非多选（single）模式下支持。

### 创建方式

```python
from desform_utils import init_api, add_list_view_board, get_form_fields
init_api('<api_base>', '<token>')

# 用户未指定分组字段 → 默认使用 create_by（创建人）
add_list_view_board('<form_code>')

# 用户指定了分组字段 → 先获取字段 model，再传入
_, fields = get_form_fields('<form_code>')
group_model = fields['状态']['model']   # 取字段 model
add_list_view_board('<form_code>', group_field=group_model)
```

- `group_field`：分组字段的 model（不传默认 `create_by`）
- `title_field`：标题字段的 **key**（看板视图特殊，使用 key 而非 model；不传则自动从表单 `config.titleField` 解析）
- `name`：视图名称（不传由后台自动生成）

### 看板视图配置更新

创建后，通过 `update_list_view(view_id, **fields)` 更新以下配置：

**1. 显示项（filterGroupType + filterGroupCondition）**

控制看板列的显示范围：

```python
# 显示全部（默认）
update_list_view(view_id, filterGroupType='all')

# 只显示指定项（select/radio/table-dict 等字段）
update_list_view(view_id,
    filterGroupType='part',
    filterGroupCondition='一年级,二年级'   # 逗号分隔的选项值
)

# 只显示指定人员（分组字段为 create_by/update_by/select-user 时）
# filterGroupCondition 存储逗号分隔的 username
update_list_view(view_id,
    filterGroupType='part',
    filterGroupCondition='zhangsan,lisi'
)
```

**2. 标题字段（titleField）**

卡片顶部显示的主标题，支持的控件类型：`input`、`textarea`、`money`、`integer`、`number`、`phone`、`email`、`link-record`。

> 传字段的 **key**（不是 model）

```python
_, fields = get_form_fields('<form_code>')
title_key = fields['项目名称']['key']
update_list_view(view_id, titleField=title_key)
```

**3. 显示字段名称（showLabel）**

卡片字段是否显示字段名称标签：

```python
update_list_view(view_id, showLabel=True)   # 显示字段名称
update_list_view(view_id, showLabel=False)  # 隐藏字段名称（默认）
```

**4. 配置显示字段（cardColumnList）**

卡片上展示哪些字段、顺序如何：

```python
_, fields = get_form_fields('<form_code>')

update_list_view(view_id, cardColumnList=[
    {"field": fields['姓名']['key'],   "show": True,  "seq": 0},
    {"field": fields['状态']['key'],   "show": True,  "seq": 1},
    {"field": fields['备注']['key'],   "show": False, "seq": 2},
])
```

> `field` 使用字段的 **key**（不是 model），通过 `get_form_fields` 的 `info['key']` 获取。未在列表中出现的字段默认隐藏。

**5. 封面（coverField + coverView）**

卡片顶部显示图片封面，封面字段必须是 `imgupload`（图片上传）类型：

```python
# 设置封面字段
_, fields = get_form_fields('<form_code>')
cover_key = fields['产品图片']['key']   # 必须是 imgupload 控件
update_list_view(view_id,
    coverField=cover_key,
    coverView=True    # True=允许点击查看大图（默认），False=不允许
)

# 不显示封面
update_list_view(view_id, coverField='none')
```

**6. 数据过滤、排序、自定义动作**

看板视图同样支持这三项配置，用法与表格视图完全一致：
- 数据过滤：`config_view_data_filter(view_id, conditions)`
- 排序：`update_list_view(view_id, orders=[{field, type}])`
- 自定义动作：详见 `references/desform-custom-button.md`

---

## 日历（calendar）

将数据记录挂载到日历中展示，需绑定日期类型字段。

### 日期字段配置规则

- 可以只选择 **1 个**日期字段（事件仅显示在该日期）
- 可以选择 **1 个开始日期 + 1 个结束日期**（事件跨日期范围显示）
- 可以配置**多组**日期字段（每组一个开始/结束对，适合有多种时间维度的数据）
- 日期字段必须是 `date` 或 `datetime` 类型

### 创建方式

```python
from desform_utils import init_api, add_list_view_calendar, get_form_fields
init_api('<api_base>', '<token>')

# 先获取字段 model（以便填入 begin_field / end_field）
_, fields = get_form_fields('<form_code>')

add_list_view_calendar('<form_code>', date_columns=[
    # 最简：只有开始日期
    {
        "begin_field": fields['开始日期']['model'],
        "tag": "计划",
        "field_type": "date",          # "date" 或 "datetime"
    },
    # 有开始+结束日期
    {
        "begin_field": fields['实际开始']['model'],
        "end_field":   fields['实际结束']['model'],
        "tag": "实际",
        "field_type": "date",
    },
])
```

**参数说明：**

| 参数 | 必填 | 说明 |
|------|------|------|
| `begin_field` | 是 | 开始日期字段 model |
| `end_field` | 否 | 结束日期字段 model；不填则只显示单个日期点 |
| `tag` | 是 | 分组标识，≤5 个字，用于区分多组日期 |
| `field_type` | 是 | `"date"` 或 `"datetime"`，必须与字段控件类型一致 |

> `title_field` 不传时自动从表单 `config.titleField` 获取。`name` 不传时由后台自动生成。

### 日历视图配置更新

创建后，通过 `update_list_view(view_id, **fields)` 更新以下配置：

**1. 默认视图（显示方式）**

```python
update_list_view(view_id, calendarDefault='dayGridMonth')
```

| 值 | 说明 |
|----|------|
| `"dayGridMonth"` | 月视图（默认） |
| `"timeGridWeek"` | 周视图 |
| `"timeGridDay"` | 日视图 |

**2. 标题字段（titleField）**

```python
update_list_view(view_id, titleField='input_xxx')
```

**3. 每周第一天（firstDay）**

```python
update_list_view(view_id, firstDay='1')  # 0=周日，1=周一，以此类推
```

**4. 只显示工作日（weekStatus + weekDayList）**

```python
# 只显示工作日，隐藏周六周日
update_list_view(view_id,
    weekStatus=True,
    weekDayList=['0', '6']   # 休息日列表，默认 0（周日）和 6（周六）
)
```

| 字段 | 说明 |
|------|------|
| `weekStatus` | `True`=只显示工作日，`False`=显示全部（默认） |
| `weekDayList` | 哪几天是休息日，字符串数组，`"0"`=周日，`"6"`=周六 |

**5. 是否显示农历（lunarStatus）**

```python
update_list_view(view_id, lunarStatus=True)
```

**6. 是否24小时制（hourStatus）**

```python
update_list_view(view_id, hourStatus=True)
```

**7. 数据过滤、排序、自定义动作**

与表格视图配置方式完全一致：
- 数据过滤：`config_view_data_filter(view_id, conditions)`
- 排序：`update_list_view(view_id, orders=[{field, type}])`
- 自定义动作：详见 `references/desform-custom-button.md`

---

## 甘特图（gantt）

以甘特图形式展示任务时间线，适合项目管理类场景。

### 字段配置规则

- **必须**指定 1 个**开始日期**字段
- **必须**指定 1 个**结束日期**字段
- 两个字段都必须是 `date` 或 `datetime` 类型

### 创建方式

```python
from desform_utils import init_api, add_list_view_gantt, get_form_fields
init_api('<api_base>', '<token>')

_, fields = get_form_fields('<form_code>')

add_list_view_gantt(
    '<form_code>',
    start_field = fields['开始日期']['model'],
    end_field   = fields['结束日期']['model'],
    field_type  = 'date',      # "date" 或 "datetime"，与字段控件类型一致
    # default_view = 'day',    # 默认 "day"，可省略
)
```

**参数说明：**

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `start_field` | 是 | — | 开始日期字段 model，不可与 `end_field` 相同 |
| `end_field` | 是 | — | 结束日期字段 model，不可与 `start_field` 相同 |
| `field_type` | 否 | `"date"` | `"date"` 或 `"datetime"`，必须与字段控件类型一致 |
| `default_view` | 否 | `"day"` | 甘特图默认视图模式 |
| `title_field` | 否 | 自动获取 | 不传则从表单 `config.titleField` 读取 |
| `name` | 否 | 后台自动 | 视图名称，不传由后台自动生成 |

### 甘特图视图配置更新

创建后，通过 `update_list_view(view_id, **fields)` 更新以下配置。

**1. 显示字段（showColumnList）**

> ⚠️ **与表格视图不同**：甘特图 `showColumnList` 的 `field` 字段存的是字段 **model**（如 `input_xxx_xxx`），而表格视图 `column_list.field` 存的是字段 **key**。

```python
_, fields = get_form_fields('<form_code>')

update_list_view(view_id, showColumnList=[
    {"key": fields['任务名称']['key'], "field": fields['任务名称']['model'], "show": True,  "seq": 0},
    {"key": fields['开始日期']['key'], "field": fields['开始日期']['model'], "show": True,  "seq": 1},
    {"key": fields['结束日期']['key'], "field": fields['结束日期']['model'], "show": True,  "seq": 2},
    {"key": fields['负责人']['key'],   "field": fields['负责人']['model'],   "show": False, "seq": 3},
])
```

**2. 自动刷新（autoRefresh）**

```python
update_list_view(view_id, autoRefresh=60)   # 60秒刷新一次，0=关闭
```

| 值 | 说明 |
|----|------|
| `0` | 关闭（默认） |
| `30` / `60` / `120` / `180` / `240` / `300` | 30秒、1分钟、2分钟、3分钟、4分钟、5分钟 |

**3. 默认视图（defaultView）**

```python
# 先查询当前视图，获取 ganttFields，再合并后更新
view = query_list_view_by_id(view_id)
update_list_view(view_id, ganttFields={
    **view['ganttFields'],
    'defaultView': 'week',   # day / week / month / quarter / year
})
```

**4. 是否显示未排期任务（showUnscheduled）**

以下情况视为未排期：①未设置开始或结束日期；②结束日期早于开始日期。

```python
view = query_list_view_by_id(view_id)
update_list_view(view_id, ganttFields={
    **view['ganttFields'],
    'showUnscheduled': True,   # True=显示，False=不显示（默认）
})
```

> 更新 `ganttFields` 时必须先查询现有值再合并传入，否则会覆盖其他甘特图字段配置（开始/结束日期字段等）。

**5. 颜色配置（colorFields）— 甘特图专属**

可根据单选字段的选项颜色为甘特条目着色。

```python
_, fields = get_form_fields('<form_code>')
view = query_list_view_by_id(view_id)

update_list_view(view_id, ganttFields={
    **view['ganttFields'],
    'colorFields': {
        'field': fields['状态']['model'],   # 颜色字段的 model
    },
})

# 清除颜色配置
update_list_view(view_id, ganttFields={
    **view['ganttFields'],
    'colorFields': {},
})
```

**颜色字段限制（三个条件必须同时满足）：**

| 条件 | 说明 |
|------|------|
| 字段类型 | 必须是 `radio`（单选）或 `select`（下拉框） |
| 非多选 | 字段不能是多选模式（`multiple: false`） |
| 已配置颜色 | 字段的选项必须设置了颜色值（`useColor: true`） |

> 如果某个 `radio`/`select` 字段在颜色下拉列表中不出现，原因通常是该字段的选项没有配置颜色——需要先在表单设计器中为该字段的选项添加颜色值。

**6. 数据过滤、排序、自定义动作**

与表格视图配置方式完全一致：
- 数据过滤：`config_view_data_filter(view_id, conditions)`
- 排序：`update_list_view(view_id, orders=[{field, type}])`
- 自定义动作：详见 `references/desform-custom-button.md`

---

## 表格视图配置项

以下函数用于配置已创建的**表格视图**的各项功能，均通过 `update_list_view` 调用 `PUT /desform/view/updateViewConfig`。

> **自定义动作**（`zdyan`）：自定义按钮通过独立 API 管理，详见 `references/desform-custom-button.md`。

---

### config_table_base — 表格基础设置

```python
from desform_utils import init_api, config_table_base
init_api('<api_base>', '<token>')

# 只改行高
config_table_base(view_id, line_height='small')

# 切换为自定义列模式
config_table_base(
    view_id,
    show_column='diy',
    column_list=[
        {"field": "input_name",    "show": True,  "seq": 0},
        {"field": "select_status", "show": True,  "seq": 1},
        {"field": "date_due",      "show": False, "seq": 2},
    ]
)

# 用 show_column_list 覆盖字段可见性（优先级高于 column_list 的 show）
config_table_base(
    view_id,
    show_column='diy',
    column_list=[{"field": "input_name", "show": True, "seq": 0}],
    show_column_list=[{"field": "input_name", "show": False}]  # 最终不可见
)
```

| 参数 | 默认 | 说明 |
|------|------|------|
| `line_height` | `'middle'` | 行高：`'small'`（紧凑）\| `'middle'`（中等）\| `'large'`（高） |
| `auto_refresh` | `0` | 自动刷新秒数，`0`=关闭，最小 `3`；常用预设：30/60/120/180/240/300 |
| `has_summary` | `False` | 是否开启数据统计 |
| `auto_submit_bpm` | `False` | 新增数据后是否自动提交关联流程 |
| `show_column` | `'default'` | `'default'`（与表单字段一致）\| `'diy'`（自定义） |
| `fixed_column_num` | `0` | 冻结前 N 列，`0`=不冻结 |
| `column_list` | — | 格式 `[{field, show, seq}]`，定义字段顺序和基础可见性（可不传，见下方说明）。**`field` 必须填字段的 `key`**（通过 `get_form_fields` 的 `info['key']` 获取） |
| `show_column_list` | — | 可见性覆盖，优先级高于 `column_list` 中的 `show`，格式 `[{field, show}]` |

> `column_list` 与 `show_column_list` 对同一字段 `show` 冲突时，以 `show_column_list` 的值为准。

> **未在 `column_list` 中列出的字段，仍按默认规则显示，不会自动隐藏。** 因此，若要隐藏某字段，必须将其显式加入 `column_list` 并设 `show: false`。

#### 两种 show_column 模式的行为差异（排查字段不可见时必看）

**普通字段（表单自定义字段）：**

| | `show_column='default'` | `show_column='diy'` |
|---|---|---|
| 字段数量上限 | **最多前 50 个** | 无限制 |
| 大字段（`textarea`/`editor`/`markdown`） | **强制排除，无法显示** | 默认排除，但可在 `column_list` 中显式设 `show=True` 来显示 |
| 不传 `column_list` 时 | 按表单字段顺序显示（受上述限制） | 显示所有非大字段控件 |
| 传 `column_list` 时 | 按列表精确控制 | 按列表精确控制（包括大字段） |

**系统字段的控制方式因模式而异：**

| | `show_column='default'` | `show_column='diy'` |
|---|---|---|
| 系统字段控制方式 | 通过 `systemColumnList` 控制 | 直接放入 `column_list` 控制 |
| `systemColumnList` 是否生效 | **生效** | **不生效** |
| `showColumnList` 是否影响系统字段 | **不影响** | **不影响** |

**系统字段默认可见性：**

| 系统字段 | `default` 模式默认 | `diy` 模式（无 column_list）默认 |
|----------|--------------------|----------------------------------|
| `create_time` 创建时间 | 隐藏 | 隐藏 |
| `create_by` 创建人 | 隐藏 | 隐藏 |
| `update_time` 修改时间 | 隐藏 | 隐藏 |
| `update_by` 修改人 | 隐藏 | 隐藏 |
| `bpm_status` 流程状态 | **显示** | 隐藏 |

**在 `diy` 模式下显示系统字段**，需将其写入 `column_list`：
```python
config_table_base(view_id, column_list=[
    {"field": "input_name",  "show": True, "seq": 0},
    {"field": "create_time", "show": True, "seq": 1},  # 系统字段直接放这里
    {"field": "create_by",   "show": True, "seq": 2},
])
```

**当用户反映某字段在列表中不可见时**，按以下顺序排查：

1. 该字段是否是 `textarea`/`editor`/`markdown` 类型？→ 两种模式均不支持显示
2. 当前是 `default` 模式，且该字段排在表单第 51 位之后？→ 切换为 `diy` 模式
3. 是系统字段？
   - `default` 模式：通过 `config_table_system_columns` 开启（`bpm_status` 默认已开启）
   - `diy` 模式：`systemColumnList` 无效，需将系统字段加入 `column_list` 并设 `show=True`
4. `column_list` 中该字段的 `show=false`？→ 改为 `true`
5. `show_column_list` 中该字段的 `show=false`？→ 优先级最高，必须修改此处（注意：`show_column_list` 不影响系统字段）

---

### config_table_system_columns — 系统字段显隐（default 模式专用）

两种模式均支持控制系统字段的显示，但机制不同：

- **`default` 模式**：使用本函数，通过 `systemColumnList` 控制
- **`diy` 模式**：本函数无效，需将系统字段写入 `column_list`（见上方示例）

`showColumnList` 不参与系统字段的显示控制，无论何种模式均如此。

| 字段 key | 说明 |
|----------|------|
| `create_time` | 创建时间 |
| `create_by` | 创建人 |
| `update_time` | 修改时间 |
| `update_by` | 修改人 |
| `bpm_status` | 流程状态 |

```python
from desform_utils import init_api, config_table_system_columns
init_api('<api_base>', '<token>')

# 只显示创建时间和创建人
config_table_system_columns(view_id, show_fields=['create_time', 'create_by'])

# 全部隐藏
config_table_system_columns(view_id, show_fields=[])

# 全部显示
config_table_system_columns(view_id, show_fields=['create_time','create_by','update_time','update_by','bpm_status'])
```

> 未包含在 `show_fields` 中的字段自动设为隐藏。

---

### config_table_sort — 默认排序

```python
from desform_utils import init_api, config_table_sort
init_api('<api_base>', '<token>')

config_table_sort(view_id, orders=[
    {"field": "date_due",        "type": "asc"},
    {"field": "select_priority", "type": "desc"},
])
```

---

### config_table_quick_filter — 快速筛选栏

```python
from desform_utils import init_api, config_table_quick_filter
init_api('<api_base>', '<token>')

config_table_quick_filter(view_id, query_list=[
    {"field": "input_name",    "name": "姓名", "type": "input",  "query_type": "like", "seq": 0},
    {"field": "select_status", "name": "状态", "type": "select", "query_type": "=",    "seq": 1},
])
```

| 参数 | 默认 | 说明 |
|------|------|------|
| `query_list` | — | 筛选字段列表，每项包含 `field`、`name`、`type`、`query_type`、`seq` |
| `query_button` | `True` | 是否显示查询按钮 |
| `wait_query` | `False` | 是否等待点击查询后才加载数据 |

---

### config_table_left_filter — 筛选列表

左侧分组筛选栏，按指定字段值分组列出可选项。

```python
from desform_utils import init_api, config_table_left_filter
init_api('<api_base>', '<token>')

config_table_left_filter(
    view_id,
    left_filter_field='select_status',
    left_filter_data='exist',     # 只显示有数据的选项
    left_filter_order='asc',
)
```

| 参数 | 默认 | 说明 |
|------|------|------|
| `left_filter_field` | — | 左侧筛选字段 model |
| `left_filter_data` | `'all'` | 数据范围：`'all'`（全部）\| `'part'`（部分）\| `'exist'`（有数据的） |
| `left_filter_order` | `'desc'` | 筛选项排序方向：`'asc'` \| `'desc'` |
| `left_filter_condition` | — | 附加过滤条件（可不传） |
| `add_form_default_status` | `True` | 新增表单时是否默认选中当前筛选项 |

---

### config_view_data_filter — 数据过滤

视图级数据过滤，限制此视图只显示满足条件的记录（类似 WHERE 子句）。**支持所有视图类型**（表格、看板、日历、甘特图）。

```python
from desform_utils import init_api, config_view_data_filter
init_api('<api_base>', '<token>')

# 简单场景：单组条件，只显示年级为"初一"的记录
config_view_data_filter(view_id, [
    {"field": "select_1775221412376_152628", "rule": "eq", "val": "初一",
     "type": "select", "name": "年级"}
])

# 多条件（同组内 and/or 关系）
config_view_data_filter(view_id, [
    {"field": "select_xxx", "rule": "in",  "val": ["初一", "初二"], "type": "select", "name": "年级"},
    {"field": "number_xxx", "rule": "gt",  "val": 10,               "type": "number", "name": "年龄"},
], match_type='and')

# 多分组：（姓王 或 姓张）且 年龄在 10~18
config_view_data_filter(view_id, [
    {
        "match_type": "or",
        "items": [
            {"field": "input_xxx", "rule": "like", "val": "王", "type": "input", "name": "姓名"},
            {"field": "input_xxx", "rule": "like", "val": "张", "type": "input", "name": "姓名"},
        ]
    },
    {
        "match_type": "and",
        "items": [
            {"field": "number_xxx", "rule": "gt", "val": 10, "type": "number", "name": "年龄"},
            {"field": "number_xxx", "rule": "lt", "val": 18, "type": "number", "name": "年龄"},
        ]
    }
], match_type='and')

# 清除数据过滤
config_view_data_filter(view_id, [])
```

**每个条件项字段说明：**

| 字段 | 必填 | 说明 |
|------|------|------|
| `field` | 是 | 字段 model 或系统字段名（如 `create_time`） |
| `rule` | 是 | 比较规则，见下方规则表 |
| `val` | 是 | 比较值；`empty`/`not_empty` 规则时传 `''` |
| `type` | 是 | 字段控件类型（如 `input`、`select`、`number`、`date`） |
| `name` | 否 | 字段中文名（界面展示用，可省略） |

> ⚠️ **构建条件前必须阅读 `references/desform-filter-rules.md`**，其中包含完整的 rule 合法值列表、各字段类型对应可用规则、及常见错误写法对照表。直接使用 `=`、`!=` 等符号会导致前端报错。

---

## 与筛选条件（高级查询）的区别

**数据过滤**（本文档）和**筛选条件（高级查询）** 是两个独立功能，用户提到以下关键词时不要混淆：

| 关键词 | 对应功能 | 文档 |
|--------|---------|------|
| 「数据过滤」「视图过滤」「sjgl」 | 本文档的 `config_view_data_filter`，管理员配置，按视图隔离 | 本文档 |
| 「筛选条件」「高级查询」「superQuery」 | 用户自定义查询条件，按表单+用户隔离，用户可自由增删改 | `references/desform-super-query.md` |

**上下文判断规则（重要）：**
- 用户在**创建/配置视图**的语境下说"筛选条件"、"添加条件"、"视图条件"等 → **使用数据过滤**（`config_view_data_filter`），这是视图级别的固定过滤
- 用户说的是**用户自己保存的查询条件**、**列表页高级查询面板**、**superQuery** → **使用筛选条件 API**（`desform-super-query.md`）
