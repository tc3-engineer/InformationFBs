# ConfirmAllAlarms

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventLogger` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050773003.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_ConfirmAllAlarms.TcPOU`](../examples/P_Demo_ConfirmAllAlarms.TcPOU) |

---

## 1. 功能简述

`FB_TcEventLogger.ConfirmAllAlarms()` 是 `ConfirmAlarms()` 的便捷版本——无过滤器参数，对所有处于 `WaitForConfirmation` 状态的 alarm 调用 Confirm。

适合"一键确认全部"操作。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nTimeStamp : ULINT := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nTimeStamp` | `ULINT` | `0` | 确认时间戳：0 = 用当前系统时间 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

调用时 EventLogger 即对所有处于 `WaitForConfirmation` 状态的 alarm 同步执行 Confirm，确认状态切换为 Confirmed。Raised/Cleared 主状态不受影响——Confirm 与主状态机正交。`nTimeStamp = 0` 用当前系统时间记录批量确认时刻，写入事件日志供事后审计。

**与 ConfirmAlarms 的区别**：本方法等价于 `ConfirmAlarms(ipFilter := 0)`，无过滤参数；用本方法 vs 显式传 0 看代码可读性偏好。已 Confirmed 的 alarm 再调用本方法不会变化（幂等操作）。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 全部 WaitForConfirmation alarm 已确认 | 继续业务 |
| `其他错误` | ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- "全确认"是审计敏感动作——HMI 端应加权限管控（管理员才能用）。（工程经验补充）
- 已 Confirmed 的 alarm 再 Confirm 不变化（幂等）。
- 批量确认时不记录"哪些 alarm 被确认"——审计追溯需要事后查 EventLogger 历史。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ConfirmAllAlarms.TcPOU`](../examples/P_Demo_ConfirmAllAlarms.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

管理员下班前"一键确认所有遗留报警"准备交班


单次调用完成批量确认；事件日志自动记录时刻供审计


`ConfirmAlarms` 带过滤器 → 精细控制；本方法适合"全确认"按钮


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.10.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050773003.html
- **相关**：`FB_TcEventLogger.ConfirmAlarms`, `FB_TcEventLogger.ClearAllAlarms`
