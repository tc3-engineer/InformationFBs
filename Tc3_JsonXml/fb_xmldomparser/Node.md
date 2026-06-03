# Node

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
| Example | [`examples/P_Demo_FB_XmlDomParser_Node.TcPOU`](../examples/P_Demo_FB_XmlDomParser_Node.TcPOU) |

---

## 1. 功能简述

`FB_XmlDomParser.Node()` 是 XML DOM 文档 提供的一个工具方法，在解析/构造 JSON 或 XML 文档的特定步骤中使用。具体参数语义见下文 §2 接口定义表格与 §3 行为说明；参数语义按命名约定推导自该方法在 `FB_XmlDomParser` 内的位置。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    it : SXmlIterator;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `it` | `SXmlIterator` | 迭代器（VAR_INPUT REFERENCE 或 VAR_IN_OUT）；调用方提供后由库填入当前位置。 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

`FB_XmlDomParser.Node()` 是 XML DOM 文档 提供的一个工具方法，在解析/构造 JSON 或 XML 文档的特定步骤中使用。具体参数语义见下文 §2 接口定义表格与 §3 行为说明；参数语义按命名约定推导自该方法在 `FB_XmlDomParser` 内的位置。调用者需注意：本方法的调用语义与 `FB_XmlDomParser` 的整体行为一致——先确保父对象已正确初始化（FB_XmlDomParser 的 `initStatus` = `S_OK`、必要时已 ParseDocument 或 NewDocument），再调用本方法。返回值/输出参数需在调用方业务代码中显式检查；如出现非预期返回，可调 `ExceptionRaised()`（DOM 解析器）或检查 `hrErrorCode`（IO/异步方法）定位问题。

## 4. 错误码 / 返回值

本方法返回 `SXmlNode` 引用/句柄。

| 返回值 | 含义 |
|---|---|
| 有效 `SXmlNode` | 调用成功，可用于后续 DOM/迭代器操作 |
| 无效（0 / NULL） | 节点不存在 / 参数错误 / 类型不匹配 |

## 5. 使用注意 / 常见坑

- 调用前确保父 FB（`FB_XmlDomParser`）的 `initStatus` 为 `S_OK`。失败排查可调 `ExceptionRaised()`（DOM）或读 `hrErrorCode`（异步方法）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_XmlDomParser_Node.TcPOU`](../examples/P_Demo_FB_XmlDomParser_Node.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：读取 XML 节点文本作为 PLC 数值类型用，如解析配置文件中的参数。
- **价值**：一次调用完成解析+类型转换，省去手写 StrToInt 等。
- **替代方案对比**：自行 NodeText 后再 ATOI / VAL → 多写一步；忘了校验类型 → 异常字符崩。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.7.66
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/5512100491.html
- **相关 FB / FC**：`FB_XmlDomParser`
