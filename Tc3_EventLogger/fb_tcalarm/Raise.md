# Raise

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcAlarm` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050505739.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_Raise.xml`](../examples/P_Demo_Raise.xml) |

---

## 1. 功能简述

`FB_TcAlarm.Raise()` 把 alarm 状态从 "Not Raised" 切换到 "Raised"。如果创建时设了 `bWithConfirmation = TRUE`，确认状态同步置为 `WaitForConfirmation`。

调用时机：业务故障逻辑里检测到故障**上升沿**——前一周期 FALSE、本周期 TRUE。调一次 Raise() 之后 EventLogger 在事件日志里追加一条 Raised 记录，HMI 把这条 alarm 标红显示。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nTimeStamp : ULINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nTimeStamp` | `ULINT` | 事件时间戳：0 = 用当前系统时间；非 0 = 自 1601-01-01 UTC 起的 100ns 数 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

方法在调用瞬间同步切换状态。`nTimeStamp = 0` 用当前系统时间；非 0 用调用方传入的时间戳（自 1601-01-01 UTC 的 100ns 数）。后者适合"事故重放"或"从远程接收事件后再 Raise"等场景。

**与 Clear 的成对调用**：典型业务模式是 IF 故障信号 AND NOT 前一周期值 THEN Raise; IF NOT 故障信号 AND 前一周期值 THEN Clear。**不要每个周期都调 Raise**，否则会产生大量重复日志、刷爆 HMI。

如果当前已经是 Raised 状态再次调 Raise 会返回 `ADS_E_INVALIDSTATE`，状态不变，不会重复写日志。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 状态成功切换到 Raised | 继续业务 |
| `ADS_E_INVALIDSTATE` | alarm 已处于 Raised 状态 | 通常无需处理；表示边沿检测漏了 |
| `其他错误` | EventLogger 内部异常 ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- Raise 必须边沿触发，不能每周期都调，否则日志会被刷爆。
- 已 Raised 状态再 Raise 返回 ADS_E_INVALIDSTATE——不是错误，只是表示状态没变。
- 非 0 时间戳必须是 100ns 单位且基准是 1601-01-01 UTC（FILETIME），不是 Unix 时间。（工程经验补充）
- Raise 之前必须先 Create()——否则方法调用无效。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Raise.xml`](../examples/P_Demo_Raise.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

电机过载检测：电流传感器读数超过阈值的上升沿触发一次 Raise()


一句调用完成"事件日志 + HMI 显示 + 监听器分发"三件事，手写至少需要 ADSLOGSTR + HMI 联动 + 持久化三套独立逻辑


直接用 ADSLOGSTR 写文本日志 → 没结构化、不能 Clear/Confirm；用 `FB_TcEventLogger.SendMessageEx()` → 适合无状态通知不适合有状态报警


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.6.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050505739.html
- **相关**：`FB_TcAlarm.Clear`, `FB_TcAlarm.Confirm`, `FB_TcAlarm.Create`
