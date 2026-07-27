---
name: Online表单head配置字段的正确值类型
description: isPage/isCheckbox是字符串Y/N，formTemplate是字符串1/2/3/4控制列数，不是tabOrderNum
type: feedback
---

Online 表单 head 配置中部分字段的值类型容易搞错：

**Why:** 曾把 `isPage` 设为数字 `0`（应为字符串 `"N"`），把列数设为 `tabOrderNum`（应为 `formTemplate`），导致配置不生效。

**How to apply:**

| 配置项 | 字段名 | 正确值 | 错误值 |
|--------|--------|--------|--------|
| 是否分页 | `isPage` | `"Y"` / `"N"` | `1` / `0` |
| 是否复选框 | `isCheckbox` | `"Y"` / `"N"` | `true` / `false` |
| 是否树表 | `isTree` | `"Y"` / `"N"` | `true` / `false` |
| 表单列数 | `formTemplate` | `"1"` / `"2"` / `"3"` / `"4"` | `tabOrderNum` |
| 滚动条 | `scroll` | `0`(无滚动) / `1`(有滚动) | — |
| 表描述 | `tableTxt` | 字符串 | — |
| **多数据源编码** | `dbSource` | `sys_data_source.code`（如 `mysql11`），非 extConfigJson | 默认 `""` |
| **开启多数据源** | `enableMultiDataSource` | extConfigJson 字段，`0`=关闭 / `1`=开启 | 配合 `dbSource` 使用 |
| 主题模板 | `themeTemplate` | `"normal"` / `"tab"` / `"erp"` / `"innerTable"` | — |

注意：`tabOrderNum` 是子表排序号（子表在 TAB 中的显示顺序），不是表单列数。
