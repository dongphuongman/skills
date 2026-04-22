"""
JeecgBoot OA 应用一键创建脚本
==============================
一次性完成：表单创建 → 流程创建 → 流程发布 → 表单关联 → 角色授权

用法:
  python bpmn_oa.py --api-base <URL> --token <TOKEN> --config <config.json>
  python bpmn_oa.py --api-base <URL> --token <TOKEN> --config <config.json> --force

参数:
  --api-base       JeecgBoot 后端地址（如 http://localhost:8080/jeecgboot）
  --token          X-Access-Token
  --config         JSON 配置文件路径
  --force          强制覆盖已存在的表单
"""

import argparse
import json
import sys
import os
import urllib.request
import urllib.parse
import time

# 修复 Windows 控制台中文乱码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SKILL_DIR = os.path.dirname(_SCRIPT_DIR)
_SKILLS_ROOT = os.path.dirname(_SKILL_DIR)

# 定位 desform 和 bpmn 脚本目录
_DESFORM_SCRIPTS = os.path.join(_SKILLS_ROOT, 'jeecg-desform', 'scripts')
_BPMN_SCRIPTS = os.path.join(_SKILLS_ROOT, 'jeecg-bpmn', 'scripts')

# 将 desform 脚本目录加入 path（需要 desform_utils）
sys.path.insert(0, _DESFORM_SCRIPTS)

# 导入 desform 和 bpmn 模块
import importlib.util


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


desform_creator = _load_module('desform_creator', os.path.join(_DESFORM_SCRIPTS, 'desform_creator.py'))
bpmn_creator = _load_module('bpmn_creator', os.path.join(_BPMN_SCRIPTS, 'bpmn_creator.py'))

# 从 desform_utils 导入核心函数
from desform_utils import init_api, get_form_id, create_form

# ====== 授权相关 ======

DEFAULT_ROLE_ID = 'f6817f48af4fb3af11b9e8bf182f618b'


def auth_api_request(api_base, token, path, data=None, method='GET'):
    """调用授权 API"""
    url = f'{api_base}{path}'
    headers = {
        'X-Access-Token': token,
        'Content-Type': 'application/json; charset=UTF-8',
    }
    if data is not None:
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read().decode('utf-8'))


def get_existing_auth_ids(api_base, token, role_id):
    """查询角色已有的授权表单ID列表"""
    ts = str(int(time.time() * 1000))
    path = f'/joa/designform/designFormCommuse/getAuthorizedDesignList?principalId={role_id}&authMode=role&_t={ts}'
    result = auth_api_request(api_base, token, path, method='GET')
    if result.get('success') and result.get('result'):
        return [item['id'] for item in result['result']]
    return []


def save_auth(api_base, token, role_id, auth_ids, auth_mode='role'):
    """保存授权（追加新表单ID，保留已有授权）"""
    path = f'/joa/designform/designFormCommuse/saveWorkorderAuth/{role_id}'
    data = {
        'authMode': auth_mode,
        'authId': ','.join(auth_ids),
        'subDepartIds': '',
    }
    return auth_api_request(api_base, token, path, data=data, method='POST')


def authorize_form(api_base, token, form_id, role_id=DEFAULT_ROLE_ID, auth_mode='role'):
    """为表单添加角色授权（保留已有授权）"""
    existing_ids = get_existing_auth_ids(api_base, token, role_id)
    if form_id not in existing_ids:
        existing_ids.append(form_id)
    result = save_auth(api_base, token, role_id, existing_ids, auth_mode)
    return result, len(existing_ids) - 1  # 返回结果和原有授权数量


# ====== 主流程 ======

def main():
    parser = argparse.ArgumentParser(description='JeecgBoot OA 应用一键创建工具')
    parser.add_argument('--api-base', required=True, help='JeecgBoot 后端地址')
    parser.add_argument('--token', required=True, help='X-Access-Token')
    parser.add_argument('--config', required=True, help='JSON 配置文件路径')
    parser.add_argument('--force', action='store_true', help='强制覆盖已存在的表单')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config = json.load(f)

    app_name = config.get('appName', config['form']['formName'])
    form_config = config['form']
    process_config = config['process']
    auth_config = config.get('auth', {})
    role_id = auth_config.get('roleId', DEFAULT_ROLE_ID)
    auth_mode = auth_config.get('authMode', 'role')

    print(f'\n{"=" * 50}')
    print(f'开始创建 OA 应用: {app_name}')
    print(f'{"=" * 50}')

    # ========== 第1步：创建表单 ==========
    print(f'\n[1/4] 创建表单...')

    form_name = form_config['formName']
    form_code = form_config['formCode']
    layout = form_config.get('layout', 'auto')
    title_index = form_config.get('titleIndex', 0)

    init_api(args.api_base, args.token)

    # 防覆盖检查
    existing_id, _ = get_form_id(form_code)
    if existing_id and not args.force:
        print(f'  [阻止] 表单 {form_code} 已存在 (ID={existing_id})')
        print(f'  如需覆盖，请加 --force 参数')
        sys.exit(1)

    # 构建控件列表（预处理 oa-approval-comments 类型）
    fields = form_config.get('fields', [])
    widgets = []
    for fd in fields:
        if fd.get('type') == 'oa-approval-comments':
            # 将审批意见组件转换为禁用的 textarea（word 布局自动处理 grid）
            converted = {
                'name': fd['name'],
                'type': 'textarea',
                'required': False,
            }
            widget = desform_creator.build_widget(converted)
            # 设置 disabled=True（由流程节点控制启用）
            if isinstance(widget, tuple):
                w = widget[0]
            else:
                w = widget
            # 深入 card → list → widget 设置 disabled
            if 'list' in w:
                for item in w['list']:
                    if 'options' in item:
                        item['options']['disabled'] = True
            widgets.append(widget)
        else:
            widget = desform_creator.build_widget(fd)
            widgets.append(widget)

    form_id, title_model = create_form(form_name, form_code, widgets,
                                        title_index=title_index, layout=layout)
    print(f'  表单创建成功: ID={form_id}, 编码={form_code}')

    # ========== 第2步：创建流程 ==========
    print(f'\n[2/4] 创建流程...')

    # 自动补全 formLink（关联刚创建的表单）
    process_config['formLink'] = {
        'formType': '2',
        'relationCode': form_code,
        'formTableName': form_code,
        'flowStatusCol': 'bpm_status',
        'titleExp': process_config.get('titleExp', f'{app_name}'),
    }

    process_config = bpmn_creator.expand_config(process_config)
    bpmn_xml = bpmn_creator.build_bpmn_xml(process_config)

    result = bpmn_creator.save_process(args.api_base, args.token, process_config, bpmn_xml)
    if not result.get('success'):
        print(f'  流程创建失败: {result.get("msg", "")}')
        sys.exit(1)

    process_id = result.get('obj', '')
    process_key = process_config['processKey']
    print(f'  流程创建成功: ID={process_id}, Key={process_key}')

    # ========== 第3步：发布流程 + 关联表单 ==========
    print(f'\n[3/4] 发布流程并关联表单...')

    # 发布
    deploy_result = bpmn_creator.deploy_process(args.api_base, args.token, process_id)
    if deploy_result.get('success'):
        print(f'  流程发布成功')
    else:
        print(f'  流程发布失败: {deploy_result.get("message", "")}')

    # 关联表单
    form_link_config = process_config.get('formLink')
    if form_link_config:
        link_result = bpmn_creator.link_form(args.api_base, args.token, process_id, form_link_config)
        if link_result.get('success'):
            print(f'  表单关联成功')
        else:
            print(f'  表单关联失败: {link_result.get("message", "")}')

    # 设置草稿节点表单可编辑 + 表单地址（调用 bpmn_creator 的通用函数）
    # 根据表单类型自动生成表单地址
    form_type = process_config.get('formLink', {}).get('formType', '2')
    if form_type == '2':
        # 设计器表单(desform)：PC和移动端地址一致
        desform_url = '{{DOMAIN_URL}}/desform/edit/' + form_code + '/${BPM_DES_DATA_ID}?token={{TOKEN}}&taskId={{TASKID}}&skip=false'
        form_url_config = {
            'modelAndView': desform_url,
            'modelAndViewMobile': desform_url,
        }
    elif form_type == '1':
        # Online表单
        form_url_config = {
            'modelAndView': 'super/bpm/process/components/OnlineFormOpt',
            'modelAndViewMobile': 'check/onlineForm/flowedit',
        }
    else:
        form_url_config = None

    updated = bpmn_creator.set_draft_nodes_editable(
        args.api_base, args.token, process_id, process_config,
        form_url_config=form_url_config)
    if updated:
        print(f'  节点表单可编辑已设置: {", ".join(updated)}')
        if form_url_config:
            print(f'  表单地址已设置: PC={form_url_config.get("modelAndView", "")}')

    # ========== 第4步：节点字段权限（可选） ==========
    node_permissions = config.get('nodePermissions', {})
    if node_permissions:
        print(f'\n[4/5] 配置节点字段权限...')
        for node_code, field_perms in node_permissions.items():
            perm_result = bpmn_creator.set_node_field_permissions(
                args.api_base, args.token, process_id, node_code, form_code,
                field_perms, form_type='2')
            if perm_result.get('success'):
                print(f'  {node_code}: {perm_result["updated"]} 个字段权限已设置')
                if perm_result.get('errors'):
                    for err in perm_result['errors']:
                        print(f'    [警告] {err}')
            else:
                print(f'  {node_code}: 设置失败 - {perm_result.get("errors", [])}')
        step_label = '5/5'
    else:
        step_label = '4/4'

    # ========== 角色授权 ==========
    print(f'\n[{step_label}] 授权给管理员角色...')

    auth_result, existing_count = authorize_form(
        args.api_base, args.token, form_id, role_id, auth_mode
    )
    if auth_result.get('success'):
        print(f'  授权成功（保留原有 {existing_count} 条授权）')
    else:
        print(f'  授权失败: {auth_result.get("message", "")}')

    # ========== 输出汇总 ==========
    print(f'\n{"=" * 50}')
    print(f'OA 应用创建完成')
    print(f'{"=" * 50}')
    print(f'  应用名称: {app_name}')
    print(f'')
    print(f'  [表单] ID: {form_id} | 编码: {form_code} | 布局: {layout}')
    print(f'  [流程] ID: {process_id} | Key: {process_key} | 已发布')
    print(f'  [关联] 表单已关联到流程')
    if node_permissions:
        print(f'  [权限] 已配置 {len(node_permissions)} 个节点的字段权限')
    print(f'  [授权] 已授权给管理员角色（保留原有 {existing_count} 条授权）')
    print(f'{"=" * 50}')


if __name__ == '__main__':
    main()
