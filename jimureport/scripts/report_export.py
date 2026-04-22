#!/usr/bin/env python3
"""
report_export.py — 积木报表导出/分享/导入 合并工具

用法：
  python report_export.py share --name 报表名 [--validity 1] [--lock 0]
  python report_export.py export <report_id> [--format pdf] [--output ./out]
  python report_export.py import-excel <xlsx_path> [--name 报表名]
"""

import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))

import requests
from urllib.parse import quote
from jimureport_utils import Session, gen_code, make_designer, base_save

VALIDITY_MAP = {"永久": "1", "7天": "2", "1天": "3", "1": "1", "2": "2", "3": "3"}


# ── 分享 ─────────────────────────────────────────────────────────────

def share_report(base_url, token, name, validity="1", lock_status="0", lock_pwd="", verify="1", index=None):
    """根据名称查询报表并创建分享链接。"""
    session = Session(base_url, token)
    encoded = quote(name)
    resp = session.get(f"/query/report/folder?pageNo=1&pageSize=50&reportType=&name={encoded}&token={token}")
    records = resp.get("result", {}).get("records", [])
    if not records:
        print(f"未找到包含「{name}」的报表")
        return

    if len(records) == 1:
        target = records[0]
    elif index:
        target = records[index - 1]
    else:
        print(f"找到 {len(records)} 个报表，请用 --index N 指定：")
        for i, r in enumerate(records, 1):
            print(f"  [{i}] {r['name']}  (ID: {r['id']})")
        return

    result = session.request("/share/addAndEdit", {
        "id": "", "reportId": target["id"], "previewUrl": "", "previewLock": lock_pwd or ("1234" if lock_status == "1" else ""),
        "status": "0", "termOfValidity": validity, "previewLockStatus": lock_status, "verifyShareToken": verify,
    }).get("result", {})

    base_host = base_url.replace("/jmreport", "")
    share_url = f"{base_host}{result.get('previewUrl', '')}"
    print(f"分享成功: {target['name']}")
    print(f"  链接: {share_url}")
    if lock_status == "1":
        print(f"  密码: {result.get('previewLock', lock_pwd)}")


# ── 导出 ─────────────────────────────────────────────────────────────

def export_report(base_url, token, report_id, fmt="pdf", output_dir="."):
    """导出报表为 PDF/Excel/Word。"""
    fmt_map = {"pdf": "pdf", "excel": "excel", "word": "word"}
    if fmt not in fmt_map:
        print(f"不支持的格式: {fmt}，可选: pdf/excel/word")
        return

    sess = requests.Session()
    sess.trust_env = False
    sess.headers.update({"X-Access-Token": token})

    url = f"{base_url}/exportPdf?reportId={report_id}" if fmt == "pdf" else \
          f"{base_url}/exportXls?reportId={report_id}" if fmt == "excel" else \
          f"{base_url}/exportWord?reportId={report_id}"

    resp = sess.get(url, stream=True)
    resp.raise_for_status()

    ext = {"pdf": ".pdf", "excel": ".xlsx", "word": ".docx"}[fmt]
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{report_id}{ext}")
    with open(path, "wb") as f:
        for chunk in resp.iter_content(8192):
            f.write(chunk)
    print(f"导出成功: {path}")


# ── 导入 Excel ──────────────────────────────────────────────────────

def import_excel(base_url, token, xlsx_path, name=None):
    """上传 Excel 文件导入为积木报表。"""
    session = Session(base_url, token)
    if not name:
        name = os.path.splitext(os.path.basename(xlsx_path))[0]

    with open(xlsx_path, "rb") as f:
        resp = session._s.post(f"{base_url}/importExcel", files={"file": (os.path.basename(xlsx_path), f)})
    resp.raise_for_status()
    result = resp.json()
    if not result.get("success"):
        print(f"导入失败: {result.get('message')}")
        return

    parsed = result["result"]
    save_resp = session.request("/save", base_save("", make_designer("", name)))
    report_id = save_resp["result"]["id"]

    overrides = {}
    for k in ["rows", "cols", "styles", "merges"]:
        if k in parsed:
            overrides[k] = parsed[k]
    session.request("/save", base_save(report_id, make_designer(report_id, name), **overrides))
    print(f"导入成功: {name} (ID: {report_id})")
    print(f"  设计器: {base_url}/index/{report_id}")


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="积木报表导出/分享/导入工具")
    p.add_argument("--base-url", default=os.environ.get("JMREPORT_URL", "<api_base>"))
    p.add_argument("--token", default=os.environ.get("JMREPORT_TOKEN", ""))
    sub = p.add_subparsers(dest="cmd")

    sh = sub.add_parser("share", help="创建分享链接")
    sh.add_argument("--name", required=True)
    sh.add_argument("--validity", default="1")
    sh.add_argument("--lock", default="0")
    sh.add_argument("--password", default="")
    sh.add_argument("--index", type=int, default=None)

    ex = sub.add_parser("export", help="导出 PDF/Excel/Word")
    ex.add_argument("report_id")
    ex.add_argument("--format", default="pdf", choices=["pdf", "excel", "word"])
    ex.add_argument("--output", default=".")

    im = sub.add_parser("import-excel", help="导入 Excel 模板")
    im.add_argument("xlsx_path")
    im.add_argument("--name", default=None)

    args = p.parse_args()
    if args.cmd == "share":
        share_report(args.base_url, args.token, args.name, args.validity, args.lock, args.password, index=args.index)
    elif args.cmd == "export":
        export_report(args.base_url, args.token, args.report_id, args.format, args.output)
    elif args.cmd == "import-excel":
        import_excel(args.base_url, args.token, args.xlsx_path, args.name)
    else:
        p.print_help()

if __name__ == "__main__":
    main()
