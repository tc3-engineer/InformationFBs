# EIB_ALL_DATA_TYPES_SEND

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EIB` |
| Library Version | `1.16.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Send` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187775755.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_EIB_ALL_DATA_TYPES_SEND.TcPOU`](../examples/P_Demo_EIB_ALL_DATA_TYPES_SEND.TcPOU) |

---

## 1. 功能简述

**发送任意类型 EIB telegram**：调用方提供 byte 数组 + 长度 + 优先级，库直接打包成 EIB telegram 下发。比所有专门类型 SEND FB 都灵活——支持非标 DPT、自定义协议、对 read 请求的回应。

**与 `EIB_*_SEND_EX` 的差异**：① 只支持 3 种模式（Manual / Polling / OnChange，**没有 OnChangePolling**）；② 可设 telegram 优先级（其它 _EX FB 固定 low）；③ 可主动发「对 read 请求的回应」（`bReadCommand = TRUE`）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart        : BOOL;
    iMode         : INT;
    CyclePolling  : TIME := t#100ms;
    DATA          : ARRAY [1..14] OF BYTE;
    EIB_Data_Len  : USINT := 1;
    PRIORITY      : EIB_PRIORITY := EIB_PRIORITY_LOW;
    MinSendTime   : TIME := t#1s;
    Group_Address : EIB_GROUP_ADDR;
    str_Rec       : EIB_REC;
    bReadCommand  : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bStart` | `BOOL` | — | Manual 模式上升沿触发；Polling/OnChange 电平 = 使能 |
| `iMode` | `INT` | — | **本 FB 只支持 3 种模式**（PDF §4.2.5.19）：0 = Manual / 1 = Polling / 2 = OnChange。**没有 OnChangePolling 模式**——与其它 _EX 不同 |
| `CyclePolling` | `TIME` | `t#100ms` | Polling 周期 |
| `DATA` | `ARRAY [1..14] OF BYTE` | — | EIB 原始负载，按 [1]..[N] 顺序填字节 |
| `EIB_Data_Len` | `USINT` | `1` | 负载长度。规则同 _REC 版本：≥ 1 byte 的负载填字节数 + 1；< 1 byte 的负载填 1 |
| `PRIORITY` | `EIB_PRIORITY` | — | telegram 优先级：`EIB_PRIORITY_LOW` (1) / `_HIGH` (2) / `_ALARM` (3)。详见 `EIB_PRIORITY` 枚举 |
| `MinSendTime` | `TIME` | `t#1s` | OnChange 模式最短间隔 |
| `Group_Address` | `EIB_GROUP_ADDR` | — | 目标组地址 |
| `str_Rec` | `EIB_REC` | — | 胶水结构 |
| `bReadCommand` | `BOOL` | — | TRUE = 本 telegram 是对 EIB READ COMMAND 的回应（不是普通数据帧） |

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

**模式**（PDF §4.2.5.19）：
- `iMode = 0` Manual：`bStart` 上升沿触发 1 次发送（Fig. 1）
- `iMode = 1` Polling：`bStart = TRUE` 期间按 `CyclePolling` 定时发，不论数据变化（Fig. 2）
- `iMode = 2` OnChange：`bStart = TRUE` 期间数据变化才发，`MinSendTime` 控制最短间隔（Fig. 3）

**`bReadCommand`**：设 TRUE 时本次发的 telegram 是「对其它设备 read 请求的回应」——必须在收到 EIB_READ_REQ 后短时间内发出。典型用法：用 `EIB_ALL_DATA_TYPES_REC` 监听 read 请求，看到 `bEIB_READ = TRUE` 就用本 FB 回应当前值。

**`PRIORITY`**：EIB 协议层优先级。`ALARM` 用于安全告警类 telegram（火警、安防）；`HIGH` 用于关键控制；`LOW` 默认。提高优先级在 EIB 总线繁忙时减少延迟。

**与 KL6301 依赖**：必须 `bReady = TRUE`；同 PLC 任务；`str_Rec` 传同一实例；`Group_Address` 必须在过滤器内。

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
- **没有 `bEnableReadReq` 输入**：与其它 _EX 不同——本 FB 不被动响应 read，而是主动用 `bReadCommand = TRUE` 发回应。
- **`EIB_Data_Len` 编码规则**：1 bit 数据填 1；2 byte 数据填 3。与 _REC 版本一致。
- **只有 3 种模式**：没有 OnChangePolling；要心跳 + 即时变化得自己用其它逻辑触发 `bStart`。
- **优先级 ALARM 应慎用**：高优先级 telegram 会抢占总线，可能导致低优先级帧被推迟。仅安全告警类用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_EIB_ALL_DATA_TYPES_SEND.TcPOU`](../examples/P_Demo_EIB_ALL_DATA_TYPES_SEND.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_EIB_ALL_DATA_TYPES_SEND
VAR
    fb         : EIB_ALL_DATA_TYPES_SEND;
    stEibRec   : EIB_REC;
    stGroup    : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 3, NUMBER := 1);
    arrPayload : ARRAY[1..14] OF BYTE;
END_VAR
fb(bStart := TRUE, iMode := 1, CyclePolling := T#1S, DATA := arrPayload,
   EIB_Data_Len := 7, PRIORITY := EIB_PRIORITY_LOW, MinSendTime := T#1S,
   Group_Address := stGroup, str_Rec := stEibRec, bReadCommand := FALSE);
```

## 7. 业务场景与实际价值

- **场景**：非标 DPT / 私有协议 / 答 read 请求 / 安全告警高优先级
- **价值**：唯一全能发送 FB
- **替代方案对比**：
  - 专用 _EX：DPT 标准类型时用，更清晰
  - 本 FB：非标类型 / 优先级控制 / answer read 时**必选**

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf) §4.2.5.19
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187775755.html
- **相关**：`EIB_ALL_DATA_TYPES_REC` / `_EX`（接收）、`EIB_PRIORITY`（同库 §4.3.1.2 枚举）、`EIB_READ_SEND`（发起 read 请求）
