"""
JeecgBoot 系统主数据批量操作脚本

通过 JSON 配置文件批量查询、创建角色/字典/用户/部门等主数据。
遵循"先查后建"原则：优先使用系统已有数据，没有才创建。

用法:
  python system_creator.py --api-base <URL> --token <TOKEN> --config <config.json>
  python system_creator.py --api-base <URL> --token <TOKEN> --action query-roles
  python system_creator.py --api-base <URL> --token <TOKEN> --action query-dicts
  python system_creator.py --api-base <URL> --token <TOKEN> --action query-users --keyword 张
  python system_creator.py --api-base <URL> --token <TOKEN> --action query-depts --keyword 研发
  python system_creator.py --api-base <URL> --token <TOKEN> --action query-dict --code sex
  python system_creator.py --api-base <URL> --token <TOKEN> --action query-positions

config.json 示例:
{
  "roles": [
    {"roleName": "部门经理", "roleCode": "dept_manager"},
    {"roleName": "HR专员", "roleCode": "hr"}
  ],
  "dicts": [
    {
      "dictCode": "leave_type",
      "dictName": "请假类型",
      "items": [
        {"value": "1", "text": "事假"},
        {"value": "2", "text": "病假"},
        {"value": "3", "text": "年假"}
      ]
    }
  ]
}
"""

import sys
import os
import json
import argparse

# 修复 Windows 控制台中文乱码
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except:
    pass

# 导入 system_utils（同目录）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from system_utils import *


# ====== 配置文件处理 ======

def process_config(config):
    """处理 JSON 配置，批量查找或创建主数据"""
    results = {
        'roles': {},
        'dicts': {},
        'users': {},
        'depts': {},
        'positions': {},
    }

    # 处理角色
    for role_cfg in config.get('roles', []):
        name = role_cfg.get('roleName', '')
        code = role_cfg.get('roleCode', '')
        desc = role_cfg.get('description', '')
        if name or code:
            found_code = find_or_create_role(name, code)
            if found_code:
                results['roles'][name or code] = found_code

    # 处理字典（批量创建）
    dict_list = []
    for dict_cfg in config.get('dicts', []):
        code = dict_cfg.get('dictCode', '')
        name = dict_cfg.get('dictName', '')
        items = dict_cfg.get('items', [])
        if code:
            dict_list.append({'dictCode': code, 'dictName': name, 'items': items})

    if dict_list:
        batch_result = create_dicts_batch(dict_list)
        for code in batch_result.get('success', []):
            results['dicts'][code] = code

    # 查询用户（只查不建）
    for user_cfg in config.get('users', []):
        keyword = user_cfg.get('keyword', '') or user_cfg.get('username', '')
        if keyword:
            user = find_user(keyword)
            if user:
                results['users'][keyword] = {
                    'username': user.get('username', ''),
                    'realname': user.get('realname', ''),
                    'id': user.get('id', ''),
                }
                print(f'[用户] 找到: {user.get("realname")} ({user.get("username")})')
            else:
                print(f'[用户] 未找到: {keyword}')

    # 查询部门（只查不建）
    for dept_cfg in config.get('depts', []):
        keyword = dept_cfg.get('keyword', '') or dept_cfg.get('departName', '')
        if keyword:
            dept = find_dept(keyword)
            if dept:
                results['depts'][keyword] = {
                    'id': dept.get('id', ''),
                    'departName': dept.get('departName', ''),
                    'orgCode': dept.get('orgCode', ''),
                    'orgCategory': dept.get('orgCategory', ''),
                }
                cat_label = {'1': '公司', '2': '部门', '3': '岗位', '4': '子公司'}.get(
                    str(dept.get('orgCategory', '')), '')
                print(f'[部门] 找到: {dept.get("departName")} ({cat_label})')
            else:
                print(f'[部门] 未找到: {keyword}')

    # 查询职务（只查不建）
    for pos_cfg in config.get('positions', []):
        keyword = pos_cfg.get('keyword', '') or pos_cfg.get('name', '') or pos_cfg.get('code', '')
        if keyword:
            # 用 _request 直接查
            result = _request(f'/sys/position/list?pageNo=1&pageSize=100&name={urllib.parse.quote(keyword)}')
            if result.get('success') and result.get('result'):
                records = result['result'].get('records', [])
                if records:
                    pos = records[0]
                    results['positions'][keyword] = {
                        'id': pos.get('id', ''),
                        'name': pos.get('name', ''),
                        'code': pos.get('code', ''),
                        'postLevel': pos.get('postLevel', ''),
                    }
                    level_label = {'1': '高管', '2': '中层', '3': '基层', '4': '实习'}.get(
                        str(pos.get('postLevel', '')), '')
                    print(f'[职务] 找到: {pos.get("name")} ({pos.get("code")}) 级别={level_label}')
                else:
                    print(f'[职务] 未找到: {keyword}')

    return results


# ====== 单项查询命令 ======

def action_query_roles(keyword=None):
    """查询并打印角色列表"""
    roles = query_roles(keyword)
    print(f'\n--- 角色列表 ({len(roles)} 条) ---')
    print(f'{"角色编码":20s} | {"角色名称":20s} | ID')
    print('-' * 70)
    for r in roles:
        print(f'{r.get("roleCode", ""):20s} | {r.get("roleName", ""):20s} | {r.get("id", "")[:16]}...')
    return roles


def action_query_users(keyword=None):
    """查询并打印用户列表"""
    users = query_users(keyword)
    print(f'\n--- 用户列表 ({len(users)} 条) ---')
    print(f'{"用户名":20s} | {"姓名":12s} | {"手机":15s} | {"状态":4s} | {"部门编码"}')
    print('-' * 90)
    for u in users:
        status = '正常' if str(u.get('status', '')) == '1' else '冻结'
        print(f'{u.get("username", ""):20s} | {u.get("realname", ""):12s} | {u.get("phone", "") or "":15s} | {status:4s} | {u.get("orgCode", "")}')
    return users


def action_query_depts(keyword=None):
    """查询并打印部门树"""
    depts = query_depts(keyword)
    count = _count_dept_tree(depts)
    print(f'\n--- 部门树 ({count} 个节点) ---')

    def _print(nodes, indent=0):
        for d in nodes:
            name = d.get('departName', '')
            did = d.get('id', '')[:12]
            code = d.get('orgCode', '')
            cat = d.get('orgCategory', '')
            cat_label = {'1': '公司', '2': '部门', '3': '岗位', '4': '子公司'}.get(str(cat), '')
            print(f'  {"  " * indent}{name} [{cat_label}] orgCode={code} id={did}...')
            children = d.get('children', [])
            if children:
                _print(children, indent + 1)

    _print(depts)
    return depts


def _count_dept_tree(nodes):
    """递归统计部门树节点数"""
    count = len(nodes)
    for d in nodes:
        children = d.get('children', [])
        if children:
            count += _count_dept_tree(children)
    return count


def action_query_dicts(keyword=None):
    """搜索并打印字典列表"""
    dicts = search_dict(keyword) if keyword else search_dict('')
    print(f'\n--- 字典列表 ({len(dicts)} 条) ---')
    print(f'{"字典编码":30s} | {"字典名称":20s} | ID')
    print('-' * 80)
    for d in dicts:
        print(f'{d.get("dictCode", ""):30s} | {d.get("dictName", ""):20s} | {d.get("id", "")[:16]}...')
    return dicts


def action_query_dict(dict_code):
    """查询并打印字典项"""
    items = query_dict(dict_code)
    print(f'\n--- 字典 {dict_code} ({len(items)} 项) ---')
    print(f'{"值":10s} | {"文本":20s} | 颜色')
    print('-' * 50)
    for item in items:
        print(f'{item.get("value", ""):10s} | {item.get("text", ""):20s} | {item.get("color", "")}')
    return items


def action_query_positions(keyword=None):
    """查询并打印职务列表"""
    import urllib.parse
    params = 'pageNo=1&pageSize=100'
    if keyword:
        params += f'&name={urllib.parse.quote(keyword)}'
    result = _request(f'/sys/position/list?{params}')
    positions = []
    if result.get('success') and result.get('result'):
        positions = result['result'].get('records', [])
    print(f'\n--- 职务列表 ({len(positions)} 条) ---')
    print(f'{"编码":15s} | {"名称":15s} | {"职级":6s} | ID')
    print('-' * 60)
    for p in positions:
        level = {'1': '高管', '2': '中层', '3': '基层', '4': '实习'}.get(
            str(p.get('postLevel', '')), str(p.get('postLevel', '')))
        print(f'{p.get("code", ""):15s} | {p.get("name", ""):15s} | {level:6s} | {p.get("id", "")[:16]}...')
    return positions


def action_query_dept_positions(dept_id=None):
    """查询并打印部门+岗位树"""
    tree = query_dept_positions(dept_id)
    print(f'\n--- 部门+岗位树 ({len(tree)} 个根节点) ---')

    def _print(nodes, indent=0):
        for d in nodes:
            title = d.get('title', d.get('departName', ''))
            key = d.get('key', d.get('id', ''))[:16]
            print(f'  {"  " * indent}{title}  key={key}...')
            children = d.get('children', [])
            if children:
                _print(children, indent + 1)

    _print(tree)
    return tree


def action_query_approval_roles(keyword=None):
    """查询审批角色"""
    result = _request('/sys/approvalRole/loadTreeRoot')
    if result.get('success'):
        nodes = result.get('result', [])
        print(f'\n--- 审批角色 ({len(nodes)} 个根节点) ---')

        def _print(items, indent=0):
            for n in items:
                title = n.get('title', n.get('roleName', ''))
                key = n.get('key', n.get('id', ''))
                is_leaf = n.get('isLeaf', False)
                node_type = '角色' if is_leaf else '分组'
                print(f'  {"  " * indent}[{node_type}] {title}  id={str(key)[:16]}...')
                children = n.get('children', [])
                if children:
                    _print(children, indent + 1)

        _print(nodes)
        return nodes
    else:
        print(f'查询失败: {result.get("message", "")}')
        return []


def action_query_tenants(keyword=None):
    """查询租户列表"""
    import urllib.parse
    params = 'pageNo=1&pageSize=100'
    if keyword:
        params += f'&name={urllib.parse.quote(keyword)}'
    result = _request(f'/sys/tenant/list?{params}')
    tenants = []
    if result.get('success') and result.get('result'):
        tenants = result['result'].get('records', [])
    print(f'\n--- 租户列表 ({len(tenants)} 条) ---')
    print(f'{"ID":8s} | {"名称":20s} | {"状态":4s} | 有效期')
    print('-' * 70)
    for t in tenants:
        status = '正常' if str(t.get('status', '')) == '1' else '禁用'
        begin = str(t.get('beginDate', ''))[:10]
        end = str(t.get('endDate', ''))[:10]
        print(f'{str(t.get("id", ""))[:8]:8s} | {t.get("name", ""):20s} | {status:4s} | {begin} ~ {end}')
    return tenants


def action_query_datasources():
    """查询数据源列表"""
    result = _request('/sys/dataSource/list?pageNo=1&pageSize=100')
    sources = []
    if result.get('success') and result.get('result'):
        sources = result['result'].get('records', [])
    print(f'\n--- 数据源列表 ({len(sources)} 条) ---')
    print(f'{"编码":15s} | {"名称":20s} | {"类型":10s} | URL')
    print('-' * 80)
    for s in sources:
        db_url = s.get('dbUrl', '')
        if len(db_url) > 40:
            db_url = db_url[:40] + '...'
        print(f'{s.get("code", ""):15s} | {s.get("name", ""):20s} | {s.get("dbType", ""):10s} | {db_url}')
    return sources


def action_query_quartz_jobs(keyword=None):
    """查询定时任务列表"""
    import urllib.parse
    params = 'pageNo=1&pageSize=100'
    if keyword:
        params += f'&jobClassName={urllib.parse.quote(keyword)}'
    result = _request(f'/sys/quartzJob/list?{params}')
    jobs = []
    if result.get('success') and result.get('result'):
        jobs = result['result'].get('records', [])
    print(f'\n--- 定时任务 ({len(jobs)} 条) ---')
    print(f'{"状态":4s} | {"类名":40s} | {"Cron表达式":20s} | 描述')
    print('-' * 100)
    for j in jobs:
        status = {'-1': '删除', '0': '停用', '1': '运行'}.get(str(j.get('status', '')), '未知')
        cls_name = j.get('jobClassName', '')
        if len(cls_name) > 40:
            cls_name = '...' + cls_name[-37:]
        print(f'{status:4s} | {cls_name:40s} | {j.get("cronExpression", ""):20s} | {j.get("description", "")}')
    return jobs


def action_query_categories(code=None, keyword=None):
    """查询分类字典"""
    if code:
        result = _request(f'/sys/category/loadAllData?code={urllib.parse.quote(code)}')
        if result.get('success'):
            data = result.get('result', [])
            print(f'\n--- 分类字典 {code} ({len(data)} 条) ---')
            for item in data:
                print(f'  {item.get("title", item.get("name", ""))} (id={str(item.get("id", ""))[:12]}... pid={item.get("pid", "")})')
            return data
    else:
        result = _request('/sys/category/loadTreeRoot?async=false')
        if result.get('success'):
            nodes = result.get('result', [])
            print(f'\n--- 分类字典根节点 ({len(nodes)} 条) ---')
            for n in nodes:
                print(f'  {n.get("title", "")} (code={n.get("code", "")}, id={str(n.get("id", ""))[:12]}...)')
            return nodes
    return []


# ====== 主入口 ======

def main():
    parser = argparse.ArgumentParser(description='JeecgBoot 系统主数据查询/创建工具')
    parser.add_argument('--api-base', required=True, help='JeecgBoot 后端地址')
    parser.add_argument('--token', required=True, help='X-Access-Token')
    parser.add_argument('--config', help='配置文件路径 (JSON)，用于批量创建')
    parser.add_argument('--action', help='查询动作: query-roles/query-users/query-depts/query-dicts/query-dict/query-positions/query-dept-positions/query-approval-roles/query-tenants/query-datasources/query-quartz-jobs/query-categories')
    parser.add_argument('--keyword', help='查询关键词')
    parser.add_argument('--code', help='字典编码/分类编码（query-dict/query-categories 时使用）')
    parser.add_argument('--dept-id', help='部门ID（query-dept-positions 时使用）')
    parser.add_argument('--output', help='输出结果到 JSON 文件')
    args = parser.parse_args()

    init_api(args.api_base, args.token)

    result = None

    if args.config:
        # 配置文件模式：批量查找/创建
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        result = process_config(config)

        # 输出汇总
        print(f'\n{"=" * 50}')
        print('执行完成汇总')
        print(f'{"=" * 50}')
        if result['roles']:
            print(f'\n角色 ({len(result["roles"])} 个):')
            for name, code in result['roles'].items():
                print(f'  {name} -> {code}')
        if result['dicts']:
            print(f'\n字典 ({len(result["dicts"])} 个):')
            for code, found_code in result['dicts'].items():
                print(f'  {code} -> {found_code}')
        if result['users']:
            print(f'\n用户 ({len(result["users"])} 个):')
            for kw, info in result['users'].items():
                print(f'  {kw} -> {info["username"]} ({info["realname"]})')
        if result['depts']:
            print(f'\n部门 ({len(result["depts"])} 个):')
            for kw, info in result['depts'].items():
                print(f'  {kw} -> {info["departName"]} (id={info["id"][:12]}...)')
        if result['positions']:
            print(f'\n职务 ({len(result["positions"])} 个):')
            for kw, info in result['positions'].items():
                print(f'  {kw} -> {info["name"]} ({info["code"]})')

    elif args.action:
        # 单项查询模式
        action_map = {
            'query-roles': lambda: action_query_roles(args.keyword),
            'query-users': lambda: action_query_users(args.keyword),
            'query-depts': lambda: action_query_depts(args.keyword),
            'query-dicts': lambda: action_query_dicts(args.keyword),
            'query-dict': lambda: action_query_dict(args.code or args.keyword or ''),
            'query-positions': lambda: action_query_positions(args.keyword),
            'query-dept-positions': lambda: action_query_dept_positions(args.dept_id),
            'query-approval-roles': lambda: action_query_approval_roles(args.keyword),
            'query-tenants': lambda: action_query_tenants(args.keyword),
            'query-datasources': lambda: action_query_datasources(),
            'query-quartz-jobs': lambda: action_query_quartz_jobs(args.keyword),
            'query-categories': lambda: action_query_categories(args.code, args.keyword),
        }
        fn = action_map.get(args.action)
        if fn:
            result = fn()
        else:
            print(f'未知 action: {args.action}')
            print(f'支持: {", ".join(action_map.keys())}')
            sys.exit(1)
    else:
        print('请指定 --config 或 --action 参数')
        parser.print_help()
        sys.exit(1)

    # 输出到 JSON 文件
    if args.output and result is not None:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f'\n结果已保存到: {args.output}')


if __name__ == '__main__':
    import urllib.parse
    main()
