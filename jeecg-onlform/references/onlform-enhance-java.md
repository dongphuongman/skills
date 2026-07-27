# Online 表单 Java 增强参考

## 配置类型

| 类型 | 内容填写 | 说明 |
|------|---------|------|
| `spring` | @Component 注解值 | Spring Bean 名称 |
| `class` | 完整类路径 | 全限定类名 |
| `http` | 请求 URL | POST 接口地址 |

> **重要限制：http 类型不支持导入增强！** 导入增强只能使用 `spring` 或 `class` 方式。

## 各 buttonCode 支持的 cgJavaType

| buttonCode | spring | class | http | 说明 |
|-----------|--------|-------|------|------|
| `add/edit/delete` | ✅ | ✅ | ✅ | 表单操作增强 |
| `query/export` | ✅ | ✅ | ✅ | 列表/导出增强 |
| `import` | ✅ | ✅ | ❌ | **导入只支持 spring 和 class** |

## Java 增强保存 API body 格式

```json
// spring 方式
{"buttonCode": "add", "event": "start", "cgJavaType": "spring", "cgJavaValue": "springKeyAddEnhance", "activeStatus": "1"}

// class 方式
{"buttonCode": "edit", "event": "start", "cgJavaType": "class", "cgJavaValue": "org.jeecg.modules.demo.online.enhance.JavaClassEditEnhance", "activeStatus": "1"}

// http 方式（导入不支持）
{"buttonCode": "query", "event": "end", "cgJavaType": "http", "cgJavaValue": "/demo/online/enhance/queryMask", "activeStatus": "1"}
```

| 字段 | 说明 | 可选值 |
|------|------|--------|
| `buttonCode` | 绑定按钮 | `add`/`edit`/`delete`/`import`/`export`/`query`/自定义按钮编码 |
| `event` | 事件时机 | `start`=操作前, `end`=操作后 |
| `cgJavaType` | 增强类型 | **`spring`**=Bean名, **`class`**=全限定类名, **`http`**=HTTP接口地址 |
| `cgJavaValue` | 增强内容 | Bean名/类路径/HTTP接口地址 |
| `activeStatus` | 是否生效 | `"1"`=有效 |

> **极重要（实测验证 2026-03-31）：**
> - `cgJavaType` 正确值是 **`spring`、`class`、`http`**（不是 `spring-key`/`java-class`/`http-api`）
> - 前端 UI 显示为 spring-key/java-class/http-api，但 API 和 DB 存储必须用 `spring`/`class`/`http`
> - 保存 API 会实时校验 Bean/Class 是否存在，必须先部署 Java 代码、重启后端再配置增强

## 接口说明

| 场景 | 实现接口 | 方法签名 |
|------|---------|---------|
| 新增/编辑/删除 | `CgformEnhanceJavaInter` | **`void execute(String tableName, JSONObject json)`** |
| 查询/导出 | `CgformEnhanceJavaListInter` | `void execute(String tableName, List<Map<String,Object>> data)` |
| 导入 | `CgformEnhanceJavaImportInter` | `EnhanceDataEnum execute(String tableName, JSONObject json)` |

> `CgformEnhanceJavaInter.execute` 返回值是 **`void`**，写成 `int` 会编译报错。

## 必须的 import 语句

```java
// 表单增强（add/edit/delete）
import org.jeecg.modules.online.cgform.enhance.CgformEnhanceJavaInter;

// 列表增强（query/export）
import org.jeecg.modules.online.cgform.enhance.CgformEnhanceJavaListInter;

// 导入增强（import）
import org.jeecg.modules.online.cgform.enhance.CgformEnhanceJavaImportInter;
import org.jeecg.modules.online.cgform.enums.EnhanceDataEnum;  // ⚠️ 注意是 enums 不是 enhance
```

## 导入增强返回值

| 枚举值 | 说明 |
|--------|------|
| `EnhanceDataEnum.ABANDON` (0) | 丢弃该行 |
| `EnhanceDataEnum.INSERT` (1) | 插入新记录 |
| `EnhanceDataEnum.UPDATE` (2) | 更新已有记录（需在 json 中设置 id） |

## HTTP-API 增强参数

**表单类**：`{tableName, record}` → 返回 `Result`（success=false 回滚操作）
**列表类**：`{tableName, dataList}` → 返回 `Result`（success=true 时 result 为转换后数据）

## Java 增强 API

| 操作 | 方法 | URL |
|------|------|-----|
| 查询Java增强 | GET | `/online/cgform/head/enhanceJava/{headId}` |
| 新增/更新Java增强 | POST/PUT | `/online/cgform/head/enhanceJava/{headId}` |

---

## 实战场景：4种Java增强完整流程（已验证 2026-03-31）

### 配置步骤（顺序不能错）

1. **编写 Java 代码**（`jeecg-module-demo/src/main/java/org/jeecg/modules/demo/online/enhance/`）
2. **编译打包** `mvn package -Dmaven.test.skip=true`
3. **重启后端**
4. **通过 API 配置增强**（此时 Bean/Class 校验才能通过）

### 示例1：spring 方式 — 新增前校验+自动填充

```java
@Slf4j
@Component("springKeyAddEnhance")
public class SpringKeyAddEnhance implements CgformEnhanceJavaInter {
    @Override
    public void execute(String tableName, JSONObject json) throws BusinessException {
        String title = json.getString("title");
        if (title != null && title.contains("测试")) {
            throw new BusinessException("标题不能包含'测试'关键词！");
        }
        if (json.getString("remark") == null) {
            json.put("remark", "由spring增强自动填充");
        }
    }
}
```
配置：`{"buttonCode":"add","event":"start","cgJavaType":"spring","cgJavaValue":"springKeyAddEnhance","activeStatus":"1"}`

### 示例2：class 方式 — 编辑前校验

```java
@Slf4j
public class JavaClassEditEnhance implements CgformEnhanceJavaInter {
    @Override
    public void execute(String tableName, JSONObject json) throws BusinessException {
        if ("2".equals(json.getString("status"))) {
            throw new BusinessException("已通过的记录不允许编辑！");
        }
    }
}
```
配置：`{"buttonCode":"edit","event":"start","cgJavaType":"class","cgJavaValue":"org.jeecg.modules.demo.online.enhance.JavaClassEditEnhance","activeStatus":"1"}`

### 示例3：http 方式 — 查询后手机号脱敏

```java
@Slf4j
@RestController("httpApiQueryEnhance")
@RequestMapping("/demo/online/enhance")
public class HttpApiQueryEnhance {
    @PostMapping("/queryMask")
    public Result<?> queryMask(@RequestBody JSONObject params) {
        JSONArray dataList = params.getJSONArray("dataList");
        if (dataList != null) {
            for (int i = 0; i < dataList.size(); i++) {
                JSONObject record = dataList.getJSONObject(i);
                String phone = record.getString("phone");
                if (phone != null && phone.length() >= 11) {
                    record.put("phone", phone.substring(0, 3) + "****" + phone.substring(7));
                }
            }
        }
        Result<?> res = Result.OK(dataList);
        res.setCode(1);
        return res;
    }
}
```
配置：`{"buttonCode":"query","event":"end","cgJavaType":"http","cgJavaValue":"/demo/online/enhance/queryMask","activeStatus":"1"}`

### 示例4：spring 方式 — 导入数据校验

```java
@Slf4j
@Component("importScoreEnhance")
public class ImportScoreEnhance implements CgformEnhanceJavaImportInter {
    @Override
    public EnhanceDataEnum execute(String tableName, JSONObject json) throws BusinessException {
        String name = json.getString("name");
        if (name == null || name.trim().isEmpty()) {
            return EnhanceDataEnum.ABANDON;
        }
        Integer score = json.getInteger("score");
        if (score != null && score > 100) {
            json.put("score", 100);
        }
        return EnhanceDataEnum.INSERT;
    }
}
```
配置：`{"buttonCode":"import","event":"start","cgJavaType":"spring","cgJavaValue":"importScoreEnhance","activeStatus":"1"}`

### Java 增强关键总结

| 对比项 | spring | class | http |
|--------|--------|-------|------|
| 需要 @Component | ✅ 是 | ❌ 否 | ✅ 是(@RestController) |
| cgJavaValue 填什么 | Bean 名称 | 全限定类名 | 接口 URL 路径 |
| 支持导入增强 | ✅ | ✅ | ❌ |
| execute 返回值 | void | void | Result（code=1 生效） |
| 抛异常拦截操作 | throw BusinessException | throw BusinessException | return Result.error() |
