# 纵向分组自定义排序示例

**验证时间：** 2026-04-17，JSON 数据集，成功。

## 关键配置

分组单元格上增加 `textOrders` 字段，值为竖线分隔的自定义顺序：

```python
"1": {
    "text": f"#{{{DB_CODE}.group(region)}}",
    "style": 3,
    "aggregate": "group",
    "subtotal": "groupField",
    "funcname": "-1",
    "subtotalText": "合计",
    "textOrders": "华北|华南|华东",   # ← 自定义排序，竖线分隔
},
```

- `textOrders` 是单元格级属性，只加在**分组字段**所在单元格上
- 顺序按 `|` 分隔，从左到右为显示顺序
- 数据集中数据本身的顺序不影响最终展示顺序

## 效果预览

```
┌──────┬──────┬─────────┐
│ 区域 │ 城市 │  销售额  │
├──────┼──────┼─────────┤
│      │ 北京 │ 120,000 │   ← 华北（自定义第1）
│ 华北 ├──────┼─────────┤
│      │ 天津 │  55,000 │
│      │ 合计 │ 175,000 │
├──────┼──────┼─────────┤
│      │ 广州 │  73,000 │   ← 华南（自定义第2）
│ 华南 ├──────┼─────────┤
│      │ 深圳 │  91,000 │
│      │ 合计 │ 164,000 │
├──────┼──────┼─────────┤
│      │ 上海 │  85,000 │   ← 华东（自定义第3）
│ 华东 ├──────┼─────────┤
│      │ 南京 │  62,000 │
│      │ 合计 │ 147,000 │
├──────┴──────┼─────────┤
│    总计      │ 486,000 │
└─────────────┴─────────┘
```

## 完整 rows 片段

```python
rows = {
    "0": {
        "cells": {
            "0": {"text": "", "style": 0},
            "1": {"text": "自定义分组排序", "style": 1, "merge": [0, 2]},
        },
        "height": 45,
    },
    "1": {
        "cells": {
            "0": {"text": "", "style": 0},
            "1": {"text": "区域", "style": 2},
            "2": {"text": "城市", "style": 2},
            "3": {"text": "销售额", "style": 2},
        },
        "height": 34,
    },
    "2": {
        "cells": {
            "0": {"text": "", "style": 0},
            "1": {
                "text": f"#{{{DB_CODE}.group(region)}}",
                "style": 3,
                "aggregate": "group",
                "subtotal": "groupField",
                "funcname": "-1",
                "subtotalText": "合计",
                "textOrders": "华北|华南|华东",  # 自定义排序
            },
            "2": {
                "text": f"#{{{DB_CODE}.group(city)}}",
                "style": 3,
                "aggregate": "group",
            },
            "3": {
                "text": f"#{{{DB_CODE}.sales}}",
                "style": 3,
            },
        },
        "height": 30,
    },
    "3": {
        "cells": {
            "0": {"text": "", "style": 0},
            "1": {"text": "总计", "style": 4, "merge": [0, 1]},
            "3": {"text": "=SUM(D3)", "style": 4},
        },
        "height": 30,
    },
    "len": 100,
}
```

## JSON 数据集注意事项

- `json_data` 参数必须传 JSON **字符串**（不是 list），用 `json.dumps` 包裹：

```python
db_id = save_db(
    session, report_id, DB_CODE, "数据集名",
    "",
    field_list,
    db_type="3",
    is_list="1",
    is_page="0",
    json_data=json.dumps({"data": raw_list}, ensure_ascii=False),  # ← 必须包裹
)
```

## 顶层分组配置

```python
save_body["isGroup"]    = True
save_body["groupField"] = f"{DB_CODE}.region"   # 格式：dbCode.字段名
```
