"""
Online 表单默认值解析工具

复刻前端 FieldDefVal.ts 的默认值转换逻辑，供 Python 脚本插入数据时使用。
来源：src/views/super/online/cgform/util/FieldDefVal.ts

用法：
  from onlform_defval import resolve_default_values, init_api

  init_api('<api_base>', '<token>')
  values = resolve_default_values({
      'sys_date': {'value': '#{date}', 'type': 'string', 'view': 'date'},
      'sys_user': {'value': '#{sysUserCode}', 'type': 'string', 'view': 'text'},
      'js_ts': {'value': '{{+new Date()}}', 'type': 'string', 'view': 'text'},
      'order_no': {'value': '${shop_order_num}', 'type': 'string', 'view': 'text'},
      'price': {'value': '100.5', 'type': 'number', 'view': 'text'},
      'year_f': {'value': '#{date}', 'type': 'string', 'view': 'date', 'picker': 'year'},
  })
  # returns: {'sys_date': '2026-03-30', 'sys_user': 'admin', 'js_ts': 1774866000000, ...}
"""
import re
import time
import math
import random
import urllib.request
import json
import ssl
from datetime import datetime, timedelta

_api_base = ''
_token = ''
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE
_user_info = None

# 三种表达式正则
NORMAL_RE = re.compile(r'#\{([^}]+?)\}')
CUSTOM_RE = re.compile(r'\{\{([^}]+?)\}\}')
FILLRULE_RE = re.compile(r'\$\{([^}]+?)\}')


def init_api(api_base: str, token: str):
    global _api_base, _token, _user_info
    _api_base = api_base
    _token = token
    _user_info = None


def _request(path: str, data=None, method='GET'):
    url = f'{_api_base}{path}'
    headers = {'X-Access-Token': _token, 'Content-Type': 'application/json; charset=UTF-8'}
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    resp = urllib.request.urlopen(req, context=_ssl_ctx)
    return json.loads(resp.read().decode('utf-8'))


def _get_user_info():
    """获取当前登录用户信息（缓存）"""
    global _user_info
    if _user_info is None:
        try:
            r = _request('/sys/user/getUserInfo')
            if r.get('success') and r.get('result'):
                # userInfo 在 result.userInfo 里
                _user_info = r['result'].get('userInfo', r['result'])
            else:
                _user_info = {}
        except Exception:
            _user_info = {}
    return _user_info


def _resolve_normal_expr(expr: str) -> str:
    """解析普通表达式 #{...}"""
    now = datetime.now()
    if expr == 'date':
        return now.strftime('%Y-%m-%d')
    elif expr == 'time':
        return now.strftime('%H:%M:%S')
    elif expr == 'datetime':
        return now.strftime('%Y-%m-%d %H:%M:%S')
    else:
        user = _get_user_info()
        mapping = {
            'sysUserId': 'id',
            'sysUserCode': 'username',
            'sys_user_code': 'username',
            'sysUserName': 'realname',
            'sysOrgCode': 'orgCode',
            'sys_org_code': 'orgCode',
        }
        if expr in mapping and user:
            return user.get(mapping[expr], '')
        return f'#{{{expr}}}'


def _resolve_custom_expr(expr: str):
    """解析用户自定义表达式 {{...}}，用 Python eval 模拟"""
    # 常用JS表达式的Python等价
    js_to_py = {
        '+new Date()': str(int(time.time() * 1000)),
        'new Date().getTime()': str(int(time.time() * 1000)),
        'Date.now()': str(int(time.time() * 1000)),
    }
    if expr in js_to_py:
        return js_to_py[expr]
    # 尝试用 Python eval
    safe_globals = {'__builtins__': {}, 'Math': math, 'math': math, 'random': random, 'int': int, 'float': float, 'str': str}
    # 转换常见JS语法到Python
    py_expr = expr
    py_expr = py_expr.replace('Math.floor', 'int')
    py_expr = py_expr.replace('Math.random()', 'random.random()')
    py_expr = py_expr.replace('Math.round', 'round')
    py_expr = py_expr.replace('Math.ceil', 'math.ceil')
    try:
        return eval(py_expr, safe_globals)
    except Exception:
        return f'{{{{{expr}}}}}'


def _resolve_fillrule_expr(expr: str) -> str:
    """解析填值规则表达式 ${...}，调用后端API"""
    # 处理 queryString 参数
    parts = expr.split('?', 1)
    rule_code = parts[0]
    try:
        r = _request(f'/sys/fillRule/executeRuleByCode/{rule_code}', {}, method='PUT')
        if r.get('success'):
            return r.get('result', '')
        return f'${{{expr}}}'
    except Exception:
        return f'${{{expr}}}'


def _transform_date_picker(value: str, picker: str) -> str:
    """
    日期picker转换：年/月/周/季度 → YYYY-MM-DD
    复刻前端 transformDefValDate 逻辑
    """
    if not picker or picker == 'default' or not value:
        return value
    try:
        if picker == 'year':
            # "2026-01-01" → 取年份
            year = int(value.split('-')[0])
            return f'{year}-01-01'
        elif picker == 'month':
            # "2026-03-01" → 取年月
            parts = value.split('-')
            year = int(parts[0])
            month = int(parts[1])
            return f'{year}-{month:02d}-01'
        elif picker == 'week':
            # "2026-03-24" → 取该周的周一
            parts = value.split('-')
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            d = datetime(year, month, day)
            monday = d - timedelta(days=d.weekday())
            return monday.strftime('%Y-%m-%d')
        elif picker == 'quarter':
            # "2026-01-01" → 取季度第一天
            parts = value.split('-')
            year = int(parts[0])
            month = int(parts[1])
            quarter = (month - 1) // 3 + 1
            first_month = (quarter - 1) * 3 + 1
            return f'{year}-{first_month:02d}-01'
    except Exception:
        pass
    return value


def resolve_single(value: str, field_type: str = 'string', view: str = 'text', picker: str = '') -> any:
    """
    解析单个默认值表达式，返回转换后的值

    Args:
        value: 默认值表达式（如 '#{date}', '{{+new Date()}}', '${shop_order_num}', 'Y'）
        field_type: 字段类型（'string', 'number' 等）
        view: 控件类型（'text', 'date', 'datetime' 等）
        picker: 日期picker（'year', 'month', 'week', 'quarter', ''）
    """
    if value is None or value == '':
        return value

    result = value

    # 检查表达式合法性（填值规则不能与其他混用）
    fillrule_count = len(FILLRULE_RE.findall(value))
    normal_count = len(NORMAL_RE.findall(value))
    custom_count = len(CUSTOM_RE.findall(value))

    if fillrule_count > 1:
        return value  # 不合法：多个填值规则
    if fillrule_count > 0 and (normal_count + custom_count) > 0:
        return value  # 不合法：填值规则与其他混用

    # 填值规则
    if fillrule_count > 0:
        match = FILLRULE_RE.search(result)
        if match:
            resolved = _resolve_fillrule_expr(match.group(1))
            if match.group(0) == result:
                result = resolved
            else:
                result = result.replace(match.group(0), str(resolved))
    else:
        # 普通表达式
        for match in NORMAL_RE.finditer(result):
            resolved = _resolve_normal_expr(match.group(1))
            if match.group(0) == result:
                result = resolved
                break
            result = result.replace(match.group(0), str(resolved))

        # 用户自定义表达式
        if isinstance(result, str):
            for match in CUSTOM_RE.finditer(result):
                resolved = _resolve_custom_expr(match.group(1))
                if match.group(0) == result:
                    result = resolved
                    break
                result = result.replace(match.group(0), str(resolved))

    # number 类型转换
    if field_type == 'number' and result is not None:
        try:
            result = float(result)
            if result == int(result):
                result = int(result)
        except (ValueError, TypeError):
            pass

    # 日期 picker 转换
    if view == 'date' and picker and isinstance(result, str):
        result = _transform_date_picker(result, picker)

    return result


def resolve_default_values(fields: dict) -> dict:
    """
    批量解析默认值

    Args:
        fields: {field_name: {'value': defVal, 'type': dbType, 'view': fieldShowType, 'picker': picker}}

    Returns:
        {field_name: resolved_value}
    """
    result = {}
    for name, config in fields.items():
        value = config.get('value', '')
        field_type = config.get('type', 'string')
        view = config.get('view', 'text')
        picker = config.get('picker', '')
        result[name] = resolve_single(value, field_type, view, picker)
    return result


if __name__ == '__main__':
    # 测试示例
    import sys
    if len(sys.argv) < 3:
        print('用法: python onlform_defval.py <api_base> <token>')
        print('示例: python onlform_defval.py http://localhost:8080/jeecg-boot your-token')
        sys.exit(1)

    init_api(sys.argv[1], sys.argv[2])

    tests = {
        'static_val': {'value': 'Y', 'type': 'string', 'view': 'text'},
        'static_num': {'value': '100', 'type': 'number', 'view': 'text'},
        'sys_date': {'value': '#{date}', 'type': 'string', 'view': 'date'},
        'sys_datetime': {'value': '#{datetime}', 'type': 'string', 'view': 'datetime'},
        'sys_user_code': {'value': '#{sysUserCode}', 'type': 'string', 'view': 'text'},
        'sys_user_name': {'value': '#{sysUserName}', 'type': 'string', 'view': 'text'},
        'sys_org_code': {'value': '#{sysOrgCode}', 'type': 'string', 'view': 'text'},
        'js_timestamp': {'value': '{{+new Date()}}', 'type': 'string', 'view': 'text'},
        'js_random': {'value': '{{Math.floor(Math.random()*10000)}}', 'type': 'string', 'view': 'text'},
        'mixed': {'value': '#{sysUserName}-#{date}', 'type': 'string', 'view': 'text'},
    }

    results = resolve_default_values(tests)
    print('默认值解析结果:')
    for k, v in results.items():
        print(f'  {k} = {v} (type={type(v).__name__})')
