# 背景图配置完整参考（background）

积木报表背景图：将图片铺设为报表 Sheet 的背景，支持重复平铺。与套打（imgList）不同，背景图不参与打印内容叠加，属于纯视觉装饰。

---

## 1. background JSON 结构

```python
background = {
    "path": "/jmreport/img/jimureport/1_1775121842772.png",  # 图片完整路径（含前缀）
    "repeat": "no-repeat",   # 重复方式
    "width": "1920",         # 宽度（px，字符串格式）
    "height": "1080"         # 高度（px，字符串格式）
}
```

### 字段说明

| 字段 | 类型 | 说明 | 可选值 |
|------|------|------|--------|
| `path` | string | 图片完整路径（`/jmreport/img/` + 上传返回的 `message`） | - |
| `repeat` | string | 图片重复方式 | `no-repeat` / `repeat-x` / `repeat-y` / `repeat` |
| `width` | string | 背景图宽度（px，字符串格式） | 如 `"1920"` |
| `height` | string | 背景图高度（px，字符串格式） | 如 `"1080"` |

### repeat 可选值说明

| 值 | 含义 |
|----|------|
| `no-repeat` | 无重复（默认，推荐） |
| `repeat-x` | 水平方向重复 |
| `repeat-y` | 垂直方向重复 |
| `repeat` | 双向重复平铺 |

---

## 2. 无背景图时

```python
# 保存 API 参数中传 Python bool False（不是字符串 "false"）
"background": False
```

---

## 3. 图片上传

背景图需先通过上传接口获取路径，**必须由用户提供图片文件**，AI 无法自动上传。

### 上传接口

```
POST /jmreport/upload
Content-Type: multipart/form-data

参数：file（MultipartFile）
```

### 返回结果

```json
{
    "success": true,
    "message": "jimureport/1_1775122603620.png",
    "code": 0,
    "result": null,
    "timestamp": 1775122603620
}
```

### 路径使用规则

- 返回值中 **`message` 字段** 即为图片路径
- `background.path` = `/jmreport/img/` + `message` 值
  - 例：`message` = `jimureport/1_1775121842772.png`
  - → `path` = `/jmreport/img/jimureport/1_1775121842772.png`

### Python 上传示例

```python
import requests, os

def upload_image(base_url, token, file_path):
    """上传图片，返回 message 字段路径"""
    with open(file_path, 'rb') as f:
        resp = requests.post(
            f"{base_url}/jmreport/upload",
            headers={"X-Access-Token": token},
            files={"file": (os.path.basename(file_path), f)}
        )
    data = resp.json()
    if data.get("success"):
        return data["message"]   # e.g. "jimureport/1_1775121842772.png"
    raise Exception(f"上传失败: {data}")

# 构建 background 对象
msg = upload_image(base_url, token, "/path/to/bg.png")
background = {
    "path": f"/jmreport/img/{msg}",   # 加前缀
    "repeat": "no-repeat",
    "width": "1920",
    "height": "1080"
}
```

---

## 4. 背景图 vs 套打（imgList）路径前缀对比

| 用途 | 字段 | 路径格式 |
|------|------|---------|
| 背景图 | `background.path` | `/jmreport/img/` + `message` |
| 套打图片 | `imgList[].src` | `message`（直接使用，无前缀） |

> **关键区别：** 背景图路径需加 `/jmreport/img/` 前缀，套打路径直接使用上传返回的 `message` 值。

---

## 5. 注意事项

1. `printConfig.isBackend` 为 `false` 时背景图正常显示；套打（`isBackend: true`）时背景图不生效，应使用 `imgList`
2. `width`/`height` 为字符串类型（`"1920"`），不是数字
3. 保存 API 中 `background` 字段**直接传对象（dict）**，不要 json.dumps 成字符串；否则前端报 `Cannot use 'in' operator to search for 'repeat'` 错误

---

# 隐藏行与隐藏列

积木报表通过 `/jmreport/save` 的 `hidden` 字段控制行/列的显示与隐藏，支持静态隐藏和条件隐藏两种模式。

---

## 1. 数据结构

```python
"hidden": {
    "rows": [],          # 静态隐藏行列表（始终隐藏，与条件隐藏完全独立）
    "cols": [],          # 静态隐藏列列表（始终隐藏）
    "conditions": {
        "rows": {},      # 条件隐藏行：{range_key: aviator表达式}，满足条件才隐藏
        "cols": {},      # 条件隐藏列：{range_key: aviator表达式}，满足条件才隐藏
    }
}
```

> **重要**：`rows`/`cols` 列表（静态隐藏）与 `conditions.rows`/`conditions.cols`（条件隐藏）是**完全独立的两套机制**。
> - 静态隐藏：放入 `rows` 列表 → 始终隐藏
> - 条件隐藏：放入 `conditions.rows` → 满足 aviator 表达式时隐藏
> - 两者不需要同时设置，混用会导致条件行变成始终隐藏

范围 key 格式：`"起:止"`（**直接对应 rows/cols dict 的 key 数字**，两端闭区间）
- `"3:3"` — rows key 为 "3" 的行（单行）
- `"1:3"` — rows key "1"~"3" 的行（多行）
- `"1:1"` — cols key 为 "1" 的列（B列）

> **关键**：index 不是"第几行的位置"，而是 rows dict 的 key 数字。rows 从 key "0" 开始时，第1行 index=0；rows 从 key "1" 开始时，第1行 index=1。必须与报表 rows 的实际 key 对应。

---

## 2. 静态隐藏（始终隐藏）

只在 `hidden.rows` / `hidden.cols` 列表中登记，不加 `conditions`。

```python
hidden = {
    "rows": ["4:4"],   # 始终隐藏第5行（index=4）
    "cols": ["1:1"],   # 始终隐藏B列（index=1）
    "conditions": {"rows": {}, "cols": {}}
}
```

取消静态隐藏：从列表中移除对应 key。

```python
hidden["rows"] = [r for r in hidden["rows"] if r != "4:4"]
```

---

## 3. 条件隐藏（aviator 表达式）

只在 `conditions.rows` / `conditions.cols` 中登记，**不要同时加到 `rows`/`cols` 列表**（加了就变成始终隐藏）。

```python
hidden = {
    "rows": [],    # 静态隐藏留空
    "cols": [],
    "conditions": {
        "rows": {
            "1:1": "person.xingming=='张三'",   # 当姓名==张三时隐藏第2行（index=1）
            "2:2": "person.xingming=='张三'",   # 当姓名==张三时隐藏第3行（index=2）
        },
        "cols": {
            "3:3": "person.age<18",   # 当年龄<18时隐藏D列（index=3）
        }
    }
}
```

取消条件隐藏：只从 `conditions` 中移除即可，无需改 `rows` 列表。

```python
hidden["conditions"]["rows"].pop("1:1", None)
```

### aviator 表达式速查

| 需求 | 表达式 |
|------|--------|
| 等于字符串 | `"dbCode.field=='值'"` |
| 不等于 | `"dbCode.field!='值'"` |
| 大于数字 | `"dbCode.field>18"` |
| AND 复合 | `"dbCode.f1=='A'&&dbCode.f2>10"` |
| OR 复合 | `"dbCode.f1=='A'||dbCode.f1=='B'"` |
| 始终隐藏 | `"1==1"` |

字段引用：`数据集编码.字段名`（与 saveDb 的 `dbCode` + `fieldName` 一致）

---

## 4. 预览行为

- 隐藏行消失后，后续行**索引上移**
- 隐藏列消失后，后续列**索引左移**
- 含 `hidden:1` 标记的单元格所在行保留原始索引（不参与位移计算）

---

## 5. 实现方式

条件隐藏和静态隐藏均通过 `get_report()` + 修改 `hidden` 字段 + `base_save()` 实现，无需独立脚本（参见上方代码片段）。

---

# 行（row）与列（col）属性

积木报表中 `rows` 和 `cols` 的属性参考。

---

## 一、行属性（rows）

行对象存储在 `rows["行号"]` 中，key 为 0-indexed 行号字符串。

### 基础结构

```json
"rows": {
    "0": {
        "cells": { ... },
        "height": 50
    },
    "1": {
        "cells": { ... },
        "height": 35,
        "pagingRow": true
    }
}
```

### 行级属性列表

| 属性 | 类型 | 说明 | 默认 |
|------|------|------|------|
| `cells` | object | 该行的单元格数据，key 为列号（0-indexed） | 必填 |
| `height` | number | 行高（像素） | 25 |
| `pagingRow` | boolean | 分页行，打印时该行在每页重复显示（常用于列头行） | 不设置 |

> **注意：** `pagingRow` 是**行级属性**，不是单元格属性。设置在 `rows["1"]` 上，不是 `rows["1"]["cells"]["1"]` 上。

### 示例：列头行设为分页行

```python
rows = {
    "0": {"cells": {...}, "height": 50},                      # 标题行
    "1": {"cells": {...}, "height": 35, "pagingRow": True},   # 列头行，每页重复
    "2": {"cells": {...}, "height": 30},                      # 数据行
}
```

---

## 二、列属性（cols）

列对象存储在 `cols["列号"]` 中，key 为 0-indexed 列号字符串。

### 基础结构

```json
"cols": {
    "0": {"width": 30},
    "1": {"width": 100},
    "2": {"width": 150}
}
```

### 列级属性列表

| 属性 | 类型 | 说明 | 默认 |
|------|------|------|------|
| `width` | number | 列宽（像素） | 100 |

> A列（col 0）通常留空作左边距，宽度设为 30px 左右。

---

# 积木报表动态合并单元格配置

## 功能说明

**功能名称**: `dynamicMerge`

**应用场景**: 当在表格数据前需要添加一列固定内容时，使用动态合并格。

**效果说明**:
- 未设置时：数据有几条记录，固定列内容就显示几次
- 设置后：固定列内容合并显示为一条

## API 配置方法

在单元格配置中添加 `dynamicMerge: 1`：

```json
{
  "cells": {
    "1": {
      "text": "固定内容标题",
      "style": 2,
      "dynamicMerge": 1
    }
  }
}
```

## 使用示例

### 场景：订单明细表，每行显示订单号和商品，但订单号是固定的

**数据结构**:
```json
{
  "data": [
    {"order_no": "ORD001", "product": "商品A"},
    {"order_no": "ORD001", "product": "商品B"},
    {"order_no": "ORD001", "product": "商品C"}
  ]
}
```

**期望效果**: 订单号列合并为一条，只显示一次

**rows 配置**:
```json
{
  "0": {"cells": {"1": {"text": "订单明细表", "style": 5, "merge": [0, 2]}}, "height": 50},
  "1": {
    "cells": {
      "1": {"text": "订单号", "style": 4},
      "2": {"text": "商品名称", "style": 4},
      "3": {"text": "数量", "style": 4}
    },
    "height": 34
  },
  "2": {
    "cells": {
      "1": {"text": "#{orders.order_no}", "style": 2, "dynamicMerge": 1},
      "2": {"text": "#{orders.product}", "style": 2},
      "3": {"text": "#{orders.qty}", "style": 2}
    }
  }
}
```

**关键点**:
- `dynamicMerge: 1` 添加在需要合并的列单元格上
- 该列必须是数据绑定列（使用 `#{db.field}`）
- 通常配合纵向分组使用，效果更佳

## 设计器配置步骤

1. 选中固定值所在列的单元格
2. 右键 → 动态合并格 → 设定
3. 设定完成后，单元格右上角显示红色角标
4. 鼠标悬浮提示"动态单元格"

## 注意事项

- `dynamicMerge` 是单元格级别的配置
- 适用于需要将重复数据合并显示的场景
- 动态合并后，该列的边框样式可能需要手动调整以保持美观
---

# 打印配置完整参考（printConfig）

积木报表的打印设置，包含纸张、布局、边距、页码、页眉页脚、水印等配置。所有配置存储在 jsonStr 的 `printConfig` 字段中。

---

## 1. 完整 printConfig 结构

```python
printConfig = {
    # ===== 纸张与布局 =====
    "paper": "A4",              # 纸张大小
    "width": 210,               # 纸张宽度(mm)
    "height": 297,              # 纸张高度(mm)
    "layout": "portrait",       # 打印布局: portrait(纵向) / landscape(横向)
    # "definition": 1,          # 清晰度（已从打印设置UI中移除，无需设置）
    "isBackend": False,         # 是否套打

    # ===== 边距 =====
    "marginX": 10,              # 左右边距(mm)
    "marginY": 10,              # 上下边距(mm)

    # ===== 回调 =====
    "printCallBackUrl": "",     # 打印回调接口URL（文档：https://help.jimureport.com/printNew/callback/）

    # ===== 页码 =====
    "paginationShow": True,     # 是否显示页码
    "paginationLocation": "middle",  # 页码位置: left / middle / right
    "paginationStart": 1,       # 页码起始范围（第N页及以后显示页码）

    # ===== 页眉页脚 =====
    "headerFooterShow": False,  # 是否启用页眉页脚
    "headerLocation": "left",   # 页眉位置: left / middle / right（配合文本使用）
    "headerText": "",           # 页眉文本
    "footerLocation": "left",   # 页脚位置: left / middle / right
    "footerText": "",           # 页脚文本

    # ===== 水印 =====
    "watermarkShow": False,     # 是否显示水印
    "watermarkText": "积木报表", # 水印文本
    "fontsize": 28,             # 水印字号(10-72)
    "watermarkColor": "#d5d5d5",# 水印颜色
    "rotationAngle": -45,       # 水印旋转角度（负值=逆时针）

    # ===== 表尾固定 =====
    "printFootorFixBottom": False  # 打印时表尾是否固定到页面底部
}
```

---

## 2. 纸张大小

### 2.1 系统内置纸张

| paper 值 | 中文名 | width × height (mm) |
|----------|--------|---------------------|
| `"A4"` | A4 | 210 × 297 |
| `"A3"` | A3 | 297 × 420 |
| `"Letter"` | Letter | 216 × 279 |
| `"Legal"` | Legal | 216 × 355 |
| `"Executive"` | Executive | 184 × 266 |

> **注意**：修改 paper 时需同步修改 width 和 height。paper 值区分大小写，需与上表完全一致（如 `"Letter"` 首字母大写）。

### 2.2 自定义纸张

通过修改 `application.yml`（启动类所在项目）新增自定义纸张（v1.1.09+）：

```yaml
jeecg:
  jmreport:
    printPaper:
      - title: A5纸
        size:
          - 148   # 宽度(mm)
          - 210   # 高度(mm)
      - title: B4纸
        size:
          - 250
          - 353
```

配置后，设计器纸张下拉列表中出现自定义选项，`paper` 字段传入 `title` 值，`width`/`height` 对应 `size[0]`/`size[1]`。

### 2.3 纸张自动识别规则（AI 生成报表时使用）

**当用户提到纸张时，按以下优先级匹配：**

1. **先读 yml 自定义配置**：从服务 `application-*.yml` 中读取 `jeecg.jmreport.printPaper` 列表，按 `title` 模糊匹配用户的描述
2. **再匹配系统内置纸张**：按下表关键词识别
3. **匹配失败时**：告知用户该纸张不在系统配置中，并列出可用选项，不要擅自选择其他纸张

**内置纸张关键词匹配表：**

| 用户描述关键词 | paper 值 | width | height |
|--------------|----------|-------|--------|
| A4、a4 | `"A4"` | 210 | 297 |
| A3、a3 | `"A3"` | 297 | 420 |
| Letter、letter、信纸 | `"Letter"` | 216 | 279 |
| Legal、legal、法律 | `"Legal"` | 216 | 355 |
| Executive、executive | `"Executive"` | 184 | 266 |

**当前服务自定义纸张：** 无（yml 中未配置 `printPaper`）

> **重要：** 若用户指定的纸张在内置列表和 yml 自定义配置中均找不到，必须明确告知用户：
> "系统中未找到「XX纸张」配置，当前可用纸张为：A4、A3、A5、B5、Letter、Legal。如需使用自定义纸张，请在 `application.yml` 中配置 `jeecg.jmreport.printPaper`。"
> 不允许静默降级到 A4 或其他纸张。

---

## 3. 打印布局

| layout | 说明 | 适用场景 |
|--------|------|---------|
| `"portrait"` | 纵向（默认） | 列数 ≤ 6 |
| `"landscape"` | 横向 | 列数 > 6，宽表格 |

---

## 4. 页码配置

```python
# 显示页码，居中，从第1页开始
"paginationShow": True,
"paginationLocation": "middle",
"paginationStart": 1

# 不显示页码
"paginationShow": False
```

| 字段 | 值 | 说明 |
|------|-----|------|
| `paginationShow` | `True/False` | 是否显示页码 |
| `paginationLocation` | `"left"/"middle"/"right"` | 页码位置 |
| `paginationStart` | 数字 | 从第N页开始显示页码（之前的页不显示） |

---

## 5. 页眉页脚配置

```python
# 启用页眉页脚
"headerFooterShow": True,
"headerLocation": "left",    # 页眉靠左
"headerText": "机密文件",     # 页眉内容
"footerLocation": "right",   # 页脚靠右
"footerText": "公司内部使用"   # 页脚内容
```

| 字段 | 值 | 说明 |
|------|-----|------|
| `headerFooterShow` | `True/False` | 是否启用页眉页脚 |
| `headerLocation` | `"left"/"middle"/"right"` | 页眉位置 |
| `headerText` | 字符串 | 页眉文本 |
| `footerLocation` | `"left"/"middle"/"right"` | 页脚位置 |
| `footerText` | 字符串 | 页脚文本 |

> **与固定表头表尾的区别**：页眉页脚是打印设置中的轻量文本，固定表头表尾是 jsonStr 中的单元格区域（支持合并、样式等）。

---

## 6. 水印配置

```python
# 启用水印
"watermarkShow": True,
"watermarkText": "机密文件",
"fontsize": 28,
"watermarkColor": "#d5d5d5",
"rotationAngle": -45
```

| 字段 | 值 | 说明 |
|------|-----|------|
| `watermarkShow` | `True/False` | 是否显示水印 |
| `watermarkText` | 字符串 | 水印文本（默认"积木报表"） |
| `fontsize` | 数字 | 水印字号，可选：10/12/14/16/18/20/22/24/26/28/36/48/72 |
| `watermarkColor` | 颜色值 | 水印颜色（默认 `#d5d5d5` 浅灰） |
| `rotationAngle` | 数字 | 旋转角度（-45=逆时针45度，0=水平） |

---

## 7. 常用配置模板

### 标准A4纵向（默认）
```python
"printConfig": {
    "paper": "A4", "width": 210, "height": 297,
    "definition": 1, "isBackend": False,
    "marginX": 10, "marginY": 10,
    "layout": "portrait", "printCallBackUrl": ""
}
```

### 横向宽表格 + 页码 + 页眉页脚
```python
"printConfig": {
    "paper": "A4", "width": 210, "height": 297,
    "definition": 1, "isBackend": False,
    "marginX": 10, "marginY": 10,
    "layout": "landscape", "printCallBackUrl": "",
    "paginationShow": True,
    "paginationLocation": "middle",
    "paginationStart": 1,
    "headerFooterShow": True,
    "headerLocation": "left",
    "headerText": "销售部门报表",
    "footerLocation": "right",
    "footerText": "仅供内部使用"
}
```

### 带水印的机密报表
```python
"printConfig": {
    "paper": "A4", "width": 210, "height": 297,
    "definition": 1, "isBackend": False,
    "marginX": 10, "marginY": 10,
    "layout": "portrait", "printCallBackUrl": "",
    "watermarkShow": True,
    "watermarkText": "机密文件",
    "fontsize": 36,
    "watermarkColor": "#e0e0e0",
    "rotationAngle": -30
}
```

### 完整配置（所有功能开启）
```python
"printConfig": {
    "paper": "A4", "width": 210, "height": 297,
    "definition": 1, "isBackend": False,
    "marginX": 15, "marginY": 15,
    "layout": "landscape", "printCallBackUrl": "",
    "paginationShow": True,
    "paginationLocation": "middle",
    "paginationStart": 1,
    "headerFooterShow": True,
    "headerLocation": "left",
    "headerText": "XX公司-销售报表",
    "footerLocation": "right",
    "footerText": "打印日期：2026-03-27",
    "watermarkShow": True,
    "watermarkText": "内部文件",
    "fontsize": 28,
    "watermarkColor": "#d5d5d5",
    "rotationAngle": -45,
    "printFootorFixBottom": True
}
```

---

## 8. 注意事项

1. **边距最小值**：`marginX`/`marginY` 建议 ≥ 10mm，小于 10mm 页眉页脚可能显示不全
2. **套打模式**（`isBackend: True`）：套打时页眉页脚不可用
3. **页码起始**：`paginationStart: 2` 表示第1页不显示页码，从第2页开始
4. **水印字号**：只支持固定值 10/12/14/16/18/20/22/24/26/28/36/48/72
5. **横向打印**：列数 > 6 时建议 `layout: "landscape"`，实际纸张宽高不变（由打印机处理方向）
6. **printFootorFixBottom**：开启后打印时表尾固定到每页底部（类似 fixedPrintTailRows 但更简单）

---

## 9. 打印规则（官方文档）

> 来源：https://help.jimureport.com/print/rule

### 9.1 纸张宽度与内容宽度规则

设计器中绿色虚线标识当前纸张宽度边界，打印时遵循以下规则：

| 情况 | 打印行为 |
|------|---------|
| 内容宽度 ≤ 纸张宽度 | 按纸张尺寸打印，内容居中或按边距对齐 |
| 内容宽度 > 纸张宽度 | **超出部分不打印**（旧的超宽规则已废弃） |

> **横向打印（landscape）不是让超宽内容适配纸张，而是需要在 `printConfig.layout` 中显式配置。**

### 9.2 打印内容居中

当内容宽度小于纸张宽度时，内容可能偏左，有两种居中方案：

1. **自动居中**：在报表设计器布局设置中开启水平居中（`isViewContentHorizontalCenter: true`）
2. **手动居中**：设计时在内容左右两侧各留等宽的空列作为边距，使内容视觉上居中

### 9.3 图表背景色

打印时图表会带灰色边框（来自图表背景颜色），若不需要，在图表属性中将背景颜色设置为透明/无色即可。

### 9.4 自定义纸张（v1.1.09+）

在 `application.yml` 中通过 `jeecg.jmreport.printPaper` 配置自定义纸张，单位为毫米：

```yaml
jeecg:
  jmreport:
    printPaper:
      - title: A5纸
        size:
          - 148
          - 210
      - title: B4纸
        size:
          - 250
          - 353
```

配置后，设计器纸张下拉列表中会出现自定义纸张选项。

### 9.5 套打（isBackend）

套打时，打印内容的范围取决于**套打图片的尺寸**，超出图片边界的单元格数据不会被打印。设计时需确保所有内容都在套打图片范围内。

### 9.6 打印全部数据的请求规则（开发参考）

当用户点击"打印全部"或"导出PDF"时，系统向后端发送的数据集查询请求会附加：

- `printAll=true`
- `pageSize` = 该数据集的 `count`（总记录数）

**含义：** 打印全部时会将全量数据一次性加载，对于大数据集需注意性能。开发自定义打印接口时，可通过 `printAll` 参数判断是否需要返回全量数据。

### 9.7 慎用自动换行

开启单元格自动换行（`wrap: true`）可能引发以下问题：

- 当某个单元格内容高度超过一页高度时，该行会被拆分到下一页
- 拆分后当前页底部出现大片空白区域，导致页面利用率低
- 多行数据时，空白问题会累积，产生多个近乎空白的页面

**建议：** 对于可能内容较多的单元格（如备注、描述字段），优先通过限制列宽、截断文本或调整字号来控制高度，而非依赖自动换行。# 报表分享/取消分享

## 创建分享流程

1. 按名称查询报表 `GET /query/report/folder?name=xxx`
2. 多条结果 → 列出让用户确认；唯一 → 直接用
3. 调用 `POST /share/addAndEdit`，默认：永久有效、不开密码、校验token
4. 输出分享链接 + 密码（如有）

### 创建分享请求

```python
session.request("/share/addAndEdit", {
    "id": "",                    # 新建传空
    "reportId": "报表ID",
    "previewUrl": "",
    "previewLock": "",           # 密码（开启时设置）
    "status": "0",               # "0"=分享中
    "termOfValidity": "1",       # "1"=永久, "2"=7天, "3"=1天
    "previewLockStatus": "0",    # "0"=无密码, "1"=有密码
    "verifyShareToken": "1",     # "0"=否, "1"=是
})
```

### 返回

```json
{
    "result": {
        "id": "分享记录ID",
        "previewUrl": "/jmreport/shareView/{reportId}?shareToken=xxx",
        "previewLock": "密码",
        "shareToken": "xxx"
    }
}
```

**分享地址拼接：** `{BASE_URL去掉/jmreport} + result.previewUrl`

---

## 取消分享

同一接口，传 `status: "1"` + 分享记录 `id`：

```python
session.request("/share/addAndEdit", {
    "id": "分享记录ID",
    "status": "1",
    "reportId": "报表ID"
})
```

**status 说明：** `"0"` = 分享中，`"1"` = 已取消

---

## 脚本用法

```bash
# 创建分享（默认永久、无密码）
python report_export.py share --name "报表名"

# 多条结果选第1个
python report_export.py share --name "报表名" --index 1

# 带密码
python report_export.py share --name "报表名" --lock 1 --password abc123

# 7天有效
python report_export.py share --name "报表名" --validity 2

# 不校验token
python report_export.py share --name "报表名" --verify 0
```
