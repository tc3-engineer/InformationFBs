# FB_AsyncStrResult

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/4278667403.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_AsyncStrResult.xml`](../examples/P_Demo_FB_AsyncStrResult.xml) |

---

## 1. 功能简述

`FB_AsyncStrResult` 是 TwinCAT 3 EventLogger 异步字符串请求的**结果承载 FB**——`FB_TcEventBase.RequestEventText()` / `F_GetEventText()` 等异步调用都返回它的实例引用，调用方持续轮询其状态属性 + 完成后调 `GetString()` 取最终字符串。

属性：`bBusy`（处理中）、`bError`（错误标志）、`hrErrorCode`（错误码）。方法：`GetString()` 取结果字符串。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sResult : REFERENCE TO STRING;
    nResult : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sResult` | `REFERENCE TO STRING` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `nResult` | `UDINT` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

FB_AsyncStrResult 不直接发起请求——它由 EventLogger API 内部填充。PLC 侧业务代码只负责声明实例、传入异步调用、轮询状态、取结果。

**典型流程**：调用 `FB_TcEventBase.RequestEventText(..., fbAsyncResult := myFbResult)` 发起异步请求，之后每周期检查 `myFbResult.bBusy`，FALSE 表示已完成；若 `bError = FALSE` 调 `GetString` 取结果文本；若 `bError = TRUE` 读 `hrErrorCode` 排错。

**并发限制**：每个 FB_AsyncStrResult 实例同时只能承载一个请求——并发查多条文本需多个实例。复用同一实例发起新请求前建议先确认 bBusy = FALSE，否则会覆盖未完成的请求。

## 4. 错误码 / 返回值

本方法/属性不返回数值（`VOID` 或 getter 直接返回引用）。状态通过 EventLogger 的事件日志间接反映。

## 5. 使用注意 / 常见坑

- **异步**：发起 Request 后必须周期检查 `bBusy` 直到 FALSE，再读结果——不能立即用。
- 失败要检查 `bError` 与 `hrErrorCode`——`bBusy = FALSE` 不等于成功。
- 发起多次 Request 之间要 `Clear()` 清理上次结果，否则可能读到旧数据。（工程经验补充）
- LangId 必须是 Windows LCID（如 1033=英文、2052=简体中文、1031=德文）；事件类未配置对应语言会回退默认。
- STRING 输出缓冲必须足够长（建议 STRING(255)+），否则文本被截断。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_AsyncStrResult.xml`](../examples/P_Demo_FB_AsyncStrResult.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

HMI 后端异步取事件文本：发起请求后等结果到达再刷新显示


非阻塞获取本地化文本，PLC 周期不卡顿；多语言资源外部修改不需要重编 PLC


同步阻塞调用 → 会拖慢 PLC 周期；本异步模式是 Beckhoff 推荐


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/4278667403.html
- **相关**：`FB_TcEventBase.RequestEventText`, `F_GetEventText`, `FB_RequestEventText`
