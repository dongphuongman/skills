# 主子表报表示例

主子表报表：主表用 `${db.field}` 单值绑定，子表用 `#{db.field}` 列表绑定，通过 linkType=4 联动。

---

## 一、核心规则

### 数据绑定

| 表 | 绑定语法 | 说明 |
|----|---------|------|
| 主表 | `${主表code.字段}` | 单值绑定，显示一条记录 |
| 子表 | `#{子表code.字段}` | 列表绑定，循环展开多条 |

### 关键约束

> **SQL 中有 `${param}` 参数时，主表和子表的 paramList 都必须生成对应参数条目。** 即使子表参数是通过主子表联动自动传递的，也必须在 paramList 中声明，否则主子表配置时子表参数下拉为空。
>
> **子表参数不勾选查询**（`searchFlag: 0`），因为子表数据由主子表联动自动传参，不需要在查询栏显示。主表参数才需要 `searchFlag: 1`。

---

## 二、完整创建流程（SQL 数据集）

### Step 1: 创建空报表

```python
report_id = gen_id()
# save 空报表 → 获取 report_id
```

### Step 2: 创建主表数据集

```python
main_sql = "select id, order_no, customer_name, customer_phone, address, order_date, total_amount, status from order_main where id = '${order_id}'"

main_db = {
    "jimuReportId": report_id,
    "dbCode": "orderMain",
    "dbChName": "订单主表",
    "dbType": "0",
    "isList": "1",
    "isPage": "1",       # 主表可分页
    "dbDynSql": main_sql,
    "fieldList": [
        {"fieldName": "id", "fieldText": "ID", "widgetType": "String", "orderNum": 1},
        {"fieldName": "order_no", "fieldText": "订单编号", "widgetType": "String", "orderNum": 2},
        {"fieldName": "customer_name", "fieldText": "客户姓名", "widgetType": "String", "orderNum": 3},
        # ...其他字段
    ],
    # SQL 有 ${order_id} → paramList 必须有 order_id
    "paramList": [
        {"paramName": "order_id", "paramTxt": "订单ID", "paramValue": "", "widgetType": "String", "orderNum": 1, "searchFlag": 1, "searchMode": 1}
    ]
}
api_request('/jmreport/saveDb', main_db)
```

### Step 3: 创建子表数据集

```python
sub_sql = "select id, product_name, price, qty, subtotal from order_detail where order_id = '${order_id}'"

sub_db = {
    "jimuReportId": report_id,
    "dbCode": "orderSub",
    "dbChName": "订单明细",
    "dbType": "0",
    "isList": "1",
    "isPage": "0",       # 子表不分页
    "dbDynSql": sub_sql,
    "fieldList": [
        {"fieldName": "id", "fieldText": "ID", "widgetType": "String", "orderNum": 1},
        {"fieldName": "product_name", "fieldText": "商品名称", "widgetType": "String", "orderNum": 2},
        {"fieldName": "price", "fieldText": "单价", "widgetType": "number", "orderNum": 3},
        {"fieldName": "qty", "fieldText": "数量", "widgetType": "number", "orderNum": 4},
        {"fieldName": "subtotal", "fieldText": "小计", "widgetType": "number", "orderNum": 5}
    ],
    # 子表 SQL 也有 ${order_id} → paramList 也必须有！但子表参数不勾选查询
    "paramList": [
        {"paramName": "order_id", "paramTxt": "订单ID", "paramValue": "", "widgetType": "String", "orderNum": 1, "searchFlag": 0, "searchMode": 1}
    ]
}
api_request('/jmreport/saveDb', sub_db)
```

### Step 4: 配置主子表联动

```python
import json

parameter = json.dumps({
    "main": "orderMain",          # 主表 dbCode
    "sub": "orderSub",            # 子表 dbCode
    "subReport": [{
        "mainField": "id",        # 主表关联字段
        "subParam": "order_id",   # 子表参数名（对应子表 SQL 中的 ${order_id}）
        "tableIndex": 1           # 子表序号（从1开始）
    }]
}, ensure_ascii=False)

link_data = {
    "mainReport": "orderMain",
    "subReport": "orderSub",
    "linkName": "订单主子表",
    "parameter": parameter,
    "linkType": "4",              # 4 = 主子表联动
    "reportId": report_id
}
api_request('/jmreport/link/saveAndEdit', link_data)
```

### Step 5: 保存报表设计

```python
rows_data = {
    # 标题
    "1": {"cells": {"1": {"text": "订单详情", "style": 5, "merge": [0, 5]}}, "height": 40},
    # 主表信息（${} 单值绑定）
    "2": {"cells": {
        "1": {"text": "订单编号：", "style": 6},
        "2": {"text": "${orderMain.order_no}", "style": 7, "merge": [0, 1]},
        "4": {"text": "下单日期：", "style": 6},
        "5": {"text": "${orderMain.order_date}", "style": 7, "merge": [0, 1]}
    }, "height": 30},
    "3": {"cells": {
        "1": {"text": "客户姓名：", "style": 6},
        "2": {"text": "${orderMain.customer_name}", "style": 7, "merge": [0, 1]},
        "4": {"text": "联系电话：", "style": 6},
        "5": {"text": "${orderMain.customer_phone}", "style": 7, "merge": [0, 1]}
    }, "height": 30},
    "4": {"cells": {
        "1": {"text": "收货地址：", "style": 6},
        "2": {"text": "${orderMain.address}", "style": 7, "merge": [0, 1]},
        "4": {"text": "订单总额：", "style": 6},
        "5": {"text": "${orderMain.total_amount}", "style": 7, "merge": [0, 1]}
    }, "height": 30},
    # 分隔
    "5": {"cells": {}, "height": 10},
    # 子表标题
    "6": {"cells": {"1": {"text": "商品明细", "style": 8, "merge": [0, 5]}}, "height": 34},
    # 子表表头
    "7": {"cells": {
        "1": {"text": "序号", "style": 4},
        "2": {"text": "商品名称", "style": 4},
        "3": {"text": "单价", "style": 4},
        "4": {"text": "数量", "style": 4},
        "5": {"text": "小计", "style": 4},
        "6": {"text": "状态", "style": 4}
    }, "height": 34},
    # 子表数据行（#{} 列表绑定）
    "8": {"cells": {
        "1": {"text": "#{orderSub.id}", "style": 2},
        "2": {"text": "#{orderSub.product_name}", "style": 2},
        "3": {"text": "#{orderSub.price}", "style": 2},
        "4": {"text": "#{orderSub.qty}", "style": 2},
        "5": {"text": "#{orderSub.subtotal}", "style": 2},
        "6": {"text": "${orderMain.status}", "style": 2}
    }},
    "len": 200
}
```

### 预览

URL 传参切换主表记录：
```
/jmreport/view/{report_id}?token=xxx&order_id=1
/jmreport/view/{report_id}?token=xxx&order_id=2
```

---

## 三、主子表联动 API 参考

### 新增联动

`POST /jmreport/link/saveAndEdit`

```json
{
    "mainReport": "主表dbCode",
    "subReport": "子表dbCode",
    "linkName": "联动名称",
    "parameter": "{\"main\":\"主表code\",\"sub\":\"子表code\",\"subReport\":[{\"mainField\":\"id\",\"subParam\":\"order_id\",\"tableIndex\":1}]}",
    "linkType": "4",
    "reportId": "报表ID"
}
```

### 编辑联动

同一接口，传 `id` 即为更新。

### 删除联动

`POST /jmreport/link/delete`

```json
{"id": "联动配置ID"}
```

### parameter 结构

```json
{
    "main": "orderMain",
    "sub": "orderSub",
    "subReport": [{
        "mainField": "id",          // 主表字段名
        "subParam": "order_id",     // 子表参数名（对应 ${order_id}）
        "tableIndex": 1             // 子表序号
    }]
}
```

### linkType 值

| linkType | 类型 |
|----------|------|
| `"4"` | 主子表联动 |
| `"2"` | 图表联动 |

---

## 四、API 数据集主子表示例

API 数据集的主子表配置方式相同，区别仅在于数据集类型。

### 主表（API）

```python
main_db = {
    "dbCode": "gg",
    "dbType": "1",           # API
    "apiUrl": "<api_base>/test/getOrder?id='${did}'",
    "apiMethod": "0",        # GET
    "paramList": [
        {"paramName": "did", "paramTxt": "订单ID", "paramValue": "", "widgetType": "String", "orderNum": 1, "searchFlag": 1, "searchMode": 1}
    ],
    ...
}
```

### 子表（API）

```python
sub_db = {
    "dbCode": "xb",
    "dbType": "1",
    "apiUrl": "<api_base>/test/getUserMsg?did='${did}'",
    "apiMethod": "0",
    # 子表也必须有 paramList！但不勾选查询
    "paramList": [
        {"paramName": "did", "paramTxt": "订单ID", "paramValue": "", "widgetType": "String", "orderNum": 1, "searchFlag": 0, "searchMode": 1}
    ],
    ...
}
```

### 联动配置

```python
parameter = json.dumps({
    "main": "gg",
    "sub": "xb",
    "subReport": [{"mainField": "id", "subParam": "did", "tableIndex": 1}]
})
```
