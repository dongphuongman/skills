# 已知坑点速查

遇到异常时先查此表。

## 什么该记录到坑点，什么不该

| 该记录 ✅ | 不该记录 ❌ |
|----------|-----------|
| API 接口字段名非预期（如 `paramName` 而非 `fieldName`）| 文档示例写错了（直接改文档即可） |
| 接口返回值路径非预期（如必须 `resp["result"]["id"]`）| 正常的配置规范（改写到 SKILL.md 规范章节） |
| 运行时才暴露的隐性错误（如 `{**bd}` 展开导致边框不生效）| 只要改文档就能避免的问题 |
| 引擎行为与直觉不符（如 `isPage:"1"` 分组导致合计不完整）| 正常业务规则（放 SKILL.md 对应说明） |
| 并发/顺序依赖导致的失败（如同秒 gen_code 重复）| — |

**判断标准：** 如果问题根源是"文档写错了"→ 改文档；如果根源是"API/引擎行为本身出乎意料"→ 记坑点。

---

| 坑 | 现象 | 解决 |
|----|------|------|
| dbCode 纯数字（所有数据集） | `#{1775721592817440.field}` 预览数据全空 | **所有类型数据集**（SQL/JSON/API）的 dbCode 均禁止纯数字；必须用字母开头的驼峰字符串如 `"schoolJf"`，禁止 `gen_code()` 直接作为 dbCode |
| dbCode 含保留关键词或特殊字符 | 数据集保存异常或绑定失败（如 `returnOrder` 含 `return`） | dbCode 只能用纯字母+数字的驼峰命名；**禁止含 `return`、`for`、`if`、`while` 等 JS/Java 保留字**；**禁止含下划线 `_`、连字符 `-`、点 `.` 等特殊字符**；正确示例：`thdMain`、`salesOrder`、`empInfo` |
| save 返回值取错路径 | `resp.get("id")` 返回 None，后续全部静默失败 | 正确路径：`resp["result"]["id"]` |
| 预览/设计器 URL 用 `?id=` | 页面可能加载但报表为空 | 正确格式：`/jmreport/view/{id}` 和 `/jmreport/index/{id}`（路径参数） |
| rows/cols 被 json.dumps | 设计器空白 | 只 dumps designerObj |
| gen_code() 同秒重复 | INSERT code 唯一键冲突 | 用毫秒+随机数：`str(time.time()*1000)+str(random.randint(100,999))`；多报表顺序创建时加 `time.sleep(2)` |
| save_db 之间加 sleep | 脚本慢 1~2 秒 | `save_db` 内部用 `gen_id()`（毫秒+随机），**不会重复**；同一报表的多个数据集之间**不需要 sleep**，直接顺序调用即可 |
| 只改报表展示配置也调 save_db | 多调了一次不必要的接口 | 修改 rpbar/样式/合并等**纯报表配置**时，不需要调 `save_db`；直接 `get_report` → 改配置 → `/save` 两步即可 |
| 修改数据集单个字段（如 isPage）用 save_db 全量重传 | 代码繁琐，需要重新填写所有参数 | 正确做法：`update_db(session, db_id, isPage="1")`；内部先 `/loadDbData/{dbId}` 取回原始数据，只改指定字段，原样回传 `/saveDb`（所有接口本身都很快，<0.1s）|
| 图表 linkIds 放顶层 | 钻取/联动无效 | 放 extData 内部 |
| 联动目标图表无默认值 | 初始页面图表空白 | paramList 必须设 paramValue |
| isPage:"1" + 分组 | 合并/合计不完整 | 分组报表数据集 isPage:"0" |
| bar.multi 用 apiStatus:"1" | 图表渲染异常 | 静态数据必须用 apiStatus:"0" |
| dbSource 传名称不传 ID | 数据源下拉不显示 | 先 getDataSourceByPage 查 ID |
| SQL 数据集 dbSource 留空 | 界面打开数据集看不出用的是哪个数据库/数据源 | SQL 数据集必须传 `dbSource` 数据源 ID（非空字符串）；从 memory 取或先调 getDataSourceByPage 查询 |
| getDataSourceByPage GET 签名校验失败 | `签名校验失败，参数有误！` | GET 签名接口必须先把 `token` 加入 params，再对完整 params（含 token）计算 X-Sign；`jimureport_utils.py` 的 `Session.request` 已修复：GET + need_sign 时先 `params["token"]=token` 再 `_compute_sign(params)` |
| executeSelectApi 调用方式 | POST + query string，不是 JSON body；result 直接是 fieldList 数组 | 用 `parse_api(session, url)` |
| 脚本走系统代理 | 连接失败 | Session 已封装 trust_env=False |
| paramValue 用图表字段名 | 图表钻取无值 | 用 name/value/seriesName |
| 诊断命令用 run_in_background | 用户等待输出超时 | 诊断/计时命令必须前台同步执行，禁止 run_in_background |
| 脚本多次并发启动 | 数据库连接池耗尽，报 `Could not open JDBC Connection for transaction` | 脚本只启动一次，用一次 `TaskOutput(block=true, timeout=30000)` 等结果；TaskOutput 超时后**不要重新启动脚本**，等原进程完成即可 |
| 修改已有报表用 `**design` | design 含 `name` 等字段冲突，图表消失 | 始终显式传 `rows=design['rows'], cols=design['cols'], styles=..., merges=..., chartList=...`，禁止 `**design` |
| 图表 extData.id 为 None | 预览图表不渲染/消失 | `extData` 中 `chartId` 和 `id` 必须同时赋值为 `layer_id`，不可缺一 |
| 只改 `color[]` 设置颜色 | 颜色不生效或不持久化 | 饼图改3处(data[i].itemStyle/label/colors[])，柱形图改2处(series[i].itemStyle/colors[])，`color[]` 不动 |
| cell 直接写 `align`/`font`/`valign` | 样式不生效（浏览器实测 2026-04-07） | 对齐+字体必须放入顶层 `styles[]` 数组，cell 用 `style` 整数索引引用；不能把 align/font/valign 直接写在 cell 对象上 |
| `color`（文字颜色）写在 `font` 内 | `font.color` 在某些 style 不生效，表头白字不显示 | `color` 必须在 style 顶层，与 `font`/`bgcolor` 同级：`{"font":{...}, "color":"#FFFFFF", "bgcolor":"..."}` |
| `merge` 不加 `merges` 顶层数组 | 合并区域在设计器显示为未合并 | cell 设 `merge:[rowSpan,colSpan]` 同时，**必须**在顶层 `merges` 加 `"B1:J1"` 等 Excel 范围字符串（UI 行号 = code 行号+1） |
| `merge` 与顶层 `merges` 列范围不一致 | 单元格合并只到部分列，右侧留空白（如收货地址未对齐） | cell `merge:[0,N]` 表示额外跨 N 列，顶层 `merges` 的结束列必须一致：`merge:[0,4]` → 起始列为C时应为 `"C?:G?"` 而非 `"C?:E?"`；**改 merge 必须同步核查 merges 字符串** |
| 用切片限制图表数据条数 | SQL LIMIT 或 Python 切片控制不稳定 | 图表 config 中设 `"dataFilter":{"filterCount":N}`，积木报表引擎会自动只显示前 N 条；SQL 不加 LIMIT |
| 象形图 symbol 图片 URL 拼错 | 图标看不到 | upload 返回 `message="jimureport/x.png"`；访问 URL = `BASE_URL + "/img/" + message`；symbol 写 `f"image://{BASE_URL}/img/{message}"` |
| 象形图开启补全用 `symbolClip` | 补全不生效 | 补全（背景虚影）用 `"double": True`，不是 `symbolClip` |
| 雷达图 series 传空字符串 | 系列属性"请选择"，legend 显示 undefined | SQL 里 `'' AS type` 只是占位，`chart_entry(series="type")` 仍必须填 `"type"` |
| 雷达图 legend.data 为空数组 | 图例显示空白方块 | `legend.data` 必须预填系列名列表，如 `["综合评分"]`；SQL动态数据集引擎不会自动填充 legend.data |
| 雷达图 SQL type 字段传空字符串 | 图例空白、tooltip 显示 series0 | 引擎用 type 字段值作为系列名；必须传实际名称如 `'综合评分' AS type`，且与 `legend.data` 和 `series[].data[].name` 三处保持一致 |
| 同一报表多图表垂直排列重叠 | 第二个图表盖在第一个上 | chart_entry rowspan 默认14但 height=420px 实际占≈17行；第二个图表的 row 必须 ≥ 第一个 row + ceil(height/行高) + 间距，保守估算：height=420 时第二图表 row = 第一图表 row + 20 |
| 表达式列写 `=` 开头 | 后端将文本当公式求值，显示计算结果而非表达式字符串 | 表达式说明列（col2）去掉 `=` 前缀，只写 `ABS(-88.5)` 而非 `=ABS(-88.5)` |
| `CEIL(n)` / `FLOOR(n)` 无结果 | JimuReport 内置函数不含 CEIL/FLOOR，只有 Aviator 的 `math.ceil/floor` 有效 | 去掉这两行；若需要向上/向下取整只能用 `math.ceil()`/`math.floor()` |
| `UPPER(#{field})` / `LOWER(#{field})` 无结果 | `#{field}` 替换后变成 `UPPER(Hello World)`（无引号），Aviator 解析失败；且绑定字段的行会随数据集展开重复多行 | 改用字符串字面量：`=UPPER('hello world')`；不要在 UPPER/LOWER 公式内使用 `#{}` 绑定 |
| get_report→删行→shift 后按硬编码行号修改 | 行号计算出错，改错了行 | 删行/移行后，按 col1 函数名（文本内容）匹配目标行，而非依赖行号索引 |
| rpbar 用 json.dumps 字符串 | 保存成功但预览工具条设置不生效 | rpbar 必须用 dict 对象，不能用 `json.dumps()`；字段名是 `rpbar`（不是 rqbar） |
| 单系列图表 series 传了 `"type"` | 预览时图表不自动加载，需手动点击"运行"按钮 | 单系列图表（pie/bar.simple/line.simple 等）`series` 必须传空字符串 `""`；`"type"` 仅用于多系列图表（bar.multi 等）且数据集中确实有该字段时才传 |
| get_report 对新报表失败 | 刚 /save 创建的报表调 get_report 返回 None | 改为从 create 响应手动构建 designer dict |
| customRows 仍需 datasetCode | build_table_rows 报 KeyError | 即使用 customRows，table 里也必须有 `"datasetCode":""` 占位 |
| report_tools.py 参数名 | 命令行报错 unrecognized arguments | 用 `--base-url`，不是 `--api-base` |
| MySQL Docker 中文乱码 | 中文以 latin1 存储损坏 | 必须加 `--default-character-set=utf8mb4` |
| FreeMarker 空值判断 | 条件不生效 | 用 `isNotEmpty(x)` 而非 `x??` 或 `x?has_content`；后两者无法过滤空串 `""` |
| 文本参数 widgetType | 控件渲染异常 | 应为 `"string"`，不是 `"text"` |
| LIKE 模糊查询写法 | 必须用 `LIKE CONCAT('%','${x}','%')`，不能用 `LIKE '%${x}%'`；后者 `${x}` 展开为 JDBC 占位符后嵌在字符串字面量里无法绑定 |
| 下拉控件配置 | 下拉单选：`widgetType:"String"` + `searchMode:4`；下拉多选：`widgetType:"String"` + `searchMode:3`；`widgetType` 不能用 `"sel_search"`，否则控件渲染异常 |
| loopTime 标题列范围含尾部空白列 | 标题偏窄，右侧留白，与内容区不对齐 | loopTime 分栏时若循环块末尾有间距列（如 col4=20px），第2张卡片复制后产生 col9（尾部空白）；**标题行的 merge 和 merges 不应包含该列**。正确范围：A1:I1（col0-col8），内容区 col0-col3+col4间距+col5-col8 = 820px 对齐；col9（尾部空白）排除在外 |
| 分版用 loopBlockList | 并列多数据集表格数据错乱/联动 | 分版场景禁止用 loopBlockList；正确做法：第一个表无标记（`#{}` 自然展开），右侧表单元格加 `zonedEdition:N`，顶层加 `zonedEditionList`（结构同 loopBlockList，含 db 字段），loopBlockList 留空 `[]` |
| 多系列图表（bar.multi/stack/line.multi等）series 为空数组或回填后丢失 itemStyle | 前端 `getSeriesItemStyle` 读 `seriesConfig[0].itemStyle` 崩溃，所有带 type 字段的图表全部空白 | ① **所有多系列图表** config 初始 `series` 必须提供至少一个带 `itemStyle` 的占位条目，禁止写 `"series":[]`；② fill_chart 多系列重建时强制补 itemStyle：先 `base_s=cfg["series"][0]`，重建后若缺 itemStyle 强制填入默认值 `{"color":"","barBorderRadius":0}`；③ 水平堆叠图（bar.stack.horizontal/bar.multi.horizontal）分类数据必须写到 `yAxis`，不能写 `xAxis`——用 `type=="category"` 判断而非 `"xAxis" in cfg` |
| 文件数据集图表 dataType 写成 "sql" | 运行时调 /qurestSql，报 "reportDb is null"，图表空白 | 文件数据集（dbType=5/6）的 chart_entry 必须传 `data_type="files"`；"sql" 只用于 MySQL SQL 数据集 |
| 文件数据集(dbType=5) fieldList 丢失 | 首次 `/saveDb`（无 id）不持久化 fieldList，UI「字段名」列全空，图表不渲染 | 拿到 db_id 后立即做第二次 `/saveDb`（payload 加 `"id": db_id`）；fieldList 条目必须带 `fieldNamePhysics` 才能正确写入 |
| save_db 重复创建数据集 | 不传 `db_id` 时每次都 INSERT 新记录，多次运行后报表内出现多个同名数据集；**更新时必须传 `db_id=<已有ID>`** |
| save_db 返回值误用 | `save_db()` 直接返回数据集 ID 字符串，不是 dict；错误用 `r["result"]["id"]` 会 TypeError | 直接用 `db_id = save_db(...)` |
| 主子表循环块用两个 loopBlock | 以为要分别配主表和子表各一条 loopBlockList → 无效，子表不展开 | **只有一个 loopBlockList，db=主表**；子表行（`#{sub.field}`）嵌入同一循环块模板，引擎靠 link 关联自动展开 |
| loopBlockList eri 设太大 | eri=35/36 等很大值 → 子表记录少时预览页出现大片空白 | eri 设为**模板内容末行 + 2~3 行缓冲**即可；引擎自动按数据量扩展，数据多不截断，数据少不留白 |
| `/link/saveAndEdit` 参数格式错误 | 用 `mainDbId/subDbId/paramList` → 关联不生效，子表数据不展开 | 正确格式：`reportId` + `mainReport/subReport`（dbCode别名）+ `parameter`（JSON字符串含 main/sub/subReport 数组）+ `linkType:"4"` |
| 主子表循环块列数不统一 | 主表标题跨 A-G（7列），子表只用 B-F（5列）→ 预览时子表比主表窄，视觉不对齐 | 主表和子表必须使用**完全相同的列范围**（如都用 col0-col5）；主表标题 `merge:[0,5]`，子表表头和数据行也铺满同样的列范围 |
| 条形码/二维码 | 用 `displayConfig` + 单元格 `display/config` 实现；详见 `references/chart-components.md` §4-6 和 `references/report-design.md` §7 |
| `python -c` 跑到后台 | 命令自动进入 background，输出丢失，反复轮询浪费时间 | 永远 Write .py 文件后 `python /path/to/file.py` 执行，禁止 `python -c` |
| JSON 数据集 `json_data` 传 list 或 dict 而非字符串 | `saveDb` 失败：`Cannot deserialize value of type java.lang.String from Object value`（传 dict）或保存异常（传 list） | `save_db(..., json_data=json.dumps({"data": raw_list}, ensure_ascii=False))`；`json_data` 参数是**JSON 字符串**，传 Python list 或 dict 均不行，必须 `json.dumps()` |
| 纵向分组+自定义排序读了无关文件 | 读 `misc-config.md`/`dataset-core.md` 浪费 30s+ 无收获 | 自定义排序场景只需读 `examples/vertical-group-custom-sort.md`，关键字段 `textOrders:"华北\|华南\|华东"` 加在分组单元格上即可；`misc-config` 无排序内容 |
| 预调外部 API 验证字段 | 网络请求慢或超时，白等 | 直接按用户提供的字段写脚本，不预调 API 验证 |
| Windows Python stdout GBK 编码 | `UnicodeEncodeError: 'gbk' codec` 导致脚本崩溃重试 | 每个脚本开头必须加：`import sys; sys.stdout.reconfigure(encoding='utf-8')` |
| 首次 save 后 sleep | `time.sleep()` 白白增加延迟 | 首次 `/save` 是同步请求，完成即可立即调 `save_db`，不需要任何 sleep |
| DB 凭证未知时猜测 | 连接失败→修改→重试，浪费多轮 | DB host/password 不确定时，写代码前先问用户，1 句话拿到信息比反复重试快得多 |
| DB 密码错误不立即问 | `Access denied` 后继续猜密码重试，耗费多轮 | 首次连接失败且密码来自记忆（可能过时），**立刻停下来问用户**，不要尝试其他密码 |
| 脚本执行失败后猜测数据库/数据源配置 | 数据源名称、库名、表名等猜错导致多次失败重试，产生脏数据或重复资源 | 脚本执行失败涉及数据库/数据源相关配置（数据源名称、库名、连接信息等）时，**立刻停下来问用户**，不要自行猜测其他值重试 |
| 工具函数签名靠记忆 | `make_designer(name)` / `save_db(dbSource=...)` 等写错，运行才发现，多轮重试 | 写主脚本前先 `python -c "from jimureport_utils import X; help(X)"` 确认所有关键函数签名，不依赖文档示例或记忆 |
| graph.simple 误配 extData | 绑定数据集/设 apiStatus/设 dataId/设 dataId1 导致图表不渲染 | extData 只需 `{"chartId": layer_id, "chartType": "graph.simple"}`；节点+边全部内嵌 config 的 series[0].data/links；virtualCellRange 只放一行锚点；**不需要任何数据集** |
| Session base_url 缺 /jmreport | `session.request("/save",...)` 实际请求 `BASE_URL/save` 返回 404 | `Session` 初始化必须传含 `/jmreport` 的完整路径：`http://host:port/jmreport` |
| report_urls 参数顺序写反 | 预览链接指向错误 id | 正确签名：`report_urls(report_id, base_url, token)`，id 在前，base_url 在后 |
| `report_urls` 返回值当 dict 用 | `TypeError: tuple indices must be integers or slices, not str`（如 `urls['preview']`） | `report_urls` 返回 **tuple**（preview_url, design_url），不是 dict；正确用法：`preview, design = report_urls(report_id, BASE_URL, TOKEN)` 或 `urls[0]`/`urls[1]` |
| 创建表达式报表前读多余文件 | 读 expressions.md + pitfalls.md + jimureport_utils.py = 多次 Read，超时 | 表达式报表：只需读 `references/expressions.md`（含全部函数）+ `references/pitfalls.md`，其余文件不用读；**严禁** grep/Read jimureport_utils.py 查函数签名，签名须熟记：`make_designer(report_id, name)`、`save_db(session, report_id, db_code, db_name, sql, field_list, *, db_type, is_list, is_page, json_data)`、`base_save(report_id, designer, **overrides)`、`report_urls(report_id, base_url, token)` |
| 导入 `JimuSession` / `JimuReportSession` 等 | `ImportError: cannot import name 'JimuReportSession'`，整个脚本挂掉 | 唯一正确写法：`from jimureport_utils import Session, gen_id, gen_layer, make_styles, base_save, save_db, make_designer, chart_entry, virtual_row, print_summary, get_report, report_urls, parallel_save_dbs, ensure_datasource, parse_and_save_dataset`；模块路径：`<skill_base_dir>\scripts\jimureport_utils.py` |
| 单报表误用首次占位 /save | 串行 `/save`（占位）→ `parse_sql` → `saveDb` → 最终 `/save`，多一次 ~0.5-2s HTTP | 推荐 3-step：`ensure_datasource` → `gen_id()` 预生成 report_id → `parse_and_save_dataset(orphan report_id OK)` → 最终 `/save` 首次创建；省掉占位 save。saveDb 对 orphan report_id 不会报错，后续 /save 以此 id 首次建报表时数据集自动绑定。 |
| DBSUM/DBAVERAGE/DBMIN/DBMAX 不出数 | cell 里写了 `=DBSUM(ds.field)` 但预览结果为空，无报错 | `base_save` 必须同时传 `dbexps=["=DBSUM(ds.field)",...]`，引擎才会执行；修改已有报表时用 `dbexps=design.get("dbexps",[])` 透传，否则已有 DBSUM 也会失效 |
| 工具库模块名写错 | `from jimureport_session import JimuReportSession` 或 `from report_builder import ...` 均报 ModuleNotFoundError | 正确导入：`from jimureport_utils import Session, gen_id, gen_code, save_db, make_designer, base_save` |
| /save 新建报表 result.id 为 null | `resp["result"]["id"]` 返回 None，无法构造预览链接 | 新建时用 `gen_id()` 预生成 report_id，保存成功后直接用该 ID；`rid = resp["result"].get("id") or report_id` |
| 报表存在性验证走错接口 | `queryById`/`reportList`/`queryReportList` 均 404 或无权限 | 最简验证：`curl http://BASE/jmreport/index/{id}` 返回 HTML 即表示报表存在 |
| 循环块 db 别名与 dbCode 不一致 | 单元格绑定 `#{emp.field}` 但 dbCode 是 `emp_xxx`，预览数据全空 | `DB_ALIAS` 必须等于完整 dbCode；单元格 `#{alias.field}`、`loopBlockList.db`、`displayConfig` 的 text 三处保持一致 |
| API 分页数据集缺少分页参数 | 报表预览不分页或字段解析失败 | `api_url` 末尾带 `?pageSize='${pageSize}'&pageNo='${pageNo}'`（固定格式），`param_list` 加两条 `searchFlag=0` 的分页参数，**必须设默认值** `pageSize="20"`、`pageNo="1"`，留空不生效 |
| 斜线表头 style 含 `valign`/`align` | 标签被垂直居中，合并单元格内产生大片空白，"地区"等标签错位 | 斜线表头（lineStart）的 style **只能有** `border + bgcolor + color`，**禁止加 `align`/`valign`**；否则标签定位失效 |
| 表格 styles 未加边框 | 预览效果无边框，表格难以辨认 | 创建任何表格报表时，所有 style 对象**默认必须加边框**：`"border": {"bottom": ["thin","#BFBFBF"], "top": ["thin","#BFBFBF"], "left": ["thin","#BFBFBF"], "right": ["thin","#BFBFBF"]}`；标题行可用深色边框，数据行用灰色即可 |
| `border` 写在 style 顶层（展开写法） | 部分边框方向不渲染，设计器看起来缺一条线 | `bottom/top/left/right` **必须嵌套在 `"border"` key 下**：`{"border": {"bottom":[...],...}, "align":"center"}` ✅；`{"bottom":[...],"align":"center"}` ❌ 顶层展开不生效 |
| 报表无左侧留白 | 内容紧贴左边框，视觉拥挤 | **所有报表** col0（A 列）固定宽度 30px 作为左边距，始终放空白格（`{"text":"","style":margin_style}`）；标题/分区标题从 col1 开始合并（`merge:[0,N-1]`），merges 写 `"B?:F?"` 而非 `"A?:F?"` |
| 多源报表误解为双独立表格或 loopBlock | 做成两个分开的表格/循环块，或用 loopBlockList 嵌套 → 主子字段无法同行显示 | 多源报表 = 同一数据行混合 `#{aa.*}`（主表）和 `#{bb.*}`（子表），引擎按子表记录数展开行，主表字段同行重复；**不需要 loopBlockList**；必须调 `/link/saveAndEdit` (linkType="4") 配置 mainField→subParam 关联 |
| save_db 省略 field_list | 调用报 TypeError（必填参数缺失） | `save_db` 第6个位置参数 `field_list` 为必填，不可省略；每个字段用 `{"fieldName":..,"fieldText":..,"widgetType":"String","isShow":"1","isQuery":"0"}` |
| 纵横组合动态列缺少二级子列表头 | 月份列下无"销售额/捐赠额"等标题，视觉混乱 | 需4行布局：标题行+双层表头行+数据行；row2 静态表头用 `merge:[1,0]` 纵跨2行，groupRight 用 `merge:[0,N-1]` 横跨N子列；row3 填静态子列名（在 groupRight 作用域内，引擎自动随月份重复）；row4 填 group+dynamic |
| 纵横组合 merges 只写标题不写静态表头跨行 | 静态表头（大区/省份）不合并，与子列行错位 | 必须同时写 `"B3:B4"` 等跨行合并 + `"D3:F3"` 等月份模板跨列合并，三处缺一不可 |
| groupRight 月份列头字母序错误 | "10月"排在"1月"前面（字母序："10月" < "1月"） | 月份字段用零填充：`CONCAT(LPAD(month_no,2,'0'),'月')` → "01月"~"12月"，字母序=时间序；不要用 `CONCAT(month_no,'月')` |
| `make_designer` 参数顺序写错 | `make_designer(name, styles)` → `TypeError` 或 id 用了报表名 | 正确签名：`make_designer(report_id: str, name: str, **extra)`；新建报表 report_id 传空字符串 `""`：`make_designer("", REPORT_NAME)` |
| `save_db` 参数名用了 `db_ch_name` | `TypeError: unexpected keyword argument 'db_ch_name'` | 正确位置参数顺序：`save_db(session, report_id, db_code, db_name, sql, field_list, ...)`；第4个参数名是 `db_name`，不是 `db_ch_name` |
| `base_save` 用关键字参数传 `report_id`/`designer` | `TypeError: missing positional argument 'designer_obj'` | `base_save` 前两个是位置参数：`base_save(report_id, designer_obj, **overrides)`；禁止写成 `base_save(report_id=..., designer=...)` |
| 首次 `/save` 返回值当字符串用 | `str(resp["result"])` 得到整个 dict 的字符串表示 | `/save` 新建时 `resp["result"]` 是 **dict**，需要 `resp["result"]["id"]`；若 id 为 None 则用预生成的 `gen_id()` |
| `rows` dict 缺 `"len"` key | 设计器列数/行数异常，图表位置偏移 | rows 必须带 `"len": 200`：`rows = {"len": 200, "1": {"height": 25, "cells": {}}, ...}` |
| YApi `init_yapi()` 后 `create_mock()` 报"请登录" | `urllib` 多 Set-Cookie 头只取了第一条，`_yapi_uid` 丢失 | 已在 `yapi_mock.py` 修复（`get_all('Set-Cookie')`）；升级后 `init_yapi()` + `create_mock()` 可正常串联使用 |
| API 数据集图表用 `/qurestSql` 回填 | 返回 0 行，图表 config 中数据为空 | API 数据集（`dataType="api"`）必须调 `/qurestApi`，返回值路径是 `resp["result"]["data"]`；SQL 数据集才用 `/qurestSql`（返回 `resp["result"]` 直接是列表）|
| API 图表字段名不是 name/value | 设计器「运行」后图表空白，分类/值属性无法绑定 | 字段名不是 `name`/`value`/`type` 时，必须在 `extData` 中设置 `"isCustomPropName": True`，并将 `xText` 设为实际分类字段名、`yText` 设为实际值字段名，`axisX`/`axisY` 同步跟随；`chart_entry` 调用后立即追加这三个字段（服务端确实会保存，放在 extData 位置正确） |
| `query_mysql` 执行 DML/DDL 数据不落库 | INSERT/DELETE/CREATE TABLE 看似成功但 COUNT 仍为 0 | `query_mysql` 内部无 `conn.commit()`，只适合 SELECT；**写数据必须直接用 pymysql**：`conn = pymysql.connect(...); cur.execute(...); conn.commit()` |
| MySQL 密码从 memory 或 get_ds_connection 猜测 | `Access denied` 后反复重试浪费多轮 | `get_ds_connection` 返回的密码可能加密；memory 记录的密码可能过时；**首次连接失败立刻停下来问用户**，不要尝试其他密码 |
| SQL 数据集 `field_list=[]` 传空 | 数据集保存成功但字段明细「暂无数据」，图表无法绑定字段 | 必须先调 `parse_sql(session, sql, db_source=ds_id)` 拿到字段列表再传给 `save_db`；不能传空数组 `[]` |
| `paramList` 字段键名用 fieldName/fieldTxt/defaultVal | `Column 'param_name' cannot be null` 报错，数据集保存失败 | `paramList` 正确键名：`paramName`（参数名）、`paramTxt`（显示名）、`paramValue`（默认值）、`searchFlag`、`widgetType`、`searchMode`；不要用 fieldName/fieldTxt/defaultVal |
| JSON 数据集 jsonData 用单对象而非数组 | 数据集保存后字段解析失败或预览无数据 | jsonData 格式必须是 `{"data": [...]}` 数组，即使只有一条记录也要包在数组里：`{"data": [{"name":"张三",...}]}`；`isList:"0"`（不勾选集合）只影响绑定方式（`${}`），不影响 jsonData 格式 |
| `border` 写成 `{"style":1}` 对象格式 | 设计器整张表渲染空白（前端 JS 解析异常） | `border` 每个方向必须是**数组**格式：`["thin","#000000"]`；正确：`"border":{"top":["thin","#000"],...}`；错误：`"border":{"top":{"style":1},...}` |
| 纵向分组报表缺少顶层 `isGroup/groupField` | 预览报 `For input string: "cells"`（Java NumberFormatException）；设计器正常但预览崩溃 | 含 `#{db.group(field)}` 绑定的报表，`base_save` 必须传 `isGroup=True, groupField="dbCode.fieldName"`；缺少这两个字段时后端走标准引擎，遇到行内 `"cells"` 子对象 key 尝试 `parseInt` 失败；`aggregate/subtotal/funcname/subtotalText` 放在**单元格**上，不是行对象上；无需手写小计行，引擎自动生成 |
| 分组聚合列缺少 `subtotal:"-1"` | 设置了 `funcname:"SUM"` 但合计行数值仍为空白 | 分组聚合列（非分组键列）必须**同时**设置 `funcname:"SUM"` + `subtotal:"-1"`，引擎才会在合计行渲染 SUM 值；只设 funcname 不够。分组键列：`subtotal:"groupField"` + `funcname:"-1"` + `subtotalText:"合计"`；聚合列：`subtotal:"-1"` + `funcname:"SUM"` |
| SQL 图表 config 无初始数据 | 设计器页面 ECharts 空白，预览正常但设计态看不到图 | **创建 SQL 图表后必须调 `/qurestSql` 回填数据**：`session.request("/qurestSql", {"apiSelectId": db_id, "chartSetting": {..."run":1}})` 返回原始行列表，转换后写入 `config.xAxis.data` / `config.series[i].data` / `config.legend.data`，再调 `/save` 保存；具体转换见下方「SQL 图表数据回填」代码片段 |
| bar.background extData.chartType 写错 | 坐标轴正常但柱体数据全部消失 | extData.chartType 必须保持 `bar.simple`，不能写 `bar.background`；带背景效果只需在 echarts series 层配置 showBackground |
| 同行图表水平重叠 | 左图溢出覆盖右图 | `width`（px）必须 ≤ `colspan × 列宽`；公式：`列宽 ≥ ceil(width / colspan)`。示例：width=560、colspan=6 → 列宽需 ≥ 94px。**设定 width 与列宽时必须同步校验，不能独立设值** |
| 多行图表垂直重叠 | 下方图表盖在上方图表上 | rowspan 默认 14，height=420px 实际占 ≈17 行；下一行图表的 row ≥ 上一行 row + ceil(height/行高) + 间距，保守估算：height=420 时 row_step=20；**同时必须初始化所有行 height=25，否则缺失行高度不确定导致位置计算失准** |
| JavaBean 数据集 `dbType` 用 `"0"` | 设计器中数据类型显示为「SQL数据集」而非「JavaBean数据集」 | JavaBean 数据集 `saveDb.dbType` 必须为 **`"2"`**（不是 `"0"`）；`chart_entry` 的 `data_type` 必须为 **`"javabean"`**（不是 `"sql"`）；两者缺一不可 |
| JavaBean 图表调 `/qurestSql` 回填 | 返回 `result: null`，所有 `dataType` 值均无效 | JavaBean 数据集**不支持设计态填充**，`/qurestSql`、`/qurestApi`、`/qurestBean` 均无效；数据由运行时引擎在 `/view/{id}` 时直接调 Bean 的 `createData()` 提供；**创建 JavaBean 图表时跳过回填步骤** |
| `queryFieldByBean` 返回结构误判 | `resp["result"].get("fieldList")` 报 `AttributeError: 'list' object has no attribute 'get'` | `queryFieldByBean` 的 `result` 直接是字段数组（`list`），不是 `{"fieldList": [...]}` 的 dict；正确写法：`raw_fields = resp["result"]` |
| SQL 别名已知却仍调 `parse_sql` | 遇到签名失败/中文字符报错后反复调试，浪费数十分钟 | SQL 字段别名已确定（如 `name/value/type`）时，**直接硬编码 fieldList**，禁止调 `parse_sql`；`parse_sql` 仅用于别名未知的情况。硬编码模板：`{"fieldName":"name","fieldText":"名称","fieldType":"String","orderNum":0,"isShow":"1","isQuery":"0","widgetType":"String","searchMode":"1","searchFormat":""}` |
| `parse_sql` SQL 含中文字符导致签名失败 | `签名校验失败，请重新登录` —— 中文字符（WHERE 条件/SELECT 字面量）影响签名计算 | 若必须调 `parse_sql`，传**纯 ASCII 的简化 SQL**（`SELECT col1, col2 FROM table LIMIT 1`），不含中文 WHERE 条件或字符串字面量；完整业务 SQL 只传给 `save_db`（不经过 SIGNED_PATHS） |
| 横向分组不读模板直接写脚本 | `groupRight` 与 `customGroup` 混用，布局完全错误；或忽略 `direction:"right"`/`rendered:""`/`isDrag:true` 等必要属性导致不渲染 | 凡涉及横向分组（groupRight / customGroup / 横向自定义分组）**必须先读** `references/horizontal-grouping.md` + `examples/horizontal-group.md`，确认类型和属性后再写脚本；禁止凭印象直接写 |
| 建表数据库与 JimuReport 默认数据源不一致 | `parse_sql`/SQL 数据集 预览报 `Table 'xxx.table' doesn't exist` | JimuReport 默认数据源连接的库（见 application.yml 的 `spring.datasource.url`）才是 `dbSource=""` 时查询的目标；**建表必须在该库**，或为 `save_db` 指定正确的 `dbSource` ID。不确定时先问用户看配置文件，不要猜 |
| 猜测不存在的 JimuReport 接口 | 调自造接口（如 `/testConnect/list`）返回 404，浪费一轮调试 | 不确定 JimuReport 有哪个接口时，**直接问用户**或查 `references/` 文档，严禁凭感觉拼接接口路径 |
| JSON 数据集绑定多系列/数组值图表 | 气泡散点图 legend 显示 "undefined"、只渲染一个点；雷达图数据丢失 | JimuReport 渲染时用 JSON 数据集的实际数据覆盖 ECharts config，导致多系列/`value:[...]` 数组格式的硬编码数据被单条记录替换。**scatter.bubble、radar.basic、radar.custom 等复杂静态数据图表必须用 `_NONE()`（不绑数据集）**，config 里的静态数据才能直接渲染 |
| 「全图表/全部图表/SQL+API+JSON 测试」绕开一键脚本自己拼 JSON | 25 张图表手写 chart_entry 几百行 JSON，反复出错回头读模板，10 分钟以上 | 命中关键词「全图表」「所有图表」「测试三种数据集」「图表大全」时，**第一反应**直接 `python scripts/generate_all_reports.py --base-url --token --name --mysql-*`，3 秒完成，禁止重新组装 JSON。脚本内置：建表 + YApi mock + 25 图表 + 三类数据集；图表类型不够补 `CHARTS` + `tpl_xxx` 函数即可 |
| 一键脚本被中断后原样重发等审批 | 用户拒绝后命令重发 N 次，每次等几十秒，比直接执行慢一个量级 | 用户中断/拒绝后**立刻读反馈消息找原因**（参数错？前置失败？），按反馈修复后再执行；不能盲目原样重发等审批，那是用户已经否决的动作 |
| `parallel_save_dbs` 触发 jimu_report_db_field deadlock | `Deadlock found when trying to get lock` Spring 异常栈，部分数据集保存失败 | 多数据集保存改为**串行** `[save_db(session, **a) for a in save_args]`；`generate_all_reports.py` 已修复，新写脚本不要再用 `parallel_save_dbs` |
| `yapi_mock.create_mock` 重复 path 直接报错 | `RuntimeError: 创建接口失败: 已存在的接口:/xxx[GET` 中断整个流程 | `yapi_mock.py` 已修复：errmsg 含「已存在」时调 `/api/interface/list` 找出 id 后调 `update_mock` 复用，业务无需变更 |
| JSON 数据集 jsonData 裸数组导致渲染空白 | 数据集保存成功、字段也正常，但预览时 `#{db.field}` 全部为空 | jsonData **必须**包裹 `{"data":[...]}` 外层对象，引擎从 `data` 键取行数据；直接传裸数组（如 `[{"name":"张三"}]`）引擎找不到 `data` 键，数据全空。正确：`json.dumps({"data": rows}, ensure_ascii=False)`；dbexps 里的 jsonData 字段同样要用此格式 |
| save_db 修改已有数据集仍新增记录 | 每次调 `save_db` 都 INSERT 新行，报表内出现多个同名 dbCode 数据集 | **更新**已有数据集必须用 `update_db(session, db_id, jsonData=...)`，而非再次调 `save_db`；`save_db` 不传 `db_id` 时始终新增 |
| 用户指定 API URL 时擅自调用 create_mock 修改数据 | 原有 mock 数据被覆盖，用户未要求却丢失数据 | 用户提供了完整 API URL 即表示接口已存在，直接将 URL 填入 `save_db(api_url=...)` 即可；**禁止**调用 `init_yapi` / `create_mock`，除非用户明确说「帮我创建 mock 数据」或「帮我修改 mock 数据」 |