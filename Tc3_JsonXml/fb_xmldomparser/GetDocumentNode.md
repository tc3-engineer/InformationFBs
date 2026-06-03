# GetDocumentNode

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `METHOD` |
| Category | `FB_XmlDomParser` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/5512100491.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_XmlDomParser_GetDocumentNode.TcPOU`](../examples/P_Demo_FB_XmlDomParser_GetDocumentNode.TcPOU) |

---

## 1. 功能简述

`FB_XmlDomParser.GetDocumentNode()` 是 XML DOM 文档 提供的一个工具方法，在解析/构造 JSON 或 XML 文档的特定步骤中使用。具体参数语义见下文 §2 接口定义表格与 §3 行为说明；参数语义按命名约定推导自该方法在 `FB_XmlDomParser` 内的位置。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

从 JSON 节点取值。如果节点不是目标类型，返回值未定义，应在调用前先用对应的 `Is*` 方法检查。节点不存在（无效 `SJsonValue`）时返回值未定义；先用 `FindMember()` / `HasMember()` 确认节点存在。若需要在不确定类型时也安全取值，可读 `GetString()` 后自己解析。本方法属 `FB_XmlDomParser` 的对外 API，调用前需要保证父 FB / 接口实例已就绪（必要时检查 `initStatus`）。

## 4. 错误码 / 返回值

本方法返回 `SXmlNode` 引用/句柄。

| 返回值 | 含义 |
|---|---|
| 有效 `SXmlNode` | 调用成功，可用于后续 DOM/迭代器操作 |
| 无效（0 / NULL） | 节点不存在 / 参数错误 / 类型不匹配 |

## 5. 使用注意 / 常见坑

- 调用前确保父 FB（`FB_XmlDomParser`）的 `initStatus` 为 `S_OK`。失败排查可调 `ExceptionRaised()`（DOM）或读 `hrErrorCode`（异步方法）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_XmlDomParser_GetDocumentNode.TcPOU`](../examples/P_Demo_FB_XmlDomParser_GetDocumentNode.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：从已解析的 JSON DOM 中读取某字段的 DocumentNode 类型值（如解析云端下发指令里的目标速度、批次号、状态码）。
- **价值**：按节点直接取值，比反复扫字符串快。
- **替代方案对比**：自己 SubString + Trim + StrToInt 解析 → JSON 格式一变就崩；用 SAX → 简单查询写一堆回调过头。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.7.50
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/5512100491.html
- **相关 FB / FC**：`FB_XmlDomParser`, `IsDocumentNode`, `SetDocumentNode`
