# FB_DALIV2Randomise

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
| Example | [`examples/P_Demo_FB_DALIV2Randomise.TcPOU`](../examples/P_Demo_FB_DALIV2Randomise.TcPOU) |

---

## 1. 功能简述

**让灯具生成 24-bit 随机地址**——`FB_DALIV2Initialise` 之后的下一步：让所有处于寻址模式的灯在自己内部生成一个 24-bit 随机地址（`RANDOM ADDRESS` 寄存器）。这是 DALI 寻址协议的核心：通过随机地址做二分搜索找出每盏灯并分配短地址。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart           : BOOL;
    eCommandPriority : E_DALIV2CommandPriority := eDALIV2CommandPriorityMiddle;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿 |
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

**调用方式**：`bStart` 上升沿；下发 `RANDOMISE` 命令（双指令防误触发）；灯具内部生成24-bit 伪随机数存入 `RANDOM ADDRESS` 寄存器。生成约 100 ms。

**生成方式**：DALI 协议不规定具体随机算法；厂家自定（典型用灯具序列号 + 时间戳 hash）。理论上两盏灯生成相同地址的概率约 1/2^24（极低），但工程上应在 randomise 后用 `VerifyShortAddress` 校验所有灯都不同。

**典型应用**：DALI 寻址流程的第二步（Initialise → Randomise → SearchAddr 二分搜索）。通常由高层 `FB_DALIV2AddressingRandomAddressing` 内部使用。

**典型陷阱**：本 FB 之前必须先 `Initialise` 让灯进入寻址模式；否则命令被普通灯具忽略。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 前置必须 `FB_DALIV2Initialise`。
- 生成时间约 100 ms；Randomise 后等待再做 SearchAddr。
- 通常通过高层 FB 间接使用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2Randomise.TcPOU`](../examples/P_Demo_FB_DALIV2Randomise.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：DALI 寻址流程的第二步——通常由 `FB_DALIV2AddressingRandomAddressing` 内部使用。
- **价值**：暴露 DALI 寻址协议中的随机地址生成命令。
- **替代方案对比**：通过高层 FB 间接使用。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.6.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142823179.html
- **相关**：[`FB_DALIV2Initialise`](FB_DALIV2Initialise.md)、[`FB_DALIV2SearchAddr`](FB_DALIV2SearchAddr.md)、[`FB_DALIV2QueryRandomAddress`](../part102_low_queries/FB_DALIV2QueryRandomAddress.md)
