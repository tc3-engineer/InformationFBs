# GetDocumentRoot

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
| Example | [`examples/P_Demo_FB_JsonDomParser_GetDocumentRoot.TcPOU`](../examples/P_Demo_FB_JsonDomParser_GetDocumentRoot.TcPOU) |

---

## 1. 功能简述

返回 DOM 内存中 JSON 文档的根节点 `SJsonValue` 句柄。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

返回 DOM 内存中 JSON 文档的根节点 `SJsonValue` 句柄。调用者需注意：本方法的调用语义与 `FB_JsonDomParser` 的整体行为一致——先确保父对象已正确初始化（FB_JsonDomParser 的 `initStatus` = `S_OK`、必要时已 ParseDocument 或 NewDocument），再调用本方法。返回值/输出参数需在调用方业务代码中显式检查；如出现非预期返回，可调 `ExceptionRaised()`（DOM 解析器）或检查 `hrErrorCode`（IO/异步方法）定位问题。

## 4. 错误码 / 返回值

本方法返回 `SJsonValue` 引用/句柄。

| 返回值 | 含义 |
|---|---|
| 有效 `SJsonValue` | 调用成功，可用于后续 DOM/迭代器操作 |
| 无效（0 / NULL） | 节点不存在 / 参数错误 / 类型不匹配 |

## 5. 使用注意 / 常见坑

- DOM 内存只在 `NewDocument()` / `ParseDocument()` 时重新分配；频繁 Set/Add 会累积 router 内存（PDF 4.1 节明确警告）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonDomParser_GetDocumentRoot.TcPOU`](../examples/P_Demo_FB_JsonDomParser_GetDocumentRoot.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：拿到根节点句柄做后续 FindMember / Add*Member 操作的入口。
- **价值**：标准 DOM 入口点，避免自己存档根节点。
- **替代方案对比**：不要根节点直接 FindMember → 第一层找不到时不知道是路径错还是文档错。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.1.37
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219231115.html
- **相关 FB / FC**：`FB_JsonDomParser`, `IsDocumentRoot`, `SetDocumentRoot`
