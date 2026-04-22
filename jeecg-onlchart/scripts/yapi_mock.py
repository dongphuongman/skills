# -*- coding: utf-8 -*-
"""
YApi Mock 接口管理脚本

功能：
  - 登录 YApi 平台获取 Cookie
  - 创建 mock 接口
  - 更新 mock 数据
  - 删除 mock 接口
  - 查询接口列表

固定配置（api.jeecg.com 项目）：
  - project_id: 57
  - catid: 1157（公共分类）
  - basepath: /claude
  - mock 完整 URL：https://api.jeecg.com/mock/57/claude/{path后缀}

用法示例：
    from yapi_mock import init_yapi, create_mock

    init_yapi(email='...', password='...')   # 凭证由 Claude 从 memory 注入，禁止硬编码
    mock_url = create_mock('/staff', '职员信息', [
        {"name": "张三", "salary": 18000},
        {"name": "李四", "salary": 15000},
    ])
    print(mock_url)  # https://api.jeecg.com/mock/57/claude/staff

兼容性说明：
    使用 http.cookiejar.CookieJar + urllib.request.build_opener 管理会话 cookie，
    标准库自动处理所有 Set-Cookie 响应头，兼容 Python 3.6+（含 3.9、3.12 及以上）。
"""

import json
import ssl
import http.cookiejar
import urllib.request

# ── 固定配置 ──────────────────────────────────────────────────
_YAPI_BASE   = 'https://api.jeecg.com'
_PROJECT_ID  = '57'
_CAT_ID      = '1157'
_BASEPATH    = '/claude'
_MOCK_PREFIX = f'{_YAPI_BASE}/mock/{_PROJECT_ID}{_BASEPATH}'

# ── 全局 opener（CookieJar 自动维护登录态，兼容所有 Python 版本）──
_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE

_jar    = http.cookiejar.CookieJar()
_opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(_jar),
    urllib.request.HTTPSHandler(context=_ctx),
)


# ── 核心请求（统一走 _opener，cookie 自动携带）──────────────────
def _request(path, data=None, method=None):
    url  = f'{_YAPI_BASE}{path}'
    body = json.dumps(data, ensure_ascii=False).encode('utf-8') if data is not None else None
    req  = urllib.request.Request(
        url, data=body,
        headers={'Content-Type': 'application/json; charset=UTF-8'},
        method=method or ('POST' if body else 'GET'),
    )
    with _opener.open(req, timeout=15) as resp:
        return json.loads(resp.read().decode('utf-8'))


# ── 登录 ──────────────────────────────────────────────────────
def init_yapi(email=None, password=None):
    """
    登录 YApi，CookieJar 自动保存会话 cookie，后续请求无需手动传 Cookie。

    email/password 无默认值，调用方必须显式传入。
    建议由 Claude 从本地 memory（reference_yapi.md）读取后注入，禁止硬编码。
    """
    if not email or not password:
        raise ValueError('请提供 YApi 登录邮箱和密码（由 Claude 从 memory 读取或向用户询问）')
    result = _request('/api/user/login', {'email': email, 'password': password})
    if result.get('errcode') != 0:
        raise RuntimeError(f'YApi 登录失败: {result.get("errmsg")}')
    print(f'✓ YApi 登录成功，用户：{result["data"]["username"]}')


# ── 创建 + 写入数据（一步完成）─────────────────────────────────
def create_mock(path, title, data):
    """
    创建 mock 接口并写入数据。

    Args:
        path:  接口路径后缀，不含 basepath，如 '/staff'（不要写 '/claude/staff'）
        title: 接口名称，如 '职员信息'
        data:  列表数据，会自动包装为 {"data": [...]}

    Returns:
        完整 mock URL，如 'https://api.jeecg.com/mock/57/claude/staff'
    """
    add_r = _request('/api/interface/add', {
        'method':     'GET',
        'catid':      _CAT_ID,
        'title':      title,
        'path':       path,
        'project_id': _PROJECT_ID,
    })
    if add_r.get('errcode') != 0:
        raise RuntimeError(f'创建接口失败: {add_r.get("errmsg")}')
    iface_id = str(add_r['data']['_id'])
    print(f'✓ 接口创建成功，id={iface_id}')

    update_mock(iface_id, path, title, data)

    url = f'{_MOCK_PREFIX}{path}'
    print(f'✓ Mock URL：{url}')
    return url


def update_mock(iface_id, path, title, data):
    """
    更新已有接口的 mock 数据。

    Args:
        iface_id: 接口 ID
        path:     接口路径后缀（不含 basepath）
        title:    接口名称
        data:     列表数据，会自动包装为 {"data": [...]}
    """
    res_body = json.dumps(
        {"data": data} if isinstance(data, list) else data,
        ensure_ascii=False, indent=2,
    )
    up_r = _request('/api/interface/up', {
        'id':       str(iface_id),
        'title':    title,
        'catid':    _CAT_ID,
        'path':     path,
        'method':   'GET',
        'project_id': _PROJECT_ID,
        'status':   'undone',
        'tag':      [],
        'req_query': [], 'req_headers': [], 'req_body_form': [], 'req_params': [],
        'req_body_is_json_schema': True,
        'res_body_is_json_schema': False,
        'res_body_type': 'raw',
        'res_body':  res_body,
        'switch_notice': True,
        'api_opened': False,
        'desc': '', 'markdown': '',
    })
    if up_r.get('errcode') != 0:
        raise RuntimeError(f'写入 mock 数据失败: {up_r.get("errmsg")}')
    print(f'✓ mock 数据写入成功')


def delete_mock(iface_id):
    """删除 mock 接口"""
    r = _request('/api/interface/del', {'id': int(iface_id)})
    if r.get('errcode') != 0:
        raise RuntimeError(f'删除失败: {r.get("errmsg")}')
    print(f'✓ 接口 {iface_id} 已删除')


def list_mocks():
    """列出项目下所有接口"""
    r = _request(f'/api/interface/list?project_id={_PROJECT_ID}&page=1&limit=50', method='GET')
    if r.get('errcode') != 0:
        raise RuntimeError(f'查询失败: {r.get("errmsg")}')
    items = r['data']['list']
    print(f'共 {len(items)} 个接口：')
    for item in items:
        print(f'  [{item["_id"]}] {item["title"]}  path={_BASEPATH}{item["path"]}')
    return items


def mock_url(path):
    """根据 path 后缀生成完整 mock URL"""
    return f'{_MOCK_PREFIX}{path}'


# ── CLI 入口 ──────────────────────────────────────────────────
if __name__ == '__main__':
    import sys, os
    args     = sys.argv[1:]
    email    = os.environ.get('YAPI_EMAIL')
    password = os.environ.get('YAPI_PASSWORD')
    if not email or not password:
        print('请设置环境变量 YAPI_EMAIL 和 YAPI_PASSWORD，或由 Claude 从 memory 读取后传入')
        sys.exit(1)
    init_yapi(email=email, password=password)
    if not args or args[0] == 'list':
        list_mocks()
    elif args[0] == 'delete' and len(args) > 1:
        delete_mock(args[1])
    else:
        print('用法：')
        print('  python yapi_mock.py list            # 列出所有接口')
        print('  python yapi_mock.py delete <id>     # 删除接口')
