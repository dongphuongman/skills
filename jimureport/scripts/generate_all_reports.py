# -*- coding: utf-8 -*-
"""
生成全部报表 — 25 种图表 + SQL/API/JSON 三种数据集一键生成

设计目标：AI 零手写模板，端到端 ~30 秒完成。

用法：
    python generate_all_reports.py \
        --base-url <api_base> \
        --token <X-Access-Token> \
        --name "全图表测试"

默认参数已内置（见 argparse）。需要修改 MySQL/YApi 凭证直接改下方常量或传参。

图表分配：
  SQL  × 12：bar.simple/horizontal/multi/stack/stack.horizontal/multi.horizontal,
             line.multi, pie.simple/rose, mixed.linebar, gauge.simple/simple180
  API  ×  2：line.simple(mock), pie.doughnut(mock)
  JSON × 9 ：bar.negative, scatter.simple/bubble, funnel.simple/pyramid,
             radar.basic/custom, pictorial.spirits, map.scatter
             （数据内嵌 config，api_status=0，无外部数据集绑定）
  不绑  ×  2：map.simple, graph.simple
"""

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import pymysql

# Windows 中文控制台
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from jimureport_utils import (
    Session, gen_id, gen_layer, save_db, parse_sql,
    make_designer, base_save, col_letter, report_urls,
    parallel_save_dbs, parallel_fill_charts, chart_entry,
)

# ============================================================
# 配置
# ============================================================
TABLE_NAME = "chart_demo_all"

MOCK_LINE_PATH = "/chart_api_line"
MOCK_PIE_PATH  = "/chart_api_pie"

# 单元格共享对象（避免 JSON 展开时引用冲突）
def _title(text, color="#c23531"):
    return {"show": True, "text": text, "left": "left", "top": "5",
            "textStyle": {"fontSize": 16, "fontWeight": "bolder", "color": color}}

def _legend():
    return {"show": True, "top": "top", "left": "center", "orient": "horizontal",
            "data": [], "padding": [25, 20, 25, 10],
            "textStyle": {"color": "#333", "fontSize": 12}}

def _grid():
    return {"left": 60, "top": 60, "right": 30, "bottom": 40}

def _tip():
    return {"show": True, "textStyle": {"color": "#fff", "fontSize": 14}}

def _tip_axis():
    return {**_tip(), "trigger": "axis", "axisPointer": {"type": "shadow"},
            "appendToBody": True, "confine": True}


# ============================================================
# MySQL: 建 chart_demo 表 + 插数据
# ============================================================
def bootstrap_mysql(host, port, db, user, pwd):
    print(f"▶ 连接 MySQL {host}:{port}/{db}")
    conn = pymysql.connect(host=host, port=port, database=db,
                           user=user, password=pwd, charset="utf8mb4", autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
            cur.execute(f"""
                CREATE TABLE {TABLE_NAME} (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(32) NOT NULL,
                    value DECIMAL(12,2) NOT NULL,
                    type VARCHAR(32) NOT NULL,
                    sort_no INT NOT NULL
                ) COMMENT='全图表测试数据'
            """)
            months = ["一月", "二月", "三月", "四月", "五月", "六月",
                      "七月", "八月", "九月", "十月", "十一月", "十二月"]
            values_sales = [120, 200, 150, 80, 70, 110, 130, 180, 220, 190, 240, 300]
            values_cost  = [80, 130, 100, 50, 40, 75, 90, 120, 150, 130, 170, 210]
            rows = []
            for i, m in enumerate(months):
                rows.append((m, values_sales[i], "销售额", i + 1))
                rows.append((m, values_cost[i],  "成本",   i + 1))
            cur.executemany(
                f"INSERT INTO {TABLE_NAME}(name,value,type,sort_no) VALUES(%s,%s,%s,%s)",
                rows,
            )
        print(f"  ✓ 建表 + 插 {len(rows)} 行完成")
    finally:
        conn.close()


# ============================================================
# YApi mock：并行创建 2 个接口
# ============================================================
def bootstrap_mocks():
    from yapi_mock import init_yapi, create_mock
    init_yapi()
    months = ["一月","二月","三月","四月","五月","六月","七月","八月","九月","十月","十一月","十二月"]
    vals   = [120,200,150,80,70,110,130,180,220,190,240,300]
    pie_data = [{"name": "苹果", "value": 120}, {"name": "香蕉", "value": 80},
                {"name": "樱桃", "value": 150}, {"name": "葡萄", "value": 60},
                {"name": "芒果", "value": 200}]
    # 串行（YApi 登录态共享，create_mock 内部 2 次 HTTP，并行收益不大）
    line_url = create_mock(MOCK_LINE_PATH, "全图表-折线API",
                           [{"name": m, "value": v} for m, v in zip(months, vals)])
    pie_url  = create_mock(MOCK_PIE_PATH,  "全图表-饼图API", pie_data)
    return line_url, pie_url


# ============================================================
# ECharts 模板生成器（25 种）
# ============================================================
# 通用: title=图表标题, color=主色
def tpl_bar_simple(title):
    return {"title": _title(title), "grid": _grid(), "tooltip": _tip_axis(),
            "xAxis": {"show": True, "type": "category", "data": []},
            "yAxis": {"show": True, "type": "value"},
            "series": [{"name": "", "type": "bar", "data": [], "barWidth": 35,
                        "itemStyle": {"barBorderRadius": 0, "color": "#5470c6"}}]}

def tpl_bar_horizontal(title):
    return {"title": _title(title), "grid": _grid(), "tooltip": _tip_axis(),
            "yAxis": {"show": True, "type": "category", "data": []},
            "xAxis": {"show": True, "type": "value"},
            "series": [{"type": "bar", "name": "", "data": [], "barWidth": 18,
                        "itemStyle": {"color": "#91cc75", "barBorderRadius": 0},
                        "label": {"show": True, "position": "right",
                                  "textStyle": {"color": "#333", "fontSize": 12}}}]}

def tpl_bar_multi(title):
    return {"title": _title(title), "legend": _legend(), "grid": _grid(), "tooltip": _tip_axis(),
            "xAxis": {"show": True, "type": "category", "data": []},
            "yAxis": {"show": True, "type": "value"},
            "series": [{"type": "bar", "data": [], "barWidth": 15,
                        "itemStyle": {"color": "", "barBorderRadius": 0}}]}

def tpl_bar_stack(title):
    return {"title": _title(title), "legend": _legend(), "grid": _grid(), "tooltip": _tip_axis(),
            "xAxis": {"show": True, "type": "category", "data": []},
            "yAxis": {"show": True, "type": "value"},
            "series": [{"type": "bar", "name": "", "stack": "tot", "data": [], "barWidth": 15,
                        "itemStyle": {"color": "", "barBorderRadius": 0}}]}

def tpl_bar_stack_horizontal(title):
    return {"title": _title(title), "legend": _legend(), "grid": _grid(), "tooltip": _tip_axis(),
            "yAxis": {"show": True, "type": "category", "data": []},
            "xAxis": {"show": True, "type": "value"},
            "series": [{"type": "bar", "name": "", "stack": "tot", "data": [], "barWidth": 15,
                        "itemStyle": {"color": "", "barBorderRadius": 0}}]}

def tpl_bar_multi_horizontal(title):
    return {"title": _title(title), "legend": _legend(), "grid": _grid(), "tooltip": _tip_axis(),
            "yAxis": {"show": True, "type": "category", "data": []},
            "xAxis": {"show": True, "type": "value"},
            "series": [{"type": "bar", "data": [], "barWidth": 12,
                        "itemStyle": {"color": "", "barBorderRadius": 0},
                        "label": {"show": True, "position": "right"}}]}

def tpl_bar_negative(title):
    return {"title": _title(title), "legend": _legend(), "grid": _grid(), "tooltip": _tip_axis(),
            "yAxis": {"show": True, "type": "category",
                      "data": ["一月","二月","三月","四月","五月","六月"]},
            "xAxis": {"show": True, "type": "value", "splitLine": {"show": True}},
            "series": [
                {"name": "正值", "type": "bar", "stack": "tot",
                 "data": [120, 80, 150, 60, 90, 180], "barWidth": 22,
                 "itemStyle": {"color": "#ee6666", "barBorderRadius": 0},
                 "label": {"show": True, "position": "right"}},
                {"name": "负值", "type": "bar", "stack": "tot",
                 "data": [-40, -30, -70, -50, -20, -60], "barWidth": 22,
                 "itemStyle": {"color": "#5470c6", "barBorderRadius": 0},
                 "label": {"show": True, "position": "left"}},
            ]}

def tpl_line_simple(title):
    return {"title": _title(title), "grid": _grid(), "tooltip": _tip_axis(),
            "xAxis": {"show": True, "type": "category", "data": []},
            "yAxis": {"show": True, "type": "value"},
            "series": [{"type": "line", "name": "", "data": [],
                        "smooth": True, "showSymbol": True, "symbolSize": 5,
                        "lineStyle": {"width": 2}, "itemStyle": {"color": "#c43632"}}]}

def tpl_line_multi(title):
    return {"title": _title(title), "legend": _legend(), "grid": _grid(), "tooltip": _tip_axis(),
            "xAxis": {"show": True, "type": "category", "boundaryGap": True, "data": []},
            "yAxis": {"show": True, "type": "value"},
            "series": [{"type": "line", "data": [], "smooth": False, "showSymbol": True,
                        "symbolSize": 5, "lineStyle": {"width": 2},
                        "itemStyle": {"color": "", "barBorderRadius": 0}}]}

def tpl_pie_simple(title):
    return {"title": _title(title), "legend": _legend(),
            "tooltip": {**_tip(), "trigger": "item", "formatter": "{a} <br/>{b} : {c} ({d}%)"},
            "series": [{"type": "pie", "name": "", "radius": "55%", "center": [320, 190],
                        "isRose": False, "isRadius": False, "roseType": "",
                        "minAngle": 0, "autoSort": False, "notCount": False, "data": [],
                        "label": {"show": True, "position": "outside",
                                  "textStyle": {"fontSize": 12, "fontWeight": "bolder"}}}]}

def tpl_pie_doughnut(title):
    cfg = tpl_pie_simple(title)
    cfg["series"][0]["isRadius"] = True
    cfg["series"][0]["radius"]   = ["45%", "65%"]
    return cfg

def tpl_pie_rose(title):
    cfg = tpl_pie_simple(title)
    cfg["series"][0]["isRose"]   = True
    cfg["series"][0]["roseType"] = "radius"
    return cfg

def tpl_mixed_linebar(title):
    return {"chartType": "linebar",
            "title": _title(title), "legend": _legend(), "grid": _grid(),
            "tooltip": {**_tip(), "trigger": "axis",
                        "axisPointer": {"type": "cross", "crossStyle": {"color": "#999"}},
                        "appendToBody": True, "confine": True},
            "xAxis": {"show": True, "type": "category", "data": [],
                      "axisPointer": {"type": "shadow"}},
            "yAxis": [{"show": True, "name": "销售", "type": "value"},
                      {"show": True, "name": "成本", "type": "value"}],
            "series": [
                {"type": "bar", "data": [], "barWidth": 15,
                 "itemStyle": {"color": "", "barBorderRadius": 0}},
                {"type": "line", "data": [], "yAxisIndex": 1, "smooth": False,
                 "showSymbol": True, "symbolSize": 5, "lineStyle": {"width": 2},
                 "itemStyle": {"color": ""}},
            ]}

def tpl_gauge_simple(title):
    return {"title": _title(title),
            "tooltip": {**_tip(), "formatter": "{b} : {c}"},
            "series": [{"type": "gauge", "name": "指标",
                        "center": [320, 200], "radius": "75%",
                        "pointer": {"show": True},
                        "data": [{"name": "完成率", "value": 75}],
                        "itemStyle": {"color": "#63869E"},
                        "axisLine": {"lineStyle": {"width": 22,
                                                   "color": [[0.2, "#91c7ae"], [0.8, "#63869E"], [1, "#C23531"]]}},
                        "axisTick":  {"length": 10, "lineStyle": {"color": "#fff"}},
                        "splitLine": {"length": 25, "lineStyle": {"color": "#fff", "width": 3}},
                        "axisLabel": {"show": True, "color": "auto",
                                      "textStyle": {"fontSize": 10}},
                        "title":  {"show": True, "textStyle": {"color": "#000", "fontSize": 16}},
                        "detail": {"formatter": "{value}%",
                                   "textStyle": {"color": "rgba(0,0,0,1)", "fontSize": 22}}}]}

def tpl_gauge_simple180(title):
    cfg = tpl_gauge_simple(title)
    s = cfg["series"][0]
    s.pop("radius", None)
    s["startAngle"] = 190
    s["endAngle"]   = -10
    return cfg

def tpl_scatter_simple(title):
    return {"title": _title(title), "grid": _grid(),
            "tooltip": {**_tip(), "formatter": "{c}"},
            "xAxis": {"show": True, "name": "X", "type": "value"},
            "yAxis": {"show": True, "name": "Y", "type": "value"},
            "series": [{"type": "scatter", "symbolSize": 18,
                        "data": [[10,20],[15,35],[20,25],[25,50],[30,40],[35,60],
                                 [40,52],[45,70],[50,63],[55,80]],
                        "itemStyle": {"color": "#C23531", "opacity": 0.9}}]}

def tpl_scatter_bubble(title):
    return {"title": _title(title), "legend": _legend(), "grid": _grid(), "tooltip": _tip(),
            "xAxis": {"show": True, "name": "X", "type": "value"},
            "yAxis": {"show": True, "name": "Y", "type": "value"},
            "series": [
                {"type": "scatter", "name": "系列A", "symbolSize": 22,
                 "data": [[10,20],[20,40],[30,30],[40,55],[50,48]],
                 "itemStyle": {"color": {"type": "radial", "r": 0.8,
                                         "colorStops": [{"offset": 0, "color": "#E7727C"},
                                                        {"offset": 1, "color": "#D7291F"}]},
                               "shadowBlur": 10, "shadowColor": "rgba(25,100,150,0.5)",
                               "shadowOffsetY": 5}},
                {"type": "scatter", "name": "系列B", "symbolSize": 20,
                 "data": [[12,28],[22,38],[32,25],[42,48],[52,60]],
                 "itemStyle": {"color": {"type": "radial", "r": 0.8,
                                         "colorStops": [{"offset": 0, "color": "#91cc75"},
                                                        {"offset": 1, "color": "#4caf50"}]}}},
            ]}

def tpl_funnel_simple(title):
    return {"title": _title(title), "legend": _legend(),
            "tooltip": {**_tip(), "trigger": "item", "formatter": "{b} : {c}"},
            "series": [{"type": "funnel", "name": "漏斗图",
                        "orient": "vertical", "sort": "descending",
                        "left": "10%", "width": "80%", "top": 60, "bottom": 40, "gap": 2,
                        "data": [{"name": "访问", "value": 100, "itemStyle": {"color": None}},
                                 {"name": "咨询", "value": 80,  "itemStyle": {"color": None}},
                                 {"name": "订单", "value": 60,  "itemStyle": {"color": None}},
                                 {"name": "付款", "value": 40,  "itemStyle": {"color": None}},
                                 {"name": "复购", "value": 20,  "itemStyle": {"color": None}}],
                        "itemStyle": {"borderColor": "#fff", "borderWidth": 1},
                        "label": {"show": True, "position": "inside",
                                  "textStyle": {"fontSize": 14, "color": "#ffffff"}}}]}

def tpl_funnel_pyramid(title):
    cfg = tpl_funnel_simple(title)
    cfg["series"][0]["sort"] = "ascending"
    cfg["series"][0]["name"] = "金字塔图"
    return cfg

def tpl_radar_basic(title):
    return {"title": _title(title), "legend": {**_legend(), "data": ["综合评分"]},
            "tooltip": _tip(),
            "radar": [{"shape": "polygon", "center": [320, 200], "radius": 90,
                       "indicator": [
                           {"name": "销售", "max": 100}, {"name": "管理", "max": 100},
                           {"name": "信息技术", "max": 100}, {"name": "客服", "max": 100},
                           {"name": "研发", "max": 100}, {"name": "市场", "max": 100}],
                       "name": {"formatter": "{value}",
                                "textStyle": {"color": "#72ACD1", "fontSize": 12}},
                       "axisLine":  {"lineStyle": {"color": "gray", "opacity": 0.5}},
                       "splitLine": {"lineStyle": {"color": "gray", "opacity": 0.5}}}],
            "series": [{"type": "radar",
                        "data": [{"name": "综合评分",
                                  "value": [80, 70, 85, 60, 90, 75], "lineStyle": {}}]}]}

def tpl_radar_custom(title):
    cfg = tpl_radar_basic(title)
    cfg["radar"][0].update({
        "shape": "circle", "startAngle": 90, "splitNumber": 4,
        "splitArea": {"areaStyle": {
            "color": ["rgba(114,172,209,0.2)", "rgba(114,172,209,0.4)",
                      "rgba(114,172,209,0.6)", "rgba(114,172,209,0.8)",
                      "rgba(114,172,209,1)"],
            "shadowBlur": 10, "shadowColor": "rgba(0,0,0,0.3)"}}
    })
    return cfg

def tpl_pictorial_spirits(title):
    return {"title": _title(title), "grid": _grid(),
            "tooltip": _tip_axis(),
            "yAxis": {"show": True, "type": "category",
                      "data": ["Q1", "Q2", "Q3", "Q4"],
                      "axisTick": {"show": False},
                      "axisLabel": {"textStyle": {"color": "#999", "fontSize": 14}}},
            "xAxis": {"show": True, "type": "value", "max": 1500},
            "series": [{"type": "pictorialBar",
                        "data": [800, 1200, 950, 1400],
                        "symbol": "roundRect", "symbolSize": 20,
                        "symbolRepeat": "fixed", "symbolMargin": "5%!",
                        "symbolBoundingData": 1500, "symbolClip": True,
                        "secondOpacity": 0.2,
                        "itemStyle": {"color": "#5470c6"},
                        "label": {"show": True, "position": "right",
                                  "textStyle": {"color": "black", "fontSize": 14,
                                                "fontWeight": "bolder"}}}]}

def tpl_map_simple(title):
    return {"chartType": "map",
            "title": _title(title),
            "tooltip": {"show": True, "trigger": "item",
                        "textStyle": {"color": "#fff", "fontSize": 13},
                        "backgroundColor": "rgba(50,50,50,0.7)",
                        "padding": [5, 4], "borderWidth": 0},
            "geo": {"map": "100000", "mapCode": [100000],
                    "mapName": "中华人民共和国", "mapLevel": "0", "mapType": "0",
                    "layoutCenter": ["50%", "50%"], "layoutSize": 520,
                    "zoom": 0.8, "roam": True, "regions": [],
                    "label": {"show": False, "color": "#fff", "fontSize": 12},
                    "itemStyle": {"areaColor": "#224C66", "borderColor": "#0692a4", "borderWidth": 1},
                    "emphasis": {"itemStyle": {"areaColor": "#0b1c2d"},
                                 "label": {"color": "#fff"}}},
            "series": [{"name": "地图", "coordinateSystem": "geo"}],
            "color": ["#c23531","#2f4554","#61a0a8","#d48265","#91c7ae","#749f83"]}

def tpl_map_scatter(title):
    cfg = tpl_map_simple(title)
    cfg["series"] = [{"type": "scatter", "name": "value", "coordinateSystem": "geo",
                      "encode": {"value": [2]},
                      "symbolSize": 18,
                      "itemStyle": {"color": "#F4E925"},
                      "label": {"show": False, "formatter": "{b}", "position": "right"},
                      "emphasis": {"label": {"show": True}},
                      "data": [
                          {"name": "北京", "value": [116.405,39.905, 120]},
                          {"name": "上海", "value": [121.473,31.230, 200]},
                          {"name": "广州", "value": [113.264,23.129, 150]},
                          {"name": "成都", "value": [104.065,30.659, 80]},
                          {"name": "西安", "value": [108.941,34.342,  70]},
                          {"name": "武汉", "value": [114.305,30.593, 110]},
                      ]}]
    return cfg

def tpl_graph_simple(title):
    return {"title": _title(title),
            "legend": {"padding": [25,20,25,10], "data": ["部门","员工"],
                       "top": "top", "orient": "horizontal", "left": "right",
                       "show": True, "textStyle": {"color": "#333", "fontSize": 12}},
            "tooltip": _tip(),
            "color": ["#c23531","#2f4554","#61a0a8","#d48265","#91c7ae"],
            "series": [{"type": "graph", "name": "关系图",
                        "layout": "circular", "center": [320, 180],
                        "lineStyle": {"curveness": 0.3, "color": "source"},
                        "label": {"show": True, "position": "right",
                                  "textStyle": {"color": "#333", "fontSize": 12}},
                        "data": [
                            {"name": "总经办", "category": 0, "value": 28},
                            {"name": "研发部", "category": 0, "value": 22},
                            {"name": "销售部", "category": 0, "value": 18},
                            {"name": "张三",  "category": 1, "value": 8},
                            {"name": "李四",  "category": 1, "value": 10},
                            {"name": "王五",  "category": 1, "value": 12},
                        ],
                        "links": [
                            {"source": "总经办", "target": "研发部"},
                            {"source": "总经办", "target": "销售部"},
                            {"source": "研发部", "target": "张三"},
                            {"source": "研发部", "target": "李四"},
                            {"source": "销售部", "target": "王五"},
                        ],
                        "categories": [
                            {"name": "部门", "itemStyle": {"color": ""}},
                            {"name": "员工", "itemStyle": {"color": ""}},
                        ]}]}


# ============================================================
# 图表定义（元数据驱动）
# ============================================================
# 每项：(标题, chartType, series, 数据集种类, SQL/mock_key/None, 模板函数)
SQL_SINGLE = ("SELECT name, CAST(value AS DECIMAL(12,2)) AS value FROM " + TABLE_NAME +
              " WHERE type='销售额' ORDER BY sort_no")
SQL_MULTI  = ("SELECT name, CAST(value AS DECIMAL(12,2)) AS value, type FROM " + TABLE_NAME +
              " ORDER BY sort_no, type")
SQL_GAUGE  = "SELECT '完成率' AS name, 75 AS value"

CHARTS = [
    # 标题,            chartType,             series,  source种类, payload,        模板
    ("普通柱形图",      "bar.simple",           "",     "sql",   SQL_SINGLE, tpl_bar_simple),
    ("横向柱形图",      "bar.horizontal",       "",     "sql",   SQL_SINGLE, tpl_bar_horizontal),
    ("多数据对比柱形图","bar.multi",            "type", "sql",   SQL_MULTI,  tpl_bar_multi),
    ("堆叠柱形图",      "bar.stack",            "type", "sql",   SQL_MULTI,  tpl_bar_stack),
    ("堆叠条形图",      "bar.stack.horizontal", "type", "sql",   SQL_MULTI,  tpl_bar_stack_horizontal),
    ("多数据条形柱状图","bar.multi.horizontal", "type", "sql",   SQL_MULTI,  tpl_bar_multi_horizontal),
    ("普通折线图",      "line.simple",          "",     "api",   "line",     tpl_line_simple),
    ("多数据折线图",    "line.multi",           "type", "sql",   SQL_MULTI,  tpl_line_multi),
    ("普通饼图",        "pie.simple",           "",     "sql",   SQL_SINGLE, tpl_pie_simple),
    ("环状饼图",        "pie.doughnut",         "",     "api",   "pie",      tpl_pie_doughnut),
    ("玫瑰饼图",        "pie.rose",             "",     "sql",   SQL_SINGLE, tpl_pie_rose),
    ("折柱混合图",      "mixed.linebar",        "type", "sql",   SQL_MULTI,  tpl_mixed_linebar),
    ("360仪表盘",       "gauge.simple",         "",     "sql",   SQL_GAUGE,  tpl_gauge_simple),
    ("180仪表盘",       "gauge.simple180",      "",     "sql",   SQL_GAUGE,  tpl_gauge_simple180),
    ("正负条形图",      "bar.negative",         "type", "json",  None,       tpl_bar_negative),
    # 散点图 src="none"：ECharts series.data 要求 [[x,y],...] 二维数组，
    # jimureport JSON数据集渲染器只做 axis_x→categories / axis_y→values 一维映射，
    # 无法自动配对成二维数组，用静态 config 数据最简洁。
    ("散点图",          "scatter.simple",       "",     "none",  None,       tpl_scatter_simple),
    ("气泡散点图",      "scatter.bubble",       "",     "none",  None,       tpl_scatter_bubble),
    ("漏斗图",          "funnel.simple",        "",     "json",  None,       tpl_funnel_simple),
    ("金字塔图",        "funnel.pyramid",       "",     "json",  None,       tpl_funnel_pyramid),
    # 雷达图 src="none"：ECharts 要求 series.data=[{name, value:[v1,v2,...]}]，
    # value 是所有维度指标值的数组（一条记录包含全部维度），
    # jimureport 渲染器按行映射 {name,value}，无法还原多维数组，用静态 config 数据。
    ("多边形雷达图",    "radar.basic",          "",     "none",  None,       tpl_radar_basic),
    ("圆形雷达图",      "radar.custom",         "",     "none",  None,       tpl_radar_custom),
    ("象形柱图",        "pictorial.spirits",    "",     "json",  None,       tpl_pictorial_spirits),
    ("区域地图",        "map.simple",           "",     "none",  None,       tpl_map_simple),
    ("点地图",          "map.scatter",          "",     "json",  None,       tpl_map_scatter),
    ("关系图",          "graph.simple",         "",     "none",  None,       tpl_graph_simple),
]


# ============================================================
# JSON 数据集静态数据（tabular，供 db_type="3" 使用）
# ============================================================
_JSON_CHART_DATA: dict[str, dict] = {
    "bar.negative": {
        "records": (
            [{"name": m, "value": v, "type": "正值"} for m, v in
             zip(["一月","二月","三月","四月","五月","六月"], [120, 80, 150, 60, 90, 180])] +
            [{"name": m, "value": v, "type": "负值"} for m, v in
             zip(["一月","二月","三月","四月","五月","六月"], [-40,-30,-70,-50,-20,-60])]
        ),
        "axis_x": "name", "axis_y": "value", "series": "type",
    },
    "funnel.simple": {
        "records": [{"name": n, "value": v} for n, v in
                    [("访问",100),("咨询",80),("订单",60),("付款",40),("复购",20)]],
        "axis_x": "name", "axis_y": "value", "series": "",
    },
    "funnel.pyramid": {
        "records": [{"name": n, "value": v} for n, v in
                    [("访问",100),("咨询",80),("订单",60),("付款",40),("复购",20)]],
        "axis_x": "name", "axis_y": "value", "series": "",
    },
    "pictorial.spirits": {
        "records": [{"name": n, "value": v} for n, v in
                    [("Q1",800),("Q2",1200),("Q3",950),("Q4",1400)]],
        "axis_x": "name", "axis_y": "value", "series": "",
    },
    "map.scatter": {
        "records": [
            {"name": "北京", "lng": 116.405, "lat": 39.905, "value": 120},
            {"name": "上海", "lng": 121.473, "lat": 31.230, "value": 200},
            {"name": "广州", "lng": 113.264, "lat": 23.129, "value": 150},
            {"name": "成都", "lng": 104.065, "lat": 30.659, "value":  80},
            {"name": "西安", "lng": 108.941, "lat": 34.342, "value":  70},
            {"name": "武汉", "lng": 114.305, "lat": 30.593, "value": 110},
        ],
        "axis_x": "name", "axis_y": "value", "series": "",
    },
}


def _json_field_list(records: list[dict]) -> list[dict]:
    if not records:
        return []
    _type_map = {str: "String", int: "Integer", float: "Double"}
    return [
        {"fieldName": k, "fieldText": k, "isShow": "1",
         "fieldType": _type_map.get(type(records[0][k]), "String"),
         "dictCode": "", "dictTable": "", "dictText": ""}
        for k in records[0].keys()
    ]


# ============================================================
# 主流程
# ============================================================
def build_report(session, report_name, report_id, line_mock_url, pie_mock_url):
    # 1. 为 SQL / API / JSON 图表建数据集
    datasets = []
    for idx, (title, ct, series, src, payload, _tpl) in enumerate(CHARTS):
        if src == "sql":
            datasets.append({"idx": idx, "kind": "sql",
                             "db_code": f"ds_{idx:02d}_{ct.replace('.', '_')}",
                             "db_name": title, "sql": payload})
        elif src == "api":
            url = line_mock_url if payload == "line" else pie_mock_url
            datasets.append({"idx": idx, "kind": "api",
                             "db_code": f"ds_{idx:02d}_{ct.replace('.', '_')}",
                             "db_name": title, "api_url": url})
        elif src == "json":
            jd = _JSON_CHART_DATA[ct]
            datasets.append({"idx": idx, "kind": "json",
                             "db_code": f"ds_{idx:02d}_{ct.replace('.', '_')}",
                             "db_name": title,
                             "records": jd["records"],
                             "axis_x": jd["axis_x"],
                             "axis_y": jd["axis_y"],
                             "series_field": jd["series"],
                             "api_status": jd.get("api_status", "1")})

    # 2. 并行解析 SQL / API 字段，JSON 字段本地构造
    print(f"▶ 并行解析字段（SQL {sum(1 for d in datasets if d['kind']=='sql')} + "
          f"API {sum(1 for d in datasets if d['kind']=='api')} + "
          f"JSON {sum(1 for d in datasets if d['kind']=='json')}）")
    def _parse(d):
        if d["kind"] == "sql":
            d["field_list"] = parse_sql(session, d["sql"])
        elif d["kind"] == "api":
            from jimureport_utils import parse_api
            d["field_list"] = parse_api(session, d["api_url"])
        else:  # json
            d["field_list"] = _json_field_list(d["records"])
        return d
    with ThreadPoolExecutor(max_workers=min(len(datasets), 10)) as ex:
        list(ex.map(_parse, datasets))

    # 3. 并行保存所有数据集
    print(f"▶ 并行保存 {len(datasets)} 个数据集")
    save_args = []
    for d in datasets:
        args = {"report_id": report_id, "db_code": d["db_code"],
                "db_name": d["db_name"], "field_list": d["field_list"],
                "is_list": "1", "is_page": "0"}
        if d["kind"] == "sql":
            args.update({"sql": d["sql"], "db_type": "0"})
        elif d["kind"] == "api":
            args.update({"sql": "", "db_type": "1", "api_url": d["api_url"]})
        else:  # json
            args.update({"sql": "", "db_type": "3",
                         "json_data": json.dumps({"data": d["records"]}, ensure_ascii=False)})
        save_args.append(args)
    # 串行避免 MySQL deadlock（jimu_report_db_field INSERT 并发冲突）
    db_ids = [save_db(session, **a) for a in save_args]
    for d, did in zip(datasets, db_ids):
        d["db_id"] = did

    ds_by_idx = {d["idx"]: d for d in datasets}

    # 4. 构造 chartList（每个图表放 2 列 × 一排），以 10 行为跨度
    print(f"▶ 构造 {len(CHARTS)} 个图表布局")
    COL_END = 14
    CHART_W, CHART_H = 6, 14
    ROW_STEP = 16

    chart_list = []
    rows_placeholders = []  # (row, col_start, col_end, layer_id)

    for i, (title, ct, series, src, payload, tpl) in enumerate(CHARTS):
        layer = gen_layer()
        cfg = tpl(title)

        # 布局：左列 col=1..7 / 右列 col=8..14
        grid_row = i // 2
        col_start = 1 if (i % 2 == 0) else 8
        col_end_c = col_start + CHART_W
        row_anchor = 2 + grid_row * ROW_STEP

        if src == "sql":
            d = ds_by_idx[i]
            chart = chart_entry(layer, d["db_id"], d["db_code"], ct, cfg,
                                row=row_anchor, col=col_start, col_end=col_end_c,
                                width="560", height="360",
                                axis_x="name", axis_y="value",
                                series=series, api_status="1", data_type="sql")
        elif src == "api":
            d = ds_by_idx[i]
            chart = chart_entry(layer, d["db_id"], d["db_code"], ct, cfg,
                                row=row_anchor, col=col_start, col_end=col_end_c,
                                width="560", height="360",
                                axis_x="name", axis_y="value",
                                series=series, api_status="1", data_type="api")
        elif src == "json":
            d = ds_by_idx[i]
            chart = chart_entry(layer, d["db_id"], d["db_code"], ct, cfg,
                                row=row_anchor, col=col_start, col_end=col_end_c,
                                width="560", height="360",
                                axis_x=d["axis_x"], axis_y=d["axis_y"],
                                series=d["series_field"], api_status="1", data_type="json")
        else:  # none — 不绑数据集
            chart = {
                "row": row_anchor, "col": col_start,
                "width": "560", "height": "360",
                "config": json.dumps(cfg, ensure_ascii=False), "url": "",
                "extData": {"chartId": layer, "id": layer, "chartType": ct},
                "layer_id": layer,
                "virtualCellRange": [[row_anchor, c] for c in range(col_start, col_end_c + 1)],
                "backgroud": {"enabled": False, "color": "#fff", "image": ""},
                "colspan": CHART_W + 1, "rowspan": CHART_H,
                "offsetX": 0, "offsetY": 0,
            }
        chart_list.append(chart)
        rows_placeholders.append((row_anchor, col_start, col_end_c, layer))

    # 5. rows / cols / styles / merges
    rows = {"len": 500}
    # 标题
    title_cells = {"1": {"merge": [0, COL_END - 1], "text": report_name, "style": 0}}
    for c in range(2, COL_END + 1):
        title_cells[str(c)] = {}
    rows["0"] = {"cells": title_cells, "height": 45}
    # 图表虚拟占位
    for r, c_s, c_e, layer in rows_placeholders:
        rows[str(r)] = {"cells": {str(c): {"text": " ", "virtual": layer}
                                   for c in range(c_s, c_e + 1)}}
    cols = {"0": {"width": 20},
            **{str(i): {"width": 80} for i in range(1, COL_END + 1)},
            "len": 100}
    styles = [{"align": "center", "valign": "middle",
               "font": {"size": 18, "bold": True}, "color": "#1677ff"}]
    merges = [f"B1:{col_letter(COL_END)}1"]

    # 6. 第一次 /save（创建报表 + chartList）
    print("▶ 第一次 /save（创建报表）")
    designer = make_designer(report_id, report_name)
    session.request("/save", base_save(report_id, designer,
                    rows=rows, cols=cols, styles=styles, merges=merges,
                    chartList=chart_list))

    # 7. 并行回填 SQL/API 图表数据
    print(f"▶ 并行回填 SQL/API 图表数据")
    parallel_fill_charts(session, chart_list)

    # 8. 最终 /save
    print("▶ 最终 /save（写入回填后的图表数据）")
    designer = make_designer(report_id, report_name)
    session.request("/save", base_save(report_id, designer,
                    rows=rows, cols=cols, styles=styles, merges=merges,
                    chartList=chart_list))


# ============================================================
# CLI 入口
# ============================================================
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="<api_base>")
    p.add_argument("--token",    default="<token>")
    p.add_argument("--tenant",   default="2")
    p.add_argument("--name",     default="全图表测试")
    p.add_argument("--mysql-host", default="<db_host>")
    p.add_argument("--mysql-port", type=int, default=3306)
    p.add_argument("--mysql-db",   default="jimureport-dev")
    p.add_argument("--mysql-user", default="root")
    p.add_argument("--mysql-pwd",  default="123456")
    p.add_argument("--skip-mysql", action="store_true",
                   help="跳过建表（表已存在时使用）")
    p.add_argument("--skip-mock",  action="store_true",
                   help="跳过创建 YApi mock（需手动传 --line-url --pie-url）")
    p.add_argument("--line-url",   default="")
    p.add_argument("--pie-url",    default="")
    args = p.parse_args()

    t0 = time.time()

    # ① MySQL 建表
    if not args.skip_mysql:
        bootstrap_mysql(args.mysql_host, args.mysql_port, args.mysql_db,
                        args.mysql_user, args.mysql_pwd)

    # ② YApi mock
    if args.skip_mock:
        line_url = args.line_url
        pie_url  = args.pie_url
        if not (line_url and pie_url):
            raise SystemExit("--skip-mock 必须同时提供 --line-url 和 --pie-url")
    else:
        print("▶ 创建 YApi mock 接口")
        line_url, pie_url = bootstrap_mocks()

    # ③ 创建报表
    session = Session(args.base_url, args.token)
    report_id = gen_id()
    build_report(session, args.name, report_id, line_url, pie_url)

    # ④ 输出
    preview, design = report_urls(report_id, args.base_url, args.token, args.tenant)
    elapsed = time.time() - t0
    print("\n" + "=" * 60)
    print(f"✓ 全图表测试报表创建成功（{elapsed:.1f}s）")
    print(f"  报表名:  {args.name}")
    print(f"  ID:      {report_id}")
    print(f"  图表数:  {len(CHARTS)} 个")
    print(f"  数据集:  SQL {sum(1 for c in CHARTS if c[3]=='sql')} / "
          f"API {sum(1 for c in CHARTS if c[3]=='api')} / "
          f"JSON {sum(1 for c in CHARTS if c[3]=='json')} / "
          f"不绑 {sum(1 for c in CHARTS if c[3]=='none')}")
    print(f"  预览:    {preview}")
    print(f"  设计器:  {design}")
    print("=" * 60)


if __name__ == "__main__":
    main()
