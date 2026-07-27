# Online 表单集成积木报表参考

## extConfigJson 中的积木报表字段

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `reportPrintShow` | int | 0 | 关联积木报表打印（1=启用） |
| `reportPrintUrl` | string | "" | 积木报表预览URL（见下方「关联积木报表」说明） |

### 关联积木报表（打印功能）

Online 表单可关联积木报表实现打印功能，配置步骤：

**第一步：配置积木报表**
1. 在积木报表设计器中添加 **API 数据集**，API 地址固定格式：
```
{{ domainURL }}/online/cgform/api/data/{tableName}/queryByIdForJmReport?id=${id}&token=${token}&mock=true
```
- `{tableName}` 替换为 Online 表名
- `{{ domainURL }}` 是域名变量（固定不改），外网可替换为真实地址如 `http://localhost:8080/jeecg-boot`
- `?id=${id}&token=${token}&mock=true` 固定参数不要改
2. 点击「API解析」生成字段（**注意：需保证 Online 表中至少存在一条记录，否则字段解析不出来**）
3. 将字段拖拽到报表模板中

**第二步：配置 Online 表单**
1. 在积木报表点击预览，复制打开的链接（**不含 `?` 后的参数**）
2. 在 Online 表单的扩展配置中设置：
   - `reportPrintShow` = 1（启用打印）
   - `reportPrintUrl` = 积木报表预览链接
   - 本项目可用变量前缀：`{{ window._CONFIG['domianURL'] }}`

**打印入口位置：**
- 列表页面「更多」→「打印」
- 详情页面顶部「打印」按钮

**通过 API 自动关联积木报表（6步流程）：**

> 注意：积木报表的 API 基础路径通常是 `http://127.0.0.1:8080/jeecg-boot/jmreport`，与 Online 表单的 API 基础路径不同。
>
> **请求 Header 必须同时传 `token` 和 `X-Access-Token`**（值相同），只传一个会返回 401。每步必须确认前一步 `success=true` 后再执行下一步，不要用延迟代替结果校验。
>
> **批量创建报表时 code 冲突问题**：积木报表 code 默认按 `yyyyMMddHHmmss` 生成，同一秒内创建多个会报 `Duplicate entry for key 'uniq_jmreport_code'`。解决：Step1 传入自定义唯一 code（如毫秒时间戳），且批量时每个报表之间间隔 1 秒确保 code 不重复。
>
> **预览验证**：`POST /jmreport/show`，params 传 `{"id":"数据ID","token":"...","pageNo":1,"pageSize":10}`，返回 `success=true` 且包含字段数据即为正常。

**Step 1：创建报表记录**
```
POST /jmreport/save
```
body: `{"id":"","code":"","name":"报表名称","type":"984272091947253760","template":0}`
返回报表对象，取 `id` 作为 reportId。

**Step 2：保存空模板（必须！否则后续 get 返回 null）**
```
POST /jmreport/save
```
body 中 `designerObj.id` = reportId，`designerObj.name` = 报表名称，其余为空模板默认值：
```json
{"designerObj":{"id":"{reportId}","name":"报表名称","type":"984272091947253760","submitForm":0},
 "name":"sheet1","freeze":"A1","rows":{"len":100},"cols":{"len":50},
 "sheetId":"default","sheetName":"默认Sheet","sheetOrder":0,
 "excel_config_id":"","background":false,"area":false, ...}
```

**Step 3：解析 Online 表单字段**
```
POST /jmreport/executeSelectApi?token={token}&api={encodedApiUrl}&method=0&apiConvert=&paramArray={encodedParams}
```
- **请求方法**：必须用 `POST`（GET 返回 405）
- `api` = URL 编码后的 API 地址，**参数使用空值而非 `${id}` 占位符**：
  - 正确：`http://localhost:8080/jeecg-boot/online/cgform/api/data/{tableName}/queryById?id=&token=&mock=true`
  - 错误：`...queryById?id=${id}&token=${token}&mock=true`（服务端无法解析占位符）
- `paramArray` = URL 编码后的参数数组 JSON，**必须包含完整字段**：
```json
[
  {"paramName":"id","orderNum":1,"tableIndex":1,"id":"","paramValue":"","extJson":"","dictCode":"","_index":0,"_rowKey":30},
  {"paramName":"token","orderNum":2,"tableIndex":2,"id":"","paramValue":"","extJson":"","dictCode":"","_index":1,"_rowKey":31}
]
```
- 返回字段列表

**Step 4：检查数据集编码可用性**
```
GET /jmreport/dataCodeExist?reportId={reportId}&code={dataCode}
```

**Step 5：保存 API 数据源到报表**
```
POST /jmreport/saveDb
```
body 完整参数结构（**不可省略任何顶层字段**）：
```json
{
  "izSharedSource": 0,
  "jimuReportId": "{reportId}",
  "dbCode": "数据集编码",
  "dbChName": "数据集名称",
  "dbType": "1",
  "dbSource": "",
  "jsonData": "",
  "apiConvert": "",
  "isList": "1",
  "isPage": "0",
  "apiUrl": "{{ domainURL }}/online/cgform/api/data/{tableName}/queryByIdForJmReport?id=${id}&token=${token}&mock=true",
  "apiMethod": "0",
  "fieldList": [
    {"fieldName": "字段名", "fieldText": "字段名", "widgetType": "String", "isShow": true, "orderNum": 0, "tableIndex": 0, "extJson": "", "dictCode": ""}
  ],
  "paramList": [
    {"paramName": "id", "orderNum": 1, "tableIndex": 1, "id": "", "paramValue": "", "extJson": "", "dictCode": "", "_index": 0, "_rowKey": 133},
    {"paramName": "token", "orderNum": 2, "tableIndex": 2, "id": "", "paramValue": "", "extJson": "", "dictCode": "", "_index": 1, "_rowKey": 134}
  ]
}
```
> **注意**：`dbType` 必须为 `"1"`（不是 `"api"`），fieldList 每个字段必须包含 `isShow`、`tableIndex`、`extJson`、`dictCode` 完整属性，否则数据源保存不完整。

**Step 6：获取报表模板数据**
```
GET /jmreport/get/{reportId}?token={token}
```
获取当前报表的完整数据（含 `jsonStr` 模板结构），用于在 cells 中插入字段引用。

> **前提：Step 2 必须先保存空模板，否则此接口返回 result=null。**

**Step 7：写入字段引用并保存模板**
```
POST /jmreport/save
```
基于 Step 6 获取的数据，在 jsonStr 的 `rows.{行号}.cells.{列号}.text` 中插入字段引用，再保存。

> 字段引用格式：`#{数据集编码.字段名}`，如 `#{demo.customer_name}`

**模板样式规范：**
- 表头行（第 1 行）：白色字 + 蓝色底色 + 居中 + 边框，使用 style 索引 6
- 数据行（第 2 行）：默认字色 + 边框，使用 style 索引 0
- 列从第 1 列开始（第 0 列宽度缩小为 29 作为序号列）
- styles 数组定义：`[{边框}, ..., {白字+深蓝底+居中=index6}]`
- cells 引用：`{"text":"标题","style":6}` / `{"text":"#{dc.field}","style":0}`
- **rows 中不能包含空行**（如 `"0": {}`），否则预览报错 `cellJson is null`，只放有 cells 的行

```json
"styles": [
  {"border":{"bottom":["thin","#000"],"top":["thin","#000"],"left":["thin","#000"],"right":["thin","#000"]}},
  ...
  {"border":{"bottom":["thin","#000"],"top":["thin","#000"],"left":["thin","#000"],"right":["thin","#000"]},"color":"#ffffff","bgcolor":"#4371c6","align":"center"}
]
"rows": {
  "1": {"cells": {"1": {"text":"标题","style":6}, "2": {"text":"字段2","style":6}}},
  "2": {"cells": {"1": {"text":"#{dc.field1}","style":0}, "2": {"text":"#{dc.field2}","style":0}}}
}
"cols": {"0": {"width": 29}, "len": 51}
```

**Step 8：将积木报表关联到 Online 表单**
```
PUT /online/cgform/head/edit
```
body 只需传 `id`（Online 表单 headId）和 `extConfigJson`（更新 reportPrintShow + reportPrintUrl）：
```json
{
  "id": "{headId}",
  "extConfigJson": "{\"reportPrintShow\":1,\"reportPrintUrl\":\"{{ window._CONFIG['domianURL'] }}/jmreport/view/{reportId}\",...}"
}
```
- `reportPrintShow` 设为 `1`
- `reportPrintUrl` 格式（**固定格式，不可修改变量前缀**）：`{{ window._CONFIG['domianURL'] }}/jmreport/view/{积木报表ID}`
  - 示例：`{{ window._CONFIG['domianURL'] }}/jmreport/view/1198447253269471232`
  - `{{ window._CONFIG['domianURL'] }}` 是前端运行时变量，保存时原样存储（不替换为实际地址）
  - `{积木报表ID}` 替换为 Step 1 创建报表返回的 `reportId`
- 其他 extConfigJson 字段保持原值

> **注意：** 使用 `head/edit` 接口只更新 head 级别属性，不影响字段配置，比 `editAll` 更轻量。
