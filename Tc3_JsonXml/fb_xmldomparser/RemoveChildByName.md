# RemoveChildByName

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
| Example | [`examples/P_Demo_FB_XmlDomParser_RemoveChildByName.TcPOU`](../examples/P_Demo_FB_XmlDomParser_RemoveChildByName.TcPOU) |

---

## 1. 功能简述

从当前节点下按名字删除指定子节点。

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

```iecst
VAR_IN_OUT
    name : STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `name` | `STRING` | 成员/属性名（VAR_IN_OUT，调用方传入字符串）。 |


## 3. 行为说明

从当前 XML 节点下删除指定子节点。调用后被删除节点的引用立刻失效，不要再使用；调用方还持有的其他子节点引用不受影响。本方法属 `FB_XmlDomParser` 的对外 API，调用前需要保证父 FB / 接口实例已就绪（必要时检查 `initStatus`）。如返回值或输出参数不符合预期，可优先检查输入参数有效性，再读 `hrErrorCode` 或检查解析上下文定位。

## 4. 错误码 / 返回值

本方法返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 调用成功 | 继续后续逻辑 |
| `FALSE` | 调用失败 | 检查输入参数 / 调 `ExceptionRaised()` 或读 `hrErrorCode` 定位 |

## 5. 使用注意 / 常见坑

- 调用前确保父 FB（`FB_XmlDomParser`）的 `initStatus` 为 `S_OK`。失败排查可调 `ExceptionRaised()`（DOM）或读 `hrErrorCode`（异步方法）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_XmlDomParser_RemoveChildByName.TcPOU`](../examples/P_Demo_FB_XmlDomParser_RemoveChildByName.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：在 `FB_XmlDomParser` 的工作流程里完成一个具体子操作；通常配合本 FB 的其他方法组合使用。
- **价值**：作为 `FB_XmlDomParser` API 的一部分提供标准化能力，业务代码无需自实现。
- **替代方案对比**：自己写实现 → 与本库类型/接口不互通；用其他库 → 与 TwinCAT 工程内现有 JSON/XML 流程脱节。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.7.78
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/5512100491.html
- **相关 FB / FC**：`FB_XmlDomParser`
