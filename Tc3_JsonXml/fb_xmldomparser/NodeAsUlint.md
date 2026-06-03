# NodeAsUlint

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
| Example | [`examples/P_Demo_FB_XmlDomParser_NodeAsUlint.TcPOU`](../examples/P_Demo_FB_XmlDomParser_NodeAsUlint.TcPOU) |

---

## 1. 功能简述

把 XML 节点的文本内容解析为 PLC `Ulint` 类型并返回。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    n : SXmlNode;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `n` | `SXmlNode` | 目标 XML 节点的 `SXmlNode` 引用。 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

读取 XML 节点文本内容并按目标 PLC 类型解析。节点文本不符合目标类型格式时（如非数字字符串调 `NodeAsInt`），返回值未定义；需要严格类型检查可先 `NodeText` 取字符串再自己解析。本方法属 `FB_XmlDomParser` 的对外 API，调用前需要保证父 FB / 接口实例已就绪（必要时检查 `initStatus`）。

## 4. 错误码 / 返回值

本方法返回 `ULINT` 数值。

## 5. 使用注意 / 常见坑

- 调用前确保父 FB（`FB_XmlDomParser`）的 `initStatus` 为 `S_OK`。失败排查可调 `ExceptionRaised()`（DOM）或读 `hrErrorCode`（异步方法）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_XmlDomParser_NodeAsUlint.TcPOU`](../examples/P_Demo_FB_XmlDomParser_NodeAsUlint.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
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

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.7.73
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/5512100491.html
- **相关 FB / FC**：`FB_XmlDomParser`
