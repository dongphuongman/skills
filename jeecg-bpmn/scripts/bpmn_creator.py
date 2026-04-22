"""
JeecgBoot BPM 流程创建工具脚本

用法:
  python bpmn_creator.py --api-base <URL> --token <TOKEN> --config <config.json>
  python bpmn_creator.py --api-base <URL> --token <TOKEN> --config <config.json> --link-form

config.json 格式见下方说明。

支持的操作:
  - 创建流程（生成 BPMN XML + 调用 saveProcess API）
  - 更新流程（传入 processId）
  - 关联表单（--link-form 参数或 config 中的 formLink 配置）
"""

import urllib.request
import urllib.parse
import json
import sys
import time
import base64
import argparse

# 修复 Windows 控制台中文乱码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


# ====== 常量 ======

BPMN_HEADER = '''<?xml version="1.0" encoding="UTF-8"?>
<bpmn2:definitions
  xmlns:bpmn2="http://www.omg.org/spec/BPMN/20100524/MODEL"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
  xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
  xmlns:flowable="http://flowable.org/bpmn"
  id="sample-diagram"
  targetNamespace="http://bpmn.io/schema/bpmn"
  xsi:schemaLocation="http://www.omg.org/spec/BPMN/20100524/MODEL BPMN20.xsd">'''

PROCESS_LISTENERS = '''    <bpmn2:extensionElements>
      <flowable:executionListener class="org.jeecg.modules.extbpm.listener.execution.ProcessEndListener" event="end" />
      <flowable:eventListener class="org.jeecg.modules.listener.tasktip.TaskCreateGlobalListener" />
    </bpmn2:extensionElements>'''

# 子流程额外需要 SubProcessStartListener
SUBPROCESS_LISTENERS = '''    <bpmn2:extensionElements>
      <flowable:executionListener class="org.jeecg.modules.extbpm.listener.execution.ProcessEndListener" event="end" />
      <flowable:eventListener class="org.jeecg.modules.listener.tasktip.TaskCreateGlobalListener" />
      <flowable:executionListener class="org.jeecg.modules.extbpm.listener.execution.SubProcessStartListener" event="start" id="64d675c1a3adcb514ea5f9835093c29b" />
    </bpmn2:extensionElements>'''

# 会签子流程需要 SubProcessHqStartListener（注意是 Hq，不是普通 Start）
SUBPROCESS_HQ_LISTENERS = '''    <bpmn2:extensionElements>
      <flowable:executionListener class="org.jeecg.modules.extbpm.listener.execution.ProcessEndListener" event="end" />
      <flowable:eventListener class="org.jeecg.modules.listener.tasktip.TaskCreateGlobalListener" />
      <flowable:executionListener class="org.jeecg.modules.extbpm.listener.execution.SubProcessHqStartListener" event="start" id="1177167770459070465" />
    </bpmn2:extensionElements>'''

# 布局常量（垂直模式 — 条件分支/顺序审批）
CENTER_X = 218
START_Y = 30
VERTICAL_GAP = 40
NODE_SIZES = {
    'startEvent':       {'w': 36, 'h': 36},
    'endEvent':         {'w': 36, 'h': 36},
    'userTask':         {'w': 100, 'h': 80},
    'serviceTask':      {'w': 100, 'h': 80},
    'aiTask':           {'w': 100, 'h': 80},
    'apiTask':          {'w': 100, 'h': 80},
    'signalThrowEvent': {'w': 36,  'h': 36},
    'signalThrow':      {'w': 36,  'h': 36},
    'signalCatch':      {'w': 36,  'h': 36},
    'messageThrow':     {'w': 36,  'h': 36},
    'messageCatch':     {'w': 36,  'h': 36},
    'scriptTask':       {'w': 100, 'h': 80},
    'exclusiveGateway': {'w': 50, 'h': 50},
    'parallelGateway':  {'w': 50, 'h': 50},
    'inclusiveGateway': {'w': 50, 'h': 50},
}

# 布局常量（水平模式 — 手工分支/意见分支）
MB_START_X = 142      # 开始事件 X
MB_SOURCE_X = 230     # 分支源节点 X
MB_TARGET_X = 570     # 分支目标节点 X
MB_END_X = 912        # 结束事件 X
MB_MID_X = 400        # 分支出口拐点 X
MB_MERGE_X = 791      # 分支汇聚拐点 X
MB_BASE_Y = 190       # 第一个分支目标 Y
MB_BRANCH_GAP = 110   # 分支目标之间的垂直间距
MB_TASK_W = 100       # 任务节点宽度
MB_TASK_H = 80        # 任务节点高度
MB_EVENT_SIZE = 36    # 事件节点尺寸


# ====== API 工具 ======

def api_request(api_base, token, path, data=None, method='POST', content_type='application/json'):
    url = f'{api_base}{path}'
    headers = {
        'X-Access-Token': token,
        'X-Sign': '00000000000000000000000000000000',
        'X-Tenant-Id': '1',
        'X-Timestamp': str(int(time.time() * 1000)),
    }
    if content_type == 'application/x-www-form-urlencoded':
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        encoded = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(url, data=encoded, headers=headers, method=method)
    elif data is not None:
        headers['Content-Type'] = 'application/json; charset=UTF-8'
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    proxy_handler = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(proxy_handler)
    resp = opener.open(req)
    return json.loads(resp.read().decode('utf-8'))


# ====== 条件表达式构建 ======

def build_condition_b64(conditions, logic='and'):
    """
    将条件列表转换为 base64 编码的 JSON，用于 flowUtil.evaluateExpression。

    conditions 格式:
    [
        {"field": "integer_xxx", "fieldType": "integer", "fieldName": "请假天数", "operator": "gt", "value": "3"}
    ]
    logic: 'and'（全部满足）或 'or'（任一满足），默认 'and'
    """
    cond_list = []
    for c in conditions:
        cond_list.append({
            'operator': c['operator'],
            'field': c['field'],
            'fieldType': c.get('fieldType', 'string'),
            'fieldName': c.get('fieldName', c['field']),
            'expectedValue': str(c['value']),
        })
    payload = [{'logic': logic, 'conditions': cond_list}]
    json_str = json.dumps(payload, ensure_ascii=False)
    return base64.b64encode(json_str.encode('utf-8')).decode('utf-8')


def build_condition_expression(conditions, logic='and'):
    """构建完整的条件表达式字符串。logic: 'and' 或 'or'"""
    b64 = build_condition_b64(conditions, logic)
    return f"${{flowUtil.evaluateExpression(execution, '{b64}', 'and')}}"


# ====== taskExtendJson 构建 ======

def build_task_extend_json(same_mode=0, skip_empty=False, skip_one=False,
                           skip_approval=False, assigned_by_prev=False,
                           empty_assigned_by_prev=False, skip_approved_on_return=False):
    """构建 taskExtendJson 的 value 字符串"""
    obj = {
        'sameMode': same_mode,
        'isSkipAssigneeEmpty': skip_empty,
        'isSkipAssigneeOnePersion': skip_one,
        'isSkipApproval': skip_approval,
        'isAssignedByPreviousNode': assigned_by_prev,
        'isEmptyAssignedByPreviousNode': empty_assigned_by_prev,
        'isSkipApprovedOnCountersignReturn': skip_approved_on_return,
    }
    return json.dumps(obj, ensure_ascii=False)


# ====== 会签辅助 ======

def build_countersign_parts(cs):
    """构建 userTask 会签所需的 XML 片段。

    cs 字段说明：
      sequential      : bool — True=串行(顺序), False=并行（默认False）
      rule            : 'countersign_all'|'countersign_one'|'countersign_half'|
                        'countersign_proportion'（默认'countersign_all'）
      proportion      : str — 仅 rule=countersign_proportion 时有效，如 '0.6'
      auditorUserType : 'candidateUsers'|'candidatePosts'|'candidateDepts'|
                        'candidateGroups'|'candidateApprovalGroups'|
                        'candidateDeptPositions'|'formData'
      # 各类型 ID/数据字段：
      auditorUserIds          : list[str]  (candidateUsers)
      auditorPostIds          : list[str]  (candidatePosts)
      auditorDeptIds          : list[str]  (candidateDepts)
      auditorGroupIds         : list[str]  (candidateGroups)
      auditorApprovalGroupIds : list[str]  (candidateApprovalGroups)
      auditorDeptPositionIds  : list[str]  (candidateDeptPositions)
      auditorCountersignFormField     : str  (formData)
      auditorCountersignFormFieldType : str  (formData，默认 'select-user')

    Returns:
      (extra_attrs, cs_extend_b64, multi_instance_xml)
      - extra_attrs      : 附加到 <bpmn2:userTask ...> 的属性字符串
      - cs_extend_b64    : taskCountersignExtendJson 的 Base64 值
      - multi_instance_xml : 完整的 <bpmn2:multiInstanceLoopCharacteristics.../> 行
    """
    rule = cs.get('rule', 'countersign_all')
    sequential = cs.get('sequential', False)
    proportion = cs.get('proportion', '')
    utype = cs.get('auditorUserType', 'candidateUsers')

    # ── 1. extra_attrs ──
    extra_attrs = f' flowable:countersignRule="{rule}"'
    if rule == 'countersign_proportion' and proportion:
        extra_attrs += f' flowable:countersignProportion="{proportion}"'

    # ── 2. taskCountersignExtendJson ──
    # customUser 类型（自定义-指定人员）：无 taskCountersignExtendJson
    if utype == 'customUser':
        cs_extend_b64 = None
        collection = cs.get('customCollection') or '${flowUtil.stringToList(assigneeUserIdList)}'
        prop_val = proportion or '0.5'
        _cond_map = {
            'countersign_all':        '${nrOfCompletedInstances/nrOfInstances==1}',
            'countersign_one':        '${nrOfCompletedInstances/nrOfInstances>0}',
            'countersign_half':       '${nrOfCompletedInstances/nrOfInstances&gt;=0.5}',
            'countersign_proportion': '${nrOfCompletedInstances/nrOfInstances&gt;=%s}' % prop_val,
            'countersign_custom':     '${nrOfCompletedInstances/nrOfInstances&gt;=1}',
        }
        completion_cond = cs.get('customCompletionCondition') or _cond_map.get(rule, '')
        seq_str = 'true' if sequential else 'false'
        if completion_cond:
            multi_xml = (
                '      <bpmn2:multiInstanceLoopCharacteristics isSequential="%s" '
                'flowable:collection="%s" flowable:elementVariable="assigneeUserId">'
                '<bpmn2:completionCondition xsi:type="bpmn2:tFormalExpression">%s'
                '</bpmn2:completionCondition>'
                '</bpmn2:multiInstanceLoopCharacteristics>'
            ) % (seq_str, collection, completion_cond)
        else:
            multi_xml = (
                '      <bpmn2:multiInstanceLoopCharacteristics isSequential="%s" '
                'flowable:collection="%s" flowable:elementVariable="assigneeUserId" />'
            ) % (seq_str, collection)
        return extra_attrs, cs_extend_b64, multi_xml

    cs_core = {'auditorUserType': utype}
    if utype == 'candidateUsers':
        cs_core['auditorUserIds'] = cs.get('auditorUserIds', [])
    elif utype == 'candidatePosts':
        cs_core['auditorPostIds'] = cs.get('auditorPostIds', [])
    elif utype == 'candidateDepts':
        cs_core['auditorDeptIds'] = cs.get('auditorDeptIds', [])
    elif utype == 'candidateGroups':
        cs_core['auditorGroupIds'] = cs.get('auditorGroupIds', [])
    elif utype == 'candidateApprovalGroups':
        cs_core['auditorApprovalGroupIds'] = cs.get('auditorApprovalGroupIds', [])
    elif utype == 'candidateDeptPositions':
        cs_core['auditorDeptPositionIds'] = cs.get('auditorDeptPositionIds', [])
    elif utype == 'formData':
        cs_core['auditorCountersignFormField'] = cs.get('auditorCountersignFormField', '')
        cs_core['auditorCountersignFormFieldType'] = cs.get('auditorCountersignFormFieldType', 'select-user')

    # getAssigneeUsers 参数（不含 timestamp / countersignProportion）
    assignee_b64 = base64.b64encode(
        json.dumps(cs_core, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    ).decode('ascii')

    # 完整 taskCountersignExtendJson（含 countersignProportion + timestamp）
    cs_full = {}
    if proportion:
        cs_full['countersignProportion'] = proportion
    cs_full.update(cs_core)
    cs_full['timestamp'] = int(time.time() * 1000)
    cs_extend_b64 = base64.b64encode(
        json.dumps(cs_full, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    ).decode('ascii')

    # ── 3. collection 表达式（&#39; 转义单引号）──
    if cs.get('customCollection'):
        # 自定义集合表达式，直接使用（调用方负责 XML 转义）
        collection = cs['customCollection']
    elif utype == 'candidateUsers':
        users = ','.join(cs.get('auditorUserIds', []))
        collection = "${flowUtil.stringToList(&#39;%s&#39;)}" % users
    else:
        collection = "${flowUtil.getAssigneeUsers(execution,&#39;%s&#39;)}" % assignee_b64

    # ── 4. completionCondition ──
    prop_val = proportion or '0.5'
    condition_map = {
        'countersign_all':        '${nrOfCompletedInstances/nrOfInstances==1}',
        'countersign_one':        '${nrOfCompletedInstances/nrOfInstances>0}',
        'countersign_half':       '${nrOfCompletedInstances/nrOfInstances&gt;=0.5}',
        'countersign_proportion': '${nrOfCompletedInstances/nrOfInstances&gt;=%s}' % prop_val,
    }
    completion_cond = cs.get('customCompletionCondition') or condition_map.get(rule, '')
    seq_str = 'true' if sequential else 'false'

    if completion_cond:
        multi_xml = (
            '      <bpmn2:multiInstanceLoopCharacteristics isSequential="%s" '
            'flowable:collection="%s" flowable:elementVariable="assigneeUserId">'
            '<bpmn2:completionCondition xsi:type="bpmn2:tFormalExpression">%s'
            '</bpmn2:completionCondition>'
            '</bpmn2:multiInstanceLoopCharacteristics>'
        ) % (seq_str, collection, completion_cond)
    else:
        multi_xml = (
            '      <bpmn2:multiInstanceLoopCharacteristics isSequential="%s" '
            'flowable:collection="%s" flowable:elementVariable="assigneeUserId" />'
        ) % (seq_str, collection)

    return extra_attrs, cs_extend_b64, multi_xml


# ====== 节点 XML 生成 ======

def xml_escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def gen_start_event(node):
    nid = node['id']
    name = xml_escape(node.get('name', '开始'))
    outgoing = node.get('_outgoing', [])
    if outgoing:
        lines = [f'    <bpmn2:startEvent id="{nid}" name="{name}" flowable:initiator="applyUserId">']
        for fid in outgoing:
            lines.append(f'      <bpmn2:outgoing>{fid}</bpmn2:outgoing>')
        lines.append('    </bpmn2:startEvent>')
        return '\n'.join(lines)
    return f'    <bpmn2:startEvent id="{nid}" name="{name}" flowable:initiator="applyUserId" />'


def gen_end_event(node):
    nid = node['id']
    name = xml_escape(node.get('name', '结束'))
    incoming = node.get('_incoming', [])
    if incoming:
        lines = [f'    <bpmn2:endEvent id="{nid}">']
        for fid in incoming:
            lines.append(f'      <bpmn2:incoming>{fid}</bpmn2:incoming>')
        lines.append('    </bpmn2:endEvent>')
        return '\n'.join(lines)
    return f'    <bpmn2:endEvent id="{nid}" name="{name}" />'


def gen_user_task(node):
    """生成 userTask XML"""
    nid = node['id']
    name = xml_escape(node.get('name', ''))
    assignee_cfg = node.get('assignee', {})

    # 构建 userTask 开标签属性
    attrs = f'id="{nid}" name="{name}"'

    atype = assignee_cfg.get('type', 'assignee')
    avalue = assignee_cfg.get('value', '')

    if atype == 'assignee':
        # 固定用户名: flowable:assignee="admin"
        attrs += f' flowable:assignee="{xml_escape(avalue)}"'
    elif atype == 'expression':
        # 表达式: flowable:assignee="${applyUserId}"
        attrs += f' flowable:assignee="${{{avalue}}}"'
    elif atype == 'candidateUsers':
        # 多候选人: flowable:candidateUsers="user1,user2"
        attrs += f' flowable:candidateUsers="{xml_escape(avalue)}"'
    elif atype == 'candidateUsersExpression':
        # 候选人表达式: flowable:candidateUsers="${flowNodeExpression.getDepartLeaders(applyUserId)}"
        attrs += f' flowable:candidateUsers="{xml_escape(avalue)}"'
    elif atype == 'role':
        # 候选角色: flowable:candidateGroups="admin,vue3" groupType="role"
        attrs += f' flowable:candidateGroups="{xml_escape(avalue)}"'
        attrs += ' flowable:groupType="role"'
    elif atype == 'approvalRole':
        # 审批角色: candidateUsers + 表达式 + groupType="approvalRole"
        attrs += f" flowable:candidateUsers=\"${{flowUtil.getUsersByApprRole(execution,'{avalue}')}}\""
        attrs += ' flowable:groupType="approvalRole"'
    elif atype == 'dept':
        # 候选部门: flowable:candidateGroups="部门ID" groupType="dept"
        attrs += f' flowable:candidateGroups="{xml_escape(avalue)}"'
        attrs += ' flowable:groupType="dept"'
    elif atype == 'deptPosition':
        # 候选岗位: flowable:candidateGroups="岗位ID" groupType="deptPosition"
        attrs += f' flowable:candidateGroups="{xml_escape(avalue)}"'
        attrs += ' flowable:groupType="deptPosition"'
    elif atype == 'position':
        # 候选职级: candidateUsers + 表达式 + groupType="position"
        attrs += f" flowable:candidateUsers=\"${{oaFlowExpression.getApplyUserDeptPositionLevel(sys_org_code, applyUserId, '{avalue}')}}\""
        attrs += ' flowable:groupType="position"'
    elif atype == 'candidateGroups':
        # 通用候选组（需指定 groupType）
        attrs += f' flowable:candidateGroups="{xml_escape(avalue)}"'
        group_type = assignee_cfg.get('groupType', 'role')
        attrs += f' flowable:groupType="{group_type}"'

    # 会签节点：覆盖 assignee 为 ${assigneeUserId}，追加 countersignRule 等属性
    cs = node.get('countersign')
    cs_extend_b64 = None
    multi_instance_xml = None
    if cs:
        # 移除已设的 assignee/candidateGroups/candidateUsers 属性，统一用 assigneeUserId
        import re as _re
        attrs = _re.sub(r' flowable:(assignee|candidateGroups|candidateUsers|groupType)="[^"]*"', '', attrs)
        attrs += ' flowable:assignee="${assigneeUserId}"'
        extra_attrs, cs_extend_b64, multi_instance_xml = build_countersign_parts(cs)
        attrs += extra_attrs

    # extensionElements
    # draft 节点（首节点提交/填写）：sameMode 默认为 0（由发起人对自己审批），
    # 同时添加 AutoSubmitListener（首任务节点自动提交）。
    # assignee.sameMode 可显式覆盖。
    is_draft = node.get('draft', False)
    if 'sameMode' in assignee_cfg:
        same_mode = assignee_cfg['sameMode']
    elif is_draft:
        same_mode = 0
    else:
        same_mode = assignee_cfg.get('sameMode', 0)

    multi_types = ('role', 'dept', 'deptPosition', 'approvalRole', 'position', 'candidateUsers', 'candidateUsersExpression', 'candidateGroups')
    skip_one = assignee_cfg.get('skipOne', atype in multi_types)
    empty_assigned = assignee_cfg.get('emptyAssignedByPrev', atype in multi_types)

    tej = build_task_extend_json(
        same_mode=same_mode,
        skip_empty=assignee_cfg.get('skipEmpty', False),
        skip_one=skip_one,
        skip_approval=assignee_cfg.get('skipApproval', False),
        assigned_by_prev=assignee_cfg.get('assignedByPrev', False),
        empty_assigned_by_prev=empty_assigned,
    )

    lines = [f'    <bpmn2:userTask {attrs}>']
    lines.append('      <bpmn2:extensionElements>')
    lines.append(f"        <flowable:taskExtendJson value='{tej}' />")
    if is_draft:
        lines.append('        <flowable:taskListener class="org.jeecg.modules.extbpm.listener.task.TaskCreatedAutoSubmitListener" event="create" id="9c3064baa7074eab62e3c5b3b5458691" />')
    else:
        lines.append('        <flowable:taskListener class="org.jeecg.modules.extbpm.listener.task.TaskSkipApprovalListener" event="create" />')
    if cs_extend_b64:
        lines.append(f'        <flowable:taskCountersignExtendJson value="{cs_extend_b64}" />')
    cc_config = node.get('ccConfig')
    if cc_config:
        import json as _json, base64 as _b64
        cc_b64 = _b64.b64encode(_json.dumps(cc_config, ensure_ascii=False).encode('utf-8')).decode('utf-8')
        lines.append(f'        <flowable:ccConfigJson value="{cc_b64}" />')
    lines.append('      </bpmn2:extensionElements>')
    # 手工分支需要 incoming/outgoing 标注
    for fid in node.get('_incoming', []):
        lines.append(f'      <bpmn2:incoming>{fid}</bpmn2:incoming>')
    for fid in node.get('_outgoing', []):
        lines.append(f'      <bpmn2:outgoing>{fid}</bpmn2:outgoing>')
    if multi_instance_xml:
        lines.append(multi_instance_xml)
    lines.append('    </bpmn2:userTask>')
    return '\n'.join(lines)


def gen_gateway(node):
    """生成网关 XML"""
    nid = node['id']
    name = xml_escape(node.get('name', ''))
    gtype = node['type']
    default_flow = node.get('default', '')
    default_attr = f' default="{default_flow}"' if default_flow else ''
    return f'    <bpmn2:{gtype} id="{nid}" name="{name}"{default_attr} />'


def gen_service_task(node):
    """生成 serviceTask（Java 服务节点）XML。

    node 字段：
      serviceType : 'class' | 'expression' | 'delegateExpression'（默认 'expression'）
      expression  : UEL 表达式，serviceType='expression' 时使用，如 ${myBean.doWork(execution)}
      className   : Java 全类名，serviceType='class' 时使用
      delegateExpr: 委托表达式，serviceType='delegateExpression' 时使用
      resultVar   : 可选，把表达式返回值存入该流程变量（仅 expression 类型有效）
    """
    nid  = node['id']
    name = node.get('name', '服务节点')
    stype = node.get('serviceType', 'expression')

    if stype == 'class':
        attr = f' flowable:class="{node.get("className", "")}"'
    elif stype == 'delegateExpression':
        attr = f' flowable:delegateExpression="{node.get("delegateExpr", "")}"'
    else:  # expression（默认）
        attr = f' flowable:expression="{node.get("expression", "")}"'
        result_var = node.get('resultVar', '')
        if result_var:
            attr += f' flowable:resultVariable="{result_var}"'

    return f'    <bpmn2:serviceTask id="{nid}" name="{name}"{attr} />'


def gen_ai_service_task(node):
    """生成 AI 流程编排服务节点（aiTask）XML。

    node 字段：
      aiFlowId         : AI 流程 ID（必填，从 AIGC 流程管理获取）
      inputParamsList  : 输入参数映射列表，如 [{"key": "content", "value": "${name}"}]
      outputParamsList : 输出参数映射列表，如 [{"key": "result", "value": "aiResult"}]
    """
    import base64, json as _json
    nid  = node['id']
    name = node.get('name', 'AI流程节点')
    ai_config = {
        'id': nid,
        'nodeName': name,
        'aiFlowId': node.get('aiFlowId', ''),
        'inputParamsList': node.get('inputParamsList', []),
        'outputParamsList': node.get('outputParamsList', []),
    }
    b64 = base64.b64encode(_json.dumps(ai_config, ensure_ascii=False).encode('utf-8')).decode('ascii')
    lines = []
    lines.append(f'    <bpmn2:serviceTask id="{nid}" name="{name}" flowable:class="org.jeecg.modules.extbpm.listener.service.AigcServiceTaskDelegate">')
    lines.append(f'      <bpmn2:extensionElements>')
    lines.append(f'        <flowable:aiServiceTaskConfig value="{b64}" />')
    lines.append(f'      </bpmn2:extensionElements>')
    lines.append(f'    </bpmn2:serviceTask>')
    return '\n'.join(lines)


def gen_api_service_task(node):
    """生成 API 服务节点（apiTask）XML。

    node 字段：
      apiUrl           : 接口地址（必填），如 '/sys/user/list'，支持 ${var} 流程变量
      method           : HTTP 方法（默认 'GET'），支持 GET/POST/PUT/DELETE
      headersList      : 请求头列表，如 [{"key": "Content-Type", "value": "application/json"}]
      inputParamsList  : 请求参数映射，如 [{"key": "pageNo", "value": "1"}, {"key": "name", "value": "${name}"}]
      outputParamsList : 响应结果映射，支持 JSONPath，如 [{"key": "result.records[0].name", "value": "flowVar"}]
      timeout          : 超时时间毫秒（默认 30000）
      retryCount       : 重试次数（默认 3）
    """
    import base64, json as _json
    nid  = node['id']
    name = node.get('name', 'API节点')
    api_config = {
        'id': nid,
        'nodeName': name,
        'apiUrl': node.get('apiUrl', ''),
        'method': node.get('method', 'GET'),
        'headersList': node.get('headersList', []),
        'inputParamsList': node.get('inputParamsList', []),
        'outputParamsList': node.get('outputParamsList', []),
        'timeout': node.get('timeout', 30000),
        'retryCount': node.get('retryCount', 3),
    }
    b64 = base64.b64encode(_json.dumps(api_config, ensure_ascii=False).encode('utf-8')).decode('ascii')
    lines = []
    lines.append(f'    <bpmn2:serviceTask id="{nid}" name="{name}" flowable:class="org.jeecg.modules.extbpm.listener.service.ApiServiceTaskDelegate">')
    lines.append(f'      <bpmn2:extensionElements>')
    lines.append(f'        <flowable:apiServiceTaskConfig value="{b64}" />')
    lines.append(f'      </bpmn2:extensionElements>')
    lines.append(f'    </bpmn2:serviceTask>')
    return '\n'.join(lines)


def _signal_ref_id(signal_name):
    """根据信号名称生成信号定义 ID（去除非字母数字字符）。"""
    import re
    safe = re.sub(r'[^A-Za-z0-9_]', '_', signal_name)
    return f'Signal_{safe}'


def _message_ref_id(message_name):
    """根据消息名称生成消息定义 ID。"""
    import re
    safe = re.sub(r'[^A-Za-z0-9_]', '_', message_name)
    return f'Message_{safe}'


def gen_signal_throw_event(node):
    """生成中间抛出信号事件（intermediateThrowEvent）XML。

    node 字段：
      signalName : 信号名称（必填），与捕获事件保持一致
    """
    nid  = node['id']
    name = node.get('name', '抛出信号')
    signal_name = node.get('signalName', 'signal')
    signal_id   = _signal_ref_id(signal_name)
    def_id = f'SignalEventDefinition_{nid}'
    lines = []
    lines.append(f'    <bpmn2:intermediateThrowEvent id="{nid}" name="{xml_escape(name)}">')
    lines.append(f'      <bpmn2:signalEventDefinition id="{def_id}" flowable:signalRef="{signal_id}" />')
    lines.append(f'    </bpmn2:intermediateThrowEvent>')
    return '\n'.join(lines)


def gen_signal_catch_event(node):
    """生成中间捕获信号事件（intermediateCatchEvent + signalEventDefinition）XML。"""
    nid = node['id']
    name = node.get('name', '等待信号')
    signal_name = node.get('signalName', 'signal')
    signal_id = _signal_ref_id(signal_name)
    def_id = f'SignalEventDefinition_{nid}'
    lines = []
    lines.append(f'    <bpmn2:intermediateCatchEvent id="{nid}" name="{xml_escape(name)}">')
    lines.append(f'      <bpmn2:signalEventDefinition id="{def_id}" flowable:signalRef="{signal_id}" />')
    lines.append(f'    </bpmn2:intermediateCatchEvent>')
    return '\n'.join(lines)


def gen_message_throw_event(node):
    """生成中间抛出消息事件（intermediateThrowEvent + messageEventDefinition）XML。"""
    nid = node['id']
    name = node.get('name', '发出消息')
    message_name = node.get('messageName', 'message')
    message_id = _message_ref_id(message_name)
    def_id = f'MessageEventDefinition_{nid}'
    lines = []
    lines.append(f'    <bpmn2:intermediateThrowEvent id="{nid}" name="{xml_escape(name)}">')
    lines.append(f'      <bpmn2:messageEventDefinition id="{def_id}" messageRef="{message_id}" />')
    lines.append(f'    </bpmn2:intermediateThrowEvent>')
    return '\n'.join(lines)


def gen_message_catch_event(node):
    """生成中间捕获消息事件（intermediateCatchEvent + messageEventDefinition）XML。"""
    nid = node['id']
    name = node.get('name', '等待消息')
    message_name = node.get('messageName', 'message')
    message_id = _message_ref_id(message_name)
    def_id = f'MessageEventDefinition_{nid}'
    lines = []
    lines.append(f'    <bpmn2:intermediateCatchEvent id="{nid}" name="{xml_escape(name)}">')
    lines.append(f'      <bpmn2:messageEventDefinition id="{def_id}" messageRef="{message_id}" />')
    lines.append(f'    </bpmn2:intermediateCatchEvent>')
    return '\n'.join(lines)


def gen_message_boundary_event(node_id, msg_config, event_id):
    """生成附加在 userTask 上的消息边界捕获事件 XML。"""
    name = msg_config.get('name', '消息边界')
    message_name = msg_config.get('messageName', 'message')
    message_id = _message_ref_id(message_name)
    cancel = 'true' if msg_config.get('cancelActivity', True) else 'false'
    def_id = f'MessageEventDefinition_{event_id}'
    lines = []
    lines.append(f'    <bpmn2:boundaryEvent id="{event_id}" name="{xml_escape(name)}" attachedToRef="{node_id}" cancelActivity="{cancel}">')
    lines.append(f'      <bpmn2:messageEventDefinition id="{def_id}" messageRef="{message_id}" />')
    lines.append(f'    </bpmn2:boundaryEvent>')
    return '\n'.join(lines)


def gen_message_boundary_shape(event_id, task_pos):
    """生成消息边界事件 BPMNShape XML（定位在任务节点右下角，与定时器错开）。"""
    ex = task_pos['x'] + task_pos['w'] / 2 + 12
    ey = task_pos['y'] + task_pos['h'] - 18
    return (
        f'      <bpmndi:BPMNShape id="shape_{event_id}" bpmnElement="{event_id}">\n'
        f'        <dc:Bounds x="{ex}" y="{ey}" width="36" height="36" />\n'
        f'      </bpmndi:BPMNShape>'
    )


def gen_intermediate_event_shape(node, pos):
    """生成中间事件（信号/消息抛出/捕获）的 BPMNShape XML。"""
    nid = node['id']
    x, y, w, h = pos['x'], pos['y'], pos['w'], pos['h']
    lines = [f'      <bpmndi:BPMNShape id="shape_{nid}" bpmnElement="{nid}">']
    lines.append(f'        <dc:Bounds x="{x}" y="{y}" width="{w}" height="{h}" />')
    lines.append(f'        <bpmndi:BPMNLabel>')
    lines.append(f'          <dc:Bounds x="{x + 7}" y="{y + h + 7}" width="22" height="14" />')
    lines.append(f'        </bpmndi:BPMNLabel>')
    lines.append(f'      </bpmndi:BPMNShape>')
    return '\n'.join(lines)


def gen_signal_catch_boundary(node_id, signal_config, event_id):
    """生成附加在 userTask 上的边界捕获信号事件 XML。

    signal_config 字段：
      signalName : 信号名称（必填），与抛出事件保持一致
      name       : 边界事件显示名称（默认'捕获信号'）
      eventId    : 自定义事件ID（默认 signal_{node_id}）
      target     : 信号触发后流转到的节点ID（可选）
    """
    name        = signal_config.get('name', '捕获信号')
    signal_name = signal_config.get('signalName', 'signal')
    signal_id   = _signal_ref_id(signal_name)
    def_id = f'SignalEventDefinition_{event_id}'
    lines = []
    lines.append(f'    <bpmn2:boundaryEvent id="{event_id}" name="{xml_escape(name)}" attachedToRef="{node_id}">')
    lines.append(f'      <bpmn2:signalEventDefinition id="{def_id}" flowable:signalRef="{signal_id}" />')
    lines.append(f'    </bpmn2:boundaryEvent>')
    return '\n'.join(lines)


def gen_signal_catch_shape(event_id, name, task_pos):
    """生成边界捕获信号事件的 BPMNShape XML（定位在任务节点左下角，与定时器错开）。"""
    # 左下角：x = 任务左边 - 12（稍偏左），y = 任务底部 - 18
    ex = task_pos['x'] - 12
    ey = task_pos['y'] + task_pos['h'] - 18
    label_x = ex - 4
    label_y = ey + 36 + 4
    lines = []
    lines.append(f'      <bpmndi:BPMNShape id="shape_{event_id}" bpmnElement="{event_id}">')
    lines.append(f'        <dc:Bounds x="{ex}" y="{ey}" width="36" height="36" />')
    lines.append(f'        <bpmndi:BPMNLabel>')
    lines.append(f'          <dc:Bounds x="{label_x}" y="{label_y}" width="44" height="14" />')
    lines.append(f'        </bpmndi:BPMNLabel>')
    lines.append(f'      </bpmndi:BPMNShape>')
    return '\n'.join(lines)


def gen_boundary_timer_event(node_id, timer, event_id):
    """生成附加在 userTask 上的边界定时器事件 XML。

    timer 字段：
      type    : 'date' | 'duration' | 'cycle'
                  date     — 指定日期，value 为 ISO 8601 datetime，如 '2026-04-03T15:00:59'
                  duration — 等待时长，value 为 ISO 8601 duration，如 'P1D'（1天）、'PT2H'（2小时）
                  cycle    — 重复周期，value 为 ISO 8601 repeat，如 'R3/PT10H'（每10小时重复3次）
      value   : 定时器的值（必填）
      eventId : 边界事件 ID（默认自动生成）
    """
    tid_inner = f'TimerEventDefinition_{event_id}'
    timer_type = timer.get('type', 'duration')
    value = timer.get('value', 'PT1H')

    if timer_type == 'date':
        timer_elem = f'        <bpmn2:timeDate>{value}</bpmn2:timeDate>'
    elif timer_type == 'cycle':
        timer_elem = f'        <bpmn2:timeCycle>{value}</bpmn2:timeCycle>'
    else:  # duration（默认）
        timer_elem = f'        <bpmn2:timeDuration>{value}</bpmn2:timeDuration>'

    lines = []
    lines.append(f'    <bpmn2:boundaryEvent id="{event_id}" attachedToRef="{node_id}">')
    lines.append(f'      <bpmn2:timerEventDefinition id="{tid_inner}">')
    lines.append(timer_elem)
    lines.append(f'      </bpmn2:timerEventDefinition>')
    lines.append(f'    </bpmn2:boundaryEvent>')
    return '\n'.join(lines)


def gen_boundary_timer_shape(event_id, task_pos):
    """生成边界定时器事件的 BPMNShape XML（定位在任务节点右下角）。"""
    # 右下角：x = 任务中心偏右12，y = 任务底部 - 18（圆心在底边上）
    ex = task_pos['x'] + task_pos['w'] / 2 + 12
    ey = task_pos['y'] + task_pos['h'] - 18
    return (
        f'      <bpmndi:BPMNShape id="shape_{event_id}" bpmnElement="{event_id}">\n'
        f'        <dc:Bounds x="{ex}" y="{ey}" width="36" height="36" />\n'
        f'      </bpmndi:BPMNShape>'
    )


def gen_script_task(node):
    """生成 scriptTask（脚本节点）XML。

    node 字段：
      scriptFormat : 脚本语言，如 'javascript'、'groovy'、'juel'（默认 'javascript'）
      script       : 脚本内容（必填）
      resultVar    : 可选，把脚本返回值存入该流程变量
    """
    nid    = node['id']
    name   = node.get('name', '脚本节点')
    fmt    = node.get('scriptFormat', 'javascript')
    script = node.get('script', '')
    result_var = node.get('resultVar', '')

    result_attr = f' flowable:resultVariable="{result_var}"' if result_var else ''
    # 脚本内容含特殊字符时用 CDATA 包裹
    special = any(c in script for c in ('<', '>', '&', '"', "'"))
    if special:
        script_body = f'<![CDATA[{script}]]>'
    else:
        script_body = script

    lines = [f'    <bpmn2:scriptTask id="{nid}" name="{name}" scriptFormat="{fmt}"{result_attr}>']
    lines.append(f'      <bpmn2:script>{script_body}</bpmn2:script>')
    lines.append(f'    </bpmn2:scriptTask>')
    return '\n'.join(lines)


def gen_call_activity(node):
    """生成 callActivity（调用子流程 / 会签子流程）XML。

    普通调用子流程: 只需 calledElement
    会签子流程: 额外需要 countersign 配置:
      {
        "sequential": false,          # false=并行会签（默认）, true=顺序会签
        "collection": "assigneeUserIdList",  # 会签人列表变量（默认）
        "elementVariable": "assigneeUserId"  # 循环变量（默认）
      }
    """
    nid = node['id']
    name = xml_escape(node.get('name', ''))
    called_element = node.get('calledElement', '')
    cs = node.get('countersign')

    lines = [f'    <bpmn2:callActivity id="{nid}" name="{name}" calledElement="{called_element}">']
    lines.append('      <bpmn2:extensionElements>')
    lines.append('        <flowable:in source="applyUserId" target="applyUserId" />')
    lines.append('        <flowable:in source="JG_LOCAL_PROCESS_ID" target="JG_SUB_MAIN_PROCESS_ID" />')
    if cs:
        elem_var = cs.get('elementVariable', 'assigneeUserId')
        lines.append(f'        <flowable:in source="{elem_var}" target="{elem_var}" />')
        lines.append('        <flowable:out source="applyUserId" target="applyUserId" />')
    lines.append('      </bpmn2:extensionElements>')
    for fid in node.get('_incoming', []):
        lines.append(f'      <bpmn2:incoming>{fid}</bpmn2:incoming>')
    for fid in node.get('_outgoing', []):
        lines.append(f'      <bpmn2:outgoing>{fid}</bpmn2:outgoing>')
    if cs:
        sequential = 'true' if cs.get('sequential', False) else 'false'
        collection = cs.get('collection', 'assigneeUserIdList')
        elem_var = cs.get('elementVariable', 'assigneeUserId')
        lines.append(f'      <bpmn2:multiInstanceLoopCharacteristics isSequential="{sequential}" '
                     f'flowable:collection="${{flowUtil.stringToList({collection})}}" '
                     f'flowable:elementVariable="{elem_var}" />')
    lines.append('    </bpmn2:callActivity>')
    return '\n'.join(lines)


def gen_sub_process(node, config):
    """生成内嵌子流程（subProcess）XML。

    node 格式:
    {
        "id": "sub_process", "type": "subProcess", "name": "内嵌子流程",
        "subNodes": [
            {"id": "sub_start", "type": "startEvent", "name": "开始"},
            {"id": "sub_task1", "type": "userTask", "name": "经理审批", "assignee": {...}},
            {"id": "sub_end", "type": "endEvent", "name": "结束"}
        ],
        "subFlows": [
            {"id": "sf1", "source": "sub_start", "target": "sub_task1"},
            {"id": "sf2", "source": "sub_task1", "target": "sub_end"}
        ]
    }
    """
    nid = node['id']
    sub_nodes = node.get('subNodes', [])
    sub_flows = node.get('subFlows', [])

    lines = [f'    <bpmn2:subProcess id="{nid}">']
    for fid in node.get('_incoming', []):
        lines.append(f'      <bpmn2:incoming>{fid}</bpmn2:incoming>')
    for fid in node.get('_outgoing', []):
        lines.append(f'      <bpmn2:outgoing>{fid}</bpmn2:outgoing>')

    # 内部节点
    for sn in sub_nodes:
        stype = sn['type']
        if stype == 'startEvent':
            sid = sn['id']
            out = [f['id'] for f in sub_flows if f['source'] == sid]
            lines.append(f'      <bpmn2:startEvent id="{sid}">')
            for o in out:
                lines.append(f'        <bpmn2:outgoing>{o}</bpmn2:outgoing>')
            lines.append(f'      </bpmn2:startEvent>')
        elif stype == 'endEvent':
            sid = sn['id']
            inc = [f['id'] for f in sub_flows if f['target'] == sid]
            lines.append(f'      <bpmn2:endEvent id="{sid}">')
            for i in inc:
                lines.append(f'        <bpmn2:incoming>{i}</bpmn2:incoming>')
            lines.append(f'      </bpmn2:endEvent>')
        elif stype == 'userTask':
            # 复用 gen_user_task 的逻辑，但需要计算 incoming/outgoing
            sid = sn['id']
            sn['_incoming'] = [f['id'] for f in sub_flows if f['target'] == sid]
            sn['_outgoing'] = [f['id'] for f in sub_flows if f['source'] == sid]
            task_xml = gen_user_task(sn)
            # 缩进调整（gen_user_task 用 4 空格，子流程内需要 6 空格）
            for line in task_xml.split('\n'):
                lines.append('  ' + line)

    # 内部连线
    for sf in sub_flows:
        sfid = sf['id']
        lines.append(f'      <bpmn2:sequenceFlow id="{sfid}" sourceRef="{sf["source"]}" targetRef="{sf["target"]}" />')

    lines.append('    </bpmn2:subProcess>')
    return '\n'.join(lines)


def gen_sequence_flow(flow):
    """生成 sequenceFlow XML"""
    fid = flow['id']
    name = xml_escape(flow.get('name', ''))
    source = flow['source']
    target = flow['target']
    conditions = flow.get('conditions')

    if conditions:
        logic = flow.get('conditionLogic', 'and')
        expr = build_condition_expression(conditions, logic)
        lines = [f'    <bpmn2:sequenceFlow id="{fid}" name="{name}" sourceRef="{source}" targetRef="{target}">']
        lines.append(f'      <bpmn2:conditionExpression xsi:type="bpmn2:tFormalExpression">{expr}</bpmn2:conditionExpression>')
        lines.append('    </bpmn2:sequenceFlow>')
        return '\n'.join(lines)
    else:
        return f'    <bpmn2:sequenceFlow id="{fid}" name="{name}" sourceRef="{source}" targetRef="{target}" />'


# ====== 布局计算 ======

def calc_layout(nodes):
    """计算所有节点的位置"""
    positions = {}
    y = START_Y
    for node in nodes:
        ntype = node['type']
        # 映射 gateway 类型
        size_key = ntype
        if ntype in ('exclusiveGateway', 'parallelGateway', 'inclusiveGateway'):
            size_key = ntype
        if ntype == 'subProcess':
            # 动态计算扩展子流程尺寸：宽度按内部节点数，高度固定 200
            sub_nodes_list = node.get('subNodes', [])
            sub_w = max(660, len(sub_nodes_list) * 160 + 100)
            sub_h = 200
            size = {'w': sub_w, 'h': sub_h}
        else:
            size = NODE_SIZES.get(size_key, {'w': 100, 'h': 60})
        x = CENTER_X - size['w'] / 2
        pos_entry = {
            'x': x, 'y': y,
            'w': size['w'], 'h': size['h'],
            'cx': CENTER_X,
            'cy': y + size['h'] / 2,
            'bottom': y + size['h'],
        }
        if ntype == 'subProcess':
            pos_entry['_isSubProcess'] = True
            pos_entry['_subNodes'] = node.get('subNodes', [])
        positions[node['id']] = pos_entry
        y += size['h'] + VERTICAL_GAP
    return positions


def gen_shape_xml(node, pos):
    """生成 BPMNShape XML"""
    nid = node['id']
    ntype = node['type']
    x, y, w, h = pos['x'], pos['y'], pos['w'], pos['h']

    is_gateway = ntype in ('exclusiveGateway', 'parallelGateway', 'inclusiveGateway')
    marker = ' isMarkerVisible="true"' if ntype == 'exclusiveGateway' else ''

    expanded_attr = ' isExpanded="true"' if ntype == 'subProcess' else ''
    lines = [f'      <bpmndi:BPMNShape id="shape_{nid}" bpmnElement="{nid}"{marker}{expanded_attr}>']
    lines.append(f'        <dc:Bounds x="{x}" y="{y}" width="{w}" height="{h}" />')

    # 标签位置
    if ntype in ('startEvent', 'endEvent'):
        lines.append(f'        <bpmndi:BPMNLabel>')
        lines.append(f'          <dc:Bounds x="{x + 7}" y="{y + h + 7}" width="22" height="14" />')
        lines.append(f'        </bpmndi:BPMNLabel>')
    elif is_gateway:
        lines.append(f'        <bpmndi:BPMNLabel>')
        lines.append(f'          <dc:Bounds x="{x + w + 10}" y="{pos["cy"] - 7}" width="78" height="14" />')
        lines.append(f'        </bpmndi:BPMNLabel>')

    lines.append(f'      </bpmndi:BPMNShape>')

    # subProcess 内部节点的 Shape
    if pos.get('_isSubProcess') and pos.get('_subNodes'):
        sub_nodes = pos['_subNodes']
        sub_x = pos['x']
        sub_cy = pos['cy']
        inner_x = sub_x + 109  # 内部起始 x（参考真实示例）
        for sn in sub_nodes:
            stype = sn['type']
            if stype == 'startEvent':
                sx, sy, sw, sh = inner_x, sub_cy - 18, 36, 36
            elif stype == 'endEvent':
                sx = inner_x
                sy, sw, sh = sub_cy - 18, 36, 36
            elif stype == 'userTask':
                sx, sy, sw, sh = inner_x, sub_cy - 40, 100, 80
            else:
                sx, sy, sw, sh = inner_x, sub_cy - 30, 100, 60
            lines.append(f'      <bpmndi:BPMNShape id="shape_{sn["id"]}" bpmnElement="{sn["id"]}">')
            lines.append(f'        <dc:Bounds x="{sx}" y="{sy}" width="{sw}" height="{sh}" />')
            lines.append(f'      </bpmndi:BPMNShape>')
            inner_x += sw + 60  # 节点间距

    return '\n'.join(lines)


def gen_edge_xml(flow, positions):
    """生成 BPMNEdge XML"""
    fid = flow['id']
    src_pos = positions[flow['source']]
    tgt_pos = positions[flow['target']]

    is_bypass = flow.get('bypass', False)

    lines = [f'      <bpmndi:BPMNEdge id="edge_{fid}" bpmnElement="{fid}">']

    if is_bypass:
        # 从网关右侧绕行到目标
        lines.append(f'        <di:waypoint x="{src_pos["cx"] + 25}" y="{src_pos["cy"]}" />')
        lines.append(f'        <di:waypoint x="{src_pos["cx"] + 132}" y="{src_pos["cy"]}" />')
        lines.append(f'        <di:waypoint x="{src_pos["cx"] + 132}" y="{tgt_pos["cy"]}" />')
        lines.append(f'        <di:waypoint x="{tgt_pos["x"] + tgt_pos["w"]}" y="{tgt_pos["cy"]}" />')
    else:
        # 直线连接：上节点底部 → 下节点顶部
        lines.append(f'        <di:waypoint x="{src_pos["cx"]}" y="{src_pos["bottom"]}" />')
        lines.append(f'        <di:waypoint x="{tgt_pos["cx"]}" y="{tgt_pos["y"]}" />')

    lines.append(f'      </bpmndi:BPMNEdge>')
    return '\n'.join(lines)


# ====== 手工分支（意见分支）布局与边 ======

def calc_layout_manual_branch(config):
    """计算手工分支模式的节点布局（水平排列）。

    布局结构（无链式节点时 — 单行布局）:
        开始(col1) → [前置节点...](col2) → 分支源(col3) →┬→ 分支1(col4) →┬→ 结束(col5)
                                                           ├→ 分支2(col4) →┤
                                                           └→ 分支N(col4) →┘

    布局结构（有链式节点时 — 双行布局）:
        Row1: 开始 → [前置节点...] → 分支源 ─────(不同意/上方绕行)───→ ┐
                                       │                                │
                                 (同意) ↓                                │
        Row2:                    分支目标 → 链式节点... → 结束 ←─────────┘

    支持：
    - 分支源前的前置节点（如草稿节点）
    - 分支目标后的链式节点（如 总监审批 → 借款子流程）
    - subProcess / callActivity 类型的节点
    """
    mb = config['_manualBranch']
    source_id = mb['sourceId']
    target_ids = mb['targets']
    nodes = config['nodes']
    flows = config['flows']
    node_map = {n['id']: n for n in nodes}

    # 找到结束事件 ID
    end_id = None
    for n in nodes:
        if n['type'] == 'endEvent':
            end_id = n['id']
            break

    # 构建出线映射
    flow_targets_map = {}
    for f in flows:
        flow_targets_map.setdefault(f['source'], []).append(f['target'])

    # 分离目标：非结束目标 vs 直达结束
    non_end_targets = [t for t in target_ids if t != end_id]

    # 检测链式节点：从非结束目标向前追踪到结束
    chain_nodes = []
    chain_set = set()
    all_branch_ids = {source_id} | set(target_ids)
    for tid in non_end_targets:
        current = tid
        while current:
            nexts = flow_targets_map.get(current, [])
            found_next = None
            for nxt in nexts:
                if (nxt != end_id and nxt not in chain_set
                        and nxt not in all_branch_ids
                        and node_map.get(nxt, {}).get('type') not in ('startEvent', 'endEvent')):
                    found_next = nxt
                    break
            if found_next:
                chain_nodes.append(found_next)
                chain_set.add(found_next)
                current = found_next
            else:
                break

    has_chain = len(chain_nodes) > 0

    # 检测前置节点（排除 source、targets、chain、start/end）
    special_ids = {source_id} | set(target_ids) | chain_set
    prefix_nodes = []
    for n in nodes:
        nid = n['id']
        if n['type'] not in ('startEvent', 'endEvent') and nid not in special_ids:
            prefix_nodes.append(n)

    # 计算 prefix_shift，subProcess 节点按实际展开宽度计算
    prefix_shift = 0
    for pn in prefix_nodes:
        if pn['type'] == 'subProcess':
            sub_nodes_list = pn.get('subNodes', [])
            prefix_shift += max(660, len(sub_nodes_list) * 160 + 100) + 100
        else:
            prefix_shift += 200

    adj_source_x = MB_SOURCE_X + prefix_shift
    adj_target_x = MB_TARGET_X + prefix_shift
    adj_end_x = MB_END_X + prefix_shift
    adj_mid_x = MB_MID_X + prefix_shift
    adj_merge_x = MB_MERGE_X + prefix_shift

    positions = {}

    if has_chain:
        # ====== 双行布局（有链式节点）======
        row1_cy = MB_BASE_Y + MB_TASK_H / 2       # 230
        row2_y = MB_BASE_Y + MB_BRANCH_GAP         # 300
        row2_cy = row2_y + MB_TASK_H / 2           # 340
        node_gap = 80  # 第二行节点间水平间距

        # 开始事件 — Row1
        for n in nodes:
            if n['type'] == 'startEvent':
                positions[n['id']] = {
                    'x': MB_START_X, 'y': row1_cy - MB_EVENT_SIZE / 2,
                    'w': MB_EVENT_SIZE, 'h': MB_EVENT_SIZE,
                    'cx': MB_START_X + MB_EVENT_SIZE / 2,
                    'cy': row1_cy,
                    'bottom': row1_cy + MB_EVENT_SIZE / 2,
                }

        # 前置节点 — Row1
        cur_prefix_x = MB_SOURCE_X
        for pn in prefix_nodes:
            if pn['type'] == 'subProcess':
                sub_nodes_list = pn.get('subNodes', [])
                pw = max(660, len(sub_nodes_list) * 160 + 100)
                ph = 200
                py = row1_cy - ph / 2
                positions[pn['id']] = {
                    'x': cur_prefix_x, 'y': py,
                    'w': pw, 'h': ph,
                    'cx': cur_prefix_x + pw / 2,
                    'cy': row1_cy,
                    'bottom': py + ph,
                    '_isSubProcess': True,
                    '_subNodes': sub_nodes_list,
                }
                cur_prefix_x += pw + 100
            else:
                positions[pn['id']] = {
                    'x': cur_prefix_x, 'y': MB_BASE_Y,
                    'w': MB_TASK_W, 'h': MB_TASK_H,
                    'cx': cur_prefix_x + MB_TASK_W / 2,
                    'cy': row1_cy,
                    'bottom': MB_BASE_Y + MB_TASK_H,
                }
                cur_prefix_x += MB_TASK_W + 100

        # 分支源节点 — Row1
        positions[source_id] = {
            'x': adj_source_x, 'y': MB_BASE_Y,
            'w': MB_TASK_W, 'h': MB_TASK_H,
            'cx': adj_source_x + MB_TASK_W / 2,
            'cy': row1_cy,
            'bottom': MB_BASE_Y + MB_TASK_H,
        }

        # Row2: 非结束目标 → 链式节点 → 结束
        current_x = adj_target_x
        for tid in non_end_targets:
            tw, th = MB_TASK_W, MB_TASK_H
            positions[tid] = {
                'x': current_x, 'y': row2_y,
                'w': tw, 'h': th,
                'cx': current_x + tw / 2,
                'cy': row2_cy,
                'bottom': row2_y + th,
            }
            current_x += tw + node_gap

        for cid in chain_nodes:
            cw, ch = MB_TASK_W, MB_TASK_H
            positions[cid] = {
                'x': current_x, 'y': row2_y,
                'w': cw, 'h': ch,
                'cx': current_x + cw / 2,
                'cy': row2_cy,
                'bottom': row2_y + ch,
            }
            current_x += cw + node_gap

        # 结束事件 — Row2 最右侧
        adj_end_x = current_x + 20
        if end_id:
            positions[end_id] = {
                'x': adj_end_x, 'y': row2_cy - MB_EVENT_SIZE / 2,
                'w': MB_EVENT_SIZE, 'h': MB_EVENT_SIZE,
                'cx': adj_end_x + MB_EVENT_SIZE / 2,
                'cy': row2_cy,
                'bottom': row2_cy + MB_EVENT_SIZE / 2,
            }

        mb['_adj_mid_x'] = adj_mid_x
        mb['_adj_merge_x'] = adj_end_x - 50
        mb['_has_chain'] = True
        mb['_chain_nodes'] = list(chain_nodes)
        mb['_non_end_targets'] = non_end_targets

    else:
        # ====== 单行布局（无链式节点，保持原有逻辑）======
        first_cy = MB_BASE_Y + MB_TASK_H / 2  # 230

        for n in nodes:
            if n['type'] == 'startEvent':
                positions[n['id']] = {
                    'x': MB_START_X, 'y': first_cy - MB_EVENT_SIZE / 2,
                    'w': MB_EVENT_SIZE, 'h': MB_EVENT_SIZE,
                    'cx': MB_START_X + MB_EVENT_SIZE / 2,
                    'cy': first_cy,
                    'bottom': first_cy + MB_EVENT_SIZE / 2,
                }

        cur_prefix_x = MB_SOURCE_X
        for pn in prefix_nodes:
            if pn['type'] == 'subProcess':
                sub_nodes_list = pn.get('subNodes', [])
                pw = max(660, len(sub_nodes_list) * 160 + 100)
                ph = 200
                py = first_cy - ph / 2
                positions[pn['id']] = {
                    'x': cur_prefix_x, 'y': py,
                    'w': pw, 'h': ph,
                    'cx': cur_prefix_x + pw / 2,
                    'cy': first_cy,
                    'bottom': py + ph,
                    '_isSubProcess': True,
                    '_subNodes': sub_nodes_list,
                }
                cur_prefix_x += pw + 100
            else:
                positions[pn['id']] = {
                    'x': cur_prefix_x, 'y': MB_BASE_Y,
                    'w': MB_TASK_W, 'h': MB_TASK_H,
                    'cx': cur_prefix_x + MB_TASK_W / 2,
                    'cy': MB_BASE_Y + MB_TASK_H / 2,
                    'bottom': MB_BASE_Y + MB_TASK_H,
                }
                cur_prefix_x += MB_TASK_W + 100

        positions[source_id] = {
            'x': adj_source_x, 'y': MB_BASE_Y,
            'w': MB_TASK_W, 'h': MB_TASK_H,
            'cx': adj_source_x + MB_TASK_W / 2,
            'cy': MB_BASE_Y + MB_TASK_H / 2,
            'bottom': MB_BASE_Y + MB_TASK_H,
        }

        for i, tid in enumerate(target_ids):
            y = MB_BASE_Y + i * MB_BRANCH_GAP
            target_node = node_map.get(tid, {})
            if target_node.get('type') == 'subProcess':
                sub_nodes = target_node.get('subNodes', [])
                tw = max(660, len(sub_nodes) * 160 + 100)
                th = 200
                positions[tid] = {
                    'x': adj_target_x, 'y': y,
                    'w': tw, 'h': th,
                    'cx': adj_target_x + tw / 2,
                    'cy': y + th / 2,
                    'bottom': y + th,
                    '_isSubProcess': True,
                    '_subNodes': sub_nodes,
                    '_subW': tw,
                }
                new_end_x = adj_target_x + tw + 80
                if new_end_x > adj_end_x:
                    adj_end_x = new_end_x
                    adj_merge_x = adj_target_x + tw + 30
            else:
                positions[tid] = {
                    'x': adj_target_x, 'y': y,
                    'w': MB_TASK_W, 'h': MB_TASK_H,
                    'cx': adj_target_x + MB_TASK_W / 2,
                    'cy': y + MB_TASK_H / 2,
                    'bottom': y + MB_TASK_H,
                }

        for n in nodes:
            if n['type'] == 'endEvent':
                positions[n['id']] = {
                    'x': adj_end_x, 'y': first_cy - MB_EVENT_SIZE / 2,
                    'w': MB_EVENT_SIZE, 'h': MB_EVENT_SIZE,
                    'cx': adj_end_x + MB_EVENT_SIZE / 2,
                    'cy': first_cy,
                    'bottom': first_cy + MB_EVENT_SIZE / 2,
                }

        mb['_adj_mid_x'] = adj_mid_x
        mb['_adj_merge_x'] = adj_merge_x
        mb['_has_chain'] = False

    return positions


def gen_edge_xml_manual_branch(flow, positions, config):
    """生成手工分支模式的 BPMNEdge XML（水平路由）。"""
    fid = flow['id']
    src_pos = positions[flow['source']]
    tgt_pos = positions[flow['target']]
    mb = config.get('_manualBranch', {})
    source_id = mb.get('sourceId', '')
    target_ids = mb.get('targets', [])
    has_chain = mb.get('_has_chain', False)
    has_label = bool(flow.get('name'))

    # 使用调整后的路由坐标（支持前置节点偏移）
    mid_x = mb.get('_adj_mid_x', MB_MID_X)
    merge_x = mb.get('_adj_merge_x', MB_MERGE_X)

    lines = [f'      <bpmndi:BPMNEdge id="edge_{fid}" bpmnElement="{fid}">']

    src_right_x = src_pos['x'] + src_pos['w']
    src_cy = src_pos['cy']
    tgt_left_x = tgt_pos['x']
    tgt_cy = tgt_pos['cy']

    label_x = None
    label_y = None

    if has_chain and flow['source'] == source_id:
        # ====== 双行布局：分支源出线 ======
        end_id = None
        for n in config['nodes']:
            if n['type'] == 'endEvent':
                end_id = n['id']
                break

        if flow['target'] == end_id:
            # 不同意：源顶部 → 上方 → 右移 → 下到结束
            src_cx = src_pos['cx']
            src_top = src_pos['y']
            tgt_cx = tgt_pos['cx']
            tgt_top = tgt_pos['y']
            top_y = src_pos['y'] - 80  # 上方绕行 Y
            lines.append(f'        <di:waypoint x="{src_cx}" y="{src_top}" />')
            lines.append(f'        <di:waypoint x="{src_cx}" y="{top_y}" />')
            lines.append(f'        <di:waypoint x="{tgt_cx}" y="{top_y}" />')
            lines.append(f'        <di:waypoint x="{tgt_cx}" y="{tgt_top}" />')
            if has_label:
                label_x = (src_cx + tgt_cx) / 2
                label_y = top_y - 17
        else:
            # 同意：源底部 → 下到目标行 → 右到目标
            src_cx = src_pos['cx']
            src_bottom = src_pos['bottom']
            lines.append(f'        <di:waypoint x="{src_cx}" y="{src_bottom}" />')
            lines.append(f'        <di:waypoint x="{src_cx}" y="{tgt_cy}" />')
            lines.append(f'        <di:waypoint x="{tgt_left_x}" y="{tgt_cy}" />')
            if has_label:
                label_x = src_cx + 10
                label_y = (src_bottom + tgt_cy) / 2 - 7

    elif has_chain and flow['source'] != source_id:
        # ====== 双行布局：链式连线（水平直连）======
        lines.append(f'        <di:waypoint x="{src_right_x}" y="{src_cy}" />')
        lines.append(f'        <di:waypoint x="{tgt_left_x}" y="{tgt_cy}" />')

    elif flow['source'] == source_id and flow['target'] in target_ids:
        # ====== 单行布局：分支源 → 分支目标 ======
        branch_idx = target_ids.index(flow['target'])
        if branch_idx == 0:
            # 第一条分支：直线水平（如 拒绝 → 结束）
            lines.append(f'        <di:waypoint x="{src_right_x}" y="{src_cy}" />')
            lines.append(f'        <di:waypoint x="{tgt_left_x}" y="{tgt_cy}" />')
            if has_label:
                label_x = (src_right_x + tgt_left_x) / 2
                label_y = src_cy - 17
        else:
            # 后续分支：从源底部向下再向右（避免与第一条分支线重叠）
            src_cx = src_pos['cx']
            src_bottom = src_pos['bottom']
            lines.append(f'        <di:waypoint x="{src_cx}" y="{src_bottom}" />')
            lines.append(f'        <di:waypoint x="{src_cx}" y="{tgt_cy}" />')
            lines.append(f'        <di:waypoint x="{tgt_left_x}" y="{tgt_cy}" />')
            if has_label:
                label_x = src_cx + 10
                label_y = (src_bottom + tgt_cy) / 2 - 7
    elif flow['source'] in target_ids:
        # 单行布局：分支目标 → 结束
        branch_idx = target_ids.index(flow['source'])
        if branch_idx == 0:
            lines.append(f'        <di:waypoint x="{src_right_x}" y="{src_cy}" />')
            lines.append(f'        <di:waypoint x="{tgt_left_x}" y="{tgt_cy}" />')
        else:
            end_cx = tgt_pos['cx']
            end_bottom = tgt_pos['y'] + tgt_pos['h']
            lines.append(f'        <di:waypoint x="{src_right_x}" y="{src_cy}" />')
            lines.append(f'        <di:waypoint x="{end_cx}" y="{src_cy}" />')
            lines.append(f'        <di:waypoint x="{end_cx}" y="{end_bottom}" />')
    else:
        # 其他连线（如 start→prefix, prefix→source）：直线水平
        lines.append(f'        <di:waypoint x="{src_right_x}" y="{src_cy}" />')
        lines.append(f'        <di:waypoint x="{tgt_left_x}" y="{tgt_cy}" />')

    # 连线名称标签
    if has_label and label_x is not None:
        lines.append(f'      <bpmndi:BPMNLabel><dc:Bounds x="{label_x}" y="{label_y}" width="44" height="14" /></bpmndi:BPMNLabel>')

    lines.append(f'      </bpmndi:BPMNEdge>')
    return '\n'.join(lines)


# ====== 主构建逻辑 ======

def build_bpmn_xml(config):
    """从 JSON 配置构建完整的 BPMN XML"""
    process_key = config['processKey']
    process_name = config['processName']
    nodes = config['nodes']
    flows = config['flows']

    # 生成节点 XML
    node_xmls = []
    _unsupported_ids = set()   # 记录跳过的节点ID，后续过滤相关连线
    for node in nodes:
        ntype = node['type']
        if ntype == 'startEvent':
            node_xmls.append(gen_start_event(node))
        elif ntype == 'endEvent':
            node_xmls.append(gen_end_event(node))
        elif ntype == 'userTask':
            node_xmls.append(gen_user_task(node))
        elif ntype == 'serviceTask':
            node_xmls.append(gen_service_task(node))
        elif ntype == 'aiTask':
            node_xmls.append(gen_ai_service_task(node))
        elif ntype == 'apiTask':
            node_xmls.append(gen_api_service_task(node))
        elif ntype == 'scriptTask':
            node_xmls.append(gen_script_task(node))
        elif ntype in ('exclusiveGateway', 'parallelGateway', 'inclusiveGateway'):
            node_xmls.append(gen_gateway(node))
        elif ntype == 'callActivity':
            node_xmls.append(gen_call_activity(node))
        elif ntype == 'subProcess':
            node_xmls.append(gen_sub_process(node, config))
        elif ntype == 'signalThrow':
            node_xmls.append(gen_signal_throw_event(node))
        elif ntype == 'signalCatch':
            node_xmls.append(gen_signal_catch_event(node))
        elif ntype == 'messageThrow':
            node_xmls.append(gen_message_throw_event(node))
        elif ntype == 'messageCatch':
            node_xmls.append(gen_message_catch_event(node))
        else:
            print(f'  [警告] 不支持的节点类型 "{ntype}"（id={node["id"]}），已跳过，相关连线也将被忽略')
            _unsupported_ids.add(node['id'])

    # 生成边界定时器事件 XML（附加在带 timer 配置的节点上）
    boundary_xmls = []
    boundary_timer_nodes = []  # (node, event_id) — 供后续 shape/edge 使用
    for node in nodes:
        timer = node.get('timer')
        if not timer:
            continue
        event_id = timer.get('eventId') or f'timer_{node["id"]}'
        boundary_xmls.append(gen_boundary_timer_event(node['id'], timer, event_id))
        boundary_timer_nodes.append((node, event_id, timer))

    # 生成信号边界事件 XML（附加在带 signalBoundary 配置的 userTask 上）
    boundary_signal_nodes = []  # (node, event_id, signal_config)
    for node in nodes:
        sig_cfg = node.get('signalBoundary')
        if not sig_cfg:
            continue
        event_id = sig_cfg.get('eventId') or f'signal_boundary_{node["id"]}'
        boundary_xmls.append(gen_signal_catch_boundary(node['id'], sig_cfg, event_id))
        boundary_signal_nodes.append((node, event_id, sig_cfg))

    # 生成消息边界事件 XML（附加在带 messageBoundary 配置的 userTask 上）
    boundary_message_nodes = []  # (node, event_id, msg_config)
    for node in nodes:
        msg_cfg = node.get('messageBoundary')
        if not msg_cfg:
            continue
        event_id = msg_cfg.get('eventId') or f'message_boundary_{node["id"]}'
        boundary_xmls.append(gen_message_boundary_event(node['id'], msg_cfg, event_id))
        boundary_message_nodes.append((node, event_id, msg_cfg))

    # 生成连线 XML（跳过涉及不支持节点的连线，避免 IDREF 悬空）
    flow_xmls = []
    for flow in flows:
        if flow['source'] in _unsupported_ids or flow['target'] in _unsupported_ids:
            print(f'  [警告] 连线 {flow["id"]} 涉及已跳过的节点，已忽略')
            continue
        flow_xmls.append(gen_sequence_flow(flow))

    # 生成边界定时器触发后的连线（若配置了 timerTarget）
    for node, event_id, timer in boundary_timer_nodes:
        timer_target = timer.get('timerTarget')
        if timer_target:
            timer_flow_id = timer.get('timerFlowId') or f'flow_{event_id}'
            flow_xmls.append(
                f'    <bpmn2:sequenceFlow id="{timer_flow_id}" sourceRef="{event_id}" targetRef="{timer_target}" />'
            )

    # 过滤掉不支持的节点，避免 layout/shape 时 KeyError
    supported_nodes = [n for n in nodes if n['id'] not in _unsupported_ids]

    # 计算布局（手工分支使用水平布局，其他使用垂直布局）
    is_manual_branch = '_manualBranch' in config
    if is_manual_branch:
        positions = calc_layout_manual_branch(config)
    else:
        positions = calc_layout(supported_nodes)

    # 生成图形 XML
    shape_xmls = []
    for node in supported_nodes:
        shape_xmls.append(gen_shape_xml(node, positions[node['id']]))

    edge_xmls = []
    for flow in flows:
        if flow['source'] in _unsupported_ids or flow['target'] in _unsupported_ids:
            continue
        if is_manual_branch:
            edge_xmls.append(gen_edge_xml_manual_branch(flow, positions, config))
        else:
            edge_xmls.append(gen_edge_xml(flow, positions))

    # 为 subProcess 内部 subFlows 生成 BPMNEdge（使用内部节点的 Shape 位置）
    for node in nodes:
        if node.get('type') == 'subProcess':
            sub_pos = positions[node['id']]
            sub_node_map = {sn['id']: sn for sn in node.get('subNodes', [])}
            # 从 gen_shape_xml 里提取内部节点坐标（重建内部位置）
            inner_positions = {}
            inner_x = sub_pos['x'] + 109
            sub_cy = sub_pos['cy']
            for sn in node.get('subNodes', []):
                stype = sn['type']
                if stype == 'startEvent':
                    sw, sh = 36, 36
                    sx, sy = inner_x, sub_cy - 18
                elif stype == 'endEvent':
                    sw, sh = 36, 36
                    sx, sy = inner_x, sub_cy - 18
                elif stype == 'userTask':
                    sw, sh = 100, 80
                    sx, sy = inner_x, sub_cy - 40
                else:
                    sw, sh = 100, 60
                    sx, sy = inner_x, sub_cy - 30
                inner_positions[sn['id']] = {
                    'x': sx, 'y': sy, 'w': sw, 'h': sh,
                    'cx': sx + sw / 2, 'cy': sub_cy,
                    'bottom': sy + sh,
                }
                inner_x += sw + 60
            for sf in node.get('subFlows', []):
                src_p = inner_positions.get(sf['source'])
                tgt_p = inner_positions.get(sf['target'])
                if src_p and tgt_p:
                    sf_id = sf['id']
                    sx2 = src_p['x'] + src_p['w']
                    sy2 = src_p['cy']
                    tx2 = tgt_p['x']
                    ty2 = tgt_p['cy']
                    edge_xmls.append(
                        f'      <bpmndi:BPMNEdge id="edge_{sf_id}" bpmnElement="{sf_id}">\n'
                        f'        <di:waypoint x="{sx2}" y="{sy2}" />\n'
                        f'        <di:waypoint x="{tx2}" y="{ty2}" />\n'
                        f'      </bpmndi:BPMNEdge>'
                    )

    # 生成边界定时器事件的 Shape 和 Edge（timerTarget 对应的连线）
    boundary_shape_xmls = []
    boundary_edge_xmls = []
    for node, event_id, timer in boundary_timer_nodes:
        task_pos = positions[node['id']]
        boundary_shape_xmls.append(gen_boundary_timer_shape(event_id, task_pos))
        timer_target = timer.get('timerTarget')
        if timer_target and timer_target in positions:
            tgt_pos = positions[timer_target]
            timer_flow_id = timer.get('timerFlowId') or f'flow_{event_id}'
            ex = task_pos['x'] + task_pos['w'] / 2 + 12 + 18  # 边界事件右边缘
            ey = task_pos['y'] + task_pos['h'] - 18 + 18       # 边界事件中心 y
            boundary_edge_xmls.append(
                f'      <bpmndi:BPMNEdge id="edge_{timer_flow_id}" bpmnElement="{timer_flow_id}">\n'
                f'        <di:waypoint x="{ex}" y="{ey}" />\n'
                f'        <di:waypoint x="{tgt_pos["cx"]}" y="{tgt_pos["y"]}" />\n'
                f'      </bpmndi:BPMNEdge>'
            )

    # 生成信号边界事件的 Shape 和 Edge
    for node, event_id, sig_cfg in boundary_signal_nodes:
        task_pos = positions[node['id']]
        boundary_shape_xmls.append(gen_signal_catch_shape(event_id, sig_cfg.get('name', ''), task_pos))
        target = sig_cfg.get('boundaryTarget')
        if target and target in positions:
            tgt_pos = positions[target]
            flow_id = 'flow_' + event_id
            ex = task_pos['x'] - 12 + 36
            ey = task_pos['y'] + task_pos['h'] - 18 + 18
            flow_xmls.append('    <bpmn2:sequenceFlow id="%s" sourceRef="%s" targetRef="%s" />' % (flow_id, event_id, target))
            boundary_edge_xmls.append(
                '      <bpmndi:BPMNEdge id="edge_%s" bpmnElement="%s">\n'
                '        <di:waypoint x="%s" y="%s" />\n'
                '        <di:waypoint x="%s" y="%s" />\n'
                '      </bpmndi:BPMNEdge>' % (flow_id, flow_id, ex, ey, tgt_pos['cx'], tgt_pos['y'])
            )

    # 生成消息边界事件的 Shape 和 Edge
    for node, event_id, msg_cfg in boundary_message_nodes:
        task_pos = positions[node['id']]
        boundary_shape_xmls.append(gen_message_boundary_shape(event_id, task_pos))
        target = msg_cfg.get('boundaryTarget')
        if target and target in positions:
            tgt_pos = positions[target]
            flow_id = 'flow_' + event_id
            ex = task_pos['x'] + task_pos['w'] / 2 + 12 + 36
            ey = task_pos['y'] + task_pos['h'] - 18 + 18
            flow_xmls.append('    <bpmn2:sequenceFlow id="%s" sourceRef="%s" targetRef="%s" />' % (flow_id, event_id, target))
            boundary_edge_xmls.append(
                '      <bpmndi:BPMNEdge id="edge_%s" bpmnElement="%s">\n'
                '        <di:waypoint x="%s" y="%s" />\n'
                '        <di:waypoint x="%s" y="%s" />\n'
                '      </bpmndi:BPMNEdge>' % (flow_id, flow_id, ex, ey, tgt_pos['cx'], tgt_pos['y'])
            )

    # 收集所有信号和消息定义（去重），放在 <bpmn2:definitions> 内、<bpmn2:process> 之前
    signal_names = set()
    message_names = set()
    for node in nodes:
        ntype = node.get('type', '')
        if ntype in ('signalThrow', 'signalCatch'):
            sn = node.get('signalName')
            if sn:
                signal_names.add(sn)
        if ntype == 'userTask':
            sb = node.get('signalBoundary', {})
            if sb.get('signalName'):
                signal_names.add(sb['signalName'])
        if ntype in ('messageThrow', 'messageCatch'):
            mn = node.get('messageName')
            if mn:
                message_names.add(mn)
        if ntype == 'userTask':
            mb = node.get('messageBoundary', {})
            if mb.get('messageName'):
                message_names.add(mb['messageName'])

    signal_def_lines = [f'  <bpmn2:signal id="{_signal_ref_id(s)}" name="{xml_escape(s)}" />' for s in sorted(signal_names)]
    message_def_lines = [f'  <bpmn2:message id="{_message_ref_id(m)}" name="{xml_escape(m)}" />' for m in sorted(message_names)]
    signal_message_defs = '\n'.join(signal_def_lines + message_def_lines)

    # 拼装完整 XML
    all_node_xmls = node_xmls + boundary_xmls
    all_shape_xmls = shape_xmls + boundary_shape_xmls
    all_edge_xmls = edge_xmls + boundary_edge_xmls

    xml = f'''{BPMN_HEADER}

{signal_message_defs}
  <bpmn2:process id="{process_key}" name="{xml_escape(process_name)}">
{SUBPROCESS_HQ_LISTENERS if config.get('isCountersignSubProcess') else (SUBPROCESS_LISTENERS if config.get('isSubProcess') else PROCESS_LISTENERS)}

{chr(10).join(all_node_xmls)}

{chr(10).join(flow_xmls)}
  </bpmn2:process>

  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="{process_key}">
{chr(10).join(all_shape_xmls)}
{chr(10).join(all_edge_xmls)}
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn2:definitions>'''

    return xml


def build_nodes_str(nodes, is_sub_process=False, is_countersign_sub=False):
    """构建 nodes 参数字符串（userTask + 子流程/会签子流程的 startEvent）"""
    parts = []
    include_start = is_sub_process or is_countersign_sub
    for node in nodes:
        if node['type'] == 'userTask':
            parts.append(f'id={node["id"]}###nodeName={node["name"]}@@@')
        elif include_start and node['type'] == 'startEvent':
            parts.append(f'id={node["id"]}###nodeName={node["name"]}@@@')
    return ''.join(parts)


def config_start_node_form(api_base, token, process_id, start_form):
    """配置子流程 start 节点的 PC 表单地址（必须在发布之前调用）。

    start_form 格式:
    {
        "formType": "desform",       # desform 或 online
        "formCode": "form_code",     # DesForm 编码（formType=desform 时必填）
        "mode": "detail"             # detail=查看（默认） / edit=编辑
    }
    """
    form_type = start_form.get('formType', 'desform')
    form_code = start_form.get('formCode', '')
    mode = start_form.get('mode', 'detail')

    if form_type == 'desform':
        url = '{{DOMAIN_URL}}/desform/' + mode + '/' + form_code + '/${BPM_DES_DATA_ID}?token={{TOKEN}}&taskId={{TASKID}}&skip=false'
    elif form_type == 'online':
        url = 'super/bpm/process/components/OnlineFormOpt' if mode == 'edit' else 'super/bpm/process/components/OnlineFormDetail'
    else:
        url = start_form.get('url', '')

    # 通过 API 查询 start 节点并更新
    result = api_request(api_base, token,
                         f'/act/process/extActProcessNode/list?processId={process_id}&pageNo=1&pageSize=50',
                         method='GET')
    records = result.get('result', {})
    if isinstance(records, dict):
        records = records.get('records', [])

    start_node = None
    for n in records:
        if n.get('processNodeCode') == 'start':
            start_node = n
            break

    if not start_node:
        print(f'  [警告] 未找到 start 节点记录，跳过表单地址配置')
        return False

    start_node['modelAndView'] = url
    update_result = api_request(api_base, token,
                                '/act/process/extActProcessNode/edit',
                                data=start_node, method='PUT')
    if update_result.get('success'):
        print(f'  start 节点表单地址配置成功: {url}')
        return True
    else:
        print(f'  [警告] start 节点配置失败: {update_result.get("message", "")}，尝试通过数据库配置...')
        return False


def save_process(api_base, token, config, bpmn_xml):
    """调用 saveProcess API"""
    process_id = config.get('processId', '0')
    process_key = config['processKey']
    process_name = config['processName']
    type_id = config.get('typeId', 'oa')
    is_sub = config.get('isSubProcess', False)
    is_cs_sub = config.get('isCountersignSubProcess', False)
    nodes_str = build_nodes_str(config['nodes'], is_sub_process=is_sub, is_countersign_sub=is_cs_sub)

    data = {
        'processDefinitionId': process_id,
        'processName': process_name,
        'processkey': process_key,
        'typeid': type_id,
        'lowAppId': '',
        'params': '',
        'nodes': nodes_str,
        'processDescriptor': bpmn_xml,
        'realProcDefId': '',
        'startType': config.get('startType', 'manual'),
    }

    result = api_request(api_base, token, '/act/designer/api/saveProcess',
                         data=data, content_type='application/x-www-form-urlencoded')
    return result


def link_form(api_base, token, process_id, form_config):
    """关联表单到流程。

    relationCode 规则：
    - formType=1 (Online): 'onl_{tableName}'
    - formType=2 (DesForm): 'desform_{formCode}'
    - formType=3 (自定义): 直接使用 relationCode
    如果用户已在 JSON 中写了正确前缀则直接使用，否则自动补全。
    """
    form_type = str(form_config.get('formType', '2'))
    relation_code = form_config.get('relationCode', '')
    # 自动补全 relationCode 前缀
    if form_type == '1' and not relation_code.startswith('onl_'):
        relation_code = f'onl_{relation_code}'
    elif form_type == '2' and not relation_code.startswith('desform_'):
        relation_code = f'desform_{relation_code}'
    link_data = {
        'processId': process_id,
        'formDealStyle': form_config.get('formDealStyle', 'default'),
        'formType': form_type,
        'relationCode': relation_code,
        'flowStatusCol': form_config.get('flowStatusCol', 'bpm_status'),
        'titleExp': form_config.get('titleExp', ''),
        'formTableName': form_config.get('formTableName', ''),
    }
    result = api_request(api_base, token, '/act/process/extActProcessForm/add', data=link_data)
    return result


def authorize_form(api_base, token, form_id, role_id='f6817f48af4fb3af11b9e8bf182f618b'):
    """为表单添加发起授权（保留已有授权）。

    form_id 取值：
    - formType=1 (Online): 传 Online 表单的 headId
    - formType=2 (DesForm): 传 DesForm 的表单记录 ID
    """
    import time as _time
    headers = {
        'X-Access-Token': token,
        'Content-Type': 'application/json; charset=UTF-8',
    }
    # 1. 查询已有授权
    ts = str(int(_time.time() * 1000))
    url = f'{api_base}/joa/designform/designFormCommuse/getAuthorizedDesignList?principalId={role_id}&authMode=role&_t={ts}'
    req = urllib.request.Request(url, headers=headers)
    resp = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    existing_ids = [item['id'] for item in resp.get('result', []) or []]

    # 2. 追加新表单ID
    if form_id not in existing_ids:
        existing_ids.append(form_id)

    # 3. 保存授权
    url = f'{api_base}/joa/designform/designFormCommuse/saveWorkorderAuth/{role_id}'
    data = json.dumps({
        'authMode': 'role',
        'authId': ','.join(existing_ids),
        'subDepartIds': '',
    }, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    resp = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    return resp


def get_authorize_form_id(api_base, token, form_config):
    """根据 formLink 配置获取用于授权的表单 ID。

    - formType=1 (Online): 通过 /online/cgform/head/list 查询 headId
    - formType=2 (DesForm): 通过 /desform/queryByIdOrCode 查询表单 ID
    返回 form_id 字符串，查询失败返回 None。
    """
    form_type = str(form_config.get('formType', '2'))
    table_name = form_config.get('formTableName', '')

    if form_type == '1' and table_name:
        # Online 表单 — 查询 headId
        result = api_request(api_base, token,
                             f'/online/cgform/head/list?tableName={table_name}&pageNo=1&pageSize=1',
                             method='GET')
        if result.get('success'):
            records = result.get('result', {}).get('records', [])
            if records:
                return records[0]['id']
    elif form_type == '2' and table_name:
        # DesForm — 查询表单 ID
        result = api_request(api_base, token,
                             f'/desform/queryByIdOrCode?desformCode={table_name}',
                             method='GET')
        if result.get('success') and result.get('result'):
            return result['result']['id']
    return None


def deploy_process(api_base, token, process_id):
    """发布流程 — PUT /act/process/extActProcess/deployProcess"""
    result = api_request(api_base, token, '/act/process/extActProcess/deployProcess',
                         data={'id': process_id}, method='PUT')
    return result


def set_draft_nodes_editable(api_base, token, process_id, config, form_url_config=None):
    """将 draft=true 的 userTask 节点设置为表单可编辑（formEditStatus=1），并设置表单地址。

    流程创建/发布后，draft 节点（提交申请/填写表单节点）默认 formEditStatus=0（只读），
    需要设置为 1 才能让发起人在该节点编辑表单。
    同时需要设置 modelAndView（PC表单地址）和 modelAndViewMobile（移动端表单地址），
    否则发起人无法正确打开表单编辑页面。

    Args:
        api_base: JeecgBoot 后端地址
        token: X-Access-Token
        process_id: 流程ID
        config: 流程配置（包含 nodes 列表）
        form_url_config: 表单地址配置（可选），格式：
            {
                "modelAndView": "PC端表单路径",
                "modelAndViewMobile": "移动端表单路径"
            }
            设计器表单(desform)示例：
                PC和移动端一致: {{DOMAIN_URL}}/desform/edit/{formCode}/${BPM_DES_DATA_ID}?token={{TOKEN}}&taskId={{TASKID}}&skip=false
            Online表单示例：
                PC: super/bpm/process/components/OnlineFormOpt
                移动端: check/onlineForm/flowedit

    Returns:
        list: 已更新的节点 code 列表
    """
    # 从配置中找出 draft 节点
    draft_node_ids = [n['id'] for n in config.get('nodes', [])
                      if n.get('draft', False) and n.get('type') == 'userTask']
    if not draft_node_ids:
        return []

    # 查询所有节点
    result = api_request(api_base, token,
        f'/act/process/extActProcessNode/list?processId={process_id}&pageNo=1&pageSize=50',
        method='GET')
    records = result.get('result', {})
    if isinstance(records, dict):
        records = records.get('records', [])

    updated = []
    for node in records:
        node_code = node.get('processNodeCode', '')
        if node_code in draft_node_ids:
            node['formEditStatus'] = '1'
            # 设置表单地址（PC端和移动端）
            if form_url_config:
                if 'modelAndView' in form_url_config:
                    node['modelAndView'] = form_url_config['modelAndView']
                if 'modelAndViewMobile' in form_url_config:
                    node['modelAndViewMobile'] = form_url_config['modelAndViewMobile']
            # 同步更新 nodeConfigJson 中的 formEditStatus
            config_json_str = node.get('nodeConfigJson', '{}')
            try:
                config_json = json.loads(config_json_str) if config_json_str else {}
                config_json['formEditStatus'] = True
                node['nodeConfigJson'] = json.dumps(config_json, ensure_ascii=False)
            except (json.JSONDecodeError, TypeError):
                pass
            update_result = api_request(api_base, token,
                '/act/process/extActProcessNode/edit',
                data=node, method='PUT')
            if update_result.get('success'):
                updated.append(node_code)
    return updated


# ====== 节点字段权限 ======

def get_desform_fields(api_base, token, form_code):
    """查询设计器表单的所有字段，返回 {字段名: {model, key, type}} 映射。

    递归遍历 desformDesignJson 中所有控件（含 card/grid/tabs 嵌套），
    排除纯布局控件（text, grid, card, tabs, divider）。
    """
    result = api_request(api_base, token,
                         f'/desform/queryByIdOrCode?desformCode={form_code}',
                         method='GET')
    if not result.get('success') or not result.get('result'):
        return {}

    design = json.loads(result['result']['desformDesignJson'])
    fields = {}

    def _walk(items):
        for w in items:
            wtype = w.get('type', '')
            # 优先用 name，其次用 label（Word布局字段名在 name 中，label 为空）
            name = w.get('name', '') or w.get('label', '')
            model = w.get('model', '')
            key = w.get('key', '')
            # 排除纯布局控件
            if wtype not in ('text', 'grid', 'card', 'tabs', 'divider', '') and model and name:
                fields[name] = {'model': model, 'key': key, 'type': wtype}
            # 递归子节点
            if 'list' in w and w['list']:
                _walk(w['list'])
            if 'columns' in w and w['columns']:
                for col in w['columns']:
                    if 'list' in col and col['list']:
                        _walk(col['list'])

    _walk(design.get('list', []))
    return fields


def get_online_form_fields(api_base, token, table_name):
    """查询 Online 表单的所有字段，返回 {字段名: {model, key, type}} 映射。

    Args:
        api_base: JeecgBoot 后端地址
        token: X-Access-Token
        table_name: 数据库表名（如 'crm_customer_apply'）

    Returns:
        dict: {字段名: {model, key, type}}，失败返回 {}
    """
    # Step 1: 通过表名查询 headId
    head_result = api_request(api_base, token,
                              f'/online/cgform/head/list?tableName={table_name}&pageNo=1&pageSize=10',
                              method='GET')
    records = head_result.get('result', {})
    if isinstance(records, dict):
        records = records.get('records', [])
    if not records:
        return {}
    head_id = records[0].get('id', '')
    if not head_id:
        return {}

    # Step 2: 通过 headId 查询字段列表
    field_result = api_request(api_base, token,
                               f'/online/cgform/field/listByHeadId?headId={head_id}',
                               method='GET')
    field_list = field_result.get('result', []) or []
    if isinstance(field_list, dict):
        field_list = field_list.get('records', [])

    fields = {}
    skip_fields = {'id', 'create_by', 'create_time', 'update_by', 'update_time', 'sys_org_code'}
    for f in field_list:
        db_field = f.get('dbFieldName', '')
        label = f.get('dbFieldTxt', '') or db_field
        field_type = f.get('fieldShowType', 'text')
        if db_field and db_field not in skip_fields:
            fields[label] = {'model': db_field, 'key': '', 'type': field_type}
            # 同时建立 model → info 的别名，支持直接用字段名匹配
            fields[db_field] = {'model': db_field, 'key': '', 'type': field_type}
    return fields


def set_node_field_permissions(api_base, token, process_id, node_code, form_code,
                               field_permissions, form_type='2'):
    """批量设置节点字段权限。

    Args:
        api_base: JeecgBoot 后端地址
        token: X-Access-Token
        process_id: 流程ID
        node_code: 节点编码（如 'task_draft'）
        form_code: 表单编码/表名（DesForm传表单编码，Online传数据库表名）
        field_permissions: 字段权限配置列表，每项格式：
            {
                "field": "字段名称（中文）或字段model",
                "visible": true,     # 可见（默认true）
                "editable": true,    # 可编辑（默认true）
                "required": false    # 必填（默认false）
            }
            联动规则：
              - required=true 时自动强制 visible=true, editable=true
              - visible=false 时自动强制 editable=false, required=false
        form_type: 表单类型，'1'=Online, '2'=DesForm（默认'2'）

    Returns:
        dict: {success: bool, updated: int, errors: list}
    """
    # 根据表单类型查询字段映射
    if form_type == '1':
        fields_map = get_online_form_fields(api_base, token, form_code)
    else:
        fields_map = get_desform_fields(api_base, token, form_code)
    if not fields_map:
        return {'success': False, 'updated': 0, 'errors': ['无法获取表单字段信息']}

    # 也建一个 model → field_info 的映射，支持用 model 直接匹配
    model_map = {info['model']: {'label': name, **info} for name, info in fields_map.items()}

    batch_data = []
    errors = []

    for perm in field_permissions:
        field_ref = perm.get('field', '')
        visible = perm.get('visible', True)
        editable = perm.get('editable', True)
        required = perm.get('required', False)

        # 联动规则：
        # 1. 隐藏时强制不可编辑+非必填
        # 2. 可编辑时强制可见
        # 3. 必填时强制可见+可编辑
        if not visible:
            editable = False
            required = False
        if editable:
            visible = True
        if required:
            visible = True
            editable = True

        # 查找字段 model 和 key
        field_info = fields_map.get(field_ref) or model_map.get(field_ref)
        if not field_info:
            errors.append(f'字段 "{field_ref}" 未找到')
            continue

        model = field_info['model']
        key = field_info.get('key', '')
        label = field_ref if field_ref in fields_map else field_info.get('label', field_ref)

        # Online 表单 ruleCode 格式：online:{表名}:{字段名}；DesForm 直接用 model/key
        if form_type == '1':
            rule_code = f'online:{form_code}:{model}'
            desform_key = None
        else:
            rule_code = model
            desform_key = key

        base_record = {
            'formType': form_type,
            'formBizCode': form_code,
            'processId': process_id,
            'processNodeCode': node_code,
            'ruleCode': rule_code,
            'ruleName': label,
            'required': 1 if required else 0,
        }
        if desform_key is not None:
            base_record['desformComKey'] = desform_key

        # ruleType=1: 可见性
        batch_data.append({**base_record, 'ruleType': '1', 'status': '1' if visible else '0'})
        # ruleType=2: 可编辑性（注意：status 与勾选状态相反，'0'=勾选=可编辑，'1'=未勾选=禁用）
        batch_data.append({**base_record, 'ruleType': '2', 'status': '0' if editable else '1'})

    if not batch_data:
        return {'success': False, 'updated': 0, 'errors': errors or ['无有效字段权限配置']}

    # 查询已有权限记录，获取 id 和 ruleName 用于更新（避免"规则编码已存在"错误）
    existing_result = api_request(api_base, token,
        f'/act/process/extActProcessNodePermission/list?processId={process_id}'
        f'&processNodeCode={node_code}&pageNo=1&pageSize=200',
        method='GET')
    existing_records = existing_result.get('result', {})
    if isinstance(existing_records, dict):
        existing_records = existing_records.get('records', [])
    # 建立 (ruleCode, ruleType) → 完整记录 映射
    existing_map = {}
    for rec in existing_records:
        key = (rec.get('ruleCode', ''), str(rec.get('ruleType', '')))
        existing_map[key] = rec

    # 合并已有记录的 id，并保留原始 ruleName（不得覆盖已有名称）
    for item in batch_data:
        lookup_key = (item['ruleCode'], item['ruleType'])
        if lookup_key in existing_map:
            existing = existing_map[lookup_key]
            item['id'] = existing.get('id', '')
            # 保留原 ruleName，防止将中文名覆盖为英文 model
            if existing.get('ruleName'):
                item['ruleName'] = existing['ruleName']

    result = api_request(api_base, token,
                         '/act/process/extActProcessNodePermission/saveOrUpdateBatch',
                         data=batch_data)
    success = result.get('success', False)
    return {
        'success': success,
        'updated': len(batch_data) // 2,
        'errors': errors,
        'message': result.get('message', ''),
    }


def edit_node_config(api_base, token, process_id, node_code, node_settings):
    """编辑流程节点配置（表单可编辑、抄送、转办、加签、驳回等开关）。

    Args:
        api_base: JeecgBoot 后端地址
        token: X-Access-Token
        process_id: 流程ID
        node_code: 节点编码
        node_settings: 需要更新的属性字典，可选 key:
            formEditStatus: '1'=可编辑
            ccStatus: '1'=启用抄送
            selnextUserStatus: '1'=选择下一步处理人
            msgStatus: '1'=消息通知
            addSignStatus: '1'=加签
            transferStatus: '1'=转办
            rejectStatus: '1'=驳回
            modelAndView: PC端表单地址
            modelAndViewMobile: 移动端表单地址

    Returns:
        dict: API 返回结果
    """
    # 查询节点记录
    result = api_request(api_base, token,
        f'/act/process/extActProcessNode/list?processId={process_id}&pageNo=1&pageSize=50',
        method='GET')
    records = result.get('result', {})
    if isinstance(records, dict):
        records = records.get('records', [])

    for node in records:
        if node.get('processNodeCode') == node_code:
            # 合并更新属性
            node.update(node_settings)
            return api_request(api_base, token,
                '/act/process/extActProcessNode/edit',
                data=node, method='PUT')

    return {'success': False, 'message': f'节点 {node_code} 未找到'}


# ====== JSON 配置解析（简化格式 → 完整格式） ======

def expand_config(config):
    """
    将简化配置展开为完整配置。

    简化格式示例:
    {
        "processName": "请假审批流程",
        "processKey": "oa_leave_approval",  // 可选，自动生成
        "typeId": "oa",
        "nodes": [
            {"id": "start", "type": "startEvent", "name": "开始"},
            {"id": "task_draft", "type": "userTask", "name": "提交申请", "draft": true,
             "assignee": {"type": "expression", "value": "applyUserId"}},
            {"id": "task_manager", "type": "userTask", "name": "部门经理审批",
             "assignee": {"type": "role", "value": "manager"}},
            {"id": "gateway_days", "type": "exclusiveGateway", "name": "请假天数判断",
             "default": "flow_le3_end"},
            {"id": "task_hr", "type": "userTask", "name": "HR审批",
             "assignee": {"type": "role", "value": "hr"}},
            {"id": "end", "type": "endEvent", "name": "结束"}
        ],
        "flows": [
            {"id": "flow_1", "source": "start", "target": "task_draft"},
            {"id": "flow_2", "source": "task_draft", "target": "task_manager"},
            {"id": "flow_3", "source": "task_manager", "target": "gateway_days"},
            {"id": "flow_gt3", "source": "gateway_days", "target": "task_hr", "name": "大于3天",
             "conditions": [{"field": "integer_xxx", "fieldType": "integer", "fieldName": "请假天数", "operator": "gt", "value": "3"}]},
            {"id": "flow_le3_end", "source": "gateway_days", "target": "end", "name": "3天及以内(默认)"},
            {"id": "flow_hr_end", "source": "task_hr", "target": "end"}
        ],
        "formLink": {
            "formType": "2",
            "relationCode": "desform_oa_leave_apply",
            "titleExp": "${select_user_xxx}提交的请假申请",
            "formTableName": "oa_leave_apply"
        }
    }
    """
    # 自动生成 processKey
    if 'processKey' not in config:
        ts = str(int(time.time() * 1000))
        config['processKey'] = f'process_{ts}'

    # ====== 手工分支（意见分支）自动检测 ======
    # 如果一个 userTask 有 2+ 条出线且都无条件，则为手工分支
    nodes = config['nodes']
    flows = config['flows']
    node_map = {n['id']: n for n in nodes}

    source_flows = {}
    for f in flows:
        source_flows.setdefault(f['source'], []).append(f)

    for node_id, out_flows in source_flows.items():
        if node_id in node_map and node_map[node_id]['type'] == 'userTask':
            if len(out_flows) >= 2 and all('conditions' not in f for f in out_flows):
                target_ids = [f['target'] for f in out_flows]
                config['_manualBranch'] = {
                    'sourceId': node_id,
                    'targets': target_ids,
                }
                # 为所有节点计算 _incoming / _outgoing
                incoming_map = {}
                outgoing_map = {}
                for f in flows:
                    outgoing_map.setdefault(f['source'], []).append(f['id'])
                    incoming_map.setdefault(f['target'], []).append(f['id'])
                for n in nodes:
                    n['_incoming'] = incoming_map.get(n['id'], [])
                    n['_outgoing'] = outgoing_map.get(n['id'], [])
                break  # 只支持一个手工分支源

    # 自动检测需要绕行的流（从网关出发但不连接到紧邻的下一个节点）
    if '_manualBranch' not in config:
        node_ids = [n['id'] for n in config['nodes']]
        for flow in config['flows']:
            if 'bypass' not in flow:
                src_idx = node_ids.index(flow['source']) if flow['source'] in node_ids else -1
                tgt_idx = node_ids.index(flow['target']) if flow['target'] in node_ids else -1
                src_node = config['nodes'][src_idx] if src_idx >= 0 else None
                if src_node and src_node['type'] in ('exclusiveGateway', 'parallelGateway', 'inclusiveGateway'):
                    if tgt_idx >= 0 and tgt_idx != src_idx + 1:
                        flow['bypass'] = True

    return config


# ====== 入口 ======

def main():
    parser = argparse.ArgumentParser(description='JeecgBoot BPM 流程创建工具')
    parser.add_argument('--api-base', required=True, help='JeecgBoot 后端地址')
    parser.add_argument('--token', required=True, help='X-Access-Token')
    parser.add_argument('--config', required=True, help='配置文件路径 (JSON)')
    parser.add_argument('--link-form', action='store_true', help='同时关联表单')
    parser.add_argument('--deploy', action='store_true', default=True, help='创建后自动发布流程（默认开启）')
    parser.add_argument('--no-deploy', action='store_true', help='创建后不自动发布')
    parser.add_argument('--dry-run', action='store_true', help='只生成 XML 不调用 API')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config = json.load(f)

    config = expand_config(config)

    # 生成 BPMN XML
    bpmn_xml = build_bpmn_xml(config)

    if args.dry_run:
        print(bpmn_xml)
        print(f'\nProcess Key: {config["processKey"]}')
        return

    # 保存流程
    print(f'正在创建流程: {config["processName"]}')
    result = save_process(args.api_base, args.token, config, bpmn_xml)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result.get('success'):
        print(f'\n流程创建失败: {result.get("msg", "")}')
        sys.exit(1)

    process_id = result.get('obj') or config.get('processId', '')
    # obj=null 说明是更新操作，按 processKey 查询真实 ID
    if not process_id:
        process_key = config['processKey']
        try:
            import urllib.parse as _up
            q = _up.urlencode({'pageNo': 1, 'pageSize': 5})
            qr = api_request(args.api_base, args.token,
                             f'/act/process/extActProcess/list?{q}', method='GET')
            for rec in (qr.get('result') or {}).get('records', []):
                if rec.get('processName') == config['processName']:
                    process_id = rec.get('id', '')
                    break
        except Exception as _e:
            print(f'  [警告] 查询流程ID失败: {_e}')

    print(f'\n{"=" * 50}')
    print(f'流程创建成功')
    print(f'{"=" * 50}')
    print(f'  流程ID:   {process_id}')
    print(f'  流程名称: {config["processName"]}')
    print(f'  流程Key:  {config["processKey"]}')

    # 子流程：配置 start 节点表单地址（必须在发布之前）
    start_form = config.get('startNodeForm')
    if start_form and config.get('isSubProcess') and process_id:
        print(f'\n正在配置 start 节点表单地址（发布前）...')
        config_start_node_form(args.api_base, args.token, process_id, start_form)

    # 自动发布流程（默认开启，--no-deploy 关闭）
    if not args.no_deploy and process_id:
        print(f'\n正在发布流程...')
        deploy_result = deploy_process(args.api_base, args.token, process_id)
        if deploy_result.get('success'):
            print(f'  流程发布成功')
        else:
            print(f'  流程发布失败: {deploy_result.get("message", "")}')

    # 设置 draft 节点表单可编辑（自动推导表单地址）
    if process_id:
        form_url_config = None
        form_config = config.get('formLink')
        # 子流程复用父流程表单地址（不关联自己的 formLink，只需配置 draft 节点 PC 地址）
        draft_node_form = config.get('draftNodeForm')
        if draft_node_form and not form_config:
            _dnf_type = draft_node_form.get('formType', 'desform')
            _dnf_code = draft_node_form.get('formCode', '')
            _dnf_mode = draft_node_form.get('mode', 'edit')
            if _dnf_type == 'desform':
                _dnf_url = '{{DOMAIN_URL}}/desform/%s/%s/${BPM_DES_DATA_ID}?token={{TOKEN}}&taskId={{TASKID}}&skip=false' % (_dnf_mode, _dnf_code)
                form_url_config = {'modelAndView': _dnf_url, 'modelAndViewMobile': 'check/desForm/flowedit'}
            elif _dnf_type == 'online':
                _dnf_url = 'super/bpm/process/components/OnlineFormOpt' if _dnf_mode == 'edit' else 'super/bpm/process/components/OnlineFormDetail'
                form_url_config = {'modelAndView': _dnf_url, 'modelAndViewMobile': 'check/onlineForm/flowedit'}
        if form_config:
            form_type = str(form_config.get('formType', ''))
            if form_type == '1':
                # Online 表单
                form_url_config = {
                    'modelAndView': 'super/bpm/process/components/OnlineFormOpt',
                    'modelAndViewMobile': 'check/onlineForm/flowedit',
                }
            elif form_type == '2':
                # DesForm 设计器表单
                form_code = form_config.get('formTableName', '') or form_config.get('relationCode', '')
                form_url_config = {
                    'modelAndView': '{{DOMAIN_URL}}/desform/edit/%s/${BPM_DES_DATA_ID}?token={{TOKEN}}&taskId={{TASKID}}&skip=false' % form_code,
                    'modelAndViewMobile': 'check/desForm/flowedit',
                }
            elif form_type == '3':
                # 自定义开发表单 — 从 formLink.formUrl 或自动推导
                custom_form_url = form_config.get('formUrl', '')
                if not custom_form_url:
                    # 自动推导：relationCode 格式 dev_{tableName}_001，推导视图目录和实体名
                    relation_code = form_config.get('relationCode', '')
                    table_name = form_config.get('formTableName', '')
                    if table_name:
                        # 表名转驼峰作为实体名，如 biz_visitor_register -> BizVisitorRegister
                        parts = table_name.split('_')
                        entity_name = ''.join(p.capitalize() for p in parts)
                        # 推导视图目录：取表名前缀作为模块名
                        # 常见模式：biz_xxx -> biz, demo_xxx -> demo, oa_xxx -> oa
                        prefix = parts[0] if len(parts) > 1 else table_name
                        # 尝试从 nodes 的 flow 中推导，或用简单规则
                        view_dir = prefix if prefix not in ('biz', 'sys') else parts[1] if len(parts) > 1 else prefix
                        # 对于 biz_ 前缀，使用第二段作为目录（如 biz_visitor_register -> visitor）
                        if prefix == 'biz' and len(parts) > 2:
                            view_dir = parts[1]
                        custom_form_url = '%s/components/%sForm?edit=1' % (view_dir, entity_name)
                form_url_config = {
                    'modelAndView': custom_form_url,
                    'modelAndViewMobile': '',
                }
        updated_nodes = set_draft_nodes_editable(args.api_base, args.token, process_id, config, form_url_config)
        if updated_nodes:
            form_addr = form_url_config.get('modelAndView', '') if form_url_config else ''
            print(f'\n已设置节点表单可编辑: {", ".join(updated_nodes)}')
            if form_addr:
                print(f'  表单地址: {form_addr}')
            # 草稿节点配置在发布后修改，必须重新发布才能生效
            if not args.no_deploy:
                print(f'\n草稿节点配置已更新，重新发布流程...')
                redeploy_result = deploy_process(args.api_base, args.token, process_id)
                if redeploy_result.get('success'):
                    print(f'  流程重新发布成功')
                else:
                    print(f'  流程重新发布失败: {redeploy_result.get("message", "")}')

    # 关联表单
    form_config = config.get('formLink')
    if (args.link_form or form_config) and form_config and process_id:
        print(f'\n正在关联表单...')
        link_result = link_form(args.api_base, args.token, process_id, form_config)
        print(json.dumps(link_result, ensure_ascii=False, indent=2))
        if link_result.get('success'):
            print(f'  表单关联成功: {form_config.get("relationCode", "")}')
        else:
            print(f'  表单关联失败: {link_result.get("message", "")}')

        # 自动发起授权（formType=1 Online 或 formType=2 DesForm）
        form_type = str(form_config.get('formType', '2'))
        if form_type in ('1', '2'):
            print(f'\n正在执行发起授权...')
            auth_form_id = get_authorize_form_id(args.api_base, args.token, form_config)
            if auth_form_id:
                auth_result = authorize_form(args.api_base, args.token, auth_form_id)
                if auth_result.get('success'):
                    print(f'  发起授权成功 (formId={auth_form_id})')
                else:
                    print(f'  发起授权失败: {auth_result.get("message", "")}')
            else:
                print(f'  未能获取表单ID，请手动授权')


if __name__ == '__main__':
    main()
