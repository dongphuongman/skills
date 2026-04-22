# -*- coding: utf-8 -*-
"""
JeecgBoot Online 图表 API 调用脚本

功能：
  - 校验图表编码唯一性
  - 解析 SQL 字段（parseSql）
  - 创建 / 编辑图表
  - 查询图表列表 / 详情 / 字段
  - 发布图表：挂载菜单 + 授权角色
  - 一键全流程：create_and_publish()

用法示例：
    import sys
    sys.path.insert(0, '/path/to/jeecg-onlchart/scripts')
    from onlchart_api import init_api, build_item, create_and_publish
    init_api('<api_base>', '<token>')

    items = [
        build_item('sex',    '性别',   order_num=0, dict_code='sex'),
        build_item('cout',   '人数',   order_num=1, is_total='Y'),
    ]
    create_and_publish(
        code='tj_user_sex',
        name='用户性别分布',
        sql='SELECT sex, count(*) cout FROM sys_user GROUP BY sex',
        x='sex', y='cout',
        graph_type='bar',
        items=items,
    )
"""
import urllib.request
import json
import time
import random
import ssl
import urllib.parse
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# 全局配置（通过 init_api 初始化）
# ============================================================
_API_BASE = ''
_TOKEN = ''

_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE


def init_api(api_base, token):
    """初始化 API 地址和 Token，所有操作前必须先调用"""
    global _API_BASE, _TOKEN
    _API_BASE = api_base.rstrip('/')
    _TOKEN = token


def _api_request(path, data=None, method=None, timeout=30):
    if not _API_BASE:
        raise RuntimeError('请先调用 init_api(api_base, token) 初始化连接')
    url = f'{_API_BASE}{path}'
    headers = {'X-Access-Token': _TOKEN, 'Content-Type': 'application/json; charset=UTF-8'}
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        method = method or 'POST'
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
    else:
        method = method or 'GET'
        req = urllib.request.Request(url, headers=headers, method=method)
    resp = urllib.request.urlopen(req, context=_ctx, timeout=timeout)
    return json.loads(resp.read().decode('utf-8'))


def gen_id():
    """生成雪花ID格式字符串（19位数字）"""
    return str(int(time.time() * 1000) * 1000000 + random.randint(100000, 999999))


# ==================== 图表查询 ====================

def list_charts(page_no=1, page_size=20):
    """查询图表列表"""
    result = _api_request(f'/online/graphreport/head/list?pageNo={page_no}&pageSize={page_size}')
    if result.get('success'):
        records = result['result']['records']
        total = result['result']['total']
        print(f'共 {total} 个图表（当前第 {page_no} 页，{len(records)} 条）:')
        for r in records:
            print(f"  {r['id']} | {r['code']} | {r['name']} | {r.get('graphType')} | {r.get('dataType')}")
    else:
        print(f'查询失败: {result.get("message")}')
    return result


def query_chart(head_id):
    """按 ID 查询图表详情"""
    result = _api_request(f'/online/graphreport/head/queryById?id={head_id}')
    if result.get('success'):
        d = result['result']
        print(f"图表: {d['name']} (code={d['code']})")
        print(f"类型: {d.get('graphType')} | X轴: {d.get('xaxisField')} | Y轴: {d.get('yaxisField')}")
        print(f"SQL: {d.get('cgrSql', '')[:200]}")
    else:
        print(f'查询失败: {result.get("message")}')
    return result


def get_chart_id_by_code(code):
    """按编码查询图表 head_id，找不到返回 None"""
    result = _api_request(f'/online/graphreport/head/list?code={urllib.parse.quote(code)}')
    records = result.get('result', {}).get('records', [])
    return records[0]['id'] if records else None


def list_chart_fields(head_id):
    """查询图表字段列表"""
    result = _api_request(f'/online/graphreport/head/queryOnlGraphreportItemByMainId?headId={head_id}')
    if result.get('success'):
        items = result.get('result', [])
        print(f'共 {len(items)} 个字段:')
        for it in items:
            print(f"  {it.get('fieldName')} | {it.get('fieldTxt')} | show={it.get('isShow')} | search={it.get('searchFlag')} | total={it.get('isTotal')}")
    else:
        print(f'查询失败: {result.get("message")}')
    return result


# ==================== 编码校验 ====================

def check_code_available(code):
    """
    检查图表编码是否可用（未被占用）。
    返回 True 表示可用，False 表示已存在。
    """
    encoded = urllib.parse.quote(code, safe='')
    result = _api_request(
        f'/sys/duplicate/check?tableName=onl_graphreport_head&fieldName=code&fieldVal={encoded}'
    )
    available = result.get('result', False)
    if available:
        print(f'编码 [{code}] 可用')
    else:
        print(f'编码 [{code}] 已存在，请更换编码！')
    return available


# ==================== SQL 解析 ====================

def parse_sql(sql, db_key=''):
    """
    调用 parseSql 解析 SQL，返回 {'fields': [...], 'params': [...]}。
    失败返回 None。
    """
    encoded = urllib.parse.quote(sql, safe='')
    db_param = f'&dbKey={db_key}' if db_key else ''
    result = _api_request(f'/online/cgreport/head/parseSql?sql={encoded}{db_param}')
    if result.get('success'):
        fields = result['result']['fields']
        params = result['result'].get('params', [])
        print(f'SQL 解析成功：{len(fields)} 个字段，{len(params)} 个参数')
        for f in fields:
            print(f"  {f['fieldName']} ({f.get('fieldType', 'String')})")
        return result['result']
    else:
        print(f'SQL 解析失败: {result.get("message")}')
        return None


# ==================== 图表创建 / 编辑 ====================

def create_chart(code, name, sql, x, y, items, graph_type='bar',
                 display_template='tab', data_type='sql',
                 db_source='', params=None, is_combination=False):
    """
    创建图表（自动校验编码唯一性）。
    返回 dict，成功时包含 head_id：{'success': True, 'head_id': '...'}

    参数说明：
      code             图表编码（唯一）
      name             图表名称
      sql              SQL 语句（dataType=sql 时）或 JSON 字符串（dataType=json 时）
      x                X 轴字段名
      y                Y 轴字段名，多个用逗号分隔
      items            字段配置列表，用 build_item() 构建
      graph_type       图表类型，如 'bar'、'line'、'pie'、'table'、'bar,line'
      display_template 展示模板：'tab'（默认）/ 'single' / 'double'
      data_type        数据类型：'sql'（默认）/ 'json' / 'api'
      db_source        数据源编码，空字符串表示默认数据源
      params           自定义参数列表，格式见 build_param()
      is_combination   是否为组合图表（折线+柱状同坐标系），True 时 graphType 应为 'line,bar'
    """
    if not check_code_available(code):
        return {'success': False, 'message': f'图表编码 [{code}] 已存在'}

    if params is None:
        params = []

    body = {
        'dbSource': db_source,
        'name': name,
        'code': code,
        'displayTemplate': display_template,
        'xaxisField': x,
        'yaxisField': y,
        'dataType': data_type,
        'graphType': graph_type,
        'cgrSql': sql,
        'onlGraphreportItemList': items,
        'paramsList': params,
    }
    if is_combination:
        body['isCombination'] = 'combination'

    result = _api_request('/online/graphreport/head/add', body)
    if result.get('success'):
        print(f'图表创建成功: {name}')
        time.sleep(0.3)
        head_id = get_chart_id_by_code(code)
        if head_id:
            print(f'图表 ID: {head_id}')
            result['head_id'] = head_id
        return result
    else:
        print(f'图表创建失败: {result.get("message")}')
        return result


def edit_chart(head_id, code, name, sql, x, y, items, graph_type='bar',
               display_template='tab', data_type='sql', db_source='',
               params=None, is_combination=False,
               tenant_id=0, y_axis_text='', extend_js=None):
    """
    编辑图表（PUT）。
    items 中每条记录需包含 graphreportHeadId=head_id（与 add 时的 cgrheadId 字段名不同）。
    """
    if params is None:
        params = []

    body = {
        'id': head_id,
        'name': name,
        'code': code,
        'cgrSql': sql,
        'xaxisField': x,
        'yaxisField': y,
        'yaxisText': y_axis_text,
        'extendJs': extend_js,
        'graphType': graph_type,
        'isCombination': 'combination' if is_combination else None,
        'displayTemplate': display_template,
        'dataType': data_type,
        'dbSource': db_source,
        'tenantId': tenant_id,
        'lowAppId': None,
        'onlGraphreportItemList': items,
        'paramsList': params,
    }
    result = _api_request('/online/graphreport/head/edit', body, method='PUT')
    if result.get('success'):
        print(f'图表更新成功: {name}')
    else:
        print(f'图表更新失败: {result.get("message")}')
    return result


# ==================== 菜单 & 权限（与 onlreport_api 同逻辑）====================

def create_menu(head_id, name, parent_id=''):
    """
    通过 API 创建图表菜单。
    菜单 URL 使用 head_id（不是 code）：/online/graphreport/chart/{head_id}
    """
    payload = {
        'id': head_id,
        'name': name,
        'parentId': parent_id,
        'url': f'/online/graphreport/chart/{head_id}',
        'component': 'super/online/graphreport/auto/GraphreportAutoChart',
        'isRoute': 1,
        'isLeaf': '1',
        'keepAlive': 0,
        'hidden': 0,
        'hideTab': 0,
        'status': '1',
        'menuType': 1,
        'sortNo': 1.0,
        'alwaysShow': 0,
        'internalOrExternal': False,
        'permsType': '0',
        'ruleFlag': 0,
    }
    result = _api_request('/sys/permission/add', payload)
    if result.get('success'):
        print(f'菜单创建成功: {name} (id={head_id})')
    else:
        print(f'菜单创建失败: {result.get("message")}')
    return result


def get_role_id_by_code(role_code):
    """按 roleCode 查找角色 ID，找不到返回 None"""
    result = _api_request('/sys/role/list?pageNo=1&pageSize=100')
    for role in result.get('result', {}).get('records', []):
        if role.get('roleCode') == role_code:
            return role['id']
    return None


def grant_menu_to_role(role_id, menu_id):
    """
    将菜单追加授权给角色（不覆盖已有权限）。
    使用 JSON body 发送，避免 URL 过长（管理员权限可达千条）。
    """
    existing = _api_request(f'/sys/permission/queryRolePermission?roleId={role_id}').get('result') or []
    if menu_id in existing:
        print(f'菜单 {menu_id} 已授权给角色 {role_id}，跳过')
        return True
    new_perms = existing + [menu_id]
    # admin 权限条目可达千条，服务端 diff 耗时较长，需要更大超时
    result = _api_request('/sys/permission/saveRolePermission', {
        'roleId': role_id,
        'permissionIds': ','.join(new_perms),
        'lastPermissionIds': ','.join(existing),
    }, timeout=120)
    if result.get('success'):
        print(f'菜单授权成功 → 角色 {role_id}')
    else:
        print(f'菜单授权失败: {result.get("message")}')
    return result.get('success', False)


def publish_chart(head_id, name, role_code='admin', parent_id=''):
    """
    发布图表三步合一：创建菜单 + 授权角色。
    返回 True/False。
    """
    # 创建菜单
    menu_result = create_menu(head_id, name, parent_id)
    if not menu_result.get('success'):
        return False

    # 授权角色
    role_id = get_role_id_by_code(role_code)
    if not role_id:
        print(f'❌ 找不到角色 [{role_code}]')
        return False

    ok = grant_menu_to_role(role_id, head_id)
    if ok:
        base_url = _API_BASE.replace('/jeecg-boot', '').replace('/jeecgboot', '')
        print(f'\n🎉 发布完成！访问地址：{base_url}/#/online/graphreport/chart/{head_id}')
    return ok


def create_and_publish(code, name, sql, x, y, items, graph_type='bar',
                       display_template='tab', data_type='sql', db_source='',
                       params=None, is_combination=False,
                       role_code='admin', parent_id=''):
    """
    一键全流程：创建图表 + 挂载菜单 + 授权角色。

    参数与 create_chart() 相同，额外支持：
      role_code   授权角色编码，默认 'admin'
      parent_id   父菜单 ID，默认空（顶级菜单）

    返回 head_id（字符串），失败返回 None。
    """
    result = create_chart(code, name, sql, x, y, items,
                          graph_type=graph_type,
                          display_template=display_template,
                          data_type=data_type,
                          db_source=db_source,
                          params=params,
                          is_combination=is_combination)
    if not result.get('success'):
        return None

    head_id = result.get('head_id')
    if not head_id:
        print('❌ 未获取到图表 ID')
        return None

    ok = publish_chart(head_id, name, role_code, parent_id)
    return head_id if ok else None


# ==================== 字段构建辅助 ====================

def build_item(field_name, field_txt=None, field_type='String', order_num=0,
               is_show='Y', search_flag='N', search_mode=None,
               is_total='N', dict_code=None, field_href=None):
    """
    构建图表字段配置 dict。

    参数说明：
      field_name    字段名（与 SQL 列名一致）
      field_txt     显示名称，默认同 field_name
      field_type    字段类型：'String'（默认）/ 'Integer' / 'BigDecimal' / 'Date'
      order_num     排序序号，从 0 开始
      is_show       是否显示：'Y'（默认）/ 'N'
      search_flag   是否作为查询条件：'N'（默认）/ 'Y'
      search_mode   查询模式：'single'（单值）/ 'group'（范围），search_flag='Y' 时生效
      is_total      是否合计：'N'（默认）/ 'Y'，适用于数值字段
      dict_code     字典编码或字典 SQL，用于值替换显示
      field_href    字段跳转链接

    用法示例：
        build_item('sex',    '性别',   search_flag='Y', search_mode='single', dict_code='sex')
        build_item('salary', '月薪',   field_type='Integer', is_total='Y')
        build_item('name',   '姓名',   search_flag='Y', search_mode='single')
    """
    return {
        'id':         gen_id(),
        'cgrheadId':  None,          # add 时为 None；edit 时需改为 graphreportHeadId=head_id
        'fieldName':  field_name,
        'fieldTxt':   field_txt or field_name,
        'fieldWidth': None,
        'fieldType':  field_type,
        'searchFlag': search_flag,
        'searchMode': search_mode,
        'isOrder':    None,
        'isSearch':   None,
        'dictCode':   dict_code,
        'fieldHref':  field_href,
        'isShow':     is_show,
        'orderNum':   order_num,
        'replaceVal': None,
        'isTotal':    is_total,
        'createBy':   None, 'createTime': None,
        'updateBy':   None, 'updateTime': None,
        'groupTitle': None,
    }


def build_param(param_name, param_txt, param_value='', order_num=1):
    """
    构建自定义参数配置 dict（对应 SQL 中的 ${paramName}）。

    参数说明：
      param_name    参数名，与 SQL 中 ${} 内的名称一致
      param_txt     参数显示名称（页面上的标签）
      param_value   默认值，默认空字符串
      order_num     排序序号，从 1 开始
    """
    return {
        'paramName':  param_name,
        'paramTxt':   param_txt,
        'paramValue': param_value,
        'orderNum':   order_num,
    }


# ==================== CLI 入口 ====================

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='JeecgBoot Online 图表 API 工具')
    parser.add_argument('--api-base', required=True, help='后端地址，如 http://192.168.x.x:8080/jeecg-boot')
    parser.add_argument('--token',    required=True, help='X-Access-Token')
    parser.add_argument('--action', '-a', required=True,
                        choices=['list', 'query', 'fields', 'parse'],
                        help='操作类型')
    parser.add_argument('--id',   help='图表 head_id')
    parser.add_argument('--code', help='图表编码')
    parser.add_argument('--sql',  help='SQL 语句（用于 parse）')
    parser.add_argument('--db',   help='数据源编码')
    args = parser.parse_args()
    init_api(args.api_base, args.token)

    if args.action == 'list':
        list_charts()
    elif args.action == 'query' and args.id:
        query_chart(args.id)
    elif args.action == 'fields' and args.id:
        list_chart_fields(args.id)
    elif args.action == 'parse' and args.sql:
        parse_sql(args.sql, args.db or '')
    else:
        parser.print_help()
