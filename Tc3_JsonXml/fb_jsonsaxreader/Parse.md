# Parse

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `METHOD` |
| Category | `FB_JsonSaxReader` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4220233355.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_JsonSaxReader_Parse.TcPOU`](../examples/P_Demo_FB_JsonSaxReader_Parse.TcPOU) |

---

## 1. 功能简述

对给定 JSON 字符串启动 SAX 解析。每扫描到一个 JSON token，按类型回调传入的 `ITcJsonSaxHandler` 接口对象的对应方法。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    ipHdl : ITcJsonSaxHandler;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ipHdl` | `ITcJsonSaxHandler` | 实现 SAX 回调接口的对象指针，调用 Parse 时把自定义业务 FB 传入。 |


### VAR_OUTPUT

```iecst
VAR_OUTPUT
    hrErrorCode : HRESULT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hrErrorCode` | `HRESULT` | 操作失败时返回错误码（HRESULT）。`S_OK` (0) = 成功；其他值见附录 ADS Return Codes 表。 |


### VAR_IN_OUT

```iecst
VAR_IN_OUT
    sJson : STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sJson` | `STRING` | 字符串参数（STRING）。 |


## 3. 行为说明

传入完整 JSON 字符串和实现 `ITcJsonSaxHandler` 的回调对象。本 FB 按 token 顺序扫描 JSON：每解析到一个值、键、对象/数组边界，就调用回调对象对应的 OnXxx 方法。回调返回 `S_OK` 解析继续；返回 `S_FALSE` 立即终止扫描，本方法整体返回 `FALSE`。解析过程同步、单次调用完成；大文档建议分批传入或评估 cycle time 影响。

## 4. 错误码 / 返回值

本方法返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 调用成功 | 继续后续逻辑 |
| `FALSE` | 调用失败 | 检查输入参数 / 调 `ExceptionRaised()` 或读 `hrErrorCode` 定位 |

## 5. 使用注意 / 常见坑

- SAX 风格依赖调用顺序：违反 JSON 语法（如对象里无键的值）本 FB 不报错，但输出不是合法 JSON。
- 传入的 JSON 字符串需在 Parse 期间保持不变；SAX 解析器内部按指针访问字符串内容。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonSaxReader_Parse.TcPOU`](../examples/P_Demo_FB_JsonSaxReader_Parse.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：解析超大 JSON 日志（>1MB），全文 DOM 会爆 router 内存。
- **价值**：事件驱动按 token 流处理，内存与文档大小无关。
- **替代方案对比**：用 FB_JsonDomParser.ParseDocument → 大文件爆 router；用 STRING 操作切分 → 转义和嵌套难处理。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.3.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4220233355.html
- **相关 FB / FC**：`FB_JsonSaxReader`
