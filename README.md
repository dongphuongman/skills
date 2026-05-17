# JeecgBoot & JimuReport AI Skills — Claude Code 技能集合

> 基于 Claude Code 的 AI 技能集合，覆盖 **JeecgBoot 低代码平台** 和 **JimuReport 积木报表** 两大产品，通过自然语言驱动，**一句话生成代码、表单、流程、报表、图表、大屏、仪表盘**，覆盖企业级开发全场景。

## 视频文档

- **视频教程：** [Skills+JeecgBoot自然语言编程实战](https://www.bilibili.com/video/BV1KKwTzJEbX/)
- **在线文档：** [Skills使用文档](https://help.jeecg.com/java/ai/skills/skill-comparison)



## 🚀 一键安装（推荐）

> **Claude Code + DeepSeek v4 一键全栈方案** — 国内镜像加速、**无需翻墙**、跑完即用。

一行命令自动装齐 `Node.js · Python · Git · Claude Code · JEECG Skills`，并写入 DeepSeek v4 作为模型后端。

### Windows（PowerShell）

```powershell
irm https://www.qiaoqiaoyun.com/claude/boot.ps1 | iex
```

> 请在 **PowerShell（建议管理员）** 中执行。若提示脚本被禁，先运行：`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### macOS / Linux（Bash / Zsh）

```bash
curl -fsSL https://www.qiaoqiaoyun.com/claude/install-claude-code.sh | bash
```

> 如需 root 权限，前缀加 `sudo`。

### 安装内容

- **Node.js 22 LTS · Python 3.12 · Git · Claude Code · JEECG Skills 全量**（华为云 / npmmirror 国内镜像加速）
- 克隆 [gitee.com/jeecg/skills](https://gitee.com/jeecg/skills) 到 `~/.claude/skills/`（已存在则自动 `git pull` 增量更新）
- 写入用户级环境变量 `ANTHROPIC_BASE_URL / ANTHROPIC_AUTH_TOKEN / ANTHROPIC_MODEL=deepseek-v4-pro`
- 幂等运行，重复跑只补缺；重装/换 Key 用 `--force`

> ⚠️ DeepSeek 按 token 计费，需自备 API Key：[DeepSeek 开放平台 申请 API Key](https://platform.deepseek.com/api_keys)

### 安装完成

```bash
claude
> 帮我生成一个订单管理功能
```

Windows 安装完成后请**新开一个 PowerShell 窗口**，环境变量才会生效；Linux/macOS 执行 `source ~/.bashrc && claude`。

> 💡 **已经装了 Claude Code？** 跳到本文末尾的 [手工安装 Skills](#手工安装-skills-技能) 段落，只追加 Skills 目录。

---

## 功能清单

### JeecgBoot 技能

| 序号 | 技能名称 | 功能说明 | 触发关键词 | 产出物 |
|------|---------|---------|-----------|--------|
| 1 | **jeecg-codegen** | 代码生成器 — 自然语言描述业务需求，自动生成全套 CRUD 代码 | 代码生成、生成代码、创建模块、新增功能、建表、加字段 | Java + Vue3 + SQL |
| 2 | **jeecg-onlform** | Online 表单生成器 — 自然语言描述表结构，自动创建 Online 表单（CRUD） | 创建Online表单、创建online表、在线表单 | Online 表单配置 |
| 3 | **jeecg-onlreport** | Online 报表生成器 — 自然语言描述报表需求，自动生成 SQL 报表 | 创建报表、生成报表、SQL报表、数据报表 | Online 报表配置 |
| 4 | **jeecg-desform** | 设计器表单生成器 — 自然语言描述表单需求或提供截图，自动生成表单 JSON 并创建 | AI设计表单、生成表单、创建表单、按照截图生成表单 | 设计器表单 JSON |
| 5 | **jeecg-onlchart** | Online 图表生成器 — 自然语言描述图表需求，自动生成数据可视化图表 | 创建图表、生成图表、柱状图、折线图、饼图、可视化 | Online 图表配置 |
| 6 | **jeecg-bpmn** | BPM 流程生成器 — 自然语言描述审批流程，自动生成 BPMN XML 并部署 | 创建流程、生成流程、审批流程、工作流、BPM | Flowable BPMN 2.0 XML |

### JimuReport 积木报表技能

| 序号 | 技能名称 | 功能说明 | 触发关键词 | 产出物 |
|------|---------|---------|-----------|--------|
| 7 | **jimubi-bigscreen** | 大屏生成器 — 自然语言描述大屏需求，自动生成全屏数据可视化大屏 | 创建大屏、生成大屏、数据大屏、可视化大屏、监控大屏、BI大屏 | Drag Page 大屏配置 |
| 8 | **jimubi-dashboard** | 仪表盘生成器 — 自然语言描述看板需求，自动生成数据仪表盘 | 创建仪表盘、数据看板、创建看板、统计看板、运营看板 | Drag Page 仪表盘配置 |
| 9 | **jimureport** | 积木报表生成器 — 自然语言描述报表需求或提供截图，自动生成积木报表（全类型支持） | 积木报表、jmreport、Excel报表、数据填报、可视化报表、打印报表、按照截图生成报表 | 积木报表配置 |



## 手工安装 Skills 技能

> 已经在用 Claude Code 的用户，可以**不跑一键脚本**，直接把 Skills 仓库克隆到 `~/.claude/skills`。

### 一行 git clone（推荐）

```bash
git clone https://github.com/jeecgboot/skills.git ~/.claude/skills
```

已存在则增量更新：

```bash
cd ~/.claude/skills && git pull
```

### 只装部分 Skill（局部复制）

将所需的 Skill 目录复制到 Claude Code 的 skills 目录：

```bash
# macOS / Linux
cp -r jeecg-codegen ~/.claude/skills/
cp -r jimureport ~/.claude/skills/

# Windows
xcopy jeecg-codegen %USERPROFILE%\.claude\skills\jeecg-codegen\ /E /I
xcopy jimureport %USERPROFILE%\.claude\skills\jimureport\ /E /I
```

### 前置依赖

- **Python 3.12+**（部分 Skill 通过 Python 脚本调用后端 API），下载：[python.org/downloads](https://www.python.org/downloads/)
- 安装后请确保 `python` / `python3` 命令在终端可用（`python --version`）

安装后需要根据实际项目修改 Skill 中的路径和数据库连接配置，具体见各 Skill 的 `SKILL.md`。


## 技能详情

### 1. jeecg-codegen — 代码生成器

**一句话**：用自然语言描述业务需求，自动生成 JeecgBoot 全套 CRUD 代码。

**核心能力**：
- 支持单表、树表、一对多（主子表）三种模式
- 智能字段推导：名称→Input、金额→InputNumber、状态→字典下拉、图片→图片上传
- 字典智能匹配：自动读取 sys_dict 表，为字段匹配已有字典编码
- 已有表反向生成：给表名即可，自动查询 DDL 生成代码
- 增量修改：加/删/改字段，精确修改每个相关文件
- 主键策略自适应、Flyway 版本号自动递增

**使用文档**：[skill-usage-guide.md](jeecg-codegen/docs/skill-usage-guide.md)


### 2. jeecg-onlform — Online 表单生成器

**一句话**：用自然语言描述表结构，自动通过 API 创建 Online 表单（元数据驱动 CRUD）。

**核心能力**：
- 元数据驱动，无需写代码即可生成完整 CRUD 页面
- 单表 / 主子表（一对多/一对一）/ 树表 三种模式
- 智能字段类型推导和控件映射（30+ 控件类型）
- 字典智能匹配（系统字典 / 字典表 / 带条件字典表）
- 增量字段修改（加/删/改字段，无需重新创建）
- 自动同步数据库 + 生成菜单 SQL


### 3. jeecg-onlreport — Online 报表生成器

**一句话**：用自然语言描述报表需求，自动生成 SQL 并通过 API 创建 Online 数据报表。

**核心能力**：
- SQL 驱动的数据报表，支持查询、排序、导出
- 智能字段配置：显示/隐藏、查询模式（模糊/精确/范围）、排序、合计
- 字段中文名自动翻译
- 字典和取值表达式支持
- 分组表头、字段跳转等高级功能
- SQL 参数化查询（Velocity 模板语法）

---

### 4. jeecg-desform — 设计器表单生成器

**一句话**：用自然语言描述表单需求或提供截图，自动生成设计器表单 JSON 并通过 API 创建。

**核心能力**：
- 支持按照截图原样生成表单：提供表单截图/图片，AI 自动识别布局和字段，还原生成对应表单
- 支持 40+ 控件类型：文本、数字、选择、日期、上传、富文本、人员选择等
- 支持主子表（明细表）设计
- 支持布局控制：一行多字段、分栏布局
- 关联记录 + 他表字段、公式计算
- 支持表单编辑和删除


### 5. jeecg-onlchart — Online 图表生成器

**一句话**：用自然语言描述图表需求，自动生成 SQL 并通过 API 创建 Online 数据可视化图表。

**核心能力**：
- 支持柱状图、折线图、饼图、组合图表
- 智能推导 X/Y 轴字段：维度字段→X 轴，度量字段→Y 轴
- 根据数据特征自动推荐图表类型
- 字段中文名翻译、字典自动关联
- 组合图表（折线+柱状同时展示）
- SQL 参数化查询、动态数据源


### 6. jeecg-bpmn — BPM 流程生成器

**一句话**：用自然语言描述审批流程，自动生成 Flowable BPMN 2.0 XML 并通过 API 部署。

**核心能力**：
- 支持顺序审批、条件分支（排他网关）、并行审批（并行网关）
- 支持会签（多实例任务）、子流程
- 多种审批人类型：固定人、发起人、部门负责人、角色组、上一节点指派
- 条件表达式自动生成：金额判断、天数判断、状态判断
- 同一会话内可连续修改流程


### 7. jimubi-bigscreen — 大屏生成器

**一句话**：用自然语言描述大屏需求，自动生成全屏数据可视化大屏并通过 API 创建。

**核心能力**：
- 全屏展示模式，绝对定位（像素坐标），深色主题
- 默认 1920×1080 分辨率，适用于监控室/展厅/展示墙
- 丰富组件支持：数字翻牌、折线图、柱状图、饼图、地图、滚动表格、排行榜等
- 装饰元素：边框（JDragBorder）、装饰条（JDragDecoration）增强视觉效果
- 自定义背景图和主题配色

> 注意：大屏与仪表盘使用完全不同的布局和样式体系，仪表盘请使用 `jimubi-dashboard`。


### 8. jimubi-dashboard — 仪表盘生成器

**一句话**：用自然语言描述看板需求，自动生成栅格布局数据仪表盘并通过 API 创建。

**核心能力**：
- 24 列栅格布局，亮色主题，卡片式设计
- 适用于日常数据看板、运营统计面板
- 支持数字卡片、折线图、柱状图、饼图、表格、排行榜、仪表盘等组件
- 智能栅格分配：数字卡片 4 个一行，图表半宽或全宽自动排列
- 卡片头与 ECharts 标题智能去重

> 注意：仪表盘与大屏使用完全不同的布局和样式体系，大屏请使用 `jimubi-bigscreen`。


### 9. jimureport — 积木报表生成器

**一句话**：用自然语言描述报表需求或提供截图，自动生成积木报表（全类型支持）并通过 API 创建。

**核心能力**：
- 支持按照截图原样生成报表：提供报表截图/图片，AI 自动识别表格布局、字段和样式，还原生成对应报表
- 全类型报表支持：数据报表、打印报表、分组报表（横向/纵向分组小计）、循环报表（loopBlock 明细循环）、数据填报等
- 可视化 Excel 设计器风格，支持自由布局、合并单元格、多 Sheet
- 数据绑定：`#{数据集编码.字段名}` 模板语法
- 支持数据填报（submitForm），用户可直接在报表中录入和提交数据
- 精细打印控制：纸张大小、边距、方向，适用于票据、证书、处方等打印场景
- CSS/JS/Python 增强能力
- 与 Online 报表（cgreport）互补：积木报表侧重复杂布局与多样化报表类型，Online 报表侧重快速配置


## 使用方式

所有技能都在 Claude Code 对话中通过自然语言触发，无需手动调用。只需描述你的需求，AI 会自动识别并使用对应技能。

### 通用交互流程

```
1. 用自然语言描述需求
2. AI 询问后端地址和 Token（如需调用 API）
3. AI 展示配置摘要，等待确认
4. 确认后自动执行，返回结果
5. 可在同一会话中继续修改
```

### Token 获取方式

1. 打开 JeecgBoot 系统并登录
2. 按 F12 打开浏览器开发者工具
3. 切换到 Network 标签页
4. 点击任意请求，在 Request Headers 中找到 `X-Access-Token`
5. 复制完整的 Token 值

---

## 适用版本

- **JeecgBoot** 3.x（Spring Boot 3 + Jakarta + MyBatis-Plus）
- **JimuReport** 积木报表 1.7+
- **前端** Vue3 + TypeScript + Vite + Ant Design Vue 4
- **Claude Code** 最新版本
