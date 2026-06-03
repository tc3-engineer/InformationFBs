# RemoveAllMembers

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
| Example | [`examples/P_Demo_FB_JsonDomParser_RemoveAllMembers.TcPOU`](../examples/P_Demo_FB_JsonDomParser_RemoveAllMembers.TcPOU) |

---

## 1. 功能简述

删除 JSON 对象节点下的所有子成员，但保留对象节点本身。

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

删除 JSON 对象节点下的所有子成员，但保留对象节点本身。调用者需注意：本方法的调用语义与 `FB_JsonDomParser` 的整体行为一致——先确保父对象已正确初始化（FB_JsonDomParser 的 `initStatus` = `S_OK`、必要时已 ParseDocument 或 NewDocument），再调用本方法。返回值/输出参数需在调用方业务代码中显式检查；如出现非预期返回，可调 `ExceptionRaised()`（DOM 解析器）或检查 `hrErrorCode`（IO/异步方法）定位问题。

## 4. 错误码 / 返回值

本方法返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 调用成功 | 继续后续逻辑 |
| `FALSE` | 调用失败 | 检查输入参数 / 调 `ExceptionRaised()` 或读 `hrErrorCode` 定位 |

## 5. 使用注意 / 常见坑

- DOM 内存只在 `NewDocument()` / `ParseDocument()` 时重新分配；频繁 Set/Add 会累积 router 内存（PDF 4.1 节明确警告）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonDomParser_RemoveAllMembers.TcPOU`](../examples/P_Demo_FB_JsonDomParser_RemoveAllMembers.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：在 `FB_JsonDomParser` 的工作流程里完成一个具体子操作；通常配合本 FB 的其他方法组合使用。
- **价值**：作为 `FB_JsonDomParser` API 的一部分提供标准化能力，业务代码无需自实现。
- **替代方案对比**：自己写实现 → 与本库类型/接口不互通；用其他库 → 与 TwinCAT 工程内现有 JSON/XML 流程脱节。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.1.91
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219231115.html
- **相关 FB / FC**：`FB_JsonDomParser`
