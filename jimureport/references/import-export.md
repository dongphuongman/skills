# 报表导出接口

## 导出流程

1. **根据报表名称查询报表** → 拿到报表 `id` 作为 `excelConfigId`
2. **组装参数** → `sheetId` 固定传 `"default"`（当前不支持按 sheet 导出），其余参数放 `queryParam`
3. **请求导出接口** → 根据需要的格式调用对应接口，返回二进制流

## 接口列表

### 导出 Excel

**POST** `/jmreport/exportAllExcelStream`

### 导出 PDF

**POST** `/jmreport/exportPdfStream`

### 导出 Word

**POST** `/jmreport/export/word`

## 请求参数

三个接口参数结构一致：

```json
{
    "excelConfigId": "报表id",
    "sheetId": "default",
    "queryParam": {
        "token": "xxx",
        "tenantId": "2",
        "pageNo": "1",
        "pageSize": 10,
        "customTableTitleSorts": [],
        "jmViewOperation": "1",
        "currentPageNo": "1",
        "currentPageSize": 10
    }
}
```

| 字段 | 说明 |
|------|------|
| `excelConfigId` | 报表 id，通过报表名称查询获得 |
| `sheetId` | 固定传 `"default"`，当前不支持按 sheet 导出 |
| `queryParam` | 查询参数，包含 token、分页等信息 |

## 响应

返回二进制流（stream），前端通过 Blob 下载：

```javascript
if (typeof window.navigator.msSaveBlob !== 'undefined') {
    window.navigator.msSaveBlob(new Blob([data]), filename)
} else {
    let url = window.URL.createObjectURL(new Blob([data]))
    let link = document.createElement('a')
    link.style.display = 'none'
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
}
```

---

# Excel 模板导入接口

## 接口

**POST** `/jmreport/importExcel?token={token}`

## 请求参数

`Content-Type: multipart/form-data`

| 参数 | 类型 | 说明 |
|------|------|------|
| `file` | binary | Excel 文件（仅支持 .xlsx） |
| `fileName` | string | 文件名（如 `处方笺20210427190844.xlsx`） |
| `biz` | string | 固定传 `excel_online` |

## 使用流程

1. **用户提供 Excel 文件路径**（仅支持 .xlsx 格式）
2. **调用 importExcel 接口** → 上传文件，返回解析后的 JSON（styles/rows/cols/merges）
3. **将返回的 result 组装到报表 JSON 中** → 作为 save 接口的 rows/cols/styles/merges
4. **调用 /jmreport/save 保存报表**

## 响应

```json
{
    "success": true,
    "message": "",
    "code": 0,
    "result": {
        "styles": [...],    // 样式数组，按索引引用
        "rows": {...},      // 行数据（含 cells、height）
        "merges": [...],    // 合并单元格列表（如 "C3:L3"）
        "cols": {...}       // 列宽配置
    },
    "timestamp": 1775636761304
}
```

### result 字段说明

| 字段 | 说明 |
|------|------|
| `styles` | 样式数组，每个元素包含 font/border/color/align 等属性，单元格通过 `style` 索引引用 |
| `rows` | 行数据，key 为行号（0-indexed），每行包含 `cells`（列数据）和 `height`（行高） |
| `cols` | 列宽配置，key 为列号（0-indexed），值包含 `width` |
| `merges` | 合并单元格列表，格式为 Excel 范围（如 `"C3:L3"`） |

### 单元格结构

```json
{
    "style": 13,        // 引用 styles 数组的索引
    "text": "内容",     // 单元格文本
    "merge": [0, 9]     // 合并：[额外行数, 额外列数]
}
```

## 脚本用法示例

```python
import requests, os

BASE_URL = "<api_base>"
TOKEN = "xxx"

# 1. 上传 Excel 文件
filepath = r"C:\Users\<用户名>\Desktop\xxx.xlsx"
filename = os.path.basename(filepath)

s = requests.Session()
s.trust_env = False
s.headers.update({"X-Access-Token": TOKEN})

with open(filepath, "rb") as f:
    resp = s.post(
        f"{BASE_URL}/importExcel?token={TOKEN}",
        files={"file": (filename, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"fileName": filename, "biz": "excel_online"},
    )
result = resp.json()["result"]

# 2. 提取 styles/rows/cols/merges 用于 save
styles = result["styles"]
rows = result["rows"]
cols = result["cols"]
merges = result["merges"]

# 3. 组装到 base_save 中保存报表
# session.request("/save", base_save(report_id, designer, rows=rows, cols=cols, styles=styles, merges=merges))
```


> 多 Sheet 接口详见 `multi-sheet.md`
