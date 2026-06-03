# AddRawObject

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `METHOD` |
| Category | `FB_JsonSaxPrettyWriter` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/11948988555.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_JsonSaxPrettyWriter_AddRawObject.TcPOU`](../examples/P_Demo_FB_JsonSaxPrettyWriter_AddRawObject.TcPOU) |

---

## 1. 功能简述

把外部已构造完成的 JSON 对象字符串原样追加到 SAX writer 缓冲中。不做语法检查；调用方需保证字符串本身是合法 JSON。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    rawJson : STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `rawJson` | `STRING` | 已构造好的 JSON 子串（数组/对象的完整字符串形式），库会原样追加。 |


## 3. 行为说明

把外部已构造完成的 JSON 对象字符串原样追加到 SAX writer 缓冲中。不做语法检查；调用方需保证字符串本身是合法 JSON。调用者需注意：本方法的调用语义与 `FB_JsonSaxPrettyWriter` 的整体行为一致——先确保父对象已正确初始化（FB_JsonSaxPrettyWriter 的 `initStatus` = `S_OK`、必要时已 ParseDocument 或 NewDocument），再调用本方法。返回值/输出参数需在调用方业务代码中显式检查；如出现非预期返回，可调 `ExceptionRaised()`（DOM 解析器）或检查 `hrErrorCode`（IO/异步方法）定位问题。

## 4. 错误码 / 返回值

本功能块/方法无返回值。状态通过 `initStatus` / `bError` / `hrErrorCode` 等输出反馈。

## 5. 使用注意 / 常见坑

- SAX 风格依赖调用顺序：违反 JSON 语法（如对象里无键的值）本 FB 不报错，但输出不是合法 JSON。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonSaxPrettyWriter_AddRawObject.TcPOU`](../examples/P_Demo_FB_JsonSaxPrettyWriter_AddRawObject.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：SAX 流式生成 JSON 时追加 RawObject 类型的值/键值对。
- **价值**：无 DOM 中间态，内存最省、速度最快。
- **替代方案对比**：用 DOM 拼后导出 → 多一份内存；手写字符串拼接 → 转义和嵌套层级控制出错风险大。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.5.21
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/11948988555.html
- **相关 FB / FC**：`FB_JsonSaxPrettyWriter`
