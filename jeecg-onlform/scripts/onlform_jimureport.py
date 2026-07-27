from typing import Optional
"""
JeecgBoot Online 表单 - 积木报表集成工具脚本

用法:
  python onlform_jimureport.py --api-base <URL> --token <TOKEN> --config <config.json>

config.json 格式:
  {
    "action": "create_report",
    "headId": "xxx",           // 可选，与 tableName 二选一
    "tableName": "customer",   // 可选，自动解析 headId
    "reportName": "客户表打印",
    "fields": [                // 可选，不提供则自动从 Online 表单查询
      {"fieldName": "customer_name", "fieldText": "客户名称"},
      {"fieldName": "phone", "fieldText": "联系电话"}
    ]
  }

支持的操作:
  - create_report: 创建积木报表并关联到 Online 表单（卡片式打印布局）
  - delete_report: 删除积木报表

验证记录: 2026-03-30 customer_info / shopping_cart 均一次成功
"""

import urllib.request
import json
import sys
import ssl
import time
import hashlib
import argparse

# 修复 Windows 控制台中文乱码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 全局 SSL 上下文（HTTPS 支持）
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE

SIGNATURE_SECRET = 'dd05f1c54d63749eda95f9fa6d49v442a'
SIGNED_ENDPOINTS = [
    '/jmreport/queryFieldBySql', '/jmreport/executeSelectApi',
    '/jmreport/loadTableData', '/jmreport/testConnection',
    '/jmreport/download/image', '/jmreport/dictCodeSearch',
    '/jmreport/getDataSourceByPage', '/jmreport/getDataSourceById',
]


# ====== 工具函数 ======

def compute_sign(params_dict: dict) -> str:
    """计算积木报表接口签名"""
    str_params = {}
    for k, v in params_dict.items():
        if v is None:
            continue
        if isinstance(v, bool):
            str_params[k] = str(v).lower()
        elif isinstance(v, (int, float)):
            str_params[k] = str(v)
        elif isinstance(v, (dict, list)):
            str_params[k] = json.dumps(v, ensure_ascii=False, separators=(',', ':'))
        else:
            str_params[k] = str(v)
    sorted_params = dict(sorted(str_params.items()))
    params_json = json.dumps(sorted_params, ensure_ascii=False, separators=(',', ':'))
    return hashlib.md5((params_json + SIGNATURE_SECRET).encode('utf-8')).hexdigest().upper()


def api_request(api_base: str, token: str, path: str, data: Optional[dict] = None,
                method: str = 'POST') -> dict:
    """发送 API 请求，返回 JSON 响应"""
    url = f'{api_base}{path}'
    if method == 'GET':
        sep = '&' if '?' in url else '?'
        url += f'{sep}_t={int(time.time() * 1000)}'
    headers = {
        'X-Access-Token': token,
        'token': token,
        'Content-Type': 'application/json; charset=UTF-8'
    }
    need_sign = any(path.rstrip('/').endswith(ep.rstrip('/')) for ep in SIGNED_ENDPOINTS)
    if need_sign:
        headers['X-TIMESTAMP'] = str(int(time.time() * 1000))
        headers['X-Sign'] = compute_sign(data if data else {})
    if data is not None:
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    resp = urllib.request.urlopen(req, context=_ssl_ctx)
    return json.loads(resp.read().decode('utf-8'))


def resolve_head_id(api_base: str, token: str, config: dict) -> tuple[str, dict]:
    """从 headId 或 tableName 解析出 (head_id, head_record)"""
    head_id = config.get('headId')
    table_name = config.get('tableName')
    if head_id and not table_name:
        qr = api_request(api_base, token,
                         f'/online/cgform/head/queryById?id={head_id}', method='GET')
        if qr.get('success'):
            return head_id, qr['result']
        result = api_request(api_base, token,
                             f'/online/cgform/head/list?copyType=0&pageNo=1&pageSize=1&id={head_id}',
                             method='GET')
        records = (result.get('result') or {}).get('records', [])
        if records:
            return head_id, records[0]
        print(f'错误: headId {head_id} 不存在')
        sys.exit(1)
    elif table_name:
        result = api_request(api_base, token,
                             f'/online/cgform/head/list?tableName={table_name}&copyType=0&pageNo=1&pageSize=1',
                             method='GET')
        records = (result.get('result') or {}).get('records', [])
        if not records:
            print(f'错误: 表 {table_name} 不存在')
            sys.exit(1)
        rec = records[0]
        return rec['id'], rec
    else:
        print('错误: 必须提供 headId 或 tableName')
        sys.exit(1)


def query_online_fields(api_base: str, token: str, head_id: str) -> list[dict]:
    """查询 Online 表单字段列表，返回 [{fieldName, fieldText}]"""
    system_fields = {'id', 'create_by', 'create_time', 'update_by', 'update_time', 'sys_org_code'}
    try:
        r = api_request(api_base, token,
                        f'/online/cgform/field/listByHeadId?headId={head_id}', method='GET')
        if r.get('success') and r.get('result'):
            fields = []
            for f in r['result']:
                db_name = f.get('dbFieldName', '')
                if db_name in system_fields:
                    continue
                if str(f.get('isShowList', '1')) == '0' and str(f.get('isShowForm', '1')) == '0':
                    continue
                fields.append({'fieldName': db_name, 'fieldText': f.get('dbFieldTxt', db_name)})
            return fields
    except Exception as e:
        print(f'  查询字段列表异常: {e}')

    # fallback: 分页查询
    all_fields: list[dict] = []
    page = 1
    while True:
        r = api_request(api_base, token,
                        f'/online/cgform/field/list?headId={head_id}&pageNo={page}&pageSize=500',
                        method='GET')
        records = (r.get('result') or {}).get('records', [])
        if not records:
            break
        for f in records:
            db_name = f.get('dbFieldName', '')
            if db_name in system_fields:
                continue
            all_fields.append({'fieldName': db_name, 'fieldText': f.get('dbFieldTxt', db_name)})
        total = (r.get('result') or {}).get('total', 0)
        if page * 500 >= total:
            break
        page += 1
    return all_fields


# ====== 报表模板构建 ======

def build_styles() -> list[dict]:
    """构建 7 个样式（与积木报表设计器一致的格式）"""
    border = {"bottom": ["thin", "#d8d8d8"], "top": ["thin", "#d8d8d8"],
              "left": ["thin", "#d8d8d8"], "right": ["thin", "#d8d8d8"]}
    return [
        # 0: 边框
        {"border": border},
        # 1: 边框+居中
        {"border": border, "align": "center"},
        # 2: 边框+居中+垂直居中（数据值）
        {"border": border, "align": "center", "valign": "middle"},
        # 3: 标签样式（灰底+右对齐+加粗）
        {"border": border, "align": "right", "valign": "middle",
         "bgcolor": "#F5F5F5", "font": {"bold": True}},
        # 4: 表头蓝底白字
        {"border": border, "align": "center", "valign": "middle",
         "bgcolor": "#01b0f1", "color": "#ffffff"},
        # 5: 标题样式（淡蓝底深蓝字加粗16号）
        {"border": border, "align": "center", "valign": "middle",
         "font": {"bold": True, "size": 16}, "bgcolor": "#E6F2FF", "color": "#0066CC"},
        # 6: 数据值左对齐
        {"border": border, "align": "left", "valign": "middle"},
    ]


def build_card_layout(report_name: str, db_code: str, fields: list[dict]) -> tuple[dict, list[str]]:
    """
    构建卡片式打印布局（标签-值对，每行2组，4列）。
    返回 (rows, merges)。
    """
    rows: dict = {}
    merges: list[str] = []

    # Row 1: 标题（合并4列）
    rows["1"] = {
        "cells": {"0": {"text": report_name, "style": 5, "merge": [0, 3], "height": 45}},
        "height": 45
    }
    merges.append("A2:D2")

    # 将字段分为：普通字段（每行2个）和长文本字段（独占一行）
    long_types = {'textarea', 'umeditor'}
    normal_fields: list[dict] = []
    long_fields: list[dict] = []
    for f in fields:
        show_type = f.get('fieldShowType', '')
        if show_type in long_types:
            long_fields.append(f)
        else:
            normal_fields.append(f)

    # 普通字段按2个一组排列
    row_idx = 2
    for i in range(0, len(normal_fields), 2):
        cells: dict = {}
        f1 = normal_fields[i]
        cells["0"] = {"text": f1['fieldText'], "style": 3}
        cells["1"] = {"text": f"#{{{db_code}.{f1['fieldName']}}}", "style": 6}
        if i + 1 < len(normal_fields):
            f2 = normal_fields[i + 1]
            cells["2"] = {"text": f2['fieldText'], "style": 3}
            cells["3"] = {"text": f"#{{{db_code}.{f2['fieldName']}}}", "style": 6}
        else:
            cells["2"] = {"text": "", "style": 3}
            cells["3"] = {"text": "", "style": 6}
        rows[str(row_idx)] = {"cells": cells, "height": 32}
        row_idx += 1

    # 长文本字段（值合并3列）
    for f in long_fields:
        rows[str(row_idx)] = {
            "cells": {
                "0": {"text": f['fieldText'], "style": 3},
                "1": {"text": f"#{{{db_code}.{f['fieldName']}}}", "style": 6, "merge": [0, 2]}
            },
            "height": 50
        }
        merges.append(f"B{row_idx + 1}:D{row_idx + 1}")
        row_idx += 1

    rows["len"] = 200
    return rows, merges


# ====== 核心流程 ======

def create_report(api_base: str, token: str, config: dict) -> None:
    """创建积木报表并关联到 Online 表单，6 步流程"""
    table_name = config.get('tableName', '')
    report_name = config.get('reportName', f'{table_name}打印报表')
    fields = config.get('fields')
    db_code = config.get('dataCode', table_name or 'ds')

    # 解析 headId
    print('[准备] 解析 headId ...')
    head_id, head_record = resolve_head_id(api_base, token, config)
    if not table_name:
        table_name = head_record.get('tableName', '')
        if not db_code or db_code == 'ds':
            db_code = table_name
    print(f'  headId: {head_id}')
    print(f'  tableName: {table_name}')

    # 如果未提供 fields，自动查询
    if not fields:
        print('[准备] 未提供 fields，从 Online 表单自动查询 ...')
        fields = query_online_fields(api_base, token, head_id)
        if not fields:
            print('错误: 无法获取字段列表，请在配置中手动提供 fields')
            sys.exit(1)
        print(f'  获取到 {len(fields)} 个字段')

    # ===== Step 1: 创建空报表 =====
    print(f'\n[Step 1/6] 创建空报表 ...')
    create_data = {
        "id": "", "code": "", "name": report_name,
        "type": "984272091947253760", "template": 0
    }
    result = api_request(api_base, token, '/jmreport/save', create_data)
    if not result.get('success'):
        print(f'  创建报表失败: {result.get("message")}')
        sys.exit(1)
    report_id = result.get('result', {}).get('id', '') if isinstance(result.get('result'), dict) else str(result.get('result', ''))
    if not report_id:
        print(f'  创建报表失败: 未返回 reportId')
        sys.exit(1)
    print(f'  success=True, reportId={report_id}')

    # ===== Step 2: 保存 API 数据源 =====
    print(f'\n[Step 2/6] 保存 API 数据源 ...')
    field_list = [{
        "fieldName": f['fieldName'], "fieldText": f['fieldText'],
        "widgetType": "String", "orderNum": i,
        "tableIndex": i + 1, "extJson": "", "dictCode": ""
    } for i, f in enumerate(fields)]

    ds_api_url = "{{ domainURL }}/online/cgform/api/data/" + table_name + "/queryByIdForJmReport?id=${id}&token=${token}&mock=true"
    save_db_data = {
        "izSharedSource": 0, "jimuReportId": report_id,
        "dbCode": db_code, "dbChName": report_name,
        "dbType": "1", "dbSource": "", "jsonData": "",
        "apiConvert": "", "jimuSharedSourceId": None,
        "apiUrl": ds_api_url, "apiMethod": "0",
        "isList": "1", "isPage": "0", "dbDynSql": "",
        "fieldList": field_list,
        "paramList": [
            {"paramName": "id", "orderNum": 1, "tableIndex": 1, "id": "",
             "paramValue": "", "extJson": "", "dictCode": "", "_index": 0, "_rowKey": 30},
            {"paramName": "token", "orderNum": 2, "tableIndex": 2, "id": "",
             "paramValue": "", "extJson": "", "dictCode": "", "_index": 1, "_rowKey": 31}
        ]
    }
    result = api_request(api_base, token, '/jmreport/saveDb', save_db_data)
    if not result.get('success'):
        print(f'  保存数据源失败: {result.get("message")}')
        sys.exit(1)
    print(f'  success=True')

    # ===== Step 3: 构造报表模板 =====
    print(f'\n[Step 3/6] 构造报表模板 ...')
    styles = build_styles()
    rows, merges = build_card_layout(report_name, db_code, fields)
    cols = {"0": {"width": 100}, "1": {"width": 180}, "2": {"width": 100}, "3": {"width": 180}, "len": 100}
    row_count = len([k for k in rows if k != "len"])
    print(f'  {row_count} 行, {len(merges)} 个合并单元格')

    # ===== Step 4: 保存完整报表设计 =====
    print(f'\n[Step 4/6] 保存完整报表设计 ...')
    designer_obj = {
        "id": report_id, "name": report_name,
        "type": "984272091947253760", "template": 0,
        "delFlag": 0, "submitForm": 0, "reportName": report_name
    }
    save_data = {
        "designerObj": json.dumps(designer_obj, ensure_ascii=False),
        "name": "sheet1", "freeze": "A1", "freezeLineColor": "rgb(185, 185, 185)",
        "rows": rows, "cols": cols, "styles": styles, "merges": merges,
        "validations": [], "autofilter": {}, "dbexps": [], "dicts": [],
        "loopBlockList": [], "zonedEditionList": [],
        "fixedPrintHeadRows": [], "fixedPrintTailRows": [],
        "rpbar": {"show": True, "pageSize": "", "btnList": []},
        "fillFormToolbar": {"show": True, "btnList": [
            "save", "subTable_add", "verify", "subTable_del", "print", "close",
            "first", "prev", "next", "paging", "total", "last",
            "exportPDF", "exportExcel", "exportWord"]},
        "hiddenCells": [],
        "hidden": {"rows": [], "cols": [], "conditions": {"rows": {}, "cols": {}}},
        "fillFormInfo": {"layout": {"direction": "horizontal", "width": 200, "height": 45}},
        "recordSubTableOrCollection": {"group": [], "record": [], "range": []},
        "displayConfig": {},
        "printConfig": {"paper": "A4", "width": 210, "height": 297, "definition": 1,
                        "isBackend": False, "marginX": 10, "marginY": 10,
                        "layout": "portrait", "printCallBackUrl": ""},
        "querySetting": {"izOpenQueryBar": False, "izDefaultQuery": True},
        "queryFormSetting": {"useQueryForm": False, "dbKey": "", "idField": ""},
        "area": {"sri": 0, "sci": 0, "eri": 0, "eci": 0, "width": 100, "height": 25},
        "submitHandlers": [], "chartList": [],
        "background": False, "dataRectWidth": 560,
        "excel_config_id": report_id, "pyGroupEngine": False,
        "isViewContentHorizontalCenter": False, "fillFormStyle": "default",
        "sheetId": "default", "sheetName": "默认Sheet", "sheetOrder": "0"
    }
    result = api_request(api_base, token, '/jmreport/save', save_data)
    if not result.get('success'):
        print(f'  保存报表失败: {result.get("message")}')
        sys.exit(1)
    print(f'  success=True')

    # ===== Step 5: 关联报表到 Online 表单 =====
    print(f'\n[Step 5/6] 关联报表到 Online 表单 ...')
    report_print_url = "{{ window._CONFIG['domianURL'] }}/jmreport/view/" + report_id

    # 获取最新 head 数据
    head_r = api_request(api_base, token,
                         f'/online/cgform/head/queryById?id={head_id}', method='GET')
    if head_r.get('success'):
        head_data = head_r['result']
    else:
        head_data = head_record

    existing_ext = head_data.get('extConfigJson', '{}')
    try:
        ext_obj = json.loads(existing_ext) if existing_ext else {}
    except (json.JSONDecodeError, TypeError):
        ext_obj = {}
    ext_obj['reportPrintShow'] = 1
    ext_obj['reportPrintUrl'] = report_print_url
    head_data['extConfigJson'] = json.dumps(ext_obj, ensure_ascii=False)

    result = api_request(api_base, token, '/online/cgform/head/edit', head_data, method='PUT')
    if result.get('success'):
        print(f'  success=True, message={result.get("message", "")}')
    else:
        print(f'  关联失败: {result.get("message")}')
        print(f'  请手动设�� extConfigJson: reportPrintShow=1, reportPrintUrl={report_print_url}')

    # ===== Step 6: 验证 =====
    print(f'\n[Step 6/6] 验证 ...')
    verify = api_request(api_base, token,
                         f'/online/cgform/head/queryById?id={head_id}', method='GET')
    if verify.get('success'):
        v_ext = json.loads(verify['result'].get('extConfigJson', '{}') or '{}')
        print(f'  reportPrintShow={v_ext.get("reportPrintShow")}')
        print(f'  reportPrintUrl={v_ext.get("reportPrintUrl")}')

    # 输出汇总
    print(f'\n{"=" * 50}')
    print(f'全部完成!')
    print(f'{"=" * 50}')
    print(f'  报表名称: {report_name}')
    print(f'  reportId: {report_id}')
    print(f'  数据集编码: {db_code}')
    print(f'  字段数量: {len(fields)}')
    print(f'  headId: {head_id}')
    print(f'  设计器: {api_base}/jmreport/index/{report_id}')
    print(f'  预览: {api_base}/jmreport/view/{report_id}')
    print(f'{"=" * 50}')


def delete_report(api_base: str, token: str, config: dict) -> None:
    """删除积木报表"""
    report_id = config.get('reportId', '')
    if not report_id:
        print('错误: delete_report 操作需要提供 reportId')
        sys.exit(1)

    print(f'[Step 1/2] 删除报表 {report_id} ...')
    try:
        result = api_request(api_base, token,
                             f'/jmreport/delete?id={report_id}', method='DELETE')
        if result.get('success'):
            print(f'  删除成功')
        else:
            print(f'  删除失败: {result.get("message")}')
            return
    except Exception as e:
        print(f'  删除异常: {e}')
        return

    # 如果提供了 headId 或 tableName，清除 extConfigJson 中的关联
    if config.get('headId') or config.get('tableName'):
        print(f'[Step 2/2] 清除 Online 表单关联 ...')
        head_id, head_record = resolve_head_id(api_base, token, config)

        # 获取最新 head 数据
        head_r = api_request(api_base, token,
                             f'/online/cgform/head/queryById?id={head_id}', method='GET')
        head_data = head_r['result'] if head_r.get('success') else head_record

        existing_ext = head_data.get('extConfigJson', '')
        if existing_ext:
            try:
                ext = json.loads(existing_ext) if isinstance(existing_ext, str) else existing_ext
                ext['reportPrintShow'] = 0
                ext['reportPrintUrl'] = ''
                head_data['extConfigJson'] = json.dumps(ext, ensure_ascii=False)
                result = api_request(api_base, token,
                                     '/online/cgform/head/edit', head_data, method='PUT')
                if result.get('success'):
                    print(f'  清除关联��功')
                else:
                    print(f'  清除关联失败: {result.get("message")}')
            except (json.JSONDecodeError, TypeError) as e:
                print(f'  解析 extConfigJson 失败: {e}')
        else:
            print(f'  无 extConfigJson，跳过')
    else:
        print(f'[Step 2/2] 未提供 headId/tableName，跳过清除表单关联')

    print(f'\n报表删除完成!')


def main() -> None:
    parser = argparse.ArgumentParser(description='JeecgBoot Online 表单 - 积木报表集成工具')
    parser.add_argument('--api-base', required=True, help='JeecgBoot 后端地址')
    parser.add_argument('--token', required=True, help='X-Access-Token')
    parser.add_argument('--config', required=True, help='配置文件路径 (JSON)')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config = json.load(f)

    action = config.get('action', 'create_report')

    if action == 'create_report':
        create_report(args.api_base, args.token, config)
    elif action == 'delete_report':
        delete_report(args.api_base, args.token, config)
    else:
        print(f'未知操作类型: {action}')
        sys.exit(1)


if __name__ == '__main__':
    main()
