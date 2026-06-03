# FB_DALIV2SetDTR0

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
| Example | [`examples/P_Demo_FB_DALIV2SetDTR0.TcPOU`](../examples/P_Demo_FB_DALIV2SetDTR0.TcPOU) |

---

## 1. 功能简述

**写灯具 DTR0 临时寄存器**——DTR0 是 DALI 灯具内一字节临时寄存器，用作各种 `STORE DTR AS ...` 命令的源（如 `STORE DTR AS MAX LEVEL`、`STORE DTR AS GROUPS 0-7`）。本 FB 直接把`nValue` 写入 DTR0。

通常作为更高层 `FB_DALIV2SetXxx` FB 的底层基础——那些 FB 内部先调本 FB 再发 STORE 命令。工程上很少直接用本 FB，但需要做厂家特殊命令（如某厂家用 DTR0 传特殊参数）时直接调用。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart           : BOOL;
    eCommandPriority : E_DALIV2CommandPriority := eDALIV2CommandPriorityMiddle;
    nDTR0            : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿 |
| `eCommandPriority` | `E_DALIV2CommandPriority` | `eDALIV2CommandPriorityMiddle` | 命令优先级：`High` / `Middle` / `Low`，决定本命令在 `FB_KL68x1Communication` 三优先级队列中的派发顺序 |
| `nDTR0` | `BYTE` | — | ⚠️ 待人工确认 |

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

**调用方式**：`bStart` 上升沿；本 FB 下发 `SET DTR` 命令带数据字节 `nValue`；灯具更新 DTR0。

**DTR0 是临时的**——不失电保护；下次 `SET DTR` 命令立即覆盖。后续要让值持久必须配套 `STORE DTR AS ...` 命令把 DTR0 写入对应失电保护寄存器。

**典型应用**：① 配合厂家自定义命令（部分厂家 DALI 设备用 DTR0 传特殊参数）；② 调试时手动构造 STORE 序列；③ `FB_DALIV2SetXxx` 高层 FB 内部使用。

**典型陷阱**：① 设 DTR0 后必须立即（同优先级队列）发 STORE 命令——否则可能被其它 FB 的 SET DTR 覆盖；② 多 FB 都用 DTR0 时优先级 / 顺序要小心。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- DTR0 不失电保护，下次 SET DTR 覆盖。
- 设 DTR0 后必须紧跟 STORE 命令——同优先级队列保证顺序。
- 工程上很少直接用，通常通过 `FB_DALIV2SetXxx` 间接使用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2SetDTR0.TcPOU`](../examples/P_Demo_FB_DALIV2SetDTR0.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：调试或厂家特殊命令——直接写 DTR0 然后发自定义 STORE 命令。
- **价值**：暴露 DALI 协议底层 DTR0 寄存器；为厂家特殊命令提供基础。
- **替代方案对比**：1) `FB_DALIV2SetFadeTime` / SetMaxLevel 等：高层 FB 已自动用 DTR0；2) **本 FB**：底层调试 / 自定义。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.6.11
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142826635.html
- **相关**：[`FB_DALIV2SetDTR1`](FB_DALIV2SetDTR1.md)、[`FB_DALIV2SetDTR2`](FB_DALIV2SetDTR2.md)、[`FB_DALIV2QueryContentDTR0`](../part102_low_queries/FB_DALIV2QueryContentDTR0.md)
