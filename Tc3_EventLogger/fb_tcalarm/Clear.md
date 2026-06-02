# Clear

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcAlarm` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050438027.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcAlarm_Clear.TcPOU`](../examples/P_Demo_FB_TcAlarm_Clear.TcPOU) |

---

## 1. 功能简述

`FB_TcAlarm.Clear()` 把 alarm 状态从 "Raised" 切换到 "Not Raised"（已清除）。如果创建时 `bWithConfirmation = TRUE`，确认状态保持 `WaitForConfirmation` 不变，需要后续 `Confirm()` 调用才完整结束。

`bRemove := TRUE` 时除了清除状态外，还把 alarm 实例从 EventLogger 的活动表中移除（释放槽位）；`bRemove := FALSE` 保留实例以便下次 Raise 复用。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nTimeStamp : ULINT;
    bResetConfirmation : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nTimeStamp` | `ULINT` | 事件时间戳：0 = 用当前系统时间；非 0 = 自 1601-01-01 UTC 起的 100ns 数 |
| `bResetConfirmation` | `BOOL` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

调用时机：故障信号**下降沿**——前一周期 TRUE、本周期 FALSE。Clear 立即同步切换状态。如果当前并不在 Raised 状态（已经是 Cleared），调用返回 `ADS_E_INVALIDSTATE`，状态不变。

**`bRemove` 取舍**：常驻设备故障建议 `FALSE`（实例长期复用，避免反复 Create/Remove 抖动）；动态生成的临时故障（如一次性配方告警）建议 `TRUE` 让 EventLogger 回收槽位。

Clear 不会自动 Confirm。要让 alarm 完整走完生命周期，confirmation 必须显式调 `Confirm()`，或在工程里关掉 `bWithConfirmation`。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 状态成功切换到 Cleared | 若 bWithConfirmation = TRUE 等待 Confirm() |
| `ADS_E_INVALIDSTATE` | alarm 不在 Raised 状态 | 通常表示边沿检测漏 |
| `其他错误` | ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- Clear 不等于 Confirm：若 bWithConfirmation = TRUE，alarm 仍处于 WaitForConfirmation。
- `bRemove := TRUE` 后再 Raise 必须重新 Create()，否则会失败。（工程经验补充）
- 已 Cleared 状态再 Clear 返回 ADS_E_INVALIDSTATE，不是错误。
- 常驻报警建议 `bRemove := FALSE`，避免反复 Create 引起的抖动。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcAlarm_Clear.TcPOU`](../examples/P_Demo_FB_TcAlarm_Clear.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

电机过载故障消失后清除报警（电流降回阈值以下的下降沿）


下降沿一次调用完成清除 + 日志记录，免去手写状态机


不 Clear 让 alarm 保持 Raised → HMI 永远显示故障，操作员困惑；改用 Remove 一步直接消失 → 失去"故障已恢复但需确认"的中间状态


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.6.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050438027.html
- **相关**：`FB_TcAlarm.Raise`, `FB_TcAlarm.Confirm`, `FB_TcEventLogger.ClearAlarms`
