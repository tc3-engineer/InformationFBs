# FB_DALIV2SetMaxLevel

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
| Example | [`examples/P_Demo_FB_DALIV2SetMaxLevel.TcPOU`](../examples/P_Demo_FB_DALIV2SetMaxLevel.TcPOU) |

---

## 1. 功能简述

**设置镇流器 `MAX VALUE` 寄存器**——灯具内部所有亮度命令的上限值，任何 DAPC / Recall / Up 超过此值都被钳位。出厂默认 254（即 100%）。工程上常调低用于保护灯具寿命 / 满足能耗法规。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart           : BOOL;
    nAddr            : BYTE;
    eAddrType        : E_DALIV2AddrType        := eDALIV2AddrTypeShort;
    eCommandPriority : E_DALIV2CommandPriority := eDALIV2CommandPriorityMiddle;
    nMaxLevel        : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿 |
| `nAddr` | `BYTE` | — | 目标地址：单灯 short address 0..63，或组号 0..15，或 `eAddrType = Broadcast` 时忽略 |
| `eAddrType` | `E_DALIV2AddrType` | `eDALIV2AddrTypeShort` | 寻址类型：`eDALIV2AddrTypeShort`（单灯）/ `eDALIV2AddrTypeGroup`（组）/ `eDALIV2AddrTypeBroadcast`（全线广播） |
| `eCommandPriority` | `E_DALIV2CommandPriority` | `eDALIV2CommandPriorityMiddle` | 命令优先级：`High` / `Middle` / `Low`，决定本命令在 `FB_KL68x1Communication` 三优先级队列中的派发顺序 |
| `nMaxLevel` | `BYTE` | — | 目标 `MAX VALUE` 寄存器值（1..254）。灯具内部任何亮度命令都会被这个上限钳位 |

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

**调用方式**：`bStart` 上升沿；本 FB 写 DTR0 = `nMaxLevel`，下发 `STORE THE DTR AS MAX LEVEL` 把 DTR0 写入灯具 EEPROM。

**MAX VALUE 的作用**：（1）`DAPC > nMaxLevel` 被钳到 nMaxLevel；（2）`RecallMaxLevel` 命令亮度等于 `nMaxLevel`；（3）`Up` 命令到达 `nMaxLevel` 后停。

**典型应用**：① 路灯调光保护：把 MAX 设为 200（约 80%）延长 LED 寿命；② 能耗法规：办公室白天 MAX = 200 节能；③ 用户调光体验：把 MAX 设到 200 而非 254，让全亮按钮不至于刺眼。

**与 `MIN VALUE` 配套**：MAX 必须 > MIN；否则灯具行为未定义。

**典型陷阱**：① MAX 设到 < `nLampPhysicalMinLevel`（灯具物理最小亮度）→ 命令无效；② MAX 设过低用户感觉不够亮投诉。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- MAX 必须 > MIN，否则灯具行为未定义。
- MAX 设过低用户感觉不够亮——调光范围与体验权衡。
- 改完用 `FB_DALIV2QueryMaxLevel` 验证。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2SetMaxLevel.TcPOU`](../examples/P_Demo_FB_DALIV2SetMaxLevel.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：路灯节能改造：把 MAX VALUE 从 254 调到 200（约 80%）保护 LED 延长寿命。
- **价值**：灯具硬件层面强制亮度上限，避免应用层错误命令把灯调过亮。
- **替代方案对比**：1) 应用层校验亮度命令：可行但需所有命令点都检查；2) **本 FB**：灯具内部硬钳位，更可靠。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.3.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142795659.html
- **相关**：[`FB_DALIV2SetMinLevel`](FB_DALIV2SetMinLevel.md)、[`FB_DALIV2QueryMaxLevel`](../part102_low_queries/FB_DALIV2QueryMaxLevel.md)、[`FB_DALIV2RecallMaxLevel`](../part102_low_power/FB_DALIV2RecallMaxLevel.md)
