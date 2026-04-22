# 查询配置与顶层配置字段

积木报表查询条件配置（fieldList/paramList）和 jsonStr 顶层字段完整参考。

---

## 0. paramList 快速速查（最常用）

### SQL 条件表达式

```sql
SELECT ... FROM t WHERE 1=1
<#if isNotEmpty(emp_name)> AND emp_name LIKE CONCAT('%','${emp_name}','%')</#if>
<#if isNotEmpty(hire_date_begin)> AND hire_date >= '${hire_date_begin}'</#if>
<#if isNotEmpty(hire_date_end)> AND hire_date <= '${hire_date_end}'</#if>
```

- `isNotEmpty(x)` — JimuReport 自定义函数，null 和 `""` 均返回 false（**必须用此函数，不能用 `?has_content` 或 `??`**）
- `${param}` — 用户查询参数；`#{sysUserCode}` — 系统变量，两者不可混用
- 解析字段时用不含 FreeMarker 的纯 SQL（`LIMIT 1`），避免解析失败

### paramList 字段值对照（按控件类型速查）

| 控件 | widgetType | searchMode | searchFormat | dictCode |
|------|-----------|-----------|--------------|---------|
| 文本输入框 | `"String"` | `1` | `""` | 空 |
| 模糊查询输入框 | `"String"` | `5` | `""` | 空 |
| 日期选择 | `"date"` | `1` | `"yyyy-MM-dd"` | 空 |
| 日期时间 | `"date"` | `1` | `"yyyy-MM-dd HH:mm:ss"` | 空 |
| 年月 | `"date"` | `1` | `"yyyy-MM"` | 空 |
| 日期范围 | `"date"` | `2` | `"yyyy-MM-dd"` | 空 |
| **下拉单选** | `"String"` | **`4`** | `""` | 字典编码/SQL/API |
| **下拉多选** | `"String"` | **`3`** | `""` | 字典编码/SQL/API |

> **注意：参数不支持范围查询和模糊查询。**
> 日期范围须拆成两个独立参数（`_begin` / `_end`）；模糊匹配在 SQL 中手写 `LIKE '%${x}%'`。

---

## 6. 查询配置

查询条件通过数据集的 `fieldList` 和 `paramList` 中的字段属性配置。

**参考文档：**
- https://help.jimureport.com/queryCriteria/api — API查询条件
- https://help.jimureport.com/queryCriteria/dictionary — 字典下拉
- https://help.jimureport.com/queryCriteria/sql — SQL动态条件
- https://help.jimureport.com/queryCriteria/apiByTime — 时间查询
- https://help.jimureport.com/queryCriteria/apiRange — 范围查询
- https://help.jimureport.com/queryCriteria/apiInterface — API接口参数接收

### 6.1 参数语法

| 语法 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `${paramName}` | 用户参数 | 需在报表参数/SQL中声明 | `${id}`, `${name}` |
| `#{sysVar}` | 系统变量 | 无需声明，自动解析 | `#{sysUserCode}` |

**SQL 示例：** `select * from demo where id='${id}' and create_by='#{sysUserCode}'`
**API 示例：** `http://host/api/getData?name=${name}&date=${date}`

### 系统变量

| 变量 | 说明 |
|------|------|
| `#{sysUserCode}` | 当前登录用户名 |
| `#{sysOrgCode}` | 当前登录用户部门编码 |
| `#{sysDate}` | 当前系统日期 |
| `#{sysDateTime}` | 当前系统日期时间 |
| `#{domainURL}` | 系统域名地址 |

### 6.2 查询控件配置（字段属性）

查询条件通过 `saveDb` 接口的 `fieldList` 或 `paramList` 中的字段属性控制：

| 字段属性 | 类型 | 说明 | 取值 |
|---------|------|------|------|
| `searchFlag` | Integer | 是否启用查询 | `1`=启用, `0`/null=不启用 |
| `searchMode` | Integer | 查询模式 | `1`=单条件, `2`=范围查询, `3`=多选 |
| `searchValue` | String | 查询默认值 | 静态值/表达式/系统变量 |
| `dictCode` | String | 字典编码（下拉数据源） | 字典编码/SQL/API地址 |
| `searchFormat` | String | 日期格式 | `yyyy-MM-dd`, `yyyy-MM-dd HH:mm:ss` |
| `widgetType` | String | 控件类型 | `String`, `Number`, `date`, `datetime` |
| `extJson` | String | 扩展配置JSON | `{"selectSearchPageSize":20}`, `{"loadTree":"..."}`, `{"required":true}` |

### searchMode 查询模式值

| searchMode | 类型 | 说明 |
|-----------|------|------|
| `1` | 文本输入 | 默认输入框 |
| `2` | 范围查询 | 日期/数值范围，自动生成 `_begin`/`_end` 参数 |
| `3` | 下拉多选 | 多选下拉框，需配合 dictCode |
| `4` | 下拉单选 | 单选下拉框，需配合 dictCode |
| `5` | 模糊查询 | 模糊匹配输入框 |
| `6` | 下拉树 | 树形下拉，需配合 extJson.loadTree |
| `7` | 自定义下拉框 | JS增强自定义下拉，需配合 JS 代码 |

### 查询控件类型对照

| 控件效果 | searchFlag | searchMode | dictCode | widgetType |
|---------|-----------|-----------|----------|-----------|
| 文本输入框 | 1 | 1 | 空 | String |
| 模糊查询输入框 | 1 | 5 | 空 | String |
| 下拉单选 | 1 | 4 | 字典编码/SQL/API | String |
| 下拉多选 | 1 | 3 | 字典编码/SQL/API | String |
| 范围查询（日期） | 1 | 2 | 空 | date |
| 范围查询（数值） | 1 | 2 | 空 | Number |
| 时间选择 | 1 | 1 | 空 | date/datetime |
| 下拉树 | 1 | 6 | 空 | String |
| 自定义下拉框 | 1 | 7 | 空 | String |

### 6.3 下拉数据源配置（dictCode）

三种方式，通过 `dictCode` 字段配置：

**系统字典：** 直接填字典编码（如 `sex`）

**SQL字典：**
```sql
SELECT username AS value, realname AS text FROM sys_user
```
> 注意：必须别名为 `value` 和 `text`，仅支持SQL数据源

**API字典：**
```
/jmreport/test/getDictSex?createBy=#{sysUserCode}
```
返回格式：`[{"text":"男","value":"1"},{"text":"女","value":"2"}]`

API字典支持（v1.7.9+）：
- `dictCode` — 字典编码
- `pageNo`/`pageSize` — 分页（默认10条）
- `searchText` — 搜索关键字
- `queryAll=true` — 返回全部数据

### 6.4 时间查询

将 `widgetType` 设为 `date` 或 `datetime`，日期以字符串格式传递。

**支持的日期格式：**

| 格式 | 示例 |
|------|------|
| `yyyy-MM-dd HH:mm:ss` | 2021-07-29 12:11:10 |
| `yyyy-MM-dd` | 2021-07-29 |
| `yyyy-MM` | 2021-07 |
| `yyyy` | 2021 |

**dateStr 默认值函数：**

| 表达式 | 结果 |
|--------|------|
| `=dateStr()` | 当前日期时间 |
| `=dateStr('yyyy-MM-dd')` | 当前日期 |
| `=dateStr('MM', 2)` | 当前月+2 |
| `=dateStr('dd', -1)` | 昨天 |
| `=dateStr('yyyy-MM', -1)` | 上个月 |

### 6.5 范围查询

`searchMode=2` 时启用范围查询。系统自动生成 `字段名_begin` 和 `字段名_end` 两个参数。

**默认值用管道符 `|` 分隔起止值：**

| 场景 | searchValue |
|------|------------|
| 数字范围 | `16\|22` |
| 本月1日到今天 | `=concat(string.substring(dateStr('yyyy-MM-dd'),0,8),'01')\|=dateStr('yyyy-MM-dd')` |
| 最近10天 | `=concat(dateStr('yyyy-MM-dd',-10),' 00:00:00')\|=dateStr('yyyy-MM-dd HH:mm:ss')` |

**API 后端接收：**
```java
@GetMapping("/getData")
public JSONObject getData(
    @RequestParam(name = "riqi_begin", required = false) String riqiBegin,
    @RequestParam(name = "riqi_end", required = false) String riqiEnd) { ... }
```

### 6.6 SQL条件表达式（FreeMarker语法）

```sql
select id, name, age from demo where create_by = '#{sysUserCode}'
<#if isNotEmpty(age)> and age = '${age}'</#if>
<#if isNotEmpty(name)> and name = '${name}'</#if>
```

**LIKE模糊查询：**
```sql
select * from demo where 1=1
<#if name?? && name?length gt 0>
  and name like concat('%', '${name}', '%')
</#if>
```

**DaoFormat 函数：**

| 函数 | 用途 | 示例 |
|------|------|------|
| `DaoFormat.in('${sex}')` | 字符串IN | `male,female` → `'male','female'` |
| `DaoFormat.inNumber('${age}')` | 数字IN | `21,22` → `21,22` |
| `DaoFormat.concat('${a}', ' 00:00:00')` | 拼接 | — |

### 6.7 下拉树控件

配置 `extJson`：`{"loadTree": "{{ domainURL }}/sys/user/treeTest"}`

接口返回格式：
```json
[
  {"id": "001", "pid": "", "value": "A01", "title": "节点1", "izLeaf": 0},
  {"id": "002", "pid": "001", "value": "A02", "title": "子节点1", "izLeaf": 1}
]
```

### 6.8 JS增强 API

| 方法 | 用途 |
|------|------|
| `updateSelectOptions(dbCode, fieldName, options)` | 动态更新下拉选项 |
| `onSearchFormChange(dbCode, fieldName, callback)` | 监听控件值变化 |
| `updateSearchFormValue(dbCode, fieldName, value)` | 设置控件初始值 |
| `getSelectOptions(dbCode, fieldName)` | 获取当前下拉选项 |
| `notLoadDataWhenShow()` | 预览时不自动加载数据 |

**三级联动下拉示例：**
```javascript
function init(){
  $http.metaGet('<backend_url>/ces/ai/customSelect')
    .then(res => { this.updateSelectOptions('pca', 'pro', res.data) })
  this.onSearchFormChange('pca', 'pro', (value) => {
    $http.metaGet('<backend_url>/ces/ai/customSelect', {pid: value})
      .then(res => { this.updateSelectOptions('pca', 'city', res.data) })
  })
  this.onSearchFormChange('pca', 'city', (value) => {
    $http.metaGet('<backend_url>/ces/ai/customSelect', {pid: value})
      .then(res => { this.updateSelectOptions('pca', 'area', res.data) })
  })
}
```

### 6.9 API 参数传递

**URL参数传递：** 预览时通过URL传参覆盖默认值
```
http://localhost:8085/jmreport/view/{reportId}?name=scott&age=25
```

**后端接收：**
- GET: `@RequestParam(name="name", required=false) String name`
- POST Body: `@RequestBody JSONObject json` → `json.getString("name")`

### 6.10 querySetting

> **注意：** `querySetting` 在 save 接口的 JSON 中是 **字符串**（JSON.stringify 后的值），不是对象。

```json
"querySetting": "{\"izOpenQueryBar\":true,\"izDefaultQuery\":true}"
```

| 设置 | 默认值 | 说明 |
|------|--------|------|
| `izDefaultQuery` | true | 是否自动执行查询（页面加载后立即请求数据） |
| `izOpenQueryBar` | false | 是否默认展开查询栏（有查询条件时建议设为 true） |

### 6.11 fieldList 查询条件配置示例

在 `saveDb` 时通过 fieldList 配置查询条件：

```python
field_list = [
    # 普通字段（不查询）
    {"fieldName": "id", "fieldText": "ID", "widgetType": "String", "orderNum": 0},

    # 文本输入查询
    {"fieldName": "name", "fieldText": "姓名", "widgetType": "String", "orderNum": 1,
     "searchFlag": 1, "searchMode": 1},

    # 下拉单选（字典）
    {"fieldName": "sex", "fieldText": "性别", "widgetType": "String", "orderNum": 2,
     "searchFlag": 1, "searchMode": 4, "dictCode": "sex"},

    # 下拉多选（API）
    {"fieldName": "department", "fieldText": "部门", "widgetType": "String", "orderNum": 3,
     "searchFlag": 1, "searchMode": 3, "dictCode": "/jmreport/test/getDept"},

    # 日期范围查询
    {"fieldName": "create_time", "fieldText": "创建时间", "widgetType": "date", "orderNum": 4,
     "searchFlag": 1, "searchMode": 2, "searchFormat": "yyyy-MM-dd",
     "searchValue": "=dateStr('yyyy-MM-dd',-30)|=dateStr('yyyy-MM-dd')"},

    # 普通数据字段
    {"fieldName": "salary", "fieldText": "薪水", "widgetType": "Number", "orderNum": 5}
]
```

---

## 8. 顶层配置字段

| 字段 | 说明 |
|------|------|
| `loopBlockList` | 循环块定义（含 `loopTime` 分栏次数） |
| `zonedEditionList` | 分版区域定义 |
| `fixedPrintHeadRows` | 固定打印表头 |
| `fixedPrintTailRows` | 固定打印表尾 |
| `groupField` | 分组字段 |
| `isGroup` | 是否启用分组 |
| `submitHandlers` | 填报提交处理器 |
| `background` | 背景图配置 |
| `imgList` | 图片列表 |
| `chartList` | 图表列表 |
| `barcodeList` | 条码列表 |
| `qrcodeList` | 二维码列表 |
| `displayConfig` | 二维码/条码显示配置 |
| `dicts` | 引用的字典编码列表 |
| `printConfig` | 打印配置（纸张/方向/边距） |
| `merges` | 合并单元格列表（如 `"A2:H2"`），**必须同时在 cell 上设置 `merge` 属性** |
| `querySetting` | 查询设置 |
| `pyGroupEngine` | 是否使用Python分组引擎 |
