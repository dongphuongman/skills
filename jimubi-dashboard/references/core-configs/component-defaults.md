# 仪表盘组件默认配置完整参考

> 提取自 `packages/dragEngine/components/jeecgComponents/data.ts`（menuData 仪表盘段）
> 所有组件通过 `menuData` 数组注册，每个组件的 `compConfig` 包含默认尺寸、数据、选项。
> 完整 JSON 数据见 `references/scripts/default_configs.json`。

---

## 与大屏的关键差异

| 项目 | 仪表盘 | 大屏 |
|------|--------|------|
| 尺寸单位 | 栅格（w:12=半宽，h:30=标准高）| 像素（w:450, h:300）|
| option.card | **必须存在**（title/extra/rightHref/size）| 无此字段 |
| 背景色 | `background: '#FFFFFF'`（白色）| `background: '#FFFFFF00'`（透明）|
| 位置字段 | x/y 为栅格坐标，mobileX/mobileY 为移动端 | x/y 为像素坐标 |

---

## 通用 compConfig 结构模板

```javascript
compConfig: {
  w: 12,               // 栅格宽度（1-24，12=半宽）
  h: 30,               // 栅格高度（30=标准图表高）
  dataType: 1,         // 1=URL/静态, 2=数据集, 4=自定义(Online表单)
  url: 'http://api.jeecg.com/mock/33/chart',  // 默认 mock API
  timeOut: 0,          // 请求超时（0=无限）
  turnConfig: { url: '' },                    // 跳转配置
  linkageConfig: [],                          // 联动配置
  dataMapping: [
    { filed: '维度', mapping: '' },
    { filed: '数值', mapping: '' },
  ],
  chartData: [...],    // 静态示例数据（数组格式）
  option: {
    card: {            // 仪表盘特有！卡片头配置
      title: '',
      extra: '',
      rightHref: '',
      size: 'default',
    },
    title: { text: '图表名称', show: true, textStyle: { fontWeight: 'normal' } },
    // ... ECharts 配置
  },
}
```

---

## 组件默认配置速查

### 柱形图系列

#### JBar（基础柱形图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ name:'苹果', value:1000879, type:'手机品牌' }, ...]`（5条，name=维度, value=数值, type=分组）
- option 关键字段：
  - `grid: { show:false, top:90, bottom:115, containLabel:true }`
  - `yAxis: { yUnit:'', splitLine:{interval:2} }`
  - `series[0]: { type:'bar', barWidth:40, itemStyle:{color:'#64b5f6', borderRadius:0}, label:{position:'top'} }`
  - `card: { title:'', extra:'', rightHref:'', size:'default' }`

#### JStackBar（堆叠柱形图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ name, value, type }]`（18条，type=分组维度，前端动态生成多系列）
- option 关键字段：`grid: { bottom:115, top:90 }`，`series: []`（运行时生成）

#### JDynamicBar（动态柱形图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ name, value, type }]`（9条，带动画翻页效果）
- option 关键字段：`grid: { bottom:65, top:50 }`，`series: []`

#### JHorizontalBar（基础条形图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ name, value, type }]`（5条）
- option 关键字段：
  - `xAxis: { type:'value' }`, `yAxis: { type:'category', yUnit:'' }`
  - `series[0]: { type:'bar', barWidth:20, itemStyle:{color:'#64b5f6'} }`

#### JBackgroundBar（背景柱形图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ name, value, type }]`（5条）
- option 关键字段：
  - `series[0]: { showBackground:true, backgroundStyle:{color:'rgba(180,180,180,0.2)'}, itemStyle:{color:'#5470c6'} }`

#### JMultipleBar（多数据对比柱形图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ name, value, type }]`（18条，多 type 分组）
- option 关键字段：`series: []`（按 type 动态分组）

#### JNegativeBar（正负条形图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ name, value, type }]`（21条，value 可为负数）
- option 关键字段：`xAxis: { type:'value' }`，轴从负数到正数

#### JMixLineBar（折柱图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ name, value, type }]`（18条）
- 额外字段：`seriesType: [{ series:'系列名', type:'bar'|'line' }]`

---

### 饼图系列

#### JPie（基础饼图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ value:1048, name:'vivo' }, ...]`（5条，注意字段顺序 value 在前）
- option 关键字段：
  - `innerRadius:60, outRadius:100`
  - `legend: { orient:'vertical', left:'left' }`
  - `series[0]: { type:'pie', radius:'50%', data:[] }`

#### JRose（玫瑰图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ value, name }]`（5条）
- option 关键字段：`series[0]: { type:'pie', roseType:'area' }`

#### JRing（环形图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ value, name }]`（5条）
- option 关键字段：`series[0]: { type:'pie', radius:['40%','70%'] }`

---

### 折线图系列

#### JLine（基础折线图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ value:1000, name:'联想' }, ...]`（5条）
- option 关键字段：`series[0]: { type:'line', smooth:false, data:[] }`

#### JSmoothLine（平滑曲线图）
- **w:12, h:30**（源码无 w/h，使用默认值）, dataType:1
- chartData 格式：`[{ value, name }]`（5条）
- option 关键字段：`series[0]: { type:'line', smooth:true }`

#### JStepLine（阶梯折线图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ value, name }]`（5条）
- option 关键字段：`series[0]: { type:'line', step:'start' }`

#### JMultipleLine（多数据对比折线图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ name, value, type }]`（18条，多 type 分组）
- option 关键字段：`series: []`（运行时按 type 动态生成）

#### DoubleLineBar（双轴图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ name, value, type }]`（18条）
- 双 Y 轴，部分系列对应左轴，部分对应右轴

#### JArea（面积图）
- **w:12, h:30**（源码无 w/h，使用默认值）, dataType:1
- chartData 格式：`[{ value, name }]`（5条）
- option 关键字段：`series[0]: { type:'line', areaStyle:{}, data:[] }`

---

### 进度/仪表系列

#### JCustomProgress（基础进度图）
- **w:12, h:10**, dataType:1
- chartData 格式：`[{ name:'进度1', value:60 }]`（1条）
- 无 card 字段，无 ECharts series

#### JProgress（进度图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ name, value }]`（1条）
- 无 card 字段

#### JGauge（标准仪表盘）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ min:0, max:100, label:'完成率', value:66.6, unit:'%' }]`（1条）
- option 关键字段：`series[0]: { type:'gauge' }`，`card: { title:'标准仪表盘' }`

#### JColorGauge（多色仪表盘）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ name:'完成率', value:66.6 }]`（1条）
- option 关键字段：多色渐变仪表盘，`series: []`（动态生成）

#### JPictorialBar（象形柱图）
- **w:12, h:30**（源码无 w/h，使用默认值）, dataType:1
- chartData 格式：`[{ name, value, symbol:'path://...', symbolSize:[20,20] }, ...]`（8条）
- option 关键字段：`series[0]: { type:'pictorialBar' }`

---

### 散点/气泡图

#### JScatter（散点图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ name, value }]`（5条，value 为数值）
- option 关键字段：`series[0]: { type:'scatter' }`

#### JBubble（气泡图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ name, value, type }]`（18条，多分组）
- option 关键字段：`series[0]: { type:'scatter', symbolSize:函数 }`

---

### 漏斗/雷达图

#### JFunnel（基础漏斗图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ value:100, name:'展现' }, ...]`（3条）
- option 关键字段：`series[0]: { type:'funnel', sort:'descending' }`

#### JPyramidFunnel（金字塔漏斗）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ value, name }]`（5条）
- option 关键字段：`series[0]: { type:'funnel', sort:'ascending' }`

#### JRadar（基础雷达图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ value, name, type, max }]`（6条，max=轴最大值）
- option 关键字段：`radar: { indicator:[...] }`，`series[0]: { type:'radar' }`

#### JCircleRadar（圆形雷达图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ value, name, type, max }]`（6条）
- option 关键字段：`radar: { shape:'circle' }`

---

### 表格/列表系列

#### JCommonTable（数据表格）
- **w:24, h:42**, dataType:1
- chartData 格式：`[{ name:'姓名', value:'张三' }, ...]`（6条键值对）
- option 关键字段：`columns: []`（列配置），`tableConfig: { bordered:true }`

#### JList（数据列表）
- **w:12, h:24**, dataType:1
- chartData 格式：`[{ title:'列表项标题', date:'2024-01-01' }, ...]`（5条）

#### JPivotTable（透视表）
- **w:24, h:42**, dataType:1
- chartData 为复杂对象格式（x/y 轴数据），通常绑定数据集（dataType:2）

#### JCommon（通用/自定义组件）
- **w:12, h:30**（源码无 w/h，使用默认值）, dataType:1
- chartData 格式：`[{ value, name }]`（1条）
- 支持 customOption 自定义 ECharts 配置字符串

#### JCustomEchart（自定义图表）
- **w:12, h:30**（源码无 w/h，使用默认值）, dataType:1
- chartData 为复杂对象，支持完全自定义 ECharts option

---

### 首页/卡片系列

#### JQuickNav（快捷导航）
- **w:12, h:26**, dataType:1
- chartData 格式：`[{ title:'导航项', icon:'图标名', color:'#颜色' }, ...]`（6条）

#### JGrowCard（增长统计卡片）
- **w:12, h:19**, dataType:1
- chartData 格式：`[{ title:'用户访问量', icon:'图标', value:2000, total:120000, prefix:'', color:'#40c9c6', action:'月' }, ...]`（4条）

#### JProjectCard（项目列表卡片）
- **w:12, h:33**, dataType:1
- chartData 格式：`[{ title, icon, color, desc:'描述', group:'分组', date:'日期' }, ...]`（6条）

#### JSimpleCard（简单统计卡片）
- **w:24, h:14**, dataType:1
- chartData 格式：`[{ title, icon, value, color:'#颜色', suffix:'后缀单位' }, ...]`（4条）

#### JWaitMatter（待处理事项）
- **w:12, h:19**, dataType:1
- chartData 格式：`[{ title, icon, content:'内容', desc:'描述', date:'日期' }, ...]`（3条）

#### JDynamicInfo（最新动态）
- **w:12, h:28**, dataType:1
- chartData 格式：`[{ name:'张三', date:'2024-01-01', desc:'描述文字', avatar:'头像URL' }, ...]`（4条）

---

### 功能/布局组件

#### JForm（表单）
- **w:24, h:12**, dataType:1
- 需要关联 Online 表单或设计器表单

#### JCarousel（轮播图）
- **w:24, h:22**, dataType:1
- chartData 格式：`[{ src:'图片URL' }, ...]`（3条）

#### JIframe（内嵌框架）
- **w:12, h:26**, dataType:1
- 有 card 字段，chartData 为 URL 字符串

#### JCalendar（日历）
- **w:10, h:40**, dataType:1
- chartData 格式：`[{ title:'事件标题', start:'2024-01-01', end:'2024-01-02', color:'#颜色', allday:true }, ...]`（2条）

#### JMultiViewCalendar（多视图日历）
- **w:10, h:40**, dataType:1
- option 从 `calendarNewOption` 生成（动态）

#### JImg（图片）
- **w:6, h:26**, dataType:1
- 有 card 字段，chartData 为空

#### JText（文本）
- **w:4, h:4**, dataType:1
- 有 card 字段，chartData 为文本字符串

#### JNumber（数值卡）
- **w:12, h:30**, dataType:1
- 有 card 字段，chartData 为对象（含 value/prefix/suffix 等）

#### JRadioButton（单选按钮）
- **w:8, h:12**, dataType:1
- chartData 格式：`[{ title:'选项A', value:'a', href:'', data:{} }, ...]`（2条）
- 用于联动筛选

#### JFilterQuery（查询过滤）
- **w:12, h:12**, dataType:1
- chartData 为空数组，用于页面筛选联动

#### JCustomButton（自定义按钮）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ btnId, title, icon, color, operationType, worksheet, view, defVal, customPage, href, openMode, bizFlow, click }]`（1条）

#### JCurrentTime（当前时间）
- **w:5, h:6**, dataType:1
- 有 card 字段，无 chartData

#### JDragEditor（富文本编辑器）
- **w:12, h:30**, dataType:1
- chartData 为 HTML 字符串

#### JTabs（选项卡）
- **w:12, h:40**，无 dataType

#### JGrid（栅格布局）
- **w:12, h:40**, dataType:1
- 有 card 字段

---

### 地图系列

#### JAreaMap（区域地图）
- **w:12, h:30**, dataType:1
- chartData 格式：`[{ name:'北京', value:100 }, ...]`（省市数据）
- option 关键字段：`areaName:'china'`，`series: []`

#### JBubbleMap（散点地图）
- **w:12, h:30**, dataType:1
- chartData 格式：含经纬度的数据点

#### JFlyLineMap（飞线地图）
- **w:12, h:30**, dataType:1
- chartData 格式：含起终点坐标的飞线数据

#### JBarMap（柱形地图）
- **w:12, h:30**, dataType:1

#### JTotalFlyLineMap（综合飞线地图）
- **w:12, h:30**, dataType:1

#### JTotalBarMap（综合柱形地图）
- **w:12, h:30**, dataType:1

#### JHeatMap（热力地图）
- **w:12, h:30**, dataType:1
- chartData 格式：含热力值和坐标的数据点

---

## 仪表盘组件的 option.card 字段

**所有仪表盘 ECharts 图表组件必须包含 `option.card` 字段：**

```json
"card": {
  "title": "",       // 卡片标题（留空则使用 option.title.text）
  "extra": "",       // 右上角额外内容
  "rightHref": "",   // 右上角链接
  "size": "default"  // 卡片尺寸：default/small/large
}
```

有 card 字段的组件（来自源码 menuData）：
JBar, JStackBar, JDynamicBar, JHorizontalBar, JBackgroundBar, JMultipleBar, JNegativeBar, JMixLineBar,
JPie, JRose, JLine, JSmoothLine, JStepLine, JMultipleLine, DoubleLineBar, JRing, JArea, JPictorialBar,
JGauge, JColorGauge, JScatter, JBubble, JFunnel, JPyramidFunnel, JRadar, JCircleRadar,
JIframe, JImg, JText, JNumber, JCurrentTime, JGrid, JCommon, JCustomEchart, JPivotTable,
JBubbleMap, JFlyLineMap, JBarMap, JTotalFlyLineMap, JTotalBarMap, JHeatMap, JAreaMap,
JQuickNav, JGrowCard, JProjectCard, JSimpleCard, JWaitMatter

无 card 字段的组件：
JCustomProgress, JProgress, JForm, JCarousel, JCalendar, JMultiViewCalendar, JRadioButton,
JFilterQuery, JCustomButton, JDragEditor, JTabs, JCommonTable, JList, JDynamicInfo

---

## 数据绑定关键差异（与大屏对比）

| 场景 | 仪表盘 | 大屏 |
|------|--------|------|
| dataType=1 | URL 接口模式 | 同左 |
| dataType=2 | SQL/API/File 数据集 | 同左 |
| dataType=4 | Online/设计器表单图表 | 同左（不同字段配置）|
| fieldOption | `{fieldName:'', fieldValue:''}` | 同左 |
| dataMapping | `[{filed:'维度',mapping:''}]` | 同左 |

---

## 重要说明

- **数据来源文件**：`jeecgComponents/data.ts`（menuData，行2~7151），不是 `config.ts`
- **config.ts**：是 UI 配置面板（getOptionConfig 函数），描述组件的可编辑属性列表，不含默认值
- **default_configs.json**：从 menuData 提取的每个组件 compConfig 的完整默认值，是创建组件时的初始状态
