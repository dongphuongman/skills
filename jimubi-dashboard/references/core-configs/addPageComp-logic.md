# 仪表盘组件创建逻辑参考

> 提取自 `packages/dragEngine/otherStyles/DragEngineJeecg.vue`
> 描述仪表盘中新组件如何被添加到页面，以及页面保存的完整流程。

---

## addPageComp 函数流程

**位置**: DragEngineJeecg.vue 第 541-602 行

### 入参
```typescript
addPageComp(item: MenuItemConfig)
```
- `item`: 菜单项配置，含 `name`, `compType`, `compConfig`（注意：仪表盘版本**无 position 参数**，大屏版有）

### 执行流程

```
1. 组件数量上限检查 → MAX_COMPONENT = 20（超过提示警告）
2. online/design 类型 → 弹出表单选择弹窗（onlineRef.value.showModal()）
3. 解析 compConfig（字符串→对象，默认 { size: {} }）
4. calcAttr(config, item) → 计算 w/h/maxY（栅格坐标）
5. 构建 newItem 对象
6. calcPosition(newItem) → 计算 x/y 坐标（避开已占位置）
   注意：designType===30（移动端视图）时跳过 calcPosition
7. 特殊组件处理：
   - JIframe → 弹出 URL 配置弹窗（iframeSetVisible.value = true）
   - JCustomCard → 弹出自定义卡片弹窗
   - JDragEditor → 弹出富文本编辑弹窗
8. 标准路径 → dragData.componentData.push(newItem)
   注意：仪表盘用 push()（追加到末尾），大屏用 unshift()（插入到首位）
9. calcScollHeight(newItem.x) → 重新计算滚动高度
```

---

## newItem 对象结构

```javascript
let newItem = {
  config: obj.config,              // 完整配置对象（来自 compConfig）
  component: item.compType || item.value,  // 组件类型（如 'JBar'）
  i: uuid(),                       // 唯一标识符
  x: 0,                            // X 坐标（栅格列，0-23）
  y: obj.maxY,                     // Y 坐标（栅格行，自动计算）
  w: obj.w || 12,                  // 宽度（栅格单位，默认12）
  h: obj.h || 30,                  // 高度（栅格单位，默认30）
  orderNum: obj.maxY,              // 排序号
};
```

**注意**：仪表盘的 newItem **没有** `componentName` 字段（大屏有此字段，对应图层名）。

---

## calcAttr 位置计算

**位置**: `packages/dragEngine/hooks/useDragBiz.ts` 第 165-180 行

```javascript
function calcAttr(config, newComp) {
  // 1. 获取 x=0 列所有组件的 Y 值
  let yArr = dragData['componentData']
    .filter(item => item.x === 0)
    .map(item => item.y);

  // 2. 找最大 Y 值
  let currentMaxY = yArr.length > 0 ? Math.max(...yArr) : 0;

  // 3. 找到该 Y 值对应的组件
  let maxYItem = dragData['componentData']
    .filter(item => item.y === currentMaxY);

  // 4. 新组件 Y = 最底部组件的 y + h
  let maxY = maxYItem.length > 0 ? currentMaxY + maxYItem[0].h : 0;

  // 5. 设置高度（优先使用 newComp.h，其次 config.h，默认 30）
  let h = newComp && newComp.h ? newComp.h : (config?.h || 30);
  let height = h * 10;             // size.height 为栅格高度×10（像素近似）
  config['size'] = { height };

  return { w: config.w, maxY, h, config };
}
```

**注意**：仪表盘的高度**不像大屏那样做 `h<40 → h×10` 的缩放处理**，栅格高度就是栅格高度。

---

## calcPosition 网格布局算法

**位置**: `packages/dragEngine/hooks/useDragBiz.ts` 第 185-234 行

```javascript
function calcPosition(newItem) {
  // 1. 计算最大 Y（所有组件的 y+h 的最大值）
  let Ys = dragData['componentData'].map(item => item.y + item.h);
  let maxY = (Ys.length && Math.max.apply(null, Ys)) || 1;
  let edgeX = 24;   // 24列栅格
  let edgeY = maxY;

  // 2. 生成二维占位图（edgeX × edgeY）
  let gridMap = new Array(edgeX).fill(null)
    .map(() => new Array(edgeY).fill(0));

  // 3. 标记已占位置为1
  dragData['componentData'].map(item => {
    for (let x = item.x; x < item.x + item.w; x++)
      for (let y = item.y; y < item.y + item.h; y++)
        gridMap[x][y] = 1;
  });

  // 4. 遍历坐标，找第一个可放置位置
  for (let y = 0; y < edgeY; y++) {
    for (let x = 0; x < edgeX; x++) {
      if (edgeX - x >= newItem.w && edgeY - y >= newItem.h) {
        // 检查目标区域是否全为0（空闲）
        let itemSignArr = [];
        for (let a = x; a < x + newItem.w; a++)
          for (let b = y; b < y + newItem.h; b++)
            itemSignArr.push(gridMap[a][b]);
        if (itemSignArr.indexOf(1) < 0) {
          newItem.x = x;
          newItem.y = y;
          return;
        }
      }
    }
  }
  // 找不到时：组件追加到最底部（不设置 x/y，保持原始 maxY）
}
```

**关键规则**：优先寻找已有空间中的空隙，找不到才追加到底部。

---

## 保存流程（saveDragData）

**位置**: DragEngineJeecg.vue 第 432-499 行

### 1. 前置校验（商业版限制检查）
```javascript
// 免费版检查页面数量/数据库表数量上限
if (DRAG_LIMIT_SWITCH) { ... }
```

### 2. 设置移动端/PC 定位
```javascript
cacheData.forEach((item, index) => {
  item.mobileX = 0;
  item.mobileY = index;   // 移动端按索引排序
  item.pcX = item.x;
  item.pcY = item.y;
});
```

### 3. 构建保存对象
```javascript
let data = {
  id: props.pageId,             // 页面 ID
  name: dragData['name'],       // 页面名称
  backgroundColor: dragData['backgroundColor'],
  theme: dragData['theme'] || 'default',
  style: dragData['style'] || 'default',
  coverUrl: dragData['coverUrl'],
  designType: dragData['designType'] || 100,   // 100=PC端
  backgroundImage: dragData['backgroundImage'],
  template: formatData(cacheData),              // 组件数组序列化（JSON字符串）
  updateCount: dragData['updateCount'],         // 乐观锁版本号
};
```

### 4. API 调用
```javascript
savePage(data).then(res => {
  if (res.data.success) {
    dragData['updateCount'] = res.data.result.updateCount;  // 更新版本号
  }
});
```

**API 端点**：`POST /drag/page/edit`（`packages/dragEngine/api.ts` 中定义）

### 5. IndexedDB 缓存
```javascript
dragEngineAppStorage.setItem(
  'dragEngineApp:cacheData:' + props.pageId,
  JSON.stringify(dragData)
);
```
保存前会先写入 IndexedDB 作为本地缓存（用于断网恢复）。

---

## 乐观锁机制（updateCount）

- `updateCount` 是后端返回的页面版本号
- 每次保存后，后端返回新的 `updateCount`，前端更新
- 下次保存时携带当前 `updateCount` 供后端校验
- 防止多人同时编辑时产生冲突覆盖

**与大屏的区别**：大屏也有相同机制，但大屏的保存还包含 `desJson`（画布宽高、水印等配置），仪表盘不包含 `desJson`。

---

## componentData 数组结构

```javascript
dragData.componentData = [
  {
    config: {
      w: 12,
      h: 30,
      dataType: 1,
      url: '...',
      chartData: [...],
      option: {
        card: { title:'', extra:'', rightHref:'', size:'default' },
        title: { text:'基础柱形图', show:true },
        // ... ECharts 配置
      },
      size: { height: 300 },    // 由 calcAttr 设置
    },
    component: 'JBar',          // 组件类型（用于渲染）
    i: 'uuid-string',           // 唯一 ID
    x: 0,                       // 栅格 X 坐标（0-23）
    y: 0,                       // 栅格 Y 坐标
    w: 12,                      // 栅格宽度
    h: 30,                      // 栅格高度
    orderNum: 0,                // 排序号
    mobileX: 0,                 // 保存时设置
    mobileY: 0,                 // 保存时按索引设置
    pcX: 0,                     // 保存时等于 x
    pcY: 0,                     // 保存时等于 y
  },
  // ...
]
```

**注意**：仪表盘 componentData 元素**没有** `componentName`（图层名）和 `visible` 字段，这两个字段是大屏专有的。

---

## 仪表盘 vs 大屏 addPageComp 对比

| 特性 | 仪表盘（DragEngineJeecg） | 大屏（DragEngineScreen）|
|------|--------------------------|------------------------|
| 添加方式 | `push`（末尾追加）| `unshift`（头部插入）|
| 坐标系 | 栅格坐标（0-23列）| 像素坐标 |
| position 参数 | 无 | 有（可指定精确位置）|
| componentName | 无 | 有（图层名显示）|
| visible 字段 | 无 | 有 |
| 历史记录 | 无显式 history.add | 有撤销/重做 |
| 自定义颜色 | 无 sysDefColor | 有 customColor 支持 |
| group 模式 | 无 | 有（组容器模式）|
| 保存 API | `POST /drag/page/edit` | `POST /drag/page/edit`（相同端点！）|
| 保存体差异 | 无 `desJson` | 有 `desJson`（画布配置）|

---

## 关键常量（constant.ts）

| 常量 | 值 | 说明 |
|------|---|------|
| MAX_COMPONENT | 20 | 单页最大组件数 |
| DRAG_PAGE_LIMIT_NUM | (免费版限制) | 免费版最多仪表盘数 |
| TABLE_LIMIT_NUM | (免费版限制) | 免费版最多数据库表数 |
