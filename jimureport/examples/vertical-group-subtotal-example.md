# 纵向分组小计报表示例

## 场景说明

员工信息登记表，按**部门**分组（一级），按**学历**分组（二级），自动合并相同分组的单元格，并在分组末尾显示小计/合计行。

## 分组效果预览

```
┌──────┬──────┬──────┬──────┬──────┬──────┐
│ 部门 │ 学历 │ 性别 │ 年龄 │ 姓名 │ 薪水 │
├──────┼──────┼──────┼──────┼──────┼──────┤
│      │      │  男  │  28  │ 张三 │ 8000 │
│      │ 本科 ├──────┼──────┼──────┼──────┤
│      │      │  女  │  25  │ 李四 │ 7500 │
│ 研发 │      ├──────┼──────┼──────┼──────┤
│  部  │      │      小计          │15500 │
│      ├──────┼──────┼──────┼──────┼──────┤
│      │ 硕士 │  男  │  30  │ 王五 │ 12000│
│      │      ├──────┼──────┼──────┼──────┤
│      │      │      小计          │12000 │
├──────┼──────┼──────┼──────┼──────┼──────┤
│      │      合计                  │27500 │
├──────┼──────┼──────┼──────┼──────┼──────┤
│ ...  │ ...  │ ...  │ ...  │ ...  │ ...  │
└──────┴──────┴──────┴──────┴──────┴──────┘
```

## 核心配置

### 1. 分组字段声明

jsonStr 顶层需要两个属性：

```json
{
    "isGroup": true,
    "groupField": "vegvkdueqw.department"
}
```

| 属性 | 说明 |
|------|------|
| `isGroup` | `true` 启用分组模式 |
| `groupField` | 主分组字段，格式 `数据集编码.字段名` |

### 2. 数据行分组绑定

```json
"3": {
    "cells": {
        "1": {
            "style": 17,
            "text": "#{vegvkdueqw.group(department)}",
            "aggregate": "group",
            "subtotal": "groupField",
            "funcname": "-1",
            "subtotalText": "合计"
        },
        "2": {
            "style": 17,
            "text": "#{vegvkdueqw.group(education)}",
            "aggregate": "group",
            "subtotal": "groupField",
            "funcname": "-1",
            "subtotalText": "小计"
        },
        "3": { "style": 17, "text": "#{vegvkdueqw.sex}" },
        "4": { "style": 17, "text": "#{vegvkdueqw.age}" },
        "5": { "style": 17, "text": "#{vegvkdueqw.name}" },
        "6": { "style": 17, "text": "#{vegvkdueqw.salary}" }
    },
    "height": 54
}
```

### 3. 分组单元格属性详解

| 属性 | 值 | 说明 |
|------|-----|------|
| `text` | `#{dbCode.group(fieldName)}` | 分组绑定语法，自动合并相同值的单元格 |
| `aggregate` | `"group"` | 标记为分组聚合列 |
| `subtotal` | `"groupField"` | 启用小计行 |
| `funcname` | `"-1"` | 小计函数，见下表 |
| `subtotalText` | `"合计"` / `"小计"` | 小计行显示的文本 |

### funcname 聚合函数对照表（分组列与聚合列通用）

| 用户需求 | funcname 值 | 说明 |
|---------|------------|------|
| 不计算，仅显示文本 | `"-1"` | 分组列固定用此值 |
| 合计 / 求和 | `"SUM"` | |
| 平均 / 平均值 | `"AVERAGE"` | ⚠️ 不是 `"AVG"` |
| 最大值 | `"MAX"` | |
| 最小值 | `"MIN"` | |
| 计数 | `"COUNT"` | |

### 聚合列（非分组列）完整格式

```json
{
    "text": "#{dbCode.fieldName}",
    "style": 3,
    "aggregate": "select",
    "subtotal": "-1",
    "funcname": "AVERAGE",
    "subtotalText": "班级平均分",
    "sort": "asc"
}
```

> ⚠️ 聚合列用 `aggregate:"select"` + `subtotal:"-1"`，**分组列**才用 `aggregate:"group"` + `subtotal:"groupField"`，不可混用。

### 4. 分组绑定语法

| 语法 | 说明 |
|------|------|
| `#{dbCode.group(field)}` | 分组字段，相同值自动合并单元格 |
| `#{dbCode.field}` | 普通字段，每行独立显示 |

### 5. 多级分组

- **一级分组**（部门）：subtotalText = `"合计"` — 部门切换时显示合计行
- **二级分组**（学历）：subtotalText = `"小计"` — 学历切换时显示小计行
- 分组列从左到右排列，左边为高级别分组

## 完整 jsonStr

```json
{
    "loopBlockList": [],
    "querySetting": {
        "izOpenQueryBar": false,
        "izDefaultQuery": true
    },
    "recordSubTableOrCollection": { "group": [], "record": [], "range": [] },
    "printConfig": {
        "paper": "A4",
        "width": 210,
        "height": 297,
        "definition": 4,
        "isBackend": false,
        "marginX": 10,
        "marginY": 10,
        "layout": "portrait",
        "printCallBackUrl": "",
        "paginationShow": false,
        "paginationLocation": "middle",
        "paginationStart": 1,
        "headerFooterShow": false,
        "headerLocation": "left",
        "headerText": "",
        "footerLocation": "left",
        "footerText": "",
        "fontsize": 28,
        "rotationAngle": -45,
        "watermarkColor": "#246DDE",
        "watermarkText": "积木报表",
        "watermarkShow": true,
        "printFootorFixBottom": false
    },
    "hidden": { "rows": [], "cols": [], "conditions": { "rows": {}, "cols": {} } },
    "queryFormSetting": { "useQueryForm": false, "dbKey": "", "idField": "" },
    "dbexps": [],
    "dicts": [],
    "fillFormToolbar": {
        "show": true,
        "btnList": ["save", "subTable_add", "verify", "subTable_del", "print", "close", "first", "prev", "next", "paging", "total", "last", "exportPDF", "exportExcel", "exportWord"]
    },
    "freeze": "A1",
    "dataRectWidth": 687,
    "isViewContentHorizontalCenter": false,
    "autofilter": {},
    "validations": [],
    "cols": {
        "0": { "width": 34 },
        "1": { "width": 119 },
        "3": { "width": 117 },
        "6": { "width": 117 },
        "7": { "width": 22 },
        "len": 100
    },
    "area": { "sri": 16, "sci": 4, "eri": 16, "eci": 4, "width": 100, "height": 25 },
    "pyGroupEngine": false,
    "submitHandlers": [],
    "excel_config_id": "1162913845578612736",
    "hiddenCells": [],
    "zonedEditionList": [],
    "rows": {
        "1": {
            "cells": {
                "1": {
                    "merge": [0, 5],
                    "style": 2,
                    "text": "纵向员工信息登记表",
                    "height": 0
                }
            },
            "height": 40
        },
        "2": {
            "cells": {
                "1": { "style": 15, "text": "部门" },
                "2": { "style": 15, "text": "学历" },
                "3": { "style": 15, "text": "性别" },
                "4": { "style": 15, "text": "年龄" },
                "5": { "style": 15, "text": "姓名" },
                "6": { "style": 15, "text": "薪水" }
            },
            "height": 34
        },
        "3": {
            "cells": {
                "1": {
                    "style": 17,
                    "text": "#{vegvkdueqw.group(department)}",
                    "aggregate": "group",
                    "subtotal": "groupField",
                    "funcname": "-1",
                    "subtotalText": "合计"
                },
                "2": {
                    "style": 17,
                    "text": "#{vegvkdueqw.group(education)}",
                    "aggregate": "group",
                    "subtotal": "groupField",
                    "funcname": "-1",
                    "subtotalText": "小计"
                },
                "3": { "style": 17, "text": "#{vegvkdueqw.sex}" },
                "4": { "style": 17, "text": "#{vegvkdueqw.age}" },
                "5": { "style": 17, "text": "#{vegvkdueqw.name}" },
                "6": { "style": 17, "text": "#{vegvkdueqw.salary}" }
            },
            "height": 54
        },
        "len": 100
    },
    "rpbar": { "show": true, "pageSize": "", "btnList": [] },
    "groupField": "vegvkdueqw.department",
    "fixedPrintHeadRows": [],
    "fixedPrintTailRows": [],
    "displayConfig": {},
    "fillFormInfo": { "layout": { "direction": "horizontal", "width": 200, "height": 45 } },
    "background": false,
    "name": "sheet1",
    "styles": [
        { "font": { "bold": true } },
        { "font": { "size": 16, "bold": true } },
        { "align": "center", "font": { "size": 16, "bold": true } },
        { "align": "center" },
        { "bgcolor": "#5b9cd6", "align": "center" },
        { "bgcolor": "#5b9cd6", "color": "#ffffff", "align": "center" },
        { "border": { "top": ["thin", "#000"], "left": ["thin", "#000"], "bottom": ["thin", "#000"], "right": ["thin", "#000"] }, "bgcolor": "#5b9cd6", "color": "#ffffff", "align": "center" },
        { "border": { "top": ["thin", "#000"], "left": ["thin", "#000"], "bottom": ["thin", "#000"], "right": ["thin", "#000"] } },
        { "border": { "top": ["thin", "#bfbfbf"], "left": ["thin", "#bfbfbf"], "bottom": ["thin", "#bfbfbf"], "right": ["thin", "#bfbfbf"] }, "bgcolor": "#5b9cd6", "color": "#ffffff", "align": "center" },
        { "border": { "top": ["thin", "#bfbfbf"], "left": ["thin", "#bfbfbf"], "bottom": ["thin", "#bfbfbf"], "right": ["thin", "#bfbfbf"] } },
        { "border": { "top": ["thin", "#9cc2e6"], "left": ["thin", "#9cc2e6"], "bottom": ["thin", "#9cc2e6"], "right": ["thin", "#9cc2e6"] }, "bgcolor": "#5b9cd6", "color": "#ffffff", "align": "center" },
        { "border": { "top": ["thin", "#9cc2e6"], "left": ["thin", "#9cc2e6"], "bottom": ["thin", "#9cc2e6"], "right": ["thin", "#9cc2e6"] } },
        { "border": { "top": ["thin", "#9cc2e6"], "left": ["thin", "#9cc2e6"], "bottom": ["thin", "#9cc2e6"], "right": ["thin", "#9cc2e6"] }, "bgcolor": "#bdd7ee", "color": "#ffffff", "align": "center" },
        { "border": { "top": ["thin", "#9cc2e6"], "left": ["thin", "#9cc2e6"], "bottom": ["thin", "#9cc2e6"], "right": ["thin", "#9cc2e6"] }, "bgcolor": "#bdd7ee", "color": "#000100", "align": "center" },
        { "border": { "top": ["thin", "#9cc2e6"], "left": ["thin", "#9cc2e6"], "bottom": ["thin", "#9cc2e6"], "right": ["thin", "#9cc2e6"] }, "bgcolor": "#9cc2e6", "color": "#000100", "align": "center" },
        { "border": { "top": ["thin", "#5b9cd6"], "left": ["thin", "#5b9cd6"], "bottom": ["thin", "#5b9cd6"], "right": ["thin", "#5b9cd6"] }, "bgcolor": "#9cc2e6", "color": "#000100", "align": "center" },
        { "border": { "top": ["thin", "#5b9cd6"], "left": ["thin", "#5b9cd6"], "bottom": ["thin", "#5b9cd6"], "right": ["thin", "#5b9cd6"] } },
        { "border": { "top": ["thin", "#5b9cd6"], "left": ["thin", "#5b9cd6"], "bottom": ["thin", "#5b9cd6"], "right": ["thin", "#5b9cd6"] }, "align": "center" }
    ],
    "isGroup": true,
    "freezeLineColor": "rgb(185, 185, 185)",
    "merges": ["B2:G2"]
}
```

## 样式方案（蓝色主题）

| 索引 | 背景色 | 字体色 | 边框色 | 用途 |
|------|--------|--------|--------|------|
| 2 | — | — | — | 标题（16号加粗居中） |
| 15 | #9cc2e6 | #000100 | #5b9cd6 | **表头行**（中蓝底） |
| 17 | — | — | #5b9cd6 | **数据行**（蓝色边框居中） |

三层蓝色渐变：
- 深蓝 `#5b9cd6` — 表头背景/边框色
- 中蓝 `#9cc2e6` — 表头行背景
- 浅蓝 `#bdd7ee` — 交替行/小计行背景

## 打印配置（含水印）

```json
"printConfig": {
    "paper": "A4",
    "definition": 4,
    "watermarkShow": true,
    "watermarkText": "积木报表",
    "watermarkColor": "#246DDE",
    "fontsize": 28,
    "rotationAngle": -45,
    "paginationShow": false,
    "headerFooterShow": false,
    "printFootorFixBottom": false
}
```

| 属性 | 说明 |
|------|------|
| `definition` | 打印清晰度（1-4，4最高） |
| `watermarkShow` | 启用水印 |
| `watermarkText` | 水印文字 |
| `watermarkColor` | 水印颜色 |
| `fontsize` | 水印字号 |
| `rotationAngle` | 水印旋转角度（负数=逆时针） |
| `paginationShow` | 是否显示页码 |
| `paginationLocation` | 页码位置：left/middle/right |
| `headerFooterShow` | 是否显示页眉页脚 |
| `printFootorFixBottom` | 页脚是否固定在底部 |
