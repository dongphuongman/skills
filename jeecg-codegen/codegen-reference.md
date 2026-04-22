# JeecgBoot 代码生成参考模板

本文档包含 JeecgBoot CRUD 代码的完整模板骨架，用 `{{变量}}` 标注替换位置。

## 变量说明

| 变量 | 说明 | 示例 |
|------|------|------|
| `{{tableName}}` | 数据库表名 | `biz_goods` |
| `{{entityName}}` | 实体类名(PascalCase) | `BizGoods` |
| `{{entityName_uncap}}` | 实体变量名(camelCase) | `bizGoods` |
| `{{entityPackage}}` | 模块包名 | `biz` |
| `{{entityPackagePath}}` | URL路径(同entityPackage或含/) | `biz` |
| `{{description}}` | 功能描述 | `商品管理` |
| `{{today}}` | 生成日期 | `2026-03-11` |
| `{{timestamp}}` | 13位毫秒级真实时间戳(用于菜单ID，通过`date +%s%3N`获取) | `1741704000123` |
| `{{moduleRoot}}` | 后端模块根路径 | `jeecg-module-system/jeecg-system-biz` |
| `{{viewDir}}` | 前端视图目录 | `biz/goods` |

---

## A. 单表模式

### 生成文件清单

**后端 6 个文件：**
1. `{{moduleRoot}}/src/main/java/org/jeecg/modules/{{entityPackage}}/entity/{{entityName}}.java`
2. `{{moduleRoot}}/src/main/java/org/jeecg/modules/{{entityPackage}}/controller/{{entityName}}Controller.java`
3. `{{moduleRoot}}/src/main/java/org/jeecg/modules/{{entityPackage}}/service/I{{entityName}}Service.java`
4. `{{moduleRoot}}/src/main/java/org/jeecg/modules/{{entityPackage}}/service/impl/{{entityName}}ServiceImpl.java`
5. `{{moduleRoot}}/src/main/java/org/jeecg/modules/{{entityPackage}}/mapper/{{entityName}}Mapper.java`
6. `{{moduleRoot}}/src/main/java/org/jeecg/modules/{{entityPackage}}/mapper/xml/{{entityName}}Mapper.xml`

**前端 - vue3 封装风格（4个文件）：**
7. `src/views/{{viewDir}}/{{entityName}}.api.ts`
8. `src/views/{{viewDir}}/{{entityName}}.data.ts`
9. `src/views/{{viewDir}}/{{entityName}}List.vue`
10. `src/views/{{viewDir}}/components/{{entityName}}Modal.vue`

**前端 - vue3Native 原生风格（5个文件）：**
7. `src/views/{{viewDir}}/{{entityName}}.api.ts`
8. `src/views/{{viewDir}}/{{entityName}}.data.ts`
9. `src/views/{{viewDir}}/{{entityName}}List.vue`
10. `src/views/{{viewDir}}/components/{{entityName}}Modal.vue`
11. `src/views/{{viewDir}}/components/{{entityName}}Form.vue`

**SQL（1个文件）：**
12. Flyway SQL: `jeecg-module-system/jeecg-system-start/src/main/resources/db/flyway/V{{version}}__{{description}}.sql`

---

### A1. Entity.java

```java
package org.jeecg.modules.{{entityPackage}}.entity;

import java.io.Serializable;
import java.util.Date;
import java.math.BigDecimal;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import com.fasterxml.jackson.annotation.JsonFormat;
import org.springframework.format.annotation.DateTimeFormat;
import org.jeecgframework.poi.excel.annotation.Excel;
import org.jeecg.common.aspect.annotation.Dict;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.EqualsAndHashCode;
import lombok.experimental.Accessors;

/**
 * @Description: {{description}}
 * @Author: jeecg-boot
 * @Date: {{today}}
 * @Version: V1.0
 */
@Data
@TableName("{{tableName}}")
@Accessors(chain = true)
@EqualsAndHashCode(callSuper = false)
@Schema(description = "{{description}}")
public class {{entityName}} implements Serializable {
    private static final long serialVersionUID = 1L;

    // === 主键字段（根据表DDL自适应） ===

    // --- 方式1: JeecgBoot 标准字符串主键 (varchar(36)/varchar(32), 无AUTO_INCREMENT) ---
    // @TableId(type = IdType.ASSIGN_ID)
    // @Schema(description = "主键")
    // private String id;

    // --- 方式2: int 自增主键 (int AUTO_INCREMENT) ---
    // @TableId(type = IdType.AUTO)
    // @Schema(description = "主键")
    // private Integer id;

    // --- 方式3: bigint 自增主键 (bigint AUTO_INCREMENT) ---
    // @TableId(type = IdType.AUTO)
    // @Schema(description = "主键")
    // private Long id;

    // --- 方式4: bigint 雪花ID (bigint, 无AUTO_INCREMENT) ---
    // @TableId(type = IdType.ASSIGN_ID)
    // @Schema(description = "主键")
    // private Long id;

    // === 业务字段（根据需求生成） ===
    // 每个业务字段按以下规则生成注解：

    // --- String 字段 ---
    // @Excel(name = "字段注释", width = 15)
    // private String fieldName;

    // --- 带字典的 String 字段 ---
    // @Excel(name = "字段注释", width = 15, dicCode = "dict_code")
    // @Dict(dicCode = "dict_code")
    // private String fieldName;

    // --- 关联表字典的 String 字段 ---
    // @Excel(name = "字段注释", width = 15, dictTable = "sys_user", dicText = "realname", dicCode = "username")
    // @Dict(dictTable = "sys_user", dicText = "realname", dicCode = "username")
    // private String fieldName;

    // --- Integer 字段 ---
    // @Excel(name = "字段注释", width = 15)
    // private Integer fieldName;

    // --- BigDecimal 字段 ---
    // @Excel(name = "字段注释", width = 15)
    // private BigDecimal fieldName;

    // --- Date 字段 ---
    // @Excel(name = "字段注释", width = 15, format = "yyyy-MM-dd")
    // @JsonFormat(timezone = "GMT+8", pattern = "yyyy-MM-dd")
    // @DateTimeFormat(pattern = "yyyy-MM-dd")
    // private Date fieldName;

    // --- DateTime 字段 ---
    // @Excel(name = "字段注释", width = 20, format = "yyyy-MM-dd HH:mm:ss")
    // @JsonFormat(timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    // @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    // private Date fieldName;

    // === 系统字段（仅在表中实际存在时才生成，不要盲目添加！） ===

    // --- 以下每个字段都需要检查表DDL中是否存在对应列，不存在则不生成 ---

    // 如果表有 create_by 列:
    // /**创建人*/
    // @Schema(description = "创建人")
    // private String createBy;

    // 如果表有 create_time 列:
    // /**创建日期*/
    // @JsonFormat(timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    // @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    // @Schema(description = "创建日期")
    // private Date createTime;

    // 如果表有 update_by 列:
    // /**更新人*/
    // @Schema(description = "更新人")
    // private String updateBy;

    // 如果表有 update_time 列:
    // /**更新日期*/
    // @JsonFormat(timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    // @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    // @Schema(description = "更新日期")
    // private Date updateTime;

    // 如果表有 sys_org_code 列:
    // /**所属部门*/
    // @Schema(description = "所属部门")
    // private String sysOrgCode;

    // 新建表时默认添加全部系统字段；已有表按实际DDL决定。
}
```

**字典注解规则：**
- 下拉/单选/多选/搜索框 + 字典编码: `@Dict(dicCode = "xxx")`
- 下拉/单选/多选/搜索框 + 字典表: `@Dict(dictTable = "tableName", dicText = "textField", dicCode = "codeField")`
- 用户选择: `@Dict(dictTable = "sys_user", dicText = "realname", dicCode = "username")`
- 部门选择: `@Dict(dictTable = "sys_depart", dicText = "depart_name", dicCode = "id")`

---

### A2. Controller.java

> **⚠️ 重要：本节模板仅适用于单表。一对多表的 Controller 请使用 C6 节的完整模板，禁止使用 `extends JeecgController`。**

```java
package org.jeecg.modules.{{entityPackage}}.controller;

import java.util.Arrays;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.jeecg.common.api.vo.Result;
import org.jeecg.common.system.query.QueryGenerator;
import org.jeecg.common.util.oConvertUtils;
import org.jeecg.modules.{{entityPackage}}.entity.{{entityName}};
import org.jeecg.modules.{{entityPackage}}.service.I{{entityName}}Service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import lombok.extern.slf4j.Slf4j;

import org.jeecg.common.system.base.controller.JeecgController;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.ModelAndView;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.Operation;
import org.jeecg.common.aspect.annotation.AutoLog;
import org.apache.shiro.authz.annotation.RequiresPermissions;

/**
 * @Description: {{description}}
 * @Author: jeecg-boot
 * @Date: {{today}}
 * @Version: V1.0
 */
@Tag(name = "{{description}}")
@RestController
@RequestMapping("/{{entityPackagePath}}/{{entityName_uncap}}")
@Slf4j
public class {{entityName}}Controller extends JeecgController<{{entityName}}, I{{entityName}}Service> {
    @Autowired
    private I{{entityName}}Service {{entityName_uncap}}Service;

    /**
     * 分页列表查询
     */
    @Operation(summary = "{{description}}-分页列表查询")
    @GetMapping(value = "/list")
    public Result<IPage<{{entityName}}>> queryPageList({{entityName}} {{entityName_uncap}},
                                                       @RequestParam(name = "pageNo", defaultValue = "1") Integer pageNo,
                                                       @RequestParam(name = "pageSize", defaultValue = "10") Integer pageSize,
                                                       HttpServletRequest req) {
        QueryWrapper<{{entityName}}> queryWrapper = QueryGenerator.initQueryWrapper({{entityName_uncap}}, req.getParameterMap());
        Page<{{entityName}}> page = new Page<>(pageNo, pageSize);
        IPage<{{entityName}}> pageList = {{entityName_uncap}}Service.page(page, queryWrapper);
        return Result.OK(pageList);
    }

    /**
     * 添加
     */
    @AutoLog(value = "{{description}}-添加")
    @Operation(summary = "{{description}}-添加")
    @RequiresPermissions("{{entityPackage}}:{{tableName}}:add")
    @PostMapping(value = "/add")
    public Result<String> add(@RequestBody {{entityName}} {{entityName_uncap}}) {
        {{entityName_uncap}}Service.save({{entityName_uncap}});
        return Result.OK("添加成功！");
    }

    /**
     * 编辑
     */
    @AutoLog(value = "{{description}}-编辑")
    @Operation(summary = "{{description}}-编辑")
    @RequiresPermissions("{{entityPackage}}:{{tableName}}:edit")
    @RequestMapping(value = "/edit", method = {RequestMethod.PUT, RequestMethod.POST})
    public Result<String> edit(@RequestBody {{entityName}} {{entityName_uncap}}) {
        {{entityName_uncap}}Service.updateById({{entityName_uncap}});
        return Result.OK("编辑成功!");
    }

    /**
     * 通过id删除
     * 注意：参数类型需与Entity主键类型一致
     * - String主键: @RequestParam(name = "id", required = true) String id
     * - Integer主键: @RequestParam(name = "id", required = true) Integer id
     * - Long主键:    @RequestParam(name = "id", required = true) Long id
     */
    @AutoLog(value = "{{description}}-通过id删除")
    @Operation(summary = "{{description}}-通过id删除")
    @RequiresPermissions("{{entityPackage}}:{{tableName}}:delete")
    @DeleteMapping(value = "/delete")
    public Result<String> delete(@RequestParam(name = "id", required = true) String id) {
        {{entityName_uncap}}Service.removeById(id);
        return Result.OK("删除成功!");
    }

    /**
     * 批量删除
     * 注意：当主键为 Integer/Long 时，需将 ids 转为对应类型的 List：
     * - Integer: Arrays.stream(ids.split(",")).map(Integer::parseInt).collect(Collectors.toList())
     * - Long:    Arrays.stream(ids.split(",")).map(Long::parseLong).collect(Collectors.toList())
     * - String:  Arrays.asList(ids.split(","))
     */
    @AutoLog(value = "{{description}}-批量删除")
    @Operation(summary = "{{description}}-批量删除")
    @RequiresPermissions("{{entityPackage}}:{{tableName}}:deleteBatch")
    @DeleteMapping(value = "/deleteBatch")
    public Result<String> deleteBatch(@RequestParam(name = "ids", required = true) String ids) {
        this.{{entityName_uncap}}Service.removeByIds(Arrays.asList(ids.split(",")));
        return Result.OK("批量删除成功!");
    }

    /**
     * 通过id查询
     * 注意：参数类型需与Entity主键类型一致（同 delete 方法）
     */
    @Operation(summary = "{{description}}-通过id查询")
    @GetMapping(value = "/queryById")
    public Result<{{entityName}}> queryById(@RequestParam(name = "id", required = true) String id) {
        {{entityName}} {{entityName_uncap}} = {{entityName_uncap}}Service.getById(id);
        if ({{entityName_uncap}} == null) {
            return Result.error("未找到对应数据");
        }
        return Result.OK({{entityName_uncap}});
    }

    /**
     * 导出excel
     */
    @RequiresPermissions("{{entityPackage}}:{{tableName}}:exportXls")
    @RequestMapping(value = "/exportXls")
    public ModelAndView exportXls(HttpServletRequest request, {{entityName}} {{entityName_uncap}}) {
        return super.exportXls(request, {{entityName_uncap}}, {{entityName}}.class, "{{description}}");
    }

    /**
     * 通过excel导入数据
     */
    @RequiresPermissions("{{entityPackage}}:{{tableName}}:importExcel")
    @RequestMapping(value = "/importExcel", method = RequestMethod.POST)
    public Result<?> importExcel(HttpServletRequest request, HttpServletResponse response) {
        return super.importExcel(request, response, {{entityName}}.class);
    }
}
```

**注意：** 如果查询字段中有下拉/单选/多选/复选框类型的，需要添加自定义查询规则：
```java
// 在 queryPageList 方法中：
Map<String, QueryRuleEnum> customeRuleMap = new HashMap<>();
customeRuleMap.put("status", QueryRuleEnum.LIKE_WITH_OR);
QueryWrapper<{{entityName}}> queryWrapper = QueryGenerator.initQueryWrapper({{entityName_uncap}}, req.getParameterMap(), customeRuleMap);
```

---

### A3. IService.java

```java
package org.jeecg.modules.{{entityPackage}}.service;

import org.jeecg.modules.{{entityPackage}}.entity.{{entityName}};
import com.baomidou.mybatisplus.extension.service.IService;

/**
 * @Description: {{description}}
 * @Author: jeecg-boot
 * @Date: {{today}}
 * @Version: V1.0
 */
public interface I{{entityName}}Service extends IService<{{entityName}}> {
}
```

---

### A4. ServiceImpl.java

```java
package org.jeecg.modules.{{entityPackage}}.service.impl;

import org.jeecg.modules.{{entityPackage}}.entity.{{entityName}};
import org.jeecg.modules.{{entityPackage}}.mapper.{{entityName}}Mapper;
import org.jeecg.modules.{{entityPackage}}.service.I{{entityName}}Service;
import org.springframework.stereotype.Service;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

/**
 * @Description: {{description}}
 * @Author: jeecg-boot
 * @Date: {{today}}
 * @Version: V1.0
 */
@Service
public class {{entityName}}ServiceImpl extends ServiceImpl<{{entityName}}Mapper, {{entityName}}> implements I{{entityName}}Service {
}
```

---

### A5. Mapper.java

```java
package org.jeecg.modules.{{entityPackage}}.mapper;

import org.jeecg.modules.{{entityPackage}}.entity.{{entityName}};
import com.baomidou.mybatisplus.core.mapper.BaseMapper;

/**
 * @Description: {{description}}
 * @Author: jeecg-boot
 * @Date: {{today}}
 * @Version: V1.0
 */
public interface {{entityName}}Mapper extends BaseMapper<{{entityName}}> {
}
```

---

### A6. Mapper.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="org.jeecg.modules.{{entityPackage}}.mapper.{{entityName}}Mapper">
</mapper>
```

---

### A7. API文件 (vue3 和 vue3Native 通用)

```typescript
import { defHttp } from '/@/utils/http/axios';
import { useMessage } from '/@/hooks/web/useMessage';

const { createConfirm } = useMessage();

enum Api {
  list = '/{{entityPackagePath}}/{{entityName_uncap}}/list',
  save = '/{{entityPackagePath}}/{{entityName_uncap}}/add',
  edit = '/{{entityPackagePath}}/{{entityName_uncap}}/edit',
  deleteOne = '/{{entityPackagePath}}/{{entityName_uncap}}/delete',
  deleteBatch = '/{{entityPackagePath}}/{{entityName_uncap}}/deleteBatch',
  importExcel = '/{{entityPackagePath}}/{{entityName_uncap}}/importExcel',
  exportXls = '/{{entityPackagePath}}/{{entityName_uncap}}/exportXls',
}

/**
 * 导出api
 */
export const getExportUrl = Api.exportXls;

/**
 * 导入api
 */
export const getImportUrl = Api.importExcel;

/**
 * 列表接口
 * @param params
 */
export const list = (params) => defHttp.get({ url: Api.list, params });

/**
 * 删除单个
 */
export const deleteOne = (params, handleSuccess) => {
  return defHttp.delete({ url: Api.deleteOne, params }, { joinParamsToUrl: true }).then(() => {
    handleSuccess();
  });
};

/**
 * 批量删除
 * @param params
 */
export const batchDelete = (params, handleSuccess) => {
  createConfirm({
    iconType: 'warning',
    title: '确认删除',
    content: '是否删除选中数据',
    okText: '确认',
    cancelText: '取消',
    onOk: () => {
      return defHttp.delete({ url: Api.deleteBatch, data: params }, { joinParamsToUrl: true }).then(() => {
        handleSuccess();
      });
    },
  });
};

/**
 * 保存或者更新
 * @param params
 * @param isUpdate
 */
export const saveOrUpdate = (params, isUpdate) => {
  let url = isUpdate ? Api.edit : Api.save;
  return defHttp.post({ url: url, params });
};
```

**vue3Native 单表风格差异：** `saveOrUpdate` 使用 `{ isTransformResponse: false }` 选项（Modal 中手动判断 `res.success`）：
```typescript
export const saveOrUpdate = (params, isUpdate) => {
  let url = isUpdate ? Api.edit : Api.save;
  return defHttp.post({ url: url, params }, { isTransformResponse: false });
};
```

**vue3Native 一对多风格差异：** `saveOrUpdate` **不用** `isTransformResponse: false`（Form 中直接 `await saveOrUpdate(values, isUpdate)` 即可）。子表查询导出为**函数**，需额外导出 `queryDataById`。详见 **C13 节**。

---

### A8. Data文件 - vue3 封装风格

```typescript
import { BasicColumn } from '/@/components/Table';
import { FormSchema } from '/@/components/Table';
import { rules } from '/@/utils/helper/validator';
import { render } from '/@/utils/common/renderUtils';

// 列表列定义
export const columns: BasicColumn[] = [
  // --- 普通字符串列 ---
  // {
  //   title: '字段名称',
  //   align: 'center',
  //   dataIndex: 'fieldName',
  // },

  // --- 日期列（截取前10位） ---
  // {
  //   title: '日期',
  //   align: 'center',
  //   dataIndex: 'dateField',
  //   customRender: ({ text }) => {
  //     text = !text ? '' : (text.length > 10 ? text.substr(0, 10) : text);
  //     return text;
  //   },
  // },

  // --- 字典翻译列（自动渲染_dictText后缀） ---
  // {
  //   title: '状态',
  //   align: 'center',
  //   dataIndex: 'status_dictText',
  // },

  // --- Switch 列 ---
  // {
  //   title: '是否启用',
  //   align: 'center',
  //   dataIndex: 'enabled',
  //   customRender: ({ text }) => {
  //     return render.renderSwitch(text, [{ text: '是', value: 'Y' }, { text: '否', value: 'N' }]);
  //   },
  // },

  // --- 图片列 ---
  // {
  //   title: '图片',
  //   align: 'center',
  //   dataIndex: 'imageField',
  //   customRender: render.renderImage,
  // },

  // --- 分类树列 ---
  // {
  //   title: '分类',
  //   align: 'center',
  //   dataIndex: 'categoryField',
  //   customRender: ({ text }) => {
  //     return render.renderCategoryTree(text, 'categoryDictCode');
  //   },
  // },
];

// 查询表单 Schema
export const searchFormSchema: FormSchema[] = [
  // --- 文本查询 ---
  // {
  //   label: '名称',
  //   field: 'name',
  //   component: 'JInput',
  //   colProps: { span: 6 },
  // },

  // --- 字典下拉查询 ---
  // {
  //   label: '状态',
  //   field: 'status',
  //   component: 'JDictSelectTag',
  //   componentProps: { dictCode: 'dict_code' },
  //   colProps: { span: 6 },
  // },

  // --- 日期范围查询 ---
  // {
  //   label: '创建日期',
  //   field: 'createTime',
  //   component: 'RangePicker',
  //   componentProps: { showTime: true },
  //   colProps: { span: 6 },
  // },
];

// 编辑表单 Schema
export const formSchema: FormSchema[] = [
  // 隐藏ID
  {
    label: '',
    field: 'id',
    component: 'Input',
    show: false,
  },

  // --- 文本输入 ---
  // {
  //   label: '名称',
  //   field: 'name',
  //   required: true,
  //   component: 'Input',
  //   componentProps: { placeholder: '请输入名称' },
  // },

  // --- 数字输入 ---
  // {
  //   label: '数量',
  //   field: 'quantity',
  //   component: 'InputNumber',
  //   componentProps: { placeholder: '请输入数量' },
  // },

  // --- 字典下拉 ---
  // {
  //   label: '状态',
  //   field: 'status',
  //   component: 'JDictSelectTag',
  //   componentProps: { dictCode: 'dict_code', placeholder: '请选择状态' },
  // },

  // --- 关联表字典下拉 ---
  // {
  //   label: '类型',
  //   field: 'type',
  //   component: 'JDictSelectTag',
  //   componentProps: { dictCode: 'tableName,textField,codeField', placeholder: '请选择类型' },
  // },

  // --- Switch ---
  // {
  //   label: '是否启用',
  //   field: 'enabled',
  //   component: 'JSwitch',
  //   componentProps: { options: ['Y', 'N'] },
  // },

  // --- 日期选择 ---
  // {
  //   label: '日期',
  //   field: 'dateField',
  //   component: 'DatePicker',
  //   componentProps: { showTime: false, valueFormat: 'YYYY-MM-DD', placeholder: '请选择日期' },
  // },

  // --- 日期时间选择 ---
  // {
  //   label: '日期时间',
  //   field: 'datetimeField',
  //   component: 'DatePicker',
  //   componentProps: { showTime: true, valueFormat: 'YYYY-MM-DD HH:mm:ss', placeholder: '请选择日期时间' },
  // },

  // --- 文本域 ---
  // {
  //   label: '备注',
  //   field: 'remark',
  //   component: 'InputTextArea',
  //   componentProps: { placeholder: '请输入备注' },
  // },

  // --- 富文本编辑器 ---
  // {
  //   label: '内容',
  //   field: 'content',
  //   component: 'JEditor',
  // },

  // --- 图片上传 ---
  // {
  //   label: '图片',
  //   field: 'imageField',
  //   component: 'JImageUpload',
  // },

  // --- 文件上传 ---
  // {
  //   label: '附件',
  //   field: 'fileField',
  //   component: 'JUpload',
  // },

  // --- 用户选择 ---
  // {
  //   label: '负责人',
  //   field: 'userId',
  //   component: 'JSelectUserByDept',
  //   componentProps: { labelKey: 'realname' },
  // },

  // --- 部门选择 ---
  // {
  //   label: '部门',
  //   field: 'deptId',
  //   component: 'JSelectDept',
  // },

  // --- 分类树选择 ---
  // {
  //   label: '分类',
  //   field: 'categoryField',
  //   component: 'JCategorySelect',
  //   componentProps: { pcode: 'categoryDictCode' },
  // },

  // --- 搜索选择 ---
  // {
  //   label: '搜索',
  //   field: 'searchField',
  //   component: 'JSearchSelect',
  //   componentProps: { dict: 'tableName,textField,codeField', placeholder: '请选择' },
  // },
];

// 高级查询配置
export const superQuerySchema = {
  // fieldName: { title: '字段名', order: 0, view: 'text' },
  // status: { title: '状态', order: 1, view: 'list', dictCode: 'dict_code' },
  // dateField: { title: '日期', order: 2, view: 'date' },
  // datetimeField: { title: '日期时间', order: 3, view: 'datetime' },
  // quantity: { title: '数量', order: 4, view: 'number' },
};
```

**高级查询 view 类型映射：**
- string → `text`
- int/double/BigDecimal → `number`
- date → `date`
- datetime → `datetime`
- 字典字段(list/radio/checkbox) → `list`, 带 `dictCode`
- 关联表字典 → `list_multi` 或 `sel_search`, 带 `dictTable/dictCode/dictText`
- switch → `radio`
- user_select → `sel_user`
- dept_select → `sel_depart`

---

### A9. List页面 - vue3 封装风格

```vue
<template>
  <div>
    <!--引用表格-->
    <BasicTable @register="registerTable" :rowSelection="rowSelection">
      <!--插槽:table标题-->
      <template #tableTitle>
        <a-button type="primary" v-auth="'{{entityPackage}}:{{tableName}}:add'" @click="handleAdd" preIcon="ant-design:plus-outlined"> 新增</a-button>
        <a-button type="primary" v-auth="'{{entityPackage}}:{{tableName}}:exportXls'" preIcon="ant-design:export-outlined" @click="onExportXls"> 导出</a-button>
        <j-upload-button type="primary" v-auth="'{{entityPackage}}:{{tableName}}:importExcel'" preIcon="ant-design:import-outlined" @click="onImportXls">导入</j-upload-button>
        <a-dropdown v-if="selectedRowKeys.length > 0">
          <template #overlay>
            <a-menu>
              <a-menu-item key="1" @click="batchHandleDelete">
                <Icon icon="ant-design:delete-outlined" />
                删除
              </a-menu-item>
            </a-menu>
          </template>
          <a-button v-auth="'{{entityPackage}}:{{tableName}}:deleteBatch'">批量操作
            <Icon icon="mdi:chevron-down" />
          </a-button>
        </a-dropdown>
        <!-- 高级查询 -->
        <super-query :config="superQueryConfig" @search="handleSuperQuery" />
      </template>
      <!--操作栏-->
      <template #action="{ record }">
        <TableAction :actions="getTableAction(record)" :dropDownActions="getDropDownAction(record)" />
      </template>
      <!--字段回显插槽-->
      <template v-slot:bodyCell="{ column, record, index, text }">
        <!-- 富文本回显 -->
        <!-- <template v-if="column.dataIndex==='content'">
          <div v-html="text"></div>
        </template> -->
        <!-- 文件下载 -->
        <!-- <template v-if="column.dataIndex==='fileField'">
          <span v-if="!text" style="font-size: 12px;font-style: italic;">无文件</span>
          <a-button v-else :ghost="true" type="primary" preIcon="ant-design:download-outlined" size="small" @click="downloadFile(text)">下载</a-button>
        </template> -->
      </template>
    </BasicTable>
    <!-- 表单区域 -->
    <{{entityName}}Modal @register="registerModal" @success="handleSuccess" />
  </div>
</template>

<script lang="ts" name="{{entityPackage}}-{{entityName_uncap}}" setup>
  import { ref, reactive } from 'vue';
  import { BasicTable, useTable, TableAction } from '/@/components/Table';
  import { useModal } from '/@/components/Modal';
  import { useListPage } from '/@/hooks/system/useListPage';
  import {{entityName}}Modal from './components/{{entityName}}Modal.vue';
  import { columns, searchFormSchema, superQuerySchema } from './{{entityName}}.data';
  import { list, deleteOne, batchDelete, getImportUrl, getExportUrl } from './{{entityName}}.api';
  import { downloadFile } from '/@/utils/common/renderUtils';

  const queryParam = reactive<any>({});
  const checkedKeys = ref<Array<string | number>>([]);
  // 注册 modal
  const [registerModal, { openModal }] = useModal();
  // 注册 table
  const { prefixCls, tableContext, onExportXls, onImportXls } = useListPage({
    tableProps: {
      title: '{{description}}',
      api: list,
      columns,
      canResize: true,
      formConfig: {
        schemas: searchFormSchema,
        autoSubmitOnEnter: true,
        showAdvancedButton: true,
        fieldMapToNumber: [
          // 数字/时间范围查询映射
          // ['fieldName', ['fieldName_begin', 'fieldName_end']],
        ],
        fieldMapToTime: [
          // 日期范围查询映射
          // ['dateField', ['dateField_begin', 'dateField_end'], 'YYYY-MM-DD'],
          // ['datetimeField', ['datetimeField_begin', 'datetimeField_end'], 'YYYY-MM-DD HH:mm:ss'],
        ],
      },
      actionColumn: {
        width: 120,
        fixed: 'right',
      },
      beforeFetch: (params) => {
        return Object.assign(params, queryParam);
      },
    },
    exportConfig: {
      name: '{{description}}',
      url: getExportUrl,
      params: queryParam,
    },
    importConfig: {
      url: getImportUrl,
      success: handleSuccess,
    },
  });

  const [registerTable, { reload }, { rowSelection, selectedRowKeys }] = tableContext;

  // 高级查询配置
  const superQueryConfig = reactive(superQuerySchema);

  /**
   * 高级查询事件
   */
  function handleSuperQuery(params) {
    Object.keys(params).map((k) => {
      queryParam[k] = params[k];
    });
    reload();
  }

  /**
   * 新增事件
   */
  function handleAdd() {
    openModal(true, {
      isUpdate: false,
      showFooter: true,
    });
  }

  /**
   * 编辑事件
   */
  function handleEdit(record: Recordable) {
    openModal(true, {
      record,
      isUpdate: true,
      showFooter: true,
    });
  }

  /**
   * 详情
   */
  function handleDetail(record: Recordable) {
    openModal(true, {
      record,
      isUpdate: true,
      showFooter: false,
    });
  }

  /**
   * 删除事件
   */
  async function handleDelete(record) {
    await deleteOne({ id: record.id }, handleSuccess);
  }

  /**
   * 批量删除事件
   */
  async function batchHandleDelete() {
    await batchDelete({ ids: selectedRowKeys.value }, handleSuccess);
  }

  /**
   * 成功回调
   */
  function handleSuccess() {
    (selectedRowKeys.value = []) && reload();
  }

  /**
   * 操作栏
   */
  function getTableAction(record) {
    return [
      {
        label: '编辑',
        onClick: handleEdit.bind(null, record),
        auth: '{{entityPackage}}:{{tableName}}:edit',
      },
    ];
  }

  /**
   * 下拉操作栏
   */
  function getDropDownAction(record) {
    return [
      {
        label: '详情',
        onClick: handleDetail.bind(null, record),
      },
      {
        label: '删除',
        popConfirm: {
          title: '是否确认删除',
          confirm: handleDelete.bind(null, record),
          placement: 'topLeft',
        },
        auth: '{{entityPackage}}:{{tableName}}:delete',
      },
    ];
  }
</script>

<style lang="less" scoped>
  :deep(.ant-picker-range) {
    width: 100%;
  }
</style>
```

---

### A10. Modal组件 - vue3 封装风格

```vue
<template>
  <BasicModal v-bind="$attrs" @register="registerModal" destroyOnClose :title="title" :width="800" @ok="handleSubmit">
    <BasicForm @register="registerForm" name="{{entityName}}Form" />
  </BasicModal>
</template>

<script lang="ts" setup>
  import { ref, computed, unref } from 'vue';
  import { BasicModal, useModalInner } from '/@/components/Modal';
  import { BasicForm, useForm } from '/@/components/Form/index';
  import { formSchema } from '../{{entityName}}.data';
  import { saveOrUpdate } from '../{{entityName}}.api';

  // Emits声明
  const emit = defineEmits(['register', 'success']);
  const isUpdate = ref(true);
  const isDetail = ref(false);

  // 表单配置
  const [registerForm, { setProps, resetFields, setFieldsValue, validate, scrollToField }] = useForm({
    // 单列布局用 labelWidth: 150
    labelWidth: 150,
    schemas: formSchema,
    showActionButtonGroup: false,
    // 多列布局用 baseColProps: { span: 12 } (双列) 或 { span: 8 } (三列)
    baseColProps: { span: 24 },
  });

  // 表单赋值
  const [registerModal, { setModalProps, closeModal }] = useModalInner(async (data) => {
    // 重置表单
    await resetFields();
    setModalProps({ confirmLoading: false, showCancelBtn: !!data?.showFooter, showOkBtn: !!data?.showFooter });
    isUpdate.value = !!data?.isUpdate;
    isDetail.value = !!data?.showFooter;
    if (unref(isUpdate)) {
      // 表单赋值
      await setFieldsValue({
        ...data.record,
      });
    }
    // 隐藏底部时禁用整个表单
    setProps({ disabled: !data?.showFooter });
  });

  // 设置标题
  const title = computed(() => (!unref(isUpdate) ? '新增' : !unref(isDetail) ? '详情' : '编辑'));

  // 表单提交事件
  async function handleSubmit(v) {
    try {
      let values = await validate();
      setModalProps({ confirmLoading: true });
      // 提交表单
      await saveOrUpdate(values, isUpdate.value);
      // 关闭弹窗
      closeModal();
      // 刷新列表
      emit('success');
    } catch ({ errorFields }) {
      if (errorFields) {
        const firstField = errorFields[0];
        if (firstField) {
          scrollToField(firstField.name, { behavior: 'smooth', block: 'center' });
        }
      }
      return Promise.reject(errorFields);
    } finally {
      setModalProps({ confirmLoading: false });
    }
  }
</script>

<style lang="less" scoped>
  :deep(.ant-input-number) {
    width: 100%;
  }
  :deep(.ant-calendar-picker) {
    width: 100%;
  }
</style>
```

**宽度规则：**
- 单列表单(fieldRowNum=1): width=800, baseColProps={span:24}
- 双列表单(fieldRowNum=2): width=1000, baseColProps={span:12}
- 三列表单(fieldRowNum=3): width=1200, baseColProps={span:8}
- 四列表单(fieldRowNum=4): width=1280, baseColProps={span:6}

---

### A8N. Data文件 - vue3Native 原生风格

vue3Native 的 data.ts 只包含 columns 和 superQuerySchema，不包含 formSchema（表单在模板中直接写控件）。

```typescript
import { BasicColumn } from '/@/components/Table';
import { FormSchema } from '/@/components/Table';
import { rules } from '/@/utils/helper/validator';
import { render } from '/@/utils/common/renderUtils';

// 列表列定义（与 vue3 封装风格完全相同）
export const columns: BasicColumn[] = [
  // ... 同 A8 的 columns
];

// 高级查询配置（与 vue3 封装风格完全相同）
export const superQuerySchema = {
  // ... 同 A8 的 superQuerySchema
};
```

---

### A9N. List页面 - vue3Native 原生风格

```vue
<template>
  <div>
    <!--引用表格-->
    <BasicTable @register="registerTable" :rowSelection="rowSelection">
      <!--插槽:table标题-->
      <template #tableTitle>
        <a-button type="primary" v-auth="'{{entityPackage}}:{{tableName}}:add'" @click="handleAdd" preIcon="ant-design:plus-outlined"> 新增</a-button>
        <a-button type="primary" v-auth="'{{entityPackage}}:{{tableName}}:exportXls'" preIcon="ant-design:export-outlined" @click="onExportXls"> 导出</a-button>
        <j-upload-button type="primary" v-auth="'{{entityPackage}}:{{tableName}}:importExcel'" preIcon="ant-design:import-outlined" @click="onImportXls">导入</j-upload-button>
        <a-dropdown v-if="selectedRowKeys.length > 0">
          <template #overlay>
            <a-menu>
              <a-menu-item key="1" @click="batchHandleDelete">
                <Icon icon="ant-design:delete-outlined" />
                删除
              </a-menu-item>
            </a-menu>
          </template>
          <a-button v-auth="'{{entityPackage}}:{{tableName}}:deleteBatch'">批量操作
            <Icon icon="mdi:chevron-down" />
          </a-button>
        </a-dropdown>
        <!-- 高级查询 -->
        <super-query :config="superQueryConfig" @search="handleSuperQuery" />
      </template>
      <!--操作栏-->
      <template #action="{ record }">
        <TableAction :actions="getTableAction(record)" :dropDownActions="getDropDownAction(record)" />
      </template>
      <!--字段回显插槽（同 vue3 封装风格）-->
      <template v-slot:bodyCell="{ column, record, index, text }">
      </template>
    </BasicTable>
    <!-- 表单区域 -->
    <{{entityName}}Modal ref="registerModal" @success="handleSuccess" />
  </div>
</template>

<script lang="ts" name="{{entityPackage}}-{{entityName_uncap}}" setup>
  import { ref, reactive } from 'vue';
  import { BasicTable, useTable, TableAction } from '/@/components/Table';
  import { useListPage } from '/@/hooks/system/useListPage';
  import {{entityName}}Modal from './components/{{entityName}}Modal.vue';
  import { columns, superQuerySchema } from './{{entityName}}.data';
  import { list, deleteOne, batchDelete, getImportUrl, getExportUrl } from './{{entityName}}.api';
  import { downloadFile } from '/@/utils/common/renderUtils';

  const queryParam = reactive<any>({});
  const registerModal = ref();

  const { prefixCls, tableContext, onExportXls, onImportXls } = useListPage({
    tableProps: {
      title: '{{description}}',
      api: list,
      columns,
      canResize: true,
      useSearchForm: false,
      actionColumn: {
        width: 120,
        fixed: 'right',
      },
      beforeFetch: (params) => {
        return Object.assign(params, queryParam);
      },
    },
    exportConfig: {
      name: '{{description}}',
      url: getExportUrl,
      params: queryParam,
    },
    importConfig: {
      url: getImportUrl,
      success: handleSuccess,
    },
  });

  const [registerTable, { reload }, { rowSelection, selectedRowKeys }] = tableContext;

  // 高级查询配置
  const superQueryConfig = reactive(superQuerySchema);

  function handleSuperQuery(params) {
    Object.keys(params).map((k) => {
      queryParam[k] = params[k];
    });
    reload();
  }

  function handleAdd() {
    registerModal.value.disableSubmit = false;
    registerModal.value.add();
  }

  function handleEdit(record: Recordable) {
    registerModal.value.disableSubmit = false;
    registerModal.value.edit(record);
  }

  function handleDetail(record: Recordable) {
    registerModal.value.disableSubmit = true;
    registerModal.value.edit(record);
  }

  async function handleDelete(record) {
    await deleteOne({ id: record.id }, handleSuccess);
  }

  async function batchHandleDelete() {
    await batchDelete({ ids: selectedRowKeys.value }, handleSuccess);
  }

  function handleSuccess() {
    (selectedRowKeys.value = []) && reload();
  }

  function getTableAction(record) {
    return [
      {
        label: '编辑',
        onClick: handleEdit.bind(null, record),
        auth: '{{entityPackage}}:{{tableName}}:edit',
      },
    ];
  }

  function getDropDownAction(record) {
    return [
      {
        label: '详情',
        onClick: handleDetail.bind(null, record),
      },
      {
        label: '删除',
        popConfirm: {
          title: '是否确认删除',
          confirm: handleDelete.bind(null, record),
          placement: 'topLeft',
        },
        auth: '{{entityPackage}}:{{tableName}}:delete',
      },
    ];
  }
</script>

<style lang="less" scoped>
  :deep(.ant-picker-range) {
    width: 100%;
  }
</style>
```

---

### A10N. Modal组件 - vue3Native 原生风格

```vue
<template>
  <j-modal :title="title" :width="800" :visible="visible" @ok="handleOk" :okButtonProps="{ class: { 'jee-hidden': disableSubmit } }" @cancel="handleCancel" cancelText="关闭">
    <{{entityName}}Form ref="registerForm" @ok="submitCallback" :formDisabled="disableSubmit" :formBpm="false" />
    <template #footer>
      <a-button @click="handleCancel">取消</a-button>
      <a-button :class="{ 'jee-hidden': disableSubmit }" type="primary" @click="handleOk">确认</a-button>
    </template>
  </j-modal>
</template>

<script lang="ts" setup>
  import { ref, nextTick, defineExpose } from 'vue';
  import {{entityName}}Form from './{{entityName}}Form.vue';
  import JModal from '/@/components/Modal/src/JModal/JModal.vue';

  const title = ref<string>('');
  const visible = ref<boolean>(false);
  const disableSubmit = ref<boolean>(false);
  const registerForm = ref();
  const emit = defineEmits(['register', 'success']);

  /**
   * 新增
   */
  function add() {
    title.value = '新增';
    visible.value = true;
    nextTick(() => {
      registerForm.value.add();
    });
  }

  /**
   * 编辑
   */
  function edit(record) {
    title.value = disableSubmit.value ? '详情' : '编辑';
    visible.value = true;
    nextTick(() => {
      registerForm.value.edit(record);
    });
  }

  /**
   * 确定按钮点击事件
   */
  function handleOk() {
    registerForm.value.submitForm();
  }

  /**
   * form保存回调事件
   */
  function submitCallback() {
    handleCancel();
    emit('success');
  }

  /**
   * 取消按钮回调事件
   */
  function handleCancel() {
    visible.value = false;
  }

  defineExpose({
    add,
    edit,
    disableSubmit,
  });
</script>

<style lang="less">
  .jee-hidden {
    display: none !important;
  }
</style>
```

---

### A11N. Form组件 - vue3Native 原生风格

```vue
<template>
  <a-spin :spinning="confirmLoading">
    <JFormContainer :disabled="disabled">
      <template #detail>
        <a-form ref="formRef" class="antd-modal-form" :labelCol="labelCol" :wrapperCol="wrapperCol" name="{{entityName}}Form">
          <a-row>
            <!-- 每个字段生成一个 a-col + a-form-item -->

            <!-- === 文本输入 === -->
            <!-- <a-col :span="24">
              <a-form-item label="名称" v-bind="validateInfos.name" id="{{entityName}}Form-name" name="name">
                <a-input v-model:value="formData.name" placeholder="请输入名称" allow-clear />
              </a-form-item>
            </a-col> -->

            <!-- === 数字输入 === -->
            <!-- <a-col :span="24">
              <a-form-item label="数量" v-bind="validateInfos.quantity" id="{{entityName}}Form-quantity" name="quantity">
                <a-input-number v-model:value="formData.quantity" placeholder="请输入数量" style="width: 100%" />
              </a-form-item>
            </a-col> -->

            <!-- === 字典下拉 === -->
            <!-- <a-col :span="24">
              <a-form-item label="状态" v-bind="validateInfos.status" id="{{entityName}}Form-status" name="status">
                <JDictSelectTag v-model:value="formData.status" dictCode="dict_code" placeholder="请选择状态" />
              </a-form-item>
            </a-col> -->

            <!-- === Switch === -->
            <!-- <a-col :span="24">
              <a-form-item label="是否启用" v-bind="validateInfos.enabled" id="{{entityName}}Form-enabled" name="enabled">
                <a-switch v-model:checked="formData.enabled" checkedValue="Y" unCheckedValue="N" />
              </a-form-item>
            </a-col> -->

            <!-- === 日期选择 === -->
            <!-- <a-col :span="24">
              <a-form-item label="日期" v-bind="validateInfos.dateField" id="{{entityName}}Form-dateField" name="dateField">
                <a-date-picker v-model:value="formData.dateField" placeholder="请选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
              </a-form-item>
            </a-col> -->

            <!-- === 日期时间选择 === -->
            <!-- <a-col :span="24">
              <a-form-item label="日期时间" v-bind="validateInfos.datetimeField" id="{{entityName}}Form-datetimeField" name="datetimeField">
                <a-date-picker v-model:value="formData.datetimeField" placeholder="请选择日期时间" :showTime="true" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
              </a-form-item>
            </a-col> -->

            <!-- === 文本域 === -->
            <!-- <a-col :span="24">
              <a-form-item label="备注" v-bind="validateInfos.remark" id="{{entityName}}Form-remark" name="remark">
                <a-textarea v-model:value="formData.remark" placeholder="请输入备注" :rows="4" />
              </a-form-item>
            </a-col> -->

            <!-- === 图片上传 === -->
            <!-- <a-col :span="24">
              <a-form-item label="图片" v-bind="validateInfos.imageField" id="{{entityName}}Form-imageField" name="imageField">
                <JImageUpload v-model:value="formData.imageField" />
              </a-form-item>
            </a-col> -->

            <!-- === 文件上传 === -->
            <!-- <a-col :span="24">
              <a-form-item label="附件" v-bind="validateInfos.fileField" id="{{entityName}}Form-fileField" name="fileField">
                <JUpload v-model:value="formData.fileField" />
              </a-form-item>
            </a-col> -->

            <!-- === 富文本 === -->
            <!-- <a-col :span="24">
              <a-form-item label="内容" v-bind="validateInfos.content" id="{{entityName}}Form-content" name="content">
                <JEditor v-model:value="formData.content" />
              </a-form-item>
            </a-col> -->

            <!-- === 用户选择 === -->
            <!-- <a-col :span="24">
              <a-form-item label="负责人" v-bind="validateInfos.userId" id="{{entityName}}Form-userId" name="userId">
                <JSelectUserByDept v-model:value="formData.userId" />
              </a-form-item>
            </a-col> -->

            <!-- === 部门选择 === -->
            <!-- <a-col :span="24">
              <a-form-item label="部门" v-bind="validateInfos.deptId" id="{{entityName}}Form-deptId" name="deptId">
                <JSelectDept v-model:value="formData.deptId" />
              </a-form-item>
            </a-col> -->

            <!-- === 搜索选择 === -->
            <!-- <a-col :span="24">
              <a-form-item label="搜索" v-bind="validateInfos.searchField" id="{{entityName}}Form-searchField" name="searchField">
                <JSearchSelect v-model:value="formData.searchField" dict="tableName,textField,codeField" placeholder="请选择" />
              </a-form-item>
            </a-col> -->
          </a-row>
        </a-form>
      </template>
    </JFormContainer>
  </a-spin>
</template>

<script lang="ts" setup>
  import { ref, reactive, defineExpose, nextTick, defineProps, computed } from 'vue';
  import { useMessage } from '/@/hooks/web/useMessage';
  import { getValueType } from '/@/utils';
  import { saveOrUpdate } from '../{{entityName}}.api';
  import { Form } from 'ant-design-vue';
  import JFormContainer from '/@/components/Form/src/container/JFormContainer.vue';
  // 按需导入组件（根据实际用到的字段类型）
  // import JDictSelectTag from '/@/components/Form/src/jeecg/components/JDictSelectTag.vue';
  // import JSearchSelect from '/@/components/Form/src/jeecg/components/JSearchSelect.vue';
  // import JImageUpload from '/@/components/Form/src/jeecg/components/JImageUpload.vue';
  // import JUpload from '/@/components/Form/src/jeecg/components/JUpload.vue';
  // import JEditor from '/@/components/Form/src/jeecg/components/JEditor.vue';
  // import JSelectUserByDept from '/@/components/Form/src/jeecg/components/JSelectUserByDept.vue';
  // import JSelectDept from '/@/components/Form/src/jeecg/components/JSelectDept.vue';

  const props = defineProps({
    formDisabled: { type: Boolean, default: false },
    formData: { type: Object, default: () => ({}) },
    formBpm: { type: Boolean, default: true },
  });
  const formRef = ref();
  const useForm = Form.useForm;
  const emit = defineEmits(['register', 'ok']);
  const formData = reactive<Record<string, any>>({
    id: '',
    // 业务字段初始值
    // name: '',
    // status: '',
    // ... 所有字段默认值
  });
  const { createMessage } = useMessage();
  const labelCol = ref<any>({ xs: { span: 24 }, sm: { span: 5 } });
  const wrapperCol = ref<any>({ xs: { span: 24 }, sm: { span: 16 } });
  const confirmLoading = ref<boolean>(false);

  // 表单验证规则
  const validatorRules = reactive({
    // name: [{ required: true, message: '请输入名称!' }],
    // ... 必填字段的验证规则
  });
  const { resetFields, validate, validateInfos } = useForm(formData, validatorRules, { immediate: false });

  // 表单禁用
  const disabled = computed(() => {
    if (props.formBpm === true) {
      if (props.formData.disabled === false) {
        return false;
      } else {
        return true;
      }
    }
    return props.formDisabled;
  });

  /**
   * 新增
   */
  function add() {
    edit({});
  }

  /**
   * 编辑
   */
  function edit(record) {
    nextTick(() => {
      resetFields();
      const tmpData = {};
      Object.keys(formData).forEach((key) => {
        if (record.hasOwnProperty(key)) {
          tmpData[key] = record[key];
        }
      });
      // 赋值
      Object.assign(formData, tmpData);
    });
  }

  /**
   * 提交数据
   */
  async function submitForm() {
    try {
      await validate();
    } catch ({ errorFields }) {
      if (errorFields) {
        const firstField = errorFields[0];
        if (firstField) {
          formRef.value.scrollToField(firstField.name, { behavior: 'smooth', block: 'center' });
        }
      }
      return Promise.reject(errorFields);
    }
    confirmLoading.value = true;
    const isUpdate = ref<boolean>(false);
    let model = formData;
    if (model.id) {
      isUpdate.value = true;
    }
    // 处理数组类型字段（多选等）
    for (let data in model) {
      if (model[data] instanceof Array) {
        let valueType = getValueType(formRef.value.getProps, data);
        if (valueType === 'string') {
          model[data] = model[data].join(',');
        }
      }
    }
    await saveOrUpdate(model, isUpdate.value)
      .then((res) => {
        if (res.success) {
          createMessage.success(res.message);
          emit('ok');
        } else {
          createMessage.warning(res.message);
        }
      })
      .finally(() => {
        confirmLoading.value = false;
      });
  }

  defineExpose({
    add,
    edit,
    submitForm,
  });
</script>

<style lang="less" scoped>
  .antd-modal-form {
    padding: 14px;
  }
</style>
```

**vue3Native 多列布局：**
- 单列: `<a-col :span="24">`
- 双列: `<a-col :span="12">`
- 三列: `<a-col :span="8">`

---

### A12. 菜单权限 SQL

```sql
-- 注意：该页面对应的前台目录为 views/{{viewDir}} 文件夹下
-- 如果你想更改到其他目录，请修改sql中component字段对应的值

-- 主菜单
INSERT INTO sys_permission(id, parent_id, name, url, component, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_route, is_leaf, keep_alive, hidden, hide_tab, description, status, del_flag, rule_flag, create_by, create_time, update_by, update_time, internal_or_external)
VALUES ('{{timestamp}}01', NULL, '{{description}}', '/{{entityPackagePath}}/{{entityName_uncap}}List', '{{viewDir}}/{{entityName}}List', NULL, NULL, 0, NULL, '1', 0.00, 0, NULL, 1, 0, 0, 0, 0, NULL, '1', 0, 0, 'admin', '{{today}} 00:00:00', NULL, NULL, 0);

-- 新增
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('{{timestamp}}02', '{{timestamp}}01', '添加{{description}}', NULL, NULL, 0, NULL, NULL, 2, '{{entityPackage}}:{{tableName}}:add', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '{{today}} 00:00:00', NULL, NULL, 0, 0, '1', 0);

-- 编辑
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('{{timestamp}}03', '{{timestamp}}01', '编辑{{description}}', NULL, NULL, 0, NULL, NULL, 2, '{{entityPackage}}:{{tableName}}:edit', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '{{today}} 00:00:00', NULL, NULL, 0, 0, '1', 0);

-- 删除
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('{{timestamp}}04', '{{timestamp}}01', '删除{{description}}', NULL, NULL, 0, NULL, NULL, 2, '{{entityPackage}}:{{tableName}}:delete', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '{{today}} 00:00:00', NULL, NULL, 0, 0, '1', 0);

-- 批量删除
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('{{timestamp}}05', '{{timestamp}}01', '批量删除{{description}}', NULL, NULL, 0, NULL, NULL, 2, '{{entityPackage}}:{{tableName}}:deleteBatch', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '{{today}} 00:00:00', NULL, NULL, 0, 0, '1', 0);

-- 导出excel
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('{{timestamp}}06', '{{timestamp}}01', '导出excel_{{description}}', NULL, NULL, 0, NULL, NULL, 2, '{{entityPackage}}:{{tableName}}:exportXls', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '{{today}} 00:00:00', NULL, NULL, 0, 0, '1', 0);

-- 导入excel
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('{{timestamp}}07', '{{timestamp}}01', '导入excel_{{description}}', NULL, NULL, 0, NULL, NULL, 2, '{{entityPackage}}:{{tableName}}:importExcel', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '{{today}} 00:00:00', NULL, NULL, 0, 0, '1', 0);

-- 角色授权（admin角色）
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('{{timestamp}}08', 'f6817f48af4fb3af11b9e8bf182f618b', '{{timestamp}}01', NULL, '{{today}} 00:00:00', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('{{timestamp}}09', 'f6817f48af4fb3af11b9e8bf182f618b', '{{timestamp}}02', NULL, '{{today}} 00:00:00', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('{{timestamp}}10', 'f6817f48af4fb3af11b9e8bf182f618b', '{{timestamp}}03', NULL, '{{today}} 00:00:00', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('{{timestamp}}11', 'f6817f48af4fb3af11b9e8bf182f618b', '{{timestamp}}04', NULL, '{{today}} 00:00:00', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('{{timestamp}}12', 'f6817f48af4fb3af11b9e8bf182f618b', '{{timestamp}}05', NULL, '{{today}} 00:00:00', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('{{timestamp}}13', 'f6817f48af4fb3af11b9e8bf182f618b', '{{timestamp}}06', NULL, '{{today}} 00:00:00', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('{{timestamp}}14', 'f6817f48af4fb3af11b9e8bf182f618b', '{{timestamp}}07', NULL, '{{today}} 00:00:00', '127.0.0.1');
```

---

## B. 树表模式差异

树表在单表基础上有以下差异，相比单表多了树结构管理（父子节点关系、懒加载、展开状态维护）。

### B1. Entity 额外字段

在 Entity 类中追加以下树结构字段（放在系统字段之前）：

```java
    // ==================== 树结构字段 ====================

    /**父ID*/
    @Schema(description = "父ID")
    private String pid;

    /**是否有子节点*/
    @Excel(name = "是否有子节点", width = 15, dicCode = "yn")
    @Dict(dicCode = "yn")
    @Schema(description = "是否有子节点")
    private String hasChild;
```

### B2. Mapper 额外方法

Mapper 接口中增加树节点状态更新和子节点查询方法：

```java
public interface {{entityName}}Mapper extends BaseMapper<{{entityName}}> {

    /**
     * 编辑节点状态
     */
    void updateTreeNodeStatus(@Param("pid") String pid, @Param("hasChild") String hasChild);

    /**
     * 根据pid查询子节点（返回SelectTreeModel用于树选择组件）
     */
    List<SelectTreeModel> queryListByPid(@Param("parentId") String parentId, @Param("installCondition") String installCondition);
}
```

对应 Mapper XML（注意 `{{displayField}}` 为树节点显示字段，如 name）：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="org.jeecg.modules.{{entityPackage}}.mapper.{{entityName}}Mapper">

    <update id="updateTreeNodeStatus">
        update {{tableName}} set has_child = #{hasChild} where id = #{pid}
    </update>

    <select id="queryListByPid" parameterType="string" resultType="org.jeecg.common.system.vo.SelectTreeModel">
        select id as "key", {{displayField}} as "title", pid as "parentId",
               (case when has_child = '1' then 0 else 1 end) as "isLeaf"
        from {{tableName}} where pid = #{parentId}
    </select>

</mapper>
```

### B3. Service 接口额外方法

```java
import org.jeecg.common.system.vo.SelectTreeModel;

public interface I{{entityName}}Service extends IService<{{entityName}}> {

    /**根节点父ID的值*/
    public static final String ROOT_PID_VALUE = "0";
    /**树节点有子节点状态值*/
    public static final String HASCHILD = "1";
    /**树节点无子节点状态值*/
    public static final String NOCHILD = "0";

    /**新增节点*/
    void add{{entityName}}({{entityName}} entity);
    /**修改节点*/
    void update{{entityName}}({{entityName}} entity);
    /**删除节点（含递归删除子节点）*/
    void delete{{entityName}}(String id) throws JeecgBootException;
    /**查询所有数据，无分页（搜索时递归找到根节点）*/
    List<{{entityName}}> queryTreeListNoPage(QueryWrapper<{{entityName}}> queryWrapper);
    /**根据父级编码加载分类字典的数据*/
    List<SelectTreeModel> queryListByCode(String parentCode);
    /**根据pid查询子节点集合*/
    List<SelectTreeModel> queryListByPid(String pid);
}
```

### B4. ServiceImpl 核心逻辑

```java
@Service
public class {{entityName}}ServiceImpl extends ServiceImpl<{{entityName}}Mapper, {{entityName}}> implements I{{entityName}}Service {

    @Override
    public void add{{entityName}}({{entityName}} entity) {
        // 新增时设置hasChild为0
        entity.setHasChild(I{{entityName}}Service.NOCHILD);
        if (oConvertUtils.isEmpty(entity.getPid())) {
            entity.setPid(I{{entityName}}Service.ROOT_PID_VALUE);
        } else {
            // 如果当前节点父ID不为空 则设置父节点的hasChild为1
            {{entityName}} parent = baseMapper.selectById(entity.getPid());
            if (parent != null && !"1".equals(parent.getHasChild())) {
                parent.setHasChild("1");
                baseMapper.updateById(parent);
            }
        }
        baseMapper.insert(entity);
    }

    @Override
    public void update{{entityName}}({{entityName}} entity) {
        {{entityName}} old = this.getById(entity.getId());
        if (old == null) {
            throw new JeecgBootException("未找到对应实体");
        }
        String old_pid = old.getPid();
        String new_pid = entity.getPid();
        if (!old_pid.equals(new_pid)) {
            // 父节点变更：更新旧父节点状态
            updateOldParentNode(old_pid);
            if (oConvertUtils.isEmpty(new_pid)) {
                entity.setPid(I{{entityName}}Service.ROOT_PID_VALUE);
            }
            // 更新新父节点为有子节点
            if (!I{{entityName}}Service.ROOT_PID_VALUE.equals(entity.getPid())) {
                baseMapper.updateTreeNodeStatus(entity.getPid(), I{{entityName}}Service.HASCHILD);
            }
        }
        baseMapper.updateById(entity);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void delete{{entityName}}(String id) throws JeecgBootException {
        // 查询选中节点下所有子节点一并删除
        id = this.queryTreeChildIds(id);
        if (id.indexOf(",") > 0) {
            StringBuffer sb = new StringBuffer();
            String[] idArr = id.split(",");
            for (String idVal : idArr) {
                if (idVal != null) {
                    {{entityName}} item = this.getById(idVal);
                    String pidVal = item.getPid();
                    // 查询此节点上一级是否还有其他子节点
                    List<{{entityName}}> dataList = baseMapper.selectList(new QueryWrapper<{{entityName}}>().eq("pid", pidVal).notIn("id", Arrays.asList(idArr)));
                    boolean flag = (dataList == null || dataList.size() == 0) && !Arrays.asList(idArr).contains(pidVal) && !sb.toString().contains(pidVal);
                    if (flag) {
                        sb.append(pidVal).append(",");
                    }
                }
            }
            // 批量删除节点
            baseMapper.deleteBatchIds(Arrays.asList(idArr));
            // 修改已无子节点的标识
            String[] pidArr = sb.toString().split(",");
            for (String pid : pidArr) {
                this.updateOldParentNode(pid);
            }
        } else {
            {{entityName}} item = this.getById(id);
            if (item == null) {
                throw new JeecgBootException("未找到对应实体");
            }
            updateOldParentNode(item.getPid());
            baseMapper.deleteById(id);
        }
    }

    @Override
    public List<{{entityName}}> queryTreeListNoPage(QueryWrapper<{{entityName}}> queryWrapper) {
        List<{{entityName}}> dataList = baseMapper.selectList(queryWrapper);
        List<{{entityName}}> mapList = new ArrayList<>();
        for ({{entityName}} data : dataList) {
            String pidVal = data.getPid();
            // 递归查询子节点的根节点
            if (pidVal != null && !I{{entityName}}Service.ROOT_PID_VALUE.equals(pidVal)) {
                {{entityName}} rootVal = this.getTreeRoot(pidVal);
                if (rootVal != null && !mapList.contains(rootVal)) {
                    mapList.add(rootVal);
                }
            } else {
                if (!mapList.contains(data)) {
                    mapList.add(data);
                }
            }
        }
        return mapList;
    }

    @Override
    public List<SelectTreeModel> queryListByCode(String parentCode) {
        String pid = ROOT_PID_VALUE;
        if (oConvertUtils.isNotEmpty(parentCode)) {
            LambdaQueryWrapper<{{entityName}}> queryWrapper = new LambdaQueryWrapper<>();
            queryWrapper.eq({{entityName}}::getPid, parentCode);
            List<{{entityName}}> list = baseMapper.selectList(queryWrapper);
            if (list == null || list.size() == 0) {
                throw new JeecgBootException("该编码【" + parentCode + "】不存在，请核实!");
            }
            if (list.size() > 1) {
                throw new JeecgBootException("该编码【" + parentCode + "】存在多个，请核实!");
            }
            pid = list.get(0).getId();
        }
        return baseMapper.queryListByPid(pid, null);
    }

    @Override
    public List<SelectTreeModel> queryListByPid(String pid) {
        if (oConvertUtils.isEmpty(pid)) {
            pid = ROOT_PID_VALUE;
        }
        return baseMapper.queryListByPid(pid, null);
    }

    /**
     * 根据所传pid查询旧的父级节点的子节点并修改相应状态值
     */
    private void updateOldParentNode(String pid) {
        if (!I{{entityName}}Service.ROOT_PID_VALUE.equals(pid)) {
            Long count = baseMapper.selectCount(new QueryWrapper<{{entityName}}>().eq("pid", pid));
            if (count == null || count <= 1) {
                baseMapper.updateTreeNodeStatus(pid, I{{entityName}}Service.NOCHILD);
            }
        }
    }

    /**
     * 递归查询节点的根节点
     */
    private {{entityName}} getTreeRoot(String pidVal) {
        {{entityName}} data = baseMapper.selectById(pidVal);
        if (data != null && !I{{entityName}}Service.ROOT_PID_VALUE.equals(data.getPid()) && !data.getPid().equals(data.getId())) {
            return this.getTreeRoot(data.getPid());
        } else {
            return data;
        }
    }

    /**
     * 根据id查询所有子节点id
     */
    private String queryTreeChildIds(String ids) {
        String[] idArr = ids.split(",");
        StringBuffer sb = new StringBuffer();
        for (String pidVal : idArr) {
            if (pidVal != null) {
                if (!sb.toString().contains(pidVal)) {
                    if (sb.toString().length() > 0) {
                        sb.append(",");
                    }
                    sb.append(pidVal);
                    this.getTreeChildIds(pidVal, sb);
                }
            }
        }
        return sb.toString();
    }

    /**
     * 递归查询所有子节点
     */
    private StringBuffer getTreeChildIds(String pidVal, StringBuffer sb) {
        List<{{entityName}}> dataList = baseMapper.selectList(new QueryWrapper<{{entityName}}>().eq("pid", pidVal));
        if (dataList != null && dataList.size() > 0) {
            for ({{entityName}} tree : dataList) {
                if (!sb.toString().contains(tree.getId())) {
                    sb.append(",").append(tree.getId());
                }
                this.getTreeChildIds(tree.getId(), sb);
            }
        }
        return sb;
    }
}
```

### B5. Controller 额外端点

树表 Controller 不使用单表的 `list` 端点，替换为以下端点：

```java
    /**
     * 分页列表查询（树根节点）
     * - 有搜索条件时(hasQuery=true)：调用 queryTreeListNoPage 搜索并递归找到根节点
     * - 无搜索条件时：只查 pid=0 的根节点
     */
    @Operation(summary = "{{description}}-分页列表查询")
    @GetMapping(value = "/rootList")
    public Result<IPage<{{entityName}}>> queryPageList({{entityName}} entity,
                                                        @RequestParam(name = "pageNo", defaultValue = "1") Integer pageNo,
                                                        @RequestParam(name = "pageSize", defaultValue = "10") Integer pageSize,
                                                        HttpServletRequest req) {
        String hasQuery = req.getParameter("hasQuery");
        if (hasQuery != null && "true".equals(hasQuery)) {
            QueryWrapper<{{entityName}}> queryWrapper = QueryGenerator.initQueryWrapper(entity, req.getParameterMap());
            List<{{entityName}}> list = {{entityName_uncap}}Service.queryTreeListNoPage(queryWrapper);
            IPage<{{entityName}}> pageList = new Page<>(1, 10, list.size());
            pageList.setRecords(list);
            return Result.OK(pageList);
        } else {
            String parentId = entity.getPid();
            if (oConvertUtils.isEmpty(parentId)) {
                parentId = "0";
            }
            entity.setPid(null);
            QueryWrapper<{{entityName}}> queryWrapper = QueryGenerator.initQueryWrapper(entity, req.getParameterMap());
            // 使用 eq 防止模糊查询
            queryWrapper.eq("pid", parentId);
            Page<{{entityName}}> page = new Page<>(pageNo, pageSize);
            IPage<{{entityName}}> pageList = {{entityName_uncap}}Service.page(page, queryWrapper);
            return Result.OK(pageList);
        }
    }

    /**
     * 获取子数据（展开树节点时调用）
     */
    @Operation(summary = "{{description}}-获取子数据")
    @GetMapping(value = "/childList")
    public Result<IPage<{{entityName}}>> queryChildList({{entityName}} entity, HttpServletRequest req) {
        QueryWrapper<{{entityName}}> queryWrapper = QueryGenerator.initQueryWrapper(entity, req.getParameterMap());
        List<{{entityName}}> list = {{entityName_uncap}}Service.list(queryWrapper);
        IPage<{{entityName}}> pageList = new Page<>(1, 10, list.size());
        pageList.setRecords(list);
        return Result.OK(pageList);
    }

    /**
     * 批量查询子节点（已展开节点刷新时批量加载子数据）
     */
    @Operation(summary = "{{description}}-批量获取子数据")
    @GetMapping("/getChildListBatch")
    public Result getChildListBatch(@RequestParam("parentIds") String parentIds) {
        try {
            QueryWrapper<{{entityName}}> queryWrapper = new QueryWrapper<>();
            List<String> parentIdList = Arrays.asList(parentIds.split(","));
            queryWrapper.in("pid", parentIdList);
            List<{{entityName}}> list = {{entityName_uncap}}Service.list(queryWrapper);
            IPage<{{entityName}}> pageList = new Page<>(1, 10, list.size());
            pageList.setRecords(list);
            return Result.OK(pageList);
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            return Result.error("批量查询子节点失败：" + e.getMessage());
        }
    }

    /**
     * 【vue3专用】加载节点的子数据（用于JTreeSelect父节点选择组件）
     */
    @RequestMapping(value = "/loadTreeChildren", method = RequestMethod.GET)
    public Result<List<SelectTreeModel>> loadTreeChildren(@RequestParam(name = "pid") String pid) {
        Result<List<SelectTreeModel>> result = new Result<>();
        try {
            List<SelectTreeModel> ls = {{entityName_uncap}}Service.queryListByPid(pid);
            result.setResult(ls);
            result.setSuccess(true);
        } catch (Exception e) {
            e.printStackTrace();
            result.setMessage(e.getMessage());
            result.setSuccess(false);
        }
        return result;
    }

    /**
     * 【vue3专用】加载一级节点/如果是同步则所有数据（用于JTreeSelect父节点选择组件）
     */
    @RequestMapping(value = "/loadTreeRoot", method = RequestMethod.GET)
    public Result<List<SelectTreeModel>> loadTreeRoot(@RequestParam(name = "async") Boolean async, @RequestParam(name = "pcode") String pcode) {
        Result<List<SelectTreeModel>> result = new Result<>();
        try {
            List<SelectTreeModel> ls = {{entityName_uncap}}Service.queryListByCode(pcode);
            if (!async) {
                loadAllChildren(ls);
            }
            result.setResult(ls);
            result.setSuccess(true);
        } catch (Exception e) {
            e.printStackTrace();
            result.setMessage(e.getMessage());
            result.setSuccess(false);
        }
        return result;
    }

    /**
     * 递归求子节点 同步加载用到
     */
    private void loadAllChildren(List<SelectTreeModel> ls) {
        for (SelectTreeModel tsm : ls) {
            List<SelectTreeModel> temp = {{entityName_uncap}}Service.queryListByPid(tsm.getKey());
            if (temp != null && temp.size() > 0) {
                tsm.setChildren(temp);
                loadAllChildren(temp);
            }
        }
    }

    // 注意：树表批量删除应逐条调用 delete{{entityName}} 以正确处理树结构
    @DeleteMapping(value = "/deleteBatch")
    public Result<String> deleteBatch(@RequestParam(name = "ids", required = true) String ids) {
        for (String id : ids.split(",")) {
            {{entityName_uncap}}Service.delete{{entityName}}(id);
        }
        return Result.OK("批量删除成功!");
    }
```

**注意：** 如果实体中有多选/checkbox类字段，需在 `rootList` 方法中添加自定义查询规则：
```java
    Map<String, QueryRuleEnum> customeRuleMap = new HashMap<>();
    customeRuleMap.put("多选字段名", QueryRuleEnum.LIKE_WITH_OR);
    // 然后传给 QueryGenerator.initQueryWrapper(entity, req.getParameterMap(), customeRuleMap);
```

### B6. 树表前端 API ({{entityName}}.api.ts)

树表 API 完整模板（注意区别于单表的几个关键点）：

```typescript
import { defHttp } from '/@/utils/http/axios';
import { useMessage } from '/@/hooks/web/useMessage';

const { createConfirm } = useMessage();

enum Api {
  rootList = '/{{entityPackagePath}}/{{entityName_uncap}}/rootList',
  childList = '/{{entityPackagePath}}/{{entityName_uncap}}/childList',
  getChildListBatch = '/{{entityPackagePath}}/{{entityName_uncap}}/getChildListBatch',
  save = '/{{entityPackagePath}}/{{entityName_uncap}}/add',
  edit = '/{{entityPackagePath}}/{{entityName_uncap}}/edit',
  deleteOne = '/{{entityPackagePath}}/{{entityName_uncap}}/delete',
  deleteBatch = '/{{entityPackagePath}}/{{entityName_uncap}}/deleteBatch',
  importExcel = '/{{entityPackagePath}}/{{entityName_uncap}}/importExcel',
  exportXls = '/{{entityPackagePath}}/{{entityName_uncap}}/exportXls',
  loadTreeData = '/{{entityPackagePath}}/{{entityName_uncap}}/loadTreeRoot',
}

export const getExportUrl = Api.exportXls;
export const getImportUrl = Api.importExcel;
export const list = (params) => defHttp.get({ url: Api.rootList, params });
export const getChildList = (params) => defHttp.get({ url: Api.childList, params });
// 关键：isTransformResponse: false 返回完整 Result 对象，用于 loadDataByExpandedRows
export const getChildListBatch = (params) => defHttp.get({ url: Api.getChildListBatch, params }, { isTransformResponse: false });
export const deleteOne = (params, handleSuccess) => {
  return defHttp.delete({ url: Api.deleteOne, params }, { joinParamsToUrl: true }).then(() => {
    handleSuccess();
  });
};
export const batchDelete = (params, handleSuccess) => {
  createConfirm({
    iconType: 'warning',
    title: '确认删除',
    content: '是否删除选中数据',
    okText: '确认',
    cancelText: '取消',
    onOk: () => {
      return defHttp.delete({ url: Api.deleteBatch, data: params }, { joinParamsToUrl: true }).then(() => {
        handleSuccess();
      });
    },
  });
};
export const saveOrUpdate = (params, isUpdate) => {
  let url = isUpdate ? Api.edit : Api.save;
  return defHttp.post({ url: url, params });
};
export const loadTreeData = (params) => defHttp.get({ url: Api.loadTreeData, params });
```

### B7. 树表前端 data.ts 差异

`formSchema` 中 `pid` 字段必须使用 `JTreeSelect` 组件（而非隐藏的 Input），配置如下：

```typescript
// formSchema 中的 pid 字段
{
  label: '父级节点',
  field: 'pid',
  component: 'JTreeSelect',
  componentProps: {
    dict: '{{tableName}},{{displayField}},id',  // 表名,显示字段,值字段
    pidField: 'pid',
    pidValue: '0',
    hasChildField: 'has_child',
    placeholder: '请选择父级节点',
  },
},
```

columns 中 `title` 字段（树表主显示列）建议 `align: 'left'`，便于展示层级缩进。

### B8. 树表前端 List 页面 ({{entityName}}List.vue) — 完整模板

树表 List 页面与单表有**根本性差异**，需要完整的树节点展开/收缩/懒加载/刷新逻辑：

```vue
<template>
  <div>
    <BasicTable @register="registerTable" :rowSelection="rowSelection" :expandedRowKeys="expandedRowKeys" @expand="handleExpand" @fetch-success="onFetchSuccess">
      <template #tableTitle>
        <a-button type="primary" v-auth="'{{entityPackage}}:{{tableName}}:add'" @click="handleCreate" preIcon="ant-design:plus-outlined"> 新增</a-button>
        <a-button type="primary" v-auth="'{{entityPackage}}:{{tableName}}:exportXls'" preIcon="ant-design:export-outlined" @click="onExportXls"> 导出</a-button>
        <j-upload-button type="primary" v-auth="'{{entityPackage}}:{{tableName}}:importExcel'" preIcon="ant-design:import-outlined" @click="onImportXls">导入</j-upload-button>
        <a-dropdown v-if="selectedRowKeys.length > 0">
          <template #overlay>
            <a-menu>
              <a-menu-item key="1" @click="batchHandleDelete">
                <Icon icon="ant-design:delete-outlined" />
                删除
              </a-menu-item>
            </a-menu>
          </template>
          <a-button v-auth="'{{entityPackage}}:{{tableName}}:deleteBatch'">批量操作
            <Icon icon="mdi:chevron-down" />
          </a-button>
        </a-dropdown>
        <!-- 高级查询 -->
        <super-query :config="superQueryConfig" @search="handleSuperQuery" />
      </template>
      <template #action="{ record }">
        <TableAction :actions="getTableAction(record)" :dropDownActions="getDropDownAction(record)" />
      </template>
      <template v-slot:bodyCell="{ column, record, index, text }">
        {{!-- 根据业务需要添加自定义列渲染 --}}
      </template>
    </BasicTable>
    <{{entityName}}Modal @register="registerModal" @success="handleSuccess" />
  </div>
</template>

<script lang="ts" name="{{entityPackage}}-{{entityName_uncap}}" setup>
  import { ref, reactive, unref } from 'vue';
  import { BasicTable, TableAction } from '/@/components/Table';
  import { useModal } from '/@/components/Modal';
  import { useListPage } from '/@/hooks/system/useListPage';
  import {{entityName}}Modal from './components/{{entityName}}Modal.vue';
  import { columns, searchFormSchema, superQuerySchema } from './{{entityName}}.data';
  import { list, getChildList, getChildListBatch, deleteOne, batchDelete, getExportUrl, getImportUrl } from './{{entityName}}.api';
  import { getDateByPicker } from '/@/utils';

  const queryParam = reactive<any>({});
  const expandedRowKeys = ref<Array<string | number>>([]);
  const [registerModal, { openModal }] = useModal();
  // 日期个性化选择（如有季度/年/月/周字段）
  const fieldPickers = reactive({
    // quarterVal: 'quarter', yearVal: 'year', monthVal: 'month', weekVal: 'week',
  });

  const { prefixCls, tableContext, onExportXls, onImportXls } = useListPage({
    tableProps: {
      title: '{{description}}',
      api: list,
      columns,
      canResize: true,
      isTreeTable: true,
      formConfig: {
        schemas: searchFormSchema,
        autoSubmitOnEnter: true,
        showAdvancedButton: true,
        fieldMapToNumber: [],
        fieldMapToTime: [],
      },
      actionColumn: {
        width: 240,
        fixed: 'right',
      },
      beforeFetch: (params) => {
        if (params && fieldPickers) {
          for (let key in fieldPickers) {
            if (params[key]) {
              params[key] = getDateByPicker(params[key], fieldPickers[key]);
            }
          }
        }
        params['hasQuery'] = 'true';
        return Object.assign(params, queryParam);
      },
    },
    exportConfig: {
      name: '{{description}}',
      url: getExportUrl,
      params: queryParam,
    },
    importConfig: {
      url: getImportUrl,
      success: importSuccess,
    },
  });

  const [registerTable, { reload, updateTableDataRecord, findTableDataRecord, getDataSource }, { rowSelection, selectedRowKeys }] = tableContext;
  const superQueryConfig = reactive(superQuerySchema);

  /**
   * 接口请求成功后回调：为有子节点的数据添加loading占位
   */
  function onFetchSuccess(result) {
    getDataByResult(result.items) && loadDataByExpandedRows();
  }

  /**
   * 根据已展开的行查询数据（用于保存后刷新时异步加载子级的数据）
   */
  async function loadDataByExpandedRows() {
    if (unref(expandedRowKeys).length > 0) {
      const res = await getChildListBatch({ parentIds: unref(expandedRowKeys).join(',') });
      if (res.success && res.result.records.length > 0) {
        let records = res.result.records;
        const listMap = new Map();
        for (let item of records) {
          let pid = item['pid'];
          if (unref(expandedRowKeys).includes(pid)) {
            let mapList = listMap.get(pid);
            if (mapList == null) {
              mapList = [];
            }
            mapList.push(item);
            listMap.set(pid, mapList);
          }
        }
        let childrenMap = listMap;
        let fn = (list) => {
          if (list) {
            list.forEach((data) => {
              if (unref(expandedRowKeys).includes(data.id)) {
                data.children = getDataByResult(childrenMap.get(data.id));
                fn(data.children);
              }
            });
          }
        };
        fn(getDataSource());
      }
    }
  }

  /**
   * 处理数据集：为 hasChild='1' 的节点添加 loading 占位子节点
   */
  function getDataByResult(result) {
    if (result && result.length > 0) {
      return result.map((item) => {
        if (item['hasChild'] == '1') {
          let loadChild = { id: item.id + '_loadChild', name: 'loading...', isLoading: true };
          item.children = [loadChild];
        }
        return item;
      });
    }
  }

  /**
   * 树节点展开/合并：展开时懒加载子节点数据
   */
  async function handleExpand(expanded, record) {
    if (expanded) {
      expandedRowKeys.value.push(record.id);
      if (record.children.length > 0 && !!record.children[0].isLoading) {
        let result = await getChildList({ pid: record.id });
        result = result.records ? result.records : result;
        if (result && result.length > 0) {
          record.children = getDataByResult(result);
        } else {
          record.children = null;
          record.hasChild = '0';
        }
      }
    } else {
      let keyIndex = expandedRowKeys.value.indexOf(record.id);
      if (keyIndex >= 0) {
        expandedRowKeys.value.splice(keyIndex, 1);
      }
    }
  }

  /**
   * 操作表格后处理树节点展开
   */
  async function expandTreeNode(key) {
    let record = findTableDataRecord(key);
    expandedRowKeys.value.push(key);
    let result = await getChildList({ pid: key });
    if (result && result.length > 0) {
      record.children = getDataByResult(result);
    } else {
      record.children = null;
      record.hasChild = '0';
    }
    updateTableDataRecord(key, record);
  }

  function handleSuperQuery(params) {
    Object.keys(params).map((k) => {
      queryParam[k] = params[k];
    });
    reload();
  }

  function handleCreate() {
    openModal(true, { isUpdate: false });
  }

  function handleAddChild(record) {
    openModal(true, { record: { pid: record.id }, isUpdate: false });
  }

  function handleEdit(record) {
    openModal(true, { record, isUpdate: true });
  }

  function handleDetail(record) {
    openModal(true, { record, isUpdate: true, hideFooter: true });
  }

  async function handleDelete(record) {
    await deleteOne({ id: record.id }, importSuccess);
  }

  async function batchHandleDelete() {
    const ids = selectedRowKeys.value.filter((item) => !item.includes('loadChild'));
    await batchDelete({ ids: ids }, importSuccess);
  }

  function importSuccess() {
    (selectedRowKeys.value = []) && reload();
  }

  /**
   * 成功回调（编辑/新增后精确刷新，避免全量reload）
   */
  async function handleSuccess({ isUpdate, values, expandedArr, changeParent }) {
    if (isUpdate) {
      if (changeParent) {
        // 父节点变更，需要全量刷新
        reload();
      } else {
        // 父节点未变，只更新单条记录
        let data = await list({ id: values.id, pageSize: 1, pageNo: 1, pid: values['pid'] });
        if (data && data.records && data.records.length > 0) {
          updateTableDataRecord(values.id, data.records[0]);
        } else {
          updateTableDataRecord(values.id, values);
        }
      }
    } else {
      if (!values['id'] || !values['pid']) {
        // 新增根节点
        reload();
      } else {
        // 新增子节点：按展开路径逐级加载
        expandedRowKeys.value = [];
        for (let key of unref(expandedArr)) {
          await expandTreeNode(key);
        }
      }
    }
  }

  function getTableAction(record) {
    return [
      { label: '编辑', onClick: handleEdit.bind(null, record), auth: '{{entityPackage}}:{{tableName}}:edit' },
      { label: '添加子节点', onClick: handleAddChild.bind(null, record), auth: '{{entityPackage}}:{{tableName}}:add' },
    ];
  }

  function getDropDownAction(record) {
    return [
      { label: '详情', onClick: handleDetail.bind(null, record) },
      {
        label: '删除',
        popConfirm: { title: '确定删除吗?', confirm: handleDelete.bind(null, record), placement: 'topLeft' },
        auth: '{{entityPackage}}:{{tableName}}:delete',
      },
    ];
  }
</script>

<style lang="less" scoped>
  :deep(.ant-picker),:deep(.ant-input-number) {
    width: 100%;
  }
</style>
```

### B9. 树表前端 Modal ({{entityName}}Modal.vue) — 完整模板

树表 Modal 与单表的关键差异：
1. 打开时加载父级树数据（`loadTreeData`），用于 JTreeSelect 组件
2. 编辑时通过 `updateSchema` 设置 `hiddenNodeKey`，防止选择自己作为父节点
3. 提交成功后回传 `expandedArr`（展开路径）和 `changeParent`（是否变更父级），以便 List 页面精确刷新

```vue
<template>
  <BasicModal v-bind="$attrs" @register="registerModal" destroyOnClose :maxHeight="500" :width="800" :title="title" @ok="handleSubmit">
    <BasicForm @register="registerForm" name="{{entityName}}Form" />
  </BasicModal>
</template>

<script lang="ts" setup>
  import { ref, computed, unref, reactive } from 'vue';
  import { BasicModal, useModalInner } from '/@/components/Modal';
  import { BasicForm, useForm } from '/@/components/Form';
  import { formSchema } from '../{{entityName}}.data';
  import { saveOrUpdate, loadTreeData } from '../{{entityName}}.api';
  import { getDateByPicker } from '/@/utils';

  const emit = defineEmits(['register', 'success']);
  const isUpdate = ref(true);
  const isDetail = ref(false);
  const expandedRowKeys = ref([]);
  const treeData = ref([]);
  // 当前编辑的数据（用于判断父节点是否变更）
  let model: Nullable<Recordable> = null;
  // 日期个性化选择（如有季度/年/月/周字段）
  const fieldPickers = reactive({
    // quarterVal: 'quarter', yearVal: 'year', monthVal: 'month', weekVal: 'week',
  });

  const [registerForm, { setProps, resetFields, setFieldsValue, validate, updateSchema, scrollToField }] = useForm({
    schemas: formSchema,
    showActionButtonGroup: false,
    baseColProps: { span: 24 },
    labelCol: { xs: { span: 24 }, sm: { span: 4 } },
    wrapperCol: { xs: { span: 24 }, sm: { span: 18 } },
    baseRowStyle: { padding: '0 20px' },
  });

  const [registerModal, { setModalProps, closeModal }] = useModalInner(async (data) => {
    await resetFields();
    expandedRowKeys.value = [];
    setModalProps({ confirmLoading: false, minHeight: 80, showOkBtn: !data?.hideFooter });
    isUpdate.value = !!data?.isUpdate;
    isDetail.value = !data?.hideFooter;
    if (data?.record) {
      model = data.record;
      await setFieldsValue({ ...data.record });
      // 编辑时隐藏自身节点（防止选自己做父级）
      updateSchema([{ field: 'pid', componentProps: { hiddenNodeKey: data.record.id } }]);
    } else {
      model = null;
      updateSchema([{ field: 'pid', componentProps: { hiddenNodeKey: '' } }]);
    }
    // 加载父级节点树信息（仅用于 getExpandKeysByPid，不传给 JTreeSelect）
    // 注意：JTreeSelect 通过 dict 配置自行加载数据，updateSchema 中禁止传递 treeData！
    treeData.value = await loadTreeData({ async: false, pcode: '' });
    // 详情模式下禁用表单
    setProps({ disabled: !!data?.hideFooter });
  });

  const title = computed(() => (!unref(isUpdate) ? '新增' : !unref(isDetail) ? '详情' : '编辑'));

  /**
   * 根据pid获取展开的节点路径（从子到根）
   */
  function getExpandKeysByPid(pid, arr) {
    if (pid && arr && arr.length > 0) {
      for (let i = 0; i < arr.length; i++) {
        if (arr[i].key == pid && unref(expandedRowKeys).indexOf(pid) < 0) {
          expandedRowKeys.value.push(arr[i].key);
          getExpandKeysByPid(arr[i]['parentId'], unref(treeData));
        } else {
          getExpandKeysByPid(pid, arr[i].children);
        }
      }
    }
  }

  const changeDateValue = (formData) => {
    if (formData && fieldPickers) {
      for (let key in fieldPickers) {
        if (formData[key]) {
          formData[key] = getDateByPicker(formData[key], fieldPickers[key]);
        }
      }
    }
  };

  async function handleSubmit() {
    try {
      let values = await validate();
      changeDateValue(values);
      setModalProps({ confirmLoading: true });
      await saveOrUpdate(values, isUpdate.value);
      closeModal();
      // 收集展开的节点路径信息
      await getExpandKeysByPid(values['pid'], unref(treeData));
      // 回传给 List 页面进行精确刷新
      emit('success', {
        isUpdate: unref(isUpdate),
        values: { ...values },
        expandedArr: unref(expandedRowKeys).reverse(),
        changeParent: model != null && model['pid'] != values['pid'],
      });
    } catch ({ errorFields }) {
      if (errorFields) {
        const firstField = errorFields[0];
        if (firstField) {
          scrollToField(firstField.name, { behavior: 'smooth', block: 'center' });
        }
      }
      return Promise.reject(errorFields);
    } finally {
      setModalProps({ confirmLoading: false });
    }
  }
</script>

<style lang="less" scoped>
  :deep(.ant-input-number) {
    width: 100%;
  }
  :deep(.ant-calendar-picker) {
    width: 100%;
  }
</style>
```

### B10. 树表技术要点总结

| 技术点 | 说明 |
|--------|------|
| **懒加载占位** | `onFetchSuccess` + `getDataByResult` 为 `hasChild='1'` 的节点添加 `isLoading` 占位子节点 |
| **占位节点显示字段** | loading 占位节点的显示字段名必须与 columns 第一列 dataIndex 一致（如 `categoryName: 'loading...'`，不要写 `name`） |
| **展开懒加载** | `handleExpand` 判断 `isLoading` 占位，首次展开时请求 `childList` 接口 |
| **handleExpand 结果处理** | `result = result.records ? result.records : result` 兼容返回 Page 和 List 两种格式 |
| **批量子节点恢复** | `loadDataByExpandedRows` 页面刷新后根据 `expandedRowKeys` 批量请求 `getChildListBatch` 恢复子数据 |
| **精确刷新** | `handleSuccess` 区分：编辑不变父→重新查询单条（含dictText），编辑变父→全刷新，新增根→全刷新，新增子→按路径展开 |
| **编辑后重新查询** | 编辑后必须 `await list({id, pageSize:1, pageNo:1})` 重新查询，不能直接用 form values（缺少 `_dictText` 翻译） |
| **新增子节点前清空** | 新增子节点展开前必须 `expandedRowKeys.value = []` 先清空，否则展开逻辑出错 |
| **展开路径回传** | Modal 的 `getExpandKeysByPid` 递归收集从当前节点到根的展开路径，提交后回传给 List |
| **父节点变更检测** | Modal 保存 `model` 原始数据，提交时对比 `model.pid != values.pid` 判断是否变更父级 |
| **隐藏自身节点** | 编辑时 `updateSchema` **只传** `hiddenNodeKey`，**禁止传 treeData**（会导致下拉框 label 变 value） |
| **treeData 用途** | `treeData` 变量仅用于 `getExpandKeysByPid` 计算展开路径，不传给 JTreeSelect（组件通过 dict 自行加载） |
| **API isTransformResponse** | `getChildListBatch` 必须设 `{ isTransformResponse: false }` 返回完整 Result 对象 |
| **批量删除过滤** | `batchHandleDelete` 需过滤掉 `_loadChild` 占位节点的 ID |
| **批量删除递归** | Controller 批量删除应逐条调用 `deleteXxx` 以正确处理树结构（递归子节点+父节点状态） |
| **搜索模式** | `rootList` 的 `hasQuery=true` 参数触发 `queryTreeListNoPage`，搜索结果递归找到根节点展示 |
| **pid 组件** | formSchema 中 `pid` 使用 `JTreeSelect` 组件（非隐藏 Input），配置 `dict/pidField/pidValue/hasChildField` |
| **id 隐藏字段位置** | formSchema 中 `id` 隐藏字段放在**最后**（参考 JeecgBoot 代码生成器标准输出） |
| **Mapper XML 参数名** | `updateTreeNodeStatus` 用 `#{id}` `#{status}`，`queryListByPid` 用 `#{pid}`，需包含 `query` 的 foreach 支持 |
| **详情模式** | Modal 用 `setProps({ disabled: !!data?.hideFooter })` 禁用表单，`showOkBtn: !!!data?.hideFooter` 隐藏确认按钮 |
| **权限和布局** | List 所有按钮需 `v-auth`，操作拆分为主操作（编辑+添加下级）和下拉操作（详情+删除），`actionColumn.fixed:'right'` |

---

## C. 一对多模式差异

一对多在单表基础上有以下差异：

### C1. 子表 Entity

每个子表生成独立的 Entity，包含外键字段：
```java
    /**主表ID（外键）*/
    @Schema(description = "主表ID")
    private String {{mainEntityName_uncap}}Id;  // 外键字段名默认为 主表实体名(camelCase) + Id
```
注意：子表 Entity 的外键字段不加 `@Excel` 注解（导出时忽略）。

### C2. 子表 Mapper

```java
public interface {{subEntityName}}Mapper extends BaseMapper<{{subEntityName}}> {
    /**
     * 通过主表id删除子表数据
     */
    @Delete("DELETE FROM {{subTableName}} WHERE {{foreignKey}} = #{mainId}")
    boolean deleteByMainId(@Param("mainId") String mainId);

    /**
     * 通过主表id查询子表数据
     */
    List<{{subEntityName}}> selectByMainId(@Param("mainId") String mainId);
}
```

### C3. 主表 Service 接口

```java
public interface I{{entityName}}Service extends IService<{{entityName}}> {
    /**
     * 添加一对多
     */
    public void saveMain({{entityName}} entity, List<{{subEntityName}}> subList);

    /**
     * 修改一对多
     */
    public void updateMain({{entityName}} entity, List<{{subEntityName}}> subList);

    /**
     * 删除一对多
     */
    public void delMain(String id);

    /**
     * 批量删除一对多
     */
    public void delBatchMain(Collection<? extends Serializable> idList);
}
```

### C4. 主表 ServiceImpl

```java
@Service
public class {{entityName}}ServiceImpl extends ServiceImpl<{{entityName}}Mapper, {{entityName}}> implements I{{entityName}}Service {

    @Autowired
    private {{subEntityName}}Mapper {{subEntityName_uncap}}Mapper;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void saveMain({{entityName}} entity, List<{{subEntityName}}> subList) {
        baseMapper.insert(entity);
        if (subList != null && subList.size() > 0) {
            for ({{subEntityName}} sub : subList) {
                sub.set{{mainEntityName}}Id(entity.getId());  // 设置外键
                {{subEntityName_uncap}}Mapper.insert(sub);
            }
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void updateMain({{entityName}} entity, List<{{subEntityName}}> subList) {
        baseMapper.updateById(entity);
        // 先删后增
        {{subEntityName_uncap}}Mapper.deleteByMainId(entity.getId());
        if (subList != null && subList.size() > 0) {
            for ({{subEntityName}} sub : subList) {
                sub.set{{mainEntityName}}Id(entity.getId());
                {{subEntityName_uncap}}Mapper.insert(sub);
            }
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void delMain(String id) {
        {{subEntityName_uncap}}Mapper.deleteByMainId(id);
        baseMapper.deleteById(id);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void delBatchMain(Collection<? extends Serializable> idList) {
        for (Serializable id : idList) {
            {{subEntityName_uncap}}Mapper.deleteByMainId(id.toString());
            baseMapper.deleteById(id);
        }
    }
}
```

### C5. Page VO（Excel导入导出用）

```java
package org.jeecg.modules.{{entityPackage}}.vo;

import org.jeecg.modules.{{entityPackage}}.entity.{{entityName}};
import org.jeecg.modules.{{entityPackage}}.entity.{{subEntityName}};
import lombok.Data;
import org.jeecgframework.poi.excel.annotation.ExcelCollection;
import java.util.List;

@Data
public class {{entityName}}Page {
    // 主表字段（同 Entity，不含系统字段）
    // ...

    @ExcelCollection(name = "{{subDescription}}")
    private List<{{subEntityName}}> {{subEntityName_uncap}}List;
}
```

### C6. 一对多 Controller 完整模板

> **⚠️ 一对多 Controller 与单表完全不同，必须整体替换 A2 模板：**
> - **不继承** `JeecgController`，是独立 class
> - 注入 `I{{subEntityName}}Service`（不是 Mapper）
> - 导出/导入有完整自定义逻辑（不能用 `super.exportXls/importExcel`）
> - edit 方法需先查询主表实体是否存在

```java
package org.jeecg.modules.{{entityPackage}}.controller;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import org.jeecgframework.poi.excel.ExcelImportUtil;
import org.jeecgframework.poi.excel.def.NormalExcelConstants;
import org.jeecgframework.poi.excel.entity.ExportParams;
import org.jeecgframework.poi.excel.entity.ImportParams;
import org.jeecgframework.poi.excel.entity.enmus.ExcelType;
import org.jeecgframework.poi.excel.view.JeecgEntityExcelView;
import org.jeecg.common.system.vo.LoginUser;
import org.apache.shiro.SecurityUtils;
import org.jeecg.common.api.vo.Result;
import org.jeecg.common.system.query.QueryGenerator;
import org.jeecg.common.util.oConvertUtils;
import org.jeecg.modules.{{entityPackage}}.entity.{{entityName}};
import org.jeecg.modules.{{entityPackage}}.entity.{{subEntityName}};
import org.jeecg.modules.{{entityPackage}}.vo.{{entityName}}Page;
import org.jeecg.modules.{{entityPackage}}.service.I{{entityName}}Service;
import org.jeecg.modules.{{entityPackage}}.service.I{{subEntityName}}Service;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.multipart.MultipartHttpServletRequest;
import org.springframework.web.servlet.ModelAndView;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import lombok.extern.slf4j.Slf4j;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.Operation;
import org.jeecg.common.aspect.annotation.AutoLog;
import org.apache.shiro.authz.annotation.RequiresPermissions;

/**
 * @Description: {{description}}
 * @Author: jeecg-boot
 * @Date: {{today}}
 * @Version: V1.0
 */
@Tag(name = "{{description}}")
@RestController
@RequestMapping("/{{entityPackagePath}}/{{entityName_uncap}}")
@Slf4j
public class {{entityName}}Controller {

    @Autowired
    private I{{entityName}}Service {{entityName_uncap}}Service;

    @Autowired
    private I{{subEntityName}}Service {{subEntityName_uncap}}Service;

    //@AutoLog(value = "{{description}}-分页列表查询")
    @Operation(summary = "{{description}}-分页列表查询")
    @GetMapping(value = "/list")
    public Result<IPage<{{entityName}}>> queryPageList({{entityName}} {{entityName_uncap}},
                                                        @RequestParam(name = "pageNo", defaultValue = "1") Integer pageNo,
                                                        @RequestParam(name = "pageSize", defaultValue = "10") Integer pageSize,
                                                        HttpServletRequest req) {
        QueryWrapper<{{entityName}}> queryWrapper = QueryGenerator.initQueryWrapper({{entityName_uncap}}, req.getParameterMap());
        Page<{{entityName}}> page = new Page<{{entityName}}>(pageNo, pageSize);
        IPage<{{entityName}}> pageList = {{entityName_uncap}}Service.page(page, queryWrapper);
        return Result.OK(pageList);
    }

    @AutoLog(value = "{{description}}-添加")
    @Operation(summary = "{{description}}-添加")
    @RequiresPermissions("{{entityPackage}}:{{tableName}}:add")
    @PostMapping(value = "/add")
    public Result<String> add(@RequestBody {{entityName}}Page {{entityName_uncap}}Page) {
        {{entityName}} {{entityName_uncap}} = new {{entityName}}();
        BeanUtils.copyProperties({{entityName_uncap}}Page, {{entityName_uncap}});
        {{entityName_uncap}}Service.saveMain({{entityName_uncap}}, {{entityName_uncap}}Page.get{{subEntityName}}List());
        return Result.OK("添加成功！");
    }

    @AutoLog(value = "{{description}}-编辑")
    @Operation(summary = "{{description}}-编辑")
    @RequiresPermissions("{{entityPackage}}:{{tableName}}:edit")
    @RequestMapping(value = "/edit", method = {RequestMethod.PUT, RequestMethod.POST})
    public Result<String> edit(@RequestBody {{entityName}}Page {{entityName_uncap}}Page) {
        {{entityName}} {{entityName_uncap}} = new {{entityName}}();
        BeanUtils.copyProperties({{entityName_uncap}}Page, {{entityName_uncap}});
        {{entityName}} {{entityName_uncap}}Entity = {{entityName_uncap}}Service.getById({{entityName_uncap}}.getId());
        if ({{entityName_uncap}}Entity == null) {
            return Result.error("未找到对应数据");
        }
        {{entityName_uncap}}Service.updateMain({{entityName_uncap}}, {{entityName_uncap}}Page.get{{subEntityName}}List());
        return Result.OK("编辑成功!");
    }

    @AutoLog(value = "{{description}}-通过id删除")
    @Operation(summary = "{{description}}-通过id删除")
    @RequiresPermissions("{{entityPackage}}:{{tableName}}:delete")
    @DeleteMapping(value = "/delete")
    public Result<String> delete(@RequestParam(name = "id", required = true) String id) {
        {{entityName_uncap}}Service.delMain(id);
        return Result.OK("删除成功!");
    }

    @AutoLog(value = "{{description}}-批量删除")
    @Operation(summary = "{{description}}-批量删除")
    @RequiresPermissions("{{entityPackage}}:{{tableName}}:deleteBatch")
    @DeleteMapping(value = "/deleteBatch")
    public Result<String> deleteBatch(@RequestParam(name = "ids", required = true) String ids) {
        this.{{entityName_uncap}}Service.delBatchMain(Arrays.asList(ids.split(",")));
        return Result.OK("批量删除成功！");
    }

    //@AutoLog(value = "{{description}}-通过id查询")
    @Operation(summary = "{{description}}-通过id查询")
    @GetMapping(value = "/queryById")
    public Result<{{entityName}}> queryById(@RequestParam(name = "id", required = true) String id) {
        {{entityName}} {{entityName_uncap}} = {{entityName_uncap}}Service.getById(id);
        if ({{entityName_uncap}} == null) {
            return Result.error("未找到对应数据");
        }
        return Result.OK({{entityName_uncap}});
    }

    //@AutoLog(value = "{{subDescription}}-通过主表ID查询")
    @Operation(summary = "{{subDescription}}-主表ID查询")
    @GetMapping(value = "/query{{subEntityName}}ByMainId")
    public Result<List<{{subEntityName}}>> query{{subEntityName}}ListByMainId(@RequestParam(name = "id", required = true) String id) {
        List<{{subEntityName}}> {{subEntityName_uncap}}List = {{subEntityName_uncap}}Service.selectByMainId(id);
        return Result.OK({{subEntityName_uncap}}List);
    }

    @RequiresPermissions("{{entityPackage}}:{{tableName}}:exportXls")
    @RequestMapping(value = "/exportXls")
    public ModelAndView exportXls(HttpServletRequest request, {{entityName}} {{entityName_uncap}}) {
        QueryWrapper<{{entityName}}> queryWrapper = QueryGenerator.initQueryWrapper({{entityName_uncap}}, request.getParameterMap());
        LoginUser sysUser = (LoginUser) SecurityUtils.getSubject().getPrincipal();
        String selections = request.getParameter("selections");
        if (oConvertUtils.isNotEmpty(selections)) {
            queryWrapper.in("id", Arrays.asList(selections.split(",")));
        }
        List<{{entityName}}> {{entityName_uncap}}List = {{entityName_uncap}}Service.list(queryWrapper);
        List<{{entityName}}Page> pageList = new ArrayList<>();
        for ({{entityName}} main : {{entityName_uncap}}List) {
            {{entityName}}Page vo = new {{entityName}}Page();
            BeanUtils.copyProperties(main, vo);
            vo.set{{subEntityName}}List({{subEntityName_uncap}}Service.selectByMainId(main.getId()));
            pageList.add(vo);
        }
        ModelAndView mv = new ModelAndView(new JeecgEntityExcelView());
        mv.addObject(NormalExcelConstants.FILE_NAME, "{{description}}列表");
        mv.addObject(NormalExcelConstants.CLASS, {{entityName}}Page.class);
        mv.addObject(NormalExcelConstants.PARAMS, new ExportParams("{{description}}数据", "导出人:" + sysUser.getRealname(), "{{description}}", ExcelType.XSSF));
        mv.addObject(NormalExcelConstants.DATA_LIST, pageList);
        return mv;
    }

    @RequiresPermissions("{{entityPackage}}:{{tableName}}:importExcel")
    @RequestMapping(value = "/importExcel", method = RequestMethod.POST)
    public Result<?> importExcel(HttpServletRequest request, HttpServletResponse response) {
        MultipartHttpServletRequest multipartRequest = (MultipartHttpServletRequest) request;
        Map<String, MultipartFile> fileMap = multipartRequest.getFileMap();
        for (Map.Entry<String, MultipartFile> entity : fileMap.entrySet()) {
            MultipartFile file = entity.getValue();
            ImportParams params = new ImportParams();
            params.setTitleRows(2);
            params.setHeadRows(1);
            params.setNeedSave(true);
            try {
                List<{{entityName}}Page> list = ExcelImportUtil.importExcel(file.getInputStream(), {{entityName}}Page.class, params);
                for ({{entityName}}Page page : list) {
                    {{entityName}} po = new {{entityName}}();
                    BeanUtils.copyProperties(page, po);
                    {{entityName_uncap}}Service.saveMain(po, page.get{{subEntityName}}List());
                }
                return Result.OK("文件导入成功！数据行数:" + list.size());
            } catch (Exception e) {
                log.error(e.getMessage(), e);
                return Result.error("文件导入失败:" + e.getMessage());
            } finally {
                try {
                    file.getInputStream().close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
        return Result.OK("文件导入失败！");
    }
}
```

**子表 Service 接口（需同步生成）：**

```java
// I{{subEntityName}}Service.java
public interface I{{subEntityName}}Service extends IService<{{subEntityName}}> {
    List<{{subEntityName}}> selectByMainId(String mainId);
}

// {{subEntityName}}ServiceImpl.java
@Service
public class {{subEntityName}}ServiceImpl extends ServiceImpl<{{subEntityName}}Mapper, {{subEntityName}}> implements I{{subEntityName}}Service {
    @Override
    public List<{{subEntityName}}> selectByMainId(String mainId) {
        return baseMapper.selectByMainId(mainId);
    }
}
```

### C7. 前端差异 — api.ts

**vue3 封装风格：** 子表查询接口导出为 URL 字符串常量（不是函数），供 Modal 中 `defHttp.get` 或 `requestSubTableData` 使用：

```typescript
enum Api {
  // ... 主表 CRUD 接口
  {{subEntityName_uncap}}List = '/{{entityPackage}}/{{entityName_uncap}}/query{{subEntityName}}ByMainId',
}

// 子表接口导出为 URL 字符串（不是函数！）
export const {{subEntityName_uncap}}List = Api.{{subEntityName_uncap}}List;
```

**vue3Native 原生风格（C13）：** 子表查询接口导出为**函数**，且需要额外的 `queryDataById`。详见 C13-1。

### C8. 前端差异 — data.ts

一对多子表使用 `JVxeColumn[]`（**不是 FormSchema[]**），组件类型使用 `JVxeTypes` 枚举：

```typescript
import { JVxeTypes, JVxeColumn } from '/@/components/jeecg/JVxeTable/types';

export const {{subEntityName_uncap}}Columns: JVxeColumn[] = [
  {
    title: '字段标题',
    key: 'fieldName',        // 注意用 key 不是 field
    type: JVxeTypes.input,   // 注意用 JVxeTypes 不是 component 字符串
    width: '200px',          // 字符串带px
    placeholder: '请输入${title}',
    defaultValue: '',
  },
  // JVxeTypes 与 FormSchema component 的对应关系见 SKILL.md 的 JVxeTable 章节
];
```

**JVxeColumn 与 FormSchema 的关键区别：**
| 维度 | FormSchema | JVxeColumn |
|------|-----------|-----------|
| 字段名属性 | `field` | `key` |
| 组件类型属性 | `component: 'JDictSelectTag'` | `type: JVxeTypes.select` |
| 字典配置 | `componentProps: { dictCode: 'xxx' }` | 顶层属性 `dictCode: 'xxx'` |
| 下拉选项 | 自动从字典加载 | 需显式声明 `options: []` |
| 宽度 | `colProps: { span: 12 }` | `width: '200px'` |
| 校验规则 | `dynamicRules` 函数 | `validateRules` 数组 |
| 占位符 | `componentProps: { placeholder }` | 顶层属性 `placeholder`，支持 `${title}` |

一对一子表使用 `FormSchema[]`（与主表 formSchema 相同的写法）：

```typescript
export const {{subEntityName_uncap}}FormSchema: FormSchema[] = [
  // 与主表 formSchema 写法完全一致，使用 component/field/componentProps
];
```

### C9. 前端差异 — Modal.vue（核心模板）

#### Tab 风格核心特征

Tab-in-Modal 使用 **radio-group 标题栏** 切换主表/子表区域，一对一子表抽成**独立 Form.vue 组件**，通过 `useJvxeMethod` + `validateSubForm` 统一处理提交。

**关键模式：**
- Modal 标题栏用 `a-radio-group` + `a-radio-button`（不是 `a-tabs`）
- 各区域用 `v-show` 切换（不是 `a-tab-pane`），避免频繁销毁/重建
- `wrapClassName="j-cgform-tab-modal"` 启用专属样式
- 一对一子表抽成独立 `XxxForm.vue` 组件，暴露 `initFormData`/`getFormData`/`validateForm`/`resetFields` 方法
- 通过 `useJvxeMethod` 第6个参数 `validateSubForm` 校验所有一对一子表
- 不需要自写 `handleSubmit`，`useJvxeMethod` 返回的 `handleSubmit` 已整合所有校验和提交逻辑

#### 文件结构

Tab-in-Modal 风格比其他风格多一个一对一子表 Form 组件：

```
views/{{viewDir}}/
├── {{entityName}}List.vue                   # 主列表
├── {{entityName}}.api.ts                    # API（子表导出为URL字符串）
├── {{entityName}}.data.ts                   # 列/表单配置（JVxeColumn + FormSchema）
└── components/
    ├── {{entityName}}Modal.vue              # Modal（radio-group Tab 切换）
    └── {{detailEntityName}}Form.vue         # 一对一子表独立Form组件（仅有一对一子表时）
```

#### 一对一子表独立 Form 组件（{{detailEntityName}}Form.vue）

```html
<template>
    <BasicForm @register="registerForm" name="{{detailEntityName}}Form" class="basic-modal-form" />
</template>
<script lang="ts">
    import {defineComponent} from 'vue';
    import {BasicForm, useForm} from '/@/components/Form/index';
    import { {{detailEntityName_uncap}}FormSchema } from '../{{entityName}}.data';
    import {defHttp} from '/@/utils/http/axios';
    import { VALIDATE_FAILED } from '/@/utils/common/vxeUtils'

    export default defineComponent({
        name:"{{detailEntityName}}Form",
        components: {BasicForm},
        emits:['register'],
        props:{
            disabled: {
                type: Boolean,
                default: false
            }
        },
        setup(props,{emit}) {
            const [registerForm, { setProps, resetFields, setFieldsValue, getFieldsValue, validate, scrollToField }] = useForm({
                schemas: {{detailEntityName_uncap}}FormSchema,
                showActionButtonGroup: false,
                baseColProps: {span: 12}
            });
            // 初始化加载数据（url 是子表查询接口的 URL 字符串）
            function initFormData(url,id){
                if(id){
                     defHttp.get({url,params:{id}},{isTransformResponse:false}).then(res=>{
                       res.success && res.result && res.result.length > 0 && setFieldsValue({...res.result[0]});
                    })
                }
                setProps({disabled: props.disabled})
            }
            // 获取表单数据（返回数组，因为后端统一用 List<Entity> 接收）
            function getFormData(){
               let formData = getFieldsValue();
               Object.keys(formData).map(k=>{
                   if(formData[k] instanceof Array){
                       formData[k] = formData[k].join(',')
                   }
               });
               return [formData];
            }
            // 表单校验（index 参数对应 refKeys 数组中的位置）
            function validateForm(index){
                return new Promise((resolve, reject) => {
                    validate().then(()=>{
                        return resolve()
                    }).catch(({ errorFields }) => {
                      return reject({ error: VALIDATE_FAILED, index, errorFields: errorFields, scrollToField: scrollToField });
                    });
                })
            }
            return {
                registerForm,
                resetFields,
                initFormData,
                getFormData,
                validateForm
            }
        }
    })
</script>
<style lang="less" scoped>
  .basic-modal-form {
    overflow: auto;
    height: 340px;
  }
</style>
```

**Form 组件关键点：**
- 使用 Options API（`defineComponent`），不是 `<script setup>`，因为需要通过 `return` 暴露方法给父组件 `ref` 调用
- `initFormData(url, id)` 中 `isTransformResponse: false` 返回完整响应 `{success, result}`，取 `result[0]`
- `getFormData()` 返回**数组** `[formData]`，与后端 `List<Entity>` 对应
- `validateForm(index)` 的 `index` 参数对应 `refKeys` 数组位置，校验失败时自动跳转到对应 Tab
- FormSchema 中必须包含隐藏的 `id` 字段：`{ label: '', field: 'id', component: 'Input', show: false }`

#### Modal.vue — 纯一对多（无一对一子表）

```html
<template>
  <BasicModal ref="modalRef" destroyOnClose wrapClassName="j-cgform-tab-modal" v-bind="$attrs" @register="registerModal" :maxHeight="500" :width="896" @ok="handleSubmit">
    <template #title>
        <div class="titleArea">
          <div class="title">{{ title }}</div>
          <div class="right">
            <a-radio-group v-model:value="activeKey">
              <template v-for="(item, index) in tabNav" :key="index">
                <a-radio-button :value="item.tableName">{{ item.tableTxt }}</a-radio-button>
              </template>
            </a-radio-group>
          </div>
        </div>
     </template>
     <div class="contentArea">
        <BasicForm @register="registerForm" ref="formRef" v-show="activeKey == refKeys[0]" name="{{entityName}}Form"/>
         <JVxeTable
           v-show="activeKey == '{{subEntityName_uncap}}'"
           keep-source resizable
           ref="{{subEntityName_uncap}}"
           :loading="{{subEntityName_uncap}}Table.loading"
           :columns="{{subEntityName_uncap}}Table.columns"
           :dataSource="{{subEntityName_uncap}}Table.dataSource"
           :height="340"
           :disabled="formDisabled"
           :rowNumber="true"
           :rowSelection="true"
           :toolbar="true"
           />
     </div>
  </BasicModal>
</template>

<script lang="ts" setup>
    import {ref, computed, unref, reactive} from 'vue';
    import {BasicModal, useModalInner} from '/@/components/Modal';
    import {BasicForm, useForm} from '/@/components/Form/index';
    import { useJvxeMethod } from '/@/hooks/system/useJvxeMethods.ts'
    import {formSchema, {{subEntityName_uncap}}Columns} from '../{{entityName}}.data';
    import {saveOrUpdate, {{subEntityName_uncap}}List} from '../{{entityName}}.api';

    const emit = defineEmits(['register','success']);
    const isUpdate = ref(true);
    const formDisabled = ref(false);
    const modalRef = ref();
    // refKeys[0] 是主表的 key，后面是各子表的 key
    const refKeys = ref(['{{entityName_uncap}}', '{{subEntityName_uncap}}']);
    const tabNav = ref<any>([
      { tableName: '{{entityName_uncap}}', tableTxt: '{{description}}' },
      { tableName: '{{subEntityName_uncap}}', tableTxt: '{{subDescription}}' },
    ]);
    const activeKey = ref('{{entityName_uncap}}');
    const {{subEntityName_uncap}} = ref();
    const tableRefs = { {{subEntityName_uncap}} };
    const {{subEntityName_uncap}}Table = reactive({
          loading: false,
          dataSource: [],
          columns: {{subEntityName_uncap}}Columns
    })
    const [registerForm, {setProps, resetFields, setFieldsValue, validate}] = useForm({
        schemas: formSchema,
        showActionButtonGroup: false,
        baseColProps: {span: 12}
    });
    const [registerModal, {setModalProps, closeModal}] = useModalInner(async (data) => {
        await reset();
        setModalProps({confirmLoading: false, showCancelBtn: data?.showFooter, showOkBtn: data?.showFooter});
        isUpdate.value = !!data?.isUpdate;
        formDisabled.value = !data?.showFooter;
        if (unref(isUpdate)) {
            await setFieldsValue({ ...data.record });
            requestSubTableData({{subEntityName_uncap}}List, {id: data?.record?.id}, {{subEntityName_uncap}}Table)
        }
        setProps({ disabled: !data?.showFooter })
    });
    const [handleChangeTabs, handleSubmit, requestSubTableData, formRef] = useJvxeMethod(requestAddOrEdit, classifyIntoFormData, tableRefs, activeKey, refKeys);

    const title = computed(() => (!unref(isUpdate) ? '新增' : !unref(formDisabled) ? '编辑' : '详情'));
    async function reset(){
      await resetFields();
      activeKey.value = '{{entityName_uncap}}';
      {{subEntityName_uncap}}Table.dataSource = [];
    }
    function classifyIntoFormData(allValues) {
         let main = Object.assign({}, allValues.formValue)
         return {
           ...main,
           {{subEntityName_uncap}}List: allValues.tablesValue[0].tableData,
         }
    }
    async function requestAddOrEdit(values) {
        try {
            setModalProps({confirmLoading: true});
            await saveOrUpdate(values, isUpdate.value);
            closeModal();
            emit('success');
        } finally {
            setModalProps({confirmLoading: false});
        }
    }
</script>

<style lang="less" scoped>
  :deep(.ant-input-number) { width: 100%; }
  :deep(.ant-calendar-picker) { width: 100%; }
  .titleArea {
    display: flex;
    align-content: center;
    padding-right: 70px;
    .title { margin-right: 16px; line-height: 32px; }
    .right {
      overflow-x: auto; overflow-y: hidden; flex: 1; white-space: nowrap;
      .ant-radio-group { font-weight: normal; }
    }
  }
  html[data-theme='light'] {
    .right .ant-radio-group {
      :deep(.ant-radio-button-wrapper:not(.ant-radio-button-wrapper-checked)) { color: #555; }
    }
  }
</style>
<style lang="less">
.j-cgform-tab-modal {
   .contentArea { padding: 20px 1.5% 0; }
  .ant-modal .ant-modal-body > .scrollbar,
  .ant-tabs-nav .ant-tabs-tab { padding-top: 0; }
  .ant-tabs-top-bar { width: calc(100% - 55px); position: relative; left: -14px; }
  .ant-tabs .ant-tabs-top-content > .ant-tabs-tabpane { overflow: hidden auto; }
}
</style>
```

#### Modal.vue — 一对一 + 一对多混合（多个子表）

当同时存在一对一子表和一对多子表时，Modal 需额外引入一对一 Form 组件，并通过 `validateSubForm` 回调校验。

**与纯一对多的关键差异：**
- 多引入 `{{detailEntityName}}Form` 组件和 `VALIDATE_FAILED`
- `refKeys` 多一项一对一子表的 key
- `tabNav` 多一项一对一子表
- `useJvxeMethod` 第6个参数传入 `validateSubForm` 函数
- `reset()` 中额外调用 `{{detailEntityName_uncap}}Form.value.resetFields()`
- `classifyIntoFormData` 中调用 `{{detailEntityName_uncap}}Form.value.getFormData()` 获取一对一数据
- 编辑时通过 `{{detailEntityName_uncap}}Form.value.initFormData(url, id)` 加载一对一数据

```html
<template>
  <BasicModal ref="modalRef" destroyOnClose wrapClassName="j-cgform-tab-modal" v-bind="$attrs" @register="registerModal" :maxHeight="500" :width="896" @ok="handleSubmit">
    <template #title>
        <div class="titleArea">
          <div class="title">{{ title }}</div>
          <div class="right">
            <a-radio-group v-model:value="activeKey">
              <template v-for="(item, index) in tabNav" :key="index">
                <a-radio-button :value="item.tableName">{{ item.tableTxt }}</a-radio-button>
              </template>
            </a-radio-group>
          </div>
        </div>
     </template>
     <div class="contentArea">
        <BasicForm @register="registerForm" ref="formRef" v-show="activeKey == refKeys[0]" name="{{entityName}}Form"/>
         <JVxeTable
           v-show="activeKey == '{{subEntityName_uncap}}'"
           keep-source resizable
           ref="{{subEntityName_uncap}}"
           :loading="{{subEntityName_uncap}}Table.loading"
           :columns="{{subEntityName_uncap}}Table.columns"
           :dataSource="{{subEntityName_uncap}}Table.dataSource"
           :height="340"
           :disabled="formDisabled"
           :rowNumber="true" :rowSelection="true" :toolbar="true"
           />
         <{{detailEntityName}}Form ref="{{detailEntityName_uncap}}Form" :disabled="formDisabled" v-show="activeKey == '{{detailEntityName_uncap}}'"><\/{{detailEntityName}}Form>
     </div>
  </BasicModal>
</template>

<script lang="ts" setup>
    import {ref, computed, unref, reactive} from 'vue';
    import {BasicModal, useModalInner} from '/@/components/Modal';
    import {BasicForm, useForm} from '/@/components/Form/index';
    import { useJvxeMethod } from '/@/hooks/system/useJvxeMethods.ts'
    import {{detailEntityName}}Form from './{{detailEntityName}}Form.vue'
    import {formSchema, {{subEntityName_uncap}}Columns} from '../{{entityName}}.data';
    import {saveOrUpdate, {{subEntityName_uncap}}List, {{detailEntityName_uncap}}List} from '../{{entityName}}.api';
    import { VALIDATE_FAILED } from '/@/utils/common/vxeUtils'

    const emit = defineEmits(['register','success']);
    const isUpdate = ref(true);
    const formDisabled = ref(false);
    const modalRef = ref();
    const refKeys = ref(['{{entityName_uncap}}', '{{subEntityName_uncap}}', '{{detailEntityName_uncap}}']);
    const tabNav = ref<any>([
      { tableName: '{{entityName_uncap}}', tableTxt: '{{description}}' },
      { tableName: '{{subEntityName_uncap}}', tableTxt: '{{subDescription}}' },
      { tableName: '{{detailEntityName_uncap}}', tableTxt: '{{detailDescription}}' },
    ]);
    const activeKey = ref('{{entityName_uncap}}');
    const {{subEntityName_uncap}} = ref();
    const {{detailEntityName_uncap}}Form = ref();
    const tableRefs = { {{subEntityName_uncap}} };
    const {{subEntityName_uncap}}Table = reactive({
          loading: false,
          dataSource: [],
          columns: {{subEntityName_uncap}}Columns
    })
    const [registerForm, {setProps, resetFields, setFieldsValue, validate}] = useForm({
        schemas: formSchema,
        showActionButtonGroup: false,
        baseColProps: {span: 12}
    });
    const [registerModal, {setModalProps, closeModal}] = useModalInner(async (data) => {
        await reset();
        setModalProps({confirmLoading: false, showCancelBtn: data?.showFooter, showOkBtn: data?.showFooter});
        isUpdate.value = !!data?.isUpdate;
        formDisabled.value = !data?.showFooter;
        if (unref(isUpdate)) {
            await setFieldsValue({ ...data.record });
            {{detailEntityName_uncap}}Form.value.initFormData({{detailEntityName_uncap}}List, data?.record?.id)
            requestSubTableData({{subEntityName_uncap}}List, {id: data?.record?.id}, {{subEntityName_uncap}}Table)
        }
        setProps({ disabled: !data?.showFooter })
    });
    // 第6个参数 validateSubForm 用于校验一对一子表
    const [handleChangeTabs, handleSubmit, requestSubTableData, formRef] = useJvxeMethod(requestAddOrEdit, classifyIntoFormData, tableRefs, activeKey, refKeys, validateSubForm);

    const title = computed(() => (!unref(isUpdate) ? '新增' : !unref(formDisabled) ? '编辑' : '详情'));
    async function reset(){
      await resetFields();
      activeKey.value = '{{entityName_uncap}}';
      {{subEntityName_uncap}}Table.dataSource = [];
      {{detailEntityName_uncap}}Form.value.resetFields();
    }
    function classifyIntoFormData(allValues) {
         let main = Object.assign({}, allValues.formValue)
         return {
           ...main,
           {{subEntityName_uncap}}List: allValues.tablesValue[0].tableData,
           {{detailEntityName_uncap}}List: {{detailEntityName_uncap}}Form.value.getFormData(),
         }
    }
    // 校验所有一对一子表表单
    function validateSubForm(allValues){
        return new Promise((resolve,reject)=>{
            Promise.all([
                 {{detailEntityName_uncap}}Form.value.validateForm(2),
            ]).then(() => {
                resolve(allValues)
            }).catch(e => {
                if (e.error === VALIDATE_FAILED) {
                    activeKey.value = e.index == null ? unref(activeKey) : refKeys.value[e.index]
                    if (e.errorFields) {
                      const firstField = e.errorFields[0];
                      if (firstField) {
                        e.scrollToField(firstField.name, { behavior: 'smooth', block: 'center' });
                      }
                    }
                } else {
                    console.error(e)
                }
            })
        })
    }
    async function requestAddOrEdit(values) {
        try {
            setModalProps({confirmLoading: true});
            await saveOrUpdate(values, isUpdate.value);
            closeModal();
            emit('success');
        } finally {
            setModalProps({confirmLoading: false});
        }
    }
</script>
<!-- 样式同纯一对多 Modal，包含 titleArea + j-cgform-tab-modal -->
```

**`validateSubForm` 中 `validateForm(2)` 的参数说明：**
- 参数 `2` 是一对一子表在 `refKeys` 数组中的索引（从0开始：0=主表, 1=一对多子表, 2=一对一子表）
- 校验失败时通过 `refKeys.value[e.index]` 自动切换到对应 Tab
- 如有多个一对一子表，在 `Promise.all` 中追加，每个传入不同的 index

### C10. 一对多技术要点和常见陷阱

| 要点 | 说明 |
|------|------|
| **三种 Modal 布局风格** | **Tab-in-Modal(C9)**：radio-group 标题栏切换，主表/子表同级用 `v-show`，需 `wrapClassName="j-cgform-tab-modal"`。**内嵌子表(C12)/ERP(C11)**：原始布局，上面主表 BasicForm，下面子表用 `a-tabs` 组织，不需要 radio-group 和 `j-cgform-tab-modal` |
| **一对一子表必须抽成独立 Form.vue** | 使用 Options API（`defineComponent`）暴露 `initFormData`/`getFormData`/`validateForm`/`resetFields` 方法，父组件通过 `ref` 调用 |
| **Form.vue 用 isTransformResponse:false** | `initFormData` 中 `defHttp.get({url,params:{id}},{isTransformResponse:false})` 返回完整 `{success,result}`，取 `result[0]` 赋值 |
| **Form.vue 的 getFormData 返回数组** | `return [formData]` 包装成数组，因为后端统一用 `List<Entity>` 接收 |
| **validateSubForm 是 useJvxeMethod 第6个参数** | 有一对一子表时，`useJvxeMethod(requestAddOrEdit, classifyIntoFormData, tableRefs, activeKey, refKeys, validateSubForm)`，第6个参数传入校验函数 |
| **validateForm(index) 的 index 对应 refKeys 位置** | 例如 `refKeys = ['main', 'subMany', 'subOne']`，一对一子表 `validateForm(2)` 对应 index=2，校验失败自动切换到该 Tab |
| **refKeys[0] 是主表 key** | `v-show="activeKey == refKeys[0]"` 控制主表显隐，`reset()` 中 `activeKey.value = refKeys[0]` 的值 |
| **JVxeTable ref 名与 refKeys/activeKey 一致** | `ref="aiControlSub"` 必须与 `refKeys` 中的 key 和 `v-show="activeKey == 'aiControlSub'"` 完全一致 |
| **JVxeTypes 不等于 FormSchema component** | 子表列定义必须用 `JVxeTypes.select` 而非 `'JDictSelectTag'`。没有 `JVxeTypes.selectDict` 这个类型！ |
| **select 必须声明 options:[]** | `JVxeTypes.select/selectMultiple` 必须显式设置 `options:[]`，配合 `dictCode` 自动加载 |
| **开关用 checkbox 不是 switch** | JVxeTable 中开关使用 `JVxeTypes.checkbox` + `customValue:['Y','N']`，没有 JSwitch 类型 |
| **文件/图片需要 token** | `JVxeTypes.file/image` 必须设置 `token:true, responseName:'message'` |
| **popup 用 popupCode** | JVxeTable 的 Popup 使用 `popupCode`（不是 `code`），多选通过 `props: { multi: true }` |
| **width 是字符串** | JVxeColumn 的 width 格式为 `'200px'`（字符串），不是数字 |
| **校验用 validateRules** | 使用 `validateRules` 数组（不是 `dynamicRules` 函数），pattern 支持正则字符串和特殊值（`'only'` = 唯一） |
| **子表 API 导出为 URL 字符串** | `export const xxxList = Api.xxxList`（导出字符串），不是 `export const xxxList = (params) => defHttp.get(...)` |
| **一对一 FormSchema 需要隐藏 id 字段** | `{ label: '', field: 'id', component: 'Input', show: false }` 必须加在 FormSchema 首位 |
| **多子表 Service 参数** | 有多个子表时 `saveMain/updateMain` 参数对应增加，ServiceImpl 中需分别处理每个子表的删除和插入 |

### C11. ERP 风格一对多（子表独立CRUD）

ERP 风格与 Tab-in-Modal 风格的核心区别：主表和子表**各自独立保存**，不再整体提交。

#### 架构对比

| 维度 | Tab-in-Modal 风格 | ERP 风格 |
|------|-------------------|---------|
| 主表列表选择 | 多选 `rowSelection` | **单选 `rowSelection: { type: 'radio' }` ** |
| 子表位置 | Modal 内 Tab 页签 | **主表列表下方 Tab 页签** |
| 子表数据传递 | useJvxeMethod + requestSubTableData | **provide/inject + watch** |
| 子表保存方式 | 随主表一起提交（saveMain/updateMain） | **子表独立 CRUD（各自 add/edit/delete）** |
| 主表 Modal | 包含主表 + 子表 Tab | **仅主表字段** |
| 后端主表接口 | `/add` (saveMain) `/edit` (updateMain) | **`/addMain` (save) `/editMain` (updateById)** |

#### 关键陷阱：主表编辑不能用 updateMain

**问题：** ERP 模式下主表 Modal 只提交主表字段，如果仍调用 `updateMain()`，该方法会先删除所有子表记录再重新插入空列表，导致**子表数据全部丢失**。

**解决：** 后端必须新增仅操作主表的接口：
```java
// ERP模式：仅操作主表，不影响子表
@PostMapping(value = "/addMain")
public Result<String> addMain(@RequestBody {{entityName}} {{entityName_uncap}}) {
    {{entityName_uncap}}Service.save({{entityName_uncap}});
    return Result.OK("添加成功！");
}

@RequestMapping(value = "/editMain", method = {RequestMethod.PUT, RequestMethod.POST})
public Result<String> editMain(@RequestBody {{entityName}} {{entityName_uncap}}) {
    {{entityName_uncap}}Service.updateById({{entityName_uncap}});
    return Result.OK("编辑成功!");
}
```
前端 api.ts 中主表的 save/edit 指向 `/addMain` 和 `/editMain`。

#### 子表独立 CRUD 接口（后端）

每个子表需要 5 个接口：list（分页）、add、edit、delete、deleteBatch：
```java
// 子表分页列表（支持 BasicTable 分页参数）
@GetMapping(value = "/list{{subEntityName}}ByMainId")
public Result<IPage<{{subEntityName}}>> list{{subEntityName}}ByMainId(
        {{subEntityName}} {{subEntityName_uncap}},
        @RequestParam(name = "pageNo", defaultValue = "1") Integer pageNo,
        @RequestParam(name = "pageSize", defaultValue = "10") Integer pageSize,
        HttpServletRequest req) {
    QueryWrapper<{{subEntityName}}> queryWrapper = QueryGenerator.initQueryWrapper({{subEntityName_uncap}}, req.getParameterMap());
    Page<{{subEntityName}}> page = new Page<>(pageNo, pageSize);
    IPage<{{subEntityName}}> pageList = {{subEntityName_uncap}}Service.page(page, queryWrapper);
    return Result.OK(pageList);
}

@PostMapping(value = "/add{{subEntityName_suffix}}")
public Result<String> add{{subEntityName_suffix}}(@RequestBody {{subEntityName}} entity) {
    {{subEntityName_uncap}}Service.save(entity);
    return Result.OK("添加成功！");
}

@RequestMapping(value = "/edit{{subEntityName_suffix}}", method = {RequestMethod.PUT, RequestMethod.POST})
public Result<String> edit{{subEntityName_suffix}}(@RequestBody {{subEntityName}} entity) {
    {{subEntityName_uncap}}Service.updateById(entity);
    return Result.OK("编辑成功!");
}

@DeleteMapping(value = "/delete{{subEntityName_suffix}}")
public Result<String> delete{{subEntityName_suffix}}(@RequestParam(name = "id") String id) {
    {{subEntityName_uncap}}Service.removeById(id);
    return Result.OK("删除成功!");
}

@DeleteMapping(value = "/deleteBatch{{subEntityName_suffix}}")
public Result<String> deleteBatch{{subEntityName_suffix}}(@RequestParam(name = "ids") String ids) {
    {{subEntityName_uncap}}Service.removeByIds(Arrays.asList(ids.split(",")));
    return Result.OK("批量删除成功!");
}
```

#### 前端文件结构

```
views/{{viewDir}}/
├── {{entityName}}List.vue                   # ERP主页面（主表 + 下方Tab子表）
├── {{subEntityName}}List.vue                # 子表列表组件（每个子表一个）
├── {{entityName}}.api.ts                    # 全部API（主表+各子表CRUD）
├── {{entityName}}.data.ts                   # 全部列/表单配置
└── components/
    ├── {{entityName}}Modal.vue              # 主表Modal（仅主表字段）
    └── {{subEntityName}}Modal.vue           # 子表Modal（每个子表一个）
```

#### 前端核心模式 — 主表 provide + 子表 inject

**主表 List.vue：**
```typescript
import { computed, unref, provide } from 'vue';

// 单选模式
rowSelection: { type: 'radio' },

// 计算选中的主表ID，下发给子表
const {{mainEntityName_uncap}}Id = computed(() =>
  unref(selectedRowKeys).length > 0 ? unref(selectedRowKeys)[0] : ''
);
provide('{{mainEntityName_uncap}}Id', {{mainEntityName_uncap}}Id);

// handleSuccess 只 reload，不清空选中（否则子表会触发 watch 变空）
function handleSuccess() {
  reload();
}
```

**子表 List.vue：**
```typescript
import type { ComputedRef } from 'vue';
import { ref, computed, unref, watch, inject, reactive } from 'vue';
import { isEmpty } from '/@/utils/is';
import { useMessage } from '/@/hooks/web/useMessage';

// 注入主表ID
const {{mainEntityName_uncap}}Id = inject<ComputedRef<string>>(
  '{{mainEntityName_uncap}}Id',
  computed(() => '')
);
const $message = useMessage();
// ⚠️ 必须用 reactive，否则 BasicTable 的 :searchInfo 绑定可能不触发重新请求
const searchInfo = reactive<Record<string, any>>({});

// 监听主表ID变化，重新加载子表
watch({{mainEntityName_uncap}}Id, () => {
  searchInfo.{{mainEntityName_uncap}}Id = unref({{mainEntityName_uncap}}Id);
  reload();
  setSelectedRowKeys([]);
});

// 包装API：主表未选中时返回空数组
async function getSubList(params) {
  let { {{mainEntityName_uncap}}Id } = params;
  if ({{mainEntityName_uncap}}Id == null || isEmpty({{mainEntityName_uncap}}Id)) {
    return [];
  }
  return await subListApi(params);
}

// 新增前检查是否选中主表
function handleCreate() {
  if (isEmpty(unref({{mainEntityName_uncap}}Id))) {
    $message.createMessage.warning('请选择一条主表记录');
    return;
  }
  openModal(true, { isUpdate: false, showFooter: true });
}
```

**子表 Modal.vue：**
```typescript
import { inject } from 'vue';

// 注入主表ID
const {{mainEntityName_uncap}}Id = inject('{{mainEntityName_uncap}}Id') || '';

// 提交时自动关联主表ID
async function handleSubmit() {
  const values = await validate();
  if (unref({{mainEntityName_uncap}}Id)) {
    values.{{mainEntityName_uncap}}Id = unref({{mainEntityName_uncap}}Id);
  }
  await saveOrUpdateSub(values, isUpdate.value);
  closeModal();
  emit('success');
}
```

#### data.ts 差异

ERP 模式下子表使用 `BasicColumn[]`（普通列表列）+ `FormSchema[]`（Modal 表单），**不使用 JVxeColumn[]**：
```typescript
// ERP 模式：子表用 BasicColumn 列表展示
export const {{subEntityName_uncap}}Columns: BasicColumn[] = [
  { title: '字段名', align: 'center', dataIndex: 'fieldName' },
  { title: '字典字段', align: 'center', dataIndex: 'dictField_dictText' },
];

// ERP 模式：子表用 FormSchema 弹窗编辑（需包含隐藏的 id 和外键字段）
export const {{subEntityName_uncap}}FormSchema: FormSchema[] = [
  { label: '', field: 'id', component: 'Input', show: false },
  { label: '', field: '{{mainEntityName_uncap}}Id', component: 'Input', show: false },
  // ... 业务字段
];
```

#### 一对一子表特殊处理

一对一关系的子表需要限制只能有一条记录：

```typescript
// 子表 List.vue — 一对一限制
const hasDetailRecord = ref(false);

// useListPage tableProps 中添加 afterFetch
afterFetch: (data) => {
  // 一对一：检查是否已有记录
  hasDetailRecord.value = data && data.length > 0;
  return data;
},

// 新增按钮添加 :disabled="hasDetailRecord"
// <a-button type="primary" @click="handleCreate" :disabled="hasDetailRecord">新增</a-button>

// handleCreate 增加双重检查
function handleCreate() {
  if (isEmpty(unref({{mainEntityName_uncap}}Id))) {
    $message.createMessage.warning('请选择一条主表记录');
    return;
  }
  if (hasDetailRecord.value) {
    $message.createMessage.warning('一对一子表只能有一条记录，请编辑现有记录');
    return;
  }
  openModal(true, { isUpdate: false, showFooter: true });
}

// 包装API中也要重置标记
async function getSubList(params) {
  let { {{mainEntityName_uncap}}Id } = params;
  if ({{mainEntityName_uncap}}Id == null || isEmpty({{mainEntityName_uncap}}Id)) {
    hasDetailRecord.value = false;
    return [];
  }
  return await subListApi(params);
}
```

---

### C12. 内嵌子表风格（expandedRowRender + Tab-in-Modal）

内嵌子表风格是 Tab-in-Modal 的增强版：**Modal 内编辑子表数据**（与 C9 相同），同时在**列表页通过行展开（expandedRowRender）直接查看子表数据**，无需打开 Modal。

#### 架构对比

| 维度 | Tab-in-Modal 风格（C9） | 内嵌子表风格（C12） | ERP 风格（C11） |
|------|------------------------|-------------------|----------------|
| 列表页子表展示 | 无（需点编辑/详情才能看） | **行展开 expandedRowRender** | 主表下方 Tab 页签 |
| Modal 布局 | **radio-group 标题栏切换**（主表/子表同级） | **上面主表 + 下面子表 a-tabs**（原始布局） | 仅主表字段 |
| 保存方式 | 整体提交（saveMain） | 整体提交（同C9） | 子表独立保存 |
| 子表数据传递 | useJvxeMethod | useJvxeMethod + SubTable组件 | provide/inject |

#### 前端文件结构

```
views/{{viewDir}}/
├── {{entityName}}List.vue                   # 主列表（含 expandedRowRender）
├── {{entityName}}.api.ts                    # API（主表CRUD + 子表双重导出）
├── {{entityName}}.data.ts                   # 列/表单配置（子表三种导出）
├── components/
│   └── {{entityName}}Modal.vue              # Modal（主表 + 子表 Tab 编辑，同C9）
└── subTables/
    ├── {{subEntityName}}SubTable.vue        # 子表展示组件（每个子表一个）
    └── {{detailEntityName}}SubTable.vue     # 一对一子表展示组件
```

#### data.ts — 子表三种数据导出

每个子表需要导出**两种或三种**列定义，分别用于不同场景：

```typescript
import { JVxeTypes, JVxeColumn } from '/@/components/jeecg/JVxeTable/types';

// ===== 一对多子表 =====

// 1. BasicColumn[] — 供 SubTable 组件展示（行展开时的只读列表）
export const {{subEntityName_uncap}}Columns: BasicColumn[] = [
  { title: '字段标题', align: 'center', dataIndex: 'fieldName' },
  { title: '字典字段', align: 'center', dataIndex: 'dictField_dictText' },
];

// 2. JVxeColumn[] — 供 Modal 内 JVxeTable 编辑（可编辑表格）
export const {{subEntityName_uncap}}JVxeColumns: JVxeColumn[] = [
  { title: '字段标题', key: 'fieldName', type: JVxeTypes.input, width: '200px',
    placeholder: '请输入${title}', defaultValue: '' },
  { title: '字典字段', key: 'dictField', type: JVxeTypes.select, width: '200px',
    dictCode: 'dict_code', placeholder: '请选择${title}' },
];

// ===== 一对一子表 =====

// 1. BasicColumn[] — 供 SubTable 组件展示
export const {{detailEntityName_uncap}}Columns: BasicColumn[] = [
  { title: '字段标题', align: 'center', dataIndex: 'fieldName' },
];

// 2. FormSchema[] — 供 Modal 内 BasicForm 编辑（一对一不用 JVxeTable）
export const {{detailEntityName_uncap}}FormSchema: FormSchema[] = [
  { label: '字段标题', field: 'fieldName', component: 'Input' },
];
// 注意：一对一的 FormSchema 不需要隐藏的 id 和外键字段（与 ERP 模式不同）
```

#### api.ts — 子表双重导出

```typescript
enum Api {
  // 主表 CRUD
  list = '/{{entityPackagePath}}/{{entityName_uncap}}/list',
  save = '/{{entityPackagePath}}/{{entityName_uncap}}/add',
  edit = '/{{entityPackagePath}}/{{entityName_uncap}}/edit',
  deleteOne = '/{{entityPackagePath}}/{{entityName_uncap}}/delete',
  deleteBatch = '/{{entityPackagePath}}/{{entityName_uncap}}/deleteBatch',
  importExcel = '/{{entityPackagePath}}/{{entityName_uncap}}/importExcel',
  exportXls = '/{{entityPackagePath}}/{{entityName_uncap}}/exportXls',
  // 子表查询（非分页接口，返回 Result<List>）
  {{subEntityName_uncap}}List = '/{{entityPackagePath}}/{{entityName_uncap}}/query{{subEntityName}}ByMainId',
  {{detailEntityName_uncap}}List = '/{{entityPackagePath}}/{{entityName_uncap}}/query{{detailEntityName}}ByMainId',
}

// === 导出方式1：URL 字符串（供 Modal 中 requestSubTableData / defHttp.get 使用） ===
export const query{{subEntityName}}ByMainId = Api.{{subEntityName_uncap}}List;
export const query{{detailEntityName}}ByMainId = Api.{{detailEntityName_uncap}}List;

// === 导出方式2：函数（供 SubTable 组件直接调用，isTransformResponse:false 返回完整响应） ===
export const {{subEntityName_uncap}}ListApi = (params) =>
  defHttp.get({ url: Api.{{subEntityName_uncap}}List, params }, { isTransformResponse: false });
export const {{detailEntityName_uncap}}ListApi = (params) =>
  defHttp.get({ url: Api.{{detailEntityName_uncap}}List, params }, { isTransformResponse: false });
```

**为什么需要双重导出？**
- **URL 字符串**：Modal 中 `requestSubTableData(urlString, params, table)` 和 `defHttp.get({ url: urlString })` 需要纯 URL
- **函数导出**：SubTable 组件需要完整的 `{ success, result, message }` 响应对象来判断请求是否成功，所以设 `isTransformResponse: false`

#### SubTable 组件模板（subTables/{{subEntityName}}SubTable.vue）

```html
<template>
  <div>
    <BasicTable bordered size="middle" :loading="loading" rowKey="id" :canResize="true"
      :columns="{{subEntityName_uncap}}Columns" :dataSource="dataSource" :pagination="false">
      <!--字段回显插槽-->
      <template v-slot:bodyCell="{ column, record, index, text }">
        <!-- 文件字段 -->
        <template v-if="column.dataIndex==='fileField'">
          <span v-if="!text" style="font-size: 12px;font-style: italic;">无文件</span>
          <a-button v-else :ghost="true" type="primary" preIcon="ant-design:download-outlined"
            size="small" @click="downloadFile(text)">下载</a-button>
        </template>
        <!-- 富文本字段 -->
        <template v-if="column.dataIndex==='richTextField'">
          <div v-html="text"></div>
        </template>
      </template>
    </BasicTable>
  </div>
</template>

<script lang="ts" setup>
  import { ref, watchEffect } from 'vue';
  import { BasicTable } from '/@/components/Table';
  import { {{subEntityName_uncap}}Columns } from '../{{entityName}}.data';
  import { {{subEntityName_uncap}}ListApi } from '../{{entityName}}.api';
  // import { downloadFile } from '/@/utils/common/renderUtils'; // 有文件字段时需要

  const props = defineProps({
    id: {
      type: String,
      default: '',
    },
  });

  const loading = ref(false);
  const dataSource = ref([]);

  watchEffect(() => {
    props.id && loadData(props.id);
  });

  function loadData(id) {
    dataSource.value = [];
    loading.value = true;
    {{subEntityName_uncap}}ListApi({ id })
      .then((res) => {
        if (res.success) {
          dataSource.value = res.result;
        }
      })
      .finally(() => {
        loading.value = false;
      });
  }
</script>
```

**SubTable 关键点：**
- `watchEffect` 监听 `props.id` 变化自动重新加载
- API 使用函数导出（`xxxListApi`），返回完整响应 `{ success, result }`
- `dataSource.value = res.result` — 非分页接口直接返回数组
- `:pagination="false"` — 子表不分页

#### List.vue — expandedRowRender 模板

```html
<template>
  <div>
    <BasicTable @register="registerTable" :rowSelection="rowSelection"
      :expandedRowKeys="expandedRowKeys" @expand="handleExpand">
      <!-- 内嵌table区域 begin -->
      <template #expandedRowRender="{ record }">
        <a-tabs tabPosition="top">
          <a-tab-pane tab="{{detailDescription}}" key="{{detailEntityName_uncap}}" forceRender>
            <{{detailEntityName}}SubTable v-if="expandedRowKeys.includes(record.id)" :id="record.id" />
          </a-tab-pane>
          <a-tab-pane tab="{{subDescription}}" key="{{subEntityName_uncap}}" forceRender>
            <{{subEntityName}}SubTable v-if="expandedRowKeys.includes(record.id)" :id="record.id" />
          </a-tab-pane>
        </a-tabs>
      </template>
      <!-- 内嵌table区域 end -->
      <!--插槽:table标题-->
      <template #tableTitle>
        <a-button type="primary" preIcon="ant-design:plus-outlined" @click="handleAdd">新增</a-button>
        <a-button type="primary" preIcon="ant-design:export-outlined" @click="onExportXls">导出</a-button>
        <j-upload-button type="primary" preIcon="ant-design:import-outlined" @click="onImportXls">导入</j-upload-button>
        <a-dropdown v-if="selectedRowKeys.length > 0">
          <template #overlay>
            <a-menu>
              <a-menu-item key="1" @click="batchHandleDelete">
                <Icon icon="ant-design:delete-outlined" />
                删除
              </a-menu-item>
            </a-menu>
          </template>
          <a-button>批量操作<Icon icon="mdi:chevron-down" /></a-button>
        </a-dropdown>
      </template>
      <!--操作栏-->
      <template #action="{ record }">
        <TableAction :actions="getTableAction(record)" :dropDownActions="getDropDownAction(record)" />
      </template>
      <!--字段回显插槽-->
      <template v-slot:bodyCell="{ column, record, index, text }">
      </template>
    </BasicTable>
    <!-- 表单区域 -->
    <{{entityName}}Modal @register="registerModal" @success="handleSuccess" />
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { BasicTable, TableAction } from '/@/components/Table';
  import { useModal } from '/@/components/Modal';
  import { useListPage } from '/@/hooks/system/useListPage';
  import {{entityName}}Modal from './components/{{entityName}}Modal.vue';
  import {{detailEntityName}}SubTable from './subTables/{{detailEntityName}}SubTable.vue';
  import {{subEntityName}}SubTable from './subTables/{{subEntityName}}SubTable.vue';
  import { columns, searchFormSchema } from './{{entityName}}.data';
  import { list, deleteOne, batchDelete, getImportUrl, getExportUrl } from './{{entityName}}.api';

  const [registerModal, { openModal }] = useModal();
  // 展开key — 控制哪些行展开
  const expandedRowKeys = ref<any[]>([]);

  const { prefixCls, tableContext, onExportXls, onImportXls } = useListPage({
    tableProps: {
      title: '{{description}}',
      api: list,
      columns,
      canResize: false,
      formConfig: {
        schemas: searchFormSchema,
        autoSubmitOnEnter: true,
      },
      actionColumn: {
        width: 120,
        fixed: 'right',
      },
    },
    exportConfig: { name: '{{description}}', url: getExportUrl },
    importConfig: { url: getImportUrl, success: handleSuccess },
  });

  const [registerTable, { reload, collapseAll, updateTableDataRecord, deleteTableDataRecord },
    { rowSelection, selectedRowKeys, selectedRows }] = tableContext;

  /**
   * 展开事件 — 同时只展开一行
   */
  function handleExpand(expanded, record) {
    expandedRowKeys.value = [];
    if (expanded === true) {
      expandedRowKeys.value.push(record.id);
    }
  }

  function handleAdd() {
    openModal(true, { isUpdate: false, showFooter: true });
  }

  function handleEdit(record: Recordable) {
    openModal(true, { record, isUpdate: true, showFooter: true });
  }

  function handleDetail(record: Recordable) {
    openModal(true, { record, isUpdate: true, showFooter: false });
  }

  async function handleDelete(record) {
    await deleteOne({ id: record.id }, handleSuccess);
  }

  async function batchHandleDelete() {
    await batchDelete({ ids: selectedRowKeys.value }, handleSuccess);
  }

  function handleSuccess() {
    (selectedRowKeys.value = []) && reload();
  }

  function getTableAction(record) {
    return [{ label: '编辑', onClick: handleEdit.bind(null, record) }];
  }

  function getDropDownAction(record) {
    return [
      { label: '详情', onClick: handleDetail.bind(null, record) },
      { label: '删除', popConfirm: { title: '是否确认删除', confirm: handleDelete.bind(null, record), placement: 'topLeft' } },
    ];
  }
</script>
```

**List.vue 关键点：**
- `expandedRowKeys` + `handleExpand`：同时只展开一行，避免多行展开时数据混乱
- `v-if="expandedRowKeys.includes(record.id)"`：仅在展开时渲染 SubTable，避免不必要的 API 请求
- `handleSuccess` 使用 `(selectedRowKeys.value = []) && reload()` 模式（标准风格，非 ERP 的 `reload()` 不清空选中）
- 不使用 `provide/inject`，子表数据通过 SubTable 的 `id` prop 传递

#### Modal.vue — 原始布局（上面主表，下面子表 Tabs）

**内嵌子表风格和 ERP 风格的 Modal 不使用 radio-group 标题栏切换**，而是采用原始布局：
- 上方：主表 BasicForm（全宽展示）
- 下方：子表区域，多个子表用 `a-tabs` 组织（注意是 **内容区的 a-tabs**，不是标题栏的 radio-group）
- 不需要 `wrapClassName="j-cgform-tab-modal"`
- 不需要 `v-show` 切换（主表始终可见）

**只有 Tab-in-Modal 风格（C9）才使用 radio-group 标题栏切换！**

##### 纯一对多 Modal

```html
<template>
  <BasicModal v-bind="$attrs" @register="registerModal" destroyOnClose :title="title" :width="896" @ok="handleSubmit">
    <!-- 主表表单 -->
    <BasicForm @register="registerForm" ref="formRef" name="{{entityName}}Form"/>
    <!-- 子表区域 -->
    <a-tabs v-model:activeKey="activeKey">
      <a-tab-pane tab="{{subDescription}}" key="{{subEntityName_uncap}}" forceRender>
        <JVxeTable
          keep-source resizable
          ref="{{subEntityName_uncap}}"
          :loading="{{subEntityName_uncap}}Table.loading"
          :columns="{{subEntityName_uncap}}Table.columns"
          :dataSource="{{subEntityName_uncap}}Table.dataSource"
          :height="340"
          :disabled="formDisabled"
          :rowNumber="true" :rowSelection="true" :toolbar="true"
        />
      </a-tab-pane>
    </a-tabs>
  </BasicModal>
</template>

<script lang="ts" setup>
    import {ref, computed, unref, reactive} from 'vue';
    import {BasicModal, useModalInner} from '/@/components/Modal';
    import {BasicForm, useForm} from '/@/components/Form/index';
    import { useJvxeMethod } from '/@/hooks/system/useJvxeMethods.ts'
    import {formSchema, {{subEntityName_uncap}}JVxeColumns} from '../{{entityName}}.data';
    import {saveOrUpdate, query{{subEntityName}}ByMainId} from '../{{entityName}}.api';

    const emit = defineEmits(['register','success']);
    const isUpdate = ref(true);
    const formDisabled = ref(false);
    const refKeys = ref(['{{subEntityName_uncap}}']);
    const activeKey = ref('{{subEntityName_uncap}}');
    const {{subEntityName_uncap}} = ref();
    const tableRefs = { {{subEntityName_uncap}} };
    const {{subEntityName_uncap}}Table = reactive({
          loading: false,
          dataSource: [],
          columns: {{subEntityName_uncap}}JVxeColumns
    })
    const [registerForm, {setProps, resetFields, setFieldsValue, validate}] = useForm({
        schemas: formSchema,
        showActionButtonGroup: false,
        baseColProps: {span: 12}
    });
    const [registerModal, {setModalProps, closeModal}] = useModalInner(async (data) => {
        await reset();
        setModalProps({confirmLoading: false, showCancelBtn: data?.showFooter, showOkBtn: data?.showFooter});
        isUpdate.value = !!data?.isUpdate;
        formDisabled.value = !data?.showFooter;
        if (unref(isUpdate)) {
            await setFieldsValue({ ...data.record });
            requestSubTableData(query{{subEntityName}}ByMainId, {id: data?.record?.id}, {{subEntityName_uncap}}Table)
        }
        setProps({ disabled: !data?.showFooter })
    });
    const [handleChangeTabs, handleSubmit, requestSubTableData, formRef] = useJvxeMethod(requestAddOrEdit, classifyIntoFormData, tableRefs, activeKey, refKeys);

    const title = computed(() => (!unref(isUpdate) ? '新增' : !unref(formDisabled) ? '编辑' : '详情'));
    async function reset(){
      await resetFields();
      activeKey.value = '{{subEntityName_uncap}}';
      {{subEntityName_uncap}}Table.dataSource = [];
    }
    function classifyIntoFormData(allValues) {
         let main = Object.assign({}, allValues.formValue)
         return {
           ...main,
           {{subEntityName_uncap}}List: allValues.tablesValue[0].tableData,
         }
    }
    async function requestAddOrEdit(values) {
        try {
            setModalProps({confirmLoading: true});
            await saveOrUpdate(values, isUpdate.value);
            closeModal();
            emit('success');
        } finally {
            setModalProps({confirmLoading: false});
        }
    }
</script>

<style lang="less" scoped>
  :deep(.ant-input-number) { width: 100%; }
  :deep(.ant-calendar-picker) { width: 100%; }
</style>
```

##### 一对一 + 一对多混合 Modal

```html
<template>
  <BasicModal v-bind="$attrs" @register="registerModal" destroyOnClose :title="title" :width="896" @ok="handleSubmit">
    <!-- 主表表单 -->
    <BasicForm @register="registerForm" ref="formRef" name="{{entityName}}Form"/>
    <!-- 子表区域 -->
    <a-tabs v-model:activeKey="activeKey">
      <a-tab-pane tab="{{subDescription}}" key="{{subEntityName_uncap}}" forceRender>
        <JVxeTable
          keep-source resizable
          ref="{{subEntityName_uncap}}"
          :loading="{{subEntityName_uncap}}Table.loading"
          :columns="{{subEntityName_uncap}}Table.columns"
          :dataSource="{{subEntityName_uncap}}Table.dataSource"
          :height="340"
          :disabled="formDisabled"
          :rowNumber="true" :rowSelection="true" :toolbar="true"
        />
      </a-tab-pane>
      <a-tab-pane tab="{{detailDescription}}" key="{{detailEntityName_uncap}}" forceRender>
        <{{detailEntityName}}Form ref="{{detailEntityName_uncap}}Form" :disabled="formDisabled" />
      </a-tab-pane>
    </a-tabs>
  </BasicModal>
</template>

<script lang="ts" setup>
    import {ref, computed, unref, reactive} from 'vue';
    import {BasicModal, useModalInner} from '/@/components/Modal';
    import {BasicForm, useForm} from '/@/components/Form/index';
    import { useJvxeMethod } from '/@/hooks/system/useJvxeMethods.ts'
    import {{detailEntityName}}Form from './{{detailEntityName}}Form.vue'
    import {formSchema, {{subEntityName_uncap}}JVxeColumns} from '../{{entityName}}.data';
    import {saveOrUpdate, query{{subEntityName}}ByMainId, query{{detailEntityName}}ByMainId} from '../{{entityName}}.api';
    import { VALIDATE_FAILED } from '/@/utils/common/vxeUtils'

    const emit = defineEmits(['register','success']);
    const isUpdate = ref(true);
    const formDisabled = ref(false);
    const refKeys = ref(['{{subEntityName_uncap}}', '{{detailEntityName_uncap}}']);
    const activeKey = ref('{{subEntityName_uncap}}');
    const {{subEntityName_uncap}} = ref();
    const {{detailEntityName_uncap}}Form = ref();
    const tableRefs = { {{subEntityName_uncap}} };
    const {{subEntityName_uncap}}Table = reactive({
          loading: false,
          dataSource: [],
          columns: {{subEntityName_uncap}}JVxeColumns
    })
    const [registerForm, {setProps, resetFields, setFieldsValue, validate}] = useForm({
        schemas: formSchema,
        showActionButtonGroup: false,
        baseColProps: {span: 12}
    });
    const [registerModal, {setModalProps, closeModal}] = useModalInner(async (data) => {
        await reset();
        setModalProps({confirmLoading: false, showCancelBtn: data?.showFooter, showOkBtn: data?.showFooter});
        isUpdate.value = !!data?.isUpdate;
        formDisabled.value = !data?.showFooter;
        if (unref(isUpdate)) {
            await setFieldsValue({ ...data.record });
            {{detailEntityName_uncap}}Form.value.initFormData(query{{detailEntityName}}ByMainId, data?.record?.id)
            requestSubTableData(query{{subEntityName}}ByMainId, {id: data?.record?.id}, {{subEntityName_uncap}}Table)
        }
        setProps({ disabled: !data?.showFooter })
    });
    // 第6个参数 validateSubForm 用于校验一对一子表
    const [handleChangeTabs, handleSubmit, requestSubTableData, formRef] = useJvxeMethod(requestAddOrEdit, classifyIntoFormData, tableRefs, activeKey, refKeys, validateSubForm);

    const title = computed(() => (!unref(isUpdate) ? '新增' : !unref(formDisabled) ? '编辑' : '详情'));
    async function reset(){
      await resetFields();
      activeKey.value = '{{subEntityName_uncap}}';
      {{subEntityName_uncap}}Table.dataSource = [];
      {{detailEntityName_uncap}}Form.value.resetFields();
    }
    function classifyIntoFormData(allValues) {
         let main = Object.assign({}, allValues.formValue)
         return {
           ...main,
           {{subEntityName_uncap}}List: allValues.tablesValue[0].tableData,
           {{detailEntityName_uncap}}List: {{detailEntityName_uncap}}Form.value.getFormData(),
         }
    }
    function validateSubForm(allValues){
        return new Promise((resolve,reject)=>{
            Promise.all([
                 {{detailEntityName_uncap}}Form.value.validateForm(1),
            ]).then(() => {
                resolve(allValues)
            }).catch(e => {
                if (e.error === VALIDATE_FAILED) {
                    activeKey.value = e.index == null ? unref(activeKey) : refKeys.value[e.index]
                } else {
                    console.error(e)
                }
            })
        })
    }
    async function requestAddOrEdit(values) {
        try {
            setModalProps({confirmLoading: true});
            await saveOrUpdate(values, isUpdate.value);
            closeModal();
            emit('success');
        } finally {
            setModalProps({confirmLoading: false});
        }
    }
</script>

<style lang="less" scoped>
  :deep(.ant-input-number) { width: 100%; }
  :deep(.ant-calendar-picker) { width: 100%; }
</style>
```

**原始布局 Modal 与 Tab-in-Modal (C9) 的关键区别：**
- **无 `wrapClassName="j-cgform-tab-modal"`**，无 `.titleArea`/`.contentArea` 样式
- **无 `#title` 插槽**，标题用普通 `:title="title"` 属性
- **无 radio-group**，主表 BasicForm 始终显示在上方
- 子表区域使用 **`a-tabs`**（内容区的标签页），而非标题栏的 radio-group
- `refKeys` **不包含主表 key**（只有子表 key），因为主表不参与 Tab 切换
- `validateSubForm` 中 `validateForm(1)` 的 index 对应 `refKeys` 中一对一子表的位置（从0开始，0=一对多，1=一对一）

#### 内嵌子表与其他风格的生成差异速查

| 生成项 | 内嵌子表（C12） | Tab-in-Modal（C9） | ERP（C11） |
|--------|---------------|-------------------|-----------|
| SubTable 组件 | **需要生成** | 不需要 | 不需要 |
| subTables/ 目录 | **需要创建** | 不需要 | 不需要 |
| api.ts 子表导出 | **URL字符串 + 函数双重导出** | 仅 URL 字符串 | 仅函数导出 |
| data.ts 子表列 | **BasicColumn[] + JVxeColumn[]** | 仅 JVxeColumn[] | 仅 BasicColumn[] + FormSchema[] |
| List.vue expandedRowRender | **需要** | 不需要 | 不需要 |
| List.vue rowSelection | 多选（默认） | 多选（默认） | 单选 radio |
| Modal 布局 | **原始布局**（上面主表 + 下面子表 a-tabs） | **radio-group 标题栏**切换 | 仅主表字段 |
| Modal wrapClassName | 无 | `j-cgform-tab-modal` | 无 |
| Modal refKeys | **只有子表 key** | 包含主表 + 子表 key | 无 |
| 后端接口 | `/add`(saveMain) `/edit`(updateMain) | 同左 | `/addMain`(save) `/editMain`(updateById) |

---

### C13. vue3Native 原生风格一对多（默认布局）

vue3Native 一对多与 vue3 封装风格（C9/C12）的架构**完全不同**。核心区别：**Form 组件（不是 Modal）** 包含主表表单和子表 Tabs，Modal 只是一个薄包装器。

#### 架构对比

| 维度 | vue3 封装风格（C9 Tab-in-Modal） | vue3Native 原生风格 |
|------|-------------------------------|-------------------|
| **Modal 职责** | 包含 BasicForm + JVxeTable + SubForm，负责数据编排和提交 | **薄包装器**，只调 `formComponent.submitForm()/edit()/add()` |
| **Form 职责** | 仅主表字段（单表场景才有 Form.vue） | **核心组件**，包含主表 a-form + 子表 a-tabs + 数据提交逻辑 |
| **数据收集 hook** | `useJvxeMethod` | `useValidateAntFormAndTable` |
| **主表表单** | `BasicForm` + `useForm` from `/@/components/Form/index` | 原生 `a-form` + `Form.useForm` from `ant-design-vue` |
| **一对一子表** | `BasicForm` + `useForm`，`initFormData(url, id)` 传 URL 字符串 | 原生 `a-form` + `Form.useForm`，`initFormData(mainId)` 传主表 ID |
| **子表 API 导出** | URL 字符串（`export const xxxList = Api.xxxList`） | **函数导出**（`export const queryXxxByMainId = (id) => defHttp.get({...})`） |
| **saveOrUpdate** | 普通 `defHttp.post({url, params})` | 同左，**不需要** `isTransformResponse: false` |
| **data.ts** | 有 formSchema（主表）+ JVxeColumn[]（子表）+ FormSchema[]（一对一子表） | **无 formSchema**（主表在模板中写），只有 JVxeColumn[]（子表），**无 FormSchema[]**（一对一子表也在模板中写） |
| **List.vue** | `useModal` + `openModal(true, {...})` | 同左 |
| **refKeys** | 包含主表 key + 子表 key | **不需要 refKeys** |

#### 文件结构

```
views/{{viewDir}}/
├── {{entityName}}List.vue                   # 主列表（useModal + openModal）
├── {{entityName}}.api.ts                    # API（子表导出为函数，需要 queryDataById）
├── {{entityName}}.data.ts                   # 仅 columns + superQuerySchema + JVxeColumn[]（无 formSchema）
└── components/
    ├── {{entityName}}Modal.vue              # 薄包装器（BasicModal + useModalInner）
    ├── {{entityName}}Form.vue               # 核心组件（主表 a-form + 子表 a-tabs + useValidateAntFormAndTable）
    └── {{detailEntityName}}Form.vue         # 一对一子表原生 Form（仅有一对一子表时）
```

#### C13-1. api.ts 差异

```typescript
import { defHttp } from '/@/utils/http/axios';

enum Api {
  // ... 主表 CRUD 接口
  queryDataById = '/{{entityPackagePath}}/{{entityName_uncap}}/queryById',
  {{subEntityName_uncap}}List = '/{{entityPackagePath}}/{{entityName_uncap}}/query{{subEntityName}}ByMainId',
  {{detailEntityName_uncap}}List = '/{{entityPackagePath}}/{{entityName_uncap}}/query{{detailEntityName}}ByMainId',
}

// ✅ saveOrUpdate 不需要 isTransformResponse: false
export const saveOrUpdate = (params, isUpdate) => {
  let url = isUpdate ? Api.edit : Api.save;
  return defHttp.post({ url: url, params });
};

// ✅ 需要 queryDataById（Form.vue 编辑时重新查询主表数据）
export const queryDataById = (id) => defHttp.get({ url: Api.queryDataById, params: { id } });

// ✅ 子表导出为函数（不是 URL 字符串！）
export const query{{subEntityName}}ListByMainId = (id) => defHttp.get({ url: Api.{{subEntityName_uncap}}List, params: { id } });
export const query{{detailEntityName}}ListByMainId = (id) => defHttp.get({ url: Api.{{detailEntityName_uncap}}List, params: { id } });
```

**与 vue3 封装风格的关键差异：**
- `saveOrUpdate` **不用** `{ isTransformResponse: false }`
- 子表查询导出为**函数**（`(id) => defHttp.get({...})`），不是 URL 字符串
- 需要额外的 `queryDataById` 函数（Form 编辑时 `queryMainData(id)` 调用）

#### C13-2. data.ts 差异

vue3Native 的 data.ts **只包含 columns、superQuerySchema 和 JVxeColumn[]**，不包含 formSchema 和一对一子表的 FormSchema：

```typescript
import { BasicColumn } from '/@/components/Table';
import { JVxeTypes, JVxeColumn } from '/@/components/jeecg/JVxeTable/types';

// 主表列定义（与单表相同）
export const columns: BasicColumn[] = [ /* ... */ ];

// 高级查询（与单表相同）
export const superQuerySchema = { /* ... */ };

// 一对多子表列定义（JVxeColumn[] 与 vue3 封装风格相同）
export const {{subEntityName_uncap}}Columns: JVxeColumn[] = [ /* ... */ ];

// ❌ 不需要 formSchema（主表表单在 Form.vue 模板中直接写 a-form）
// ❌ 不需要 {{detailEntityName_uncap}}FormSchema（一对一子表在 DetailForm.vue 模板中写 a-form）
```

#### C13-3. Modal.vue — 薄包装器

```html
<template>
  <BasicModal v-bind="$attrs" @register="registerModal" :title="title" maxHeight="500px" :width="800" @ok="handleSubmit">
    <{{entityName_uncap}}-form ref="formComponent" :formDisabled="formDisabled" :formBpm="false" @success="submitSuccess"><\/{{entityName_uncap}}-form>
  </BasicModal>
</template>

<script lang="ts">
  import { ref, unref } from 'vue';
  import { BasicModal, useModalInner } from '/@/components/Modal';
  import {{entityName}}Form from './{{entityName}}Form.vue';

  export default {
    name: "{{entityName}}Modal",
    components:{ BasicModal, {{entityName}}Form },
    emits:['register','success'],
    setup(_p, {emit}){
      const formComponent = ref()
      const isUpdate = ref(true);
      const formDisabled = ref(false);
      const title = ref('')

      const [registerModal, {setModalProps, closeModal}] = useModalInner(async (data) => {
        setModalProps({confirmLoading: false, showCancelBtn: data?.showFooter, showOkBtn: data?.showFooter});
        isUpdate.value = !!data?.isUpdate;
        formDisabled.value = !data?.showFooter;
        title.value = data?.isUpdate ? (unref(formDisabled) ? '详情' : '编辑') : '新增';
        if (unref(isUpdate)) {
          formComponent.value.edit(data.record)
        } else {
          formComponent.value.add()
        }
      });

      function handleSubmit() {
        formComponent.value.submitForm();
      }

      function submitSuccess(){
        emit('success');
        closeModal();
      }
      return { registerModal, title, formComponent, formDisabled, handleSubmit, submitSuccess }
    }
  }
</script>
```

**关键点：**
- **不用** `<script setup>`，使用 Options API（`export default {...}`）
- Modal 只做三件事：(1) 新增时调 `formComponent.value.add()`，(2) 编辑时调 `formComponent.value.edit(data.record)`，(3) 提交时调 `formComponent.value.submitForm()`
- `submitSuccess` 由 Form 组件 `emit('success')` 触发，然后 Modal 关闭并通知 List 刷新

#### C13-4. Form.vue — 核心组件（主表 + 子表 + 提交逻辑）

```html
<template>
  <a-spin :spinning="loading">
    <JFormContainer :disabled="disabled">
      <template #detail>
        <a-form v-bind="formItemLayout" name="{{entityName}}Form" ref="formRef" class="jeecg-native-form">
          <a-row>
            <!-- 主表字段，与单表 Form.vue 相同 -->
            <a-col :span="24">
              <a-form-item label="字段名" v-bind="validateInfos.fieldName" id="{{entityName}}Form-fieldName" name="fieldName">
                <a-input v-model:value="formData.fieldName" placeholder="请输入" allow-clear />
              </a-form-item>
            </a-col>
            <!-- ... 其他主表字段 ... -->
          </a-row>
        </a-form>
      </template>
    </JFormContainer>

    <!-- ✅ 子表区域在 Form 中，不是在 Modal 中 -->
    <a-tabs v-model:activeKey="activeKey" animated style="overflow:hidden;" class="jeecg-native-tab">
      <!-- 一对多子表 Tab -->
      <a-tab-pane tab="{{subDescription}}" key="{{subEntityName_uncap}}" :forceRender="true">
        <j-vxe-table
          :keep-source="true" resizable
          ref="{{subEntityName_uncap}}TableRef"
          :loading="{{subEntityName_uncap}}Table.loading"
          :columns="{{subEntityName_uncap}}Table.columns"
          :dataSource="{{subEntityName_uncap}}Table.dataSource"
          :height="340" :disabled="disabled"
          :rowNumber="true" :rowSelection="true" :toolbar="true"/>
      </a-tab-pane>
      <!-- 一对一子表 Tab -->
      <a-tab-pane class="sub-one-form" tab="{{detailDescription}}" key="{{detailEntityName_uncap}}" :forceRender="true">
        <{{detailEntityName_uncap}}-form ref="{{detailEntityName_uncap}}FormRef" :disabled="disabled"><\/{{detailEntityName_uncap}}-form>
      </a-tab-pane>
    </a-tabs>
    <!-- 流程表单提交按钮（仅 BPM 模式可见） -->
    <div v-if="showFlowSubmitButton" :span="24" style="width: 100%;text-align: center;margin-top: 10px">
      <a-button preIcon="ant-design:check-outlined" style="width: 126px" type="primary" @click="submitForm">提 交</a-button>
    </div>
  </a-spin>
</template>

<script lang="ts">
  import { defineComponent, ref, reactive, computed, toRaw, onMounted } from 'vue';
  import { defHttp } from '/@/utils/http/axios';
  import { useValidateAntFormAndTable } from '/@/hooks/system/useJvxeMethods';
  import { query{{subEntityName}}ListByMainId, queryDataById, saveOrUpdate } from '../{{entityName}}.api';
  import {{detailEntityName}}Form from './{{detailEntityName}}Form.vue';
  import { {{subEntityName_uncap}}Columns } from '../{{entityName}}.data';
  // ... import 表单控件组件 ...
  import JFormContainer from '/@/components/Form/src/container/JFormContainer.vue';
  import { Form } from 'ant-design-vue';
  const useForm = Form.useForm;

  export default defineComponent({
    name: "{{entityName}}Form",
    components:{ JFormContainer, {{detailEntityName}}Form, /* ... 其他控件 ... */ },
    props:{
      formDisabled: { type: Boolean, default: false },
      formData: { type: Object, default: ()=>{} },
      formBpm: { type: Boolean, default: true },
      showSubmitButton: { type: Boolean, default: true },
    },
    emits:['success'],
    setup(props, {emit}) {
      const loading = ref(false);
      const formRef = ref();
      const {{detailEntityName_uncap}}FormRef = ref();
      const {{subEntityName_uncap}}TableRef = ref();
      const {{subEntityName_uncap}}Table = reactive<Record<string, any>>({
        loading: false,
        columns: {{subEntityName_uncap}}Columns,
        dataSource: []
      });
      const activeKey = ref('{{subEntityName_uncap}}');
      const formData = reactive<Record<string, any>>({
        id: '',
        // ... 主表字段
      });

      const validatorRules = reactive({ /* 校验规则 */ });
      const { resetFields, validate, validateInfos } = useForm(formData, validatorRules, { immediate: false });
      const dbData = {};
      const formItemLayout = {
        labelCol: { xs: { span: 24 }, sm: { span: 5 } },
        wrapperCol: { xs: { span: 24 }, sm: { span: 16 } },
      };

      const disabled = computed(() => {
        if (props.formBpm === true) {
          return props.formData.disabled !== false;
        }
        return props.formDisabled;
      });

      // ✅ 使用 useValidateAntFormAndTable（不是 useJvxeMethod）
      // key 与 a-tabs 的 activeKey 对应，value 是子组件的 ref
      const { getSubFormAndTableData, transformData } = useValidateAntFormAndTable(activeKey, {
        '{{detailEntityName_uncap}}': {{detailEntityName_uncap}}FormRef,  // 一对一子表（isForm = true）
        '{{subEntityName_uncap}}': {{subEntityName_uncap}}TableRef,       // 一对多子表（JVxeTable ref）
      });

      function add() {
        resetFields();
        {{detailEntityName_uncap}}FormRef.value.initFormData();  // 无参数 = 新增
        {{subEntityName_uncap}}Table.dataSource = [];
      }

      async function edit(row) {
        // 1. 主表数据
        await queryMainData(row.id);
        // 2. 一对一子表数据
        await {{detailEntityName_uncap}}FormRef.value.initFormData(row['id']);
        // 3. 一对多子表数据
        const subDataList = await query{{subEntityName}}ListByMainId(row['id']);
        {{subEntityName_uncap}}Table.dataSource = [...subDataList];
      }

      async function queryMainData(id) {
        const row = await queryDataById(id);
        resetFields();
        const tmpData = {};
        Object.keys(formData).forEach((key) => {
          if (row.hasOwnProperty(key)) {
            tmpData[key] = row[key];
          }
        });
        Object.assign(formData, tmpData);
      }

      async function getFormData() {
        try {
          await validate();
        } catch ({ errorFields }) {
          if (errorFields) {
            const firstField = errorFields[0];
            if (firstField) {
              formRef.value.scrollToField(firstField.name, { behavior: 'smooth', block: 'center' });
            }
          }
          return Promise.reject(errorFields);
        }
        return transformData(toRaw(formData));
      }

      // ✅ 提交逻辑在 Form 中，不在 Modal 中
      async function submitForm() {
        const mainData = await getFormData();
        const subData = await getSubFormAndTableData();
        const values = Object.assign({}, dbData, mainData, subData);
        const isUpdate = values.id ? true : false;
        await saveOrUpdate(values, isUpdate);
        emit('success');
      }

      function setFieldsValue(values) {
        if (values) {
          Object.keys(values).map(k => { formData[k] = values[k]; });
        }
      }

      // 流程表单 BPM 相关（与单表 Form 相同）
      onMounted(() => { /* initFormData for BPM */ });
      const showFlowSubmitButton = computed(() => {
        return props.formBpm === true && props.showSubmitButton === true && props.formData.disabled === false;
      });

      return {
        {{detailEntityName_uncap}}FormRef, {{subEntityName_uncap}}TableRef, {{subEntityName_uncap}}Table,
        validatorRules, validateInfos, activeKey, loading, formData,
        setFieldsValue, formItemLayout, disabled, showFlowSubmitButton,
        getFormData, submitForm, add, edit, formRef,
      }
    }
  });
</script>
<style lang="less" scoped>
  .ant-tabs-tabpane.sub-one-form { max-height: 340px; overflow: auto; }
  .jeecg-native-form, .jeecg-native-tab { padding: 0 20px; }
</style>
```

**Form.vue 关键点：**
1. **必须用 `defineComponent`**（Options API），不能用 `<script setup>`，因为需要 `return` 暴露方法给 Modal 通过 `ref` 调用
2. **`useValidateAntFormAndTable`** 是核心 hook，它根据子组件是否有 `isForm = true` 属性来区分一对一表单和 JVxeTable
3. **`getSubFormAndTableData()`** 自动收集所有子表数据：一对一子表调用 `getFormData()` 取数据，一对多子表从 JVxeTable 取 `tableData`
4. **`transformData(toRaw(formData))`** 处理主表数据中的数组字段（逗号拼接）
5. 编辑时通过 `queryDataById(id)` 重新查询主表数据，不直接用 record（确保字段完整）
6. 子表数据加载通过**函数调用**（不是 `defHttp.get({url: urlString, ...})`）

#### C13-5. 一对一子表 Form（原生 a-form 风格）

```html
<template>
  <a-spin :spinning="loading">
    <JFormContainer :disabled="disabled">
      <template #detail>
        <a-form v-bind="formItemLayout" name="{{detailEntityName}}Form" ref="formRef" class="antd-modal-form">
          <a-row>
            <!-- 一对一子表字段 -->
            <a-col :span="24">
              <a-form-item label="字段名" v-bind="validateInfos.fieldName" id="{{detailEntityName}}Form-fieldName" name="fieldName">
                <a-input v-model:value="formData.fieldName" placeholder="请输入" allow-clear />
              </a-form-item>
            </a-col>
            <!-- ... -->
          </a-row>
        </a-form>
      </template>
    </JFormContainer>
  </a-spin>
</template>

<script lang="ts">
  import { defineComponent, ref, reactive, toRaw } from 'vue';
  import { query{{detailEntityName}}ListByMainId } from '../{{entityName}}.api';
  import JFormContainer from '/@/components/Form/src/container/JFormContainer.vue';
  import { Form } from 'ant-design-vue';
  const useForm = Form.useForm;

  export default defineComponent({
    name: '{{detailEntityName}}Form',
    components:{ JFormContainer },
    props:{
      disabled: { type: Boolean, default: false }
    },
    setup(){
      const isForm = true;  // ✅ 关键标记！useValidateAntFormAndTable 用此判断为表单而非 JVxeTable
      const loading = ref(false);
      const formRef = ref();
      const formData = reactive<Record<string, any>>({
        id: '',
        // ... 一对一子表字段
      });
      const validatorRules = reactive({ /* 校验规则 */ });
      const { resetFields, validate, validateInfos } = useForm(formData, validatorRules, { immediate: false });
      const formItemLayout = {
        labelCol: { xs: { span: 24 }, sm: { span: 5 } },
        wrapperCol: { xs: { span: 24 }, sm: { span: 16 } },
      };

      // ✅ 接收 mainId（不是 url + id），直接调用 API 函数
      async function initFormData(mainId) {
        resetFields();
        let tmpData = {};
        if (mainId) {
          let list = await query{{detailEntityName}}ListByMainId(mainId);
          if (list && list.length > 0) {
            let temp = list[0];
            Object.keys(formData).forEach((key) => {
              if (temp.hasOwnProperty(key)) {
                tmpData[key] = temp[key];
              }
            });
          }
        }
        Object.assign(formData, tmpData);
      }

      // ✅ getFormData 返回 toRaw(formData)（不是数组！）
      async function getFormData() {
        try {
          await validate();
        } catch ({ errorFields }) {
          if (errorFields) {
            const firstField = errorFields[0];
            if (firstField) {
              formRef.value.scrollToField(firstField.name, { behavior: 'smooth', block: 'center' });
            }
          }
          return Promise.reject(errorFields);
        }
        let subFormData = toRaw(formData);
        if (Object.keys(subFormData).length > 0) {
          return subFormData;
        }
        return false;
      }

      function setFieldsValue(values) {
        if (values) {
          Object.keys(values).map(k => { formData[k] = values[k]; });
        }
      }

      return {
        loading, formData, formItemLayout, initFormData, getFormData,
        setFieldsValue, isForm, validateInfos, formRef,
      }
    }
  });
</script>
```

**一对一子表 Form（vue3Native）与 vue3 封装风格的关键差异：**

| 维度 | vue3 封装风格 (C9) | vue3Native 原生风格 (C13) |
|------|-------------------|-------------------------|
| 模板 | `<BasicForm @register="registerForm" />` | 原生 `<a-form>` + `<JFormContainer>` + 手写每个 `<a-form-item>` |
| useForm 来源 | `import { useForm } from '/@/components/Form/index'` | `import { Form } from 'ant-design-vue'; Form.useForm` |
| `initFormData` 参数 | `(url, id)` — 传 URL 字符串 + 主表 ID | `(mainId)` — 只传主表 ID，内部直接调用 API 函数 |
| `initFormData` 实现 | `defHttp.get({url, params:{id}}, {isTransformResponse:false})` 取 `res.result[0]` | `await queryXxxByMainId(mainId)` 取 `list[0]` |
| `getFormData` 返回值 | **数组** `[formData]` | **对象** `toRaw(formData)`（`useValidateAntFormAndTable` 内部处理包装） |
| 暴露 `isForm` 属性 | 不需要 | **必须** `const isForm = true` 并 return |
| 暴露 `validateForm` | 需要（`useJvxeMethod` 的 `validateSubForm` 回调会调用） | 不需要（`useValidateAntFormAndTable` 内部自动校验） |

#### C13-6. List.vue 差异

vue3Native 一对多的 List.vue 使用 `useModal` + `openModal(true, {...})` 模式（与 vue3 封装风格**相同**）：

```typescript
import { useModal } from '/@/components/Modal';
import EduCourseModal from './components/EduCourseModal.vue';

const [registerModal, { openModal }] = useModal();

function handleAdd() {
  openModal(true, { isUpdate: false, showFooter: true });
}
function handleEdit(record) {
  openModal(true, { record, isUpdate: true, showFooter: true });
}
function handleDetail(record) {
  openModal(true, { record, isUpdate: true, showFooter: false });
}
```

模板中使用 `@register="registerModal"`：
```html
<EduCourseModal @register="registerModal" @success="handleSuccess"></EduCourseModal>
```

**注意：** 不要用 `ref` + `registerModal.value.add()` 模式（那是 `j-modal` 风格），vue3Native 一对多使用 `BasicModal` + `useModal/useModalInner` 配对。

#### C13-7. vue3Native 一对多技术要点和常见陷阱

| 要点 | 说明 |
|------|------|
| **Form.vue 必须用 `defineComponent`** | 不能用 `<script setup>`，因为 Modal 需要通过 `ref` 调用 `add()/edit()/submitForm()` 方法，`defineComponent` + `return` 自动暴露 |
| **Modal 是薄包装器** | Modal 不包含子表，不做数据收集，只负责打开/关闭和调用 Form 方法 |
| **`useValidateAntFormAndTable` 替代 `useJvxeMethod`** | 原生风格使用 `useValidateAntFormAndTable(activeKey, refsMap)` 而非 `useJvxeMethod`，它根据 `isForm` 属性自动区分表单和 JVxeTable |
| **一对一子表必须暴露 `isForm = true`** | `useValidateAntFormAndTable` 通过检查 ref 组件上的 `isForm` 属性来判断是调用 `getFormData()` 还是 `getTableData()` |
| **一对一子表 `getFormData()` 返回对象** | 返回 `toRaw(formData)`（对象），不是数组 `[formData]`；`useValidateAntFormAndTable` 内部会自动包装 |
| **一对一子表 `initFormData(mainId)` 只传 ID** | 直接调用 API 函数获取数据，不传 URL 字符串 |
| **子表 API 必须是函数导出** | `export const queryXxxByMainId = (id) => defHttp.get({...})`，不是 URL 字符串 |
| **`saveOrUpdate` 不用 `isTransformResponse: false`** | 原生风格的 `saveOrUpdate` 直接 `defHttp.post({url, params})`，不需要手动解析响应 |
| **需要 `queryDataById` 函数** | Form 编辑时通过 `queryDataById(id)` 重新查询主表完整数据，不直接用 record（避免字段缺失） |
| **activeKey 与 a-tabs 对应** | `useValidateAntFormAndTable` 的第一个参数 `activeKey` 与 `<a-tabs v-model:activeKey>` 一致 |
| **refsMap 的 key 与 tab key 一致** | `useValidateAntFormAndTable` 的第二个参数中，key 必须与 `<a-tab-pane key="xxx">` 的 key 一致 |
| **数据提交在 Form 中完成** | `submitForm()` 在 Form.vue 中，调用 `getFormData()` + `getSubFormAndTableData()` 后 `saveOrUpdate` |
| **`getSubFormAndTableData()` 自动组装子表字段名** | 返回对象的 key 格式为 `{tabKey}List`（如 `eduCourseChapterList`），与后端 Page VO 属性名一致 |

---

## D. 字段类型完整映射速查表

| 业务语义 | DB列类型 | Java类型 | @Excel format | vue3 FormSchema component | vue3Native 控件 | 查询组件 |
|----------|---------|----------|---------------|--------------------------|----------------|---------|
| 名称/编码/标题 | varchar(100) | String | - | Input | a-input | JInput |
| 金额/价格 | decimal(10,2) | BigDecimal | - | InputNumber | a-input-number | InputNumber |
| 整数/数量 | int(11) | Integer | - | InputNumber | a-input-number | InputNumber |
| 浮点数 | double | Double | - | InputNumber | a-input-number | InputNumber |
| 状态/类型(字典) | varchar(10) | String | dicCode | JDictSelectTag | JDictSelectTag | JDictSelectTag |
| 单选(字典) | varchar(10) | String | dicCode | JDictSelectTag(type=radio) | a-radio-group | JDictSelectTag |
| 多选(字典) | varchar(200) | String | dicCode | JDictSelectTag(type=checkbox) | a-checkbox-group | - |
| 开关/是否 | varchar(2) | String | - | JSwitch | a-switch | - |
| 日期 | date | Date | yyyy-MM-dd | DatePicker | a-date-picker | DatePicker |
| 日期时间 | datetime | Date | yyyy-MM-dd HH:mm:ss | DatePicker(showTime) | a-date-picker(showTime) | DatePicker(showTime) |
| 长文本/备注 | text | String | - | InputTextArea | a-textarea | - |
| 富文本 | text | String | - | JEditor | JEditor | - |
| Markdown | text | String | - | JMarkdownEditor | JMarkdownEditor | - |
| 图片 | varchar(1000) | String | - | JImageUpload | JImageUpload | - |
| 文件/附件 | varchar(1000) | String | - | JUpload | JUpload | - |
| 用户选择 | varchar(32) | String | dictTable=sys_user | JSelectUserByDept | JSelectUserByDept | - |
| 部门选择 | varchar(32) | String | dictTable=sys_depart | JSelectDept | JSelectDept | - |
| 分类树 | varchar(64) | String | - | JCategorySelect | JCategorySelect | JCategorySelect |
| 搜索选择 | varchar(32) | String | dictTable | JSearchSelect | JSearchSelect | JSearchSelect |
| 省市区 | varchar(200) | String | - | JAreaLinkage | JAreaLinkage | - |
| 排序号 | int(11) | Integer | - | InputNumber | a-input-number | - |

## E. 建表 DDL 模板（如需要自动建表）

```sql
CREATE TABLE `{{tableName}}` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  -- 业务字段
  -- `field_name` varchar(100) DEFAULT NULL COMMENT '字段注释',
  `create_by` varchar(50) DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT NULL COMMENT '创建日期',
  `update_by` varchar(50) DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT NULL COMMENT '更新日期',
  `sys_org_code` varchar(64) DEFAULT NULL COMMENT '所属部门',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='{{description}}';
```

树表额外字段：
```sql
  `pid` varchar(36) DEFAULT NULL COMMENT '父级节点',
  `has_child` varchar(3) DEFAULT NULL COMMENT '是否有子节点',
```

子表额外字段：
```sql
  `{{main_table_name}}_id` varchar(36) DEFAULT NULL COMMENT '主表外键',
```

---

## F. 增量字段修改（加字段/删字段/改字段）

### F1. 定位已有代码文件

增量修改时，必须先找到并读取所有相关文件：

```
后端文件（在后端根目录搜索）：
  - **/entity/{EntityName}.java          → 实体类
  - **/controller/{EntityName}Controller.java  → 控制器（通常不需要改）
  - **/service/I{EntityName}Service.java       → Service接口（通常不需要改）
  - **/service/impl/{EntityName}ServiceImpl.java → Service实现（通常不需要改）

前端文件（在前端 src/views/ 下搜索）：
  - **/{EntityName}.data.ts              → 列定义 + 表单Schema
  - **/{EntityName}List.vue              → 列表页（通常不需要改）
  - **/{EntityName}Modal.vue             → 弹窗（通常不需要改）
  - **/{EntityName}Form.vue              → 表单（vue3Native风格，需要改）
```

### F2. 加字段 — 需要修改的位置

**每加一个字段，需要修改以下文件：**

#### 1) Entity.java — 在业务字段区域末尾追加

根据字段类型选择对应的注解模式（参考 A1 节的业务字段模板）：

```java
// String 字段
@Excel(name = "字段注释", width = 15)
@Schema(description = "字段注释")
private String fieldName;

// 带字典的 String 字段
@Excel(name = "字段注释", width = 15, dicCode = "dict_code")
@Dict(dicCode = "dict_code")
@Schema(description = "字段注释")
private String fieldName;

// Integer 字段
@Excel(name = "字段注释", width = 15)
@Schema(description = "字段注释")
private Integer fieldName;

// BigDecimal 字段（需确认 import java.math.BigDecimal 已存在）
@Excel(name = "字段注释", width = 15)
@Schema(description = "字段注释")
private BigDecimal fieldName;

// Date 字段（需确认 import java.util.Date + JsonFormat + DateTimeFormat 已导入）
@Excel(name = "字段注释", width = 15, format = "yyyy-MM-dd")
@JsonFormat(timezone = "GMT+8", pattern = "yyyy-MM-dd")
@DateTimeFormat(pattern = "yyyy-MM-dd")
@Schema(description = "字段注释")
private Date fieldName;

// DateTime 字段
@Excel(name = "字段注释", width = 20, format = "yyyy-MM-dd HH:mm:ss")
@JsonFormat(timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
@DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss")
@Schema(description = "字段注释")
private Date fieldName;
```

**注意：** 检查是否需要新增 import 语句（如 BigDecimal、Date、JsonFormat、Dict 等）。

#### 2) *.data.ts — 三处追加

**a) columns 数组末尾追加列定义：**
```typescript
// 普通列
{
  title: '字段名称',
  align: 'center',
  dataIndex: 'fieldName',
},
// 字典列（dataIndex 加 _dictText 后缀）
{
  title: '状态',
  align: 'center',
  dataIndex: 'status_dictText',
},
// 图片列
{
  title: '图片',
  align: 'center',
  dataIndex: 'imageField',
  customRender: render.renderImage,
},
```

**b) searchFormSchema 数组追加查询条件（仅常用查询字段需要）：**
```typescript
{
  label: '字段名称',
  field: 'fieldName',
  component: 'JInput',  // 或 JDictSelectTag 等
  colProps: { span: 6 },
},
```

**c) formSchema 数组末尾追加（在最后一个字段 `}` 后、`];` 前）：**
```typescript
{
  label: '字段名称',
  field: 'fieldName',
  component: 'Input',  // 根据字段类型选择组件
  componentProps: { placeholder: '请输入字段名称' },
},
```

**d) superQuerySchema 数组追加（如果存在）：**
```typescript
{ title: '字段名称', value: 'fieldName', type: 'string' },
```

#### 3) *Form.vue — 仅 vue3Native 风格需要修改

在 `<a-form>` 中追加表单项：
```vue
<a-form-item label="字段名称" v-bind="validatorRules.fieldName" name="fieldName">
  <a-input v-model:value="formData.fieldName" placeholder="请输入字段名称" />
</a-form-item>
```

在 `formData` reactive 对象中追加初始值：
```typescript
fieldName: '',
```

#### 4) Flyway SQL — 生成 ALTER TABLE

```sql
ALTER TABLE `{{tableName}}` ADD COLUMN `column_name` varchar(100) DEFAULT NULL COMMENT '字段注释';
```

多个字段可合并为一条 ALTER：
```sql
ALTER TABLE `{{tableName}}`
  ADD COLUMN `field1` varchar(100) DEFAULT NULL COMMENT '注释1',
  ADD COLUMN `field2` int DEFAULT NULL COMMENT '注释2';
```

### F3. 删字段 — 需要修改的位置

**从以下位置移除字段相关代码：**

1. **Entity.java** — 删除字段声明及其注解（@Excel、@Dict、@Schema、@JsonFormat 等）
2. ***.data.ts** — 删除 columns 中对应列、searchFormSchema 中对应项、formSchema 中对应项、superQuerySchema 中对应项
3. ***Form.vue**（vue3Native）— 删除 `<a-form-item>` 和 formData 中对应属性
4. **Flyway SQL** — 生成 `ALTER TABLE \`{{tableName}}\` DROP COLUMN \`column_name\`;`

**注意：** 删除 Entity 字段后检查是否有不再使用的 import（如删除了唯一的 BigDecimal 字段，则移除 BigDecimal import）。

### F4. 改字段 — 需要修改的位置

根据修改内容，可能需要改动：

- **改类型**：Entity 字段类型 + data.ts 组件类型 + Form.vue 控件 + ALTER TABLE MODIFY
- **改注释/标题**：Entity @Excel name + @Schema description + data.ts title/label
- **加/改字典**：Entity @Dict + data.ts 组件改为 JDictSelectTag + columns dataIndex 加 _dictText
- **改必填**：data.ts formSchema 中 required 属性

Flyway SQL 示例：
```sql
ALTER TABLE `{{tableName}}` MODIFY COLUMN `column_name` decimal(10,2) DEFAULT NULL COMMENT '新注释';
```

### F5. 增量修改检查清单

每次增量修改完成后，确认：
- [ ] Entity.java — 字段声明 + 注解 + import
- [ ] *.data.ts — columns + searchFormSchema(如需) + formSchema + superQuerySchema(如存在)
- [ ] *Form.vue — 表单控件 + formData 初始值（仅 vue3Native）
- [ ] Flyway SQL — ALTER TABLE 语句
- [ ] 无遗漏的 import 增删
