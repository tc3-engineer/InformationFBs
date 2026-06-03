# FB_DALIV2SetDTR2

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
| Example | [`examples/P_Demo_FB_DALIV2SetDTR2.TcPOU`](../examples/P_Demo_FB_DALIV2SetDTR2.TcPOU) |

---

## 1. 功能简述

**写灯具 DTR2 临时寄存器**——同 DTR1，用于需要 3 个字节参数的扩展命令。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart           : BOOL;
    eCommandPriority : E_DALIV2CommandPriority := eDALIV2CommandPriorityMiddle;
    nDTR2            : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿 |
| `eCommandPriority` | `E_DALIV2CommandPriority` | `eDALIV2CommandPriorityMiddle` | 命令优先级：`High` / `Middle` / `Low`，决定本命令在 `FB_KL68x1Communication` 三优先级队列中的派发顺序 |
| `nDTR2` | `BYTE` | — | ⚠️ 待人工确认 |

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

**调用方式**：`bStart` 上升沿；下发 `SET DTR2` 命令。

**DTR2 用途**：与 DTR0/DTR1 组合实现 3 字节参数命令（如 24-bit 地址扩展、颜色 xy 坐标等）。在 Part 209 颜色控制命令族里，DTR0 / DTR1 / DTR2 分别承载颜色 xy 坐标的 LSB / 中间字节 / MSB，组成完整 16-bit 色坐标值。

**典型应用**：颜色控制 FB 内部、内存访问 FB 内部、扩展命令传 24-bit 内存地址等。

**典型陷阱**：同 DTR0 / DTR1——临时寄存器、不失电保护、需要紧跟相应 STORE / 命令；DTR0/1/2 三个写入要保证顺序（同优先级队列保证 FIFO）。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 同 DTR0/DTR1：临时、不失电、需配套 STORE。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2SetDTR2.TcPOU`](../examples/P_Demo_FB_DALIV2SetDTR2.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：需要 3 字节参数的扩展命令底层操作。
- **价值**：暴露 DTR2 寄存器。
- **替代方案对比**：通过高层 FB 间接使用。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.6.13
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142829707.html
- **相关**：[`FB_DALIV2SetDTR0`](FB_DALIV2SetDTR0.md)、[`FB_DALIV2SetDTR1`](FB_DALIV2SetDTR1.md)、[`FB_DALIV2QueryContentDTR2`](../part102_low_queries/FB_DALIV2QueryContentDTR2.md)
