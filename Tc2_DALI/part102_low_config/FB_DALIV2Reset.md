# FB_DALIV2Reset

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
| Example | [`examples/P_Demo_FB_DALIV2Reset.TcPOU`](../examples/P_Demo_FB_DALIV2Reset.TcPOU) |

---

## 1. 功能简述

**镇流器复位到出厂默认值的命令**——把目标镇流器的全部配置寄存器（亮度、`FADE TIME`、`FADE RATE`、`MIN/MAX VALUE`、`POWER ON LEVEL`、组归属、场景值、短地址等）复位到 DALI 规范的出厂默认。

**危险操作**——慎用；通常仅在工程上线初次配置前 / 灯具配置完全混乱需重新规划时使用。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart           : BOOL;
    nAddr            : BYTE;
    eAddrType        : E_DALIV2AddrType        := eDALIV2AddrTypeShort;
    eCommandPriority : E_DALIV2CommandPriority := eDALIV2CommandPriorityMiddle;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿 |
| `nAddr` | `BYTE` | — | 目标地址：单灯 short address 0..63，或组号 0..15，或 `eAddrType = Broadcast` 时忽略 |
| `eAddrType` | `E_DALIV2AddrType` | `eDALIV2AddrTypeShort` | 寻址类型：`eDALIV2AddrTypeShort`（单灯）/ `eDALIV2AddrTypeGroup`（组）/ `eDALIV2AddrTypeBroadcast`（全线广播） |
| `eCommandPriority` | `E_DALIV2CommandPriority` | `eDALIV2CommandPriorityMiddle` | 命令优先级：`High` / `Middle` / `Low`，决定本命令在 `FB_KL68x1Communication` 三优先级队列中的派发顺序 |

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

**调用方式**：`bStart` 上升沿；本 FB 下发两次 `RESET` 命令（DALI 协议要求双指令防误触发），灯具收到后用约 300 ms 完成 EEPROM 清空与重写。命令派发完 `bBusy` 回 FALSE，但灯具复位过程仍可能持续到调用结束后 300+ ms。

**复位的内容**：（按 DALI 规范 IEC 62386 Part 102）`ACTUAL DIM LEVEL` 复位为 `POWER ON LEVEL` （出厂 254）；`FADE TIME = 0`、`FADE RATE = 7`、`MIN VALUE = 1`、`MAX VALUE = 254`、`POWER ON LEVEL = 254`、`SYSTEM FAILURE LEVEL = 254`、组归属 = 0（不属任何组）、场景 0..15 全为 `MASK`、`RANDOM ADDRESS = 0xFFFFFF`。**短地址（`SHORT ADDRESS`）也被清成 `MASK`（即 255 = 无短地址）**。

**短地址清空后的影响**：本 FB 用 `eAddrType := Short` + `nAddr := N` 调用后，灯具短地址被清——再用同样 `nAddr := N` 找不到这盏灯了！需要重新做寻址（用 `FB_DALIV2AddressingRandomAddressing`）。

**用 Broadcast 复位整网**：`eAddrType := Broadcast` 一次复位所有灯具——工程上线第一步常用法。

**典型陷阱**：① Reset 单灯后短地址也被清，找不到了；② Broadcast Reset 会清光所有灯的配置，包括组归属——工程上线前用没事，运行时绝对不要广播 Reset；③ Reset 命令期间灯具亮度可能短暂跳到 254（`POWER ON LEVEL` 默认值），用户可能感知到闪烁。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- **复位会清掉短地址**——单灯复位后这盏灯失联，需要重新寻址。
- **Broadcast Reset 清光所有配置**——运行时绝对不要广播 Reset。
- 复位期间灯具亮度可能短暂跳变（`POWER ON LEVEL` 默认 254），用户感知闪烁。
- EEPROM 写次数高（一次复位写多个寄存器），不要频繁调用。
- 复位后立即下发其它命令前应等 ~500 ms 让灯具完成 EEPROM 操作。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2Reset.TcPOU`](../examples/P_Demo_FB_DALIV2Reset.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：DALI 工程初始装机第一步：上线前对整条 DALI 线广播一次 Reset，把所有镇流器复位到出厂状态，然后按设计文档统一寻址 / 分组 / 配置 Fade 参数。也用于灯具配置完全混乱（被多人乱改）需要重新规划的场景。
- **价值**：替代手动用厂家工具一盏盏复位；广播一次复位整网，省时省事。
- **替代方案对比**：1) 手动用厂家工具：太慢；2) 单独发各个 SetXxx 命令把每个寄存器写回默认值：相当于重写本 FB，效率低；3) **本 FB**：标准复位接口。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.3.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142791051.html
- **相关**：[`FB_DALIV2AddressingRandomAddressing`](../part102_addressing/FB_DALIV2AddressingRandomAddressing.md)（复位后重新寻址）、[`FB_DALIV2QueryResetState`](../part102_low_queries/FB_DALIV2QueryResetState.md)（查询是否处于复位状态）、[`FB_DALIV2SetSettings`](../part102_settings/FB_DALIV2SetSettings.md)（高层批量配置）
