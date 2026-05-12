# Confirm

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcAlarm` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050451339.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_Confirm.xml`](../examples/P_Demo_Confirm.xml) |

---

## 1. 功能简述

`FB_TcAlarm.Confirm()` 把 alarm 的确认状态切到 `Confirmed`。只有 alarm 创建时 `bWithConfirmation = TRUE` 才需要这步——它代表"操作员已经看到这条故障并处理了"。

调用时机：HMI 上操作员点确认按钮（边沿触发），或者业务上判定故障已被处置（如自动复位条件）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nTimeStamp : ULINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nTimeStamp` | `ULINT` | 确认事件时间戳：0 = 用当前系统时间；非 0 = 自 1601-01-01 UTC 起的 100ns 数 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

Confirm 是单纯的确认状态切换，不改变 Raised/Cleared 主状态。一条 alarm 完整生命周期是：Created → Raised → Cleared → Confirmed。前三步必经，第四步只在 `bWithConfirmation = TRUE` 时存在。

**典型用法**：HMI 上的「确认所有未确认」按钮可以走 `FB_TcEventLogger.ConfirmAllAlarms()` 批量确认所有报警；单点确认则用本方法。`nTimeStamp = 0` 用当前时间记录确认时刻——这个时间在事后审计里是"操作员响应时间"的关键指标。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 确认成功 | 继续业务 |
| `ADS_E_INVALIDSTATE` | alarm 不需要确认或已确认 | 通常无需处理 |
| `其他错误` | ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- `bWithConfirmation = FALSE` 的 alarm 不能 Confirm，否则返回 ADS_E_INVALIDSTATE。
- Confirm 不会自动 Clear，必须先 Clear 后 Confirm 或反过来都行，但两者都得做。
- HMI 集成时记得用边沿触发——按住按钮不松不要每周期都 Confirm。（工程经验补充）
- 操作员误确认无法撤销——审计要靠 EventLogger 的时间戳记录。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Confirm.xml`](../examples/P_Demo_Confirm.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

HMI 上操作员处理完故障后点"确认"按钮，关闭这条报警条目


确认时刻被自动写入 EventLogger 审计日志，事后能查"故障响应时长 = Confirm 时间 - Raise 时间"


不用 Confirm 直接 Clear → 失去操作员审计；走 `ConfirmAllAlarms` 批量 → 适合"全清"按钮，不适合单条精细确认


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.6.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050451339.html
- **相关**：`FB_TcAlarm.Raise`, `FB_TcAlarm.Clear`, `FB_TcEventLogger.ConfirmAlarms`, `FB_TcEventLogger.ConfirmAllAlarms`
