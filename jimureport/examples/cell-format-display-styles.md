# 单元格格式、类型与样式综合示例

> **此文件已拆分为3个较小文件（建议直接读取拆分后的文件）：**
> - `cell-format-concepts.md` — 数据集配置 + format/display/styles 核心概念
> - `cell-format-rows.md` — 完整 rows/merges/cols 配置
> - `cell-format-script.md` — 完整创建脚本（可直接运行）

> 报表名：员工数据格式展示报表（ID: 1775125218946541259）
> 用途：展示积木报表中所有常用的 `format`（数值/日期格式化）、`display`（单元格类型）、以及单元格样式（font/align/bgcolor/color）配置方式。
> 数据集：JSON数据集（dbType="3"），无查询条件，不分组不合计。

---

## 报表结构总览

```
行0: 大标题（合并B~K列，10列）
行1: 一、数值与货币格式（合并B~K列）
行2: 表头行（姓名 | 正常数值 | 数值(千分位) | 百分比 | 人民币 | 美元 | 欧元）
行3: 数据绑定行（#{emp.name} | #{emp.salary}×3种format | ...）
行4: 空行（间距15px）
行5: 二、日期时间格式（合并B~K列）
行6: 表头行（姓名 | 短日期 | 长日期 | 年 | 月 | 年月 | 时间 | 日期+时间）
行7: 数据绑定行
行8: 空行（间距15px）
行9: 三、单元格类型（合并B~K列）
行10: 表头行（姓名 | 文本 | 数值 | 图片 | 条形码 | 二维码 | 富文本(合并4列)）
行11: 数据绑定行（height:80，富文本合并4列）
行12: 空行（间距15px）
行13: 四、单元格样式展示（合并B~K列）
行14: 表头行（样式名称 | 左对齐 | 居中 | 右对齐 | 加粗14 | 斜体 | 红色 | 下划线 | 删除线）
行15: 效果展示行（静态文本展示各种样式）
行16: 背景色展示行（成功/通过 | 警告/待处理 | 失败/拒绝）
```

---

## 数据集配置

### JSON数据集（dbType="3"）

- 编码：`emp`
- 中文名：员工数据
- `isList`: "1"，`isPage`: "0"（不分页，展示全量数据）
- `jsonData` 必须用 `{"data": [...]}` 格式包裹

```python
json_data = {
    "data": [
        {
            "name": "张三", "code": "EMP001", "dept": "技术部",
            "hire_date": "2020-03-15", "create_time": "2020-03-15 09:30:00",
            "salary": 15000.5, "bonus": 3800, "factor": 1.25, "rate": 0.95,
            "price_usd": 2100.0, "price_eur": 1900.0,
            "avatar": "https://cdn.pixabay.com/photo/2016/08/08/09/17/avatar-1577909_1280.png",
            "barcode_val": "6901234567890",
            "qrcode_val": "https://www.jeecg.com",
            "remark": "<b>年度优秀</b>员工，<font color='red'>连续三年</font>绩效A+"
        },
        {
            "name": "李四", "code": "EMP002", "dept": "市场部",
            "hire_date": "2019-07-20", "create_time": "2019-07-20 14:00:00",
            "salary": 12000.0, "bonus": 2500, "factor": 1.1, "rate": 0.88,
            "price_usd": 1680.0, "price_eur": 1520.0,
            "avatar": "https://cdn.pixabay.com/photo/2016/08/08/09/17/avatar-1577909_1280.png",
            "barcode_val": "6901234567891",
            "qrcode_val": "https://www.baidu.com",
            "remark": "<b>季度销售冠军</b>，<font color='blue'>超额完成</font>目标120%"
        },
        {
            "name": "王五", "code": "EMP003", "dept": "财务部",
            "hire_date": "2021-01-08", "create_time": "2021-01-08 10:15:00",
            "salary": 13500.75, "bonus": 1800, "factor": 0.95, "rate": 0.76,
            "price_usd": 1890.0, "price_eur": 1710.0,
            "avatar": "https://cdn.pixabay.com/photo/2016/08/08/09/17/avatar-1577909_1280.png",
            "barcode_val": "6901234567892",
            "qrcode_val": "https://www.github.com",
            "remark": "考核待提升，<i>需加强业务学习</i>"
        },
        {
            "name": "赵六", "code": "EMP004", "dept": "技术部",
            "hire_date": "2018-11-25", "create_time": "2018-11-25 08:45:00",
            "salary": 18000.0, "bonus": 5200, "factor": 1.35, "rate": 0.92,
            "price_usd": 2520.0, "price_eur": 2280.0,
            "avatar": "https://cdn.pixabay.com/photo/2016/08/08/09/17/avatar-1577909_1280.png",
            "barcode_val": "6901234567893",
            "qrcode_val": "https://www.zhihu.com",
            "remark": "<b>技术骨干</b>，带队完成<font color='green'>多个核心项目</font>"
        },
        {
            "name": "孙七", "code": "EMP005", "dept": "人事部",
            "hire_date": "2022-06-10", "create_time": "2022-06-10 11:30:00",
            "salary": 11000.0, "bonus": 2000, "factor": 1.0, "rate": 0.83,
            "price_usd": 1540.0, "price_eur": 1395.0,
            "avatar": "https://cdn.pixabay.com/photo/2016/08/08/09/17/avatar-1577909_1280.png",
            "barcode_val": "6901234567894",
            "qrcode_val": "https://www.bilibili.com",
            "remark": "新入职培训中，<u>表现良好</u>"
        }
    ]
}

db_data = {
    "izSharedSource": 0,
    "jimuReportId": report_id,
    "dbCode": "emp",
    "dbChName": "员工数据",
    "dbType": "3",
    "dbSource": "",
    "jsonData": json.dumps(json_data, ensure_ascii=False),
    "apiConvert": "",
    "isList": "1",
    "isPage": "0",
    "dbDynSql": "",
    "fieldList": [
        {"fieldName": "name",        "fieldText": "姓名",    "widgetType": "String", "orderNum": 1},
        {"fieldName": "code",        "fieldText": "工号",    "widgetType": "String", "orderNum": 2},
        {"fieldName": "dept",        "fieldText": "部门",    "widgetType": "String", "orderNum": 3},
        {"fieldName": "hire_date",   "fieldText": "入职日期", "widgetType": "String", "orderNum": 4},
        {"fieldName": "create_time", "fieldText": "创建时间", "widgetType": "String", "orderNum": 5},
        {"fieldName": "salary",      "fieldText": "基本工资", "widgetType": "Number", "orderNum": 6},
        {"fieldName": "bonus",       "fieldText": "奖金",    "widgetType": "Number", "orderNum": 7},
        {"fieldName": "factor",      "fieldText": "绩效系数", "widgetType": "Number", "orderNum": 8},
        {"fieldName": "rate",        "fieldText": "完成率",  "widgetType": "Number", "orderNum": 9},
        {"fieldName": "price_usd",   "fieldText": "美元价格", "widgetType": "Number", "orderNum": 10},
        {"fieldName": "price_eur",   "fieldText": "欧元价格", "widgetType": "Number", "orderNum": 11},
        {"fieldName": "avatar",      "fieldText": "头像",    "widgetType": "String", "orderNum": 12},
        {"fieldName": "barcode_val", "fieldText": "条形码值", "widgetType": "String", "orderNum": 13},
        {"fieldName": "qrcode_val",  "fieldText": "二维码值", "widgetType": "String", "orderNum": 14},
        {"fieldName": "remark",      "fieldText": "备注",    "widgetType": "String", "orderNum": 15}
    ],
    "paramList": []
}
```

> **注意：** JSON数据集不需要调用 `queryFieldBySql`，直接手动构建 `fieldList` 即可。

---

## 核心概念说明

### 1. `format` —— 数值/日期格式化（样式属性）

`format` 写在 `styles` 数组中的样式对象内，通过 cell 的 `style` 索引引用。

| format 值 | 效果 | 示例输出 |
|-----------|------|---------|
| `"normal"` | 原始值（默认） | `15000.5` |
| `"number"` | 千分位数值 | `15,000.50` |
| `"percent"` | 百分比 | `95.00%` |
| `"rmb"` | 人民币 | `￥15,000.50` |
| `"usd"` | 美元 | `$2,100.00` |
| `"eur"` | 欧元 | `€1,900.00` |
| `"date"` | 短日期 | `2020-03-15` |
| `"date2"` | 长日期 | `2020年03月15日` |
| `"year"` | 年 | `2020` |
| `"month"` | 月 | `3` |
| `"yearMonth"` | 年月 | `2020-03` |
| `"time"` | 时间 | `09:30:00` |
| `"datetime"` | 日期+时间 | `2020-03-15 09:30:00` |

**同一字段可通过不同 style 展示不同格式（复用字段绑定）：**
```python
# 行3：同一个 #{emp.salary} 字段，三种格式
"3": {"text": "#{emp.salary}", "style": 3, "display": "number"},  # 普通数值(居中)
"4": {"text": "#{emp.salary}", "style": 5, "display": "number"},  # 千分位number
"5": {"text": "#{emp.salary}", "style": 7, "display": "number"},  # 人民币rmb
```

> **重要：** format 为数值格式（number/percent/rmb/usd/eur）时，cell 上还需同时设置 `"display": "number"`。仅有日期格式时不需要额外 display。

### 2. `display` —— 单元格类型（cell属性）

`display` 是单元格（cell）的属性，不在 style 中，直接写在 cell 对象上。

| display 值 | 说明 | 字段值要求 |
|------------|------|----------|
| （不设置） | 普通文本 | 任意字符串 |
| `"number"` | 数值（配合format使用） | 数字 |
| `"img"` | 图片（自动渲染） | 图片URL或base64 |
| `"barcode"` | 条形码 | EAN/Code128等编码字符串 |
| `"qrcode"` | 二维码 | 任意字符串/URL |
| `"richText"` | 富文本（渲染HTML） | HTML字符串 |

```python
# display 配置示例
"4": {"text": "#{emp.avatar}",      "style": 3, "display": "img"},
"5": {"text": "#{emp.barcode_val}", "style": 3, "display": "barcode"},
"6": {"text": "#{emp.qrcode_val}",  "style": 3, "display": "qrcode"},
"7": {"text": "#{emp.remark}",      "style": 17, "display": "richText", "merge": [0, 3]}
```

> **富文本注意：** display:"richText" 的单元格通常需要更大的行高（如 `height: 80`），且文本内容为 HTML 字符串。

### 3. 样式（styles 数组）—— font/align/bgcolor/color

样式写在 styles 数组，通过索引引用。以下是本报表完整样式表：

```python
styles_list = [
    # 0: 大标题 —— 淡蓝底+深蓝字+18px加粗
    {"border": B, "align": "center", "valign": "middle",
     "font": {"bold": True, "size": 18}, "bgcolor": "#E6F2FF", "color": "#0066CC"},
    # 1: 分节标题（橙色）—— 浅黄底+橙色字+12px加粗
    {"border": B, "align": "center", "valign": "middle",
     "font": {"bold": True, "size": 12}, "bgcolor": "#FFF2CC", "color": "#E67E00"},
    # 2: 表头 —— 蓝底白字加粗
    {"border": B, "align": "center", "valign": "middle",
     "font": {"bold": True}, "bgcolor": "#01b0f1", "color": "#ffffff"},
    # 3: 普通数据 —— 居中
    {"border": B, "align": "center", "valign": "middle"},
    # 4: 姓名字段 —— 居中加粗
    {"border": B, "align": "center", "valign": "middle", "font": {"bold": True}},
    # 5: 数值格式(千分位) —— format:number
    {"border": B, "align": "center", "valign": "middle", "format": "number"},
    # 6: 百分比 —— format:percent
    {"border": B, "align": "center", "valign": "middle", "format": "percent"},
    # 7: 人民币 —— format:rmb, 右对齐
    {"border": B, "align": "right", "valign": "middle", "format": "rmb"},
    # 8: 美元 —— format:usd, 右对齐
    {"border": B, "align": "right", "valign": "middle", "format": "usd"},
    # 9: 欧元 —— format:eur, 右对齐
    {"border": B, "align": "right", "valign": "middle", "format": "eur"},
    # 10: 短日期 —— format:date (yyyy-MM-dd)
    {"border": B, "align": "center", "valign": "middle", "format": "date"},
    # 11: 长日期 —— format:date2 (yyyy年MM月dd日)
    {"border": B, "align": "center", "valign": "middle", "format": "date2"},
    # 12: 年 —— format:year
    {"border": B, "align": "center", "valign": "middle", "format": "year"},
    # 13: 月 —— format:month
    {"border": B, "align": "center", "valign": "middle", "format": "month"},
    # 14: 年月 —— format:yearMonth
    {"border": B, "align": "center", "valign": "middle", "format": "yearMonth"},
    # 15: 时间 —— format:time (HH:mm:ss)
    {"border": B, "align": "center", "valign": "middle", "format": "time"},
    # 16: 日期+时间 —— format:datetime
    {"border": B, "align": "center", "valign": "middle", "format": "datetime"},
    # 17: 左对齐（富文本/长文本）
    {"border": B, "align": "left", "valign": "middle"},
    # 18: 灰背景（效果展示行标签）
    {"border": B, "align": "center", "valign": "middle",
     "bgcolor": "#F2F2F2", "color": "#333333"},
    # 19: 分节标题（紫色）
    {"border": B, "align": "center", "valign": "middle",
     "font": {"bold": True, "size": 12}, "bgcolor": "#E8DAEF", "color": "#6A1B9A"},
    # 20: 分节标题（绿色）
    {"border": B, "align": "center", "valign": "middle",
     "font": {"bold": True, "size": 12}, "bgcolor": "#E2EFDA", "color": "#2E7D32"},
    # 21: 左对齐文本
    {"border": B, "align": "left", "valign": "middle"},
    # 22: 右对齐文本
    {"border": B, "align": "right", "valign": "middle"},
    # 23: 加粗14号
    {"border": B, "align": "center", "valign": "middle", "font": {"bold": True, "size": 14}},
    # 24: 斜体
    {"border": B, "align": "center", "valign": "middle", "font": {"italic": True}},
    # 25: 红色字体
    {"border": B, "align": "center", "valign": "middle", "color": "#FF0000"},
    # 26: 成功/通过（绿色背景）
    {"border": B, "align": "center", "valign": "middle",
     "bgcolor": "#C6EFCE", "color": "#006100"},
    # 27: 失败/拒绝（红色背景）
    {"border": B, "align": "center", "valign": "middle",
     "bgcolor": "#FFC7CE", "color": "#9C0006"},
    # 28: 警告/待处理（黄色背景）
    {"border": B, "align": "center", "valign": "middle",
     "bgcolor": "#FFEB9C", "color": "#9C6500"},
    # 29: 下划线
    {"border": B, "align": "center", "valign": "middle", "font": {"underline": True}},
    # 30: 删除线
    {"border": B, "align": "center", "valign": "middle", "font": {"strike": True}}
]
# B = {"bottom": ["thin", "#d8d8d8"], "top": ["thin", "#d8d8d8"],
#      "left": ["thin", "#d8d8d8"], "right": ["thin", "#d8d8d8"]}
```

**字体属性速查（font 对象的 key）：**

| key | 值 | 效果 |
|-----|----|------|
| `"bold"` | `True` | 加粗 |
| `"italic"` | `True` | 斜体 |
| `"underline"` | `True` | 下划线 |
| `"strike"` | `True` | 删除线 |
| `"size"` | 数字（如 14） | 字号（px） |

---

## 完整 rows 配置

```python
B = {"bottom": ["thin", "#d8d8d8"], "top": ["thin", "#d8d8d8"],
     "left": ["thin", "#d8d8d8"], "right": ["thin", "#d8d8d8"]}

rows_data = {
    # 行0: 大标题（合并B~K，10列=col1~col10）
    "0": {
        "cells": {"1": {"text": "员工数据格式展示报表", "style": 0, "merge": [0, 9]}},
        "height": 55
    },
    # 行1: 一、数值与货币格式（橙色分节标题）
    "1": {
        "cells": {"1": {"text": "一、数值与货币格式（format）", "style": 1, "merge": [0, 9]}},
        "height": 32
    },
    # 行2: 数值格式表头
    "2": {
        "cells": {
            "1": {"text": "姓名",         "style": 2},
            "2": {"text": "正常数值",      "style": 2},
            "3": {"text": "数值(千分位)",  "style": 2},
            "4": {"text": "百分比",        "style": 2},
            "5": {"text": "人民币(￥)",    "style": 2},
            "6": {"text": "美元($)",       "style": 2},
            "7": {"text": "欧元(€)",       "style": 2}
        },
        "height": 34
    },
    # 行3: 数值格式数据绑定（同字段不同format）
    "3": {
        "cells": {
            "1": {"text": "#{emp.name}",      "style": 4},
            "2": {"text": "#{emp.salary}",    "style": 3,  "display": "number"},  # 原始值
            "3": {"text": "#{emp.salary}",    "style": 5,  "display": "number"},  # 千分位
            "4": {"text": "#{emp.rate}",      "style": 6,  "display": "number"},  # 百分比
            "5": {"text": "#{emp.salary}",    "style": 7,  "display": "number"},  # 人民币
            "6": {"text": "#{emp.price_usd}", "style": 8,  "display": "number"},  # 美元
            "7": {"text": "#{emp.price_eur}", "style": 9,  "display": "number"}   # 欧元
        },
        "height": 30
    },
    # 行4: 间距空行
    "4": {"cells": {}, "height": 15},

    # 行5: 二、日期时间格式（紫色分节标题）
    "5": {
        "cells": {"1": {"text": "二、日期时间格式（format）", "style": 19, "merge": [0, 9]}},
        "height": 32
    },
    # 行6: 日期格式表头
    "6": {
        "cells": {
            "1": {"text": "姓名",     "style": 2},
            "2": {"text": "短日期",   "style": 2},
            "3": {"text": "长日期",   "style": 2},
            "4": {"text": "年",       "style": 2},
            "5": {"text": "月",       "style": 2},
            "6": {"text": "年月",     "style": 2},
            "7": {"text": "时间",     "style": 2},
            "8": {"text": "日期+时间","style": 2}
        },
        "height": 34
    },
    # 行7: 日期格式数据绑定（同字段不同日期format）
    "7": {
        "cells": {
            "1": {"text": "#{emp.name}",        "style": 4},
            "2": {"text": "#{emp.hire_date}",   "style": 10},  # date
            "3": {"text": "#{emp.hire_date}",   "style": 11},  # date2
            "4": {"text": "#{emp.hire_date}",   "style": 12},  # year
            "5": {"text": "#{emp.hire_date}",   "style": 13},  # month
            "6": {"text": "#{emp.hire_date}",   "style": 14},  # yearMonth
            "7": {"text": "#{emp.create_time}", "style": 15},  # time
            "8": {"text": "#{emp.create_time}", "style": 16}   # datetime
        },
        "height": 30
    },
    # 行8: 间距空行
    "8": {"cells": {}, "height": 15},

    # 行9: 三、单元格类型（绿色分节标题）
    "9": {
        "cells": {"1": {"text": "三、单元格类型（display / 类型）", "style": 20, "merge": [0, 9]}},
        "height": 32
    },
    # 行10: 单元格类型表头（富文本表头合并4列）
    "10": {
        "cells": {
            "1": {"text": "姓名",   "style": 2},
            "2": {"text": "文本",   "style": 2},
            "3": {"text": "数值",   "style": 2},
            "4": {"text": "图片",   "style": 2},
            "5": {"text": "条形码", "style": 2},
            "6": {"text": "二维码", "style": 2},
            "7": {"text": "富文本", "style": 2, "merge": [0, 3]}
        },
        "height": 34
    },
    # 行11: 单元格类型数据绑定（行高80以容纳图片/条码/富文本）
    "11": {
        "cells": {
            "1": {"text": "#{emp.name}",        "style": 4},
            "2": {"text": "#{emp.code}",         "style": 3},
            "3": {"text": "#{emp.salary}",       "style": 5,  "display": "number"},
            "4": {"text": "#{emp.avatar}",       "style": 3,  "display": "img"},
            "5": {"text": "#{emp.barcode_val}",  "style": 3,  "display": "barcode"},
            "6": {"text": "#{emp.qrcode_val}",   "style": 3,  "display": "qrcode"},
            "7": {"text": "#{emp.remark}",       "style": 17, "display": "richText", "merge": [0, 3]}
        },
        "height": 80
    },
    # 行12: 间距空行
    "12": {"cells": {}, "height": 15},

    # 行13: 四、单元格样式展示（橙色分节标题）
    "13": {
        "cells": {"1": {"text": "四、单元格样式展示（font / align / bgcolor）", "style": 1, "merge": [0, 9]}},
        "height": 32
    },
    # 行14: 样式展示表头
    "14": {
        "cells": {
            "1": {"text": "样式名称", "style": 2},
            "2": {"text": "左对齐",   "style": 2},
            "3": {"text": "居中对齐", "style": 2},
            "4": {"text": "右对齐",   "style": 2},
            "5": {"text": "加粗14号", "style": 2},
            "6": {"text": "斜体",     "style": 2},
            "7": {"text": "红色字体", "style": 2},
            "8": {"text": "下划线",   "style": 2},
            "9": {"text": "删除线",   "style": 2}
        },
        "height": 34
    },
    # 行15: 静态样式效果展示
    "15": {
        "cells": {
            "1": {"text": "效果展示",   "style": 18},
            "2": {"text": "左对齐文本", "style": 21},
            "3": {"text": "居中文本",   "style": 3},
            "4": {"text": "右对齐文本", "style": 22},
            "5": {"text": "加粗大字",   "style": 23},
            "6": {"text": "斜体文字",   "style": 24},
            "7": {"text": "红色警告",   "style": 25},
            "8": {"text": "下划线文本", "style": 29},
            "9": {"text": "已完成项目", "style": 30}
        },
        "height": 30
    },
    # 行16: 背景色状态展示
    "16": {
        "cells": {
            "1": {"text": "背景色",      "style": 2},
            "2": {"text": "成功/通过",   "style": 26, "merge": [0, 2]},
            "5": {"text": "警告/待处理", "style": 28, "merge": [0, 1]},
            "7": {"text": "失败/拒绝",   "style": 27, "merge": [0, 2]}
        },
        "height": 30
    },
    "len": 200
}
```

---

## merges 列表

```python
merges_list = [
    "B1:K1",   # 大标题（行0,UI第1行，B=col1, K=col10）
    "B2:K2",   # 分节标题（行1）
    "B6:K6",   # 分节标题（行5）
    "B10:K10", # 分节标题（行9）
    "H11:K11", # 富文本表头合并（行10, col7~col10）
    "H12:K12", # 富文本数据合并（行11, col7~col10）
    "B14:K14", # 分节标题（行13）
    "C17:E17", # 成功/通过合并（行16, col2~col4）
    "F17:G17", # 警告/待处理合并（行16, col5~col6）
    "H17:J17"  # 失败/拒绝合并（行16, col7~col9）
]
```

---

## cols 与打印配置

```python
cols_data = {
    "0": {"width": 25},   # A列 左边距
    "1": {"width": 80},   # 姓名
    "2": {"width": 100},
    "3": {"width": 100},
    "4": {"width": 130},
    "5": {"width": 130},
    "6": {"width": 130},
    "7": {"width": 130},
    "8": {"width": 120},
    "9": {"width": 120},
    "10": {"width": 250},  # 富文本列宽（合并后）
    "len": 100
}

print_config = {
    "paper": "A4",
    "width": 210, "height": 297,
    "definition": 1,
    "isBackend": False,
    "marginX": 10, "marginY": 10,
    "layout": "landscape",   # 横向打印（列较多）
    "printCallBackUrl": ""
}
```

---

## 完整创建脚本

```python
import urllib.request
import json
import ssl
import time
import random
import hashlib

API_BASE = '<api_base>'
TOKEN = 'YOUR_TOKEN_HERE'
SIGNATURE_SECRET = 'dd05f1c54d63749eda95f9fa6d49v442a'

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SIGNED_ENDPOINTS = ['/jmreport/queryFieldBySql', '/jmreport/executeSelectApi',
                    '/jmreport/loadTableData', '/jmreport/testConnection',
                    '/jmreport/download/image', '/jmreport/dictCodeSearch',
                    '/jmreport/getDataSourceByPage', '/jmreport/getDataSourceById']

def compute_sign(params_dict):
    str_params = {}
    for k, v in params_dict.items():
        if v is None: continue
        if isinstance(v, bool): str_params[k] = str(v).lower()
        elif isinstance(v, (int, float)): str_params[k] = str(v)
        elif isinstance(v, (dict, list)): str_params[k] = json.dumps(v, ensure_ascii=False, separators=(',', ':'))
        else: str_params[k] = str(v)
    sorted_params = dict(sorted(str_params.items()))
    params_json = json.dumps(sorted_params, ensure_ascii=False, separators=(',', ':'))
    return hashlib.md5((params_json + SIGNATURE_SECRET).encode('utf-8')).hexdigest().upper()

def api_request(path, data=None, method=None):
    url = f'{API_BASE}{path}'
    headers = {'X-Access-Token': TOKEN, 'Content-Type': 'application/json; charset=UTF-8'}
    need_sign = any(path.rstrip('/').endswith(ep.rstrip('/')) for ep in SIGNED_ENDPOINTS)
    if need_sign:
        headers['X-TIMESTAMP'] = str(int(time.time() * 1000))
        headers['X-Sign'] = compute_sign(data if data else {})
    if data is not None:
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers=headers, method=method or 'POST')
    else:
        req = urllib.request.Request(url, headers=headers, method=method or 'GET')
    resp = urllib.request.urlopen(req, context=ctx)
    return json.loads(resp.read().decode('utf-8'))

def gen_id():
    return str(int(time.time() * 1000) * 1000000 + random.randint(100000, 999999))

# ===== Step 1: 创建空报表 =====
report_id = gen_id()
designer_obj = {
    "id": report_id, "name": "员工数据格式展示报表",
    "type": "0", "template": 0, "delFlag": 0,
    "viewCount": 0, "updateCount": 0, "submitForm": 0,
    "reportName": "员工数据格式展示报表"
}
r1 = api_request('/jmreport/save', {
    "designerObj": json.dumps(designer_obj, ensure_ascii=False),
    "rows": {"len": 200}, "cols": {"len": 100}, "styles": [], "merges": [],
    "validations": [], "autofilter": {}, "dbexps": [], "dicts": [],
    "loopBlockList": [], "zonedEditionList": [], "fixedPrintHeadRows": [],
    "fixedPrintTailRows": [], "hiddenCells": [], "submitHandlers": [],
    "rpbar": {"show": True, "pageSize": "", "btnList": []},
    "fillFormToolbar": {"show": True, "btnList": ["save","print","close","exportPDF","exportExcel"]},
    "hidden": {"rows": [], "cols": [], "conditions": {"rows": {}, "cols": {}}},
    "fillFormInfo": {"layout": {"direction": "horizontal", "width": 200, "height": 45}},
    "recordSubTableOrCollection": {"group": [], "record": [], "range": []},
    "displayConfig": {},
    "printConfig": {"paper": "A4", "width": 210, "height": 297, "definition": 1,
                    "isBackend": False, "marginX": 10, "marginY": 10,
                    "layout": "landscape", "printCallBackUrl": ""},
    "querySetting": {"izOpenQueryBar": False, "izDefaultQuery": True},
    "queryFormSetting": {"useQueryForm": False, "dbKey": "", "idField": ""},
    "area": False, "chartList": [], "background": False, "dataRectWidth": 1200,
    "excel_config_id": report_id, "pyGroupEngine": False,
    "isViewContentHorizontalCenter": False, "fillFormStyle": "default",
    "freeze": "A1", "freezeLineColor": "rgb(185, 185, 185)",
    "sheetId": "default", "sheetName": "默认Sheet", "sheetOrder": "0"
})
print('Step1 创建空报表:', r1.get('code'))

# ===== Step 2: 保存JSON数据集 =====
json_data_content = {"data": [
    {"name": "张三", "code": "EMP001", "dept": "技术部",
     "hire_date": "2020-03-15", "create_time": "2020-03-15 09:30:00",
     "salary": 15000.5, "bonus": 3800, "factor": 1.25, "rate": 0.95,
     "price_usd": 2100.0, "price_eur": 1900.0,
     "avatar": "https://cdn.pixabay.com/photo/2016/08/08/09/17/avatar-1577909_1280.png",
     "barcode_val": "6901234567890", "qrcode_val": "https://www.jeecg.com",
     "remark": "<b>年度优秀</b>员工，<font color='red'>连续三年</font>绩效A+"},
    {"name": "李四", "code": "EMP002", "dept": "市场部",
     "hire_date": "2019-07-20", "create_time": "2019-07-20 14:00:00",
     "salary": 12000.0, "bonus": 2500, "factor": 1.1, "rate": 0.88,
     "price_usd": 1680.0, "price_eur": 1520.0,
     "avatar": "https://cdn.pixabay.com/photo/2016/08/08/09/17/avatar-1577909_1280.png",
     "barcode_val": "6901234567891", "qrcode_val": "https://www.baidu.com",
     "remark": "<b>季度销售冠军</b>，<font color='blue'>超额完成</font>目标120%"},
    {"name": "王五", "code": "EMP003", "dept": "财务部",
     "hire_date": "2021-01-08", "create_time": "2021-01-08 10:15:00",
     "salary": 13500.75, "bonus": 1800, "factor": 0.95, "rate": 0.76,
     "price_usd": 1890.0, "price_eur": 1710.0,
     "avatar": "https://cdn.pixabay.com/photo/2016/08/08/09/17/avatar-1577909_1280.png",
     "barcode_val": "6901234567892", "qrcode_val": "https://www.github.com",
     "remark": "考核待提升，<i>需加强业务学习</i>"},
    {"name": "赵六", "code": "EMP004", "dept": "技术部",
     "hire_date": "2018-11-25", "create_time": "2018-11-25 08:45:00",
     "salary": 18000.0, "bonus": 5200, "factor": 1.35, "rate": 0.92,
     "price_usd": 2520.0, "price_eur": 2280.0,
     "avatar": "https://cdn.pixabay.com/photo/2016/08/08/09/17/avatar-1577909_1280.png",
     "barcode_val": "6901234567893", "qrcode_val": "https://www.zhihu.com",
     "remark": "<b>技术骨干</b>，带队完成<font color='green'>多个核心项目</font>"},
    {"name": "孙七", "code": "EMP005", "dept": "人事部",
     "hire_date": "2022-06-10", "create_time": "2022-06-10 11:30:00",
     "salary": 11000.0, "bonus": 2000, "factor": 1.0, "rate": 0.83,
     "price_usd": 1540.0, "price_eur": 1395.0,
     "avatar": "https://cdn.pixabay.com/photo/2016/08/08/09/17/avatar-1577909_1280.png",
     "barcode_val": "6901234567894", "qrcode_val": "https://www.bilibili.com",
     "remark": "新入职培训中，<u>表现良好</u>"}
]}

field_list = [
    {"fieldName": "name",        "fieldText": "姓名",    "widgetType": "String", "orderNum": 1},
    {"fieldName": "code",        "fieldText": "工号",    "widgetType": "String", "orderNum": 2},
    {"fieldName": "dept",        "fieldText": "部门",    "widgetType": "String", "orderNum": 3},
    {"fieldName": "hire_date",   "fieldText": "入职日期", "widgetType": "String", "orderNum": 4},
    {"fieldName": "create_time", "fieldText": "创建时间", "widgetType": "String", "orderNum": 5},
    {"fieldName": "salary",      "fieldText": "基本工资", "widgetType": "Number", "orderNum": 6},
    {"fieldName": "bonus",       "fieldText": "奖金",    "widgetType": "Number", "orderNum": 7},
    {"fieldName": "factor",      "fieldText": "绩效系数", "widgetType": "Number", "orderNum": 8},
    {"fieldName": "rate",        "fieldText": "完成率",  "widgetType": "Number", "orderNum": 9},
    {"fieldName": "price_usd",   "fieldText": "美元价格", "widgetType": "Number", "orderNum": 10},
    {"fieldName": "price_eur",   "fieldText": "欧元价格", "widgetType": "Number", "orderNum": 11},
    {"fieldName": "avatar",      "fieldText": "头像",    "widgetType": "String", "orderNum": 12},
    {"fieldName": "barcode_val", "fieldText": "条形码值", "widgetType": "String", "orderNum": 13},
    {"fieldName": "qrcode_val",  "fieldText": "二维码值", "widgetType": "String", "orderNum": 14},
    {"fieldName": "remark",      "fieldText": "备注",    "widgetType": "String", "orderNum": 15}
]

r2 = api_request('/jmreport/saveDb', {
    "izSharedSource": 0, "jimuReportId": report_id,
    "dbCode": "emp", "dbChName": "员工数据",
    "dbType": "3", "dbSource": "",
    "jsonData": json.dumps(json_data_content, ensure_ascii=False),
    "apiConvert": "", "isList": "1", "isPage": "0", "dbDynSql": "",
    "fieldList": field_list, "paramList": []
})
print('Step2 保存数据集:', r2.get('code'))

# ===== Step 3: 保存完整报表设计 =====
B = {"bottom": ["thin", "#d8d8d8"], "top": ["thin", "#d8d8d8"],
     "left": ["thin", "#d8d8d8"], "right": ["thin", "#d8d8d8"]}

styles_list = [
    {"border": B, "align": "center", "valign": "middle", "font": {"bold": True, "size": 18}, "bgcolor": "#E6F2FF", "color": "#0066CC"},
    {"border": B, "align": "center", "valign": "middle", "font": {"bold": True, "size": 12}, "bgcolor": "#FFF2CC", "color": "#E67E00"},
    {"border": B, "align": "center", "valign": "middle", "font": {"bold": True}, "bgcolor": "#01b0f1", "color": "#ffffff"},
    {"border": B, "align": "center", "valign": "middle"},
    {"border": B, "align": "center", "valign": "middle", "font": {"bold": True}},
    {"border": B, "align": "center", "valign": "middle", "format": "number"},
    {"border": B, "align": "center", "valign": "middle", "format": "percent"},
    {"border": B, "align": "right",  "valign": "middle", "format": "rmb"},
    {"border": B, "align": "right",  "valign": "middle", "format": "usd"},
    {"border": B, "align": "right",  "valign": "middle", "format": "eur"},
    {"border": B, "align": "center", "valign": "middle", "format": "date"},
    {"border": B, "align": "center", "valign": "middle", "format": "date2"},
    {"border": B, "align": "center", "valign": "middle", "format": "year"},
    {"border": B, "align": "center", "valign": "middle", "format": "month"},
    {"border": B, "align": "center", "valign": "middle", "format": "yearMonth"},
    {"border": B, "align": "center", "valign": "middle", "format": "time"},
    {"border": B, "align": "center", "valign": "middle", "format": "datetime"},
    {"border": B, "align": "left",   "valign": "middle"},
    {"border": B, "align": "center", "valign": "middle", "bgcolor": "#F2F2F2", "color": "#333333"},
    {"border": B, "align": "center", "valign": "middle", "font": {"bold": True, "size": 12}, "bgcolor": "#E8DAEF", "color": "#6A1B9A"},
    {"border": B, "align": "center", "valign": "middle", "font": {"bold": True, "size": 12}, "bgcolor": "#E2EFDA", "color": "#2E7D32"},
    {"border": B, "align": "left",   "valign": "middle"},
    {"border": B, "align": "right",  "valign": "middle"},
    {"border": B, "align": "center", "valign": "middle", "font": {"bold": True, "size": 14}},
    {"border": B, "align": "center", "valign": "middle", "font": {"italic": True}},
    {"border": B, "align": "center", "valign": "middle", "color": "#FF0000"},
    {"border": B, "align": "center", "valign": "middle", "bgcolor": "#C6EFCE", "color": "#006100"},
    {"border": B, "align": "center", "valign": "middle", "bgcolor": "#FFC7CE", "color": "#9C0006"},
    {"border": B, "align": "center", "valign": "middle", "bgcolor": "#FFEB9C", "color": "#9C6500"},
    {"border": B, "align": "center", "valign": "middle", "font": {"underline": True}},
    {"border": B, "align": "center", "valign": "middle", "font": {"strike": True}}
]

rows_data = {
    "0": {"cells": {"1": {"text": "员工数据格式展示报表", "style": 0, "merge": [0, 9]}}, "height": 55},
    "1": {"cells": {"1": {"text": "一、数值与货币格式（format）", "style": 1, "merge": [0, 9]}}, "height": 32},
    "2": {"cells": {"1": {"text": "姓名", "style": 2}, "2": {"text": "正常数值", "style": 2}, "3": {"text": "数值(千分位)", "style": 2}, "4": {"text": "百分比", "style": 2}, "5": {"text": "人民币(￥)", "style": 2}, "6": {"text": "美元($)", "style": 2}, "7": {"text": "欧元(€)", "style": 2}}, "height": 34},
    "3": {"cells": {"1": {"text": "#{emp.name}", "style": 4}, "2": {"text": "#{emp.salary}", "style": 3, "display": "number"}, "3": {"text": "#{emp.salary}", "style": 5, "display": "number"}, "4": {"text": "#{emp.rate}", "style": 6, "display": "number"}, "5": {"text": "#{emp.salary}", "style": 7, "display": "number"}, "6": {"text": "#{emp.price_usd}", "style": 8, "display": "number"}, "7": {"text": "#{emp.price_eur}", "style": 9, "display": "number"}}, "height": 30},
    "4": {"cells": {}, "height": 15},
    "5": {"cells": {"1": {"text": "二、日期时间格式（format）", "style": 19, "merge": [0, 9]}}, "height": 32},
    "6": {"cells": {"1": {"text": "姓名", "style": 2}, "2": {"text": "短日期", "style": 2}, "3": {"text": "长日期", "style": 2}, "4": {"text": "年", "style": 2}, "5": {"text": "月", "style": 2}, "6": {"text": "年月", "style": 2}, "7": {"text": "时间", "style": 2}, "8": {"text": "日期+时间", "style": 2}}, "height": 34},
    "7": {"cells": {"1": {"text": "#{emp.name}", "style": 4}, "2": {"text": "#{emp.hire_date}", "style": 10}, "3": {"text": "#{emp.hire_date}", "style": 11}, "4": {"text": "#{emp.hire_date}", "style": 12}, "5": {"text": "#{emp.hire_date}", "style": 13}, "6": {"text": "#{emp.hire_date}", "style": 14}, "7": {"text": "#{emp.create_time}", "style": 15}, "8": {"text": "#{emp.create_time}", "style": 16}}, "height": 30},
    "8": {"cells": {}, "height": 15},
    "9": {"cells": {"1": {"text": "三、单元格类型（display / 类型）", "style": 20, "merge": [0, 9]}}, "height": 32},
    "10": {"cells": {"1": {"text": "姓名", "style": 2}, "2": {"text": "文本", "style": 2}, "3": {"text": "数值", "style": 2}, "4": {"text": "图片", "style": 2}, "5": {"text": "条形码", "style": 2}, "6": {"text": "二维码", "style": 2}, "7": {"text": "富文本", "style": 2, "merge": [0, 3]}}, "height": 34},
    "11": {"cells": {"1": {"text": "#{emp.name}", "style": 4}, "2": {"text": "#{emp.code}", "style": 3}, "3": {"text": "#{emp.salary}", "style": 5, "display": "number"}, "4": {"text": "#{emp.avatar}", "style": 3, "display": "img"}, "5": {"text": "#{emp.barcode_val}", "style": 3, "display": "barcode"}, "6": {"text": "#{emp.qrcode_val}", "style": 3, "display": "qrcode"}, "7": {"text": "#{emp.remark}", "style": 17, "display": "richText", "merge": [0, 3]}}, "height": 80},
    "12": {"cells": {}, "height": 15},
    "13": {"cells": {"1": {"text": "四、单元格样式展示（font / align / bgcolor）", "style": 1, "merge": [0, 9]}}, "height": 32},
    "14": {"cells": {"1": {"text": "样式名称", "style": 2}, "2": {"text": "左对齐", "style": 2}, "3": {"text": "居中对齐", "style": 2}, "4": {"text": "右对齐", "style": 2}, "5": {"text": "加粗14号", "style": 2}, "6": {"text": "斜体", "style": 2}, "7": {"text": "红色字体", "style": 2}, "8": {"text": "下划线", "style": 2}, "9": {"text": "删除线", "style": 2}}, "height": 34},
    "15": {"cells": {"1": {"text": "效果展示", "style": 18}, "2": {"text": "左对齐文本", "style": 21}, "3": {"text": "居中文本", "style": 3}, "4": {"text": "右对齐文本", "style": 22}, "5": {"text": "加粗大字", "style": 23}, "6": {"text": "斜体文字", "style": 24}, "7": {"text": "红色警告", "style": 25}, "8": {"text": "下划线文本", "style": 29}, "9": {"text": "已完成项目", "style": 30}}, "height": 30},
    "16": {"cells": {"1": {"text": "背景色", "style": 2}, "2": {"text": "成功/通过", "style": 26, "merge": [0, 2]}, "5": {"text": "警告/待处理", "style": 28, "merge": [0, 1]}, "7": {"text": "失败/拒绝", "style": 27, "merge": [0, 2]}}, "height": 30},
    "len": 200
}

cols_data = {
    "0": {"width": 25}, "1": {"width": 80}, "2": {"width": 100}, "3": {"width": 100},
    "4": {"width": 130}, "5": {"width": 130}, "6": {"width": 130}, "7": {"width": 130},
    "8": {"width": 120}, "9": {"width": 120}, "10": {"width": 250}, "len": 100
}

merges_list = [
    "B1:K1", "B2:K2", "B6:K6", "B10:K10",
    "H11:K11", "H12:K12",
    "B14:K14", "C17:E17", "F17:G17", "H17:J17"
]

r3 = api_request('/jmreport/save', {
    "designerObj": json.dumps(designer_obj, ensure_ascii=False),
    "name": "sheet1", "freeze": "A1", "freezeLineColor": "rgb(185, 185, 185)",
    "rows": rows_data, "cols": cols_data, "styles": styles_list, "merges": merges_list,
    "validations": [], "autofilter": {}, "dbexps": [], "dicts": [],
    "loopBlockList": [], "zonedEditionList": [], "fixedPrintHeadRows": [],
    "fixedPrintTailRows": [], "hiddenCells": [], "submitHandlers": [],
    "rpbar": {"show": True, "pageSize": "", "btnList": []},
    "fillFormToolbar": {"show": True, "btnList": ["save","print","close","exportPDF","exportExcel","exportWord"]},
    "hidden": {"rows": [], "cols": [], "conditions": {"rows": {}, "cols": {}}},
    "fillFormInfo": {"layout": {"direction": "horizontal", "width": 200, "height": 45}},
    "recordSubTableOrCollection": {"group": [], "record": [], "range": []},
    "displayConfig": {},
    "printConfig": {"paper": "A4", "width": 210, "height": 297, "definition": 1,
                    "isBackend": False, "marginX": 10, "marginY": 10,
                    "layout": "landscape", "printCallBackUrl": ""},
    "querySetting": {"izOpenQueryBar": False, "izDefaultQuery": True},
    "queryFormSetting": {"useQueryForm": False, "dbKey": "", "idField": ""},
    "area": False, "chartList": [], "background": False, "dataRectWidth": 1200,
    "excel_config_id": report_id, "pyGroupEngine": False,
    "isViewContentHorizontalCenter": False, "fillFormStyle": "default",
    "sheetId": "default", "sheetName": "默认Sheet", "sheetOrder": "0"
})
print('Step3 保存完整设计:', r3.get('code'))
print(f'报表地址: {API_BASE}/jmreport/view/{report_id}')
```