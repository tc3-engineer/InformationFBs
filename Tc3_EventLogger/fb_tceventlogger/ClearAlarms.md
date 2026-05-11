# ClearAlarms

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventLogger` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/10361937547.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_ClearAlarms.xml`](../examples/P_Demo_ClearAlarms.xml) |

---

## 1. 功能简述

`FB_TcEventLogger.ClearAlarms()` 批量清除符合过滤条件的活动报警（即调用对应 alarm 的 `Clear()`）。支持 `I_TcEventFilter` 过滤器精确选择要清除的 alarm 集合。

适用：操作员在 HMI 上点「清除全部当前报警」按钮、或自动化逻辑里按 Severity / EventClass 批量复位故障状态。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nTimeStamp : ULINT := 0;
    bResetConfirmation : BOOL := FALSE;
    ipFilter : I_TcEventFilter;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nTimeStamp` | `ULINT` | `0` | 清除事件时间戳：0 = 用当前系统时间；非 0 = 自 1601-01-01 UTC 起的 100ns 数 |
| `bResetConfirmation` | `BOOL` | `FALSE` | TRUE = 同时把 WaitForConfirmation 状态置为 Reset；FALSE = 仅清除 Raised 状态 |
| `ipFilter` | `I_TcEventFilter` | - | 事件过滤器；传 0 清除全部活动 alarm |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

对每个匹配的 alarm 调用 `Clear()`：状态从 Raised 转 Cleared。若 alarm 是 `bWithConfirmation = TRUE`，确认状态保持 `WaitForConfirmation` 不变（除非传 `bResetConfirmation := TRUE`，则同时把确认状态置为 `Reset`）。

**过滤器逻辑**：`ipFilter` 传 0 时清除**所有**活动 alarm；传入 `FB_TcEventFilter` 实例则按规则匹配。时间戳 `nTimeStamp = 0` 用当前系统时间记录清除时刻——这个时间在审计里就是"批量清除动作"的发生时间。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 批量清除成功 | 继续业务 |
| `其他错误` | 过滤器无效 / 内部异常 ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- `bResetConfirmation := TRUE` 会绕过操作员确认环节——审计场景慎用。
- 过滤器传 0 = 清全部，操作前应在 HMI 端给操作员一个二次确认。（工程经验补充）
- Clear 后 alarm 实例仍在活动表里——下次 Raise 可以直接复用，无需重新 Create。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ClearAlarms.xml`](../examples/P_Demo_ClearAlarms.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

夜班操作员下班前"清空全部当前报警"按钮——把所有遗留的报警一次性收拾干净，准备交班


一句调用替代手写 FOR 循环遍历所有 alarm 实例 + 逐个 Clear


`ClearAllAlarms` 是本方法的简化版（不需要过滤器）；用 `GetAlarm` 拿到单个 alarm 指针后 Clear → 适合精细控制不适合批量


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.10.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/10361937547.html
- **相关**：`FB_TcEventLogger.ClearAllAlarms`, `FB_TcEventLogger.ConfirmAlarms`, `FB_TcEventFilter`
