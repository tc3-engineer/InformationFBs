# FB_DALIV2SetShortAddress

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DALI` |
| Library Version | `2.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Part 102 / Low-Level / Configuration` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/index.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DALIV2SetShortAddress.TcPOU`](../examples/P_Demo_FB_DALIV2SetShortAddress.TcPOU) |

---

## 1. 功能简述

**直接设置镇流器短地址的命令**——给当前已寻址（用 random addressing 找到）的灯具写入一个新的 short address。`nShortAddress` 范围 0..63，写入后灯具立即按新短地址应答。

与 `FB_DALIV2ProgramShortAddress` 区别：本 FB 用于重新分配已有地址；后者用于初始寻址过程中写入第一个地址。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart           : BOOL;
    nAddr            : BYTE;
    eAddrType        : E_DALIV2AddrType := eDALIV2AddrTypeShort;
    nNewShortAddress : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿 |
| `nAddr` | `BYTE` | — | 目标地址：单灯 short address 0..63，或组号 0..15，或 `eAddrType = Broadcast` 时忽略 |
| `eAddrType` | `E_DALIV2AddrType` | `eDALIV2AddrTypeShort` | 寻址类型：`eDALIV2AddrTypeShort`（单灯）/ `eDALIV2AddrTypeGroup`（组）/ `eDALIV2AddrTypeBroadcast`（全线广播） |
| `nNewShortAddress` | `BYTE` | — | ⚠️ 待人工确认 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy    : BOOL;
    bError   : BOOL;
    nErrorId : UDINT;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 本 FB 接到 `bStart` 上升沿后置 TRUE；命令派发完且收到 DALI 响应（或超时）后回 FALSE |
| `bError` | `BOOL` | 执行错时置 TRUE；下次 `bStart` 上升沿自动复位 |
| `nErrorId` | `UDINT` | 错误号（命令专用）；详见 §4 错误码表与全库错误码（PDF §4.1.4） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stCommandBuffer : ST_DALIV2CommandBuffer;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `stCommandBuffer` | `ST_DALIV2CommandBuffer` | DALI 命令缓冲区结构；连到对应 KL68x1 通信 FB 的同名变量 |


## 3. 行为说明

**调用方式**：`bStart` 上升沿；本 FB 写 DTR0 = `nShortAddress` 经过特殊编码（DALI 协议要求`(nShortAddress << 1) | 1`），下发 `STORE THE DTR AS SHORT ADDRESS` 命令灯具更新短地址寄存器。

**寻址模式要求**：本命令在 random addressing 序列中（已 SELECT 一盏灯）才能精确指定哪盏灯改地址。在普通模式下用 `eAddrType := Short` + 旧短地址寻址也行，但风险是写后旧地址失效，下一次寻址要重新校验。

**EEPROM 写**：失电保护。

**典型陷阱**：① `nShortAddress > 63` 灯具忽略；② 设到已被其它灯占用的短地址 → 总线上两盏灯同地址，命令冲突，必须重新寻址；③ 改完后用 `FB_DALIV2QueryShortAddress` 验证。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- `nShortAddress` 必须 0..63，64..254 灯具忽略。
- 改地址前确认目标地址未被其它灯占用，否则总线冲突。
- 通常在 random addressing 序列中调用（已 SELECT 一盏灯）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2SetShortAddress.TcPOU`](../examples/P_Demo_FB_DALIV2SetShortAddress.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：DALI 寻址过程中给具体一盏灯写入设计文档规定的短地址（如把找到的某盏灯设为 short addr 5）。
- **价值**：替代厂家工具的 GUI 操作；PLC 程序里按设计表批量改地址。
- **替代方案对比**：1) `FB_DALIV2ProgramShortAddress`：寻址过程中分配新地址；2) `FB_DALIV2SwapShortAddress`：两灯地址交换；3) **本 FB**：直接覆盖单灯短地址。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.3.11
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142801803.html
- **相关**：[`FB_DALIV2QueryShortAddress`](../part102_low_special/FB_DALIV2QueryShortAddress.md)、[`FB_DALIV2ProgramShortAddress`](../part102_low_special/FB_DALIV2ProgramShortAddress.md)、[`FB_DALIV2SwapShortAddress`](../part102_addressing/FB_DALIV2SwapShortAddress.md)
