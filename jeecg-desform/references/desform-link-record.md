# 关联记录（link-record）与他表字段（link-field）完整参考

## 一、link-record 完整 options

```json
{
  "sourceCode": "",              // 源表单 desformCode（必填）
  "showMode": "single",          // "single" 单条 / "many" 多条
  "showType": "card",            // "card" 卡片 / "select" 下拉 / "table" 表格
  "titleField": "",              // 源表标题字段 model（必填）
  "showFields": [],              // 额外展示的字段 model 列表
  "allowView": true,             // 允许查看
  "allowEdit": true,             // 允许编辑
  "allowAdd": true,              // 允许新增并关联
  "allowSelect": true,           // 允许从已有记录选择
  "buttonText": "添加记录",
  "twoWayModel": "",             // 双向关联：源表中反向 link-record 的 model
  "dataSelectAuth": "all",       // "all" 全部 / "read" 仅有读权限的
  "filters": [],                 // 过滤条件
  "search": {},                  // 搜索配置
  "createMode": {},              // 新增模式
  "width": "100%",
  "defaultValue": "",
  "defaultValType": "none",
  "required": false,
  "disabled": false,
  "hidden": false
}
```

**className**: `form-link-record`，**icon**: `icon-link`

## 二、showType 三种模式

| 特性 | card（卡片） | select（下拉） | table（表格） |
|------|-------------|--------------|-----------|
| 显示样式 | 卡片网格 | 下拉框 | 表格行列 |
| 适用 showMode | single / many | many | many |
| 内置搜索 | 否 | 是 | 否 |
| 子表内可用 | 是 | 是 | 否 |
| 需要 card 包裹 | single 时是 | 否 | 否（独占整行） |
| 适用场景 | 字段多详细展示 | 数据量大空间有限 | 一对多行数据 |

## 三、filters 过滤条件

```json
{
  "filters": [{
    "matchType": "AND",
    "rules": [
      {
        "model": "status_field",
        "rule": "eq",
        "type": "text",
        "value": ["1"],
        "valueType": "value"
      },
      {
        "model": "depart_field",
        "rule": "eq",
        "type": "text",
        "value": ["select_depart_xxx"],
        "valueType": "field"
      }
    ]
  }]
}
```

- `valueType: "value"` — 固定值
- `valueType: "field"` — 引用本表字段 model

支持的 rule：`eq`, `like`, `gt`, `gte`, `lt`, `lte`, `range`, `in`, `notIn`, `isNull`, `isNotNull`

## 四、search 搜索配置

```json
{
  "search": {
    "enabled": true,
    "field": "input_xxx",
    "rule": "like",
    "afterShow": false,
    "fields": ["phone_xxx"]
  }
}
```

## 五、createMode 新增模式

```json
{
  "createMode": {
    "add": true,
    "select": false,
    "params": { "selectLinkModel": "" }
  }
}
```

- `add: true` — 打开源表新增弹窗
- `select: true` — 从其他 link-record 批量选择

## 六、twoWayModel 双向关联

表单 A 的 link-record 设 `sourceCode=B_code`，B 的 link-record 设 `sourceCode=A_code`，双方 `twoWayModel` 互指对方的 model。选择关联时自动在两边建立关系。

## 七、link-field（他表字段）

```json
{
  "linkRecordKey": "",       // link-record 的 KEY（注意是 key 不是 model！）
  "showField": "",           // 源表字段 model
  "saveType": "view",        // "view" 仅展示 / "save" 保存到当前表单
  "fieldType": "",           // 源字段控件类型
  "fieldOptions": {}         // 源字段 options 子集
}
```

**className**: `form-link-field`，**icon**: `icon-field`

### saveType 区别

- `view`：运行时动态查询展示，数据始终最新
- `save`：选择时保存字段值快照，同时保存 `{model}_dictText` 翻译值

### 关键注意

`linkRecordKey` 必须是 link-record 的 `key`（如 `1774581245281_700049`），不是 `model`（如 `link_record_1774581245281_700049`）。这是最常见的配置错误。

## 八、子表内使用

- showType 不能为 `table`（避免嵌套表格）
- 需设置 `isSubItem: true`
- 使用 `SUB_LINK_RECORD` 和 `SUB_LINK_FIELD` 快捷函数

## 九、Python 工具函数

```python
# 主表
LINK_RECORD(name, source_code, title_field,
            show_fields=None, show_mode='single', show_type='card',
            is_self=False, **kw)
# is_self=True：自关联树模式，自动在顶层写入 isSelf=true 并将 valueSplit 置空
LINK_FIELD(name, link_record_key, show_field,
           field_type='input', field_options=None, save_type='view', **kw)

# 子表
SUB_LINK_RECORD(name, parent_key, source_code, title_field,
                show_fields=None, col_width='200px')
SUB_LINK_FIELD(name, parent_key, link_record_key, show_field,
               field_type='input', field_options=None, col_width='150px')
```

## 十、自关联（表单数据树）

当 `sourceCode` 指向表单自身（link-record 关联自己）时，会形成**表单数据树**结构——记录之间通过父子关系形成无限级层级（如组织架构、任务分解、无限级分类）。

> 这是一种特殊配置，需要额外的 `isSelf: true` 顶层属性，且有"先有鸡先有蛋"的创建顺序问题。**遇到此场景必须阅读 `references/desform-self-tree.md`**，其中包含完整配置方法和两阶段创建法。

## 十一、常见踩坑

| 问题 | 原因 | 解决 |
|------|------|------|
| 关联记录不显示 | sourceCode 或 titleField 错误 | 核实源表编码和标题字段 model |
| link-field 始终空白 | linkRecordKey 写的是 model | 改为 link-record 的 key |
| link-field 数据不保存 | saveType 为 view | 改为 save |
| icon 显示异常 | icon 写成 icon-link-record | 改为 icon-link |
| 过滤条件不生效 | valueType 和 value 格式不匹配 | field 类型 value 须传本表字段 model |
