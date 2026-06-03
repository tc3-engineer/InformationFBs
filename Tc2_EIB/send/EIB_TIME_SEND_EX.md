# EIB_TIME_SEND_EX

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EIB` |
| Library Version | `1.16.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Send` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/16287833611.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_EIB_TIME_SEND_EX.TcPOU`](../examples/P_Demo_EIB_TIME_SEND_EX.TcPOU) |

---

## 1. 功能简述

**`EIB_TIME_SEND` 的扩展版本**：发送 3 字节时间 telegram（DPT 10.001），支持 4 种模式 + 答查。

**PDF 排版错警告（§4.2.5.29）**：PDF VAR_INPUT 代码块误抄了 `EIB_DATE_SEND_EX` 的 `wDay`/`wMonth`/`wYear`，但 §4.2.5.29 描述表（下页）写的是 `wHour`/`wMinute`/`wSecond`（时间字段）。**实际库**究竟用什么引脚名 PDF 自相矛盾；InfoSys 也不能明确这点。

⚠️ **本文档逐字保留 PDF VAR_INPUT 代码块**（按 CLAUDE.md 硬规则 #1 不许补全/篡改）。实际工程中可能需要：① 查 .library 实际定义；② 用 `EIB_ALL_DATA_TYPES_SEND` 配置 3 byte 时间负载替代。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart         : BOOL;
    iMode          : INT;
    CyclePolling   : TIME := t#500ms;
    MinSendTime    : TIME := t#1s;
    Group_Address  : EIB_GROUP_ADDR;
    wDay           : WORD;
    wMonth         : WORD;
    wYear          : WORD;
    str_Rec        : EIB_REC;
    bEnableReadReq : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bStart` | `BOOL` | — | 触发 |
| `iMode` | `INT` | — | 0/1/2/3 模式 |
| `CyclePolling` | `TIME` | `t#500ms` | Polling 周期 |
| `MinSendTime` | `TIME` | `t#1s` | OnChange 最短间隔 |
| `Group_Address` | `EIB_GROUP_ADDR` | — | 目标组地址 |
| `wDay` | `WORD` | — | **PDF 排版错——本 FB 名为 TIME_SEND_EX 但 VAR_INPUT 误抄了 DATE_SEND_EX 的 wDay/wMonth/wYear**。详见 §3 行为说明。按 PDF 逐字保留 |
| `wMonth` | `WORD` | — | （同上 PDF 排版错） |
| `wYear` | `WORD` | — | （同上 PDF 排版错） |
| `str_Rec` | `EIB_REC` | — | 胶水结构 |
| `bEnableReadReq` | `BOOL` | — | 使能 read 响应 |

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
| `bBusy` | `BOOL` | 忙 |
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

**⚠️ PDF 排版错澄清（§4.2.5.29）**：PDF 第 67 页 VAR_INPUT 代码块列出 `wDay : WORD; wMonth : WORD; wYear : WORD;`（看起来像日期参数）；第 68 页表格紧接着列出 `wHour / wMinute / wSecond`（时间参数）。本 FB 名字 `TIME_SEND_EX` 暗示是时间——但 VAR_INPUT 代码块逐字是日期字段。**正确语义无法仅凭 PDF 判定**——InfoSys 该 topic 页内容与 PDF 完全一致（同样的 PDF 排版错被搬运），未给出额外澄清。

**工程建议**：① 若要可靠地用本 FB，先用 XAE 打开实际 .library 查 VAR_INPUT 实际命名；② 或退回用 `EIB_TIME_SEND`（节拍固定但定义清晰）；③ 或用 `EIB_ALL_DATA_TYPES_SEND` 手动构造 3 byte DPT 10.001 负载。

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
- ⚠️ **PDF + InfoSys VAR_INPUT 引脚名为 `wDay/wMonth/wYear` 但 FB 名是 TIME_SEND_EX**：PDF 排版错，实际库定义未确认。建议先用 `EIB_TIME_SEND`（固定 5 分钟节拍但定义清晰）。
- **实际语义需以 XAE 打开 .library 实查 VAR_INPUT 为准**——本文档逐字保留 PDF 写法。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_EIB_TIME_SEND_EX.TcPOU`](../examples/P_Demo_EIB_TIME_SEND_EX.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_EIB_TIME_SEND_EX
VAR
    fb       : EIB_TIME_SEND_EX;
    stEibRec : EIB_REC;
    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 0, NUMBER := 2);
END_VAR
// ⚠️ PDF 排版错：VAR_INPUT 是 wDay/wMonth/wYear 但 FB 名是 TIME_SEND_EX
fb(bStart := TRUE, iMode := 1, CyclePolling := T#1M, MinSendTime := T#500MS,
   Group_Address := stGroup, wDay := 14, wMonth := 30, wYear := 0,
   str_Rec := stEibRec, bEnableReadReq := TRUE);
```

## 7. 业务场景与实际价值

- **场景**：时间灵活间隔广播；但 PDF 排版错需 XAE 实查
- **价值**：灵活间隔；建议优先 EIB_TIME_SEND
- **替代方案对比**：
  - `EIB_TIME_SEND`：5 分钟节拍但定义清晰，建议优先
  - `EIB_ALL_DATA_TYPES_SEND`：手构 3 byte DPT 10 负载，完全可控
  - 本 _EX：仅在确认 .library 实际语义后才用

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf) §4.2.5.29
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/16287833611.html
- **相关**：`EIB_TIME_SEND`、`EIB_TIME_REC`、`EIB_DATE_SEND_EX`
