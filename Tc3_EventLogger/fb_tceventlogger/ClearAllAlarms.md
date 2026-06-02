# ClearAllAlarms

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventLogger` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050746891.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_ClearAllAlarms.TcPOU`](../examples/P_Demo_ClearAllAlarms.TcPOU) |

---

## 1. 功能简述

`FB_TcEventLogger.ClearAllAlarms()` 是 `ClearAlarms()` 的便捷版本——无过滤器参数，对所有处于 Raised 状态的 alarm 调用 Clear。

适合"全部一次清空"场景，无需构造 `I_TcEventFilter` 实例。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nTimeStamp : ULINT := 0;
    bResetConfirmation : BOOL := FALSE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nTimeStamp` | `ULINT` | `0` | 清除事件时间戳：0 = 用当前系统时间 |
| `bResetConfirmation` | `BOOL` | `FALSE` | TRUE = 同时把确认状态置为 Reset |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

调用本方法时 EventLogger 即对所有处于 Raised 状态的 alarm 同步执行 Clear，状态从 Raised 切换到 Cleared。`bResetConfirmation := TRUE` 时同时把处于 `WaitForConfirmation` 状态的 alarm 确认状态置为 `Reset`。`nTimeStamp = 0` 用当前系统时间记录清除时刻——这个时间在事后审计里就是"批量清除动作"的发生时刻。

**与 ClearAlarms 的区别**：本方法少一个 ipFilter 参数，行为完全等价于 `ClearAlarms(ipFilter := 0)`。选哪个看代码可读性偏好——"全清"场景用 ClearAllAlarms 语义更直观；需要按规则筛选则用 ClearAlarms 加过滤器。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 全部 Raised alarm 已清除 | 继续业务 |
| `其他错误` | ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- `bResetConfirmation := TRUE` 绕过操作员审计——慎用。
- "全清"不可撤销：清完后操作员看不到原 Raised 状态。（工程经验补充）
- Clear 不等于 Remove——alarm 实例仍在 EventLogger 活动表里。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ClearAllAlarms.TcPOU`](../examples/P_Demo_ClearAllAlarms.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

设备维护模式下，运维人员先确认所有故障已物理处理，再用本方法"一键全清"准备复产


单方法调用 vs 自己写循环遍历——少错少漏


`ClearAlarms` 带过滤器 → 精细控制；本方法适合"全清"按钮


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.10.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050746891.html
- **相关**：`FB_TcEventLogger.ClearAlarms`, `FB_TcEventLogger.ConfirmAllAlarms`
