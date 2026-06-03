# GetJsonLength

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `METHOD` |
| Category | `FB_JsonDomParser` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219231115.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_JsonDomParser_GetJsonLength.TcPOU`](../examples/P_Demo_FB_JsonDomParser_GetJsonLength.TcPOU) |

---

## 1. 功能简述

返回 JSON 节点序列化后的字节长度。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    v : SJsonValue;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `v` | `SJsonValue` | 目标 JSON 节点的 `SJsonValue` 句柄。 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

返回 JSON 节点序列化后的字节长度。调用者需注意：本方法的调用语义与 `FB_JsonDomParser` 的整体行为一致——先确保父对象已正确初始化（FB_JsonDomParser 的 `initStatus` = `S_OK`、必要时已 ParseDocument 或 NewDocument），再调用本方法。返回值/输出参数需在调用方业务代码中显式检查；如出现非预期返回，可调 `ExceptionRaised()`（DOM 解析器）或检查 `hrErrorCode`（IO/异步方法）定位问题。

## 4. 错误码 / 返回值

本方法返回 `UDINT`，表示字节数或元素数。返回 0 通常表示对应内容不存在或长度为零。

## 5. 使用注意 / 常见坑

- DOM 内存只在 `NewDocument()` / `ParseDocument()` 时重新分配；频繁 Set/Add 会累积 router 内存（PDF 4.1 节明确警告）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonDomParser_GetJsonLength.TcPOU`](../examples/P_Demo_FB_JsonDomParser_GetJsonLength.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：从已解析的 JSON DOM 中读取某字段的 JsonLength 类型值（如解析云端下发指令里的目标速度、批次号、状态码）。
- **价值**：按节点直接取值，比反复扫字符串快。
- **替代方案对比**：自己 SubString + Trim + StrToInt 解析 → JSON 格式一变就崩；用 SAX → 简单查询写一堆回调过头。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.1.44
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219231115.html
- **相关 FB / FC**：`FB_JsonDomParser`, `IsJsonLength`, `SetJsonLength`
