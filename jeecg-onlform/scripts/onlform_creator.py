"""
JeecgBoot Online 表单创建/编辑工具脚本

用法:
  python onlform_creator.py --api-base <URL> --token <TOKEN> --config <config.json>

config.json 格式见下方示例。

支持的操作:
  - 单表创建 (tableType=1)
  - 主子表创建 (主表 tableType=2 + 子表 tableType=3)
  - 树表创建 (tableType=1, isTree='Y')
  - 编辑表单 (action='edit')
"""

import urllib.request
import json
import sys
import ssl
import random
import string
from concurrent.futures import ThreadPoolExecutor, as_completed

# 修复 Windows 控制台中文乱码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
import argparse

# 全局 SSL 上下文（HTTPS 支持）
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE


# ====== 工具函数 ======

def rand_id(prefix=''):
    chars = string.ascii_lowercase + string.digits
    suffix = ''.join(random.choices(chars, k=8))
    return f'{prefix}{suffix}'


def api_request(api_base, token, path, data=None, method='POST'):
    url = f'{api_base}{path}'
    # GET 请求加时间戳防缓存（JeecgBoot 服务端可能缓存 listByHeadId 等查询）
    if method == 'GET':
        import time as _time
        sep = '&' if '?' in url else '?'
        url += f'{sep}_t={int(_time.time() * 1000)}'
    headers = {
        'X-Access-Token': token,
        'Content-Type': 'application/json; charset=UTF-8'
    }
    if data is not None:
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    resp = urllib.request.urlopen(req, context=_ssl_ctx)
    return json.loads(resp.read().decode('utf-8'))


def resolve_head_id(api_base, token, edit_config):
    """从 headId 或 tableName 解析出 (head_id, head_record)
    head_record 来自 head/list，可直接作为 editAll 的 head，避免额外查询。
    """
    head_id = edit_config.get('headId')
    table_name = edit_config.get('tableName')
    if head_id and not table_name:
        # 有 headId 无 tableName，仍需查 head 记录
        result = api_request(api_base, token,
                             f'/online/cgform/head/list?copyType=0&pageNo=1&pageSize=1&id={head_id}',
                             method='GET')
        records = result.get('result', {}).get('records', [])
        if not records:
            # fallback: queryById
            qr = api_request(api_base, token, f'/online/cgform/head/queryById?id={head_id}', method='GET')
            return head_id, qr.get('result')
        return head_id, records[0]
    elif table_name:
        result = api_request(api_base, token,
                             f'/online/cgform/head/list?tableName={table_name}&copyType=0&pageNo=1&pageSize=1',
                             method='GET')
        records = result.get('result', {}).get('records', [])
        if not records:
            print(f'错误: 表 {table_name} 不存在')
            sys.exit(1)
        rec = records[0]
        return rec['id'], rec
    else:
        print('错误: 编辑配置必须提供 headId 或 tableName')
        sys.exit(1)


def get_head_and_fields(api_base, token, head_id, head_record=None):
    """获取表单 head + fields + indexs，带 getByHead → fallback 链。
    如果已有 head_record（来自 resolve_head_id），则并行只查 fields。
    """
    # 优先尝试 getByHead（一次请求拿全部）
    try:
        detail = api_request(api_base, token,
                             f'/online/cgform/api/getByHead?id={head_id}', method='GET')
        if detail.get('success') and detail.get('result'):
            r = detail['result']
            if r.get('head') and r.get('fields'):
                return r['head'], r['fields'], r.get('indexs', [])
    except Exception:
        pass

    # fallback: 并行查询 head（如果没有）+ fields
    head = head_record
    fields = None

    if head:
        # 已有 head，只查 fields
        fields = _query_fields(api_base, token, head_id)
    else:
        # 并行查 head 和 fields
        with ThreadPoolExecutor(max_workers=2) as pool:
            fh = pool.submit(api_request, api_base, token,
                             f'/online/cgform/head/queryById?id={head_id}', None, 'GET')
            ff = pool.submit(_query_fields, api_base, token, head_id)
            head = fh.result().get('result')
            fields = ff.result()

    return head, fields, []


def _query_fields(api_base, token, head_id):
    """查询字段列表，优先 listByHeadId，fallback field/list 分页"""
    try:
        r = api_request(api_base, token,
                        f'/online/cgform/field/listByHeadId?headId={head_id}', method='GET')
        if r.get('success') and r.get('result'):
            return r['result']
    except Exception:
        pass
    # fallback: field/list 分页 + 过滤
    all_fields = []
    page = 1
    while True:
        r = api_request(api_base, token,
                        f'/online/cgform/field/list?headId={head_id}&pageNo={page}&pageSize=500',
                        method='GET')
        records = r.get('result', {}).get('records', [])
        if not records:
            break
        for f in records:
            if f.get('cgformHeadId') == head_id:
                all_fields.append(f)
        total = r.get('result', {}).get('total', 0)
        if page * 500 >= total:
            break
        page += 1
    return all_fields


def make_system_fields():
    """生成6个系统默认字段（注意：checkbox 字段必须用字符串 '1'/'0'）"""
    return [
        {"id": rand_id("id"), "dbFieldName": "id", "dbFieldTxt": "主键", "queryConfigFlag": "0", "fieldMustInput": "1", "isShowForm": "0", "isShowList": "0", "isReadOnly": "1", "fieldShowType": "text", "fieldLength": 120, "isQuery": "0", "queryMode": "single", "dbLength": 36, "dbPointLength": 0, "dbType": "string", "dbIsKey": "1", "dbIsNull": "0", "orderNum": 0},
        {"id": rand_id("createby"), "dbFieldName": "create_by", "dbFieldTxt": "创建人", "queryConfigFlag": "0", "fieldMustInput": "0", "isShowForm": "0", "isShowList": "0", "sortFlag": "0", "isReadOnly": "0", "fieldShowType": "text", "fieldLength": 120, "isQuery": "0", "queryMode": "single", "dbLength": 50, "dbPointLength": 0, "dbType": "string", "dbIsKey": "0", "dbIsNull": "1", "orderNum": 1},
        {"id": rand_id("createti"), "dbFieldName": "create_time", "dbFieldTxt": "创建时间", "queryConfigFlag": "0", "fieldMustInput": "0", "isShowForm": "0", "isShowList": "0", "sortFlag": "0", "isReadOnly": "0", "fieldShowType": "datetime", "fieldLength": 120, "isQuery": "0", "queryMode": "single", "dbLength": 50, "dbPointLength": 0, "dbType": "Datetime", "dbIsKey": "0", "dbIsNull": "1", "orderNum": 2},
        {"id": rand_id("updateby"), "dbFieldName": "update_by", "dbFieldTxt": "更新人", "queryConfigFlag": "0", "fieldMustInput": "0", "isShowForm": "0", "isShowList": "0", "sortFlag": "0", "isReadOnly": "0", "fieldShowType": "text", "fieldLength": 120, "isQuery": "0", "queryMode": "single", "dbLength": 50, "dbPointLength": 0, "dbType": "string", "dbIsKey": "0", "dbIsNull": "1", "orderNum": 3},
        {"id": rand_id("updateti"), "dbFieldName": "update_time", "dbFieldTxt": "更新时间", "queryConfigFlag": "0", "fieldMustInput": "0", "isShowForm": "0", "isShowList": "0", "sortFlag": "0", "isReadOnly": "0", "fieldShowType": "datetime", "fieldLength": 120, "isQuery": "0", "queryMode": "single", "dbLength": 50, "dbPointLength": 0, "dbType": "Datetime", "dbIsKey": "0", "dbIsNull": "1", "orderNum": 4},
        {"id": rand_id("sysorgco"), "dbFieldName": "sys_org_code", "dbFieldTxt": "所属部门", "queryConfigFlag": "0", "fieldMustInput": "0", "isShowForm": "0", "isShowList": "0", "sortFlag": "0", "isReadOnly": "0", "fieldShowType": "text", "fieldLength": 120, "isQuery": "0", "queryMode": "single", "dbLength": 64, "dbPointLength": 0, "dbType": "string", "dbIsKey": "0", "dbIsNull": "1", "orderNum": 5},
    ]


def make_field(order, db_name, db_txt, show_type='text', db_type='string', db_length=100,
               db_point=0, must_input='0', is_query='0', query_mode='single',
               is_show_form='1', is_show_list='1', is_read_only='0', sort_flag='0',
               dict_field='', dict_table='', dict_text='',
               field_valid_type='', field_default_value='', field_extend_json='',
               field_length=120, main_table='', main_field='',
               query_config_flag='0', query_show_type=None,
               query_dict_field='', query_dict_table='', query_dict_text='', query_def_val='',
               db_is_persist=1, field_href='', converter=''):
    """生成业务字段配置（注意：checkbox 字段必须用字符串 '1'/'0'）"""
    field = {
        "id": rand_id(db_name[:8]),
        "dbFieldName": db_name,
        "dbFieldTxt": db_txt,
        "queryShowType": query_show_type,
        "queryDictTable": query_dict_table,
        "queryDictField": query_dict_field,
        "queryDictText": query_dict_text,
        "queryDefVal": query_def_val,
        "queryConfigFlag": str(query_config_flag),
        "mainTable": main_table,
        "mainField": main_field,
        "fieldHref": field_href,
        "fieldValidType": field_valid_type,
        "fieldMustInput": str(must_input),
        "dictTable": dict_table,
        "dictField": dict_field,
        "dictText": dict_text,
        "isShowForm": str(is_show_form),
        "isShowList": str(is_show_list),
        "sortFlag": str(sort_flag),
        "isReadOnly": str(is_read_only),
        "fieldShowType": show_type,
        "fieldLength": field_length,
        "isQuery": str(is_query),
        "queryMode": query_mode,
        "fieldDefaultValue": field_default_value,
        "converter": converter,
        "fieldExtendJson": field_extend_json,
        "dbLength": db_length,
        "dbPointLength": db_point,
        "dbType": db_type,
        "dbIsKey": "0",
        "dbIsNull": "1",
        "orderNum": order,
    }
    # link_table_field 等不持久化字段需设置 dbIsPersist='0'
    if str(db_is_persist) == '0':
        field["dbIsPersist"] = "0"
    return field


def make_ext_config():
    """生成默认扩展配置JSON字符串"""
    return json.dumps({
        "reportPrintShow": 0, "reportPrintUrl": "",
        "joinQuery": 0, "modelFullscreen": 0, "modalMinWidth": "",
        "commentStatus": 0, "tableFixedAction": 1,
        "tableFixedActionType": "right",
        "formLabelLengthShow": 0, "formLabelLength": None,
        "enableExternalLink": 0, "externalLinkActions": "add,edit,detail"
    }, ensure_ascii=False)


def build_fields_from_config(field_configs):
    """从配置列表构建字段数组（含系统字段）"""
    fields = make_system_fields()
    for i, fc in enumerate(field_configs):
        fields.append(_make_field_from_config(fc, 6 + i))
    return fields


def build_head(table_config):
    """从表配置构建 head 对象"""
    head = {
        "tableVersion": "1",
        "tableName": table_config['tableName'],
        "tableTxt": table_config['tableTxt'],
        "tableType": table_config.get('tableType', 1),
        "formCategory": table_config.get('formCategory', 'temp'),
        "idType": table_config.get('idType', 'UUID'),
        "isCheckbox": table_config.get('isCheckbox', 'Y'),
        "themeTemplate": table_config.get('themeTemplate', 'normal'),
        "formTemplate": table_config.get('formTemplate', '1'),
        "scroll": table_config.get('scroll', 1),
        "isPage": table_config.get('isPage', 'Y'),
        "isTree": table_config.get('isTree', 'N'),
        "extConfigJson": table_config.get('extConfigJson', make_ext_config()),
        "isDesForm": "N",
        "desFormCode": ""
    }
    # 主表额外字段
    if table_config.get('tableType') == 2:
        head['subTableStr'] = table_config.get('subTableStr', '')
    # 子表额外字段
    if table_config.get('tableType') == 3:
        head['relationType'] = table_config.get('relationType', 0)
        head['tabOrderNum'] = table_config.get('tabOrderNum', 1)
        head['mainTable'] = table_config.get('mainTable', '')
        head['mainField'] = table_config.get('mainField', '')
    # 树表额外字段
    if table_config.get('isTree') == 'Y':
        head['treeParentIdField'] = table_config.get('treeParentIdField', 'pid')
        head['treeIdField'] = table_config.get('treeIdField', 'has_child')
        head['treeFieldname'] = table_config.get('treeFieldname', 'name')
    return head


def build_indexs(index_configs):
    """从索引配置列表构建索引数组"""
    indexs = []
    for ic in (index_configs or []):
        indexs.append({
            "id": rand_id("idx"),
            "indexName": ic['indexName'],
            "indexField": ic['indexField'],
            "indexType": ic.get('indexType', 'normal')
        })
    return indexs


def create_table(api_base, token, table_config):
    """创建单个表并返回 headId"""
    table_name = table_config['tableName']
    table_txt = table_config['tableTxt']
    print(f'\n{"=" * 50}')
    print(f'创建表: {table_name} ({table_txt})')
    print(f'{"=" * 50}')

    fields = build_fields_from_config(table_config.get('fields', []))

    # 子表自动注入外键字段（tableType=3 且配置了 mainTable）
    # 规则：子表必须有一个隐藏的外键字段指向主表，否则主子表关联完全失效。
    # 字段名默认为 {mainTable}_id，若用户已在 fields 中手动配置了带 mainTable 的字段则跳过。
    if table_config.get('tableType') == 3:
        main_table = table_config.get('mainTable', '')
        main_field = table_config.get('mainField', 'id')
        if main_table:
            # 检查用户是否已手动配置外键字段
            has_fk = any(
                f.get('mainTable') == main_table
                for f in table_config.get('fields', [])
            )
            if not has_fk:
                fk_field_name = f'{main_table}_id'
                fk_field = make_field(
                    order=1,
                    db_name=fk_field_name,
                    db_txt='主表ID',
                    show_type='text',
                    db_type='string',
                    db_length=36,
                    is_show_form='0',
                    is_show_list='0',
                    main_table=main_table,
                    main_field=main_field,
                )
                fields.insert(0, fk_field)
                print(f'  [自动] 注入外键字段 {fk_field_name}（主表={main_table}, 主字段={main_field}）')

    # 自动添加 bpm_status 字段（如果配置了 bpmForm: true）
    if table_config.get('bpmForm', False):
        bpm_status_field = {
            "dbFieldName": "bpm_status",
            "dbFieldTxt": "流程状态",
            "fieldShowType": "list",
            "dbType": "string",
            "dbLength": 32,
            "fieldMustInput": "0",
            "isQuery": "0",
            "isShowForm": "0",
            "isShowList": "1",
            "dictField": "bpm_status"
        }
        fields.append(bpm_status_field)
        print(f'  [自动] 添加 bpm_status 字段（流程状态）')
    head = build_head(table_config)
    indexs = build_indexs(table_config.get('indexs'))

    form_data = {
        "head": head,
        "fields": fields,
        "indexs": indexs,
        "deleteFieldIds": [],
        "deleteIndexIds": []
    }

    result = api_request(api_base, token, '/online/cgform/api/addAll', form_data)
    print(f'创建结果: success={result.get("success")}, message={result.get("message")}')

    if not result.get('success'):
        print(f'创建失败: {result.get("message")}')
        return None

    # 查询 headId
    list_result = api_request(api_base, token,
                              f'/online/cgform/head/list?tableName={table_name}&pageNo=1&pageSize=1',
                              method='GET')
    if list_result.get('success') and list_result['result']['records']:
        head_id = list_result['result']['records'][0]['id']
        print(f'headId: {head_id}')

        # 同步数据库
        sync = api_request(api_base, token,
                           f'/online/cgform/api/doDbSynch/{head_id}/normal',
                           method='POST')
        print(f'同步数据库: success={sync.get("success")}, message={sync.get("message")}')
        return head_id
    else:
        print('查询 headId 失败，请手动同步数据库')
        return None


def _make_field_from_config(fc, order):
    """从字段配置 dict 构建完整字段，统一入口减少重复代码"""
    return make_field(
        order=order,
        db_name=fc['dbFieldName'],
        db_txt=fc['dbFieldTxt'],
        show_type=fc.get('fieldShowType', 'text'),
        db_type=fc.get('dbType', 'string'),
        db_length=fc.get('dbLength', 100),
        db_point=fc.get('dbPointLength', 0),
        must_input=fc.get('fieldMustInput', '0'),
        is_query=fc.get('isQuery', 0),
        query_mode=fc.get('queryMode', 'single'),
        is_show_form=fc.get('isShowForm', 1),
        is_show_list=fc.get('isShowList', 1),
        is_read_only=fc.get('isReadOnly', 0),
        sort_flag=fc.get('sortFlag', '0'),
        dict_field=fc.get('dictField', ''),
        dict_table=fc.get('dictTable', ''),
        dict_text=fc.get('dictText', ''),
        field_valid_type=fc.get('fieldValidType', ''),
        field_default_value=fc.get('fieldDefaultValue', ''),
        field_extend_json=fc.get('fieldExtendJson', ''),
        field_length=fc.get('fieldLength', 120),
        main_table=fc.get('mainTable', ''),
        main_field=fc.get('mainField', ''),
        query_config_flag=fc.get('queryConfigFlag', '0'),
        query_show_type=fc.get('queryShowType', None),
        query_dict_field=fc.get('queryDictField', ''),
        query_dict_table=fc.get('queryDictTable', ''),
        query_dict_text=fc.get('queryDictText', ''),
        query_def_val=fc.get('queryDefVal', ''),
        db_is_persist=fc.get('dbIsPersist', 1),
        field_href=fc.get('fieldHref', ''),
        converter=fc.get('converter', ''),
    )


def reorder_fields(api_base, token, reorder_config):
    """
    移动字段顺序。支持两种模式：

    模式1 - move（移动指定字段到目标字段之后）：
    {"action": "reorder", "tableName": "xxx", "move": [
        {"field": "father_name", "after": "real_name"},
        {"field": "mother_name", "after": "father_name"}
    ]}

    模式2 - order（指定完整字段顺序，只需列业务字段名）：
    {"action": "reorder", "tableName": "xxx", "order": [
        "real_name", "father_name", "mother_name", "gender", ...
    ]}
    """
    head_id, head_record = resolve_head_id(api_base, token, reorder_config)
    print(f'\n{"=" * 50}')
    print(f'字段排序: headId={head_id}')
    print(f'{"=" * 50}')

    head, fields, indexs = get_head_and_fields(api_base, token, head_id, head_record)
    if not fields:
        print('错误: 无法获取现有字段列表')
        return None

    fields.sort(key=lambda x: x['orderNum'])
    sys_fields = [f for f in fields if f['dbFieldName'] in ('id', 'create_by', 'create_time', 'update_by', 'update_time', 'sys_org_code')]
    biz_fields = [f for f in fields if f['dbFieldName'] not in ('id', 'create_by', 'create_time', 'update_by', 'update_time', 'sys_org_code')]

    if 'move' in reorder_config:
        # 模式1: move
        # after 支持特殊值: "FIRST"=排到第一位, "LAST"=排到末尾
        for m in reorder_config['move']:
            target = m['field']
            after = m.get('after', 'LAST')
            # 找到要移动的字段
            moving = None
            for i, f in enumerate(biz_fields):
                if f['dbFieldName'] == target:
                    moving = biz_fields.pop(i)
                    break
            if not moving:
                print(f'  字段 {target} 不存在，跳过')
                continue
            if after == 'FIRST':
                biz_fields.insert(0, moving)
                print(f'  移动 {target} → 第一位')
            elif after == 'LAST':
                biz_fields.append(moving)
                print(f'  移动 {target} → 末尾')
            else:
                insert_idx = len(biz_fields)
                for i, f in enumerate(biz_fields):
                    if f['dbFieldName'] == after:
                        insert_idx = i + 1
                        break
                biz_fields.insert(insert_idx, moving)
                print(f'  移动 {target} → {after} 之后')

    elif 'order' in reorder_config:
        # 模式2: order（完整顺序）
        order_list = reorder_config['order']
        field_map = {f['dbFieldName']: f for f in biz_fields}
        new_biz = []
        for name in order_list:
            if name in field_map:
                new_biz.append(field_map.pop(name))
        # 未指定的字段追加到末尾
        for f in biz_fields:
            if f['dbFieldName'] in field_map:
                new_biz.append(f)
        biz_fields = new_biz
        print(f'  按指定顺序排列 {len(order_list)} 个字段')

    # 重新编号
    all_fields = sys_fields + biz_fields
    for i, f in enumerate(all_fields):
        f['orderNum'] = i

    # 保存
    edit_data = {'head': head, 'fields': all_fields, 'deleteFieldIds': []}
    if indexs:
        edit_data['indexs'] = indexs
    result = api_request(api_base, token, '/online/cgform/api/editAll', edit_data, method='PUT')
    if result.get('success'):
        print('排序保存成功!')
        # 同步
        api_request(api_base, token, f'/online/cgform/api/doDbSynch/{head_id}/normal', method='POST')
        print('同步数据库成功!')
    else:
        # fallback: 用 modifyFields 方式
        print(f'editAll 失败({result.get("message")}), 使用 fallback 方式...')
        modify_config = {
            'tableName': reorder_config.get('tableName', ''),
            'headId': head_id,
            'modifyFields': [{'dbFieldName': f['dbFieldName'], 'orderNum': f['orderNum']} for f in biz_fields]
        }
        edit_table(api_base, token, modify_config)

    # 展示结果
    print('\n当前字段顺序:')
    for f in all_fields:
        if f['dbFieldName'] not in ('id', 'create_by', 'create_time', 'update_by', 'update_time', 'sys_org_code'):
            print(f'  {f["orderNum"]:3d}  {f["dbFieldName"]:20s}  {f.get("dbFieldTxt", "")}')

    return head_id


def edit_table(api_base, token, edit_config):
    """编辑现有表单（优化版：tableName 自动解析 + getByHead fallback 链 + 并行查询）"""

    # Step 1: 解析 headId + head_record（支持 tableName 或 headId）
    head_id, head_record = resolve_head_id(api_base, token, edit_config)
    print(f'\n{"=" * 50}')
    print(f'编辑表单: headId={head_id}')
    print(f'{"=" * 50}')

    # Step 2: 查询完整配置（getByHead → fallback 链，复用 head_record 减少请求）
    head, fields, indexs = get_head_and_fields(api_base, token, head_id, head_record)
    if not fields:
        print('错误: 无法获取现有字段列表')
        return None

    # 删除字段：从 fields 中移除 + 记录 id 到 deleteFieldIds
    has_changes = False
    delete_field_ids = []
    for field_name in edit_config.get('deleteFields', []):
        found = False
        for f in fields:
            if f['dbFieldName'] == field_name:
                fields.remove(f)
                if f.get('id'):
                    delete_field_ids.append(f['id'])
                print(f'  删除字段: {field_name}')
                found = True
                has_changes = True
                break
        if not found:
            print(f'  字段 {field_name} 不存在，已跳过（可能已删除）')

    # 添加新字段
    for fc in edit_config.get('addFields', []):
        new_order = max(f['orderNum'] for f in fields) + 1
        fields.append(_make_field_from_config(fc, new_order))
        print(f'  新增字段: {fc["dbFieldName"]} ({fc["dbFieldTxt"]})')
        has_changes = True

    # 修改字段
    for mc in edit_config.get('modifyFields', []):
        target_name = mc['dbFieldName']
        for f in fields:
            if f['dbFieldName'] == target_name:
                for key, val in mc.items():
                    if key != 'dbFieldName':
                        f[key] = val
                print(f'  修改字段: {target_name}')
                has_changes = True
                break

    if not has_changes:
        print('无需修改')
        return head_id

    edit_data = {
        "head": head,
        "fields": fields,
        "indexs": indexs,
        "deleteFieldIds": delete_field_ids,
        "deleteIndexIds": []
    }

    result = api_request(api_base, token, '/online/cgform/api/editAll', edit_data, method='PUT')
    print(f'编辑结果: success={result.get("success")}, message={result.get("message")}')

    if result.get('success'):
        sync = api_request(api_base, token,
                           f'/online/cgform/api/doDbSynch/{head_id}/normal', method='POST')
        print(f'同步数据库: success={sync.get("success")}, message={sync.get("message")}')
    return head_id


def print_menu_sql(head_id, table_txt):
    """输出菜单SQL"""
    menu_id = head_id.replace('-', '')[:32]
    print(f"""
--- 菜单 SQL（可选）---

INSERT INTO sys_permission(id, parent_id, name, url, component, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_route, is_leaf, keep_alive, hidden, hide_tab, description, status, del_flag, rule_flag, create_by, create_time, update_by, update_time, internal_or_external)
VALUES ('{menu_id}', NULL, '{table_txt}', '/online/cgformList/{head_id}', '1', 'OnlineAutoList', NULL, 0, NULL, '1', 0.00, 0, NULL, 0, 1, 0, 0, 0, NULL, '1', 0, 0, 'admin', now(), NULL, NULL, 0);
""")


def main():
    parser = argparse.ArgumentParser(description='JeecgBoot Online 表单创建/编辑工具')
    parser.add_argument('--api-base', required=True, help='JeecgBoot 后端地址')
    parser.add_argument('--token', required=True, help='X-Access-Token')
    parser.add_argument('--config', required=True, help='配置文件路径 (JSON)')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config = json.load(f)

    action = config.get('action', 'create')

    if action == 'create':
        # 创建表单（支持单表、主子表、树表）
        tables = config.get('tables', [])
        if not tables:
            print('错误: 配置文件中没有 tables 定义')
            sys.exit(1)

        head_ids = {}
        for table_config in tables:
            head_id = create_table(args.api_base, args.token, table_config)
            if head_id:
                head_ids[table_config['tableName']] = head_id

        # 输出汇总
        print(f'\n{"=" * 50}')
        print('创建完成汇总')
        print(f'{"=" * 50}')
        for tname, hid in head_ids.items():
            print(f'  {tname} -> headId: {hid}')

        # 为主表输出菜单SQL
        main_table = tables[0]
        main_head_id = head_ids.get(main_table['tableName'])
        if main_head_id:
            print_menu_sql(main_head_id, main_table['tableTxt'])

    elif action == 'edit':
        head_id = edit_table(args.api_base, args.token, config)
        if head_id:
            print(f'\n编辑完成! headId={head_id}')

    elif action == 'reorder':
        reorder_fields(args.api_base, args.token, config)

    else:
        print(f'未知操作类型: {action}')
        sys.exit(1)


if __name__ == '__main__':
    main()
