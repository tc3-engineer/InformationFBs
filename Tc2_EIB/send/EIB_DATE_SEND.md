# EIB_DATE_SEND

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EIB` |
| Library Version | `1.16.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Send` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187783435.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_EIB_DATE_SEND.TcPOU`](../examples/P_Demo_EIB_DATE_SEND.TcPOU) |

---

## 1. 功能简述

**发送 3 字节日期 telegram**（DPT 11.001）。**首次调用 + 之后每 5 分钟**自动重发（PDF §4.2.5.25 描述："data are sent when the block is called for the first time and then every 5 minutes"）。

**`wYear` 自动减 2000**：传入 2025 → 库发 25。这是为了兼容业务代码直接传 4 位年。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Group_Address : EIB_GROUP_ADDR;
    wDay          : WORD;
    wMonth        : WORD;
    wYear         : WORD;
    str_Rec       : EIB_REC;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Group_Address` | `EIB_GROUP_ADDR` | — | 目标组地址 |
| `wDay` | `WORD` | — | 日，1..31 |
| `wMonth` | `WORD` | — | 月，1..12 |
| `wYear` | `WORD` | — | 年，0..99。**若传入值 > 2000，库会自动减 2000**——例 2025 → 实际发 25（PDF §4.2.5.25 表） |
| `str_Rec` | `EIB_REC` | — | 胶水结构 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError   : BOOL;
    iErrorID : EIB_ERROR_CODE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | 出错 |
| `iErrorID` | `EIB_ERROR_CODE` | 错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：首次调用立即发一次；之后每 5 分钟自动重发当前 (wDay/wMonth/wYear)。

**与变化无关**：本 FB 不检测数据变化——按固定 5 分钟节拍刷新。业务上要更频繁就用 `EIB_DATE_SEND_EX` 配 Polling 模式。

**年自动减 2000**：传入 > 2000 时库内部减 2000；< 2000 直接当作 0..99。因此 2025 → 实际发 25；24 → 实际发 24（不变）。

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

- **只在数据变化时发送**：写 `iData := iData` 不会触发 telegram。要强制重发用对应 `_EX` 版本的 Polling 模式。
- **最小发送间隔由库固化**：在间隔内的连续变化会被合并；中间值会丢。需要精细控制就用 `_EX` 版本。
- **`Group_Address` 不在 KL6301 过滤器内 → 静默丢弃**：写值看似成功但 EIB 网上没出帧。
- **必须 `KL6301.bReady = TRUE`** 才能开始发送；启动前调用本 FB 不会出错但也不会发。
- **与所有 EIB FB 在同一 PLC 任务**：跨任务 EIB_REC 状态不一致，发送丢失。
- **EIB 网络高负载时会触发 `WATCHDOG_ERROR_NO_SEND` (104)**：本帧未发出，失败的 group address 记录在 `KL6301.NotSendGroup` 局部变量供调试。（工程经验补充）
- **5 分钟固定节拍**：本 FB 不可调整。要更短间隔用 `_EX` 版本。
- **年字段自动减 2000**：传 2025 不会发 2025；库自动减成 25。业务可直接传 4 位年。
- **接收端 `EIB_DATE_REC` 也是 2 位年**：业务上做「未来 / 过去」判断要自己加世纪基。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_EIB_DATE_SEND.TcPOU`](../examples/P_Demo_EIB_DATE_SEND.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_EIB_DATE_SEND
VAR
    fb       : EIB_DATE_SEND;
    stEibRec : EIB_REC;
    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 0, NUMBER := 1);
END_VAR
fb(Group_Address := stGroup, wDay := 3, wMonth := 6, wYear := 2026,
   str_Rec := stEibRec);
```

## 7. 业务场景与实际价值

- **场景**：BMS 主时钟日期广播 / 设备日历同步
- **价值**：DPT 11 标准发送，无代码量
- **替代方案对比**：
  - `EIB_DATE_SEND_EX`：间隔可调 + read 响应
  - 本 FB：固定 5 分钟节拍

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf) §4.2.5.25
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187783435.html
- **相关**：`EIB_DATE_SEND_EX`（§4.2.5.26）、`EIB_DATE_REC`、`EIB_TIME_SEND`
