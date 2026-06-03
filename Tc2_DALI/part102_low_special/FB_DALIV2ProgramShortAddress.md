# FB_DALIV2ProgramShortAddress

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DALI` |
| Library Version | `2.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Part 102 / Low-Level / Special` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/index.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DALIV2ProgramShortAddress.TcPOU`](../examples/P_Demo_FB_DALIV2ProgramShortAddress.TcPOU) |

---

## 1. 功能简述

**寻址过程中给当前已选中的灯写入短地址**——DALI 寻址流程中通过 `SearchAddr` 二分查找到一盏灯后，用本 FB 给它写入短地址。`nShortAddress` 经过 DALI 协议特殊编码（`(addr<<1)|1`）。

**与 `FB_DALIV2SetShortAddress` 区别**：本 FB 用于寻址过程中（已 SELECT 一盏灯）写入第一个短地址；后者用于正常运行时改地址。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart           : BOOL;
    eCommandPriority : E_DALIV2CommandPriority := eDALIV2CommandPriorityMiddle;
    nShortAddress    : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿 |
| `eCommandPriority` | `E_DALIV2CommandPriority` | `eDALIV2CommandPriorityMiddle` | 命令优先级：`High` / `Middle` / `Low`，决定本命令在 `FB_KL68x1Communication` 三优先级队列中的派发顺序 |
| `nShortAddress` | `BYTE` | — | 目标短地址（0..63） |

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

**调用方式**：`bStart` 上升沿；下发 `PROGRAM SHORT ADDRESS` 命令带编码字节；当前 SELECT 的灯具更新短地址寄存器（EEPROM）。

**前置条件**：本 FB 之前必须有 `FB_DALIV2SearchAddr` 序列把目标灯精确选中。否则命令对所有处于寻址模式但符合搜索条件的灯都生效，可能导致多灯同短地址。

**典型应用**：DALI 寻址流程中分配第一个短地址。通常由高层 FB 内部使用。

**典型陷阱**：① 没 SELECT 直接 ProgramShortAddress 多灯同地址；② 本命令是 SELECTED 灯的特定操作——不带 `nAddr` 参数走 broadcast。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 必须前置 `FB_DALIV2SearchAddr` 精确 SELECT 目标灯。
- 本命令对当前 SELECTED 灯生效，与寻址命令的 nAddr 无关。
- 通常通过高层 `AddressingRandomAddressing` 间接使用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2ProgramShortAddress.TcPOU`](../examples/P_Demo_FB_DALIV2ProgramShortAddress.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：DALI 寻址流程中分配短地址——通常由高层 FB 内部使用。
- **价值**：暴露 DALI 寻址协议的短地址编程命令。
- **替代方案对比**：1) `FB_DALIV2SetShortAddress`：正常运行时改地址；2) **本 FB**：寻址过程中分配。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.6.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142820107.html
- **相关**：[`FB_DALIV2SetShortAddress`](../part102_low_config/FB_DALIV2SetShortAddress.md)、[`FB_DALIV2SearchAddr`](FB_DALIV2SearchAddr.md)、[`FB_DALIV2QueryShortAddress`](FB_DALIV2QueryShortAddress.md)
