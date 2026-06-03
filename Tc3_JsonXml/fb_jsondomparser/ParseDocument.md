# ParseDocument

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
| Example | [`examples/P_Demo_FB_JsonDomParser_ParseDocument.TcPOU`](../examples/P_Demo_FB_JsonDomParser_ParseDocument.TcPOU) |

---

## 1. 功能简述

解析输入的 JSON 字符串并加载到 DOM 内存。调用后旧 DOM 被释放。返回值非零表示根节点的 `SJsonValue` 句柄。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

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

把外部 JSON 字符串完整加载到 DOM 内存。调用后旧 DOM 节点被释放，旧的 `SJsonValue` 句柄全部失效。成功返回值为新文档根节点的 `SJsonValue` 句柄；解析失败返回无效句柄，此时 `ExceptionRaised()` 会返回 `TRUE`。本方法是同步调用，单次 PLC 周期内完成；大文档可能拖长 PLC 周期，注意 cycle time。

## 4. 错误码 / 返回值

本方法返回 `SJsonValue` 引用/句柄。

| 返回值 | 含义 |
|---|---|
| 有效 `SJsonValue` | 调用成功，可用于后续 DOM/迭代器操作 |
| 无效（0 / NULL） | 节点不存在 / 参数错误 / 类型不匹配 |

## 5. 使用注意 / 常见坑

- DOM 内存只在 `NewDocument()` / `ParseDocument()` 时重新分配；频繁 Set/Add 会累积 router 内存（PDF 4.1 节明确警告）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonDomParser_ParseDocument.TcPOU`](../examples/P_Demo_FB_JsonDomParser_ParseDocument.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：接收一帧 MQTT JSON 报文，加载到 DOM 准备后续 Find / Get 操作。
- **价值**：同步单次调用，调用后立刻可访问；省去维护 SAX 状态机的复杂度。
- **替代方案对比**：FB_JsonSaxReader 流式解析 → 写一堆回调；自己写 token 扫描 → 工作量大。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.1.75
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219231115.html
- **相关 FB / FC**：`FB_JsonDomParser`
