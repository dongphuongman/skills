# -*- coding: utf-8 -*-
"""
JeecgBoot Online 报表 API 调用脚本
自动生成字段 ID（雪花算法格式）
自动 UTF-8 输出
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
# 全局配置（通过 init_api 初始化，无需手动修改此文件）
# ============================================================
_API_BASE = ''
_TOKEN = ''

_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE


def init_api(api_base, token):
    """初始化 API 地址和 Token，调用任何操作函数前必须先执行此函数"""
    global _API_BASE, _TOKEN
    _API_BASE = api_base.rstrip('/')
    _TOKEN = token


def api_request(path, data=None, method=None):
    if not _API_BASE:
        raise RuntimeError("请先调用 init_api(api_base, token) 初始化连接")
    url = f'{_API_BASE}{path}'
    headers = {
        'X-Access-Token': _TOKEN,
        'Content-Type': 'application/json; charset=UTF-8'
    }
    if data is not None:
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        if method is None:
            method = 'POST'
        req = urllib.request.Request(url, data=json_data, headers=headers, method=method)
    else:
        if method is None:
            method = 'GET'
        req = urllib.request.Request(url, headers=headers, method=method)
    resp = urllib.request.urlopen(req, context=_ctx)
    return json.loads(resp.read().decode('utf-8'))


def gen_id():
    """生成雪花ID格式的字符串（19位数字）"""
    return str(int(time.time() * 1000) * 1000000 + random.randint(100000, 999999))


# ==================== 操作函数 ====================

def list_reports():
    """查询所有报表"""
    result = api_request('/online/cgreport/head/list')
    if result.get('success'):
        records = result.get('result', {}).get('records', [])
        print(f'共 {len(records)} 个报表:')
        for r in records:
            print(f"  {r.get('id')} | {r.get('code')} | {r.get('name')} | {r.get('dbSource') or '默认'} | {r.get('createTime')}")
    else:
        print(f"查询失败: {result.get('message')}")


def list_all_reports_table():
    """
    语法糖：查询系统中所有 Online 报表，返回仅含报表名称/编码/SQL 的表格。
    自动分页（每页50条），遍历所有页。
    返回格式：Markdown 表格字符串，供 AI 直接使用。
    """
    PAGE_SIZE = 50
    all_records = []
    page_no = 1
    total = None  # 未成功获取 total 前为 None

    while True:
        result = api_request(f'/online/cgreport/head/list?pageNo={page_no}&pageSize={PAGE_SIZE}')
        if not result.get('success'):
            print(f"[WARN] 第 {page_no} 页查询失败: {result.get('message')}")
            break
        page_data = result.get('result', {})
        records = page_data.get('records') or []
        all_records.extend(records)
        total = page_data.get('total', 0)
        pages = page_data.get('pages', 1)
        if page_no >= pages or not records:
            break
        page_no += 1

    # 构建 Markdown 表格
    lines = []
    lines.append(f"| 报表名称 | 报表编码 | 报表 SQL |")
    lines.append(f"|----------|----------|----------|")
    for r in all_records:
        name = (r.get('name') or '').replace('|', '\\|').replace('\n', ' ')
        code = (r.get('code') or '').replace('|', '\\|').replace('\n', ' ')
        sql = (r.get('cgrSql') or '').replace('|', '\\|').replace('\n', ' ')
        lines.append(f"| {name} | {code} | {sql} |")

    table = '\n'.join(lines)
    # 判断是否还有未显示的数据
    page_info = ""
    if total is not None and len(all_records) < total:
        remaining = total - len(all_records)
        page_info = f"\n> ⚠️ 当前仅返回了 {len(all_records)} 条，还有 {remaining} 条没有显示。\n> 如需继续查询，请传入分页参数重新调用：`pageNo=2&pageSize=50`"
    elif total is not None:
        page_info = f"\n> ✅ 没有更多数据了，已查询全部 {total} 条。"

    summary = f"**共 {len(all_records)} 个 Online 报表**{page_info}\n\n{table}"
    print(summary)
    return summary


def list_fields_by_code_table(code):
    """
    语法糖：根据报表编码查询字段，返回仅含字段编码/显示名/类型三列的表格。
    直接使用 /online/cgreport/item/listByHeadCode?headCode={code} 接口。
    """
    fi = api_request(f'/online/cgreport/item/listByHeadCode?headCode={urllib.parse.quote(code)}')
    if not fi.get('success'):
        print(f"[ERROR] 查询字段失败: {fi.get('message')}")
        return None
    items = fi.get('result') or []

    # 构建 Markdown 表格
    lines = []
    lines.append(f"| 字段编码 | 字段文本(显示名) | 字段类型 |")
    lines.append(f"|----------|-----------------|----------|")
    for it in items:
        fname = (it.get('fieldName') or '').replace('|', '\\|')
        ftxt = (it.get('fieldTxt') or '').replace('|', '\\|')
        ftype = (it.get('fieldType') or '')
        lines.append(f"| {fname} | {ftxt} | {ftype} |")

    table = '\n'.join(lines)
    summary = f"**报表（{code}）— 共 {len(items)} 个字段**\n\n{table}"
    print(summary)
    return summary


def query_report(head_id):
    """查询报表配置（head 详情）"""
    result = api_request(f'/online/cgreport/head/queryById?id={head_id}')
    if result.get('success'):
        data = result.get('result', {})
        print(f"报表: {data.get('name')} (code: {data.get('code')})")
        print(f"SQL: {data.get('cgrSql')}")
        print(f"数据源: {data.get('dbSource') or '默认'}")
    else:
        print(f"查询失败: {result.get('message')}")


def list_fields(head_id):
    """查询报表字段列表"""
    result = api_request(f'/online/cgreport/item/listByHeadId?headId={head_id}')
    if result.get('success'):
        items = result.get('result', [])
        print(f'共 {len(items)} 个字段:')
        for it in items:
            print(f"  {it.get('fieldName')} | {it.get('fieldTxt')} | type={it.get('fieldType')} | show={it.get('isShow')} | search={it.get('isSearch')} | order={it.get('isOrder')}")
    else:
        print(f"查询失败: {result.get('message')}")


def list_params(head_id):
    """查询报表参数列表"""
    result = api_request(f'/online/cgreport/param/listByHeadId?headId={head_id}')
    if result.get('success'):
        items = result.get('result', [])
        print(f'共 {len(items)} 个参数:')
        for it in items:
            print(f"  {it.get('paramName')} | {it.get('paramTxt')} | 默认值={it.get('paramValue')}")
    else:
        print(f"查询失败: {result.get('message')}")


def parse_sql(sql, db_key=''):
    """调用 parseSql 解析 SQL 字段"""
    encoded_sql = urllib.parse.quote(sql, safe='')
    db_key_param = f'&dbKey={db_key}' if db_key else ''
    result = api_request(f'/online/cgreport/head/parseSql?sql={encoded_sql}{db_key_param}')
    if result.get('success'):
        fields = result.get('result', {}).get('fields', [])
        params = result.get('result', {}).get('params', [])
        print(f'SQL 解析成功，字段数: {len(fields)}，参数数: {len(params)}')
        for f in fields:
            print(f"  {f.get('fieldName')} -> {f.get('fieldTxt')} ({f.get('fieldType')})")
        for p in params:
            print(f"  参数: {p.get('paramName')}")
        return result.get('result', {})
    else:
        print(f"解析失败: {result.get('message')}")
        return None


def check_code_available(code):
    """
    检查报表编码是否可用（未被占用）。
    返回 True 表示可用，False 表示已存在。
    """
    encoded = urllib.parse.quote(code, safe='')
    result = api_request(f'/sys/duplicate/check?tableName=onl_cgreport_head&fieldName=code&fieldVal={encoded}')
    available = result.get('success', False)
    if available:
        print(f'编码 [{code}] 可用')
    else:
        print(f'编码 [{code}] 已存在，请更换编码！')
    return available


def create_report(code, name, sql, db_source, items, params):
    """
    创建报表（自动校验编码唯一性）。
    返回 dict，成功时包含 head_id 字段：{'success': True, 'head_id': '...', ...}
    """
    # 先校验编码是否可用
    if not check_code_available(code):
        return {'success': False, 'message': f'报表编码 [{code}] 已存在'}

    report_data = {
        "head": {
            "code": code,
            "name": name,
            "cgrSql": sql,
            "dbSource": db_source
        },
        "items": items,
        "params": params
    }
    result = api_request('/online/cgreport/head/add', report_data)
    if result.get('success'):
        print('报表创建成功!')
        # 查询刚创建的报表 ID
        list_result = api_request(f'/online/cgreport/head/list?code={urllib.parse.quote(code)}')
        if list_result.get('success') and list_result['result']['records']:
            head_id = list_result['result']['records'][0]['id']
            print(f'报表 ID: {head_id}')
            print_menu_sql(head_id, name)
            result['head_id'] = head_id
        return result
    else:
        print(f'创建失败: {result.get("message")}')
        return result


def edit_report(head_id, code, name, sql, db_source, items, params, delete_item_ids=None, delete_param_ids=None):
    """编辑报表"""
    report_data = {
        "head": {
            "id": head_id,
            "code": code,
            "name": name,
            "cgrSql": sql,
            "dbSource": db_source
        },
        "items": items,
        "params": params
    }
    if delete_item_ids:
        report_data["deleteItemIds"] = delete_item_ids
    if delete_param_ids:
        report_data["deleteParamIds"] = delete_param_ids

    result = api_request('/online/cgreport/head/editAll', report_data)
    if result.get('success'):
        print('报表更新成功!')
    else:
        print(f'更新失败: {result.get("message")}')
    return result


def print_menu_sql(head_id, name):
    """输出菜单 SQL"""
    print(f'\n-- 菜单 SQL（可复制执行）')
    print(f"INSERT INTO sys_permission (id, parent_id, name, url, component, component_name, is_route, is_leaf, keep_alive, hidden, hide_tab, description, del_flag, rule_flag, status, internal_or_external, perms_type, sort_no, menu_type, route_redirect) VALUES ('{head_id}', NULL, '{name}', '/online/cgreport/{head_id}', 'modules/online/cgreport/auto/OnlCgreportAutoMain', NULL, 1, 1, 0, 0, 0, NULL, 0, 0, '1', 0, '0', 1.0, 1, NULL);")


# ==================== 菜单 & 权限 ====================

def create_menu(head_id, name, parent_id=''):
    """
    通过 API 创建报表菜单（sys_permission）。
    head_id: 报表 ID，同时作为菜单 ID
    name:    菜单显示名称
    parent_id: 父菜单 ID，默认为空（顶级菜单）
    """
    payload = {
        'id': head_id,
        'name': name,
        'parentId': parent_id,
        'url': f'/online/cgreport/{head_id}',
        'component': 'modules/online/cgreport/auto/OnlCgreportAutoMain',
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
    result = api_request('/sys/permission/add', payload)
    if result.get('success'):
        print(f'菜单创建成功: {name} (id={head_id})')
    else:
        print(f'菜单创建失败: {result.get("message")}')
    return result


def get_role_id_by_code(role_code):
    """按 roleCode 查找角色 ID，找不到返回 None"""
    result = api_request('/sys/role/list?pageNo=1&pageSize=100')
    for role in result.get('result', {}).get('records', []):
        if role.get('roleCode') == role_code:
            return role['id']
    return None


def grant_menu_to_role(role_id, menu_id):
    """
    将菜单授权给指定角色（追加，不覆盖已有权限）。
    使用 JSON body 发送，避免 URL 过长（管理员权限可达千条）。
    """
    existing = api_request(f'/sys/permission/queryRolePermission?roleId={role_id}').get('result') or []
    if menu_id in existing:
        print(f'菜单 {menu_id} 已授权给角色 {role_id}，无需重复操作')
        return True
    new_perms = existing + [menu_id]
    result = api_request('/sys/permission/saveRolePermission', {
        'roleId': role_id,
        'permissionIds': ','.join(new_perms),
        'lastPermissionIds': ','.join(existing),
    })
    if result.get('success'):
        print(f'菜单授权成功 → 角色 {role_id}')
    else:
        print(f'菜单授权失败: {result.get("message")}')
    return result.get('success', False)


def add_data_rule(menu_id, role_id, rule_name, rule_column, rule_conditions, rule_value):
    """
    完整四步数据规则配置：创建 → 启用 → 授权角色 → 返回规则 ID。
    rule_value: 字符串类型的值需加单引号，例如 "'1'" 而非 "1"
    rule_conditions: 条件符，如 '!='、'='、'like'、'>='、'<='、'in'
    返回规则 ID（字符串），失败返回 None。
    """
    # Step 1: 创建规则
    r1 = api_request('/sys/permission/addPermissionRule', {
        'permissionId': menu_id,
        'ruleName': rule_name,
        'ruleColumn': rule_column,
        'ruleConditions': rule_conditions,
        'ruleValue': rule_value,
    })
    if not r1.get('success'):
        print(f'创建数据规则失败: {r1.get("message")}')
        return None
    # addPermissionRule 返回 result=null，需查询列表获取刚创建的规则 ID
    rule_id = r1.get('result')
    if not rule_id:
        rules_r = api_request(f'/sys/permission/queryPermissionRule?permissionId={menu_id}')
        for rule in rules_r.get('result') or []:
            if rule.get('ruleName') == rule_name and rule.get('status') is None:
                rule_id = rule['id']
                break
    if not rule_id:
        print(f'创建数据规则失败: 无法获取规则 ID')
        return None
    print(f'数据规则已创建: {rule_name} (id={rule_id})')

    # Step 2: 启用规则（status:"1"）
    r2 = api_request('/sys/permission/editPermissionRule', {
        'id': rule_id,
        'permissionId': menu_id,
        'ruleName': rule_name,
        'ruleColumn': rule_column,
        'ruleConditions': rule_conditions,
        'ruleValue': rule_value,
        'status': '1',
    })
    if not r2.get('success'):
        print(f'启用数据规则失败: {r2.get("message")}')
        return None
    print(f'数据规则已启用')

    # Step 3: 授权给角色
    r3 = api_request('/sys/role/datarule', {
        'permissionId': menu_id,
        'roleId': role_id,
        'dataRuleIds': rule_id,
    })
    if not r3.get('success'):
        print(f'数据规则授权角色失败: {r3.get("message")}')
        return None
    print(f'数据规则已授权给角色 {role_id}')
    return rule_id


def get_report_id_by_code(code):
    """按报表编码查询报表 ID，找不到返回 None"""
    result = api_request(f'/online/cgreport/head/list?pageNo=1&pageSize=10&code={urllib.parse.quote(code)}')
    records = result.get('result', {}).get('records', [])
    if records:
        return records[0]['id']
    return None


def validate_report(head_id):
    """
    验证报表 SQL 是否可正常执行。
    返回 True/False，成功时打印字段数和行数。
    """
    result = api_request(f'/online/cgreport/api/getColumnsAndData/{head_id}')
    if result.get('success'):
        r = result.get('result', {})
        cols = r.get('columns', [])
        rows = r.get('rows', [])
        print(f'✅ SQL 验证通过：{len(cols)} 个字段，{len(rows)} 行数据')
        return True
    else:
        print(f'❌ SQL 验证失败：{result.get("message")}')
        return False


def publish_report(head_id, name, role_code='admin', parent_id=''):
    """
    发布报表三步合一：验证 SQL + 创建菜单 + 授权角色。
    head_id:   报表 ID
    name:      菜单显示名称
    role_code: 授权目标角色编码，默认 'admin'
    parent_id: 父菜单 ID，默认空（顶级菜单）
    返回 True/False。
    """
    # Step 1: 验证 SQL
    if not validate_report(head_id):
        return False

    # Step 2: 创建菜单
    menu_result = create_menu(head_id, name, parent_id)
    if not menu_result.get('success'):
        return False

    # Step 3: 授权角色
    role_id = get_role_id_by_code(role_code)
    if not role_id:
        print(f'❌ 找不到角色 [{role_code}]')
        return False
    ok = grant_menu_to_role(role_id, head_id)
    if ok:
        print(f'\n🎉 发布完成！访问地址：{_API_BASE.replace("/jeecg-boot", "")}/#/online/cgreport/{head_id}')
    return ok


def create_and_publish(code, name, sql, items, params=None, db_source='', role_code='admin', parent_id=''):
    """
    一键完整流程：创建报表 + 验证 SQL + 创建菜单 + 授权角色。
    code:      报表编码
    name:      报表/菜单名称
    sql:       报表 SQL
    items:     字段配置列表（用 build_item() 构建）
    params:    参数列表，默认空
    db_source: 数据源，默认空（系统默认库）
    role_code: 授权角色编码，默认 'admin'
    parent_id: 父菜单 ID，默认空
    返回 head_id（字符串），失败返回 None。
    """
    if params is None:
        params = []

    result = create_report(code, name, sql, db_source, items, params)
    if not result.get('success'):
        return None

    head_id = result.get('head_id')
    if not head_id:
        print('❌ 未获取到报表 ID')
        return None

    ok = publish_report(head_id, name, role_code, parent_id)
    return head_id if ok else None


# ==================== 字段构建辅助 ====================

# 按字段名关键词推断默认配置
_FIELD_RULES = [
    # (关键词列表, fieldType, isShow, isSearch, searchMode, isOrder, dictCode)
    (['id'],                          'String',     0, None,  None,    None, None),
    (['create_by', 'update_by'],      'String',     0, None,  None,    None, None),
    (['sys_org_code', 'tenant_id',
      'org_code'],                    'String',     0, None,  None,    None, None),
    (['avatar', 'photo', 'image',
      'pic', 'img'],                  'Image',      1, None,  None,    None, None),
    (['create_time', 'update_time'],  'Datetime',   1, None,  None,    1,    None),
    (['amount', 'money', 'price',
      'fee', 'cost', 'total'],        'BigDecimal', 1, None,  None,    1,    None),
    (['count', 'qty', 'num',
      'number', 'quantity'],          'Integer',    1, None,  None,    1,    None),
    (['birthday', 'date'],            'Date',       1, 1,     'group', None, None),
    (['time', 'datetime'],            'Datetime',   1, 1,     'group', 1,    None),
    (['sex'],                         'String',     1, 1,     'single',None, 'sex'),
    (['status'],                      'String',     1, 1,     'single',None, 'valid_status'),
    (['email'],                       'String',     1, None,  None,    None, None),
    (['phone', 'mobile', 'tel'],      'String',     1, None,  None,    None, None),
    (['remark', 'description',
      'content', 'note'],             'String',     1, None,  None,    None, None),
    (['name', 'title'],               'String',     1, 1,     'single',None, None),
    (['code', 'no'],                  'String',     1, 1,     'single',None, None),
    (['type', 'category', 'kind'],    'String',     1, 1,     'single',None, None),
    (['dept', 'org', 'depart'],       'String',     1, 1,     'single',None, None),
]


def build_item(field_name, field_txt=None, field_type=None, order_num=0,
               is_show=None, is_search=None, search_mode=None,
               is_order=None, is_total=None, dict_code=None,
               field_href=None, field_width=None, replace_val=None, group_title=None):
    """
    构建字段配置 dict，按字段名语义自动推断默认值，支持手动覆盖任意属性。

    用法示例：
        build_item('username', '用户名')
        build_item('amount', '金额', is_total='1')
        build_item('status', '状态', dict_code='my_status_dict')
        build_item('email', '邮箱', field_href='mailto:${email}')

    自动推断规则（可被参数覆盖）：
    - id / create_by / update_by / sys_org_code → 隐藏
    - avatar/photo/image → Image 类型
    - amount/money/price → BigDecimal，合计
    - count/qty/num → Integer，合计
    - birthday/date → Date，范围查询
    - create_time/update_time → Datetime，可排序
    - sex → dictCode=sex
    - status → dictCode=valid_status
    - name/title/code → 单值查询
    """
    fname_lower = field_name.lower()

    # 默认值
    _type     = 'String'
    _show     = 1
    _search   = None
    _mode     = None
    _order    = None
    _total    = None
    _dict     = None

    for keywords, t, show, search, mode, order, dc in _FIELD_RULES:
        if any(kw == fname_lower or fname_lower.endswith('_' + kw) or fname_lower.startswith(kw + '_') or fname_lower == kw
               for kw in keywords):
            _type, _show, _search, _mode, _order, _dict = t, show, search, mode, order, dc
            break

    # 手动覆盖
    return {
        'id':          gen_id(),
        'headId':      None,
        'fieldName':   field_name,
        'fieldTxt':    field_txt or field_name,
        'fieldType':   field_type  if field_type  is not None else _type,
        'isShow':      is_show     if is_show      is not None else _show,
        'isSearch':    is_search   if is_search    is not None else _search,
        'searchMode':  search_mode if search_mode  is not None else _mode,
        'isOrder':     is_order    if is_order     is not None else _order,
        'isTotal':     is_total    if is_total     is not None else _total,
        'dictCode':    dict_code   if dict_code    is not None else _dict,
        'fieldHref':   field_href,
        'fieldWidth':  field_width,
        'orderNum':    order_num,
        'replaceVal':  replace_val,
        'groupTitle':  group_title,
        'createBy':    None, 'createTime': None, 'updateBy': None, 'updateTime': None,
    }


def query_data_rules(menu_id, role_id):
    """
    查询指定菜单下对某角色生效的数据规则。
    返回 dict: {'datarule': [...], 'drChecked': '...'}
    """
    result = api_request(f'/sys/role/datarule/{menu_id}/{role_id}')
    if result.get('success'):
        data = result.get('result', {})
        rules = data.get('datarule', [])
        checked = data.get('drChecked', '')
        print(f'共 {len(rules)} 条数据规则，已授权: {checked or "（无）"}')
        for r in rules:
            active = '✓' if r['id'] in (checked or '') else '✗'
            print(f'  [{active}] {r["ruleName"]}: {r["ruleColumn"]} {r["ruleConditions"]} {r["ruleValue"]} (status={r["status"]})')
        return data
    else:
        print(f'查询失败: {result.get("message")}')
        return None


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='JeecgBoot Online 报表 API 工具')
    parser.add_argument('--api-base', required=True, help='JeecgBoot 后端地址，如 http://192.168.x.x:8080/jeecgboot')
    parser.add_argument('--token', required=True, help='X-Access-Token')
    parser.add_argument('--action', '-a', required=True,
                        choices=['list', 'list-table', 'fields-table', 'query', 'fields', 'params', 'parse', 'create', 'edit'],
                        help='操作类型')
    parser.add_argument('--id', help='报表 ID（用于 query/fields/params/edit）')
    parser.add_argument('--code', help='报表编码')
    parser.add_argument('--name', help='报表名称（用于 create）')
    parser.add_argument('--sql', help='SQL 语句（用于 create/parse）')
    parser.add_argument('--db', help='数据源编码')
    args = parser.parse_args()
    init_api(args.api_base, args.token)

    if args.action == 'list':
        list_reports()
    elif args.action == 'list-table':
        list_all_reports_table()
    elif args.action == 'fields-table' and args.code:
        list_fields_by_code_table(args.code)
    elif args.action == 'query' and args.id:
        query_report(args.id)
    elif args.action == 'fields' and args.id:
        list_fields(args.id)
    elif args.action == 'params' and args.id:
        list_params(args.id)
    elif args.action == 'parse' and args.sql:
        parse_sql(args.sql, args.db or '')
    else:
        parser.print_help()
