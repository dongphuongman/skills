# 仪表盘组件菜单层级结构

> 提取自 `packages/dragEngine/components/jeecgComponents/data.ts` 的 `menuData` 导出。
> 仪表盘引擎文件：`packages/dragEngine/otherStyles/DragEngineJeecg.vue`
> 此文件记录组件面板的完整分类树，用于理解组件归属和定位。

---

## 与大屏的关键区别

| 对比项 | 仪表盘（jeecgComponents） | 大屏（bigScreenComponents） |
|--------|--------------------------|----------------------------|
| 数据源文件 | `jeecgComponents/data.ts` | `bigScreenComponents/data.ts` |
| 引擎组件 | `DragEngineJeecg.vue` | `DragEngineScreen.vue` |
| 布局模式 | 24列栅格（w/h 为栅格单位） | 像素坐标（w/h 为像素） |
| 默认 w/h | w:12, h:30 | w:450, h:300 |
| 组件 ID字段 | `i`（uuid） | `i`（uuid） |
| 背景色 | 默认白色 `#FFFFFF` | 默认透明 |
| 最大组件数 | 20（`MAX_COMPONENT`） | 同 20 |
| 没有的功能 | 无右键图层操作、无弹窗组件 | 有右键图层、有边框装饰等 |

---

## 一级分类（顶级 menuData 节点）

```
menuData [
  {id:'local-200',                    name:'图表',      compType:'chart'}
  {id:'local-100',                    name:'组件',      compType:''}
  {id:'local-707153616621699072',     name:'表单',      compType:'customForm'}
  {id:'local-100101',                 name:'布局',      compType:'layout'}
  {id:'local-100102',                 name:'组件',      compType:'dataList'}
  {id:'local-100120',                 name:'图表',      compType:'dataList'}
  {id:'local-100104',                 name:'首页',      compType:'home'}
  {id:'local-708970414976712704',     name:'高级',      compType:'custom'}
]
```

---

## 完整层级树

### 图表 (id:local-200, compType:chart)

```
图表
├── [柱形图] (id:local-200200)
│   ├── JBar            基础柱形图
│   ├── JStackBar       堆叠柱形图
│   ├── JDynamicBar     动态柱形图
│   ├── JHorizontalBar  基础条形图
│   ├── JBackgroundBar  背景柱形图
│   ├── JMultipleBar    对比柱形图
│   ├── JNegativeBar    正负条形图
│   └── JMixLineBar     折柱图
│
├── JPie                基础饼图           ← 直接挂在图表下（非子分类）
├── JRose               南丁格尔玫瑰图     ← 直接挂在图表下
│
├── [折线图] (id:local-200202)
│   ├── JLine           基础折线图
│   ├── JSmoothLine     平滑曲线图
│   ├── JStepLine       阶梯折线图
│   ├── JMultipleLine   对比折线图
│   └── DoubleLineBar   双折线图
│
├── JRing               环形图             ← 直接挂在图表下
├── JArea               面积图             ← 直接挂在图表下
├── JCustomProgress     基础进度图         ← 直接挂在图表下
├── JProgress           进度图             ← 直接挂在图表下
├── JPictorialBar       象形图             ← 直接挂在图表下
│
├── [仪表盘] (id:local-200207)
│   ├── JGauge          基础仪表盘
│   └── JColorGauge     彩色仪表盘
│
├── [散点图] (id:local-200205)
│   ├── JScatter        普通散点图
│   └── JBubble         气泡图
│
├── [漏斗图] (id:local-200206)
│   ├── JFunnel         普通漏斗图
│   └── JPyramidFunnel  金字塔漏斗
│
└── [雷达图] (id:local-200204)
    ├── JRadar          普通雷达图
    └── JCircleRadar    圆形雷达图
```

### 组件 (id:local-100, compType:'')

```
组件
├── JForm               表单
├── JCarousel           轮播图
├── JIframe             Iframe
├── JCalendar           日历
├── JMultiViewCalendar  多视图日历
├── JImg                图片
├── JText               文本
├── JNumber             数值
├── JRadioButton        单选按钮
├── JFilterQuery        查询过滤
├── JCustomButton       自定义按钮
├── JCurrentTime        当前时间
└── JDragEditor         富文本
```

### 表单 (id:local-707153616621699072, compType:customForm)

```
表单
├── Online表单          (compType:'online')
└── 设计器表单          (compType:'design')
```

### 布局 (id:local-100101, compType:layout)

```
布局
├── JTabs               选项卡
└── JGrid               栅格
```

### 组件/数据列表 (id:local-100102, compType:dataList)

```
组件
├── JCommonTable        数据表格
├── JList               数据列表
├── JCommon             通用组件
├── JCustomEchart       自定义图表
└── JPivotTable         透视表
```

### 图表/数据列表 (id:local-100120, compType:dataList)

```
图表（数据列表分类）
├── JBubbleMap          散点地图
├── JFlyLineMap         飞线地图
├── JBarMap             柱形地图
├── JTotalFlyLineMap    时序动态飞线地图
├── JTotalBarMap        时序动态柱形地图
├── JHeatMap            热力地图
└── JAreaMap            区域地图
```

### 首页 (id:local-100104, compType:home)

```
首页
├── JQuickNav           快捷导航
├── JGrowCard           统计卡片
├── JProjectCard        项目列表
├── JSimpleCard         简单卡片
├── JWaitMatter         待处理事项
└── JDynamicInfo        最新动态
```

### 高级 (id:local-708970414976712704, compType:custom)

```
高级
└── JCommon             牛魔王（自定义复杂图表）
    （注：此分类还有 JArchitecture/JVrHourse/JMap 等 3D 组件，w:12, h:55）
```

---

## 组件总数统计

| 分类 | 组件数 | 说明 |
|------|--------|------|
| 柱形图 | 8 | JBar/JStackBar/JDynamicBar/JHorizontalBar/JBackgroundBar/JMultipleBar/JNegativeBar/JMixLineBar |
| 饼图 | 2 | JPie/JRose（直接挂在图表下） |
| 折线图 | 5 | JLine/JSmoothLine/JStepLine/JMultipleLine/DoubleLineBar |
| 其他图表 | 5 | JRing/JArea/JCustomProgress/JProgress/JPictorialBar |
| 仪表盘 | 2 | JGauge/JColorGauge |
| 散点图 | 2 | JScatter/JBubble |
| 漏斗图 | 2 | JFunnel/JPyramidFunnel |
| 雷达图 | 2 | JRadar/JCircleRadar |
| 组件 | 13 | JForm/JCarousel/JIframe/JCalendar/JMultiViewCalendar/JImg/JText/JNumber/JRadioButton/JFilterQuery/JCustomButton/JCurrentTime/JDragEditor |
| 表单 | 2 | online/design（需弹窗选择表单） |
| 布局 | 2 | JTabs/JGrid |
| 数据/表格 | 5 | JCommonTable/JList/JCommon/JCustomEchart/JPivotTable |
| 地图 | 7 | JBubbleMap/JFlyLineMap/JBarMap/JTotalFlyLineMap/JTotalBarMap/JHeatMap/JAreaMap |
| 首页 | 6 | JQuickNav/JGrowCard/JProjectCard/JSimpleCard/JWaitMatter/JDynamicInfo |
| 高级 | 1+ | JCommon（自定义）+ 3D组件 |
| **总计** | **~58** | 标准 compType（不含 3D/特殊） |

---

## 注意事项

1. **JPie/JRose 直接挂在图表分类下**，不在子分类中（与大屏结构不同）
2. **online/design 组件**：点击后弹出表单选择弹窗，不直接添加组件
3. **JCommon 重复注册**：在"组件/数据列表"和"高级"两个分类下都有 JCommon
4. **无大屏专用组件**：JBorderBox/JDragBorder/JDragDecoration 等装饰类组件只在大屏中
5. **无弹窗功能**：仪表盘不支持大屏的 popup 弹窗组件
6. **JIframe 特殊处理**：添加时弹出 URL 配置弹窗（`iframeSetVisible.value = true`）
7. **JDragEditor 特殊处理**：添加时弹出富文本编辑弹窗
