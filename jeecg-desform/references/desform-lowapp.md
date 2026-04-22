# lowApp 模式（敲敲云 / 零代码模式）

> 当用户提及「应用」「工作表」「敲敲云」「零代码」「lowApp」时，必须先阅读本文档，再执行任何操作。

---

## 概念说明

**lowApp 模式**（又称「敲敲云模式」「零代码模式」）是 JeecgBoot 中以「应用」为单位组织表单的零代码平台。

| lowApp 概念 | 对应普通模式 |
|------------|------------|
| 工作表 | 设计器表单（desform） |
| 应用 | 无对应概念 |
| 组织（租户） | 系统租户（tenantId） |

**层级体系：**

```
组织（租户）
  └── 应用分组（对应用归类，可选）
  └── 应用
        └── 工作表分组（对工作表归类，可选）
        └── 工作表（= 设计器表单）
```

**关键认知：**
- 「工作表」就是设计器表单，创建工作表 = 创建设计器表单，只是多了应用上下文
- 所有工作表相关操作（字段设计、视图、业务规则等）与普通模式完全相同，只需提前通过 `init_lowapp` 注入上下文
- 工作表有两个 ID：`menu_id`（菜单系统的 ID）和 `desform_id`（表单自身 ID）——操作菜单（改名、排序、删除）用 `menu_id`，操作表单内容（字段、数据）用 `desform_id` 或 `desformCode`

---

## 初始化

所有操作前，必须通过 `init_lowapp` 设置组织和应用上下文：

```python
import sys
sys.path.insert(0, r'<skill目录>/scripts')
from desform_lowapp_utils import init_lowapp

init_lowapp(
    api_base='<api_base>',
    token='<token>',
    tenant_id=<tenant_id>,
    app_id='<app_id>'  # 操作具体应用时必填
)
```

**初始化后**，`desform_utils` 中所有表单操作函数（`create_form`、`add_widget`、`update_widget` 等）会自动携带 `x-tenant-id` 和 `x-low-app-id` header，无需任何额外改动。

**切换应用（不重新初始化）：**

```python
from desform_lowapp_utils import set_app
set_app('<app_id>')  # 切换到另一个应用
```

---

## 操作前置流程

### 1. 确认组织

用户未指定组织时，查询所有组织，询问用户选择：

```python
from desform_lowapp_utils import get_tenants
tenants = get_tenants()
# 返回：[{'id': 2, 'name': '北京国炬信息技术有限公司', 'status': 1}, ...]
# → 展示给用户，让用户选择
```

### 2. 确认应用

用户未指定应用时，查询组织内所有应用，询问用户选择：

```python
from desform_lowapp_utils import get_apps
data = get_apps(tenant_id=<tenant_id>)
apps = data['apps']  # [{id, appName, ...}]
# → 展示给用户，让用户选择
```

### 3. 初始化上下文

用户确认组织和应用后，调用 `init_lowapp` 完成初始化。

---

## 函数速查表

详细说明见 `references/desform-lowapp-utils.md`。

### desform_lowapp_utils.py

**初始化**

| 函数 | 说明 |
|------|------|
| `init_lowapp(api_base, token, tenant_id, app_id=None)` | 初始化 lowApp 上下文（替代 `init_api`） |
| `set_app(app_id)` | 切换当前应用（不重新初始化） |

**组织管理**

| 函数 | 说明 |
|------|------|
| `get_tenants()` | 查询当前用户的所有组织 |

**应用管理**

| 函数 | 说明 |
|------|------|
| `get_apps(tenant_id=None)` | 查询组织下所有应用（含分组和关联） |
| `create_app(tenant_id=None, app_name, ...)` | 创建应用，返回应用ID |
| `edit_app(app_id, app_name=None, ...)` | 修改应用信息 |
| `copy_app(app_id, target_tenant_id=None)` | 复制应用到租户，返回新应用ID |
| `star_app(app_id, star=True)` | 标星/取消标星应用 |
| `delete_app(app_id)` | ⚠️ 删除应用（含所有工作表和数据） |

**应用分组（组织级别）**

| 函数 | 说明 |
|------|------|
| `get_app_groups(tenant_id=None)` | 查询应用分组列表 |
| `create_app_group(tenant_id=None, group_name, ...)` | 创建应用分组 |
| `add_app_to_group(group_id, app_id)` | 将应用加入分组 |
| `edit_app_group(group_id, group_name=None, ...)` | 修改分组 |
| `star_app_group(group_id, star=True)` | 标星分组 |
| `delete_app_group(group_id)` | 删除应用分组（应用不受影响） |

**工作表菜单（应用内）**

| 函数 | 说明 |
|------|------|
| `get_menus(app_id=None)` | 查询应用内所有菜单（工作表+分组） |
| `get_worksheet_groups(app_id=None)` | ⚡ 只查分组（语法糖，返回 `{count, groups}`） |
| `edit_worksheet(menu_id, menu_name=None, icon_type=None)` | 修改工作表名称/图标 |
| `sort_worksheets(order_info)` | 重排工作表顺序 |
| `delete_worksheet(menu_id)` | ⚠️ 删除工作表（含所有数据） |

**工作表分组（应用内）**

| 函数 | 说明 |
|------|------|
| `create_worksheet_group(app_id=None, group_name)` | ⚡ 创建分组（自动判断首次/追加） |
| `edit_worksheet_group(group_id, group_name)` | 改分组名称 |
| `move_worksheet_to_group(menu_id, parent_group_id, app_id=None)` | 移动工作表到分组 |
| `delete_worksheet_group(group_id)` | 删除分组（工作表不受影响） |

---

## 在 lowApp 下创建工作表（核心流程）

lowApp 模式下创建工作表与普通创建表单的唯一区别：
1. 需要提前 `init_lowapp`（注入 tenant/app header）
2. 调用 `create_form` 时传入 `app_menu_group_id`（决定工作表放在哪个分组）

### 完整流程

```python
import sys
sys.path.insert(0, r'<skill目录>/scripts')
from desform_lowapp_utils import init_lowapp, get_worksheet_groups
from desform_utils import create_form, INPUT, SELECT, DATE

# 1. 初始化
init_lowapp('<api_base>', TOKEN, tenant_id=<tenant_id>,
            app_id='<app_id>')

# 2. 查询分组，确定工作表放在哪个分组
groups = get_worksheet_groups()  # {'count': 2, 'groups': [{id, menuName, orderNum}]}

# 分组选择逻辑：
# - 无分组（count=0）：app_menu_group_id=None 或先创建分组
# - 有分组且用户未指定：默认使用第一个分组
# - 有分组且用户指定：使用用户指定的分组
group_id = groups['groups'][0]['id'] if groups['count'] > 0 else None

# 3. 创建工作表（与普通 create_form 完全相同，多一个 app_menu_group_id 参数）
widgets = [
    INPUT('客户名称', required=True),
    SELECT('客户类型', options=['企业', '个人']),
    DATE('创建日期'),
]
form_id, title_model = create_form(
    '客户信息', 'customer_info', widgets,
    app_menu_group_id=group_id
)
```

### 分组处理规则

| 场景 | 处理方式 |
|------|---------|
| 应用无分组，用户未要求分组 | `app_menu_group_id=None`（不传分组，工作表直接创建） |
| 应用无分组，用户要求分组 | 先 `create_worksheet_group()` 创建分组，再创建工作表 |
| 有分组，用户未指定 | 默认使用 `get_worksheet_groups()` 返回的第一个分组 |
| 有分组，用户指定了分组名 | 从 `get_worksheet_groups()` 中匹配 `menuName`，取对应 `id` |

---

## ⚠️ 关键注意事项

### 1. menu_id 与 desform_id 的区分

工作表有两个 ID，**绝对不能混用**：

| ID 类型 | 来源 | 用于 |
|--------|------|------|
| `menu_id` | `get_menus().menuList[].id` | 改名(`edit_worksheet`)、排序(`sort_worksheets`)、删除(`delete_worksheet`)、移动(`move_worksheet_to_group`) |
| `desform_id` | `get_menus().menuList[].menuUrl` | 表单字段操作（`update_widget`、`add_widget` 等）、数据 CRUD |
| `desformCode` | `get_menus().menuList[].desformCode` | 表单设计操作（推荐用此而非 desform_id） |

### 2. delete_worksheet 的危险性

`delete_worksheet(menu_id)` 会级联删除该工作表的**所有字段设计、视图配置和业务数据**，执行前务必向用户二次确认。

### 3. 封面图可选值

`create_app` 和 `edit_app` 的 `app_cover_img` 参数只允许 `coverImage001` ~ `coverImage012`，共 12 个值。不传时随机选取。

### 4. 应用分组 vs 工作表分组

这是两个独立的分组体系，不要混淆：

| | 应用分组 | 工作表分组 |
|-|---------|----------|
| 作用范围 | 组织级别，对多个应用归类 | 应用内，对工作表归类 |
| API 前缀 | `/online/lowAppGroup/` | `/online/lowAppMenu/` |
| 函数前缀 | `_app_group` | `_worksheet_group` |
