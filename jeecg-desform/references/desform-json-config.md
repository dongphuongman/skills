# desform_creator.py JSON 配置格式

通用脚本 `scripts/desform_creator.py` 支持通过 JSON 配置文件创建表单，避免每次编写大量 Python 代码。

## JSON 顶层结构

```json
{
  "formName": "表单中文名称",
  "formCode": "module_form_code",
  "layout": "word",
  "titleIndex": 0,
  "fields": [
    {"name": "字段名", "type": "控件类型", ...控件参数}
  ],
  "menuParent": "父菜单名称",
  "menuIcon": "ant-design:appstore-outlined",
  "expand": {
    "js": "// JS 增强代码",
    "css": "/* CSS 增强代码 */",
    "url": {
      "js": "",
      "css": "/desform/expand/css/custom.css"
    }
  }
}
```

| JSON 字段 | 必填 | 默认值 | 说明 |
|-----------|------|--------|------|
| `formName` | 是 | - | 表单中文名称 |
| `formCode` | 是 | - | 表单编码（英文，模块名前缀） |
| `layout` | 否 | `"auto"` | 布局模式：`auto`/`half`/`full`/`word`（详见 `desform-layout.md`） |
| `titleIndex` | 否 | `0` | 标题字段在 fields 中的索引 |
| `fields` | 是 | - | 字段定义数组 |
| `menuParent` | 否 | - | 生成菜单 SQL 的父菜单名称 |
| `menuIcon` | 否 | `ant-design:appstore-outlined` | 父菜单图标 |
| `expand` | 否 | - | JS/CSS 增强配置（见下方说明） |

## 字段定义（fields 数组）

每个字段只需 `name` + `type`，其余参数可选：

```json
{"name": "工程名称", "type": "input", "required": true}
{"name": "工程类别", "type": "radio", "options": ["土建", "安装", "装饰"]}
{"name": "验收日期", "type": "date"}
{"name": "金额", "type": "money", "unit": "万元"}
{"name": "自动编号", "type": "auto-number", "prefix": "GCYS"}
{"name": "条码", "type": "barcode"}
{"name": "定位", "type": "location"}
{"name": "签字", "type": "hand-sign", "required": true}
{"name": "---", "type": "divider", "text": "分隔标题"}
{"name": "性别", "type": "radio", "dictCode": "sex",
 "options": [{"value": "1", "label": "男"}, {"value": "2", "label": "女"}]}
```

## 主表支持的 type 及可选参数

**所有主表控件（除 divider/text/buttons/tabs 布局控件外）均支持以下两个通用参数：**

**`remoteAPI`** — 远程取值接口地址（URL 支持 `{{上下文变量}}` 和 `${字段model}` 动态传参）：
```json
{"name": "真实姓名", "type": "input", "remoteAPI": "/desform/api/getName?userId={{sysUserCode}}"}
```
> 详见 `desform-remote-api.md`

**`defaultExpr`** — 默认值表达式，支持上下文变量 `{{varName}}` 和字段引用 `$fieldModel$`，仅新增时生效：
```json
{"name": "操作人", "type": "input", "defaultExpr": "{{sysUserName}}"}
{"name": "记录时间", "type": "input", "defaultExpr": "{{sysDate}} {{sysTime}}"}
```
> 详见 `desform-context-vars.md` — 完整变量列表、混合语法、注意事项。

| type | 可选参数 | 说明 |
|------|---------|------|
| `input` | `required`, `placeholder`, `unique`, `remoteAPI`, `fillRuleCode`, `readonly` | 单行文本 |
| `textarea` | `required`, `remoteAPI`, `fillRuleCode`, `readonly` | 多行文本 |
| `number` | `required`, `unit`, `precision`, `remoteAPI` | 数字 |
| `integer` | `required`, `unit`, `remoteAPI` | 整数 |
| `money` | `required`, `unit`, `remoteAPI` | 金额 |
| `date` | `required`, `fmt` | 日期（fmt 默认 `yyyy-MM-dd`） |
| `time` | `required` | 时间 |
| `switch` | - | 开关 |
| `slider` | - | 滑块 |
| `rate` | - | 评分 |
| `color` | - | 颜色 |
| `radio` | `options`(必填), `required`, `dictCode` | 单选 |
| `select` | `options`(必填), `required`, `multiple`, `dictCode` | 下拉 |
| `checkbox` | `options`(必填), `required`, `dictCode` | 多选 |
| `select-user` | `required`, `multiple` | 选人 |
| `select-depart` | `required`, `multiple` | 选部门 |
| `select-depart-post` | `required` | 选岗位 |
| `org-role` | `required`, `multiple` | 组织角色 |
| `phone` | `required` | 手机 |
| `email` | `required` | 邮箱 |
| `area-linkage` | `required` | 省市级联 |
| `table-dict` | `dictTable`, `dictCodeCol`, `dictTextCol`, `style`, `multiple`, `queryScope` | 表字典（options 内置 dictTable/dictCode/dictText/queryScope；**style=popup 时 dictTextCol 会被替换为该控件自身的 model**；queryScope=database 时仅支持 style=select） |
| `select-tree` | `categoryCode`(必填), `dataFrom`(必填), `tableConf`, `required`, `multiple` | 下拉树；**`categoryCode` 和 `dataFrom` 必须显式传入，不可省略**；`dataFrom="category"` 时传 `categoryCode`（默认 `"B02"`）；`dataFrom="table"` 时传 `tableConf`（含 name/code/text/pidField/rootPid/leaf/converIsLeafVal） |
| `file-upload` | `required` | 文件上传 |
| `imgupload` | `required` | 图片上传 |
| `hand-sign` | `required` | 手写签名 |
| `auto-number` | `prefix` | 自动编号 |
| `barcode` | `sourceModel`, `codeType`(`barcode`/`qrcode`), `maxWidth` | 条码/二维码 |
| `capital-money` | `moneyField`, `moneyWidgetKey` | 大写金额（关联 money/formula/summary 字段） |
| `text-compose` | `expression` | 文本组合（$model$ 引用字段） |
| `location` | `required`, `defaultCurrent`, `showMap` | 定位 |
| `map` | `height`, `zoom`, `lng`, `lat` | 地图（百度地图） |
| `ocr` | `ocrType`(`normal`/`id_card`/`vat_invoice`/`train_ticket`), `fieldMapping` | 文本识别 |
| `formula` | `mode`, `expression`, `decimal`, `unit` | 公式 |
| `divider` | `text` | 分隔符（name 会被忽略，用 text） |
| `editor` | `required` | 富文本 |
| `markdown` | `required` | Markdown |
| `text` | `text`, `fontSize`, `fontColor`, `align`, `bold` | 静态文本（不存储数据） |
| `buttons` | `text`, `btnType`, `icon`, `clickCode` | 按钮（不存储数据） |
| `tabs` | `tabLabels`(数组), `tabType`, `position` | 标签页容器（见下方 tabs 说明） |
| `link-record` | `sourceCode`, `titleField`, `showFields`, `showMode`, `showType` | 关联记录 |
| `link-field` | `linkRecordKey`, `showField`, `fieldType`, `fieldOptions` | 他表字段 |
| `summary` | `linkTable`, `field`, `summaryType`, `filter` | 汇总（summaryType: inner-sum/inner-average/inner-max/inner-min/inner-record-count/inner-completed-count/inner-incompletely-count/inner-date-earliest/inner-date-latest） |
| `sub-table-design` | `fields`(必填，子控件数组) | 设计子表（见下方子表说明） |

---

## 重要注意事项（AI 生成必读）

### 1. capital-money 关联金额控件

`capital-money`（大写金额）可关联 `money`、`formula`、`summary` 三种类型的控件。关联优先级：

1. **`moneyField`（推荐）**：传入目标字段的中文名，脚本自动解析为对应控件的 key。适用于大写金额与目标字段不相邻的场景。
2. **`moneyWidgetKey`**：直接传入控件 key（适用于已知 key 的场景）。
3. **自动查找（兜底）**：如果两者都未指定，脚本向前查找最近的 `money`/`formula`/`summary` 控件。

```json
{"name": "预算总额", "type": "money", "required": true, "unit": "万元"},
{"name": "总金额", "type": "formula", "mode": "CUSTOM",
 "expression": "$预算总额$*1.13", "decimal": 2, "unit": "元"},
{"name": "其他字段", "type": "input"},
{"name": "大写金额", "type": "capital-money", "moneyField": "总金额"}
```

### 2. formula 表达式使用字段中文名引用（自动解析）

公式控件的 `expression`、`dateBegin`、`dateEnd` 等表达式中的 `$model$` 引用必须是实际控件的 model。但 JSON 配置中无法预知 model（因为包含时间戳），因此 **`desform_creator.py` 支持使用字段中文名作为占位符，自动解析为实际 model**。

```json
{"name": "预算总额", "type": "money"},
{"name": "已拨付金额", "type": "money"},
{"name": "剩余预算", "type": "formula", "mode": "CUSTOM",
 "expression": "$预算总额$-$已拨付金额$", "decimal": 2}
```

脚本会将 `$预算总额$` 自动替换为 `$money_1774607470511_377187$` 等实际 model。

**日期公式同理：**
```json
{"name": "计划开始日期", "type": "date"},
{"name": "计划结束日期", "type": "date"},
{"name": "项目工期", "type": "formula", "mode": "DATEIF",
 "dateBegin": "$计划开始日期$", "dateEnd": "$计划结束日期$",
 "dateFormatMethod": 2, "datePrintUnit": "d"}
```

> **注意：** 引用的字段必须在 fields 数组中定义且在 formula 之前出现。如果字段名未找到匹配，占位符将保持原样不替换。

### 3. Word 布局下分隔符自动适配

在 Word 风格布局（`layout: "word"`）下，`divider` 分隔符会自动包裹在一个 `span=24`、`isWordStyle=true` 的 grid 容器中，以确保与 Word 风格的表格边框视觉一致。无需手动配置，JSON 中按普通分隔符写法即可：

```json
{"name": "---", "type": "divider", "text": "分区标题"}
```

---

## tabs（标签页容器）

```json
{
  "type": "tabs",
  "name": "Tabs",
  "tabLabels": ["基本信息", "详细信息", "附件"],
  "tabType": "border-card",
  "position": "top"
}
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `tabLabels` | 标签页名称数组 | `["Tab1", "Tab2"]` |
| `tabType` | 标签样式：`border-card` / `card` / `''` | `border-card` |
| `position` | 标签位置：`top` / `bottom` / `left` / `right` | `top` |

> 注意：tabs 内的子控件需要在创建后通过 Python 脚本手动添加到 `panes[i]['list']` 中，JSON 配置暂不支持嵌套子控件定义。

---

## 子表 `sub-table-design` 说明

子表通过嵌套 `fields` 数组定义子控件，无需手动处理 `parent_key`，脚本自动完成。

### 子表配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `columnNumber` | 1/2/3/4 | 2 | 布局列数（单列/双列/三列/四列） |
| `operationMode` | 1/2 | 1 | 操作方式：1=行内编辑，2=弹出编辑 |
| `isWordStyle` | bool | false | Word 文档风格（黑色边框表格样式，仅预览和使用时生效） |
| `isWordInnerGrid` | bool | false | 内嵌栅格模式（配合 isWordStyle 解决内部边框显示问题） |
| `defaultRows` | int | 0 | 默认预填行数（0=不预填） |

### columnNumber 与 columns 数组的对应关系（重要）

`columnNumber` 控制子表设计区域的布局列数，JSON 中的 `columns` 数组长度**必须**与 `columnNumber` 一致，
每列的 `span = 24 / columnNumber`。如果不匹配（如 `columnNumber=2` 但 `columns` 只有 1 个元素），
设计器会显示异常（空白列或控件挤压）。

| columnNumber | columns 数组 | 每列 span |
|---|---|---|
| 1 | `[{span:24, list:[...]}]` | 24 |
| 2 | `[{span:12, list:[...]}, {span:12, list:[...]}]` | 12 |
| 3 | `[{span:8, list:[...]}, {span:8, list:[...]}, {span:8, list:[...]}]` | 8 |
| 4 | `[{span:6, list:[...]}, ...(共4个)]` | 6 |

`make_sub_table()` 和 `desform_creator.py` 已自动处理：根据 `columnNumber` 生成对应数量的列，并将子控件**顺序填充**到各列（先填满第1列，再填第2列……），确保表格视图的列顺序与字段定义顺序一致。当字段较多时，可将 `columnNumber` 设为 3 或 4 以获得更紧凑的设计视图布局。

### 子表内支持的 type

> **注意：** 子表内只支持以下 type，不要凭空捏造不存在的类型。数字用 `number`，整数用 `integer`，多行文本用 `textarea`。

**基础类型：**

| type | 可选参数 | 说明 |
|------|---------|------|
| `input` | `required`, `col_width` | 单行文本 |
| `textarea` | `required`, `col_width` | 多行文本 |
| `integer` | `required`, `col_width`, `unit` | 整数 |
| `number` | `required`, `col_width`, `unit` | 数字 |
| `money` | `required`, `col_width`, `unit` | 金额 |
| `date` | `required`, `col_width` | 日期 |
| `time` | `required`, `col_width` | 时间 |

**选择类型：**

| type | 可选参数 | 说明 |
|------|---------|------|
| `select` | `options`(必填), `required`, `col_width`, `dictCode` | 下拉选择 |
| `radio` | `options`(必填), `required`, `col_width`, `dictCode` | 单选 |
| `checkbox` | `options`(必填), `required`, `col_width`, `dictCode` | 多选 |
| `table-dict` | `dictTable`, `dictCodeCol`, `dictTextCol`, `queryScope`, `required`, `col_width` | 表字典（options 内置 dictTable/dictCode/dictText/queryScope；queryScope=database 时仅支持 style=select） |
| `select-tree` | `categoryCode`, `required`, `col_width` | 下拉树 |

**系统类型：**

| type | 可选参数 | 说明 |
|------|---------|------|
| `select-user` | `required`, `col_width`, `multiple` | 选人 |
| `select-depart` | `required`, `col_width`, `multiple` | 选部门 |
| `select-depart-post` | `required`, `col_width` | 选岗位 |
| `phone` | `required`, `col_width` | 手机 |
| `email` | `required`, `col_width` | 邮箱 |
| `area-linkage` | `required`, `col_width` | 省市级联 |

**开关/滑块/评分：**

| type | 可选参数 | 说明 |
|------|---------|------|
| `switch` | `col_width`, `active`, `inactive` | 开关（默认 Y/N） |
| `slider` | `col_width` | 滑块 |
| `rate` | `col_width` | 评分 |
| `color` | `col_width` | 颜色 |

**文件类型：**

| type | 可选参数 | 说明 |
|------|---------|------|
| `imgupload` | `required`, `col_width` | 图片上传（子表内缩略图自动缩小为 50x50） |
| `file-upload` | `required`, `col_width` | 文件上传 |

**关联/公式：**

| type | 可选参数 | 说明 |
|------|---------|------|
| `link-record` | `sourceCode`, `titleField`, `showFields`, `showMode` | 关联记录（子表内强制为下拉模式） |
| `link-field` | `linkRecordKey`, `showField`, `fieldType`, `fieldOptions` | 他表字段（子表内强制为保存模式） |
| `formula` | `mode`, `expression`, `col_width`, `unit` | 公式 |
| `product` | `field_models`(必填), `col_width`, `unit` | 乘积公式 |

### 子表内特殊约束（源码强制行为）

- `imgupload` 在子表内缩略图自动缩小为 50x50（主表默认 100x100）
- `link-record` 在子表内强制为下拉模式（`showType = 'select'`），不支持卡片/表格模式
- `link-field` 在子表内强制为保存模式（`saveType = 'save'`），不支持 view 模式
- 所有子表内控件自动设置 `isSubItem: true` 和 `subOptions.parentKey`
- 子表内控件不使用 `autoWidth`，使用 `col_width` 控制列宽（默认 200px）

---

## 完整示例

### 主表示例（工程竣工验收申请表）

```json
{
  "formName": "工程竣工验收申请表",
  "formCode": "eng_completion_acceptance",
  "layout": "word",
  "fields": [
    {"name": "自动编号", "type": "auto-number", "prefix": "GCYS"},
    {"name": "条码", "type": "barcode"},
    {"name": "工程名称", "type": "input", "required": true},
    {"name": "工程编号", "type": "input"},
    {"name": "工程类别", "type": "radio", "options": ["土建工程", "安装工程", "装饰工程", "市政工程"]},
    {"name": "建设单位", "type": "input"},
    {"name": "工程地址", "type": "input"},
    {"name": "施工单位", "type": "input"},
    {"name": "开工时间", "type": "date"},
    {"name": "完工时间", "type": "date"},
    {"name": "工程量清单", "type": "textarea"},
    {"name": "图片上传", "type": "imgupload"},
    {"name": "定位", "type": "location"},
    {"name": "验收类别", "type": "radio", "options": ["竣工验收", "分部验收", "专项验收"]},
    {"name": "施工单位项目经理签字", "type": "hand-sign"},
    {"name": "---", "type": "divider", "text": "广电工程完工验收报告"},
    {"name": "工程名称(报告)", "type": "input"},
    {"name": "工程编号(报告)", "type": "input"},
    {"name": "建设单位(报告)", "type": "input"},
    {"name": "施工单位(报告)", "type": "input"},
    {"name": "开工时间(报告)", "type": "date"},
    {"name": "完工时间(报告)", "type": "date"},
    {"name": "验收时间", "type": "time"},
    {"name": "验收类别(报告)", "type": "radio", "options": ["竣工验收", "分部验收", "专项验收"]},
    {"name": "---", "type": "divider", "text": "竣工项目分项审查情况"},
    {"name": "立项手续完整性", "type": "radio", "options": ["合格", "不合格", "整改后合格"]},
    {"name": "项目主体组签字(立项)", "type": "hand-sign"},
    {"name": "竣工资料完整性", "type": "radio", "options": ["合格", "不合格", "整改后合格"]},
    {"name": "项目主体组签字(资料)", "type": "hand-sign"},
    {"name": "施工工艺合规性", "type": "radio", "options": ["合格", "不合格", "整改后合格"]},
    {"name": "项目主体组签字(工艺)", "type": "hand-sign"},
    {"name": "技术指标达标情况", "type": "radio", "options": ["合格", "不合格", "整改后合格"]},
    {"name": "项目主体组签字(技术)", "type": "hand-sign"},
    {"name": "材料设备核定结果", "type": "radio", "options": ["合格", "不合格", "整改后合格"]},
    {"name": "项目主体组签字(材料)", "type": "hand-sign"},
    {"name": "工程量核量结果", "type": "radio", "options": ["合格", "不合格", "整改后合格"]},
    {"name": "项目主体组签字(核量)", "type": "hand-sign"},
    {"name": "验收问题清单", "type": "textarea"},
    {"name": "验收结论", "type": "radio", "options": ["合格", "不合格", "整改后复验"]},
    {"name": "技术部负责人签字", "type": "hand-sign"},
    {"name": "施工单位签字", "type": "hand-sign"},
    {"name": "分管领导组签字", "type": "hand-sign"}
  ],
  "menuParent": "工程验收管理"
}
```

### 子表示例（采购订单）

```json
{
  "formName": "采购订单",
  "formCode": "purchase_order",
  "titleIndex": 0,
  "fields": [
    {"name": "订单编号", "type": "auto-number", "prefix": "PO"},
    {"name": "供应商", "type": "input", "required": true},
    {"name": "采购员", "type": "select-user", "required": true},
    {"name": "订单日期", "type": "date", "required": true},
    {"name": "商品明细", "type": "sub-table-design",
     "columnNumber": 2, "operationMode": 1, "fields": [
      {"name": "商品名称", "type": "input", "required": true},
      {"name": "规格", "type": "input"},
      {"name": "类别", "type": "radio", "options": ["原材料", "半成品", "成品"]},
      {"name": "数量", "type": "integer", "col_width": "100px"},
      {"name": "单价", "type": "money", "col_width": "120px"},
      {"name": "金额", "type": "money", "col_width": "120px"},
      {"name": "是否含税", "type": "switch"},
      {"name": "交货日期", "type": "date"},
      {"name": "备注", "type": "textarea", "col_width": "250px"}
    ]},
    {"name": "备注", "type": "textarea"}
  ]
}
```

### 弹出编辑 + Word 风格子表示例

```json
{"name": "检验明细", "type": "sub-table-design",
 "operationMode": 2, "isWordStyle": true, "fields": [
  {"name": "检验项目", "type": "input", "required": true},
  {"name": "检验人", "type": "select-user"},
  {"name": "检验结果", "type": "radio", "options": ["合格", "不合格", "待检"]},
  {"name": "检验日期", "type": "date"},
  {"name": "照片", "type": "imgupload"},
  {"name": "附件", "type": "file-upload"}
]}
```

---

## JS/CSS 增强配置（expand）

通过 `expand` 字段可在 JSON 配置中直接设置 JS/CSS 增强，无需编写自定义 Python 脚本。

```json
{
  "formName": "请假申请",
  "formCode": "oa_leave",
  "fields": [...],
  "expand": {
    "js": "if (data.isAddAction) { api.hide('approve_status') }",
    "css": ".el-form-item__label { font-weight: bold; color: #333; }",
    "url": {
      "js": "",
      "css": "/desform/expand/css/custom-theme.css"
    }
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `expand.js` | string | 内联 JS 增强代码（可用 api/data/moment 等上下文） |
| `expand.css` | string | 内联 CSS 增强代码 |
| `expand.url.js` | string | 外部 JS 文件 URL |
| `expand.url.css` | string | 外部 CSS 文件 URL |

- `expand` 中的四个字段均为可选，只需填写需要的部分
- JS/CSS 增强的详细用法见 `desform-js-enhance.md` 和 `desform-css-enhance.md`

---

## 调用示例

> ⛔ **方式选择（必须遵守）：字段数 ≤50 → stdin 管道；字段数 >50 → 临时文件。禁止在字段数 ≤50 时使用临时文件。**

```bash
# ✅ 默认方式（字段数 ≤50）：stdin 管道，无需临时文件
echo '<json_config>' | python "<skill目录>/scripts/desform_creator.py" \
    --api-base <api_base> \
    --token <token> \
    --config -

# 如需覆盖已存在的表单（加 --force）
echo '<json_config>' | python "<skill目录>/scripts/desform_creator.py" \
    --api-base <api_base> \
    --token <token> \
    --config - --force
```

```bash
# ⚠️ 仅当字段数 >50 时才使用临时文件方式
# 1. Write 工具生成 JSON 配置文件
# 2. 执行脚本
python "<skill目录>/scripts/desform_creator.py" \
    --api-base <api_base> \
    --token <token> \
    --config eng_acceptance.json

# 如需覆盖已存在的表单
python "<skill目录>/scripts/desform_creator.py" \
    --api-base <api_base> \
    --token <token> \
    --config eng_acceptance.json \
    --force

# 3. 删除临时 JSON 文件
```
