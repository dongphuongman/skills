"""
JeecgBoot 表单设计器通用创建脚本
=================================
通过 JSON 配置文件创建/更新表单设计器，避免每次编写大量 Python 代码。

用法:
  python desform_creator.py --api-base <URL> --token <TOKEN> --config <config.json>
  python desform_creator.py --api-base <URL> --token <TOKEN> --config <config.json> --force
  python desform_creator.py --api-base <URL> --token <TOKEN> --tenant-id 2 --app-id <APP_ID> --config <config.json>

参数:
  --api-base    JeecgBoot 后端地址
  --token       X-Access-Token
  --config      JSON 配置文件路径
  --force       强制覆盖已存在的表单（默认检测到已存在时退出）
  --tenant-id   lowApp 模式：组织（租户）ID（整数）
  --app-id      lowApp 模式：应用 ID（字符串）；与 --tenant-id 配合使用

JSON 配置格式:
{
  "formName": "工程竣工验收申请表",
  "formCode": "eng_completion_acceptance",
  "layout": "word",            // auto|half|full|word，默认 auto
  "titleIndex": 0,             // 标题字段索引，默认 0（第一个非分隔符字段）
  "fields": [
    {"name": "自动编号", "type": "auto-number", "prefix": "GCYS"},
    {"name": "条码", "type": "barcode"},
    {"name": "工程名称", "type": "input", "required": true},
    {"name": "工程类别", "type": "radio", "options": ["土建", "安装"]},
    {"name": "开工时间", "type": "date"},
    {"name": "工程量清单", "type": "textarea"},
    {"name": "图片上传", "type": "imgupload"},
    {"name": "定位", "type": "location"},
    {"name": "签字", "type": "hand-sign"},
    {"name": "---", "type": "divider", "text": "第二部分"},
    {"name": "金额", "type": "money", "unit": "万元"},
    {"name": "状态", "type": "select", "options": ["启用", "禁用"]},
    {"name": "性别", "type": "radio", "dictCode": "sex",
     "options": [{"value": "1", "label": "男"}, {"value": "2", "label": "女"}]}
  ],
  "menuParent": "工程管理",     // 可选，生成菜单 SQL 的父菜单名称
  "menuIcon": "ant-design:tool-outlined",  // 可选，父菜单图标
  "expand": {                  // 可选，JS/CSS 增强
    "js": "api.watch({...})",
    "css": ".el-form-item__label { font-weight: bold; }",
    "url": {
      "js": "",
      "css": "/desform/expand/css/custom.css"
    }
  }
}

支持的 type 值:
  基础: input, textarea, number, integer, money, date, time, switch, slider, rate, color
  选择: radio, select, checkbox（支持 options + dictCode）
  系统: select-user, select-depart, org-role, phone, email, area-linkage
  文件: file-upload, imgupload, hand-sign
  高级: auto-number, formula, barcode, location, link-record, link-field
  容器: sub-table-design（设计子表，内嵌 fields 数组）
  布局: divider, editor, markdown

子表配置选项:
  columnNumber: 1/2/3/4，布局列数（默认 2）
  operationMode: 1=行内编辑，2=弹出编辑（默认 1）
  isWordStyle: true/false，Word 文档风格（默认 false）
  isWordInnerGrid: true/false，内嵌栅格（默认 false）
  defaultRows: 默认预填行数（默认 0）

子表示例:
    {"name": "明细清单", "type": "sub-table-design",
     "columnNumber": 2, "operationMode": 1, "fields": [
      {"name": "物品名称", "type": "input", "required": true},
      {"name": "负责人", "type": "select-user"},
      {"name": "数量", "type": "integer"},
      {"name": "单价", "type": "money"},
      {"name": "是否验收", "type": "switch"}
    ]}
  子表内支持的 type:
    基础: input, textarea, integer, number, money, date, time
    选择: select, radio, checkbox, table-dict, select-tree
    系统: select-user, select-depart, select-depart-post, phone, email, area-linkage
    开关: switch, slider, rate, color
    文件: imgupload, file-upload
    关联: link-record, link-field, formula, product
"""

import argparse
import json
import sys
import os

# 注意：Windows 中文乱码修复已在 desform_utils.py 模块加载时自动处理

# 自动定位 desform_utils.py
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SKILL_DIR = os.path.dirname(_SCRIPT_DIR)
for _path in [os.getcwd(), _SCRIPT_DIR]:
    if os.path.exists(os.path.join(_path, 'desform_utils.py')):
        sys.path.insert(0, _path)
        break

from desform_utils import *
from desform_utils import _apply_half_layout, _apply_word_layout, _is_half_suitable


# ============================================================
# type → 工厂函数 映射
# ============================================================
_TYPE_MAP = {
    # 基础
    'input': INPUT,
    'textarea': TEXTAREA,
    'number': NUMBER,
    'integer': INTEGER,
    'money': MONEY,
    'date': DATE,
    'time': TIME,
    'switch': SWITCH,
    'slider': SLIDER,
    'rate': RATE,
    'color': COLOR,
    # 选择
    'radio': RADIO,
    'select': SELECT,
    'checkbox': CHECKBOX,
    # 系统
    'select-user': USER,
    'select-depart': DEPART,
    'select-depart-post': DEPART_POST,
    'phone': PHONE,
    'email': EMAIL,
    'area-linkage': AREA,
    'org-role': ORG_ROLE,
    # 文件
    'file-upload': FILE,
    'imgupload': IMGUPLOAD,
    'hand-sign': HANDSIGN,
    # 高级
    'auto-number': AUTONUMBER,
    'formula': FORMULA,
    'barcode': BARCODE,
    'location': LOCATION,
    'table-dict': TABLE_DICT,
    'select-tree': SELECT_TREE,
    'link-record': LINK_RECORD,
    'link-field': LINK_FIELD,
    'capital-money': CAPITAL_MONEY,
    'text-compose': TEXT_COMPOSE,
    'ocr': OCR,
    'map': MAP,
    'summary': SUMMARY,
    'editor': EDITOR,
    'markdown': MARKDOWN,
    # OA
    'oa-approval-comments': OA_APPROVAL_COMMENTS,
    # 布局容器
    'tabs': TABS,
    'grid': GRID,
    'card': CARD,
    # 静态
    'divider': DIVIDER,
    'text': TEXT,
    'buttons': BUTTONS,
}

# 子表内控件 type → 工厂函数 映射
_SUB_TYPE_MAP = {
    # 基础
    'input': SUB_INPUT,
    'textarea': SUB_TEXTAREA,
    'integer': SUB_INTEGER,
    'number': SUB_NUMBER,
    'money': SUB_MONEY,
    'date': SUB_DATE,
    'time': SUB_TIME,
    # 选择
    'select': SUB_SELECT,
    'radio': SUB_RADIO,
    'checkbox': SUB_CHECKBOX,
    'table-dict': SUB_TABLE_DICT,
    'select-tree': SUB_SELECT_TREE,
    # 系统
    'select-user': SUB_USER,
    'select-depart': SUB_DEPART,
    'select-depart-post': SUB_DEPART_POST,
    'org-role': SUB_ORG_ROLE,
    'phone': SUB_PHONE,
    'email': SUB_EMAIL,
    'area-linkage': SUB_AREA,
    # 开关/评分
    'switch': SUB_SWITCH,
    'slider': SUB_SLIDER,
    'rate': SUB_RATE,
    'color': SUB_COLOR,
    # 文件
    'imgupload': SUB_IMGUPLOAD,
    'file-upload': SUB_FILE,
    # 关联/公式
    'link-record': SUB_LINK_RECORD,
    'link-field': SUB_LINK_FIELD,
    'formula': SUB_FORMULA,
    'product': SUB_PRODUCT,
}

# 子表内控件的参数名映射
_SUB_PARAM_MAP = {
    'required': 'required',
    'col_width': 'col_width',
    'unit': 'unit',
    # sub-select / sub-radio / sub-checkbox
    'options': 'options',
    'dictCode': 'dict_code',
    # sub-select-user / sub-select-depart
    'multiple': 'multiple',
    # sub-switch
    'active': 'active',
    'inactive': 'inactive',
    # sub-table-dict
    'dictTable': 'dict_table',
    'dictCodeCol': 'dict_code_col',
    'dictTextCol': 'dict_text_col',
    'style': 'style',
    'queryScope': 'query_scope',
    'filterable': 'filterable',
    'clearable': 'clearable',
    'disabled': 'disabled',
    # sub-select-tree
    'categoryCode': 'category_code',
    'dataFrom': 'data_from',
    'tableConf': 'table_conf',
    # sub-link-record
    'sourceCode': 'source_code',
    'titleField': 'title_field',
    'showFields': 'show_fields',
    'showMode': 'show_mode',
    # sub-link-field
    'linkRecordKey': 'link_record_key',
    'showField': 'show_field',
    'fieldType': 'field_type',
    'fieldOptions': 'field_options',
    # sub-formula
    'mode': 'mode',
    'expression': 'expression',
    # sub-formula - date modes
    'dateBegin': 'date_begin',
    'dateEnd': 'date_end',
    'dateFormatMethod': 'date_format_method',
    'datePrintUnit': 'date_print_unit',
    'dateAddExp': 'date_add_exp',
    'datePrintFormat': 'date_print_format',
    # sub-product
    'field_models': 'field_models',
}

# 需要 options 参数的控件类型（options 作为第二个位置参数）
_OPTION_TYPES = {'radio', 'select', 'checkbox'}

# 参数名映射：JSON key → 函数参数名
_PARAM_MAP = {
    'required': 'required',
    'width': 'width',
    'prefix': 'prefix',
    'unit': 'unit',
    'placeholder': 'placeholder',
    'multiple': 'multiple',
    'dictCode': 'dict_code',
    'unique': 'unique',
    'precision': 'precision',
    'allowHalf': 'allow_half',
    'fmt': 'fmt',
    'codeType': 'code_type',
    # formula
    'mode': 'mode',
    'expression': 'expression',
    'decimal': 'decimal',
    # formula - date modes
    'dateBegin': 'date_begin',
    'dateEnd': 'date_end',
    'dateFormatMethod': 'date_format_method',
    'datePrintUnit': 'date_print_unit',
    'dateAddExp': 'date_add_exp',
    'datePrintFormat': 'date_print_format',
    # link-record
    'sourceCode': 'source_code',
    'titleField': 'title_field',
    'showFields': 'show_fields',
    'showMode': 'show_mode',
    'showType': 'show_type',
    'isSelf': 'is_self',
    # link-field
    'linkRecordKey': 'link_record_key',
    'showField': 'show_field',
    'fieldType': 'field_type',
    'fieldOptions': 'field_options',
    # table-dict
    'dictTable': 'dict_table',
    'dictCodeCol': 'dict_code_col',
    'dictTextCol': 'dict_text_col',
    'style': 'style',
    'queryScope': 'query_scope',
    'filterable': 'filterable',
    'clearable': 'clearable',
    'disabled': 'disabled',
    # select-tree
    'categoryCode': 'category_code',
    'dataFrom': 'data_from',
    'tableConf': 'table_conf',
    # barcode
    'sourceModel': 'source_model',
    'maxWidth': 'max_width',
    # capital-money
    'moneyWidgetKey': 'money_widget_key',
    'moneyField': 'money_field',
    # summary
    'subTableModel': 'sub_table_model',
    'fieldModel': 'field_model',
    'summaryType': 'summary_type',
    'linkTable': 'sub_table_model',
    'field': 'field_model',
    'filter': 'filter',
    # text-compose
    # (expression 已在 formula 区映射)
    # remoteAPI 远程取值
    'remoteAPI': 'remote_api',
    # 默认值表达式（compose 类型，支持 {{上下文变量}} 和 $字段引用$）
    'defaultExpr': 'default_expr',
    # 填值规则编码（仅 input 控件支持）
    'fillRuleCode': 'fill_rule_code',
    # 完全只读（配合填值规则使用，防止用户修改生成值）
    'readonly': 'readonly',
    # location
    'defaultCurrent': 'default_current',
    'showMap': 'show_map',
    # map
    'height': 'height',
    'zoom': 'zoom',
    'lng': 'lng',
    'lat': 'lat',
    # ocr
    'ocrType': 'ocr_type',
    'fieldMapping': 'field_mapping',
    # text
    'text': 'text',
    'fontSize': 'font_size',
    'fontColor': 'font_color',
    'align': 'align',
    'bold': 'bold',
    # buttons
    'btnType': 'btn_type',
    'icon': 'icon',
    'clickCode': 'click_code',
    # tabs
    'tabLabels': 'tab_labels',
    'tabType': 'tab_type',
    'position': 'position',
    # switch
    'active': 'active',
    'inactive': 'inactive',
    # slider
    'minVal': 'min_val',
    'maxVal': 'max_val',
    'showInput': 'show_input',
    # imgupload
    'length': 'length',
}


def _build_sub_widget(field_def, parent_key):
    """根据 JSON 字段定义构建子表内控件 tuple"""
    ftype = field_def['type']
    name = field_def['name']

    factory = _SUB_TYPE_MAP.get(ftype)
    if not factory:
        raise ValueError(f'子表内不支持的控件类型: {ftype}（支持: {", ".join(_SUB_TYPE_MAP.keys())}）')

    kwargs = {}
    for json_key, param_name in _SUB_PARAM_MAP.items():
        if json_key in field_def:
            kwargs[param_name] = field_def[json_key]

    # sub-select / sub-radio / sub-checkbox 需要 options 作为位置参数
    if ftype in ('select', 'radio', 'checkbox'):
        options = kwargs.pop('options', [])
        return factory(name, parent_key, options, **kwargs)

    # sub-table-dict 需要 dict_table, dict_code_col, dict_text_col
    if ftype == 'table-dict':
        dict_table = kwargs.pop('dict_table', '')
        dict_code_col = kwargs.pop('dict_code_col', '')
        dict_text_col = kwargs.pop('dict_text_col', '')
        return factory(name, parent_key, dict_table, dict_code_col, dict_text_col, **kwargs)

    # sub-link-record 需要 source_code, title_field 作为位置参数
    if ftype == 'link-record':
        source_code = kwargs.pop('source_code')
        title_field = kwargs.pop('title_field')
        return factory(name, parent_key, source_code, title_field, **kwargs)

    # sub-link-field 需要 link_record_key, show_field 作为位置参数
    if ftype == 'link-field':
        link_record_key = kwargs.pop('link_record_key')
        show_field = kwargs.pop('show_field')
        return factory(name, parent_key, link_record_key, show_field, **kwargs)

    # sub-product 需要 field_models 作为位置参数
    if ftype == 'product':
        field_models = kwargs.pop('field_models')
        return factory(name, parent_key, field_models, **kwargs)

    return factory(name, parent_key, **kwargs)


def build_widget(field_def):
    """根据 JSON 字段定义构建控件 tuple（或子表容器 dict）"""
    ftype = field_def['type']
    name = field_def['name']

    # 子表特殊处理
    if ftype == 'sub-table-design':
        sub_fields = field_def.get('fields', [])
        column_number = field_def.get('columnNumber', 2)
        # 先用临时 key 构建子控件（需要 parent_key）
        # 创建空子表仅为获取 key
        tmp_table, parent_key = make_sub_table(name, [], column_number=1)
        sub_widgets = []
        for sf in sub_fields:
            w, k, m = _build_sub_widget(sf, parent_key)
            sub_widgets.append(w)
        # 用真正的参数创建子表（sub_widgets 会被均匀分配到各列）
        sub_table, _ = make_sub_table(
            name, sub_widgets,
            column_number=column_number,
            operation_mode=field_def.get('operationMode', 1),
            is_word_style=field_def.get('isWordStyle', False),
            is_word_inner_grid=field_def.get('isWordInnerGrid', False),
            default_rows=field_def.get('defaultRows', 0),
        )
        # 修正 key/model：使用第一次生成的 key（子控件的 parentKey 指向它）
        sub_table['key'] = parent_key
        sub_table['model'] = tmp_table['model']
        return sub_table

    factory = _TYPE_MAP.get(ftype)
    if not factory:
        raise ValueError(f'未知的控件类型: {ftype}')

    # 构建关键字参数
    kwargs = {}
    for json_key, param_name in _PARAM_MAP.items():
        if json_key in field_def:
            kwargs[param_name] = field_def[json_key]

    # divider 特殊处理：text 参数
    if ftype == 'divider':
        text = field_def.get('text', name)
        return factory(text)

    # text 静态文本：无 name 参数，用 text 参数
    if ftype == 'text':
        return factory(**kwargs)

    # buttons 按钮：无 name 参数
    if ftype == 'buttons':
        return factory(**kwargs)

    # tabs 容器：无 name 参数
    if ftype == 'tabs':
        return factory(**kwargs)

    # map 地图：name + kwargs
    if ftype == 'map':
        return factory(name, **kwargs)

    # summary 汇总控件：需要 sub_table_model + field_model 作为位置参数
    if ftype == 'summary':
        sub_table_model = kwargs.pop('sub_table_model', '')
        field_model = kwargs.pop('field_model', '')
        return factory(name, sub_table_model, field_model, **kwargs)

    # 需要 options 的控件
    if ftype in _OPTION_TYPES:
        options = field_def.get('options', [])
        return factory(name, options, **kwargs)

    # auto-number 特殊处理
    if ftype == 'auto-number':
        return factory(name, **kwargs)

    # table-dict：需要 dict_table 等位置参数，style 和 query_scope 通过 **kwargs 传递
    if ftype == 'table-dict':
        dict_table = kwargs.pop('dict_table', '')
        dict_code_col = kwargs.pop('dict_code_col', '')
        dict_text_col = kwargs.pop('dict_text_col', '')
        return factory(name, dict_table, dict_code_col, dict_text_col, **kwargs)

    # select-tree：需要 category_code
    if ftype == 'select-tree':
        category_code = kwargs.pop('category_code', '')
        return factory(name, category_code, **kwargs)

    # 其余控件：name + kwargs
    return factory(name, **kwargs)


def _extract_widget_info(item):
    """从 widget tuple 或 dict 中提取 (inner_widget, key, model, type)"""
    if isinstance(item, tuple):
        w, key, model = item[0], item[1], item[2]
    else:
        w = item
        key, model = w.get('key', ''), w.get('model', '')
    # card 容器：提取内部控件
    inner = w
    if w.get('type') == 'card' and w.get('list') and len(w['list']) == 1:
        inner = w['list'][0]
    return inner, key, model, inner.get('type', '')


def _build_name_registry(fields, widgets):
    """构建字段名 → (key, model) 的映射注册表

    用于后续自动解析 capital-money 的 moneyWidgetKey 和 formula 的表达式引用。
    注册表 key 为字段名（中文），同时为每个字段生成类型前缀别名（如 'money_预算总额'）。
    """
    registry = {}  # name → (key, model, type)
    for i, (fd, widget) in enumerate(zip(fields, widgets)):
        inner, key, model, wtype = _extract_widget_info(widget)
        name = fd.get('name', '')
        if name and name != '---' and key and model:
            registry[name] = (key, model, wtype)
            # 同时注册 子表内的子控件
        # 子表内控件也注册
        if wtype == 'sub-table-design' and 'columns' in inner:
            sub_fields = fd.get('fields', [])
            sub_idx = 0
            for col in inner.get('columns', []):
                for sub_w in col.get('list', []):
                    sub_name = sub_w.get('name', '')
                    sub_key = sub_w.get('key', '')
                    sub_model = sub_w.get('model', '')
                    sub_type = sub_w.get('type', '')
                    if sub_name and sub_key and sub_model:
                        registry[sub_name] = (sub_key, sub_model, sub_type)
                    sub_idx += 1
    return registry


def _resolve_model_ref(expression, registry):
    """解析表达式中的 $placeholder$ 引用，替换为实际的 model

    支持的占位符格式：
    - $字段名$  — 直接使用字段中文名匹配（如 $预算总额$）
    """
    import re

    def replacer(match):
        ref = match.group(1)
        # 直接匹配字段名
        if ref in registry:
            return f'${registry[ref][1]}$'
        # 未匹配到，保留原始引用（可能已经是实际 model）
        return match.group(0)

    return re.sub(r'\$([^$]+)\$', replacer, expression)


def _post_process_widgets(fields, widgets):
    """对构建完成的控件列表进行后处理，自动解析跨控件引用

    处理内容：
    1. capital-money: 自动查找前面最近的 money 控件 key，设置 moneyWidgetKey
    2. summary: linkTable/field/filter.rules 中的中文名解析为实际 model
    3. formula: 表达式中的 $字段名$ 替换为实际 model
    4. barcode: sourceModel 中的字段名替换为实际 model
    5. text-compose: expression 中的字段名替换为实际 model
    """
    registry = _build_name_registry(fields, widgets)

    for i, (fd, widget) in enumerate(zip(fields, widgets)):
        inner, key, model, wtype = _extract_widget_info(widget)

        # 1. capital-money: 关联 moneyWidgetKey
        #    优先级: moneyField(字段中文名解析) > moneyWidgetKey(直接指定) > 自动查找前面最近的 money/formula/summary
        if wtype == 'capital-money':
            opts = inner.get('options', {})
            money_field_name = opts.pop('moneyField', None) or fd.get('moneyField')
            if money_field_name and money_field_name in registry:
                resolved_key = registry[money_field_name][0]
                opts['moneyWidgetKey'] = resolved_key
                print(f'  [指定关联] 大写金额 "{fd.get("name")}" → moneyField="{money_field_name}" → moneyWidgetKey={resolved_key}')
            elif not opts.get('moneyWidgetKey'):
                # 兜底：查找前面最近的 money/formula/summary 控件
                money_key = None
                for j in range(i - 1, -1, -1):
                    _, prev_key, _, prev_type = _extract_widget_info(widgets[j])
                    if prev_type in ('money', 'formula', 'summary'):
                        money_key = prev_key
                        break
                if money_key:
                    opts['moneyWidgetKey'] = money_key
                    print(f'  [自动关联] 大写金额 "{fd.get("name")}" → moneyWidgetKey={money_key}')
                else:
                    print(f'  [警告] 大写金额 "{fd.get("name")}" 未找到可关联的金额控件')

        # 2. summary: 将中文名解析为实际 model（linkTable → sub_table_model, field → field_model）
        if wtype == 'summary':
            opts = inner.get('options', {})
            # 解析 linkTable（子表中文名 → 子表 model）
            link_table = opts.get('linkTable', '')
            if link_table and link_table in registry:
                resolved_model = registry[link_table][1]
                opts['linkTable'] = resolved_model
                print(f'  [自动解析] 汇总 "{fd.get("name")}" linkTable: "{link_table}" → {resolved_model}')
            # 解析 field（子表列中文名 → 列 model），inner-record-count 不需要解析
            field_val = opts.get('field', '')
            if field_val and field_val != 'inner-record-count' and field_val in registry:
                resolved_field = registry[field_val][1]
                opts['field'] = resolved_field
                print(f'  [自动解析] 汇总 "{fd.get("name")}" field: "{field_val}" → {resolved_field}')
            # 解析 filter.rules 中的 model 和 value（中文名 → 实际 model）
            flt = opts.get('filter', {})
            if flt.get('enabled'):
                for rule in flt.get('rules', []):
                    # 解析 rule.model（子表列中文名 → 列 model）
                    rule_model = rule.get('model', '')
                    if rule_model and rule_model in registry:
                        resolved_model = registry[rule_model][1]
                        rule['model'] = resolved_model
                        print(f'  [自动解析] 汇总 "{fd.get("name")}" filter.model: "{rule_model}" → {resolved_model}')
                    # 当 valueType=field 时，value 数组中的值也是字段引用，需要解析
                    if rule.get('valueType') == 'field':
                        new_values = []
                        for v in rule.get('value', []):
                            if isinstance(v, str) and v in registry:
                                resolved_v = registry[v][1]
                                print(f'  [自动解析] 汇总 "{fd.get("name")}" filter.value: "{v}" → {resolved_v}')
                                new_values.append(resolved_v)
                            else:
                                new_values.append(v)
                        rule['value'] = new_values

        # 3. formula: 解析表达式中的字段引用
        if wtype == 'formula':
            opts = inner.get('options', {})
            for expr_field in ('expression', 'dateBegin', 'dateEnd', 'dateAddExp'):
                val = opts.get(expr_field, '')
                if val and '$' in val:
                    resolved = _resolve_model_ref(val, registry)
                    if resolved != val:
                        opts[expr_field] = resolved
                        print(f'  [自动解析] 公式 "{fd.get("name")}" {expr_field}: {val} → {resolved}')

        # 3. barcode: sourceModel 字段引用
        if wtype == 'barcode':
            opts = inner.get('options', {})
            src = opts.get('sourceModel', '')
            if src and '$' in src:
                resolved = _resolve_model_ref(src, registry)
                if resolved != src:
                    opts['sourceModel'] = resolved

        # 4. text-compose: expression 字段引用
        if wtype == 'text-compose':
            opts = inner.get('options', {})
            expr = opts.get('expression', '')
            if expr and '$' in expr:
                resolved = _resolve_model_ref(expr, registry)
                if resolved != expr:
                    opts['expression'] = resolved
                    print(f'  [自动解析] 文本组合 "{fd.get("name")}" expression: {expr} → {resolved}')

        # 5. link-record: titleField 若为字段中文名则解析为实际 model（自关联时常用）
        if wtype == 'link-record':
            opts = inner.get('options', {})
            tf = opts.get('titleField', '')
            if tf and tf in registry:
                resolved_model = registry[tf][1]
                opts['titleField'] = resolved_model
                print(f'  [自动解析] 关联记录 "{fd.get("name")}" titleField: "{tf}" → {resolved_model}')

    # 子表内 formula/product 也需要解析
    for i, (fd, widget) in enumerate(zip(fields, widgets)):
        inner, _, _, wtype = _extract_widget_info(widget)
        if wtype == 'sub-table-design' and 'columns' in inner:
            for col in inner.get('columns', []):
                for sub_w in col.get('list', []):
                    sub_type = sub_w.get('type', '')
                    if sub_type == 'formula':
                        sub_opts = sub_w.get('options', {})
                        for expr_field in ('expression', 'dateBegin', 'dateEnd', 'dateAddExp'):
                            val = sub_opts.get(expr_field, '')
                            if val and '$' in val:
                                resolved = _resolve_model_ref(val, registry)
                                if resolved != val:
                                    sub_opts[expr_field] = resolved


def _extract_field_table(design_json):
    """从设计 JSON 中提取字段参照表，委托给 desform_utils 中的同名函数"""
    return extract_field_table_from_design(design_json)


def _print_field_table(field_rows):
    """格式化打印字段参照表"""
    print(f'\n  {"字段名称":<20} {"key":<35} {"model":<45} {"type"}')
    print(f'  {"-"*20} {"-"*35} {"-"*45} {"-"*15}')
    for row in field_rows:
        print(f'  {row["name"]:<20} {row["key"]:<35} {row["model"]:<45} {row["type"]}')


def main():
    parser = argparse.ArgumentParser(description='JeecgBoot 表单设计器通用创建工具')
    parser.add_argument('--api-base', required=True, help='JeecgBoot 后端地址')
    parser.add_argument('--token', required=True, help='X-Access-Token')
    parser.add_argument('--config', required=True, help='JSON 配置文件路径，传 "-" 则从 stdin 读取')
    parser.add_argument('--force', action='store_true', help='强制覆盖已存在的表单')
    parser.add_argument('--check-only', action='store_true',
                        help='仅检查表单编码是否可用，不创建表单')
    parser.add_argument('--preprocess', action='store_true',
                        help='预处理模式：生成设计JSON到临时文件后退出，供AI手动修改，'
                             '修改完成后调用 save_design_from_file(code, file_path) 保存')
    parser.add_argument('--tenant-id', type=int, default=None,
                        help='lowApp 模式：组织（租户）ID，与 --app-id 配合使用')
    parser.add_argument('--app-id', default=None,
                        help='lowApp 模式：应用 ID，与 --tenant-id 配合使用')
    args = parser.parse_args()

    if args.config == '-':
        import sys as _sys, io as _io
        stdin_stream = _io.TextIOWrapper(_sys.stdin.buffer, encoding='utf-8')
        config = json.load(stdin_stream)
    else:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)

    form_name = config['formName']
    form_code = config['formCode']
    layout = config.get('layout', 'auto')
    title_index = config.get('titleIndex', 0)

    if args.tenant_id is not None:
        import importlib, desform_lowapp_utils as _lowapp_utils
        _lowapp_utils.init_lowapp(args.api_base, args.token,
                                  tenant_id=args.tenant_id,
                                  app_id=args.app_id)
    else:
        init_api(args.api_base, args.token)

    # --check-only：仅检查编码可用性
    if args.check_only:
        available = check_code_available(form_code)
        print(f"编码 {form_code} {'可用' if available else '已被占用'}")
        sys.exit(0 if available else 1)

    # 防覆盖检查
    existing_id, _ = get_form_id(form_code)
    if existing_id and not args.force:
        print(f'[阻止] 表单 {form_code} 已存在 (ID={existing_id})')
        print(f'如需覆盖，请加 --force 参数')
        sys.exit(1)

    # 构建控件列表
    fields = config.get('fields', [])
    widgets = []
    for fd in fields:
        widget = build_widget(fd)
        widgets.append(widget)

    # 后处理：自动解析跨控件引用（capital-money、formula 表达式等）
    _post_process_widgets(fields, widgets)

    # JS/CSS 增强配置
    expand = config.get('expand')

    # config 覆盖项：从 JSON 配置中提取需要覆盖的 config 字段
    config_overrides = {}
    if config.get('customRequestURL'):
        config_overrides['customRequestURL'] = [{"url": config['customRequestURL']}]
    if 'transactional' in config:
        config_overrides['transactional'] = config['transactional']

    # --preprocess：生成设计 JSON 到临时文件后退出，供 AI 手动修改
    if args.preprocess:
        import tempfile
        form_style = 'word' if layout == 'word' else 'normal'

        # 与 create_form 内部相同的布局逻辑
        if layout == 'word':
            top_items, all_models = _apply_word_layout(widgets, form_name=form_name)
        elif layout == 'half' or (layout == 'auto' and len(widgets) >= 6):
            top_items, all_models = _apply_half_layout(widgets)
        else:
            top_items = []
            all_models = []
            for item in widgets:
                if isinstance(item, tuple):
                    top_items.append(item[0])
                    all_models.append((item[1], item[2]))
                else:
                    top_items.append(item)
                    all_models.append((item.get('key', ''), item.get('model', '')))

        title_model = all_models[title_index][1] if title_index < len(all_models) else all_models[0][1]
        design_json = build_design_json(top_items, title_model, form_style, expand=expand,
                                        config_overrides=config_overrides or None)

        # 创建表单实体（获取 form_id，设计 JSON 稍后由 save_design_from_file 保存）
        form_id, uc, actual_code = find_or_create_form(form_name, form_code)

        # 写入临时文件（格式化 JSON）
        tmp = tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False,
            encoding='utf-8', prefix=f'desform_{form_code}_'
        )
        json.dump(design_json, tmp, ensure_ascii=False, indent=2)
        tmp.close()

        field_rows = _extract_field_table(design_json)

        print(f'\n{"=" * 60}')
        print(f'[预处理模式] 设计JSON已生成，等待手动修改后保存')
        print(f'{"=" * 60}')
        print(f'  表单ID:   {form_id}')
        print(f'  表单编码: {actual_code}')
        print(f'  JSON文件: {tmp.name}')
        _print_field_table(field_rows)
        print(f'\n修改完成后，调用以下方法保存:')
        print(f'  save_design_from_file("{actual_code}", r"{tmp.name}")')
        sys.exit(0)

    # 创建表单
    form_id, title_model = create_form(form_name, form_code, widgets,
                                        title_index=title_index, layout=layout,
                                        expand=expand,
                                        config_overrides=config_overrides or None)

    print(f'\n{"=" * 50}')
    print(f'表单创建成功')
    print(f'{"=" * 50}')
    print(f'  表单ID:   {form_id}')
    print(f'  表单名称: {form_name}')
    print(f'  表单编码: {form_code}')
    print(f'  标题字段: {title_model}')
    print(f'  布局风格: {layout}')

    # 生成菜单 SQL
    menu_parent = config.get('menuParent')
    if menu_parent:
        menu_icon = config.get('menuIcon', 'ant-design:appstore-outlined')
        sql = gen_menu_sql(menu_parent, [
            (form_name, form_code, 1),
        ], icon=menu_icon)
        print(f'\n--- 菜单 SQL ---\n{sql}')


if __name__ == '__main__':
    main()
