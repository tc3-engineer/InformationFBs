# FB_DALIV2Initialise

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
| Example | [`examples/P_Demo_FB_DALIV2Initialise.TcPOU`](../examples/P_Demo_FB_DALIV2Initialise.TcPOU) |

---

## 1. 功能简述

**进入寻址初始化模式**——DALI 寻址流程的开端命令。本 FB 让灯具进入寻址模式（接受后续的 `SearchAddr` / `ProgramShortAddress` 等命令）。本命令必须在两次 200 ms 间隔内重发以确认（DALI 协议反误触发保护）。

通常被 `FB_DALIV2AddressingRandomAddressing` 等高层 FB 内部使用；工程上很少直接调用。

## 2. 接口定义

### VAR_INPUT
无

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

**调用方式**：`bStart` 上升沿；本 FB 下发 `INITIALISE` 命令（两次 200 ms 内）；灯具进入寻址模式持续 15 分钟（之后自动退出，需重发或用 `FB_DALIV2Terminate` 主动结束）。

**寻址模式下灯具行为**：仅响应 `SearchAddr / ProgramShortAddress / Withdraw / VerifyShortAddress / QueryShortAddress / Terminate` 这几条寻址相关命令；普通调光命令被忽略。

**广播模式的特殊语义**：`eAddrType := Broadcast` 让所有灯进入寻址模式；`eAddrType := Short` + `nAddr := X` 让短地址 X 的灯进入寻址模式（用于二分搜索单灯）；`eAddrType := Group` 让某组的灯进入。

**典型陷阱**：① 寻址模式 15 分钟过长——开发调试时容易遗忘 `Terminate`；② 寻址模式期间下发普通调光命令灯不响应，调试时会迷惑；③ 通常通过高层 `AddressingRandomAddressing` 间接使用。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 寻址模式持续 15 分钟，开发期间务必用 `FB_DALIV2Terminate` 主动结束。
- 寻址模式下灯具忽略普通命令，调试要注意。
- 通常通过高层 FB 间接使用，工程很少直接调本 FB。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2Initialise.TcPOU`](../examples/P_Demo_FB_DALIV2Initialise.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：DALI 寻址流程的开端——通常由 `FB_DALIV2AddressingRandomAddressing` 内部使用。
- **价值**：暴露 DALI 寻址协议的初始化命令；为定制寻址流程提供基础。
- **替代方案对比**：通常用高层 `FB_DALIV2AddressingRandomAddressing` 间接调用。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.6.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142810443.html
- **相关**：[`FB_DALIV2Randomise`](FB_DALIV2Randomise.md)、[`FB_DALIV2SearchAddr`](FB_DALIV2SearchAddr.md)、[`FB_DALIV2Terminate`](FB_DALIV2Terminate.md)、[`FB_DALIV2AddressingRandomAddressing`](../part102_addressing/FB_DALIV2AddressingRandomAddressing.md)
