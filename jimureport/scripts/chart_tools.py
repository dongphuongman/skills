#!/usr/bin/env python3
"""
chart_tools.py — 积木报表图表工具（追加图表/修改图表类型）

用法：
  python chart_tools.py change-type <报表ID> <新chartType>   # 修改图表类型
  python chart_tools.py add <报表ID> --chart-type bar.simple  # 追加图表

常用 chartType：
  bar.simple / bar.multi / bar.stack / bar.horizontal / bar.multi.horizontal
  line.simple / line.smooth / pie.simple / pie.ring / gauge.simple
"""

import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))

from jimureport_utils import Session, get_report, base_save, gen_layer

HORIZONTAL_TYPES = {"bar.horizontal", "bar.multi.horizontal", "bar.stack.horizontal", "bar.negative"}


def swap_axes(config, to_horizontal):
    """纵向 ↔ 横向时互换 xAxis/yAxis。"""
    old_x, old_y = config.get("xAxis", {}), config.get("yAxis", {})
    if to_horizontal:
        config["yAxis"] = {"show": True, "type": "category", "data": old_x.get("data", []),
                           "axisLabel": old_x.get("axisLabel", {}), "axisLine": old_x.get("axisLine", {}),
                           "splitLine": {"show": False}, "axisTick": old_x.get("axisTick", {"show": True})}
        config["xAxis"] = {"show": True, "axisLabel": old_y.get("axisLabel", {}),
                           "axisLine": old_y.get("axisLine", {}), "splitLine": old_y.get("splitLine", {})}
        for s in config.get("series", []):
            if isinstance(s.get("label"), dict): s["label"]["position"] = "right"
    else:
        config["xAxis"] = {"show": True, "type": "category", "data": old_y.get("data", []),
                           "axisLabel": old_y.get("axisLabel", {}), "axisLine": old_y.get("axisLine", {}),
                           "splitLine": {"show": False}, "axisTick": old_y.get("axisTick", {"show": True})}
        config["yAxis"] = {"show": True, "axisLabel": old_x.get("axisLabel", {}),
                           "axisLine": old_x.get("axisLine", {}), "splitLine": old_x.get("splitLine", {})}
        for s in config.get("series", []):
            if isinstance(s.get("label"), dict): s["label"]["position"] = "top"


def change_chart_type(base_url, token, report_id, new_type, chart_index=0):
    """修改已有图表的 chartType（自动处理轴向切换）。"""
    session = Session(base_url, token)
    designer, design = get_report(session, report_id)
    charts = design.get("chartList", [])
    if not charts:
        print("报表没有图表组件"); return

    chart = charts[chart_index]
    ext = chart.get("extData", {})
    old_type = ext.get("chartType", "")
    ext["chartType"] = new_type

    config = json.loads(chart["config"]) if isinstance(chart.get("config"), str) else chart.get("config", {})
    if (old_type in HORIZONTAL_TYPES) != (new_type in HORIZONTAL_TYPES):
        swap_axes(config, new_type in HORIZONTAL_TYPES)

    chart["config"] = json.dumps(config, ensure_ascii=False)
    session.request("/save", base_save(report_id, designer,
        rows=design["rows"], cols=design["cols"], styles=design["styles"],
        merges=design["merges"], chartList=charts))
    print(f"图表类型已从 {old_type} 改为 {new_type}")
    print(f"  预览: {base_url}/view/{report_id}?token={token}")


def add_chart(base_url, token, report_id, chart_type="bar.simple",
              db_code="", data_id="", axis_x="name", axis_y="value",
              width="650", height="380"):
    """向已有报表追加图表。"""
    session = Session(base_url, token)
    designer, design = get_report(session, report_id)

    # 找最大行号 + 1
    rows = design.get("rows", {})
    max_row = max((int(k) for k in rows if k.isdigit()), default=0) + 1
    layer_id = gen_layer()

    rows[str(max_row)] = {"cells": {str(c): {"text": " ", "virtual": layer_id} for c in range(1, 7)}}
    virtual_range = [[max_row, c] for c in range(1, 7)]

    new_chart = {
        "row": max_row, "col": 1, "colspan": 0, "rowspan": 0,
        "width": str(width), "height": str(height),
        "config": json.dumps({"color": ["#5470c6","#91cc75","#fac858","#ee6666","#73c0de"]}),
        "url": "",
        "extData": {"chartType": chart_type, "dataType": "sql", "dataId": data_id,
                    "dbCode": db_code, "axisX": axis_x, "axisY": axis_y,
                    "series": "", "apiStatus": "1"},
        "layer_id": layer_id, "offsetX": 0, "offsetY": 0,
        "backgroud": {"enabled": False, "color": "#fff", "image": ""},
        "virtualCellRange": virtual_range,
    }

    charts = design.get("chartList", [])
    charts.append(new_chart)
    session.request("/save", base_save(report_id, designer,
        rows=rows, cols=design["cols"], styles=design["styles"],
        merges=design["merges"], chartList=charts))
    print(f"已追加 {chart_type} 图表到报表 {report_id}")


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="积木报表图表工具")
    p.add_argument("--base-url", default=os.environ.get("JMREPORT_URL", "<api_base>"))
    p.add_argument("--token", default=os.environ.get("JMREPORT_TOKEN", ""))
    sub = p.add_subparsers(dest="cmd")

    ct = sub.add_parser("change-type", help="修改图表类型")
    ct.add_argument("report_id")
    ct.add_argument("new_type")
    ct.add_argument("--index", type=int, default=0)

    ad = sub.add_parser("add", help="追加图表")
    ad.add_argument("report_id")
    ad.add_argument("--chart-type", default="bar.simple")
    ad.add_argument("--db-code", default="")
    ad.add_argument("--data-id", default="")

    args = p.parse_args()
    if args.cmd == "change-type":
        change_chart_type(args.base_url, args.token, args.report_id, args.new_type, args.index)
    elif args.cmd == "add":
        add_chart(args.base_url, args.token, args.report_id, args.chart_type, args.db_code, args.data_id)
    else:
        p.print_help()

if __name__ == "__main__":
    main()
