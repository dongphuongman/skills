# 积木报表速查手册

> 本文件从 SKILL.md 移出，仅在需要时 Read。

## 冻结行列（freeze）

```python
base_save(report_id, designer, ..., freeze="A3", freezeLineColor="red")
```

| freeze 值 | 效果 |
|-----------|------|
| `"A1"` | 不冻结（默认） |
| `"A3"` | 冻结前2行 |
| `"A2"` | 只冻结第1行 |
| `"C1"` | 冻结前2列 |
| `"C3"` | 同时冻结前2行和前2列 |

## 预览页工具条（rpbar）

```python
base_save(report_id, designer, ..., rpbar={"show": True, "pageSize": "", "btnList": [1,2,3,4,5,6,7,8,9], "childrenBtnList": [7.1,7.2,7.3,7.4,8.1,8.2,8.3,8.4,8.5,8.6]})
```

> **关键规则**：`btnList` 和 `childrenBtnList` 存的是「**显示**」的按钮列表，不是隐藏列表。
> 要隐藏某个按钮，从列表中删除对应编号即可；`[]` 表示全部隐藏。
> 默认全显示时传完整列表（如上）。

| 主按钮 | | | |
|-------|------|-------|------|
| 1 首页 | 4 分页显示数 | 7 打印 | |
| 2 上一页 | 5 下一页 | 8 导出 | |
| 3 当前/总页数 | 6 末页 | 9 清晰度 | |

| 子按钮 | | | |
|-------|------|-------|------|
| 7.1 默认打印 | 7.2 打印当前页 | 8.1 导出Excel | 8.2 大数据Excel |
| 7.3 分页缩放打印 | 7.4 整体缩放打印 | 8.3 导出PDF | 8.4 导出PDF图像 |
| | | 8.5 导出图像 | 8.6 导出WORD |

**示例：只保留导出、去掉打印及所有分页导航**
```python
rpbar={
    "show": True,
    "pageSize": "20",
    "btnList": [3, 4, 8, 9],                          # 去掉 1,2,5,6,7
    "childrenBtnList": [8.1, 8.2, 8.3, 8.5, 8.6],    # 去掉 7.x 和 8.4
}
```

rpbar 必须是 dict 对象，不能 json.dumps()。

## 钻取/联动 parameter 结构

| linkType | 说明 | reportId 含义 | paramValue |
|---------|------|-------------|-----------|
| "0" | 报表钻取 | 目标报表ID | 字段名 |
| "1" | 网络链接 | 当前报表ID | 字段名 |
| "2" 表格→图表 | 联动 | 当前报表ID | 字段名 |
| "2" 图表→图表 | 联动 | 当前报表ID | name/value/seriesName |

- 单元格触发：`cell["linkIds"] = link_id` + `cell["display"] = "link"`
- 图表触发：`extData["linkIds"] = link_id`
- 联动必须有 `linkChartId`（目标图表 layer_id）

## 图表 extData 必填字段

| 字段 | 说明 |
|------|------|
| chartId / id | = layer_id（两个都要填） |
| chartType | bar.simple / pie.normal / line.simple 等 |
| dataType | "sql" / "json" |
| apiStatus | "1"=动态SQL / "0"=静态JSON |
| dataId | save_db() 返回值 |
| dbCode | 数据集编码 |
| axisX / axisY | X/Y 轴字段名 |
| series | 分组字段名，单系列传 "" |

## searchMode 映射

| searchMode | 控件 |
|-----------|------|
| 1 | 输入框 |
| 2 | 范围查询 |
| 3 | 下拉多选 |
| 4 | 下拉单选 |
| 5 | 模糊查询 |
| 6 | 下拉树 |
| 7 | 自定义下拉 |
| 8 | 时间控件 |

## 参考文档索引

| 文档 | 何时读 |
|------|--------|
| `pitfalls.md` | **必读** — 已知坑点速查 |
| `report-drilling.md` | 钻取/联动 |
| `chart-components.md` | chartList/extData/imgList |
| `chart-echarts-templates.md` | 各图表 ECharts 配置 |
| `chart-echarts-props.md` | ECharts 属性速查 |
| `loopblock-grouping.md` | 循环块 |
| `horizontal-grouping.md` | 横向分组 groupRight+dynamic |
| `dataset-types.md` | 数据集类型速查 |
| `dataset-core.md` | SQL/API/JSON 数据集 |
| `dataset-advanced.md` | 数据源管理/主子表/共享/JavaBean |
| `query-controls.md` | 查询控件 |
| `query-params.md` | querySetting/fieldList |
| `cell-config.md` | 单元格格式/属性/计算/自定义编辑 |
| `expressions.md` | 表达式函数全集 |
| `misc-config.md` | 背景/隐藏行列/行列属性/动态合并/打印/分享 |
| `import-export.md` | 导出PDF·Excel·Word / 导入Excel |
| `multi-sheet.md` | 多 Sheet 接口（添加/重命名/保存/查询） |
| `json-dataset-cells.md` | JSON 数据集绑定 |
| `troubleshooting.md` | 报错排查 |
| `mock-apis.md` | 官方示例 Mock API（字段未确定时用） |
