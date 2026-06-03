# EIB_4OCTET_FLOAT_SEND

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EIB` |
| Library Version | `1.16.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Send` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187761931.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_EIB_4OCTET_FLOAT_SEND.TcPOU`](../examples/P_Demo_EIB_4OCTET_FLOAT_SEND.TcPOU) |

---

## 1. 功能简述

**发送 DPT 14.xxx (4-byte IEEE 754 float) telegram**：把 IEC `REAL` 值经库编码成 EIB 标准格式，发送到指定 `Group_Address`。**只在 `rData` 值变化时下发**——周期重发要用 `EIB_4OCTET_FLOAT_SEND_EX`。

**最小发送间隔由库内部固化为 1 秒**：在该间隔内的连续变化会被合并到最后一次值。如果值在间隔内变化又回到旧值，**不会**发新帧（PDF §4.2.5.x 明确）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Group_Address : EIB_GROUP_ADDR;
    rData         : REAL;
    str_Rec       : EIB_REC;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Group_Address` | `EIB_GROUP_ADDR` | — | **目标 EIB 组地址**（数据发送到的地址；必须在 KL6301 过滤器内） |
| `rData` | `REAL` | — | IEC `REAL`（IEEE 754 single），库直接编码为 EIB 4-byte float（DPT 14.xxx） |
| `str_Rec` | `EIB_REC` | — | 收发胶水结构，必须传 `KL6301.str_Data_Rec` 同一个实例 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError   : BOOL;
    iErrorID : EIB_ERROR_CODE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | 发送出错时置 TRUE；错误码在 `iErrorID` |
| `iErrorID` | `EIB_ERROR_CODE` | 错误码，详见 `EIB_ERROR_CODE` 枚举 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发方式**：每周期调用本 FB；**只要数据值（rData）发生变化**，库就把新值编码成 EIB telegram 并下发到 EIB 总线。**初次调用**也会发一次（首次值通过）。

**最小发送间隔**：本 FB 不带 `MinSendTime` 引脚，但库内部固化了 1 秒（PDF §4.2.5.x 描述）。在间隔内连续变化会被合并——最后一次值在间隔到期后被发出（PDF "No new EIB telegram is sent if the value changes within the min. send time but falls back to the old, already sent value within the min. send time" 描述：变化又回到旧值则不发新帧）。

**与 KL6301 依赖**：必须先有 `KL6301.bReady = TRUE`；本 FB 与 KL6301 必须**同一 PLC 任务**；`str_Rec` 必须传 KL6301 的 `str_Data_Rec` 同一个实例。

**`Group_Address` 必须出现在 KL6301 过滤器内**——否则 KL6301 不 ACK 也不下发，发送看似「成功」但 EIB 物理层根本没出帧。

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

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_EIB_4OCTET_FLOAT_SEND.TcPOU`](../examples/P_Demo_EIB_4OCTET_FLOAT_SEND.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_EIB_4OCTET_FLOAT_SEND
VAR
    fb       : EIB_4OCTET_FLOAT_SEND;
    stEibRec : EIB_REC;
    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 4, NUMBER := 13);
    data     : REAL := REAL#0.0;
END_VAR
fb(Group_Address := stGroup, rData := data, str_Rec := stEibRec);
```

## 7. 业务场景与实际价值

- **场景**：PLC 瞬时功率 (W)发送到 BMS
- **价值**：DPT DPT 14.xxx 标准发送方式
- **替代方案对比**：
  - `EIB_4OCTET_FLOAT_SEND_EX`：周期发 + read 响应
  - `EIB_ALL_DATA_TYPES_SEND`：raw byte 模式
  - 本 FB：简单变化发送的标准选择

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf) §4.2.5.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187761931.html
- **相关**：`EIB_4OCTET_FLOAT_SEND_EX`（同库 §4.2.5.10）、对应接收 FB
