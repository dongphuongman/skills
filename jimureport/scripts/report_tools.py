#!/usr/bin/env python3
"""
report_tools.py — 积木报表查询/管理/详情/更新 合并工具

用法：
  python report_tools.py list [-k 关键词] [-n 50]       # 列出报表
  python report_tools.py detail <report_id>             # 查看报表详情
  python report_tools.py delete <report_id>             # 删除报表
  python report_tools.py copy <report_id> <新名称>      # 复制报表

提供可 import 的函数（供 heredoc 脚本调用）：
  from report_tools import update_colors, update_legend, update_label, upload_image
"""

import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(__file__))

import pymysql, requests
from jimureport_utils import Session, gen_id, gen_code, base_save, get_report


# ── 查询 ─────────────────────────────────────────────────────────────

def list_reports(base_url, token, db_cfg, keyword="", limit=20):
    """按名称模糊搜索报表列表。"""
    conn = pymysql.connect(**db_cfg, charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cur:
            sql = "SELECT id, name, code, create_by, create_time FROM jimu_report WHERE del_flag=0"
            params = []
            if keyword:
                sql += " AND name LIKE %s"
                params.append(f"%{keyword}%")
            sql += " ORDER BY create_time DESC LIMIT %s"
            params.append(limit)
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        print("未找到报表" + (f"（关键词: {keyword}）" if keyword else ""))
        return
    print(f"\n{'ID':<22} {'名称':<28} {'创建人':<12} {'创建时间'}")
    print("-" * 80)
    for r in rows:
        ct = str(r.get("create_time", ""))[:19]
        print(f"{r['id']:<22} {str(r['name']):<28} {str(r.get('create_by','')):<12} {ct}")
    print(f"\n共 {len(rows)} 条")


def show_detail(base_url, token, report_id):
    """查看报表详情（数据集/字段/图表/样式/CSS/JS）。"""
    session = Session(base_url, token)
    designer, design = get_report(session, report_id)

    print(f"\n{'='*60}")
    print(f"  报表名称 : {designer.get('name')}")
    print(f"  报表 ID  : {designer.get('id')}")
    print(f"  报表编码 : {designer.get('code')}")
    print(f"{'='*60}")

    # 样式
    styles = design.get("styles", [])
    if styles:
        print(f"\n[样式] 共 {len(styles)} 个")
        for i, s in enumerate(styles):
            print(f"  {i}: {json.dumps(s, ensure_ascii=False)[:120]}")

    # rows
    rows = design.get("rows", {})
    print(f"\n[行列]")
    for rk in sorted((k for k in rows if k != "len"), key=lambda x: int(x)):
        rv = rows[rk]
        cells = rv.get("cells", {})
        for ck, cv in cells.items():
            t = cv.get("text", "")
            if t:
                print(f"  r{rk}c{ck}: {t}  style={cv.get('style','')} agg={cv.get('aggregate','')}")

    # 图表
    chart_list = design.get("chartList", [])
    if chart_list:
        print(f"\n[图表] 共 {len(chart_list)} 个")
        for ch in chart_list:
            ed = ch.get("extData", {})
            print(f"  type={ed.get('chartType')} dbCode={ed.get('dbCode')} "
                  f"axisX={ed.get('axisX')} axisY={ed.get('axisY')}")

    # CSS/JS
    for key in ("cssStr", "jsStr"):
        val = designer.get(key) or design.get(key)
        if val:
            print(f"\n[{key}] {str(val)[:200]}")

    print(f"\n  设计器: {base_url}/index/{report_id}")
    print(f"  预览  : {base_url}/view/{report_id}?token={token}")


# ── 管理 ─────────────────────────────────────────────────────────────

def delete_report(base_url, token, report_id):
    """删除报表。"""
    sess = requests.Session()
    sess.trust_env = False
    sess.headers.update({"X-Access-Token": token})
    resp = sess.delete(f"{base_url}/delete", params={"id": report_id})
    resp.raise_for_status()
    result = resp.json()
    if result.get("success"):
        print(f"删除成功: {report_id}")
    else:
        print(f"删除失败: {result.get('message')}")
        sys.exit(1)


def copy_report(base_url, token, src_id, new_name):
    """复制报表。"""
    sess = requests.Session()
    sess.trust_env = False
    sess.headers.update({"X-Access-Token": token})

    resp = sess.get(f"{base_url}/show", params={"id": src_id})
    resp.raise_for_status()
    data = resp.json()["result"]

    json_str = data.get("jsonStr", "{}")
    design = json.loads(json_str) if isinstance(json_str, str) else (json_str or {})
    sheets = design.get("sheets", {})
    sheet = next(iter(sheets.values()), {}) if sheets else design

    new_id, new_code = gen_id(), gen_code()
    designer_obj = {"id": new_id, "code": new_code, "name": new_name, "reportName": new_name,
                    "type": data.get("reportType", "0"), "template": 0, "delFlag": 0,
                    "viewCount": 0, "updateCount": 0, "submitForm": 0}
    overrides = {}
    for f in ["rows","cols","styles","merges","chartList","imgList","barcodeList","qrcodeList",
              "loopBlockList","hiddenCells","querySetting","printConfig","displayConfig",
              "fixedPrintHeadRows","fixedPrintTailRows","dbexps","dicts","area","background"]:
        v = sheet.get(f)
        if v is not None:
            overrides[f] = v

    session = Session(base_url, token)
    session.request("/save", base_save(new_id, designer_obj, **overrides))
    print(f"复制成功! 新报表: {new_id}  名称: {new_name}")
    print(f"  设计器: {base_url}/index/{new_id}")


# ── 更新函数（供 import 使用）────────────────────────────────────────

def update_colors(session, report_id, colors, chart_type_filter=None):
    """更新图表配色。colors: list of hex colors。"""
    designer, design = get_report(session, report_id)
    for ch in design.get("chartList", []):
        ct = ch.get("extData", {}).get("chartType", "")
        if chart_type_filter and chart_type_filter not in ct:
            continue
        config = json.loads(ch["config"]) if isinstance(ch.get("config"), str) else ch.get("config", {})
        if "color" in config:
            config["color"] = colors
        ch["config"] = json.dumps(config, ensure_ascii=False)
    session.request("/save", base_save(report_id, designer,
        rows=design["rows"], cols=design["cols"], styles=design["styles"],
        merges=design["merges"], chartList=design.get("chartList", [])))
    print(f"配色更新成功: {report_id}")


def update_legend(session, report_id, legend_updates, chart_index=0):
    """更新图例配置。legend_updates: dict 如 {"show": True, "orient": "horizontal"}。"""
    designer, design = get_report(session, report_id)
    charts = design.get("chartList", [])
    if chart_index < len(charts):
        config = json.loads(charts[chart_index]["config"]) if isinstance(charts[chart_index].get("config"), str) else charts[chart_index].get("config", {})
        config.setdefault("legend", {}).update(legend_updates)
        charts[chart_index]["config"] = json.dumps(config, ensure_ascii=False)
    session.request("/save", base_save(report_id, designer,
        rows=design["rows"], cols=design["cols"], styles=design["styles"],
        merges=design["merges"], chartList=charts))
    print(f"图例更新成功: {report_id}")


def update_label(session, report_id, label_config, chart_index=0):
    """更新标签配置。"""
    designer, design = get_report(session, report_id)
    charts = design.get("chartList", [])
    if chart_index < len(charts):
        config = json.loads(charts[chart_index]["config"]) if isinstance(charts[chart_index].get("config"), str) else charts[chart_index].get("config", {})
        if "series" in config:
            for s in config["series"]:
                s["label"] = label_config
        charts[chart_index]["config"] = json.dumps(config, ensure_ascii=False)
    session.request("/save", base_save(report_id, designer,
        rows=design["rows"], cols=design["cols"], styles=design["styles"],
        merges=design["merges"], chartList=charts))
    print(f"标签更新成功: {report_id}")


def upload_image(session, file_path):
    """上传图片，返回服务端路径。"""
    with open(file_path, "rb") as f:
        resp = session._s.post(f"{session.base_url}/upload/image",
                               files={"file": (os.path.basename(file_path), f)})
    resp.raise_for_status()
    result = resp.json()
    if result.get("success"):
        path = result["result"]
        print(f"上传成功: {path}")
        return path
    raise RuntimeError(f"上传失败: {result.get('message')}")


# ── CLI ──────────────────────────────────────────────────────────────

def _parse_db_cfg():
    """从环境变量或默认值获取 DB 配置。"""
    return {"host": os.environ.get("DB_HOST", "<db_host>"),
            "port": int(os.environ.get("DB_PORT", "3306")),
            "user": os.environ.get("DB_USER", "root"),
            "password": os.environ.get("DB_PASS", "root"),
            "database": os.environ.get("DB_NAME", "jeecg-boot")}


def main():
    p = argparse.ArgumentParser(description="积木报表工具")
    p.add_argument("--base-url", default=os.environ.get("JMREPORT_URL", "<api_base>"))
    p.add_argument("--token", default=os.environ.get("JMREPORT_TOKEN", ""))
    sub = p.add_subparsers(dest="cmd")

    ls = sub.add_parser("list", help="列出报表")
    ls.add_argument("-k", "--keyword", default="")
    ls.add_argument("-n", "--limit", type=int, default=20)

    dt = sub.add_parser("detail", help="查看报表详情")
    dt.add_argument("report_id")

    dl = sub.add_parser("delete", help="删除报表")
    dl.add_argument("report_id")

    cp = sub.add_parser("copy", help="复制报表")
    cp.add_argument("report_id")
    cp.add_argument("new_name")

    args = p.parse_args()
    if args.cmd == "list":
        list_reports(args.base_url, args.token, _parse_db_cfg(), args.keyword, args.limit)
    elif args.cmd == "detail":
        show_detail(args.base_url, args.token, args.report_id)
    elif args.cmd == "delete":
        delete_report(args.base_url, args.token, args.report_id)
    elif args.cmd == "copy":
        copy_report(args.base_url, args.token, args.report_id, args.new_name)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
