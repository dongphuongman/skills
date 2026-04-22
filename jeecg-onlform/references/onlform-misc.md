# Online 表单杂项配置参考

## head 级别配置属性补充

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `scroll` | int | 1 | 列表是否只读。`1`=只读列表（有横向滚动），`0`=可编辑列表（列表中可直接编辑字段） |

### extConfigJson 完整字段清单

> **适用范围：** 主表（tableType=2）和单表（tableType=1）拥有完整扩展配置。一对多子表（tableType=3, relationType=0）**没有扩展配置**。一对一子表（tableType=3, relationType=1）**仅有 `tableFixedAction`/`tableFixedActionType`（固定操作列）、`canResizeColumn`（列宽拖动）、`formLabelLengthShow` + `formLabelLength`**（表单Label长度设置）。
>
> **联动约束（源码 ExtendConfigModal.vue）：**
> - `modelFullscreen=1` 时 `modalMinWidth` 自动禁用
> - `joinQuery=1` 时校验：ERP/innerTable/单表/子表/树表自动重置为 0
> - `reportPrintShow=1` 时 `reportPrintUrl` 必填，且必须替换 `{积木报表ID}` 为真实 ID
> - `formLabelLengthShow=0` 时 `formLabelLength` 自动置空
> - `isDesForm`（集成设计表单）在 vue3 中已注释，**不可用**；且 erp 风格不支持对接设计表单

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `reportPrintShow` | int | 0 | 关联积木报表打印（1=启用） |
| `reportPrintUrl` | string | "" | 积木报表预览URL（见下方「关联积木报表」说明） |
| `joinQuery` | int | 0 | 联合查询（1=启用，**仅主表(tableType=2) + normal/tab 风格支持**。ERP/innerTable/单表/子表/树表均不支持，源码会自动重置为0） |
| `modelFullscreen` | int | 0 | 弹窗默认全屏（1=启用） |
| `modalMinWidth` | string/int | "" | 弹窗最小宽度（px），**modelFullscreen=1 时自动禁用** |
| `commentStatus` | int | 0 | 开启评论（1=启用，编辑/详情页面右侧显示评论区，开启后默认全屏） |
| `tableFixedAction` | int | 1 | 固定操作列（1=启用） |
| `tableFixedActionType` | string | "right" | 操作列固定位置（`"right"` / `"left"`） |
| `canResizeColumn` | int | 0 | 开启拖动列宽（1=启用） |
| `formLabelLengthShow` | int | 0 | 自定义 label 长度开关（1=启用） |
| `formLabelLength` | int/null | null | 表单 label 长度 |
| `enableExternalLink` | int | 0 | 启用外部链接（1=启用） |
| `externalLinkActions` | string | "add,edit,detail" | 外部链接支持的操作 |

### 已有表后续开启联合查询

如果主子表创建时未启用联合查询，后续可通过 `PUT /online/cgform/head/edit` 修改 extConfigJson 开启：

```bash
# 1. 查询当前 extConfigJson
GET /online/cgform/head/list?tableName={表名}&copyType=0&pageNo=1&pageSize=1
# 从 result.records[0].extConfigJson 获取当前值

# 2. 修改 joinQuery 为 1，其余字段保持不变
PUT /online/cgform/head/edit
{
  "id": "{headId}",
  "extConfigJson": "{...\"joinQuery\":1,...}"
}
```

> **注意：** 必须保留 extConfigJson 中的其他字段原值，只修改 `joinQuery`。如果传空或缺少字段会导致配置丢失。

### 关联积木报表（打印功能）

Online 表单可关联积木报表实现打印功能，配置步骤：

**第一步：配置积木报表**
1. 在积木报表设计器中添加 **API 数据集**，API 地址固定格式：
```
{{ domainURL }}/online/cgform/api/data/{tableName}/queryById?id=${id}&token=${token}&mock=true
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
  "apiUrl": "{{ domainURL }}/online/cgform/api/data/{tableName}/queryById?id=${id}&token=${token}&mock=true",
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
- `reportPrintUrl` 格式：`{{ window._CONFIG['domianURL'] }}/jmreport/view/{积木报表ID}`
- 其他 extConfigJson 字段保持原值

> **注意：** 使用 `head/edit` 接口只更新 head 级别属性，不影响字段配置，比 `editAll` 更轻量。

---

## 表单布局 (formTemplate)

| formTemplate | 说明 |
|-------------|------|
| `"1"` | 一列布局（默认，字段独占一行） |
| `"2"` | 两列布局（字段并排显示） |
| `"3"` | 三列布局 |
| `"4"` | 四列布局 |

在 JSON 配置的表级别设置：`"formTemplate": "2"`

> **默认使用一列布局（`"1"`），除非用户特别指明多列。**

> 注意：
> - 富文本(umeditor)和Markdown(markdown)控件在多列布局中可独占一行，通过 fieldExtendJson `{"isOneRow":true}` 设置。
> - **一对一子表的 formTemplate 继承主表**，不需要单独设置。

---

## 主子表创建流程

使用 `scripts/onlform_creator.py` 创建主子表，只需在 JSON 配置的 `tables` 数组中按顺序定义主表和子表即可。脚本会自动依次创建并同步数据库。

### 关键配置要点

1. **主表**：`tableType=2`，`subTableStr` 填子表名（多个用逗号分隔）
2. **子表**：`tableType=3`，必须设置：
   - `relationType`(0=一对多/1=一对一)
   - `tabOrderNum`(排序号)
   - **`mainTable`**(主表表名)
   - **`mainField`**(主表关联字段，通常是 `id`)
3. **子表外键字段（CRITICAL）**：子表必须包含一个**隐藏的外键字段**，在**字段级别**同时设置 `mainTable`/`mainField`，且 `isShowForm=0, isShowList=0`。**缺少此字段会导致主子表关联完全失效**（子表数据插入后无法关联到主表记录，外键列为空）。
   - `onlform_creator.py` 已升级为**自动注入**此字段（当 `tableType=3` 且 `mainTable` 有值时），无需手动配置
   - 字段名默认为 `{mainTable}_id`，如 `demo_ms_main_id`
   - 若手动在 `fields` 中配置了带 `mainTable` 属性的字段，脚本会跳过自动注入
4. **tables 数组顺序**：主表在前，子表在后（脚本按顺序创建）
5. **启用联合查询**：主表 `extConfigJson` 中设置 `joinQuery=1`，仅 normal/tab 风格支持（ERP/innerTable 不支持）

> **重要**：子表 head 层的 `mainTable`/`mainField` 是元数据标记，**不等于**外键约束。真正驱动主子表数据关联的是**字段级别的外键字段**（第3点）。两者缺一不可。

### 启用联合查询的主子表 JSON 示例

```json
{
  "action": "create",
  "tables": [
    {
      "tableName": "demo_join_main",
      "tableTxt": "联合查询主表",
      "tableType": 2,
      "themeTemplate": "normal",
      "subTableStr": "demo_join_school,demo_join_info",
      "extConfigJson": "{\"joinQuery\":1,\"reportPrintShow\":0,\"reportPrintUrl\":\"\",\"modelFullscreen\":0,\"modalMinWidth\":\"\",\"commentStatus\":0}",
      "fields": [
        {"dbFieldName": "name", "dbFieldTxt": "名称", "fieldShowType": "text", "dbType": "string", "dbLength": 100},
        {"dbFieldName": "age", "dbFieldTxt": "年龄", "fieldShowType": "text", "dbType": "int", "dbLength": 3}
      ]
    },
    {
      "tableName": "demo_join_school",
      "tableTxt": "学校信息(一对多)",
      "tableType": 3,
      "relationType": 0,
      "tabOrderNum": 1,
      "mainTable": "demo_join_main",
      "mainField": "id",
      "fields": [
        {"dbFieldName": "main_id", "dbFieldTxt": "主表ID", "fieldShowType": "text", "dbType": "string", "dbLength": 36, "mainTable": "demo_join_main", "mainField": "id", "isShowForm": "0", "isShowList": "0"},
        {"dbFieldName": "school", "dbFieldTxt": "学校", "fieldShowType": "text", "dbType": "string", "dbLength": 200},
        {"dbFieldName": "phone", "dbFieldTxt": "联系方式", "fieldShowType": "text", "dbType": "string", "dbLength": 50}
      ]
    },
    {
      "tableName": "demo_join_info",
      "tableTxt": "个人信息(一对一)",
      "tableType": 3,
      "relationType": 1,
      "tabOrderNum": 2,
      "mainTable": "demo_join_main",
      "mainField": "id",
      "fields": [
        {"dbFieldName": "main_id", "dbFieldTxt": "主表ID", "fieldShowType": "text", "dbType": "string", "dbLength": 36, "mainTable": "demo_join_main", "mainField": "id", "isShowForm": "0", "isShowList": "0"},
        {"dbFieldName": "nation", "dbFieldTxt": "民族", "fieldShowType": "text", "dbType": "string", "dbLength": 50},
        {"dbFieldName": "place", "dbFieldTxt": "籍贯", "fieldShowType": "text", "dbType": "string", "dbLength": 100}
      ]
    }
  ]
}
```

> **联合查询数据权限配置**详见 `onlform-auth.md` 的「联合查询数据权限配置」章节。

完整 JSON 配置示例见上方 Step 6.2 中的「主子表创建示例」。

### 主题模板说明

| themeTemplate | 组件名(component_name) | 子表展示方式 | 行选择 | 限制 |
|--------------|----------------------|-------------|--------|------|
| `normal` | `OnlineAutoList` | 弹窗中展示 | 多选(checkbox) | 无 |
| `tab` | `OnlCgformTabList` | 弹窗中TAB页签 | 多选(checkbox) | 无 |
| `erp` | `CgformErpList` | 主表下方TAB页签 | **单选(radio)** | 不支持联合查询 |
| `innerTable` | `OnlCgformInnerTableList` | 行展开内嵌TAB | 多选(checkbox) | 不支持联合查询 |

**树表组件名**：`DefaultOnlineList`（不走 themeTemplate，单独路由）
- 树表不支持导入功能
- 子节点懒加载，通过 pidField 父子关联

> 注意：`themeTemplate` 仅主表（tableType=2）可设置，单表（tableType=1）该字段禁用。
> 组件名用于菜单缓存配置（`component_name` 字段）。

---

## 树表创建

使用 `scripts/onlform_creator.py` 创建树表，在表配置中设置 `isTree: "Y"` 及相关树字段即可。

### 关键配置要点

1. `tableType=1`，`isTree="Y"`
2. 必须设置 `treeParentIdField`(父ID字段)、`treeIdField`(是否有子节点字段)、`treeFieldname`(树展示字段)
3. `pid` 字段**需要在表单中显示**（`isShowForm="1"`），列表中可隐藏
4. `has_child` 字段隐藏（表单和列表都不显示）
5. `has_child` 是 string 类型，值为 `"1"`(有子节点) / `"0"`(无子节点)

完整 JSON 配置示例见上方 Step 6.2 中的「树表创建示例」。

## 树表数据插入顺序

造树表测试数据时，**必须先插入父节点，拿到返回的 id，再作为子节点的 pid 插入**。不能一次性批量插入，否则 pid 无法正确关联。

```python
# 先插一级（pid 传空字符串，API 会自动存为 "0"）
resp = api_post({"name": "总公司", "pid": "", "has_child": "1", ...})
id1 = resp['result']  # POST 返回记录 ID
# 再插二级（pid 指向一级 id）
resp = api_post({"name": "技术部", "pid": id1, "has_child": "1", ...})
id11 = resp['result']
# 最后插三级（pid 指向二级 id）
api_post({"name": "前端组", "pid": id11, "has_child": "0", ...})
```

- 根节点 `pid` 传空字符串 `""`（**API 实际存储为字符 `"0"`，数据库中根节点 pid='0'，不是空串也不是 NULL**）
- 有子节点的 `has_child` 设为 `"1"`，叶子节点设为 `"0"`
- **pid 和 has_child 字段的 `isShowForm` 必须为 `1`**（设为 0 会导致 API 忽略这两个字段值，树结构无法建立）
- 如果直接用 SQL 造数据，根节点 pid 必须写 `'0'`（不是 `''` 或 `NULL`），否则前端 `hasQuery=false` 查不到

---

## Online 表单走流程配置

> **【强制要求】Online 表单如需对接 BPM 流程审批，必须按本章节要求配置 `bpm_status` 字段。配置错误会导致流程无法关联、状态无法显示等问题。**

### bpm_status 字段配置（必须严格按此配置）

### bpm_status 字段配置

```json
{
  "dbFieldName": "bpm_status",
  "dbFieldTxt": "流程状态",
  "fieldShowType": "list",
  "dbType": "string",
  "dbLength": 32,
  "fieldMustInput": "0",
  "isQuery": "0",
  "isShowForm": "0",
  "isShowList": "1",
  "dictField": "bpm_status"
}
```

**关键配置说明：**

| 属性 | 值 | 说明 |
|------|-----|------|
| `fieldShowType` | `list` | 下拉列表，使用系统字典显示状态文本 |
| `dictField` | `bpm_status` | 系统内置流程状态字典（1=未发起, 2=进行中, 3=已完成, 4=已作废） |
| `isShowForm` | `0` | 表单中隐藏（流程引擎自动维护，用户不可编辑） |
| `isShowList` | `1` | 列表中显示（方便查看当前流程状态） |

### 流程关联

创建流程后，通过 `bpmn_creator.py` 的 `formLink` 配置关联 Online 表单：

```json
{
  "formLink": {
    "formType": "1",
    "relationCode": "onl_{tableName}",
    "formTableName": "{tableName}",
    "flowStatusCol": "bpm_status",
    "titleExp": "标题表达式-${字段名}"
  }
}
```

> **重要：** Online 表单的 `relationCode` 格式为 `onl_{表名}`（脚本会自动补全前缀），`formType` 必须为 `"1"`。

### JSON 配置快捷方式

**方式一：使用 `bpmForm: true` 自动添加（推荐）**

在 `onlform_creator.py` 的 JSON 配置中，设置 `bpmForm: true` 会自动添加正确的 bpm_status 字段：

```json
{
  "action": "create",
  "tables": [{
    "tableName": "my_apply",
    "tableTxt": "我的申请单",
    "tableType": 1,
    "bpmForm": true,
    "fields": [
      {"dbFieldName": "title", "dbFieldTxt": "标题", "fieldShowType": "text", "dbType": "string", "dbLength": 200, "fieldMustInput": "1"}
    ]
  }]
}
```

**方式二：手动添加（不推荐，容易配置错误）**

```json
{
  "action": "create",
  "tables": [{
    "tableName": "my_apply",
    "tableTxt": "我的申请单",
    "tableType": 1,
    "fields": [
      {"dbFieldName": "title", "dbFieldTxt": "标题", "fieldShowType": "text", "dbType": "string", "dbLength": 200, "fieldMustInput": "1"},
      {"dbFieldName": "bpm_status", "dbFieldTxt": "流程状态", "fieldShowType": "list", "dbType": "string", "dbLength": 32, "isShowForm": "0", "isShowList": "1", "dictField": "bpm_status"}
    ]
  }]
}
```

> **bpm_status 配置要求**：必须严格按 `fieldShowType: "list"` + `dictField: "bpm_status"` 配置，使用 `bpmForm: true` 可避免配置错误。

---

## 主键策略 (idType)

| idType | 说明 |
|--------|------|
| `UUID` | UUID 随机字符串（默认，推荐） |
| `NATIVE` | 数据库自增（MySQL auto_increment） |
| `SEQUENCE` | 序列（Oracle 使用） |

---

## sel_user / sel_depart 存储字段

通过 fieldExtendJson 配置 `{"store":"fieldName","text":"displayField","multiSelect":true}` 可自定义存储和显示字段。

**用户组件可选存储字段：**
`id`、`username`、`realname`、`birthday`、`sex`、`email`、`phone`、`telephone`

**部门组件可选存储字段：**
`id`、`departName`、`departNameEn`、`departNameAbbr`、`description`、`orgCode`、`mobile`、`fax`、`address`、`memo`

> 注意：存储字段值必须唯一。仅单表支持自定义存储字段，一对多子表暂不支持。

---

## Popup 弹窗说明

**Popup 控件依赖 Online 报表（cgreport）**，dictTable 填写的是 **Online 报表的编码**（不是积木报表、不是普通数据库表名）。

**Online 报表 API：**

| 操作 | 方法 | URL | 说明 |
|------|------|-----|------|
| 报表列表 | GET | `/online/cgreport/head/list?column=createTime&order=desc&pageNo=1&pageSize=10` | 返回 `code`（编码）和 `id`（ID） |
| 报表列定义 | GET | `/online/cgreport/api/getRpColumns/{code}` | 通过**编码**查列 |
| 报表数据 | GET | `/online/cgreport/api/getColumnsAndData/{id}?pageNo=1&pageSize=10&onlRepUrlParamStr=` | 通过**ID**查数据，返回 `result.data.records` |
| **创建报表** | POST | `/online/cgreport/head/add` | 创建 Online 报表（popup/popup_dict 前置依赖） |

**创建 Online 报表 API（POST `/online/cgreport/head/add`）：**

```json
{
  "head": {
    "code": "report_code",
    "name": "报表名称",
    "cgrSql": "select * from table_name"
  },
  "params": [],
  "items": [
    {
      "fieldName": "id",
      "fieldTxt": "id",
      "fieldType": "String",
      "isShow": 1,
      "orderNum": 0
    },
    {
      "fieldName": "name",
      "fieldTxt": "名称",
      "fieldType": "String",
      "isShow": 1,
      "orderNum": 1
    }
  ]
}
```

**items 字段说明：**

| 字段 | 说明 |
|------|------|
| `fieldName` | SQL 结果列名 |
| `fieldTxt` | 显示文本 |
| `fieldType` | 类型（`String`/`Integer`/`Date` 等） |
| `isShow` | 列显示（1=显示） |
| `orderNum` | 排序号（从 0 开始） |
| `isSearch` | 是否可查询 |
| `searchMode` | 查询模式（`single`/`range`） |
| `dictCode` | 字典编码 |
| `fieldHref` | 字段超链接 |
| `fieldWidth` | 列宽 |
| `replaceVal` | 取值表达式 |
| `groupTitle` | 分组标题 |
| `isTotal` | 是否合计 |

> **使用流程**：先通过 `head/add` 创建 Online 报表 → 获得报表 `code` → 在 popup/popup_dict 的 `dictTable` 中填入该 `code`

> **注意：** Online 报表有两个标识：`code`（编码，如 `report_user`）和 `id`（如 `6c7f59741c814347905a938f06ee003c`）。popup 表单配置的 dictTable 填 **code**，但查询报表数据用 **id**。需先通过 `head/list` 查到 id。

配置步骤：
1. 先创建一个 **Online 报表**（如编码 `report_user`）
2. Online 表单中选择 popup 控件
3. **dictTable**：填 Online 报表编码（如 `report_user`）
4. **dictField**：填 Online 报表中的字段名（多个逗号隔开，如 `username,realname`）
5. **dictText**：填本表中接收回填的字段名（多个逗号隔开，如 `popup_val,popup_back`）
6. dictField 和 dictText **成对映射**：报表字段值 → 本表字段

**popup_dict 也依赖 Online 报表**，与 popup 的区别：
- **popup**：可回填到本表**多个字段**（dictField/dictText 成对映射多个字段）
- **popup_dict**：只回填到**当前字段**（dictField 填值字段，dictText 填显示字段）
- 两者都支持单选/多选（通过 fieldExtendJson `{"popupMulti":false}` 设为单选，**默认 true=多选**）
- 两者的 dictTable 都填 **Online 报表编码**（不是数据库表名）

---

## 视图功能

Online 表单支持生成多个**视图**，每个视图可独立配置字段显隐、控件类型等，不影响原表和其他视图。

### 使用场景
1. **一对多子表独立配置**：生成子表视图，单独修改子表的字段显示和控件
2. **流程节点差异展示**：不同审批节点显示不同字段（如节点1显示前两个字段，节点2显示后两个字段）

### 视图 API

| 操作 | 方法 | URL |
|------|------|-----|
| 生成视图 | POST | `/online/cgform/head/copyOnline?code={headId}` |
| 视图列表 | GET | `/online/cgform/head/list?column=createTime&order=desc&pageNo=1&pageSize=10&copyType=1&physicId={headId}` |
| 删除视图 | DELETE | `/online/cgform/head/delete?id={viewHeadId}` |

- 每次调用 `copyOnline` 会生成一个新视图，视图表名格式 `{原表名}${序号}`（如 `meeting_register$1`），不是 `lv_` 前缀
- 视图有独立的 `id`（headId），`physicId` 指向原表的 headId
- 视图与原表**共享数据**，可独立修改字段显隐、控件类型、查询配置等，不影响原表
- 编辑视图字段时用**视图自己的 headId**，通过 `onlform_creator.py` 的 edit 操作（内部调用 editAll API）
- 修改视图 head 级配置（如 formTemplate）用 `PUT /online/cgform/head/edit`，传视图的 headId
- 视图有独立的配置地址（`/online/cgformList/{视图headId}`），可单独配置菜单
- 视图列表通过 `copyType=1&physicId={原表headId}` 过滤
- 视图管理页面还支持配置自定义按钮、JS增强、SQL增强、Java增强

### 视图操作完整流程（已验证）

#### Step 1: 生成视图

```bash
# 可多次调用生成多个视图，每次序号自增
POST /online/cgform/head/copyOnline?code={原表headId}
```

#### Step 2: 查询视图列表获取视图 headId

```bash
GET /online/cgform/head/list?copyType=1&physicId={原表headId}&pageNo=1&pageSize=10
# 返回 records 中每个视图的 id(headId)、tableName(如 xxx$1)
```

#### Step 3: 修改视图 head 级配置（如表单列数）

```bash
PUT /online/cgform/head/edit
{"id":"{视图headId}","formTemplate":"2"}
# formTemplate: "1"=一列, "2"=两列, "3"=三列, "4"=四列
```

#### Step 4: 修改视图字段配置（如查询字段）

使用 `onlform_creator.py` 的 edit 操作，**headId 填视图自己的 ID**：

```json
{
  "action": "edit",
  "headId": "{视图headId}",
  "modifyFields": [
    {"dbFieldName": "meeting_no", "isQuery": "0"},
    {"dbFieldName": "meeting_subject", "isQuery": "1", "queryMode": "like"},
    {"dbFieldName": "host_user", "isQuery": "1", "queryMode": "single"},
    {"dbFieldName": "start_time", "isQuery": "0"}
  ]
}
```

> **注意：** 视图字段修改不影响原表和其他视图，各自独立。

#### Step 5: 删除视图

```bash
DELETE /online/cgform/head/delete?id={视图headId}
# 仅删除视图配置，不影响原表和数据
```

---

## 表单管理操作 API 速查

| 操作 | 方法 | URL |
|------|------|-----|
| 删除表单（含数据库表） | DELETE | `/online/cgform/head/delete?id={headId}` |
| 批量删除 | DELETE | `/online/cgform/head/deleteBatch?ids={id1},{id2}` |
| 仅移除配置（保留数据库表） | DELETE | `/online/cgform/head/removeRecord?id={headId}` |
| 复制视图（共享数据） | POST | `/online/cgform/head/copyOnline?code={headId}` |
| 完整复制（独立新表） | GET | `/online/cgform/head/copyOnlineTable/{headId}?tableName={新表名}` |
| 导入数据库表 | GET | `/online/cgform/head/transTables/{tableName}` |
| 表名查重（按需，**默认不调用**） | GET | `/sys/duplicate/check?tableName=onl_cgform_head&fieldName=table_name&fieldVal={表名}` |

---

## 错误处理

| 错误 | 解决方案 |
|------|---------|
| Token 过期（401/认证失败） | 提示用户重新获取 X-Access-Token |
| `数据库表[xxx]已存在` | **新建场景**：自动加后缀重试 `xxx_1`、`xxx_2`… 直到成功，告知用户实际表名。**编辑场景**：切换到 editAll。**导入场景**：调 `transTables/{tableName}`。**禁止**用 delete 接口删除已有表来"让位" |
| `保存失败，一对一的表只能新增一条数据` | 一对一子表每条主表记录只能对应一条子表数据，已有则只能 PUT 更新 |
| `附表必须选择映射关系！` | tableType=3 时必须设置 relationType |
| `附表必须填写排序序号！` | tableType=3 时必须设置 tabOrderNum |
| `未找到对应实体` | editAll 时 head.id 不正确 |
| 中文乱码 | 确认使用 Python urllib（不要用 curl） |
| `No static resource online/cgform/api/getByHead` | 该版本不支持 getByHead 查询参数格式，改用 `queryById` + `field/list` 备选方案（见 Step 1B 和 6.4） |
| `Table 'xxx.SYS_CATEGORY' doesn't exist` | MySQL `lower_case_table_names=0`（区分大小写），而框架 XML 用大写表名。解决：cat_tree 的 dictField 留空（不配分类编码），或修改 MySQL 配置为 `lower_case_table_names=1` |
| `Sign签名校验失败` | `/sys/dict/loadTreeData` 等接口需要签名校验，造数据时改用 `/sys/category/rootList` 和 `/sys/category/childList` 查询分类数据 |
| 导入增强不生效（数据全部导入无过滤） | 检查 cgJavaType：**import 不支持 http-api**，必须用 `spring`（spring-key）或 `class`（java-class）方式实现 `CgformEnhanceJavaImportInter` 接口 |
| 树表前端 `hasQuery=false` 查不到数据 | 1. pid/has_child 的 `isShowForm` 必须为 `"1"`；2. 根节点 pid 必须为 `"0"`（字符零），不能是空串或 NULL |
| 主子表 POST 返回「不支持GET请求方法」 | 确认 HTTP method 为 POST，Python 中 `urllib.request.Request` 需显式传 `method='POST'` |
| `exportXlsOld` 返回空内容（Content-Length: 0） | 该接口使用 chunked 流式输出，仅浏览器环境有效，CLI（curl/python）无法下载。替代方案：用 `getColumns` + `getData` API 查询数据后生成 CSV（见 API 参考文档） |
| `No static resource online/cgform/head/copyOnlineTable` | 正确格式是 `GET /online/cgform/head/copyOnlineTable/{headId}?tableName={新表名}`，不是 `?code=` |

---

## 表单删除模式

- **删除**：同时删除 Online 配置 + 物理数据库表
- **移除**：仅删除 Online 配置，保留物理表

## 路由缓存配置

菜单的 `component_name` 必须与表主题匹配，否则路由缓存不生效：

| themeTemplate | component_name |
|--------------|----------------|
| normal | OnlineAutoList |
| tab | OnlCgformTabList |
| erp | CgformErpList |
| innerTable | OnlCgformInnerTableList |
| 树表 | DefaultOnlineList |

## 多租户支持

- Online 表单支持多租户隔离，通过 `tenant_id` 字段实现
- 需配置 `MybatisPlusSaasConfig`
- 数据权限变量 `#{tenant_id}` 可在 SQL 增强中使用

---

## 导入/导出自定义转换器

通过实现 `FieldCommentConverter` 接口自定义字段值的导入导出转换：
- `converterToVal()`：导入时将文本转为存储值
- `converterToTxt()`：导出时将存储值转为显示文本
- `getConfig()`：返回转换器配置

在字段的 `converter` 属性中填写转换器 Bean 名。

## 导入数据校验

- 导入弹窗中勾选「校验数据」启用
- **注意：导入校验不检查唯一约束**，唯一性必须靠数据库层保证
