# ConfirmAlarms

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventLogger` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/10361939723.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_ConfirmAlarms.xml`](../examples/P_Demo_ConfirmAlarms.xml) |

---

## 1. 功能简述

`FB_TcEventLogger.ConfirmAlarms()` 批量确认符合过滤条件的 alarm（即调用对应 alarm 的 `Confirm()`）。

适用：HMI 上「确认选定报警」批量操作、或自动化逻辑按 EventClass / Severity 批量确认特定类别的故障。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nTimeStamp : ULINT := 0;
    ipFilter : I_TcEventFilter;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nTimeStamp` | `ULINT` | `0` | 确认时间戳：0 = 当前系统时间 |
| `ipFilter` | `I_TcEventFilter` | - | 过滤器；传 0 确认全部 WaitForConfirmation |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

对每个匹配的 alarm 调用 `Confirm()`：把 `WaitForConfirmation` 状态切换为 `Confirmed`。Raised/Cleared 主状态不受影响。

**过滤器**：`ipFilter := 0` 时确认所有 `WaitForConfirmation` 状态的 alarm；传 `FB_TcEventFilter` 实例可按规则匹配子集。`nTimeStamp = 0` 用当前系统时间作为确认时刻。确认时刻在事后审计里就是「操作员响应时间」的关键指标——比 Raise 晚的越多代表响应越慢。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 批量确认成功 | 继续业务 |
| `其他错误` | 过滤器无效 / 内部异常 ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- 批量确认绕过逐条审视——若某条故障未真正处理就被确认，事故责任不清。（工程经验补充）
- 过滤器要写对——错误的过滤器可能漏确认（看似确认实际没动）。（工程经验补充）
- Confirm 不改变 Raised/Cleared 主状态——alarm 还在 Raised 时调 Confirm 仍生效。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ConfirmAlarms.xml`](../examples/P_Demo_ConfirmAlarms.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

HMI 上「确认选定类别报警」批量操作（例如只确认 Severity ≥ Warning 的报警，Info 类不动）


过滤器机制让批量确认精细可控


`ConfirmAllAlarms` → 无过滤器全确认；逐个 alarm 调 Confirm → 适合精细控制不适合批量


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.10.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/10361939723.html
- **相关**：`FB_TcEventLogger.ConfirmAllAlarms`, `FB_TcEventLogger.ClearAlarms`, `FB_TcEventFilter`
