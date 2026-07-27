---
name: Online全组件表创建模板
description: 创建包含全部26种控件的Online单表的完整字段配置模板和注意事项
type: feedback
---

创建全组件 Online 表时的字段配置模板，覆盖全部 26 种控件。

**Why:** 每次创建全组件表都需要记住各控件的正确配置方式，特别是 popup/popup_dict/link_down/cat_tree 等特殊控件容易配错。

**How to apply:** 直接复用以下模板，按需调整字段名和字典配置。

## 控件配置速查（26种）

| 控件 | dictTable | dictField | dictText | fieldExtendJson | 特殊说明 |
|------|-----------|-----------|----------|-----------------|---------|
| text | - | - | - | - | |
| password | - | - | - | - | |
| textarea | - | - | - | - | |
| date | - | - | - | `{"picker":"year"}` 可选 | dbType=Date |
| datetime | - | - | - | - | dbType=Datetime |
| time | - | - | - | - | dbType=string |
| radio | - | 字典编码如`sex` | - | - | 数据字典 |
| list | - | 字典编码 | - | - | 数据字典 |
| checkbox | - | 字典编码如`hobby` | - | - | 数据字典，需先创建 |
| list_multi | - | 字典编码 | - | - | 数据字典 |
| switch | - | - | - | `["Y","N"]` | |
| image | - | - | - | - | dbLength=500 |
| file | - | - | - | - | dbLength=500 |
| sel_user | - | - | - | - | |
| sel_depart | - | - | - | - | |
| pca | - | - | - | `{"displayLevel":"all"}` | |
| umeditor | - | - | - | - | dbType=Text |
| markdown | - | - | - | - | dbType=Text |
| sel_search | `sys_user` | `username` | `realname` | - | 表字典 |
| cat_tree | - | 类型编码如`B02` | - | - | 分类字典 |
| sel_tree | `sys_category` | `0` | `id,pid,name,has_child` | - | |
| link_table | `关联表名` | `id` | `显示字段1,字段2` | `{"showType":"card","multiSelect":false}` | |
| link_table_field | `本表link_table字段名` | - | `引用字段名` | - | dbIsPersist=0 |
| popup | Online报表编码 | `字段1,字段2` | `本表字段1,本表字段2` | - | 依赖Online报表！ |
| popup_dict | Online报表编码 | `value字段` | `显示字段` | - | 依赖Online报表！ |
| link_down | JSON配置 | - | - | - | 只配第一个字段，后续用text |

## 关键注意事项

1. **字段名不能以单字母+下划线开头**（正则 `/^[a-zA-Z]{1}(?!_)/`）。`f_text` ❌ → `fc_text` ✅；`f_num` ❌ → `fnum` ✅。下划线前至少 2 个字母。
2. **popup/popup_dict 的 dictTable 是 Online 报表编码，不是数据库表名**
3. **checkbox/list/radio 等用数据字典或表字典，不用 fieldExtendJson options**
4. **link_down 只有第一个字段配 link_down，后续级联字段用 text**
5. **cat_tree 插入数据前要先查节点 ID：rootList → loadTreeData**
6. **数据字典 = 系统字典**，对应菜单【系统管理】→【数据字典】
