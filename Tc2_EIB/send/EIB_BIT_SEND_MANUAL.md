# EIB_BIT_SEND_MANUAL

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EIB` |
| Library Version | `1.16.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Send` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187781899.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_EIB_BIT_SEND_MANUAL.TcPOU`](../examples/P_Demo_EIB_BIT_SEND_MANUAL.TcPOU) |

---

## 1. 功能简述

**手动触发 1-bit 发送**：与 `EIB_BIT_SEND` 区别——本 FB 必须 `bSend` 上升沿才触发，**不论 `bData` 是否变化**都强制下发当前值。

用于「心跳」或「刷新」场景：业务上想周期重发开关状态以防 BMS 失同步、或想在 BMS 失联后强制重新推送当前状态。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Group_Address : EIB_GROUP_ADDR;
    bSend         : BOOL;
    bData         : BOOL;
    str_Rec       : EIB_REC;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Group_Address` | `EIB_GROUP_ADDR` | — | 目标组地址 |
| `bSend` | `BOOL` | — | 上升沿触发一次发送（即使 `bData` 没变化也强制下发） |
| `bData` | `BOOL` | — | 1 bit 数据值 |
| `str_Rec` | `EIB_REC` | — | 胶水结构 |

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
| `bBusy` | `BOOL` | FB 活动期间为 TRUE，发送完成 / 失败后回 FALSE |
| `bError` | `BOOL` | 出错 |
| `iErrorID` | `EIB_ERROR_CODE` | 错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：仅 `bSend` 上升沿触发一次发送，**不看 `bData` 是否变化**——与 `EIB_BIT_SEND`（变化触发）相反。

**状态机**：`bSend ↑` → `bBusy := TRUE` 发送 → 完成或失败 `bBusy := FALSE`。完成时 `bError := FALSE`；失败时 `bError := TRUE`、`iErrorID` 给错误码。

**与 KL6301 依赖**：必须 `bReady = TRUE`；同 PLC 任务；`str_Rec` 传同一实例；`Group_Address` 必须在过滤器内。

**vs `EIB_BIT_SEND`**：BIT_SEND 自动检测 `bData` 变化触发；MANUAL 必须显式 `bSend` 上升沿。MANUAL 可重发同一值。

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

- **只在数据变化时发送**：写 `iData := iData` 不会触发 telegram。要强制重发用对应 `_EX` 版本的 Polling 模式。
- **最小发送间隔由库固化**：在间隔内的连续变化会被合并；中间值会丢。需要精细控制就用 `_EX` 版本。
- **`Group_Address` 不在 KL6301 过滤器内 → 静默丢弃**：写值看似成功但 EIB 网上没出帧。
- **必须 `KL6301.bReady = TRUE`** 才能开始发送；启动前调用本 FB 不会出错但也不会发。
- **与所有 EIB FB 在同一 PLC 任务**：跨任务 EIB_REC 状态不一致，发送丢失。
- **EIB 网络高负载时会触发 `WATCHDOG_ERROR_NO_SEND` (104)**：本帧未发出，失败的 group address 记录在 `KL6301.NotSendGroup` 局部变量供调试。（工程经验补充）
- **`bSend` 是手动触发**：业务逻辑里要自己定时拉高 `bSend` 一个 PLC 周期触发重发。
- **可重发同一值**：与 `EIB_BIT_SEND` 不同——MANUAL 能强制重发，用于心跳。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_EIB_BIT_SEND_MANUAL.TcPOU`](../examples/P_Demo_EIB_BIT_SEND_MANUAL.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_EIB_BIT_SEND_MANUAL
VAR
    fb       : EIB_BIT_SEND_MANUAL;
    stEibRec : EIB_REC;
    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 1, NUMBER := 55);
    bSend    : BOOL;
    bData    : BOOL := TRUE;
END_VAR
fb(Group_Address := stGroup, bSend := bSend, bData := bData, str_Rec := stEibRec);
```

## 7. 业务场景与实际价值

- **场景**：BMS 心跳重发 / 失同步保险 / 强制刷新当前状态
- **价值**：唯一支持强制重发同一值的 1-bit FB
- **替代方案对比**：
  - `EIB_BIT_SEND`：仅变化发，做不到强制重发
  - `EIB_BIT_SEND_EX` (Polling 模式)：能周期发，但触发不那么显式
  - 本 FB：心跳重发的清晰选择

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf) §4.2.5.24
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187781899.html
- **相关**：`EIB_BIT_SEND`、`EIB_BIT_SEND_EX`、`EIB_BIT_REC`
