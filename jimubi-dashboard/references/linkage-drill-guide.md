# 组件联动与钻取

## 组件联动（linkageConfig）

组件联动实现"点击 A 组件 → 刷新 B 组件"的交互效果。

### 联动配置结构

**只需配置源组件**，目标组件不需要额外联动配置，只需有对应的 `paramOption` 参数即可接收。

```python
cfg['linkType'] = 'comp'           # 必须设为 'comp'
cfg['linkageConfig'] = [
    {
        'linkageId': '目标组件的i值',
        'linkage': [
            {
                'source': 'name',      # 点击时获取的字段
                'target': 'name'       # 传给目标组件的参数名
            }
        ]
    }
]
```

### source 可用字段

| source 值 | 含义 | 示例 |
|-----------|------|------|
| `name` | 类目/标签名（维度） | 饼图扇区名、柱子 x 轴标签 |
| `value` | 数值 | 饼图扇区值、柱子高度 |
| `type` | 多系列图表的系列名 | "系列A"、"手机品牌" |

### 目标组件要求

1. `paramOption` 中有对应参数定义（`value` 字段与 `target` 匹配）
2. SQL 数据集中有对应 FreeMarker 动态条件：`<#if isNotEmpty(paramName)> and field = '${paramName}' </#if>`

### 完整示例：饼图联动柱形图

```python
PIE_ID = 'pie_component_i'
BAR_ID = 'bar_component_i'

page = query_page(PAGE_ID)
template = page.get('template', [])
if isinstance(template, str):
    template = json.loads(template)

for comp in template:
    cfg = comp.get('config', {})
    if isinstance(cfg, str):
        cfg = json.loads(cfg)
    if comp['i'] == PIE_ID:
        cfg['linkType'] = 'comp'
        cfg['linkageConfig'] = [
            {
                'linkageId': BAR_ID,
                'linkage': [{'source': 'name', 'target': 'name'}]
            }
        ]
    comp['config'] = cfg

bi_utils._page_components[PAGE_ID] = template
save_page(PAGE_ID)
```

### 多目标联动

```python
cfg['linkageConfig'] = [
    {'linkageId': BAR_ID, 'linkage': [{'source': 'name', 'target': 'name'}]},
    {'linkageId': TABLE_ID, 'linkage': [{'source': 'name', 'target': 'keyword'}]},
]
```

### 运行时流程

```
用户点击饼图 "张三" 扇区
→ bindClick() 获取 params: {name: '张三', value: 1000}
→ 遍历 linkageConfig，构建 linkageParams
→ refreshComp(linkageParams) → 找到柱形图实例
→ barInstance.queryData(null, {name: '张三'})
→ SQL 拼接: ... and name like '%张三%'
→ 柱形图刷新
```

---

## 组件钻取（drillData）

钻取实现"点击组件自身 → 用点击值作为参数重新查询自身"的下钻效果。与联动不同，钻取是**组件对自身的递归查询**，支持多级下钻和回退。

### 钻取配置结构

```python
cfg['drillData'] = [
    {
        'source': 'value',    # 点击时获取的字段
        'target': 'sex'       # 传给自身的参数名
    }
]
```

### 完整示例：柱形图下钻

```python
BAR_ID = 'bar_component_i'

page = query_page(PAGE_ID)
template = page.get('template', [])
if isinstance(template, str):
    template = json.loads(template)

for comp in template:
    if comp['i'] == BAR_ID:
        cfg = comp.get('config', {})
        if isinstance(cfg, str):
            cfg = json.loads(cfg)
        cfg['drillData'] = [
            {'source': 'value', 'target': 'sex'}
        ]
        comp['config'] = cfg
        break

bi_utils._page_components[PAGE_ID] = template
save_page(PAGE_ID)
```

## 联动与钻取的区别

| 特性 | 联动（linkageConfig） | 钻取（drillData） |
|------|----------------------|-------------------|
| 作用对象 | 刷新**其他**组件 | 刷新**自身** |
| 配置位置 | 源组件 config | 自身 config |
| queryMode | `'link'` | `'drill'` |
| 支持回退 | 不支持 | 支持 |
| 可同时使用 | 是 | 是 |

### 联动 + 钻取同时配置

```python
cfg['linkType'] = 'comp'
cfg['linkageConfig'] = [{'linkageId': OTHER_ID, 'linkage': [...]}]
cfg['drillData'] = [{'source': 'name', 'target': 'category'}]
# 点击时：先执行联动刷新其他组件，再执行钻取刷新自身
```

### 关键源码位置

| 文件 | 职责 |
|------|------|
| `packages/hooks/charts/useEChartsNew.ts` (551-728) | ECharts 点击事件绑定 |
| `packages/hooks/common/useLinkage.ts` (218-288) | `refreshComp()` 执行联动/钻取刷新 |
| `packages/dragEngine/modal/LinkConfig.vue` | 联动配置 UI 弹窗 |
| `packages/dragEngine/modal/chartset/components/LowDrillConfig.vue` | 钻取配置 UI |
