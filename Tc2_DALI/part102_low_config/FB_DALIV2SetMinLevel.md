# FB_DALIV2SetMinLevel

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
| Example | [`examples/P_Demo_FB_DALIV2SetMinLevel.TcPOU`](../examples/P_Demo_FB_DALIV2SetMinLevel.TcPOU) |

---

## 1. 功能简述

**设置镇流器 `MIN VALUE` 寄存器**——灯具最低非零亮度。任何 DAPC / Down 命令低于此值（但不为 0）都被钳到 `MIN VALUE`。0（关灯）不受此限。出厂默认 1（DALI 对数曲线最暗的非零档，约物理 0.1%）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart           : BOOL;
    nAddr            : BYTE;
    eAddrType        : E_DALIV2AddrType        := eDALIV2AddrTypeShort;
    eCommandPriority : E_DALIV2CommandPriority := eDALIV2CommandPriorityMiddle;
    nMinLevel        : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿 |
| `nAddr` | `BYTE` | — | 目标地址：单灯 short address 0..63，或组号 0..15，或 `eAddrType = Broadcast` 时忽略 |
| `eAddrType` | `E_DALIV2AddrType` | `eDALIV2AddrTypeShort` | 寻址类型：`eDALIV2AddrTypeShort`（单灯）/ `eDALIV2AddrTypeGroup`（组）/ `eDALIV2AddrTypeBroadcast`（全线广播） |
| `eCommandPriority` | `E_DALIV2CommandPriority` | `eDALIV2CommandPriorityMiddle` | 命令优先级：`High` / `Middle` / `Low`，决定本命令在 `FB_KL68x1Communication` 三优先级队列中的派发顺序 |
| `nMinLevel` | `BYTE` | — | 目标 `MIN VALUE` 寄存器值（1..254）。任何亮度命令低于 `nMinLevel`（但 > 0）都被钳到 `nMinLevel` |

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

**调用方式**：`bStart` 上升沿；写 DTR0 = `nMinLevel`，下发 `STORE THE DTR AS MIN LEVEL`。

**MIN VALUE 的作用**：（1）`DAPC` 0 < val < `nMinLevel` 被钳到 `nMinLevel`；（2）`RecallMinLevel` 命令亮度 = `nMinLevel`；（3）`Down` 命令到达 `nMinLevel` 后停（不会关到 0）。

**关灯特例**：`DAPC = 0` 一定关灯，不受 MIN 钳位。

**典型应用**：① 调光下限保护——LED 灯极低亮度时可能闪烁，把 MIN 设到 50 避免；② 不希望调光时关灯——把 MIN 设到 1 让 Down 停在最暗但不关；③ 应急照明法规要求最低亮度，把 MIN 设为法规规定值（如 50% 即 193）。

**典型陷阱**：① MIN > MAX 灯具行为未定义；② 设到 0 灯具拒绝；③ 实际 MIN 不能低于灯具`PHYSICAL MIN LEVEL`（灯具硬件极限），强制低于该值灯具自动钳到物理极限。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- MIN 必须 1..254，且 < MAX；0 灯具拒绝。
- DAPC = 0 仍是关灯，不被 MIN 钳位。
- 灯具硬件 `PHYSICAL MIN LEVEL` 优先——本 FB 设的值可能被灯具硬件钳到更高。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2SetMinLevel.TcPOU`](../examples/P_Demo_FB_DALIV2SetMinLevel.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：应急照明法规：要求最低亮度 50% (193)，把 MIN VALUE 设为 193——用户怎么调光都不低于 193。
- **价值**：灯具硬件层面强制亮度下限，运行时调光时不会跌穿。
- **替代方案对比**：**本 FB**：调光下限标准方法。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.3.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142797195.html
- **相关**：[`FB_DALIV2SetMaxLevel`](FB_DALIV2SetMaxLevel.md)、[`FB_DALIV2QueryMinLevel`](../part102_low_queries/FB_DALIV2QueryMinLevel.md)、[`FB_DALIV2QueryPhysicalMinLevel`](../part102_low_queries/FB_DALIV2QueryPhysicalMinLevel.md)
