# -*- coding: utf-8 -*-
"""
地图数据管理工具 —— JAreaMap / JFlyLineMap / JBubbleMap
======================================================

使用方式（命令行）：

  # 列出已上传的地图数据
  py map_ops.py list <API_BASE> <TOKEN>

  # 检查某个 adcode 是否已上传
  py map_ops.py check <API_BASE> <TOKEN> --adcode 650000
  py map_ops.py check <API_BASE> <TOKEN> --adcode 新疆

  # 上传 GeoJSON（从 DataV Aliyun 下载，自动去重）
  py map_ops.py upload <API_BASE> <TOKEN> --adcode 650000 --name "新疆维吾尔自治区"
  py map_ops.py upload <API_BASE> <TOKEN> --adcode 新疆 --name "新疆维吾尔自治区"

  # 添加 JAreaMap 组件到页面
  py map_ops.py add-map <API_BASE> <TOKEN> --page PAGE_ID --adcode 650000 --area-name "新疆维吾尔自治区" --title "区域地图" --x 50 --y 100 --w 700 --h 550 --data '[{"name":"乌鲁木齐市","value":405}]'
"""

import sys, json, os, argparse, ssl, urllib.request

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
from bi_utils import init_api, query_page, save_page, add_component


# ============================================================
# 省份 adcode 速查表
# ============================================================
PROVINCE_CODES = {
    '北京': 110000, '天津': 120000, '河北': 130000, '山西': 140000, '内蒙古': 150000,
    '辽宁': 210000, '吉林': 220000, '黑龙江': 230000, '上海': 310000, '江苏': 320000,
    '浙江': 330000, '安徽': 340000, '福建': 350000, '江西': 360000, '山东': 370000,
    '河南': 410000, '湖北': 420000, '湖南': 430000, '广东': 440000, '广西': 450000,
    '海南': 460000, '重庆': 500000, '四川': 510000, '贵州': 520000, '云南': 530000,
    '西藏': 540000, '陕西': 610000, '甘肃': 620000, '青海': 630000, '宁夏': 640000,
    '新疆': 650000, '台湾': 710000, '香港': 810000, '澳门': 820000, '全国': 100000,
}


def resolve_adcode(raw):
    """将 adcode 参数解析为数字。支持数字或中文省份名。"""
    if raw is None:
        return None
    raw = str(raw).strip()
    # 直接是数字
    try:
        return int(raw)
    except ValueError:
        pass
    # 中文省份名查找
    if raw in PROVINCE_CODES:
        return PROVINCE_CODES[raw]
    # 模糊匹配（如"新疆维吾尔自治区" -> "新疆"）
    for name, code in PROVINCE_CODES.items():
        if name in raw or raw in name:
            return code
    raise ValueError(f'无法识别的 adcode: {raw}（支持数字或省份简称如"新疆"、"广东"）')


# ============================================================
# 地图数据 API
# ============================================================
def list_map_data():
    """查询已上传的地图数据列表"""
    result = bi_utils._request('GET', '/drag/jimuDragMap/list', params={
        'pageNo': 1,
        'pageSize': 100,
    })
    return result


def check_map_exists(adcode):
    """检查指定 adcode 的地图数据是否已上传"""
    result = bi_utils._request('GET', '/drag/jimuDragMap/list', params={
        'pageNo': 1,
        'pageSize': 100,
        'name': str(adcode),
    })
    records = result.get('result', {}).get('records', [])
    return any(r.get('name') == str(adcode) for r in records)


def download_geojson(adcode):
    """从 DataV Aliyun 下载 GeoJSON 数据"""
    geo_url = f'https://geo.datav.aliyun.com/areas_v3/bound/{adcode}_full.json'
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(geo_url, headers={'User-Agent': 'Mozilla/5.0'})
    print(f'下载 GeoJSON: {geo_url}')
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        geo_json = resp.read().decode('utf-8')
    print(f'下载完成，数据大小: {len(geo_json)} 字节')
    return geo_json


def upload_map_data(adcode, geo_json):
    """上传地图数据到后端"""
    result = bi_utils._request('POST', '/jmreport/map/addMapData', data={
        'name': str(adcode),
        'mapData': geo_json,
    })
    return result


# ============================================================
# 命令实现
# ============================================================
def cmd_list(args):
    """列出已上传的地图数据"""
    result = list_map_data()
    records = result.get('result', {}).get('records', [])
    total = result.get('result', {}).get('total', 0)

    print(f'共 {total} 条地图数据：\n')
    print(f'{"序号":<4} {"ID":<36} {"名称(adcode)":<16} {"创建时间":<20}')
    print('-' * 80)
    for i, rec in enumerate(records):
        rid = rec.get('id', '?')
        name = rec.get('name', '?')
        create_time = rec.get('createTime', '?')
        print(f'{i+1:<4} {rid:<36} {name:<16} {create_time:<20}')


def cmd_check(args):
    """检查指定 adcode 是否已上传"""
    adcode = resolve_adcode(args.adcode)
    exists = check_map_exists(adcode)
    if exists:
        print(f'adcode {adcode} 的地图数据已存在')
    else:
        print(f'adcode {adcode} 的地图数据不存在')
    return exists


def cmd_upload(args):
    """下载并上传 GeoJSON 数据"""
    adcode = resolve_adcode(args.adcode)
    display_name = args.name or str(adcode)

    # 检查是否已存在
    exists = check_map_exists(adcode)
    if exists:
        print(f'adcode {adcode} ({display_name}) 的地图数据已存在，跳过上传')
        return

    # 下载 GeoJSON
    geo_json = download_geojson(adcode)

    # 上传
    print(f'上传地图数据: adcode={adcode}, name={display_name}')
    result = upload_map_data(adcode, geo_json)
    if result.get('success'):
        print(f'上传成功: adcode {adcode} ({display_name})')
    else:
        print(f'上传失败: {result.get("message", json.dumps(result, ensure_ascii=False))}')


def cmd_add_map(args):
    """添加 JAreaMap 组件到页面"""
    adcode = resolve_adcode(args.adcode)
    area_name = args.area_name or str(adcode)
    title = args.title or '区域地图'

    # 解析 chartData
    chart_data = []
    if args.data:
        try:
            chart_data = json.loads(args.data)
        except json.JSONDecodeError as e:
            print(f'--data JSON 解析失败: {e}')
            return

    # 计算 visualMap 的 min/max
    values = [item.get('value', 0) for item in chart_data if isinstance(item.get('value'), (int, float))]
    v_min = min(values) if values else 0
    v_max = max(values) if values else 100

    # 加载页面现有组件
    page = query_page(args.page)
    tmpl = page.get('template', [])
    if isinstance(tmpl, str):
        tmpl = json.loads(tmpl)
    bi_utils._page_components[args.page] = tmpl

    # 构建 JAreaMap config
    config = {
        'dataType': 1,
        'background': 'rgba(0,0,0,0)',
        'borderColor': '',
        'chartData': json.dumps(chart_data, ensure_ascii=False),
        'option': {
            'title': {
                'text': title,
                'show': True,
                'textStyle': {'color': '#ffffff', 'fontSize': 16},
            },
            'card': {'title': '', 'extra': '', 'rightHref': '', 'size': 'small'},
            'area': {
                'value': [str(adcode)],
                'name': [area_name],
            },
            'geo': {
                'show': True,
                'roam': True,
                'zoom': 1,
                'aspectScale': 0.75,
                'layoutCenter': ['50%', '50%'],
                'layoutSize': '100%',
                'itemStyle': {
                    'areaColor': '#0d2c54',
                    'borderColor': '#4ebfcf',
                    'borderWidth': 1.5,
                    'shadowColor': 'rgba(0,0,0,0.5)',
                    'shadowBlur': 10,
                    'shadowOffsetX': 0,
                    'shadowOffsetY': 5,
                },
                'emphasis': {
                    'itemStyle': {
                        'areaColor': '#2B91B7',
                        'borderColor': '#4ebfcf',
                        'borderWidth': 2,
                    },
                },
                'label': {
                    'show': True,
                    'color': '#ffffff',
                    'fontSize': 12,
                },
                'regions': [],
            },
            'visualMap': {
                'show': True,
                'type': 'continuous',
                'min': v_min,
                'max': v_max,
                'left': 20,
                'bottom': 20,
                'text': ['高', '低'],
                'textStyle': {'color': '#ffffff'},
                'calculable': True,
                'inRange': {
                    'color': ['#0b1c3e', '#0e4177', '#1a7cc1', '#2badd9', '#60d5e8'],
                },
                'seriesIndex': 0,
            },
            'tooltip': {
                'show': True,
                'trigger': 'item',
                'textStyle': {'color': '#ffffff'},
            },
        },
    }

    comp = add_component(args.page, 'JAreaMap', title, args.x, args.y, args.w, args.h, config)
    save_page(args.page)
    print(f'添加成功: {title} (JAreaMap) adcode={adcode} area={area_name}')
    print(f'位置({args.x},{args.y}) 尺寸{args.w}x{args.h}')
    print(f'组件ID: {comp["i"]}')
    if chart_data:
        print(f'数据项: {len(chart_data)} 条, visualMap 范围: {v_min}~{v_max}')


# ============================================================
# CLI 入口
# ============================================================
def main():
    parser = argparse.ArgumentParser(description='地图数据管理工具（JAreaMap/JFlyLineMap/JBubbleMap）')
    subparsers = parser.add_subparsers(dest='command', help='操作类型')

    # list
    p_list = subparsers.add_parser('list', help='列出已上传的地图数据')
    p_list.add_argument('api_base', help='API 地址')
    p_list.add_argument('token', help='X-Access-Token')

    # check
    p_check = subparsers.add_parser('check', help='检查 adcode 是否已上传')
    p_check.add_argument('api_base', help='API 地址')
    p_check.add_argument('token', help='X-Access-Token')
    p_check.add_argument('--adcode', required=True, help='adcode（数字或省份名如"新疆"）')

    # upload
    p_upload = subparsers.add_parser('upload', help='上传 GeoJSON 数据')
    p_upload.add_argument('api_base', help='API 地址')
    p_upload.add_argument('token', help='X-Access-Token')
    p_upload.add_argument('--adcode', required=True, help='adcode（数字或省份名如"新疆"）')
    p_upload.add_argument('--name', default=None, help='地图显示名称（如"新疆维吾尔自治区"）')

    # add-map
    p_add = subparsers.add_parser('add-map', help='添加 JAreaMap 组件到页面')
    p_add.add_argument('api_base', help='API 地址')
    p_add.add_argument('token', help='X-Access-Token')
    p_add.add_argument('--page', required=True, help='页面 ID')
    p_add.add_argument('--adcode', required=True, help='adcode（数字或省份名如"新疆"）')
    p_add.add_argument('--area-name', default=None, help='区域名称（如"新疆维吾尔自治区"）')
    p_add.add_argument('--title', default='区域地图', help='组件标题')
    p_add.add_argument('--x', type=int, default=50, help='X 坐标')
    p_add.add_argument('--y', type=int, default=100, help='Y 坐标')
    p_add.add_argument('--w', type=int, default=700, help='宽度')
    p_add.add_argument('--h', type=int, default=550, help='高度')
    p_add.add_argument('--data', default=None, help='图表数据（JSON 字符串，如 \'[{"name":"城市","value":100}]\'）')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    init_api(args.api_base, args.token)

    if args.command == 'list':
        cmd_list(args)
    elif args.command == 'check':
        cmd_check(args)
    elif args.command == 'upload':
        cmd_upload(args)
    elif args.command == 'add-map':
        cmd_add_map(args)


if __name__ == '__main__':
    main()
