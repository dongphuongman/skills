"""
积木报表布局构建器 (jimureport_creator)

提供主题配色、表格/图表布局构建函数，供内联 heredoc 脚本 import 调用：
    from jimureport_creator import THEMES, get_theme, build_styles, build_cols,
                                   build_table_rows, build_chart_rows, build_echarts_config

也可作为独立 CLI 工具直接创建/编辑报表（通过 config.json 驱动）：
    python jimureport_creator.py --api-base <URL> --token <TOKEN> --config <config.json>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
config.json 示例（创建）:
{
    "action":     "create",
    "reportName": "登录日志统计报表",
    "theme":      "green",
    "pageSize":   10,
    "datasets": [
        {
            "dbCode":    "login_detail",
            "dbChName":  "登录日志明细",
            "dbDynSql":  "SELECT username, ip FROM sys_log WHERE log_type=1",
            "isPage":    "1"
        },
        {
            "dbCode":    "ip_daily",
            "dbChName":  "每日IP统计",
            "dbDynSql":  "SELECT DATE_FORMAT(...) AS name, COUNT(*) AS value, '' AS type ...",
            "isPage":    "0",
            "forChart":  true
        }
    ],
    "layout": "chart_bottom",
    "table": {
        "datasetCode": "login_detail",
        "title":       "登录日志统计报表",
        "columns": [
            {"field": "username", "title": "用户名", "width": 100},
            {"field": "ip",       "title": "IP地址",  "width": 120}
        ]
    },
    "chart": {
        "datasetCode": "ip_daily",
        "chartType":   "line.smooth",
        "title":       "最近10日每日访问IP总数",
        "width":       "680",
        "height":      "350"
    }
}

layout 可选值：table_only | chart_only | chart_top | chart_bottom | chart_right
theme  可选值：blue | green | orange | purple | red  或  {"primary":"#xxx","title":"#xxx"}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import sys
import argparse

from jimureport_utils import (
    Session, gen_layer, parse_sql, save_db,
    make_designer, base_save, get_report, print_summary,
)

# Windows 控制台中文
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


# ── 主题配色 ─────────────────────────────────────────────────────────────

THEMES = {
    "blue":   {"primary": "#01b0f1", "title": "#333333", "chart": "#01b0f1", "area_rgba": "1,176,241"},
    "green":  {"primary": "#4CAF50", "title": "#333333", "chart": "#43A047", "area_rgba": "76,175,80"},
    "orange": {"primary": "#FF9800", "title": "#333333", "chart": "#F57C00", "area_rgba": "255,152,0"},
    "purple": {"primary": "#9C27B0", "title": "#333333", "chart": "#8E24AA", "area_rgba": "156,39,176"},
    "red":    {"primary": "#F44336", "title": "#333333", "chart": "#E53935", "area_rgba": "244,67,54"},
}

DEFAULT_CHART_COLORS = ["#5470c6", "#ee6666", "#91cc75", "#fac858", "#73c0de", "#3ba272", "#fc8452", "#9a60b4"]


def get_theme(config: dict) -> dict:
    """获取主题配色，支持预设名称或自定义对象。"""
    theme = config.get("theme", "blue")
    if isinstance(theme, dict):
        return {
            "primary":    theme.get("primary", "#01b0f1"),
            "title":      theme.get("title", "#333333"),
            "chart":      theme.get("chart", theme.get("primary", "#01b0f1")),
            "area_rgba":  theme.get("area_rgba", "1,176,241"),
        }
    return THEMES.get(theme, THEMES["blue"])


def build_styles(theme: dict) -> list:
    """根据主题生成标准 styles 列表（索引 0-5）。"""
    border = {"bottom": ["thin", "#d8d8d8"], "top": ["thin", "#d8d8d8"],
              "left":   ["thin", "#d8d8d8"], "right": ["thin", "#d8d8d8"]}
    return [
        {"border": border},                                                                    # 0 仅边框
        {"border": border, "align": "center"},                                                 # 1 边框+居中
        {"border": border, "align": "center", "valign": "middle"},                            # 2 数据行
        {"border": border, "align": "center", "valign": "middle", "bgcolor": theme["primary"]},              # 3
        {"border": border, "align": "center", "valign": "middle", "bgcolor": theme["primary"], "color": "#ffffff"},  # 4 表头
        {"align": "center", "valign": "middle", "font": {"bold": True, "size": 18}},          # 5 标题
    ]


# ── 布局构建 ─────────────────────────────────────────────────────────────

def _col_letter(idx: int) -> str:
    """列索引(1-based) → Excel列字母：1→B, 2→C（col 0 = A 留空）。"""
    return chr(ord("A") + idx)


def build_cols(columns: list) -> dict:
    """根据 columns 配置生成 cols 对象。"""
    cols: dict = {"len": 100}
    for i, col in enumerate(columns):
        if col.get("width"):
            cols[str(i + 1)] = {"width": col["width"]}
    return cols


def build_table_rows(
    table_config: dict,
    start_row: int = 1,
    title_style: int = 5,
    header_style: int = 4,
    data_style: int = 2,
) -> tuple[dict, list, int, dict]:
    """
    构造数据表格的 rows 和 merges。
    返回 (rows, merges, next_row, group_config)。

    columns 字段可选属性：
      group       True  → #{db.group(field)} 纵向分组
      funcname    "SUM" → 数据集聚合（SUM/COUNT/AVG）
      subtotalText      → 合计行标签，默认"合计"
      decimalPlaces     → 小数位数
    """
    rows: dict = {}
    merges: list = []
    columns = table_config.get("columns", [])
    ds_code  = table_config["datasetCode"]
    col_count = len(columns)
    row = start_row
    group_config: dict = {}

    # 标题行
    title = table_config.get("title")
    if title:
        rows[str(row)] = {"cells": {"0": {"text": title, "style": title_style,
                                          "merge": [0, col_count], "height": 50}}, "height": 50}
        ui_row = row + 1
        merges.append(f"A{ui_row}:{_col_letter(col_count)}{ui_row}")
        row += 1

    # 表头行
    rows[str(row)] = {"cells": {str(i + 1): {"text": col["title"], "style": header_style}
                                for i, col in enumerate(columns)}, "height": 34}
    row += 1

    # 数据绑定行
    data_cells: dict = {}
    for i, col in enumerate(columns):
        field = col["field"]
        cell: dict = {"style": data_style}
        if col.get("group"):
            cell["text"]         = f"#{{{ds_code}.group({field})}}"
            cell["aggregate"]    = "group"
            if "subtotalText" in col:
                cell["subtotal"]     = "groupField"
                cell["funcname"]     = "-1"
                cell["subtotalText"] = col["subtotalText"]
            if not group_config:
                group_config = {"isGroup": True, "groupField": f"{ds_code}.{field}"}
        elif col.get("funcname"):
            cell["text"]     = f"#{{{ds_code}.{field}}}"
            cell["subtotal"] = "-1"
            cell["funcname"] = col["funcname"]
            if col.get("decimalPlaces"):
                cell["decimalPlaces"] = col["decimalPlaces"]
        else:
            cell["text"] = f"#{{{ds_code}.{field}}}"
        data_cells[str(i + 1)] = cell

    rows[str(row)] = {"cells": data_cells}
    row += 1
    return rows, merges, row, group_config


def build_chart_rows(
    chart_config: dict,
    chart_db_id: str,
    theme: dict,
    start_row: int = 1,
    col_start: int = 1,
    col_end: int = 6,
    row_count: int = 1,
) -> tuple[dict, list, int]:
    """
    构造图表虚拟占位行和 chartList。
    返回 (rows, chart_list, next_row)。
    """
    layer_id = gen_layer()
    rows: dict = {}
    virtual_cell_range: list = []

    for r in range(start_row, start_row + row_count):
        rows[str(r)] = {"cells": {str(c): {"text": " ", "virtual": layer_id}
                                  for c in range(col_start, col_end + 1)}}
        for c in range(col_start, col_end + 1):
            virtual_cell_range.append([r, c])

    chart_type = chart_config.get("chartType", "bar.simple")
    chart_item = {
        "row":    start_row,
        "col":    col_start,
        "colspan": 0,
        "rowspan": 0,
        "width":  str(chart_config.get("width",  "650")),
        "height": str(chart_config.get("height", "350")),
        "config": json.dumps(build_echarts_config(chart_type, chart_config, theme), ensure_ascii=False),
        "url":    "",
        "extData": {
            "chartType": chart_type,
            "dataType":  chart_config.get("dataType", "sql"),
            "dataId":    chart_db_id,
            "dbCode":    chart_config["datasetCode"],
            "axisX":     "name",
            "axisY":     "value",
            "series":    "type",
            "xText":     "",
            "yText":     "",
            "apiStatus": "1",
        },
        "layer_id":         layer_id,
        "offsetX":          0,
        "offsetY":          0,
        "backgroud":        {"enabled": False, "color": "#fff", "image": ""},
        "virtualCellRange": virtual_cell_range,
    }
    return rows, [chart_item], start_row + row_count


def build_echarts_config(chart_type: str, chart_config: dict, theme: dict) -> dict:
    """根据图表类型构造最小 ECharts 配置。"""
    title_text = chart_config.get("title", "")
    colors     = chart_config.get("colors", [theme["chart"]] + DEFAULT_CHART_COLORS)
    area_rgba  = theme.get("area_rgba", "1,176,241")

    if chart_type.startswith("pie"):
        radius = ["40%", "70%"] if "doughnut" in chart_type else "70%"
        if "rose" in chart_type:
            radius = [20, "70%"]
        return {
            "title":   {"text": title_text, "left": "center", "textStyle": {"fontSize": 16}},
            "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)",
                        "textStyle": {"color": "#fff", "fontSize": 14}},
            "legend":  {"orient": "vertical", "left": "left", "top": "middle"},
            "series":  [{"type": "pie", "radius": radius, "center": ["50%", "45%"],
                         "avoidLabelOverlap": True,
                         "itemStyle": {"borderRadius": 6, "borderColor": "#fff", "borderWidth": 2},
                         "label": {"show": True, "formatter": "{b}: {c} ({d}%)", "fontSize": 14},
                         "emphasis": {"label": {"show": True, "fontSize": 18, "fontWeight": "bold"}},
                         "data": [],
                         "roseType": "area" if "rose" in chart_type else None}],
            "color": colors,
        }
    if chart_type.startswith("bar"):
        is_h = "horizontal" in chart_type
        return {
            "title":   {"text": title_text, "left": "center"},
            "tooltip": {"trigger": "axis"},
            "legend":  {"bottom": 0},
            "xAxis":   [{"type": "value" if is_h else "category", "data": []}],
            "yAxis":   [{"type": "category" if is_h else "value",  "data": []}],
            "series":  [{"type": "bar", "data": [], "itemStyle": {"color": colors[0]}}],
            "color":   colors,
        }
    if chart_type.startswith("line"):
        smooth = "smooth" in chart_type
        return {
            "title":   {"text": title_text, "left": "center",
                        "textStyle": {"fontSize": 16, "color": theme["title"]}},
            "grid":    {"left": 60, "top": 60, "right": 40, "bottom": 60},
            "tooltip": {"show": True, "trigger": "axis"},
            "xAxis":   [{"type": "category", "data": []}],
            "yAxis":   [{"type": "value", "minInterval": 1}],
            "series":  [{"type": "line", "data": [], "smooth": smooth,
                         "lineStyle": {"width": 3, "color": theme["chart"]},
                         "itemStyle": {"color": theme["chart"]},
                         "areaStyle": {"color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                                                  "colorStops": [
                                                      {"offset": 0, "color": f"rgba({area_rgba},0.3)"},
                                                      {"offset": 1, "color": f"rgba({area_rgba},0.05)"},
                                                  ]}}}],
            "color": colors,
        }
    if chart_type.startswith("gauge"):
        return {"title": {"text": title_text, "left": "center"},
                "tooltip": {"formatter": "{b}: {c}"},
                "series": [{"type": "gauge", "data": [], "detail": {"formatter": "{value}"}}]}
    if chart_type.startswith("radar"):
        return {"title": {"text": title_text, "left": "center"}, "tooltip": {},
                "legend": {"bottom": 0}, "radar": {"indicator": []},
                "series": [{"type": "radar", "data": []}], "color": colors}
    if chart_type.startswith("funnel"):
        return {"title": {"text": title_text, "left": "center"},
                "tooltip": {"trigger": "item", "formatter": "{b}: {c}"},
                "legend": {"bottom": 0},
                "series": [{"type": "funnel", "data": [], "left": "10%", "width": "80%"}],
                "color": colors}
    if chart_type == "mixed.linebar":
        return {"title": {"text": title_text, "left": "center"},
                "tooltip": {"trigger": "axis"}, "legend": {"bottom": 0},
                "xAxis": [{"type": "category", "data": []}],
                "yAxis": [{"type": "value"}],
                "series": [{"type": "bar",  "data": []},
                           {"type": "line", "data": [], "smooth": True}],
                "color": colors}
    # fallback
    return {"title": {"text": title_text, "left": "center"}, "tooltip": {},
            "series": [{"type": "bar", "data": []}], "color": colors}


# ── 主流程（CLI 驱动） ────────────────────────────────────────────────────

def create_report(session: Session, config: dict) -> str | None:
    """创建新报表，返回 report_id。"""
    report_name = config["reportName"]
    theme  = get_theme(config)
    styles = build_styles(theme)
    print(f"\n{'=' * 50}\n创建积木报表: {report_name}\n{'=' * 50}")

    # Step 1: 创建空报表，取服务端 ID
    r = session.request("/save", base_save("", make_designer("", report_name)))
    report_id = r["result"]["id"]
    designer  = make_designer(report_id, report_name)
    print(f"  report_id={report_id}")

    # Step 2: 解析并保存数据集（支持 SQL / JSON）
    print("\n[1/3] 保存数据集...")
    dataset_ids: dict = {}
    for ds in config.get("datasets", []):
        db_code  = ds["dbCode"]
        db_type  = ds.get("dbType", "0")  # "0"=SQL, "3"=JSON

        if db_type == "3":
            # ── JSON 数据集 ──
            json_data = ds.get("jsonData", [])
            fl = ds.get("fieldList", [])
            # 简写支持：fieldList 可以是 [{"fieldName":"x","fieldText":"X"},...]
            # 也可以是 [["x","X"], ...] 简写格式
            if fl and isinstance(fl[0], (list, tuple)):
                fl = [{"fieldName":f,"fieldText":t,"widgetType":"String","orderNum":i,
                       "tableIndex":0,"extJson":"","dictCode":""} for i,(f,t) in enumerate(fl)]
            save_body = {
                "izSharedSource": 0, "jimuReportId": report_id,
                "dbCode": db_code, "dbChName": ds.get("dbChName", db_code),
                "dbType": "3", "dbSource": "", "isList": ds.get("isList", "1"),
                "isPage": ds.get("isPage", "0"), "dbDynSql": "",
                "jsonData": json.dumps({"data": json_data}, ensure_ascii=False),
                "apiConvert": "", "fieldList": fl, "paramList": ds.get("paramList", []),
            }
            resp = session.request("/saveDb", save_body)
            ds_id = resp["result"]["id"]
            print(f"  [{db_code}] JSON数据集 OK  id={ds_id}  records={len(json_data)}")
        else:
            # ── SQL 数据集 ──
            sql = ds.get("dbDynSql", "")
            print(f"  解析 [{db_code}]: {sql[:60]}{'...' if len(sql) > 60 else ''}")
            fl = parse_sql(session, sql, ds.get("dbSource", ""))
            for f in fl:
                if f["fieldName"] in ds.get("fieldTextMap", {}):
                    f["fieldText"] = ds["fieldTextMap"][f["fieldName"]]
            ds_id = save_db(session, report_id, db_code,
                            ds.get("dbChName", db_code), sql, fl,
                            is_page=ds.get("isPage", "1"))
            print(f"  [{db_code}] SQL数据集 OK  id={ds_id}")

        dataset_ids[db_code] = ds_id

    # Step 3: 构造布局
    print("\n[2/3] 构造报表布局...")
    layout       = config.get("layout", "table_only")
    table_config = config.get("table")
    chart_config = config.get("chart")
    all_rows: dict = {"len": 200}
    all_merges: list = []
    chart_list: list = []
    group_config: dict = {}
    col_count = len(table_config["columns"]) if table_config else 6

    def _add_chart(start: int, c_start: int = 1, c_end: int = None):
        nonlocal chart_list
        c_end = c_end or col_count
        c_db_id = dataset_ids.get(chart_config["datasetCode"], "")
        c_rows, cl, next_r = build_chart_rows(chart_config, c_db_id, theme, start, c_start, c_end)
        all_rows.update(c_rows)
        chart_list = cl
        return next_r

    if layout == "chart_top" and chart_config and table_config:
        next_row = _add_chart(1)
        all_rows[str(next_row)] = {"cells": {}, "height": 10}
        t_rows, t_merges, _, group_config = build_table_rows(table_config, next_row + 1)
        all_rows.update(t_rows); all_merges.extend(t_merges)
        print(f"  布局: 图表在上 + 数据表")

    elif layout == "chart_bottom" and chart_config and table_config:
        t_rows, t_merges, next_row, group_config = build_table_rows(table_config)
        all_rows.update(t_rows); all_merges.extend(t_merges)
        page_size = config.get("pageSize", 10)
        chart_start = (next_row - 1) + page_size + config.get("gap", 1)
        _add_chart(chart_start)
        all_rows[str(chart_start + page_size + 3)] = {"cells": {"1": {"text": " "}}}
        print(f"  布局: 数据表 + 图表在下")

    elif layout == "chart_right" and chart_config and table_config:
        t_rows, t_merges, _, group_config = build_table_rows(table_config)
        all_rows.update(t_rows); all_merges.extend(t_merges)
        c_start = col_count + 2
        c_rows, chart_list, _ = build_chart_rows(
            chart_config, dataset_ids.get(chart_config["datasetCode"], ""),
            theme, 1, c_start, c_start + 5)
        for k, v in c_rows.items():
            if k in all_rows and k != "len":
                all_rows[k]["cells"].update(v["cells"])
            else:
                all_rows[k] = v
        print(f"  布局: 数据表在左 + 图表在右")

    elif layout == "chart_only" and chart_config:
        _add_chart(1, 1, 6)
        print(f"  布局: 仅图表")

    elif table_config:
        t_rows, t_merges, _, group_config = build_table_rows(table_config)
        all_rows.update(t_rows); all_merges.extend(t_merges)
        print(f"  布局: 仅数据表")

    else:
        print("  错误: 未配置 table 或 chart"); return None

    # 自定义 rows/merges 覆盖（复杂表头场景：跳过 build_table_rows，直接传完整 rows）
    if "customRows" in config:
        all_rows = config["customRows"]
        all_merges = config.get("customMerges", [])
        chart_list = config.get("customChartList", chart_list)
        gf = config.get("groupField")
        if gf:
            group_config = {"isGroup": True, "groupField": gf}
        print(f"  布局: 自定义 rows（{len(all_rows)} 行, {len(all_merges)} 合并）")

    # 自定义 styles 覆盖
    if "customStyles" in config:
        styles = config["customStyles"]

    # 自定义 cols 覆盖
    if "customCols" in config:
        cols = config["customCols"]
    else:
        cols = build_cols(table_config["columns"]) if table_config else {"len": 100}
    total_w = sum(v["width"] for v in cols.values() if isinstance(v, dict) and "width" in v)

    # Step 4: 保存完整报表
    print("\n[3/3] 保存报表设计...")
    session.request("/save", base_save(
        report_id, designer,
        rows=all_rows, cols=cols, styles=styles, merges=all_merges,
        chartList=chart_list,
        dataRectWidth=total_w or 700,
        **({"isGroup": True, "groupField": group_config["groupField"]} if group_config else {}),
    ))

    print_summary(report_id, report_name, session.base_url, "")
    return report_id


def edit_report(session: Session, config: dict) -> str | None:
    """编辑已有报表（GET → 改 → save）。"""
    report_id = config["reportId"]
    print(f"\n{'=' * 50}\n编辑积木报表: {report_id}\n{'=' * 50}")

    designer, design = get_report(session, report_id)
    report_name = config.get("reportName", designer.get("name", ""))
    theme  = get_theme(config)
    mods   = config.get("modifications", {})

    # 修改样式
    if "theme" in config:
        design["styles"] = build_styles(theme)

    # 修改图表配色
    if mods.get("updateChartTheme"):
        for chart in design.get("chartList", []):
            ec = json.loads(chart["config"])
            ct = chart.get("extData", {}).get("chartType", "")
            chart["config"] = json.dumps(
                build_echarts_config(ct, {"title": ec.get("title", {}).get("text", ""),
                                          "datasetCode": chart.get("extData", {}).get("dbCode", "")},
                                     theme), ensure_ascii=False)

    # 修改 merges / rows
    if "merges" in mods:
        design["merges"] = mods["merges"]
    for k, v in mods.get("rows", {}).items():
        design["rows"][k] = v

    session.request("/save", base_save(
        report_id, designer,
        rows=design["rows"], cols=design["cols"],
        styles=design["styles"], merges=design["merges"],
        chartList=design.get("chartList", []),
        isGroup=design.get("isGroup", False),
        groupField=design.get("groupField", ""),
    ))
    print_summary(report_id, report_name, session.base_url, "")
    return report_id


def main():
    parser = argparse.ArgumentParser(description="积木报表创建/编辑工具")
    parser.add_argument("--api-base", required=True, help="JeecgBoot 后端地址，如 http://192.168.x.x:8085")
    parser.add_argument("--token",    required=True, help="X-Access-Token")
    parser.add_argument("--config",   required=True, help="配置文件路径 (JSON)")
    args = parser.parse_args()

    base = args.api_base.rstrip("/")
    if not base.endswith("/jmreport"):
        base += "/jmreport"
    session = Session(base, args.token)

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    action = config.get("action", "create")
    if action == "create":
        create_report(session, config)
    elif action == "edit":
        edit_report(session, config)
    else:
        print(f"未知操作类型: {action}"); sys.exit(1)


if __name__ == "__main__":
    main()
