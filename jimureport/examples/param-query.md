# 报表参数查询示例

报表参数（paramList）的完整配置参考，包含 SQL 数据集和 API 数据集两种场景。

---

## 一、SQL 数据集示例

基于 `sys_user` 表，查询条件：username like、sex in、create_time 日期查询。

### SQL（FreeMarker 动态条件）

```sql
select username, realname, sex, email, phone, create_time from sys_user where 1=1
<#if isNotEmpty(username)> and username like concat('%','${username}','%')</#if>
<#if isNotEmpty(sex)> and sex in(${DaoFormat.in('${sex}')})</#if>
<#if isNotEmpty(create_time)> and DATE_FORMAT(create_time,'%Y-%m-%d') = '${create_time}'</#if>
```

### fieldList（纯字段定义，不设置 searchFlag）

```json
[
    {"fieldName": "username", "fieldText": "用户账号", "widgetType": "String", "orderNum": 1},
    {"fieldName": "realname", "fieldText": "真实姓名", "widgetType": "String", "orderNum": 2},
    {"fieldName": "sex", "fieldText": "性别", "widgetType": "String", "orderNum": 3},
    {"fieldName": "email", "fieldText": "邮箱", "widgetType": "String", "orderNum": 4},
    {"fieldName": "phone", "fieldText": "电话", "widgetType": "String", "orderNum": 5},
    {"fieldName": "create_time", "fieldText": "创建时间", "widgetType": "date", "orderNum": 6}
]
```

> **注意：** 数据库中日期类型字段，`widgetType` 设为 `"date"`；数值类型设为 `"number"`。

### paramList

```json
[
    {"paramName": "username", "paramTxt": "用户账号", "paramValue": "", "widgetType": "String", "orderNum": 1, "searchFlag": 1, "searchMode": 1},
    {"paramName": "sex", "paramTxt": "性别", "paramValue": "", "widgetType": "String", "orderNum": 2, "searchFlag": 1, "searchMode": 4, "dictCode": "sex"},
    {"paramName": "create_time", "paramTxt": "创建时间", "paramValue": "", "widgetType": "date", "orderNum": 3, "searchFlag": 1, "searchMode": 1, "searchFormat": "yyyy-MM-dd"}
]
```

### paramList 参数配置（extJson）

报表参数也支持 extJson 参数配置，但**不支持排序（order）**，其余配置与字段查询一致：

```json
[
    {"paramName": "username", "paramTxt": "用户账号", "searchFlag": 1, "searchMode": 1,
     "extJson": "{\"required\":true}"},
    {"paramName": "sex", "paramTxt": "性别", "searchFlag": 1, "searchMode": 4, "dictCode": "sex",
     "extJson": "{\"selectSearchPageSize\":20}"},
    {"paramName": "category", "paramTxt": "分类", "searchFlag": 1, "searchMode": 6,
     "extJson": "{\"loadTree\":\"http://xxx/getCategoryTree\",\"loadTreeByValue\":\"http://xxx/getCategoryTreeByValue\",\"treeMultiple\":false}"}
]
```

**报表参数 extJson 可用配置：**

| 配置项 | 说明 | 适用 searchMode |
|-------|------|----------------|
| `required` | 必填 true/false | 所有 |
| `dictSplit` | 字典分隔符 | 下拉多选(3) |
| `selectSearchPageSize` | 下拉每次加载条数 | 下拉单选(4)/多选(3) |
| `loadTree` | 加载树结构请求地址 | 下拉树(6)，**必填** |
| `loadTreeByValue` | 根据值获取树信息地址（穿透回显） | 下拉树(6) |
| `treeMultiple` | 下拉树是否多选 | 下拉树(6) |

> **注意：** 报表参数不支持 `order`（排序），排序仅报表字段明细支持。

### saveDb 请求体

```json
{
    "izSharedSource": 0,
    "jimuReportId": "报表ID",
    "dbCode": "users",
    "dbChName": "用户信息",
    "dbType": "0",
    "dbSource": "",
    "jsonData": "",
    "apiConvert": "",
    "isList": "1",
    "isPage": "1",
    "dbDynSql": "SQL语句（含FreeMarker条件）",
    "fieldList": [],
    "paramList": []
}
```

---

## 二、API 数据集示例

基于 `/jmreport/test/getUserMsg` 接口，参数：cname、did、riqi。

### API 地址配置

**默认使用后台完整地址，不用 `#{domainURL}`：**

```
<api_base>/test/getUserMsg?cname='${cname}'&did='${did}'&riqi='${riqi}'
```

> 参数用 `'${param}'` 格式拼接在 URL 中，多参数用 `&` 连接。

### API 字段解析

`executeSelectApi` 接口使用 `@RequestParam`，必须发送 **form-urlencoded** 格式（不是 JSON body）：

```python
import urllib.parse

# 解析时用不带参数变量的完整URL
parse_url = f"{API_BASE}/jmreport/test/getUserMsg?cname=&did=&riqi="
form_params = {"api": parse_url, "method": "0", "paramArray": "[]"}

form_data = urllib.parse.urlencode(form_params).encode('utf-8')
req_url = f'{API_BASE}/jmreport/executeSelectApi'
headers = {
    'X-Access-Token': TOKEN,
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-TIMESTAMP': str(int(time.time() * 1000)),
    'X-Sign': compute_sign(form_params)
}
req = urllib.request.Request(req_url, data=form_data, headers=headers, method='POST')
```

**返回结构（直接数组，不是 result.fieldList）：**
```json
{
  "result": [
    {"fieldName": "cname", "fieldText": "cname", "widgetType": "String", "isShow": true, "orderNum": 1}
  ]
}
```

### paramList

```json
[
    {"paramName": "cname", "paramTxt": "名称", "paramValue": "", "widgetType": "String", "orderNum": 1, "searchFlag": 1, "searchMode": 1},
    {"paramName": "did", "paramTxt": "ID", "paramValue": "", "widgetType": "String", "orderNum": 2, "searchFlag": 1, "searchMode": 1},
    {"paramName": "riqi", "paramTxt": "日期", "paramValue": "", "widgetType": "date", "orderNum": 3, "searchFlag": 1, "searchMode": 1, "searchFormat": "yyyy-MM-dd"}
]
```

### saveDb 请求体

```json
{
    "izSharedSource": 0,
    "jimuReportId": "报表ID",
    "dbCode": "userMsg",
    "dbChName": "用户信息",
    "dbType": "1",
    "apiUrl": "<api_base>/test/getUserMsg?cname='${cname}'&did='${did}'&riqi='${riqi}'",
    "apiMethod": "0",
    "dbSource": "",
    "jsonData": "",
    "apiConvert": "",
    "isList": "1",
    "isPage": "1",
    "dbDynSql": "",
    "fieldList": [],
    "paramList": []
}
```

---

## 三、JavaBean 数据集示例

基于 `testRpSpringBean`（实现 `IDataSetFactory`），`createData` 方法接受 `name`、`sex` 参数，返回字段 `name`、`value`、`sex`。

### JavaBean 字段解析

`queryFieldByBean` 用 `@RequestBody` JSON，**不需要签名**：

```python
parse_result = api_request('/jmreport/queryFieldByBean', {
    "javaType": "spring-key",
    "javaValue": "testRpSpringBean",
    "isPage": False,
    "param": {}
})
```

**返回结构（与 API 解析相同，直接数组）：**
```json
{
  "result": [
    {"fieldName": "name", "fieldText": "name", "widgetType": "String", "orderNum": 1},
    {"fieldName": "value", "fieldText": "value", "widgetType": "String", "orderNum": 2},
    {"fieldName": "sex", "fieldText": "sex", "widgetType": "String", "orderNum": 3}
  ]
}
```

### paramList

JavaBean 的参数对应 `createData(Map<String, Object> param)` 中 `param.get("xxx")` 的 key：

```json
[
    {"paramName": "name", "paramTxt": "名称", "paramValue": "", "widgetType": "String", "orderNum": 1, "searchFlag": 1, "searchMode": 1},
    {"paramName": "sex", "paramTxt": "性别", "paramValue": "", "widgetType": "String", "orderNum": 2, "searchFlag": 1, "searchMode": 1}
]
```

### saveDb 请求体

```json
{
    "izSharedSource": 0,
    "jimuReportId": "报表ID",
    "dbCode": "beanData",
    "dbChName": "JavaBean数据",
    "dbType": "2",
    "javaType": "spring-key",
    "javaValue": "testRpSpringBean",
    "dbSource": "",
    "jsonData": "",
    "apiConvert": "",
    "isList": "1",
    "isPage": "0",
    "dbDynSql": "",
    "fieldList": [
        {"fieldName": "name", "fieldText": "名称", "widgetType": "String", "orderNum": 1},
        {"fieldName": "value", "fieldText": "数值", "widgetType": "String", "orderNum": 2},
        {"fieldName": "sex", "fieldText": "性别", "widgetType": "String", "orderNum": 3}
    ],
    "paramList": [
        {"paramName": "name", "paramTxt": "名称", "paramValue": "", "widgetType": "String", "orderNum": 1, "searchFlag": 1, "searchMode": 1},
        {"paramName": "sex", "paramTxt": "性别", "paramValue": "", "widgetType": "String", "orderNum": 2, "searchFlag": 1, "searchMode": 1}
    ]
}
```

> **注意：** `isPage` 设为 `"0"`，因为 `createData` 返回全部数据不分页。若 Bean 实现了 `createPageData` 方法且需要分页，则 `isPage` 设为 `"1"`。

### 图表绑定 JavaBean 数据集

图表的 `extData.dataType` 使用 `"javabean"`：

```json
{
    "extData": {
        "chartType": "pie.simple",
        "dataType": "javabean",
        "dataId": "数据集ID",
        "dbCode": "beanData",
        "axisX": "name",
        "axisY": "value",
        "series": "type",
        "apiStatus": "1"
    }
}
```

> **图表字段映射：** JavaBean 返回的字段名必须包含 `name` 和 `value`（图表固定字段），否则需要在 Bean 中做别名映射。

---

## 四、通用参考

### fieldList 字段说明（报表字段明细）

| 字段 | 说明 |
|------|------|
| `fieldName` | 字段名，对应 SQL 查询结果列名 |
| `fieldText` | 字段显示文本（中文名） |
| `widgetType` | 数据类型：`"String"` / `"date"` / `"number"` |
| `orderNum` | 显示排序 |
| `searchFlag` | 1=勾选查询，0=不查询 |
| `searchMode` | 查询模式，见 searchMode 映射表 |
| `searchValue` | **查询默认值**（fieldList 专用，对应 UI "查询默认值"列）。支持静态值、`\|` 范围分隔、`=dateStr()` 表达式、`#{sysDate}` 系统变量 |
| `dictCode` | 数据字典，3种格式：① 系统字典编码（如 `sex`）② SQL字典（见下方规则）③ API接口地址 |
| `searchFormat` | 日期格式，如 `yyyy-MM-dd`、`yyyy-MM-dd HH:mm:ss` |
| `extJson` | 参数配置（JSON字符串），见 extJson 章节 |

> **易错：** fieldList 默认值用 `searchValue`，**不是** `paramValue`。`paramValue` 是 paramList 专用字段，写到 fieldList 里会被忽略。

> **SQL字典必须包含 `FROM 表名`**：纯 `SELECT '1' AS value UNION SELECT '2' AS value`（无 FROM）系统无法识别。
> 正确写法：`SELECT username AS value, username AS text FROM sys_user`

### paramList 字段说明

| 字段 | 说明 |
|------|------|
| `paramName` | 参数名，对应 SQL 中 `${paramName}` 或 API URL 中 `'${paramName}'` |
| `paramTxt` | 参数显示文本 |
| `paramValue` | **查询默认值**（paramList 专用）。**不要自动生成，只有用户明确要求时才配置**（支持静态值、`=dateStr()` 表达式、`#{sysUserCode}` 系统变量） |
| `widgetType` | 数据类型：`"String"` / `"date"` / `"number"` |
| `orderNum` | 显示排序 |
| `searchFlag` | 1=勾选查询，0=不查询 |
| `searchMode` | 查询模式，见下方规则 |
| `dictCode` | 数据字典，3种格式：① 系统字典编码（如 `sex`）② SQL字典（必须含 `FROM 表名`）③ API接口地址 |
| `searchFormat` | 日期格式，如 `yyyy-MM-dd`、`yyyy-MM-dd HH:mm:ss` |

### searchMode 值映射（源码确认）

**报表字段明细（fieldList）可用值：**

| searchMode | 查询模式 | 约束 |
|-----------|---------|------|
| 1 | 输入框 | 无 |
| **2** | **范围查询** | 仅数值(Number)或日期(date)类型 |
| 3 | 下拉多选 | **须配置 dictCode** |
| **4** | **下拉单选** | **须配置 dictCode** |
| 5 | 模糊查询 | 仅字符串(String)类型 |
| 6 | 下拉树 | dictCode 栏填接口地址 |
| 7 | 自定义下拉框 | 需配合 JS 增强，多字段联动 |

**报表参数（paramList）可用值：** 1(输入框)、3(下拉多选)、4(下拉单选)、6(下拉树)、7(自定义下拉框)。不支持 2(范围查询)、5(模糊查询)。

### 报表参数 vs 报表字段查询

| 对比项 | 报表参数（paramList） | 报表字段查询（fieldList searchFlag） |
|-------|---------------------|----------------------------------|
| 触发条件 | SQL/API 中有 `${param}` 参数 | 用户明确说"用字段查询" |
| **默认值字段名** | **`paramValue`** | **`searchValue`** |
| 日期/数值查询模式 | 只能用输入框(1) | 可用输入框(1) 或 范围查询(2) |
| 字符串查询模式 | 只能用输入框(1) | 可用输入框(1) 或 模糊查询(5) |
| 字典字段 | 下拉单选(4) / 下拉多选(3) | 下拉单选(4) / 下拉多选(3) |

### SQL / API / JavaBean 数据集对比

| 对比项 | SQL (dbType=0) | API (dbType=1) | JavaBean (dbType=2) |
|-------|----------------|----------------|---------------------|
| 数据来源 | `dbDynSql` | `apiUrl` + `apiMethod` | `javaType` + `javaValue` |
| 参数格式 | SQL `${param}` + FreeMarker | URL `'${param}'` | `param.get("xxx")` |
| 字段解析接口 | `queryFieldBySql`（JSON body） | `executeSelectApi`（form-urlencoded） | `queryFieldByBean`（JSON body） |
| 需要签名 | 是 | 是 | 否 |
| 解析返回格式 | `result.fieldList[]` | `result[]` | `result[]` |
| 图表 dataType | `"sql"` | `"sql"` | `"javabean"` |
| apiUrl | — | 后台完整地址 | — |
| isPage | 通常 `"1"` | 通常 `"1"` | `"0"`（createData）/ `"1"`（createPageData） |

---

## 五、报表字段查询全类型示例

基于 `test_query_demo` 表，覆盖所有 7 种查询模式 + JS 增强三级联动。

### fieldList 配置

```json
[
    {"fieldName":"user_name","fieldText":"用户名","widgetType":"String","searchFlag":1,"searchMode":5,
     "extJson":"{\"required\":true}"},
    {"fieldName":"phone","fieldText":"电话","widgetType":"String","searchFlag":1,"searchMode":1},
    {"fieldName":"sex","fieldText":"性别","widgetType":"String","searchFlag":1,"searchMode":4,"dictCode":"sex"},
    {"fieldName":"status","fieldText":"状态","widgetType":"String","searchFlag":1,"searchMode":3,"dictCode":"sex",
     "extJson":"{\"dictSplit\":\",\"}"},
    {"fieldName":"age","fieldText":"年龄","widgetType":"number","searchFlag":1,"searchMode":1,
     "extJson":"{\"order\":\"desc\"}"},
    {"fieldName":"province","fieldText":"省","widgetType":"String","searchFlag":1,"searchMode":7},
    {"fieldName":"city","fieldText":"市","widgetType":"String","searchFlag":1,"searchMode":7},
    {"fieldName":"area","fieldText":"区","widgetType":"String","searchFlag":1,"searchMode":7},
    {"fieldName":"category","fieldText":"分类","widgetType":"String","searchFlag":1,"searchMode":6,
     "extJson":"{\"loadTree\":\"http://xxx/getCategoryTree\",\"loadTreeByValue\":\"http://xxx/getCategoryTreeByValue\",\"treeMultiple\":false}"},
    {"fieldName":"birthday","fieldText":"生日","widgetType":"date","searchFlag":1,"searchMode":2},
    {"fieldName":"salary","fieldText":"薪资","widgetType":"number","searchFlag":1,"searchMode":2},
    {"fieldName":"create_time","fieldText":"创建时间","widgetType":"date","searchFlag":1,"searchMode":1}
]
```

### 字段查询模式一览

| 字段 | widgetType | searchMode | 查询模式 | extJson |
|------|-----------|-----------|---------|---------|
| user_name | String | 5 | 模糊查询 | required:true |
| phone | String | 1 | 输入框 | — |
| sex | String | 4 | 下拉单选 | dictCode=sex |
| status | String | 3 | 下拉多选 | dictSplit:"," |
| age | number | 1 | 输入框 | order:desc |
| province | String | 7 | 自定义下拉框 | JS 三级联动 |
| city | String | 7 | 自定义下拉框 | JS 三级联动 |
| area | String | 7 | 自定义下拉框 | JS 三级联动 |
| category | String | 6 | 下拉树 | loadTree + loadTreeByValue |
| birthday | date | 2 | 范围查询 | — |
| salary | number | 2 | 范围查询 | — |
| create_time | date | 1 | 输入框 | — |

### JS 增强（三级联动）

通过 `POST /jmreport/editEnhance` 保存（不是 save 接口）：

```python
api_request('/jmreport/editEnhance', {
    "id": report_id,
    "jsStr": js_code
})
```

```javascript
function init(){
  var apiBase = '<api_base>/test/getAreaList';

  $http.metaGet(apiBase).then(res => {
    var data = Array.isArray(res) ? res : (res.data || res);
    this.updateSelectOptions('queryDemo', 'province', data);
  })

  this.onSearchFormChange('queryDemo', 'province', (value) => {
    this.updateSelectOptions('queryDemo', 'city', []);
    this.updateSelectOptions('queryDemo', 'area', []);
    if(!value) return;
    $http.metaGet(apiBase, {pid: value}).then(res => {
      var data = Array.isArray(res) ? res : (res.data || res);
      this.updateSelectOptions('queryDemo', 'city', data);
    })
  })

  this.onSearchFormChange('queryDemo', 'city', (value) => {
    this.updateSelectOptions('queryDemo', 'area', []);
    if(!value) return;
    $http.metaGet(apiBase, {pid: value}).then(res => {
      var data = Array.isArray(res) ? res : (res.data || res);
      this.updateSelectOptions('queryDemo', 'area', data);
    })
  })
}
```

### 下拉树接口（loadTree + loadTreeByValue）

**loadTree** — 加载树结构，返回 `[{id, pid, value, title, izLeaf}]`：
```java
@GetMapping("/getCategoryTree")
public List<Map<String, Object>> getCategoryTree(@RequestParam(value = "pid", required = false) String pid) {
    // 不传pid返回一级节点，传pid返回子节点
}
```

**loadTreeByValue** — 根据值获取节点及父级（穿透回显）：
```java
@GetMapping("/getCategoryTreeByValue")
public List<Map<String, Object>> getCategoryTreeByValue(@RequestParam(value = "value", required = false) String value) {
    // 返回该节点及所有父级节点（从根到叶）
}
```

### 自定义下拉框联动接口

返回 `[{value, text}]` 格式：
```java
@GetMapping("/getAreaList")
public List<Map<String, String>> getAreaList(@RequestParam(value = "pid", required = false) String pid) {
    // 不传pid返回省份，传pid返回下级市/区
}
```