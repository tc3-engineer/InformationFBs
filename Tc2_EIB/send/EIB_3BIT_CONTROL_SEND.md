# EIB_3BIT_CONTROL_SEND

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EIB` |
| Library Version | `1.16.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Send` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187760395.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_EIB_3BIT_CONTROL_SEND.TcPOU`](../examples/P_Demo_EIB_3BIT_CONTROL_SEND.TcPOU) |

---

## 1. 功能简述

**发送 4-bit Controlled telegram**（DPT 3.xxx：调光控制 / 卷帘步进）：1 bit 控制 + 3 bit 范围。`bControl` 或 `byRange` **任一变化**就发；最小间隔 200 ms。

典型用于「按住按钮调光」「按住按钮收/放卷帘」——按下时持续发 (TRUE, n)，松开发 (X, 0)。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Group_Address : EIB_GROUP_ADDR;
    bControl      : BOOL;
    byRange       : BYTE;
    str_Rec       : EIB_REC;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Group_Address` | `EIB_GROUP_ADDR` | — | 目标组地址（必须在 KL6301 过滤器内） |
| `bControl` | `BOOL` | — | DPT 3.xxx 控制位（TRUE = 向上 / 增 / 开方向；FALSE = 向下 / 减 / 关方向） |
| `byRange` | `BYTE` | — | DPT 3.xxx 范围 / 步幅（0..7；0 = 停止，1..7 = 步长） |
| `str_Rec` | `EIB_REC` | — | 胶水结构，传 `KL6301.str_Data_Rec` |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError   : BOOL;
    iErrorID : EIB_ERROR_CODE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | 发送出错时置 TRUE |
| `iErrorID` | `EIB_ERROR_CODE` | 错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发方式**：只要 `bControl` 或 `byRange` 任一值发生变化，就立即编码并发送一帧 EIB telegram。PDF §4.2.5.7 明确指出，只在两个数据位中至少一个发生变化时才会下发——**值未变就不发**，不论 FB 被调用多少次。

**最小发送间隔 200 ms**（PDF 明确）：200 ms 内的连续变化会被合并到最后一次值；如果值在间隔内变化又回到旧值，则**不会**发送新帧（与 PDF "No new EIB telegram is sent if the value changes within the min. send time but falls back to the old, already sent value" 描述一致）。

**业务用法**：调光按钮按下时业务代码持续刷 (`bControl = TRUE`, `byRange = n`)，松开时刷 (`bControl = TRUE`, `byRange = 0`)。因为最小 200 ms 间隔，「按住按钮快速变化方向」会被库自动合并，符合调光器物理响应能力。

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

- **只在数据变化时发送**：写 `iData := iData` 不会触发 telegram。要强制重发用对应 `_EX` 版本的 Polling 模式。
- **最小发送间隔由库固化**：在间隔内的连续变化会被合并；中间值会丢。需要精细控制就用 `_EX` 版本。
- **`Group_Address` 不在 KL6301 过滤器内 → 静默丢弃**：写值看似成功但 EIB 网上没出帧。
- **必须 `KL6301.bReady = TRUE`** 才能开始发送；启动前调用本 FB 不会出错但也不会发。
- **与所有 EIB FB 在同一 PLC 任务**：跨任务 EIB_REC 状态不一致，发送丢失。
- **EIB 网络高负载时会触发 `WATCHDOG_ERROR_NO_SEND` (104)**：本帧未发出，失败的 group address 记录在 `KL6301.NotSendGroup` 局部变量供调试。（工程经验补充）
- **`byRange = 0` 是停止语义**：DPT 3.007 规范。
- **两个 IEC 入口任一变化就发**：业务上要「按住保持」语义就要持续刷 (TRUE, n) 而不是只触发一次。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_EIB_3BIT_CONTROL_SEND.TcPOU`](../examples/P_Demo_EIB_3BIT_CONTROL_SEND.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_EIB_3BIT_CONTROL_SEND
VAR
    fb       : EIB_3BIT_CONTROL_SEND;
    stEibRec : EIB_REC;
    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 15);
    bDir     : BOOL := TRUE;
    byR      : BYTE := 4;
END_VAR
fb(Group_Address := stGroup, bControl := bDir, byRange := byR, str_Rec := stEibRec);
```

## 7. 业务场景与实际价值

- **场景**：调光控制、卷帘步进等 4-bit 控制场景
- **价值**：DPT 3.xxx 标准发送
- **替代方案对比**：
  - `EIB_3BIT_CONTROL_SEND_EX`：周期 / OnChange / 主动答查
  - `EIB_ALL_DATA_TYPES_SEND`：手动拼字节
  - 本 FB：简单变化发送的标准选择

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf) §4.2.5.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187760395.html
- **相关**：`EIB_3BIT_CONTROL_SEND_EX`（§4.2.5.8）、`EIB_3BIT_CONTROL_REC`（接收端）
