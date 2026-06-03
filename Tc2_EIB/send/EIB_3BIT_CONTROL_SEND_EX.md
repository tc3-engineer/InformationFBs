# EIB_3BIT_CONTROL_SEND_EX

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EIB` |
| Library Version | `1.16.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Send` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/15012536971.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_EIB_3BIT_CONTROL_SEND_EX.TcPOU`](../examples/P_Demo_EIB_3BIT_CONTROL_SEND_EX.TcPOU) |

---

## 1. 功能简述

`EIB_3BIT_CONTROL_SEND` 的扩展版本：发送 DPT 3.xxx 4-bit Controlled telegram，支持 Manual / Polling / OnChange / OnChangePolling 4 种模式。适合场景灯的状态心跳（避免 BMS 失同步）+ 响应 BMS 主动查值。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart         : BOOL;
    iMode          : INT;
    CyclePolling   : TIME := t#500ms;
    MinSendTime    : TIME := t#1s;
    Group_Address  : EIB_GROUP_ADDR;
    bControl       : BOOL;
    byRange        : BYTE;
    str_Rec        : EIB_REC;
    bEnableReadReq : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bStart` | `BOOL` | — | FB 触发输入；模式 0 用上升沿，模式 1/2/3 用电平 |
| `iMode` | `INT` | — | 0/1/2/3 = Manual/Polling/OnChange/OnChangePolling，见 §3 |
| `CyclePolling` | `TIME` | `t#500ms` | Polling 周期，下限 200 ms |
| `MinSendTime` | `TIME` | `t#1s` | OnChange 最短间隔，下限 200 ms |
| `Group_Address` | `EIB_GROUP_ADDR` | — | 目标组地址 |
| `bControl` | `BOOL` | — | 1 bit 控制位 |
| `byRange` | `BYTE` | — | 3 bit 范围（0..7） |
| `str_Rec` | `EIB_REC` | — | 胶水结构，传 `KL6301.str_Data_Rec` |
| `bEnableReadReq` | `BOOL` | — | 使能响应 read_group_req |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy    : BOOL;
    bError   : BOOL;
    iErrorID : EIB_ERROR_CODE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 发送 / 等待中 |
| `bError` | `BOOL` | 出错 |
| `iErrorID` | `EIB_ERROR_CODE` | 错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

**`iMode` 模式（_EX 系列）**：
- `0` = Manual：`bStart` 上升沿触发 1 次发送，`bBusy` 期间忽略后续触发
- `1` = Polling：`bStart = TRUE` 期间按 `CyclePolling` 周期定时发送（不论数据变没变）
- `2` = OnChange：`bStart = TRUE` 期间数据变化才发送，`MinSendTime` 控制最短发送间隔（≥ 200 ms）
- `3` = OnChangePolling：`bStart = TRUE` 期间按 `CyclePolling` 周期定时发送 + 数据变化时立即发送，`MinSendTime` 仍控制最短间隔

**触发流程**：

1. `bStart` 上升沿 → 根据 `iMode` 选定的发送策略开始执行；`bBusy := TRUE` 直到发送完成或失败
2. 发送成功 → `bBusy := FALSE`，`bError := FALSE`
3. 发送失败 → `bBusy := FALSE`，`bError := TRUE`，`iErrorID` 给错误码

**`bEnableReadReq`**：使能响应 EIB Read 请求。设 TRUE 时，若 EIB 网内有别人对本 `Group_Address` 发 Read_Group_Req，本 FB 会自动回应当前数据值；设 FALSE 不响应。

**`CyclePolling` 最小值 200 ms**：低于 200 ms 库强制按 200 ms 处理。

**`MinSendTime` 最小值 200 ms**：同上。OnChange 模式下避免高频抖动 telegram 刷屏。

**与 KL6301 依赖**：必须 `KL6301.bReady = TRUE`；同 PLC 任务；`str_Rec` 传 `KL6301.str_Data_Rec` 同一实例；`Group_Address` 必须在过滤器内。

## 4. 错误码 / 返回值

| 枚举值 / 16# | 含义 | 常见原因 |
|---|---|---|
| `NO_EIB_ERROR` / 0 | 无错 | — |
| `WRONG_EIB_DATA_LEN` / 20 | 发送数据长度异常 | 库内部检测，正常使用不应触发 |
| `ERROR_EIB_NO_ACK` / 16#0BBB | EIB 端没有收到目标设备的 ACK | 目标组地址在 EIB 网络上无任何 ACK 设备 / 总线段不通 |
| `WATCHDOG_ERROR_NO_SEND` / 104 | 看门狗判定本帧未发出 | KL6301 长时间忙、被低优先级帧拖死；失败的 group address 写入 `KL6301.NotSendGroup` 局部变量供调试 |
| `KL6301_TP_TOGGLE_ERROR` / 30 | KL6301 1 秒未响应 toggle | KL6301 已死锁；触发 `KL6301.bActivate := FALSE` 再 TRUE 重参数化 |
| `ERROR_EIB_NO_COM_TO_TP` / 16#FAFB | EIB 物理层失联 | KL6301 EIB 侧硬件 / 电源故障 |
| `ERROR_TP_*` / 16#0FCC..16#87CC | KL6301 物理层各类错 | 见 §4 错误码完整表，多为现场布线 / 干扰问题 |

参见 `EIB_ERROR_CODE` 枚举完整定义（PDF §4.3.1.1）。


## 5. 使用注意 / 常见坑

- **`iMode = 1` 时 `CyclePolling` 起作用**：周期发送即使数据不变。注意带宽占用——多 _EX 实例同时 Polling 会冲爆 EIB 网。
- **`iMode = 2` OnChange + `MinSendTime` 抑频**：避免抖动数据轰炸 EIB 网。MinSendTime 内变化会被合并。
- **`CyclePolling` 与 `MinSendTime` 下限均为 200 ms**：库强制；填更小值无效。
- **`bBusy` 期间忽略新触发**：上一次发送未完成时，`bStart` 重新拉高不会「排队」，只能等 `bBusy` 回 FALSE。
- **`bEnableReadReq` 使能 read 响应**：BMS 监控软件经常用 Read_Group_Req 主动查值；不使能就查不到。
- **与 KL6301 在同一 PLC 任务**：跨任务静默丢失。
- **iMode 改变需先把 `bStart` 拉低**：上升沿才采样 iMode；运行中改 iMode 不会立即生效。（工程经验补充）
- **与对应非 _EX 版本不可对同一 Group_Address 共用**：会冲突；选一种用。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_EIB_3BIT_CONTROL_SEND_EX.TcPOU`](../examples/P_Demo_EIB_3BIT_CONTROL_SEND_EX.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_EIB_3BIT_CONTROL_SEND_EX
VAR
    fb       : EIB_3BIT_CONTROL_SEND_EX;
    stEibRec : EIB_REC;
    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 15);
END_VAR
fb(bStart := TRUE, iMode := 3, CyclePolling := T#10S, MinSendTime := T#500MS,
   Group_Address := stGroup, bControl := TRUE, byRange := 4,
   str_Rec := stEibRec, bEnableReadReq := TRUE);
```

## 7. 业务场景与实际价值

- **场景**：BMS 调光场景灯，心跳 + 即时变化 + 答查
- **价值**：BMS 调光工程首选
- **替代方案对比**：
  - 非 _EX：只变化发
  - 本 _EX：复杂场景首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf) §4.2.5.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/15012536971.html
- **相关**：`EIB_3BIT_CONTROL_SEND`（§4.2.5.7）、`EIB_3BIT_CONTROL_REC`
