# -*- coding: utf-8 -*-
"""
大屏/仪表盘组件操作工具 —— 增、删、改、查
============================================

使用方式（命令行）：

  # 查看页面所有组件
  py comp_ops.py list <API_BASE> <TOKEN> <PAGE_ID>

  # 删除组件（按名称或类型）
  py comp_ops.py delete <API_BASE> <TOKEN> <PAGE_ID> --name "组件名"
  py comp_ops.py delete <API_BASE> <TOKEN> <PAGE_ID> --type "JAreaMap"
  py comp_ops.py delete <API_BASE> <TOKEN> <PAGE_ID> --id "组件i值"

  # 编辑组件属性（JSON path 赋值）
  py comp_ops.py edit <API_BASE> <TOKEN> <PAGE_ID> --name "基础柱形图" --set "option.series[0].itemStyle.color=#FFD700"
  py comp_ops.py edit <API_BASE> <TOKEN> <PAGE_ID> --type "JBar" --set "option.title.text=新标题"
  py comp_ops.py edit <API_BASE> <TOKEN> <PAGE_ID> --name "文本" --set "chartData.value=新文本内容"
  py comp_ops.py edit <API_BASE> <TOKEN> <PAGE_ID> --name "数字指标" --set "option.body.fontSize=48" --set "option.body.color=#FF0000"

  # 添加组件（JSON config）
  py comp_ops.py add <API_BASE> <TOKEN> <PAGE_ID> --comp "JBar" --title "新柱形图" --x 50 --y 500 --w 450 --h 300
  py comp_ops.py add <API_BASE> <TOKEN> <PAGE_ID> --comp "JText" --title "标题文本" --x 560 --y 15 --w 800 --h 60 --config '{"chartData":{"value":"大屏标题"},"option":{"body":{"color":"#ffffff","fontSize":42,"fontWeight":"bold"}}}'

  # 移动/缩放组件
  py comp_ops.py move <API_BASE> <TOKEN> <PAGE_ID> --name "基础柱形图" --x 100 --y 200 --w 600 --h 400
"""

import sys, json, os, argparse

# ============================================================
# bi_utils 加载（自动查找）
# ============================================================
def _find_bi_utils():
    """按优先级查找 bi_utils.py"""
    candidates = [
        os.path.dirname(os.path.abspath(__file__)),                    # 同目录
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'),# 上级目录(references/)
        os.getcwd(),                                                    # 当前工作目录
    ]
    for d in candidates:
        p = os.path.join(d, 'bi_utils.py')
        if os.path.exists(p):
            return d
    return None

_bu_dir = _find_bi_utils()
if _bu_dir:
    sys.path.insert(0, _bu_dir)
import bi_utils
from bi_utils import init_api, query_page, save_page


# ============================================================
# 核心操作函数
# ============================================================
def load_template(page_id):
    """加载页面模板，返回组件列表"""
    page = query_page(page_id)
    tmpl = page.get('template', [])
    if isinstance(tmpl, str):
        tmpl = json.loads(tmpl)
    # 确保每个组件的 config 是 dict
    for comp in tmpl:
        cfg = comp.get('config', {})
        if isinstance(cfg, str):
            try:
                comp['config'] = json.loads(cfg)
            except:
                comp['config'] = {}
    return tmpl


def save_template(page_id, tmpl):
    """保存组件列表到页面"""
    # config 转回字符串供 save_page 使用
    for comp in tmpl:
        cfg = comp.get('config', {})
        if isinstance(cfg, dict):
            comp['config'] = cfg  # bi_utils save_page 内部会 json.dumps template
    bi_utils._page_components[page_id] = tmpl
    save_page(page_id)


def find_components(tmpl, name=None, comp_type=None, comp_id=None):
    """在 template 中查找组件（包括 JGroup 内部）"""
    results = []
    for comp in tmpl:
        matched = False
        if comp_id and comp.get('i') == comp_id:
            matched = True
        elif name and comp.get('componentName', '') == name:
            matched = True
        elif comp_type and comp.get('component') == comp_type:
            matched = True
        if matched:
            results.append(('top', comp))
        # 检查 JGroup 内部
        if comp.get('component') == 'JGroup':
            elements = comp.get('props', {}).get('elements', [])
            for el in elements:
                el_matched = False
                if comp_id and el.get('i') == comp_id:
                    el_matched = True
                elif name and el.get('componentName', '') == name:
                    el_matched = True
                elif comp_type and el.get('component') == comp_type:
                    el_matched = True
                if el_matched:
                    results.append(('group', el, comp))
    return results


def set_nested(obj, path, value):
    """
    按路径设置嵌套字典的值。
    支持: option.series[0].itemStyle.color, chartData.value, option.body.fontSize
    """
    parts = []
    for p in path.split('.'):
        # 解析数组索引 如 series[0]
        if '[' in p:
            key = p[:p.index('[')]
            idx = int(p[p.index('[')+1:p.index(']')])
            parts.append(('key', key))
            parts.append(('idx', idx))
        else:
            parts.append(('key', p))

    current = obj
    for i, (kind, val) in enumerate(parts[:-1]):
        if kind == 'key':
            if isinstance(current, dict):
                if val not in current:
                    # 看下一步是数组还是字典
                    next_kind = parts[i+1][0] if i+1 < len(parts) else 'key'
                    current[val] = [] if next_kind == 'idx' else {}
                current = current[val]
        elif kind == 'idx':
            if isinstance(current, list):
                while len(current) <= val:
                    current.append({})
                current = current[val]

    last_kind, last_val = parts[-1]
    if last_kind == 'key':
        # 自动类型转换
        if isinstance(current, dict):
            current[last_val] = _auto_type(value)
    elif last_kind == 'idx':
        if isinstance(current, list):
            while len(current) <= last_val:
                current.append({})
            current[last_val] = _auto_type(value)


def _auto_type(val):
    """字符串自动转换为合适类型"""
    if isinstance(val, str):
        if val.lower() == 'true':
            return True
        if val.lower() == 'false':
            return False
        if val.lower() == 'null' or val.lower() == 'none':
            return None
        try:
            if '.' in val:
                return float(val)
            return int(val)
        except ValueError:
            pass
        # 尝试 JSON 解析
        if val.startswith('{') or val.startswith('['):
            try:
                return json.loads(val)
            except:
                pass
    return val


# ============================================================
# 命令实现
# ============================================================
def cmd_list(args):
    """列出页面所有组件"""
    tmpl = load_template(args.page_id)
    print(f'页面共 {len(tmpl)} 个组件：\n')
    print(f'{"序号":<4} {"组件ID":<36} {"类型":<20} {"名称":<20} {"位置":<12} {"尺寸":<12}')
    print('-' * 110)
    for i, comp in enumerate(tmpl):
        cid = comp.get('i', '?')
        ctype = comp.get('component', '?')
        cname = comp.get('componentName', '')
        x, y = comp.get('x', 0), comp.get('y', 0)
        w, h = comp.get('w', 0), comp.get('h', 0)
        print(f'{i+1:<4} {cid:<36} {ctype:<20} {cname:<20} ({x},{y}){"":<4} {w}x{h}')
        # JGroup 内部
        if ctype == 'JGroup':
            elements = comp.get('props', {}).get('elements', [])
            for j, el in enumerate(elements):
                eid = el.get('i', '?')
                etype = el.get('component', '?')
                ename = el.get('componentName', '')
                ex, ey = el.get('x', 0), el.get('y', 0)
                ew, eh = el.get('w', 0), el.get('h', 0)
                print(f'  └{j+1:<2} {eid:<36} {etype:<20} {ename:<20} ({ex},{ey}){"":<4} {ew}x{eh}')


def cmd_delete(args):
    """删除组件"""
    tmpl = load_template(args.page_id)
    original_count = len(tmpl)

    new_tmpl = []
    removed = 0
    for comp in tmpl:
        # 检查 JGroup 内部
        if comp.get('component') == 'JGroup':
            elements = comp.get('props', {}).get('elements', [])
            new_elements = []
            for el in elements:
                if _match_comp(el, args):
                    removed += 1
                    print(f'  删除(组内): {el.get("componentName", "")} ({el.get("component", "")})')
                else:
                    new_elements.append(el)
            comp['props']['elements'] = new_elements

        if _match_comp(comp, args):
            removed += 1
            print(f'  删除: {comp.get("componentName", "")} ({comp.get("component", "")})')
        else:
            new_tmpl.append(comp)

    if removed == 0:
        print('未找到匹配的组件')
        return

    save_template(args.page_id, new_tmpl)
    print(f'共删除 {removed} 个组件，剩余 {len(new_tmpl)} 个')


def cmd_edit(args):
    """编辑组件属性"""
    tmpl = load_template(args.page_id)

    edited = 0
    for comp in tmpl:
        targets = []
        if _match_comp(comp, args):
            targets.append(comp)
        # JGroup 内部
        if comp.get('component') == 'JGroup':
            for el in comp.get('props', {}).get('elements', []):
                if _match_comp(el, args):
                    targets.append(el)

        for target in targets:
            cfg = target.get('config', {})
            if isinstance(cfg, str):
                try:
                    cfg = json.loads(cfg)
                except:
                    cfg = {}
                target['config'] = cfg

            for s in args.set:
                if '=' not in s:
                    print(f'无效的 --set 参数（需要 key=value 格式）: {s}')
                    continue
                path, value = s.split('=', 1)
                set_nested(cfg, path, value)
                print(f'  设置 {target.get("componentName","")}: config.{path} = {value}')
            edited += 1

    if edited == 0:
        print('未找到匹配的组件')
        return

    save_template(args.page_id, tmpl)
    print(f'共编辑 {edited} 个组件')


def _load_default_configs():
    """加载 default_configs.json，返回字典；找不到返回 {}"""
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'default_configs.json'),
        os.path.join(os.getcwd(), 'default_configs.json'),
    ]
    for p in candidates:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                return json.load(f)
    return {}


def _build_comp_config(comp_type, title, custom_config=None):
    """
    构建单个组件的 config：
    1. 先从 default_configs.json 深拷贝完整默认配置
    2. 再用 custom_config 覆盖
    """
    import copy
    defaults = _load_default_configs()
    config = copy.deepcopy(defaults.get(comp_type, {}))

    # 确保基础字段存在
    config.setdefault('background', '#FFFFFF')
    config.setdefault('borderColor', '#E8E8E8')
    config.setdefault('dataType', 1)
    if 'option' not in config:
        config['option'] = {}
    config['option'].setdefault('card', {'title': '', 'extra': '', 'rightHref': '', 'size': 'default'})

    # chartData 必须是 JSON 字符串
    if 'chartData' in config and not isinstance(config['chartData'], str):
        config['chartData'] = json.dumps(config['chartData'], ensure_ascii=False)

    # 如果 default_configs.json 中也没有 chartData，给最小兜底数据
    if 'chartData' not in config or config.get('chartData') in ('[]', '', None):
        _line_data = [{"name":"1月","value":820},{"name":"2月","value":932},{"name":"3月","value":901},{"name":"4月","value":760},{"name":"5月","value":1090},{"name":"6月","value":1230}]
        _bar_data  = [{"name":"A","value":100},{"name":"B","value":200},{"name":"C","value":150},{"name":"D","value":180},{"name":"E","value":130}]
        _pie_data  = [{"name":"直接访问","value":335},{"name":"邮件营销","value":310},{"name":"联盟广告","value":234},{"name":"视频广告","value":135},{"name":"搜索引擎","value":548}]
        _multi_data = [{"name":"1月","value":820,"type":"收入"},{"name":"2月","value":932,"type":"收入"},{"name":"3月","value":901,"type":"收入"},{"name":"1月","value":620,"type":"支出"},{"name":"2月","value":732,"type":"支出"},{"name":"3月","value":701,"type":"支出"}]
        fallback = {
            'JBar':             _bar_data,
            'JStackBar':        _multi_data,
            'JDynamicBar':      _bar_data,
            'JHorizontalBar':   _bar_data,
            'JBackgroundBar':   _bar_data,
            'JMultipleBar':     _multi_data,
            'JNegativeBar':     _multi_data,
            'JPictorialBar':    _bar_data,
            'JMixLineBar':      _multi_data,
            'DoubleLineBar':    _multi_data,
            'JLine':            _line_data,
            'JSmoothLine':      _line_data,
            'JStepLine':        _line_data,
            'JArea':            _line_data,
            'JMultipleLine':    _multi_data,
            'JPie':             _pie_data,
            'JRose':            _pie_data,
            'JRing':            _pie_data,
            'JScatter':         _bar_data,
            'JBubble':          _bar_data,
            'JFunnel':          [{"name":"展现","value":900},{"name":"点击","value":600},{"name":"转化","value":300},{"name":"下单","value":150},{"name":"付款","value":80}],
            'JPyramidFunnel':   [{"name":"展现","value":900},{"name":"点击","value":600},{"name":"转化","value":300},{"name":"下单","value":150},{"name":"付款","value":80}],
            'JRadar':           [{"name":"销售能力","value":85,"type":"实际"},{"name":"市场开拓","value":72,"type":"实际"},{"name":"客户满意","value":90,"type":"实际"},{"name":"团队协作","value":78,"type":"实际"},{"name":"创新能力","value":65,"type":"实际"},{"name":"执行力","value":88,"type":"实际"}],
            'JCircleRadar':     [{"name":"销售能力","value":85,"type":"实际"},{"name":"市场开拓","value":72,"type":"实际"},{"name":"客户满意","value":90,"type":"实际"},{"name":"团队协作","value":78,"type":"实际"},{"name":"创新能力","value":65,"type":"实际"}],
            'JGauge':           [{"name":"速率","value":72}],
            'JColorGauge':      [{"name":"速率","value":72}],
            'JProgress':        [{"name":"季度目标完成率","value":82},{"name":"客户增长率","value":67},{"name":"收入达标率","value":91},{"name":"成本控制率","value":74},{"name":"用户满意度","value":88}],
            'JCustomProgress':  [{"name":"研发部","value":78},{"name":"销售部","value":92},{"name":"市场部","value":65},{"name":"运营部","value":83},{"name":"财务部","value":70}],
            'JNumber':          {"value": 12345},
            'JGrowCard':        [{"name":"总用户数","value":15890,"icon":"user","color":"#1890FF"},{"name":"今日活跃","value":3256,"icon":"fire","color":"#52C41A"}],
            'JSimpleCard':      [{"name":"总收入","value":89600,"icon":"pay-circle","color":"#FA8C16"}],
            'JCommonTable':     [{"name":"张三","value":100},{"name":"李四","value":200},{"name":"王五","value":150}],
            'JList':            [{"name":"项目A","value":100},{"name":"项目B","value":80},{"name":"项目C","value":60}],
            'JScrollRankingBoard': [{"name":"项目A","value":100},{"name":"项目B","value":80},{"name":"项目C","value":60}],
            'JText':            {"value": title or "文本内容"},
            'JWordCloud':       _bar_data,
        }
        data = fallback.get(comp_type, [])
        config['chartData'] = json.dumps(data, ensure_ascii=False) if not isinstance(data, str) else data

    # 注入 option.series 模板（前端访问 series[0] 来获取样式，缺失会报 undefined 错误）
    _BAR_SERIES    = [{"data":[],"type":"bar","barWidth":40,"itemStyle":{"color":"#64b5f6","borderRadius":0},"label":{"show":False,"position":"top"}}]
    _LINE_SERIES   = [{"data":[],"type":"line","smooth":False,"itemStyle":{"color":"#64b5f6"},"lineStyle":{"width":2},"areaStyle":None,"label":{"show":False}}]
    _PIE_SERIES    = [{"data":[],"type":"pie","radius":"70%","center":["50%","55%"],"label":{"show":True},"itemStyle":{}}]
    _STACK_SERIES  = [{"data":[],"type":"bar","stack":"total","barWidth":40,"itemStyle":{"borderRadius":0},"label":{"show":False}}]
    _MULTI_SERIES  = [{"data":[],"type":"bar","barWidth":30,"itemStyle":{"borderRadius":0},"label":{"show":False}}]
    _MIX_SERIES    = [{"data":[],"type":"bar","barWidth":40,"itemStyle":{"color":"#64b5f6"},"label":{"show":False}},
                      {"data":[],"type":"line","smooth":True,"itemStyle":{"color":"#ff7c7c"},"lineStyle":{"width":2},"yAxisIndex":1}]
    _DOUBLE_SERIES = [{"data":[],"type":"bar","barWidth":40,"itemStyle":{"color":"#64b5f6"},"label":{"show":False},"yAxisIndex":0},
                      {"data":[],"type":"line","smooth":True,"itemStyle":{"color":"#ff7c7c"},"lineStyle":{"width":2},"yAxisIndex":1}]
    _RADAR_SERIES  = [{"type":"radar","data":[],"areaStyle":{"opacity":0.3},"lineStyle":{"width":2}}]
    _GAUGE_SERIES  = [{"type":"gauge","data":[],"min":0,"max":100,"startAngle":225,"endAngle":-45,
                       "axisLine":{"lineStyle":{"width":10}},"pointer":{"show":True},
                       "detail":{"formatter":"{value}%","fontSize":18},"title":{"show":True}}]
    _FUNNEL_SERIES = [{"type":"funnel","data":[],"sort":"descending","gap":2,"left":"10%","width":"80%",
                       "label":{"show":True,"position":"inside"},"itemStyle":{}}]
    series_map = {
        'JBar':           _BAR_SERIES,
        'JDynamicBar':    _BAR_SERIES,
        'JHorizontalBar': [{"data":[],"type":"bar","barWidth":30,"itemStyle":{"color":"#64b5f6","borderRadius":0},"label":{"show":False,"position":"right"}}],
        'JBackgroundBar': _BAR_SERIES,
        'JPictorialBar':  [{"data":[],"type":"pictorialBar","itemStyle":{"color":"#64b5f6"},"label":{"show":False}}],
        'JStackBar':      _STACK_SERIES,
        'JMultipleBar':   _MULTI_SERIES,
        'JNegativeBar':   _MULTI_SERIES,
        'JMixLineBar':    _MIX_SERIES,
        'DoubleLineBar':  _DOUBLE_SERIES,
        'JLine':          _LINE_SERIES,
        'JSmoothLine':    [{"data":[],"type":"line","smooth":True,"itemStyle":{"color":"#64b5f6"},"lineStyle":{"width":2},"areaStyle":None,"label":{"show":False}}],
        'JStepLine':      [{"data":[],"type":"line","step":True,"itemStyle":{"color":"#64b5f6"},"lineStyle":{"width":2},"label":{"show":False}}],
        'JArea':          [{"data":[],"type":"line","smooth":False,"itemStyle":{"color":"#64b5f6"},"lineStyle":{"width":2},"areaStyle":{"opacity":0.4},"label":{"show":False}}],
        'JMultipleLine':  [{"data":[],"type":"line","smooth":True,"itemStyle":{"color":"#64b5f6"},"lineStyle":{"width":2},"label":{"show":False}}],
        'JPie':           _PIE_SERIES,
        'JRose':          [{"data":[],"type":"pie","roseType":"area","radius":"70%","center":["50%","55%"],"label":{"show":True}}],
        'JRing':          [{"data":[],"type":"pie","radius":["40%","70%"],"center":["50%","55%"],"label":{"show":True}}],
        'JScatter':       [{"data":[],"type":"scatter","itemStyle":{"color":"#64b5f6"},"symbolSize":10}],
        'JFunnel':        _FUNNEL_SERIES,
        'JPyramidFunnel': [{"type":"funnel","data":[],"sort":"ascending","gap":2,"left":"10%","width":"80%","label":{"show":True,"position":"inside"},"itemStyle":{}}],
        'JRadar':         _RADAR_SERIES,
        'JCircleRadar':   _RADAR_SERIES,
        'JGauge':         _GAUGE_SERIES,
        'JColorGauge':    _GAUGE_SERIES,
    }
    if comp_type in series_map and 'series' not in config.get('option', {}):
        import copy as _copy
        config['option'].setdefault('series', _copy.deepcopy(series_map[comp_type]))

    # 将 chartData 预填充到 option.series[i].data（静态数据直接使用 chartData，不留空 []）
    _cd_raw = config.get('chartData', '[]')
    try:
        _cd = json.loads(_cd_raw) if isinstance(_cd_raw, str) else _cd_raw
    except Exception:
        _cd = []

    _series = config.get('option', {}).get('series')
    if isinstance(_cd, list) and isinstance(_series, list) and len(_series) > 0:
        # 多系列图表（含 type 字段）：按 type 分组，映射到各系列
        _MULTI_TYPES = {'JStackBar','JMultipleBar','JNegativeBar','JMixLineBar','DoubleLineBar','JMultipleLine','JRadar','JCircleRadar'}
        if comp_type in _MULTI_TYPES and _cd and isinstance(_cd[0], dict) and 'type' in _cd[0]:
            from collections import OrderedDict as _OD
            _groups = _OD()
            for _row in _cd:
                _t = _row.get('type', '')
                _groups.setdefault(_t, [])
                _groups[_t].append(_row)
            _tmpl = _series[0]
            _new_series = []
            for _i, (_gname, _rows) in enumerate(_groups.items()):
                import copy as _copy2
                _s = _copy2.deepcopy(_tmpl)
                _s['name'] = _gname
                if comp_type in ('JRadar', 'JCircleRadar'):
                    _s['data'] = [{"value": [r['value'] for r in _rows], "name": _gname}]
                elif comp_type in ('JMixLineBar', 'DoubleLineBar'):
                    _s['type'] = 'bar' if _i == 0 else 'line'
                    _s['data'] = [r['value'] for r in _rows]
                    if 'yAxisIndex' in _tmpl:
                        _s['yAxisIndex'] = _i
                else:
                    _s['data'] = [r['value'] for r in _rows]
                _new_series.append(_s)
            config['option']['series'] = _new_series
            # 提取有序唯一 name 列表 → xAxis.data（多系列图表 x 轴类目）
            if comp_type not in ('JRadar', 'JCircleRadar'):
                _seen_names = []
                for _row in _cd:
                    n = _row.get('name', '')
                    if n not in _seen_names:
                        _seen_names.append(n)
                if not isinstance(config['option'].get('xAxis'), dict):
                    config['option']['xAxis'] = {}
                config['option']['xAxis']['data'] = _seen_names
                config['option']['xAxis']['type'] = 'category'
        # 饼图/漏斗图：data 直接是 [{name, value}] 数组
        elif comp_type in ('JPie','JRose','JRing','JFunnel','JPyramidFunnel','JRotatePie','JActiveRing'):
            _series[0]['data'] = _cd
        # 仪表盘
        elif comp_type in ('JGauge','JColorGauge','JAntvGauge'):
            _series[0]['data'] = [{"value": _cd[0]['value'], "name": _cd[0].get('name','')}] if _cd else []
        # 单系列图表：data 取 value 列表
        else:
            _series[0]['data'] = [r['value'] if isinstance(r, dict) else r for r in _cd]

    # DoubleLineBar 需要双 yAxis
    if comp_type == 'DoubleLineBar' and 'yAxis' not in config.get('option', {}):
        config['option']['yAxis'] = [
            {"type":"value","axisLabel":{"color":"#909198"},"splitLine":{"lineStyle":{"color":"#F3F3F3"}}},
            {"type":"value","axisLabel":{"color":"#909198"},"splitLine":{"show":False}},
        ]

    # JMixLineBar 需要双 yAxis
    if comp_type == 'JMixLineBar' and 'yAxis' not in config.get('option', {}):
        config['option']['yAxis'] = [
            {"type":"value","axisLabel":{"color":"#909198"},"splitLine":{"lineStyle":{"color":"#F3F3F3"}}},
            {"type":"value","axisLabel":{"color":"#909198"},"splitLine":{"show":False}},
        ]

    # 默认 option.title
    if comp_type not in ('JText', 'JDragBorder', 'JDragDecoration', 'JImg', 'JCurrentTime'):
        config['option'].setdefault('title', {
            'text': title or '', 'show': True,
            'textStyle': {'color': '#464646', 'fontSize': 14}
        })

    # 用户自定义 config 覆盖
    if custom_config:
        for k, v in custom_config.items():
            config[k] = v

    # 动态数据（dataType != 1）不使用静态 series data：
    # 清空 option.series[i].data 和 xAxis.data，让前端从数据集重新拉取真实数据
    _final_dtype = config.get('dataType', 1)
    if _final_dtype not in (1, '1'):
        _dyn_series = config.get('option', {}).get('series')
        if isinstance(_dyn_series, list):
            for _s in _dyn_series:
                if isinstance(_s, dict):
                    _s['data'] = []
        _xaxis = config.get('option', {}).get('xAxis')
        if isinstance(_xaxis, dict) and 'data' in _xaxis:
            _xaxis['data'] = []

    return config


def cmd_add(args):
    """添加单个组件（一次 query + save，不得并行调用）"""
    tmpl = load_template(args.page_id)
    bi_utils._page_components[args.page_id] = tmpl

    custom_config = None
    if args.config:
        try:
            custom_config = json.loads(args.config)
        except json.JSONDecodeError as e:
            print(f'config JSON 解析失败: {e}')
            return

    config = _build_comp_config(args.comp, args.title, custom_config)

    from bi_utils import add_component
    comp = add_component(args.page_id, args.comp, args.title or args.comp,
                         args.x, args.y, args.w, args.h, config)
    save_page(args.page_id)
    print(f'添加成功: {args.title} ({args.comp}) 位置({args.x},{args.y}) 尺寸{args.w}x{args.h}')
    print(f'组件ID: {comp["i"]}')


def cmd_batch_add(args):
    """
    批量添加组件（一次 query + save，彻底消除并发锁冲突）。

    --specs 格式（JSON 数组）：
    [
      {"comp":"JBar","title":"柱形图","x":0,"y":0,"w":12,"h":30},
      {"comp":"JPie","title":"饼图","x":12,"y":0,"w":12,"h":30,"config":{...}}
    ]
    """
    try:
        specs = json.loads(args.specs)
    except json.JSONDecodeError as e:
        print(f'--specs JSON 解析失败: {e}')
        return

    tmpl = load_template(args.page_id)
    bi_utils._page_components[args.page_id] = tmpl

    from bi_utils import add_component
    added = []
    for spec in specs:
        comp_type = spec.get('comp', '')
        title     = spec.get('title', comp_type)
        x = spec.get('x', 0)
        y = spec.get('y', 0)
        w = spec.get('w', 12)
        h = spec.get('h', 30)
        custom_config = spec.get('config', None)

        config = _build_comp_config(comp_type, title, custom_config)
        comp = add_component(args.page_id, comp_type, title, x, y, w, h, config)
        added.append(f'{title}({comp_type})')

    save_page(args.page_id)
    print(f'批量添加成功 {len(added)} 个组件: {", ".join(added)}')


def cmd_move(args):
    """移动/缩放组件"""
    tmpl = load_template(args.page_id)

    moved = 0
    for comp in tmpl:
        targets = []
        if _match_comp(comp, args):
            targets.append(comp)
        if comp.get('component') == 'JGroup':
            for el in comp.get('props', {}).get('elements', []):
                if _match_comp(el, args):
                    targets.append(el)

        for target in targets:
            changes = []
            if args.x is not None:
                target['x'] = args.x
                changes.append(f'x={args.x}')
            if args.y is not None:
                target['y'] = args.y
                changes.append(f'y={args.y}')
            if args.w is not None:
                target['w'] = args.w
                changes.append(f'w={args.w}')
            if args.h is not None:
                target['h'] = args.h
                changes.append(f'h={args.h}')
            # 同步 config 中的尺寸
            cfg = target.get('config', {})
            if isinstance(cfg, str):
                try: cfg = json.loads(cfg)
                except: cfg = {}
                target['config'] = cfg
            if args.w is not None:
                cfg['w'] = args.w
                if 'size' in cfg:
                    cfg['size']['width'] = args.w
            if args.h is not None:
                cfg['h'] = args.h
                if 'size' in cfg:
                    cfg['size']['height'] = args.h
            if changes:
                print(f'  移动 {target.get("componentName","")}: {", ".join(changes)}')
                moved += 1

    if moved == 0:
        print('未找到匹配的组件')
        return

    save_template(args.page_id, tmpl)
    print(f'共移动 {moved} 个组件')


def _match_comp(comp, args):
    """检查组件是否匹配筛选条件"""
    if hasattr(args, 'id') and args.id and comp.get('i') == args.id:
        return True
    if hasattr(args, 'name') and args.name and comp.get('componentName', '') == args.name:
        return True
    if hasattr(args, 'type') and args.type and comp.get('component') == args.type:
        return True
    return False


# ============================================================
# CLI 入口
# ============================================================
def main():
    parser = argparse.ArgumentParser(description='大屏组件操作工具')
    subparsers = parser.add_subparsers(dest='command', help='操作类型')

    # 通用参数
    def add_common(sub):
        sub.add_argument('api_base', help='API 地址')
        sub.add_argument('token', help='X-Access-Token')
        sub.add_argument('page_id', help='页面 ID')

    def add_filter(sub):
        sub.add_argument('--name', help='按组件名称匹配')
        sub.add_argument('--type', help='按组件类型匹配（如 JBar）')
        sub.add_argument('--id', help='按组件 ID 匹配')

    # list
    p_list = subparsers.add_parser('list', help='列出所有组件')
    add_common(p_list)

    # delete
    p_del = subparsers.add_parser('delete', help='删除组件')
    add_common(p_del)
    add_filter(p_del)

    # edit
    p_edit = subparsers.add_parser('edit', help='编辑组件属性')
    add_common(p_edit)
    add_filter(p_edit)
    p_edit.add_argument('--set', action='append', required=True,
                        help='设置属性，格式: path=value（可多次使用）')

    # add
    p_add = subparsers.add_parser('add', help='添加组件')
    add_common(p_add)
    p_add.add_argument('--comp', required=True, help='组件类型（如 JBar, JText）')
    p_add.add_argument('--title', default='', help='组件标题')
    p_add.add_argument('--x', type=int, default=50, help='X 坐标')
    p_add.add_argument('--y', type=int, default=50, help='Y 坐标')
    p_add.add_argument('--w', type=int, default=450, help='宽度')
    p_add.add_argument('--h', type=int, default=300, help='高度')
    p_add.add_argument('--config', default=None, help='自定义 config（JSON 字符串）')

    # move
    p_move = subparsers.add_parser('move', help='移动/缩放组件')
    add_common(p_move)
    add_filter(p_move)
    p_move.add_argument('--x', type=int, default=None, help='新 X 坐标')
    p_move.add_argument('--y', type=int, default=None, help='新 Y 坐标')
    p_move.add_argument('--w', type=int, default=None, help='新宽度')
    p_move.add_argument('--h', type=int, default=None, help='新高度')

    # batch-add（多组件一次保存，消除并发锁冲突）
    p_batch = subparsers.add_parser('batch-add', help='批量添加多个组件（一次保存）')
    add_common(p_batch)
    p_batch.add_argument('--specs', required=True,
                         help='组件规格 JSON 数组，每项含 comp/title/x/y/w/h/config')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    init_api(args.api_base, args.token)

    if args.command == 'list':
        cmd_list(args)
    elif args.command == 'delete':
        cmd_delete(args)
    elif args.command == 'edit':
        cmd_edit(args)
    elif args.command == 'add':
        cmd_add(args)
    elif args.command == 'batch-add':
        cmd_batch_add(args)
    elif args.command == 'move':
        cmd_move(args)


if __name__ == '__main__':
    main()
