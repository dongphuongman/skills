# -*- coding: utf-8 -*-
"""
大屏/仪表盘批量样式操作工具
============================

使用方式（命令行）：

  # 查看所有图表组件的颜色设置
  py style_ops.py show-colors <API_BASE> <TOKEN> <PAGE_ID>

  # 设置所有图表的标题颜色
  py style_ops.py set-title-color <API_BASE> <TOKEN> <PAGE_ID> --color "#00FF00"

  # 设置所有图表的轴标签颜色
  py style_ops.py set-axis-color <API_BASE> <TOKEN> <PAGE_ID> --color "#ffffff"

  # 设置所有图表的网格线颜色
  py style_ops.py set-grid-color <API_BASE> <TOKEN> <PAGE_ID> --color "rgba(255,255,255,0.1)"

  # 设置所有图表的图例文字颜色
  py style_ops.py set-legend-color <API_BASE> <TOKEN> <PAGE_ID> --color "#ffffff"

  # 设置所有图表的调色板
  py style_ops.py set-palette <API_BASE> <TOKEN> <PAGE_ID> --colors "#5470C6,#91CC75,#FAC858,#EE6666,#73C0DE"

  # 设置所有图表的标题字号
  py style_ops.py set-font-size <API_BASE> <TOKEN> <PAGE_ID> --size 16

  # 设置所有组件的背景色
  py style_ops.py set-bg-all <API_BASE> <TOKEN> <PAGE_ID> --color "#FFFFFF00"

  # 批量编辑：对指定类型组件应用任意 config 路径赋值
  py style_ops.py batch-edit <API_BASE> <TOKEN> <PAGE_ID> --type JBar --path "option.series[0].itemStyle.borderRadius" --value 5
"""

import sys, json, os, argparse

# ============================================================
# bi_utils 加载（自动查找）
# ============================================================
def _find_bi_utils():
    """按优先级查找 bi_utils.py"""
    candidates = [
        os.path.dirname(os.path.abspath(__file__)),                     # 同目录
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'), # 上级目录(references/)
        os.getcwd(),                                                     # 当前工作目录
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
# 图表组件类型列表
# ============================================================
CHART_TYPES = {
    'JBar', 'JLine', 'JPie', 'JRing', 'JRose', 'JFunnel', 'JRadar', 'JGauge',
    'JSmoothLine', 'JStackBar', 'JHorizontalBar', 'JMixLineBar', 'JScatter',
    'JBubble', 'JWordCloud', 'JAreaMap', 'JArea', 'JStackArea',
    'JWaterfall', 'JBoxplot', 'JHeatmap', 'JTreemap', 'JSunburst',
    'JSankey', 'JGraph', 'JTree', 'JParallel', 'JThemeRiver',
    'JCandlestick', 'JPictorialBar', 'JMap', 'JGlobe',
}


# ============================================================
# 模板加载/保存（与 comp_ops 一致）
# ============================================================
def load_template(page_id):
    """加载页面模板，返回组件列表"""
    page = query_page(page_id)
    tmpl = page.get('template', [])
    if isinstance(tmpl, str):
        tmpl = json.loads(tmpl)
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
    for comp in tmpl:
        cfg = comp.get('config', {})
        if isinstance(cfg, dict):
            comp['config'] = cfg
    bi_utils._page_components[page_id] = tmpl
    save_page(page_id)


# ============================================================
# 工具函数
# ============================================================
def set_nested(obj, path, value):
    """
    按路径设置嵌套字典的值。
    支持: option.series[0].itemStyle.color, chartData.value 等
    """
    parts = []
    for p in path.split('.'):
        if '[' in p:
            key = p[:p.index('[')]
            idx = int(p[p.index('[') + 1:p.index(']')])
            parts.append(('key', key))
            parts.append(('idx', idx))
        else:
            parts.append(('key', p))

    current = obj
    for i, (kind, val) in enumerate(parts[:-1]):
        if kind == 'key':
            if isinstance(current, dict):
                if val not in current:
                    next_kind = parts[i + 1][0] if i + 1 < len(parts) else 'key'
                    current[val] = [] if next_kind == 'idx' else {}
                current = current[val]
        elif kind == 'idx':
            if isinstance(current, list):
                while len(current) <= val:
                    current.append({})
                current = current[val]

    last_kind, last_val = parts[-1]
    if last_kind == 'key':
        if isinstance(current, dict):
            current[last_val] = _auto_type(value)
    elif last_kind == 'idx':
        if isinstance(current, list):
            while len(current) <= last_val:
                current.append({})
            current[last_val] = _auto_type(value)


def get_nested(obj, path, default=None):
    """
    按路径读取嵌套字典的值。路径不存在返回 default。
    """
    parts = []
    for p in path.split('.'):
        if '[' in p:
            key = p[:p.index('[')]
            idx = int(p[p.index('[') + 1:p.index(']')])
            parts.append(('key', key))
            parts.append(('idx', idx))
        else:
            parts.append(('key', p))

    current = obj
    for kind, val in parts:
        if current is None:
            return default
        if kind == 'key':
            if isinstance(current, dict):
                current = current.get(val)
            else:
                return default
        elif kind == 'idx':
            if isinstance(current, list) and val < len(current):
                current = current[val]
            else:
                return default
    return current if current is not None else default


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
        if val.startswith('{') or val.startswith('['):
            try:
                return json.loads(val)
            except:
                pass
    return val


def iter_all_components(tmpl):
    """遍历所有组件（包括 JGroup 内部），yield (comp, parent_or_None)"""
    for comp in tmpl:
        yield comp
        if comp.get('component') == 'JGroup':
            elements = comp.get('props', {}).get('elements', [])
            for el in elements:
                yield el


def is_chart(comp):
    """判断组件是否为图表类型"""
    return comp.get('component', '') in CHART_TYPES


# ============================================================
# 命令实现
# ============================================================
def cmd_show_colors(args):
    """查看所有图表组件的颜色设置"""
    tmpl = load_template(args.page_id)

    header = f'{"组件名":<20} {"类型":<18} {"标题色":<12} {"轴标签色":<12} {"图例色":<12} {"背景色":<12}'
    print(header)
    print('-' * 90)

    count = 0
    for comp in iter_all_components(tmpl):
        if not is_chart(comp):
            continue
        cfg = comp.get('config', {})
        name = comp.get('componentName', '(无名)')
        ctype = comp.get('component', '?')

        title_color = get_nested(cfg, 'option.title.textStyle.color', '-')
        x_axis_color = get_nested(cfg, 'option.xAxis.axisLabel.color', '-')
        y_axis_color = get_nested(cfg, 'option.yAxis.axisLabel.color', '-')
        # 轴标签色取 x 或 y 中有值的
        axis_color = x_axis_color if x_axis_color != '-' else y_axis_color
        legend_color = get_nested(cfg, 'option.legend.textStyle.color', '-')
        bg_color = cfg.get('background', '-')

        print(f'{name:<20} {ctype:<18} {str(title_color):<12} {str(axis_color):<12} {str(legend_color):<12} {str(bg_color):<12}')
        count += 1

    print(f'\n共 {count} 个图表组件')


def cmd_set_title_color(args):
    """设置所有图表的标题颜色"""
    tmpl = load_template(args.page_id)
    modified = 0
    for comp in iter_all_components(tmpl):
        if not is_chart(comp):
            continue
        cfg = comp.get('config', {})
        set_nested(cfg, 'option.title.textStyle.color', args.color)
        modified += 1
        print(f'  {comp.get("componentName", "")} ({comp.get("component", "")}): 标题色 -> {args.color}')

    if modified == 0:
        print('未找到图表组件')
        return
    save_template(args.page_id, tmpl)
    print(f'\n共修改 {modified} 个图表组件的标题颜色')


def cmd_set_axis_color(args):
    """设置所有图表的轴标签颜色"""
    tmpl = load_template(args.page_id)
    modified = 0
    for comp in iter_all_components(tmpl):
        if not is_chart(comp):
            continue
        cfg = comp.get('config', {})
        set_nested(cfg, 'option.xAxis.axisLabel.color', args.color)
        set_nested(cfg, 'option.yAxis.axisLabel.color', args.color)
        # 同时设置轴线颜色
        set_nested(cfg, 'option.xAxis.axisLine.lineStyle.color', args.color)
        set_nested(cfg, 'option.yAxis.axisLine.lineStyle.color', args.color)
        modified += 1
        print(f'  {comp.get("componentName", "")} ({comp.get("component", "")}): 轴标签色 -> {args.color}')

    if modified == 0:
        print('未找到图表组件')
        return
    save_template(args.page_id, tmpl)
    print(f'\n共修改 {modified} 个图表组件的轴标签颜色')


def cmd_set_grid_color(args):
    """设置所有图表的网格/分隔线颜色"""
    tmpl = load_template(args.page_id)
    modified = 0
    for comp in iter_all_components(tmpl):
        if not is_chart(comp):
            continue
        cfg = comp.get('config', {})
        set_nested(cfg, 'option.xAxis.splitLine.lineStyle.color', args.color)
        set_nested(cfg, 'option.yAxis.splitLine.lineStyle.color', args.color)
        modified += 1
        print(f'  {comp.get("componentName", "")} ({comp.get("component", "")}): 网格线色 -> {args.color}')

    if modified == 0:
        print('未找到图表组件')
        return
    save_template(args.page_id, tmpl)
    print(f'\n共修改 {modified} 个图表组件的网格线颜色')


def cmd_set_legend_color(args):
    """设置所有图表的图例文字颜色"""
    tmpl = load_template(args.page_id)
    modified = 0
    for comp in iter_all_components(tmpl):
        if not is_chart(comp):
            continue
        cfg = comp.get('config', {})
        set_nested(cfg, 'option.legend.textStyle.color', args.color)
        modified += 1
        print(f'  {comp.get("componentName", "")} ({comp.get("component", "")}): 图例色 -> {args.color}')

    if modified == 0:
        print('未找到图表组件')
        return
    save_template(args.page_id, tmpl)
    print(f'\n共修改 {modified} 个图表组件的图例颜色')


def cmd_set_palette(args):
    """设置所有图表的调色板"""
    color_list = [c.strip() for c in args.colors.split(',')]
    custom_color = [{'color': c, 'color1': c} for c in color_list]

    tmpl = load_template(args.page_id)
    modified = 0
    for comp in iter_all_components(tmpl):
        if not is_chart(comp):
            continue
        cfg = comp.get('config', {})
        if 'option' not in cfg:
            cfg['option'] = {}
        cfg['option']['customColor'] = custom_color
        modified += 1
        print(f'  {comp.get("componentName", "")} ({comp.get("component", "")}): 调色板 -> {color_list}')

    if modified == 0:
        print('未找到图表组件')
        return
    save_template(args.page_id, tmpl)
    print(f'\n共修改 {modified} 个图表组件的调色板')


def cmd_set_font_size(args):
    """设置所有图表的标题字号"""
    tmpl = load_template(args.page_id)
    modified = 0
    for comp in iter_all_components(tmpl):
        if not is_chart(comp):
            continue
        cfg = comp.get('config', {})
        set_nested(cfg, 'option.title.textStyle.fontSize', str(args.size))
        modified += 1
        print(f'  {comp.get("componentName", "")} ({comp.get("component", "")}): 标题字号 -> {args.size}')

    if modified == 0:
        print('未找到图表组件')
        return
    save_template(args.page_id, tmpl)
    print(f'\n共修改 {modified} 个图表组件的标题字号')


def cmd_set_bg_all(args):
    """设置所有组件的背景色"""
    tmpl = load_template(args.page_id)
    modified = 0
    for comp in iter_all_components(tmpl):
        cfg = comp.get('config', {})
        cfg['background'] = args.color
        modified += 1
        print(f'  {comp.get("componentName", "")} ({comp.get("component", "")}): 背景色 -> {args.color}')

    if modified == 0:
        print('未找到组件')
        return
    save_template(args.page_id, tmpl)
    print(f'\n共修改 {modified} 个组件的背景色')


def cmd_batch_edit(args):
    """批量编辑：对指定类型组件应用任意 config 路径赋值"""
    tmpl = load_template(args.page_id)
    modified = 0
    for comp in iter_all_components(tmpl):
        # 按类型过滤
        if args.type and comp.get('component') != args.type:
            continue
        # 按名称过滤
        if args.name and comp.get('componentName', '') != args.name:
            continue
        # 如果没有过滤条件，跳过（防止误操作）
        if not args.type and not args.name:
            print('错误：batch-edit 需要至少指定 --type 或 --name 过滤条件')
            return

        cfg = comp.get('config', {})
        set_nested(cfg, args.path, args.value)
        modified += 1
        print(f'  {comp.get("componentName", "")} ({comp.get("component", "")}): config.{args.path} = {args.value}')

    if modified == 0:
        print('未找到匹配的组件')
        return
    save_template(args.page_id, tmpl)
    print(f'\n共修改 {modified} 个组件')


# ============================================================
# CLI 入口
# ============================================================
def main():
    parser = argparse.ArgumentParser(description='大屏批量样式操作工具')
    subparsers = parser.add_subparsers(dest='command', help='操作类型')

    def add_common(sub):
        sub.add_argument('api_base', help='API 地址')
        sub.add_argument('token', help='X-Access-Token')
        sub.add_argument('page_id', help='页面 ID')

    # show-colors
    p_show = subparsers.add_parser('show-colors', help='查看所有图表组件的颜色设置')
    add_common(p_show)

    # set-title-color
    p_title = subparsers.add_parser('set-title-color', help='设置所有图表的标题颜色')
    add_common(p_title)
    p_title.add_argument('--color', required=True, help='颜色值，如 "#00FF00"')

    # set-axis-color
    p_axis = subparsers.add_parser('set-axis-color', help='设置所有图表的轴标签颜色')
    add_common(p_axis)
    p_axis.add_argument('--color', required=True, help='颜色值，如 "#ffffff"')

    # set-grid-color
    p_grid = subparsers.add_parser('set-grid-color', help='设置所有图表的网格线颜色')
    add_common(p_grid)
    p_grid.add_argument('--color', required=True, help='颜色值，如 "rgba(255,255,255,0.1)"')

    # set-legend-color
    p_legend = subparsers.add_parser('set-legend-color', help='设置所有图表的图例文字颜色')
    add_common(p_legend)
    p_legend.add_argument('--color', required=True, help='颜色值，如 "#ffffff"')

    # set-palette
    p_palette = subparsers.add_parser('set-palette', help='设置所有图表的调色板')
    add_common(p_palette)
    p_palette.add_argument('--colors', required=True, help='逗号分隔的颜色列表，如 "#5470C6,#91CC75,#FAC858"')

    # set-font-size
    p_font = subparsers.add_parser('set-font-size', help='设置所有图表的标题字号')
    add_common(p_font)
    p_font.add_argument('--size', type=int, required=True, help='字号大小，如 16')

    # set-bg-all
    p_bg = subparsers.add_parser('set-bg-all', help='设置所有组件的背景色')
    add_common(p_bg)
    p_bg.add_argument('--color', required=True, help='颜色值，如 "#FFFFFF00"（透明）')

    # batch-edit
    p_batch = subparsers.add_parser('batch-edit', help='批量编辑：对匹配组件应用任意 config 路径赋值')
    add_common(p_batch)
    p_batch.add_argument('--type', default=None, help='按组件类型过滤（如 JBar）')
    p_batch.add_argument('--name', default=None, help='按组件名称过滤')
    p_batch.add_argument('--path', required=True, help='config 内的属性路径，如 "option.series[0].itemStyle.borderRadius"')
    p_batch.add_argument('--value', required=True, help='要设置的值')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    init_api(args.api_base, args.token)

    commands = {
        'show-colors': cmd_show_colors,
        'set-title-color': cmd_set_title_color,
        'set-axis-color': cmd_set_axis_color,
        'set-grid-color': cmd_set_grid_color,
        'set-legend-color': cmd_set_legend_color,
        'set-palette': cmd_set_palette,
        'set-font-size': cmd_set_font_size,
        'set-bg-all': cmd_set_bg_all,
        'batch-edit': cmd_batch_edit,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
