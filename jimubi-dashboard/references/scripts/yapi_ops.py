"""
yapi_ops.py — YApi Mock 接口管理预置脚本
=========================================
统一使用 claude AI 项目（proj_id=57，catid=1157，basepath=/claude）

命令：
  create-mock   创建 mock 接口（单个或批量）
  list          列出项目中的接口
  delete        删除接口（按标题）
  update        更新接口 res_body

用法示例：
  py yapi_ops.py create-mock YAPI_BASE EMAIL PASSWORD \
      --title "折线图单系列数据" \
      --path "/line_single" \
      --body '[{"name":"一月","value":120}]'

  py yapi_ops.py list YAPI_BASE EMAIL PASSWORD

  py yapi_ops.py delete YAPI_BASE EMAIL PASSWORD --title "折线图单系列数据"

单系列数据模板（--template single）：
  [{"name":"一月","value":120},{"name":"二月","value":200},
   {"name":"三月","value":150},{"name":"四月","value":300},
   {"name":"五月","value":280},{"name":"六月","value":350}]

多系列数据模板（--template multi）：
  [{"type":"系列A","name":"一月","value":120},{"type":"系列A","name":"二月","value":200},
   {"type":"系列A","name":"三月","value":150},{"type":"系列A","name":"四月","value":280},
   {"type":"系列A","name":"五月","value":350},
   {"type":"系列B","name":"一月","value":80}, {"type":"系列B","name":"二月","value":160},
   {"type":"系列B","name":"三月","value":220},{"type":"系列B","name":"四月","value":180},
   {"type":"系列B","name":"五月","value":240}]
"""

import sys, json, argparse, time, http.cookiejar, urllib.request, urllib.parse

sys.stdout.reconfigure(encoding='utf-8')

# ── 固定项目参数（claude AI，禁止修改为其他项目）──────────────────────────────
PROJ_ID  = 57
CATID    = 1157
BASEPATH = '/claude'

# ── 内置数据模板 ───────────────────────────────────────────────────────────────
TEMPLATES = {
    'single': [
        {"name": "一月", "value": 120}, {"name": "二月", "value": 200},
        {"name": "三月", "value": 150}, {"name": "四月", "value": 300},
        {"name": "五月", "value": 280}, {"name": "六月", "value": 350},
    ],
    'multi': [
        {"type": "系列A", "name": "一月", "value": 120},
        {"type": "系列A", "name": "二月", "value": 200},
        {"type": "系列A", "name": "三月", "value": 150},
        {"type": "系列A", "name": "四月", "value": 280},
        {"type": "系列A", "name": "五月", "value": 350},
        {"type": "系列B", "name": "一月", "value": 80},
        {"type": "系列B", "name": "二月", "value": 160},
        {"type": "系列B", "name": "三月", "value": 220},
        {"type": "系列B", "name": "四月", "value": 180},
        {"type": "系列B", "name": "五月", "value": 240},
    ],
    'bar_multi': [
        {"type": "Q1", "name": "华北", "value": 320},
        {"type": "Q1", "name": "华南", "value": 280},
        {"type": "Q1", "name": "华东", "value": 410},
        {"type": "Q2", "name": "华北", "value": 380},
        {"type": "Q2", "name": "华南", "value": 350},
        {"type": "Q2", "name": "华东", "value": 460},
    ],
    'pie': [
        {"name": "直接访问", "value": 335},
        {"name": "邮件营销", "value": 310},
        {"name": "联盟广告", "value": 234},
        {"name": "视频广告", "value": 135},
        {"name": "搜索引擎", "value": 548},
    ],
    'gauge': [
        {"name": "总量", "value": 100},
        {"name": "当前", "value": 73},
    ],
    'table': [
        {"name": "项目A", "value": 1250},
        {"name": "项目B", "value": 980},
        {"name": "项目C", "value": 1560},
        {"name": "项目D", "value": 720},
        {"name": "项目E", "value": 1840},
    ],
}

# ── YApi HTTP 工具 ─────────────────────────────────────────────────────────────
_cookie_jar = http.cookiejar.CookieJar()
_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_cookie_jar))
_yapi_base = ''

def _req(method, path, data=None, params=None):
    url = _yapi_base + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    body = json.dumps(data, ensure_ascii=False).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with _opener.open(req, timeout=20) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f'[HTTP {e.code}] {path}: {body[:200]}')
        return {}
    except Exception as e:
        print(f'[请求失败] {path}: {e}')
        return {}

def _login(email, password):
    global _yapi_base
    r = _req('POST', '/api/user/login', {'email': email, 'password': password})
    if r.get('errcode') != 0:
        print(f'YApi 登录失败: {r.get("errmsg")}')
        sys.exit(1)
    uname = (r.get('data') or {}).get('username', email)
    print(f'登录成功: {uname}')
    return r

def mock_url(path):
    """生成正确的 Mock URL（含 basepath）"""
    return f"{_yapi_base}/mock/{PROJ_ID}{BASEPATH}{path}"

# ── 命令实现 ───────────────────────────────────────────────────────────────────

def cmd_create_mock(args):
    _login(args.email, args.password)

    # 决定 res_body
    if args.template:
        if args.template not in TEMPLATES:
            print(f'未知模板: {args.template}，可用: {list(TEMPLATES.keys())}')
            sys.exit(1)
        res_body = json.dumps(TEMPLATES[args.template], ensure_ascii=False)
    elif args.body:
        res_body = args.body
    elif args.body_file:
        with open(args.body_file, 'r', encoding='utf-8') as f:
            res_body = f.read()
    else:
        print('必须提供 --body、--body-file 或 --template')
        sys.exit(1)

    # 生成唯一 path（加时间戳避免冲突）
    ts = int(time.time())
    iface_path = args.path if args.path else f'/{args.title.replace(" ","_")}_{ts}'

    payload = {
        'project_id': PROJ_ID,
        'catid':      CATID,
        'title':      args.title,
        'path':       iface_path,
        'method':     'GET',
        'status':     'done',
        'res_body_type': 'raw',
        'res_body':   res_body,
    }
    r = _req('POST', '/api/interface/add', payload)
    ec = r.get('errcode')
    if ec != 0:
        print(f'创建失败 errcode={ec}: {r.get("errmsg")}')
        sys.exit(1)

    actual_path = (r.get('data') or {}).get('path', iface_path)
    url = mock_url(actual_path)
    iid = (r.get('data') or {}).get('_id')
    print(f'创建成功: id={iid}')
    print(f'Mock URL: {url}')
    return url


def cmd_list(args):
    _login(args.email, args.password)
    r = _req('GET', '/api/interface/list', params={
        'project_id': PROJ_ID, 'page': 1, 'limit': 50
    })
    items = ((r.get('data') or {}).get('list') or [])
    if not items:
        print('（无接口）')
        return
    print(f'{"ID":<8} {"标题":<30} {"路径"}')
    print('-' * 70)
    for it in items:
        print(f'{it["_id"]:<8} {it["title"]:<30} {BASEPATH}{it["path"]}')
        print(f'         Mock URL: {mock_url(it["path"])}')


def cmd_delete(args):
    _login(args.email, args.password)
    # 查找接口 ID
    r = _req('GET', '/api/interface/list', params={
        'project_id': PROJ_ID, 'page': 1, 'limit': 100
    })
    items = ((r.get('data') or {}).get('list') or [])
    targets = [it for it in items if it.get('title') == args.title]
    if not targets:
        print(f'未找到标题为"{args.title}"的接口')
        return
    for it in targets:
        dr = _req('POST', '/api/interface/del', {'id': it['_id']})
        print(f'删除 {it["title"]} (id={it["_id"]}): errcode={dr.get("errcode")}')


def cmd_update(args):
    _login(args.email, args.password)
    # 查找接口
    r = _req('GET', '/api/interface/list', params={
        'project_id': PROJ_ID, 'page': 1, 'limit': 100
    })
    items = ((r.get('data') or {}).get('list') or [])
    targets = [it for it in items if it.get('title') == args.title]
    if not targets:
        print(f'未找到标题为"{args.title}"的接口')
        return

    if args.template:
        res_body = json.dumps(TEMPLATES[args.template], ensure_ascii=False)
    elif args.body:
        res_body = args.body
    else:
        print('必须提供 --body 或 --template')
        sys.exit(1)

    for it in targets:
        payload = dict(it)
        payload['_id'] = it['_id']
        payload['res_body'] = res_body
        payload['res_body_type'] = 'raw'
        ur = _req('POST', '/api/interface/save', payload)
        print(f'更新 {it["title"]} (id={it["_id"]}): errcode={ur.get("errcode")}')
        print(f'Mock URL: {mock_url(it["path"])}')


# ── CLI 入口 ───────────────────────────────────────────────────────────────────

def main():
    global _yapi_base
    parser = argparse.ArgumentParser(description='YApi Mock 接口管理（claude AI 项目）')
    sub = parser.add_subparsers(dest='cmd', required=True)

    # 公共参数
    def add_common(p):
        p.add_argument('yapi_base', help='YApi 地址，如 https://api.jeecg.com')
        p.add_argument('email',    help='YApi 账号 Email')
        p.add_argument('password', help='YApi 密码')

    # create-mock
    pm = sub.add_parser('create-mock', help='创建 mock 接口')
    add_common(pm)
    pm.add_argument('--title',     required=True, help='接口标题')
    pm.add_argument('--path',      help='接口路径（默认自动生成）')
    pm.add_argument('--body',      help='JSON 响应体字符串')
    pm.add_argument('--body-file', help='从文件读取响应体')
    pm.add_argument('--template',  help=f'内置数据模板: {list(TEMPLATES.keys())}')

    # list
    pl = sub.add_parser('list', help='列出接口')
    add_common(pl)

    # delete
    pd = sub.add_parser('delete', help='删除接口')
    add_common(pd)
    pd.add_argument('--title', required=True, help='接口标题')

    # update
    pu = sub.add_parser('update', help='更新接口 res_body')
    add_common(pu)
    pu.add_argument('--title',    required=True)
    pu.add_argument('--body',     help='新的 JSON 响应体')
    pu.add_argument('--template', help='内置数据模板')

    args = parser.parse_args()
    _yapi_base = args.yapi_base.rstrip('/')

    if   args.cmd == 'create-mock': cmd_create_mock(args)
    elif args.cmd == 'list':        cmd_list(args)
    elif args.cmd == 'delete':      cmd_delete(args)
    elif args.cmd == 'update':      cmd_update(args)


if __name__ == '__main__':
    main()
