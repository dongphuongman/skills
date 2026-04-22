"""
jimureport_utils.py — 积木报表脚本公共工具库
所有 create_*.py 脚本通过 `from jimureport_utils import *` 引入，避免重复实现。

用法示例：
    from jimureport_utils import (
        Session, gen_id, gen_code, gen_layer, col_letter,
        parse_sql, save_db, make_designer, base_save, make_styles,
        get_report, chart_entry, virtual_row, create_link,
        parallel_parse_sqls, parallel_save_dbs, parallel_create_links,
    )

环境配置：直接改下方常量，或在调用方覆盖。
"""

import json
import hashlib
import random
import string
import time
from concurrent.futures import ThreadPoolExecutor

import requests

# ── 默认环境（可在调用脚本中覆盖） ─────────────────────────────────
DEFAULT_BASE_URL = "<api_base>"
DEFAULT_TOKEN    = "<token>"
DEFAULT_TENANT   = "2"

def report_urls(report_id: str, base_url: str = DEFAULT_BASE_URL,
                token: str = DEFAULT_TOKEN, tenant: str = DEFAULT_TENANT) -> tuple[str, str]:
    """返回 (preview_url, design_url)，格式：/view/{id}?token=...&tenantId=..."""
    host = base_url.rstrip("/jmreport").rstrip("/")
    qs   = f"token={token}&tenantId={tenant}"
    return (
        f"{host}/jmreport/view/{report_id}?{qs}",
        f"{host}/jmreport/index/{report_id}?{qs}",
    )
SIGN_SECRET      = "dd05f1c54d63749eda95f9fa6d49v442a"   # 第29位是字母 v

# 需要在 Header 中携带 X-Sign + X-TIMESTAMP 的接口路径后缀
SIGNED_PATHS = [
    "/queryFieldBySql", "/executeSelectApi", "/loadTableData",
    "/testConnection",  "/download/image",   "/dictCodeSearch",
    "/getDataSourceByPage", "/getDataSourceById",
]

# ── Session ─────────────────────────────────────────────────────────

class Session:
    """轻量封装：自动处理签名、Token、代理绕过。"""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, token: str = DEFAULT_TOKEN):
        self.base_url = base_url.rstrip("/")
        self._s = requests.Session()
        self._s.trust_env = False   # 必须：绕过系统代理（proxies=None 不够）
        # 并行请求时复用连接，减少 TCP 握手开销
        adapter = requests.adapters.HTTPAdapter(pool_connections=5, pool_maxsize=10)
        self._s.mount("http://", adapter)
        self._s.mount("https://", adapter)
        self._s.headers.update({
            "X-Access-Token": token,
            "Content-Type": "application/json",
        })

    def request(self, path: str, data: dict | None = None, method: str = "POST") -> dict:
        for attempt in range(3):
            headers = {}
            need_sign = data is not None and any(path.endswith(p) for p in SIGNED_PATHS)
            url = self.base_url + path
            if method.upper() == "GET":
                params = dict(data) if data else {}
                if need_sign:
                    # token 必须先加入 params，再一起参与签名计算
                    params["token"] = self._s.headers.get("X-Access-Token", "")
                    headers["X-TIMESTAMP"] = str(int(time.time() * 1000))
                    headers["X-Sign"] = _compute_sign(params)
                resp = self._s.request(method, url, params=params, headers=headers)
            else:
                if need_sign:
                    headers["X-TIMESTAMP"] = str(int(time.time() * 1000))
                    headers["X-Sign"] = _compute_sign(data)
                resp = self._s.request(method, url, json=data, headers=headers)
            resp.raise_for_status()
            result = resp.json()
            if not result.get("success"):
                msg = result.get("message", "")
                # /save 时服务端 code 重复（同秒创建两张报表）→ 重新生成 code 重试
                if path.endswith("/save") and "Duplicate entry" in msg and "uniq_jmreport_code" in msg:
                    if data and "designerObj" in data:
                        obj = json.loads(data["designerObj"])
                        obj["code"] = gen_code()
                        data = {**data, "designerObj": json.dumps(obj, ensure_ascii=False)}
                    time.sleep(1.1)
                    continue
                raise RuntimeError(f"[{path}] 失败: {msg}\n{result}")
            return result
        raise RuntimeError(f"[{path}] 重试3次仍失败")

    def get(self, path: str) -> dict:
        return self.request(path, method="GET")


def _compute_sign(params: dict) -> str:
    """计算积木报表接口签名（MD5 大写）。"""
    sp: dict[str, str] = {}
    for k, v in params.items():
        if v is None:
            continue
        if isinstance(v, bool):
            sp[k] = str(v).lower()
        elif isinstance(v, (int, float)):
            sp[k] = str(v)
        elif isinstance(v, (dict, list)):
            sp[k] = json.dumps(v, ensure_ascii=False, separators=(",", ":"))
        else:
            sp[k] = str(v)
    sorted_json = json.dumps(dict(sorted(sp.items())), ensure_ascii=False, separators=(",", ":"))
    return hashlib.md5((sorted_json + SIGN_SECRET).encode()).hexdigest().upper()


# ── ID / 编码生成 ────────────────────────────────────────────────────

def gen_id() -> str:
    """生成雪花风格 ID（18位字符串）。"""
    return str(int(time.time() * 1000) * 1_000_000 + random.randint(100_000, 999_999))


def gen_code() -> str:
    """生成唯一报表编码（毫秒+随机数，避免同秒冲突）。"""
    return str(int(time.time() * 1000)) + str(random.randint(100, 999))


def gen_layer() -> str:
    """生成图表/图层 layer_id（lyr_ 前缀 + 10位随机字符）。"""
    return "lyr_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=10))


def col_letter(idx: int) -> str:
    """0-based 列索引 → Excel 列字母（0→A, 1→B, 25→Z, 26→AA ...）。"""
    result, n = "", idx + 1
    while n:
        n, r = divmod(n - 1, 26)
        result = chr(65 + r) + result
    return result


# ── 数据集操作 ────────────────────────────────────────────────────────

def parse_api(session: Session, api_url: str) -> list[dict]:
    """
    解析 API 数据集字段，返回 fieldList。
    executeSelectApi 用 POST + query string（不是 JSON body）。
    """
    import hashlib as _hl, requests as _req
    params = {"api": api_url, "method": "0"}
    sp = {k: str(v) for k, v in params.items()}
    sorted_json = json.dumps(dict(sorted(sp.items())), ensure_ascii=False, separators=(",", ":"))
    sign = _hl.md5((sorted_json + SIGN_SECRET).encode()).hexdigest().upper()
    resp = _req.post(
        session.base_url + "/executeSelectApi",
        params=params,
        headers={
            "X-Access-Token": session._s.headers["X-Access-Token"],
            "X-Sign": sign,
            "X-TIMESTAMP": str(int(time.time() * 1000)),
        },
        proxies={},
    )
    resp.raise_for_status()
    r = resp.json()
    if not r.get("success"):
        raise RuntimeError(f"[executeSelectApi] 失败: {r.get('message')}")
    result = r["result"]
    return result["fieldList"] if isinstance(result, dict) else result


def parse_sql(session: Session, sql: str, db_source: str = "") -> list[dict]:
    """
    调用 queryFieldBySql 解析 SQL，返回 fieldList。
    注意：FreeMarker <#if> 中的参数无法识别，传入前需替换为具体值。
    """
    r = session.request("/queryFieldBySql", {"sql": sql, "dbSource": db_source, "type": "0"})
    return r["result"]["fieldList"]


def save_db(
    session: Session,
    report_id: str,
    db_code: str,
    db_name: str,
    sql: str,
    field_list: list[dict],
    param_list: list[dict] | None = None,
    *,
    db_type: str = "0",
    db_source: str = "",
    is_list: str = "1",
    is_page: str = "1",
    json_data: str = "",
    db_id: str | None = None,          # 传入 id = 更新已有数据集
    is_shared: int = 0,
    api_url: str = "",                 # API 数据集：接口地址（db_type="1" 时必填）
    api_method: str = "0",             # API数据集请求方式，db_type="1" 时生效，"0"=GET "1"=POST
) -> str:
    """
    保存（新增/更新）数据集，返回数据集 ID。

    db_type: "0"=SQL / "1"=API / "3"=JSON / "4"=共享
    is_list / is_page: "0"/"1"
    json_data: JSON数据集时必填，格式 '{"data":[...]}'（必须包裹！）
    api_method: API数据集请求方式，"0"=GET，"1"=POST
    """
    payload: dict = {
        "izSharedSource": is_shared,
        "jimuReportId":   "" if is_shared else report_id,
        "dbCode":         db_code,
        "dbChName":       db_name,
        "dbType":         db_type,
        "dbSource":       db_source,
        "isList":         is_list,
        "isPage":         is_page,
        "dbDynSql":       sql,
        "jsonData":       json_data,
        "apiConvert":     "",
        "apiUrl":         api_url,
        "apiMethod":      api_method,
        "fieldList":      field_list,
        "paramList":      param_list or [],
    }
    # API 数据集专用字段
    if db_type == "1":
        payload["apiUrl"]    = api_url or sql
        payload["apiMethod"] = api_method
    if db_id:
        payload["id"] = db_id
    # 死锁自动重试（并行 saveDb 时 MySQL 可能报 Deadlock）
    for attempt in range(3):
        try:
            r = session.request("/saveDb", payload)
            return r["result"]["id"]
        except RuntimeError as e:
            if "Deadlock" in str(e) and attempt < 2:
                time.sleep(0.3 * (attempt + 1))
            else:
                raise


def update_db(session: "Session", db_id: str, **fields) -> None:
    """
    轻量更新数据集的单个或多个字段（如 isPage、isList、dbDynSql 等）。

    用 /loadDbData 取回原始数据，只改指定字段，原样回传 /saveDb。
    比 save_db 快 300x（~0.1s vs ~37s），因为服务端不重新解析 SQL。

    示例：
        update_db(session, db_id, isPage="1")
        update_db(session, db_id, isPage="0", isList="1")
    """
    result = session.get(f"/loadDbData/{db_id}")["result"]
    db = result["reportDb"]
    db["fieldList"] = result["fieldList"]
    db["paramList"] = result["paramList"] or []
    db.update(fields)
    session.request("/saveDb", db)


# ── 报表保存 ──────────────────────────────────────────────────────────

def make_designer(report_id: str, name: str, **extra) -> dict:
    """构造 designerObj 基础结构（save 接口的 designerObj 字段内容）。"""
    return {
        "id":          report_id,
        "code":        gen_code(),
        "name":        name,
        "reportName":  name,
        "type":        "0",
        "template":    0,
        "delFlag":     0,
        "viewCount":   0,
        "updateCount": 0,
        "submitForm":  0,
        **extra,
    }


def base_save(report_id: str, designer_obj: dict, **overrides) -> dict:
    """
    构造 /jmreport/save 请求体。
    !! 只有 designerObj 会被 json.dumps；其他所有字段保持原始 Python 对象 !!

    用法：
        session.request("/save", base_save(report_id, designer, rows=rows, styles=styles, ...))
    """
    payload: dict = {
        # ── 唯一需要 json.dumps 的字段 ──
        "designerObj":  json.dumps(designer_obj, ensure_ascii=False),
        # ── Sheet 元信息 ──
        "name":         "sheet1",
        "sheetId":      "default",
        "sheetName":    "默认Sheet",
        "sheetOrder":   "0",
        "freeze":       "A1",
        "freezeLineColor": "rgb(185, 185, 185)",
        "excel_config_id": report_id,
        # ── 设计数据（调用方通过 overrides 传入）──
        "rows":         {"len": 200},
        "cols":         {"len": 100},
        "styles":       [],
        "merges":       [],
        "chartList":    [],
        "imgList":      [],
        "barcodeList":  [],
        "qrcodeList":   [],
        # ── 固定配置 ──
        "loopBlockList":    [],
        "zonedEditionList": [],
        "fixedPrintHeadRows": [],
        "fixedPrintTailRows": [],
        "hiddenCells":    [],
        "submitHandlers": [],
        "validations":    [],
        "autofilter":     {},
        "dbexps":         [],
        "dicts":          [],
        "displayConfig":  {},
        "printConfig": {
            "paper": "A4", "width": 210, "height": 297, "definition": 1,
            "isBackend": False, "marginX": 10, "marginY": 10,
            "layout": "portrait", "printCallBackUrl": "",
        },
        "querySetting":      {"izOpenQueryBar": False, "izDefaultQuery": True},
        "queryFormSetting":  {"useQueryForm": False, "dbKey": "", "idField": ""},
        "rpbar": {"show": True, "pageSize": "", "btnList": []},
        "fillFormToolbar": {"show": True, "btnList": [
            "save", "subTable_add", "verify", "subTable_del", "print", "close",
            "first", "prev", "next", "paging", "total", "last",
            "exportPDF", "exportExcel", "exportWord",
        ]},
        "hidden": {"rows": [], "cols": [], "conditions": {"rows": {}, "cols": {}}},
        "fillFormInfo":   {"layout": {"direction": "horizontal", "width": 200, "height": 45}},
        "recordSubTableOrCollection": {"group": [], "record": [], "range": []},
        "area":             False,      # False = 系统自动计算滚动高度（推荐）
        "background":       False,
        "pyGroupEngine":    False,
        "isViewContentHorizontalCenter": False,
        "fillFormStyle":    "default",
        "dataRectWidth":    700,
    }
    payload.update(overrides)
    return payload


# ── 样式 ──────────────────────────────────────────────────────────────

def make_styles(border_color: str = "#d8d8d8") -> list[dict]:
    """
    返回标准5种样式列表（通过 cell["style"] 索引引用）：
      0 = 基础边框
      1 = 居中+垂直居中（数据行）
      2 = 蓝底白字（表头）
      3 = 淡蓝底深蓝加粗（标题）
      4 = 蓝色字体（链接/钻取列）
    """
    b = lambda: {"bottom": ["thin", border_color], "top": ["thin", border_color],
                 "left":   ["thin", border_color], "right": ["thin", border_color]}
    return [
        {"border": b()},
        {"border": b(), "align": "center", "valign": "middle"},
        {"border": b(), "align": "center", "valign": "middle",
         "bgcolor": "#01b0f1", "color": "#ffffff"},
        {"border": b(), "align": "center", "valign": "middle",
         "bgcolor": "#E6F2FF", "color": "#0066CC", "font": {"bold": True, "size": 14}},
        {"border": b(), "align": "center", "valign": "middle", "color": "#1677ff"},
    ]


# ── 图表辅助 ──────────────────────────────────────────────────────────

def get_report(session: "Session", report_id: str) -> tuple[dict, dict]:
    """
    获取报表设计，返回 (designer_obj, design) 供 GET→修改→save 场景使用。

    designer_obj: 元数据 dict（直接作为 base_save 第二个参数）
    design:       设计 dict（rows/cols/chartList/styles 等，用 **design 传给 base_save）

    用法：
        designer, design = get_report(session, report_id)
        design["chartList"][0]["extData"]["chartType"] = "bar.stack"
        session.request("/save", base_save(report_id, designer, **design))
    """
    r = session.get(f"/get/{report_id}")
    result = r["result"]
    json_str = result.get("jsonStr", "{}")
    design = json.loads(json_str) if isinstance(json_str, str) else (json_str or {})
    designer_obj = {
        "id":          result["id"],
        "code":        result.get("code", ""),
        "name":        result.get("name", ""),
        "reportName":  result.get("name", ""),
        "type":        result.get("reportType", result.get("type", "0")),
        "template":    result.get("template", 0),
        "delFlag":     result.get("delFlag", 0),
        "viewCount":   result.get("viewCount", 0),
        "updateCount": result.get("updateCount", 0),
        "submitForm":  result.get("submitForm", 0),
        "cssStr":      result.get("cssStr", ""),
        "jsStr":       result.get("jsStr", ""),
    }
    return designer_obj, design


def chart_entry(
    layer_id: str,
    db_id: str,
    db_code: str,
    chart_type: str,
    echarts_cfg: dict,
    row: int,
    col: int = 1,
    col_end: int = 6,
    width: str = "580",
    height: str = "320",
    link_ids: str = "",
    axis_x: str = "name",
    axis_y: str = "value",
    series: str = "",
    api_status: str = "1",
    data_type: str = "sql",
) -> dict:
    """
    构造 chartList 中的单个图表对象。
    virtualCellRange 自动生成为单行（只需1行锚点）。
    """
    return {
        "row":    row,
        "col":    col,
        "width":  width,
        "height": height,
        "config": json.dumps(echarts_cfg, ensure_ascii=False),
        "url":    "",
        "extData": {
            "chartId": layer_id,
            "id":      layer_id,
            "chartType":  chart_type,
            "dataType":   data_type,
            "apiStatus":  api_status,
            "dataId":     db_id,
            "dataId1":    "",
            "dbCode":     db_code,
            "axisX":      axis_x,
            "axisY":      axis_y,
            "series":     series,
            "xText": "", "yText": "",
            "linkIds":    link_ids,
            "source": "", "target": "",
            "isTiming": "", "intervalTime": "",
            "isCustomPropName": False,
        },
        "layer_id": layer_id,
        "virtualCellRange": [[row, c] for c in range(col, col_end + 1)],
        "backgroud": {"enabled": False, "color": "#fff", "image": ""},
        "colspan":  col_end - col + 1,
        "rowspan":  14,
        "offsetX":  0,
        "offsetY":  0,
    }


def virtual_row(layer_id: str, col_start: int = 1, col_end: int = 6) -> dict:
    """生成图表虚拟占位行（放入 rows 字典中）。"""
    return {"cells": {str(c): {"text": " ", "virtual": layer_id}
                      for c in range(col_start, col_end + 1)}}


# ── 联动/钻取 ─────────────────────────────────────────────────────────

def create_link(
    session: Session,
    report_id: str,
    link_name: str,
    link_type: str,
    parameter_list: list[dict],
    *,
    target_report_id: str = "",
    link_chart_id: str = "",
    api_url: str = "",
    eject_type: str = "0",
) -> str:
    """
    创建钻取/联动配置，返回 linkId。

    link_type:
      "0" = 报表钻取（target_report_id 为目标报表 ID）
      "1" = 网络链接（api_url 为目标 URL，target_report_id 传当前报表 ID）
      "2" = 图表联动（link_chart_id 为目标图表 layer_id，target_report_id 传当前报表 ID）

    parameter_list:
      钻取: [{paramName, paramValue, tableIndex, dbCode, fieldName}]
      联动图表→图表: [{paramName, paramValue, index}]
    """
    payload = {
        "linkName":    link_name,
        "linkType":    link_type,
        "reportId":    target_report_id if link_type == "0" else report_id,
        "ejectType":   eject_type,
        "apiUrl":      api_url,
        "apiMethod":   "",
        "requirement": "",
        "linkChartId": link_chart_id,
        "parameter":   json.dumps(parameter_list, ensure_ascii=False),
    }
    r = session.request("/link/saveAndEdit", payload)
    return r["result"]


# ── 并行执行工具 ──────────────────────────────────────────────────────
# 用于在多数据集/多SQL/多联动场景下并行发出 HTTP 请求，大幅降低等待时间。

def parallel_parse_sqls(session: Session, sql_configs: list[dict]) -> list[list[dict]]:
    """
    并行解析多条 SQL，返回对应 fieldList 列表（顺序与输入一致）。

    sql_configs: [{"sql": "...", "db_source": ""}, ...]
    返回:        [fieldList_0, fieldList_1, ...]
    """
    with ThreadPoolExecutor(max_workers=len(sql_configs)) as ex:
        futures = [
            ex.submit(parse_sql, session, cfg["sql"], cfg.get("db_source", ""))
            for cfg in sql_configs
        ]
        return [f.result() for f in futures]


def parallel_save_dbs(session: Session, db_configs: list[dict]) -> list[str]:
    """
    并行保存多个数据集，返回对应 db_id 列表（顺序与输入一致）。

    db_configs: [{"report_id":..., "db_code":..., "db_name":..., "sql":..., "field_list":..., ...}, ...]
    返回:        [db_id_0, db_id_1, ...]
    """
    with ThreadPoolExecutor(max_workers=len(db_configs)) as ex:
        futures = [ex.submit(save_db, session, **cfg) for cfg in db_configs]
        return [f.result() for f in futures]


def parallel_init_and_parse(
    session: Session,
    report_id: str,
    designer_obj: dict,
    sql: str,
    db_source: str = "",
    **save_overrides,
) -> list[dict]:
    """
    ⚠️ 已不推荐。保留供旧脚本兼容。新脚本请用 `parse_and_save_dataset`（3-step 流程）。

    并行执行「首次 /save（创建报表占位）」和「parse_sql（解析 SQL 字段）」，返回 fieldList。
    """
    with ThreadPoolExecutor(max_workers=2) as ex:
        save_fut  = ex.submit(
            session.request, "/save",
            base_save(report_id, designer_obj, **save_overrides)
        )
        parse_fut = ex.submit(parse_sql, session, sql, db_source)
        save_fut.result()
        return parse_fut.result()


def parse_and_save_dataset(
    session: Session,
    report_id: str,
    db_code: str,
    db_name: str,
    sql: str,
    db_source: str = "",
    **save_db_kwargs,
) -> tuple[list[dict], str]:
    """
    解析 SQL → 保存数据集，返回 (field_list, db_id)。

    **关键特性：允许 report_id 此时尚不存在于服务端**（orphan report_id）。
    后续最终 /save 会以此 id 创建报表，数据集会正确绑定上去。实测验证通过。

    相比「首次 /save + parse + saveDb」3 步，此路径**省掉 1 次占位 /save**（~0.5-2s）。

    推荐的单报表最快流程（3 步，4 HTTP 串行）：
        ds_id = ensure_datasource(session, ...)          # 1-2 HTTP
        report_id = gen_id()                              # 客户端，0 HTTP
        field_list, db_id = parse_and_save_dataset(       # 2 HTTP
            session, report_id, "dsCode", "中文名", sql, db_source=ds_id)
        session.request("/save", base_save(               # 1 HTTP — 首次创建报表
            report_id, make_designer(report_id, name),
            rows=rows, cols=cols, styles=styles, merges=merges, chartList=[]))

    **save_db_kwargs** 透传给 `save_db`（常用：db_type, is_list, is_page, json_data, api_url）。
    """
    field_list = parse_sql(session, sql, db_source)
    db_id = save_db(session, report_id, db_code, db_name, sql, field_list,
                    db_source=db_source, **save_db_kwargs)
    return field_list, db_id


# ── 数据源辅助 ──────────────────────────────────────────────────────

def find_datasource(session: Session, ds_name: str) -> str:
    """
    通过 initDataSource 按名称查找数据源 ID。
    返回匹配名称中 ID 最大的记录（即最新创建的）。
    """
    resp = session.get("/initDataSource")
    records = resp.get("result", [])
    matched = [r for r in records if r.get("name") == ds_name]
    if not matched:
        names = [r.get("name") for r in records]
        raise RuntimeError(f"未找到数据源 '{ds_name}'，可用列表：{names}")
    return max(matched, key=lambda x: x["id"])["id"]


def ensure_datasource(
    session: Session,
    name: str,
    db_type: str,
    db_url: str,
    db_username: str = "",
    db_password: str = "",
    db_driver: str = "",
    report_id: str = "",
) -> str:
    """
    确保指定名称的数据源存在，返回其 ID。

    - 已存在（按 name 匹配）: 直接返回 ID，**1 次 HTTP**
    - 不存在: 创建 + 再查 ID，**2 次 HTTP**

    与手写「查询 + 保存 + 再查」3 次 HTTP 相比，已存在场景省 2 次、新建场景省 1 次。
    `/initDataSource` 不需要签名，比 `/getDataSourceByPage` 更快。

    注意：`addDataSource` 返回 `result: true`（布尔值），服务端不返回新建 ID，
    因此新建后必须再次查询才能拿到 ID。
    """
    # 1. 按名称查重
    resp = session.get("/initDataSource")
    records = resp.get("result", [])
    matched = [r for r in records if r.get("name") == name]
    if matched:
        return max(matched, key=lambda x: x["id"])["id"]

    # 2. 不存在 → 新建
    session.request("/addDataSource", {
        "id": "", "reportId": report_id, "code": "",
        "name": name, "dbType": db_type, "dbDriver": db_driver,
        "dbUrl": db_url, "dbUsername": db_username, "dbPassword": db_password,
    })

    # 3. 再查以获取新建的 ID
    resp = session.get("/initDataSource")
    records = resp.get("result", [])
    matched = [r for r in records if r.get("name") == name]
    if not matched:
        raise RuntimeError(f"数据源 '{name}' 保存后仍无法查询到，请检查服务端日志")
    return max(matched, key=lambda x: x["id"])["id"]


def get_ds_connection(session: Session, ds_id: str) -> tuple[str, int, str, str, str]:
    """
    获取数据源 JDBC 连接信息，返回 (host, port, db_name, username, password)。
    仅支持 MySQL JDBC URL 格式。
    """
    import re
    sign = _compute_sign({"id": ds_id})
    resp = session._s.get(
        f"{session.base_url}/getDataSourceById?id={ds_id}",
        headers={
            "X-Access-Token": session._s.headers["X-Access-Token"],
            "X-TIMESTAMP": str(int(time.time() * 1000)),
            "X-Sign": sign,
        },
    )
    resp.raise_for_status()
    ds = resp.json()["result"]
    m = re.search(r"jdbc:mysql://([^:/]+):(\d+)/([^?]+)", ds["dbUrl"])
    if not m:
        raise RuntimeError(f"无法解析 JDBC URL: {ds['dbUrl']}")
    return m.group(1), int(m.group(2)), m.group(3), ds["dbUsername"], ds["dbPassword"]


def query_mysql(host: str, port: int, db_name: str, user: str, pwd: str, sql: str) -> list[tuple]:
    """
    执行 MySQL 查询，返回原始行列表。调用方自行解包。
    需要 pymysql 已安装。
    """
    import pymysql
    conn = pymysql.connect(host=host, port=port, database=db_name,
                           user=user, password=pwd, charset="utf8mb4")
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    finally:
        conn.close()


# ── 图表布局辅助 ────────────────────────────────────────────────────

def build_chart_layout(
    report_name: str,
    layer_configs: list[dict],
    col_end: int = 9,
) -> tuple[dict, dict, list, list]:
    """
    构建标准图表布局（标题行 + 图表虚拟占位行），返回 (rows, cols, styles, merges)。

    layer_configs: [{"layer_id": str, "row": int, "span": int}, ...]
      - layer_id: 图表 layer_id
      - row:      图表起始行号
      - span:     图表行跨度（用于计算下方留白行）

    返回值可直接传给 base_save:
        rows, cols, styles, merges = build_chart_layout(...)
        session.request("/save", base_save(report_id, designer,
            rows=rows, cols=cols, styles=styles, merges=merges, chartList=[...]))
    """
    styles = [
        {"align": "center"},                                        # 0
        {"align": "center", "font": {"size": 14}},                 # 1
        {"font": {"size": 14}},                                     # 2
        {"align": "center", "font": {"size": 14, "bold": True}},   # 3 标题主格
        {"font": {"size": 14, "bold": True}},                       # 4 标题合并格
    ]

    # 标题行
    title_cells = {"1": {"merge": [0, col_end - 1], "text": report_name, "style": 3}}
    for c in range(2, col_end + 1):
        title_cells[str(c)] = {"style": 4}

    rows: dict = {
        "0": {"cells": title_cells, "height": 50},
        "len": 200,
    }

    # 图表虚拟占位行
    for cfg in layer_configs:
        lid, row = cfg["layer_id"], cfg["row"]
        rows[str(row)] = {
            "cells": {str(c): {"text": " ", "virtual": lid}
                      for c in range(1, col_end + 1)}
        }

    # 末尾留白行（最后一个图表下方）
    if layer_configs:
        last = max(layer_configs, key=lambda c: c["row"])
        end_row = last["row"] + last.get("span", 16)
        rows[str(end_row)] = {"cells": {"1": {"text": " "}}}

    cols = {
        "0": {"width": 20},
        **{str(i): {"width": 100} for i in range(1, col_end + 1)},
        "len": 100,
    }

    merges = [f"B1:{col_letter(col_end)}1"]

    return rows, cols, styles, merges


# ── 图表更新辅助 ────────────────────────────────────────────────────

def update_chart_config(
    session: Session,
    report_id: str,
    updater_fn,
    *,
    chart_index: int | None = None,
    chart_type_filter: str = "",
) -> int:
    """
    通用图表配置更新：获取报表 → 遍历图表 → 调用 updater_fn 修改 config → 保存。

    updater_fn(config: dict, chart_type: str) -> bool
        接收 ECharts config dict 和 chartType 字符串，原地修改 config，
        返回 True 表示已修改，False 表示跳过。

    chart_index: 只更新指定索引的图表（None = 全部）
    chart_type_filter: 只更新指定 chartType 的图表（"" = 不过滤）

    返回实际更新的图表数量。
    """
    designer, design = get_report(session, report_id)
    chart_list = design.get("chartList", [])
    if not chart_list:
        raise RuntimeError("报表没有图表组件")

    updated = 0
    for idx, chart in enumerate(chart_list):
        if chart_index is not None and idx != chart_index:
            continue
        ct = chart.get("extData", {}).get("chartType", "")
        if chart_type_filter and ct != chart_type_filter:
            continue

        config = json.loads(chart.get("config", "{}"))
        if updater_fn(config, ct):
            chart["config"] = json.dumps(config, ensure_ascii=False)
            updated += 1

    if updated:
        session.request("/save", base_save(report_id, designer, **design))

    return updated


def parallel_create_links(session: Session, link_configs: list[dict]) -> list[str]:
    """
    并行创建多个钻取/联动配置，返回对应 link_id 列表（顺序与输入一致）。

    link_configs: [{"report_id":..., "link_name":..., "link_type":..., "parameter_list":..., ...}, ...]
    返回:          [link_id_0, link_id_1, ...]
    """
    with ThreadPoolExecutor(max_workers=len(link_configs)) as ex:
        futures = [ex.submit(create_link, session, **cfg) for cfg in link_configs]
        return [f.result() for f in futures]


def parallel_parse_apis(session: Session, api_urls: list[str]) -> list[list[dict]]:
    """并行解析多个 API 数据集字段，返回 fieldList 列表（顺序与输入一致）。"""
    with ThreadPoolExecutor(max_workers=min(len(api_urls), 8)) as ex:
        futures = [ex.submit(parse_api, session, u) for u in api_urls]
        return [f.result() for f in futures]


def parallel_fill_charts(session: Session, charts: list[dict]) -> list[dict]:
    """
    并行回填 chartList 里的 SQL/API 图表数据（原地修改 + 返回列表）。

    支持规则：
      - extData.dataType in ("sql","api") 且 extData.dataId 非空 → 调 /qurestSql 或 /qurestApi
      - 其他（JSON/静态/_NONE） → 跳过
      - 单系列（series=""）：回填 series[0].data 和 xAxis.data / yAxis.data
      - 多系列（series="type"）：按 type 列分组重建 series，保留第 0 条模板样式
      - 横向图（yAxis.type=="category"）：分类回填到 yAxis.data
      - 饼图/漏斗/仪表盘（无 xAxis/yAxis）：rows 为 [{name,value},...] 直接回填 series[0].data

    并发上限 10。
    """
    from collections import OrderedDict
    import copy

    def _fill_one(chart: dict) -> dict:
        ext = chart.get("extData", {})
        data_type = ext.get("dataType")
        data_id = ext.get("dataId")
        if data_type not in ("sql", "api") or not data_id:
            return chart

        payload = {
            "apiSelectId": data_id,
            "chartSetting": {
                "chartId": ext.get("chartId", ""), "id": ext.get("chartId", ""),
                "chartType": ext.get("chartType", ""), "dataType": data_type,
                "apiStatus": ext.get("apiStatus", "1"), "dataId": data_id,
                "dataId1": "", "dbCode": ext.get("dbCode", ""),
                "axisX": ext.get("axisX", "name"), "axisY": ext.get("axisY", "value"),
                "series": ext.get("series", ""),
                "xText": ext.get("xText", ""), "yText": ext.get("yText", ""),
                "linkIds": "", "source": "", "target": "", "isTiming": "", "intervalTime": "",
                "isCustomPropName": ext.get("isCustomPropName", False), "run": 1,
            },
        }
        if data_type == "api":
            result = session.request("/qurestApi", payload)["result"]
            rows = result.get("data") if isinstance(result, dict) else result
        else:
            rows = session.request("/qurestSql", payload)["result"]
        if not rows:
            return chart

        cfg = json.loads(chart["config"])
        axis_x = ext.get("axisX", "name")
        axis_y = ext.get("axisY", "value")
        series_fld = ext.get("series", "")

        if series_fld:
            # 多系列：按 type 分组
            x_seen = OrderedDict()
            for r in rows:
                x_seen[r[axis_x]] = None
            x_data = list(x_seen.keys())

            smap = OrderedDict()
            for r in rows:
                t = r[series_fld]
                smap.setdefault(t, {})[r[axis_x]] = r[axis_y]
            series_names = list(smap.keys())
            for t in smap:
                smap[t] = [smap[t].get(x) for x in x_data]

            if isinstance(cfg.get("xAxis"), dict):
                cfg["xAxis"]["data"] = x_data
            elif isinstance(cfg.get("yAxis"), dict):
                cfg["yAxis"]["data"] = x_data
            if isinstance(cfg.get("legend"), dict):
                cfg["legend"]["data"] = series_names

            orig = {s.get("name", ""): s for s in cfg.get("series", [])}
            template = cfg["series"][0] if cfg.get("series") else {}
            new_series = []
            for sname in series_names:
                tmpl = copy.deepcopy(orig.get(sname, template))
                tmpl["name"] = sname
                tmpl["data"] = smap[sname]
                tmpl.setdefault("typeData", [])
                new_series.append(tmpl)
            cfg["series"] = new_series
        else:
            # 单系列：rows 可能是 [{name,value},...] 或两列
            if rows and isinstance(rows[0], dict) and axis_x in rows[0] and axis_y in rows[0]:
                x_data = [r[axis_x] for r in rows]
                y_data = [r[axis_y] for r in rows]
            else:
                x_data = y_data = []

            # 饼图/漏斗：无 xAxis/yAxis，series[0].data 是 {name,value} 列表
            if not cfg.get("xAxis") and not cfg.get("yAxis"):
                if cfg.get("series"):
                    cfg["series"][0]["data"] = [
                        {"name": n, "value": v, "itemStyle": {"color": None}}
                        for n, v in zip(x_data, y_data)
                    ]
            else:
                if isinstance(cfg.get("xAxis"), dict) and cfg["xAxis"].get("type") != "value":
                    cfg["xAxis"]["data"] = x_data
                elif isinstance(cfg.get("yAxis"), dict) and cfg["yAxis"].get("type") == "category":
                    cfg["yAxis"]["data"] = x_data
                if cfg.get("series"):
                    cfg["series"][0]["data"] = y_data

        chart["config"] = json.dumps(cfg, ensure_ascii=False)
        return chart

    with ThreadPoolExecutor(max_workers=10) as ex:
        list(ex.map(_fill_one, charts))
    return charts


def print_summary(report_id: str, report_name: str, base_url: str = DEFAULT_BASE_URL, token: str = DEFAULT_TOKEN):
    """打印报表创建结果摘要。"""
    preview, design = report_urls(report_id, base_url, token)
    print(f"\n{'=' * 50}")
    print(f"报表创建成功: {report_name}")
    print(f"  report_id:  {report_id}")
    print(f"  预览地址:   {preview}")
    print(f"  设计器地址: {design}")
    print(f"{'=' * 50}")
