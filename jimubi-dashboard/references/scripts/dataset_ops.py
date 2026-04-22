# -*- coding: utf-8 -*-
"""
大屏/仪表盘数据集操作工具 —— 增、删、查、测试、绑定
====================================================

使用方式（命令行）：

  # 列出数据集
  py dataset_ops.py list <API_BASE> <TOKEN> --page-size 20

  # 创建 SQL 数据集
  py dataset_ops.py create-sql <API_BASE> <TOKEN> --name "销售数据" --code "sale_data" --db-source "707437208002265088" --sql "SELECT name, value FROM table" --fields "name:String,value:String"

  # 创建 API 数据集
  py dataset_ops.py create-api <API_BASE> <TOKEN> --name "天气数据" --code "weather_data" --url "https://api.example.com/data" --method get --agent 0 --fields "name:String,value:String"

  # 测试数据集
  py dataset_ops.py test <API_BASE> <TOKEN> --id "dataset_id"

  # 删除数据集
  py dataset_ops.py delete <API_BASE> <TOKEN> --id "dataset_id"

  # 绑定数据集到组件
  py dataset_ops.py bind <API_BASE> <TOKEN> --page PAGE_ID --comp-name "基础柱形图" --dataset-id "xxx" --dataset-name "销售数据" --dataset-type sql --mapping "维度=name,数值=value"
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
# 辅助函数
# ============================================================
def _parse_fields(fields_str):
    """
    解析 --fields "name:String,value:String" 为 datasetItemList 格式。

    返回:
        [{"fieldName":"name","fieldTxt":"name","fieldType":"String","izShow":"Y","orderNum":0}, ...]
    """
    items = []
    for idx, part in enumerate(fields_str.split(',')):
        part = part.strip()
        if ':' not in part:
            print(f'警告: 忽略无效字段定义 "{part}"（需要 name:Type 格式）')
            continue
        field_name, field_type = part.split(':', 1)
        field_name = field_name.strip()
        field_type = field_type.strip()
        items.append({
            'fieldName': field_name,
            'fieldTxt': field_name,
            'fieldType': field_type,
            'izShow': 'Y',
            'orderNum': idx,
        })
    return items


def _parse_mapping(mapping_str):
    """
    解析 --mapping "维度=name,数值=value" 为 dataMapping 格式。

    注意: 后端使用 'filed'（不是 'field'）。

    返回:
        [{"filed":"维度","mapping":"name"}, {"filed":"数值","mapping":"value"}]
    """
    items = []
    for part in mapping_str.split(','):
        part = part.strip()
        if '=' not in part:
            print(f'警告: 忽略无效映射定义 "{part}"（需要 filed=mapping 格式）')
            continue
        filed, mapping = part.split('=', 1)
        items.append({
            'filed': filed.strip(),
            'mapping': mapping.strip(),
        })
    return items


# ============================================================
# 命令实现
# ============================================================
def cmd_list(args):
    """列出数据集"""
    params = {
        'pageNo': 1,
        'pageSize': args.page_size,
    }
    result = bi_utils._request('GET', '/drag/onlDragDatasetHead/list', params=params)
    if not result.get('success'):
        print(f'查询失败: {result.get("message", "")}')
        return

    data = result.get('result', {})
    records = data.get('records', [])
    total = data.get('total', 0)

    print(f'共 {total} 个数据集（当前显示 {len(records)} 个）：\n')
    print(f'{"序号":<4} {"ID":<24} {"编码":<20} {"名称":<20} {"类型":<8} {"数据源":<24}')
    print('-' * 110)
    for i, rec in enumerate(records):
        ds_id = rec.get('id', '?')
        code = rec.get('code', '')
        name = rec.get('name', '')
        data_type = rec.get('dataType', '')
        db_source = rec.get('dbSource', '') or ''
        print(f'{i+1:<4} {ds_id:<24} {code:<20} {name:<20} {data_type:<8} {db_source:<24}')


def cmd_create_sql(args):
    """创建 SQL 数据集"""
    field_list = _parse_fields(args.fields)
    if not field_list:
        print('错误: 至少需要一个字段定义')
        return

    payload = {
        'name': args.name,
        'code': args.code,
        'dataType': 'sql',
        'dbSource': args.db_source,
        'querySql': args.sql,
        'datasetItemList': field_list,
    }

    result = bi_utils._request('POST', '/drag/onlDragDatasetHead/add', data=payload)
    if not result.get('success'):
        print(f'创建失败: {result.get("message", "")}')
        return

    ds = result.get('result', {})
    ds_id = ds.get('id', '') if isinstance(ds, dict) else ds
    print(f'SQL 数据集创建成功: {args.name} (编码: {args.code})')
    print(f'数据集ID: {ds_id}')


def cmd_create_api(args):
    """创建 API 数据集"""
    field_list = _parse_fields(args.fields)
    if not field_list:
        print('错误: 至少需要一个字段定义')
        return

    payload = {
        'name': args.name,
        'code': args.code,
        'dataType': 'api',
        'dbSource': None,
        'querySql': args.url,
        'apiMethod': args.method,
        'izAgent': str(args.agent),
        'datasetItemList': field_list,
    }

    result = bi_utils._request('POST', '/drag/onlDragDatasetHead/add', data=payload)
    if not result.get('success'):
        print(f'创建失败: {result.get("message", "")}')
        return

    ds = result.get('result', {})
    ds_id = ds.get('id', '') if isinstance(ds, dict) else ds
    print(f'API 数据集创建成功: {args.name} (编码: {args.code})')
    print(f'数据集ID: {ds_id}')


def cmd_test(args):
    """测试数据集"""
    payload = {
        'id': args.id,
    }

    result = bi_utils._request('POST', '/drag/onlDragDatasetHead/getAllChartData', data=payload)
    if not result.get('success'):
        print(f'测试失败: {result.get("message", "")}')
        return

    data = result.get('result', [])
    print(f'测试成功，返回 {len(data) if isinstance(data, list) else 1} 条数据：\n')
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_delete(args):
    """删除数据集"""
    result = bi_utils._request('DELETE', '/drag/onlDragDatasetHead/delete', params={'id': args.id})
    if not result.get('success'):
        print(f'删除失败: {result.get("message", "")}')
        return

    print(f'数据集删除成功: {args.id}')


def cmd_bind(args):
    """绑定数据集到组件"""
    # 加载页面模板
    page = query_page(args.page)
    tmpl = page.get('template', [])
    if isinstance(tmpl, str):
        tmpl = json.loads(tmpl)

    # 查找组件
    target = None
    for comp in tmpl:
        cfg = comp.get('config', {})
        if isinstance(cfg, str):
            try:
                comp['config'] = json.loads(cfg)
            except:
                comp['config'] = {}

        if comp.get('componentName', '') == args.comp_name:
            target = comp
            break

        # 检查 JGroup 内部
        if comp.get('component') == 'JGroup':
            elements = comp.get('props', {}).get('elements', [])
            for el in elements:
                el_cfg = el.get('config', {})
                if isinstance(el_cfg, str):
                    try:
                        el['config'] = json.loads(el_cfg)
                    except:
                        el['config'] = {}
                if el.get('componentName', '') == args.comp_name:
                    target = el
                    break
            if target:
                break

    if not target:
        print(f'未找到组件: {args.comp_name}')
        return

    # 解析映射
    data_mapping = _parse_mapping(args.mapping)

    # 设置数据集绑定
    cfg = target.get('config', {})
    if isinstance(cfg, str):
        try:
            cfg = json.loads(cfg)
        except:
            cfg = {}
        target['config'] = cfg

    cfg['dataType'] = 2
    cfg['dataSetId'] = args.dataset_id
    cfg['dataSetName'] = args.dataset_name
    cfg['dataSetType'] = args.dataset_type
    cfg['dataSetApi'] = ''
    cfg['dataSetMethod'] = ''
    cfg['dataMapping'] = data_mapping

    # 保存
    bi_utils._page_components[args.page] = tmpl
    save_page(args.page)

    print(f'数据集绑定成功:')
    print(f'  组件: {args.comp_name}')
    print(f'  数据集: {args.dataset_name} ({args.dataset_id})')
    print(f'  类型: {args.dataset_type}')
    print(f'  映射: {json.dumps(data_mapping, ensure_ascii=False)}')


# ============================================================
# CLI 入口
# ============================================================
def main():
    parser = argparse.ArgumentParser(description='大屏数据集操作工具')
    subparsers = parser.add_subparsers(dest='command', help='操作类型')

    # 通用参数（api_base + token）
    def add_common(sub):
        sub.add_argument('api_base', help='API 地址')
        sub.add_argument('token', help='X-Access-Token')

    # list
    p_list = subparsers.add_parser('list', help='列出数据集')
    add_common(p_list)
    p_list.add_argument('--page-size', type=int, default=20, help='每页数量（默认 20）')

    # create-sql
    p_sql = subparsers.add_parser('create-sql', help='创建 SQL 数据集')
    add_common(p_sql)
    p_sql.add_argument('--name', required=True, help='数据集名称')
    p_sql.add_argument('--code', required=True, help='数据集编码')
    p_sql.add_argument('--db-source', required=True, help='数据源 ID')
    p_sql.add_argument('--sql', required=True, help='SQL 查询语句')
    p_sql.add_argument('--fields', required=True, help='字段定义，格式: name:String,value:String')

    # create-api
    p_api = subparsers.add_parser('create-api', help='创建 API 数据集')
    add_common(p_api)
    p_api.add_argument('--name', required=True, help='数据集名称')
    p_api.add_argument('--code', required=True, help='数据集编码')
    p_api.add_argument('--url', required=True, help='API URL')
    p_api.add_argument('--method', default='get', help='HTTP 方法（默认 get）')
    p_api.add_argument('--agent', type=int, default=0, help='是否使用代理（0=否，1=是，默认 0）')
    p_api.add_argument('--fields', required=True, help='字段定义，格式: name:String,value:String')

    # test
    p_test = subparsers.add_parser('test', help='测试数据集')
    add_common(p_test)
    p_test.add_argument('--id', required=True, help='数据集 ID')

    # delete
    p_del = subparsers.add_parser('delete', help='删除数据集')
    add_common(p_del)
    p_del.add_argument('--id', required=True, help='数据集 ID')

    # bind
    p_bind = subparsers.add_parser('bind', help='绑定数据集到组件')
    add_common(p_bind)
    p_bind.add_argument('--page', required=True, help='页面 ID')
    p_bind.add_argument('--comp-name', required=True, help='组件名称')
    p_bind.add_argument('--dataset-id', required=True, help='数据集 ID')
    p_bind.add_argument('--dataset-name', required=True, help='数据集名称')
    p_bind.add_argument('--dataset-type', required=True, choices=['sql', 'api'], help='数据集类型')
    p_bind.add_argument('--mapping', required=True, help='字段映射，格式: 维度=name,数值=value')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    init_api(args.api_base, args.token)

    if args.command == 'list':
        cmd_list(args)
    elif args.command == 'create-sql':
        cmd_create_sql(args)
    elif args.command == 'create-api':
        cmd_create_api(args)
    elif args.command == 'test':
        cmd_test(args)
    elif args.command == 'delete':
        cmd_delete(args)
    elif args.command == 'bind':
        cmd_bind(args)


if __name__ == '__main__':
    main()
