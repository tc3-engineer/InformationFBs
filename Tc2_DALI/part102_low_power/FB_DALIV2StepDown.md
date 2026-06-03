# FB_DALIV2StepDown

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DALI` |
| Library Version | `2.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Part 102 / Low-Level / Power Control` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/index.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DALIV2StepDown.TcPOU`](../examples/P_Demo_FB_DALIV2StepDown.TcPOU) |

---

## 1. 功能简述

**亮度递减一步命令**——灯具按当前 `FADE RATE` 步进减少一步亮度。最多减到 `MIN VALUE`，不关灯（要关用 `FB_DALIV2StepDownAndOff`）。

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

**调用方式**：`bStart` 上升沿；下发 `STEP DOWN` 命令；灯具按内部 `FADE RATE` 步进一档（FADE RATE 决定每秒可触发的最大步数，本 FB 调用一次只触发一步）。

**典型连续调光**：PLC 用 IL/ST 循环每 50 ms 调一次本 FB，配合 `FADE RATE = 7` 实现平滑的连续递减；用户长按 - 按钮触发该循环，松开停止。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 不关灯——最低 `MIN VALUE`。要关灯用 `FB_DALIV2StepDownAndOff`。
- 单步幅度由灯具 `FADE RATE` 决定；不同 `FADE RATE` 步幅不同。
- 连续调光需要 PLC 循环触发；间隔太短可能命令缓冲区溢出。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2StepDown.TcPOU`](../examples/P_Demo_FB_DALIV2StepDown.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：面板长按减亮按钮：PLC 检测按钮持续按下，每 100 ms 调一次本 FB；松开停止。
- **价值**：替代手写 DALI 字节命令；按 `FADE RATE` 自动应用 DALI 标准步进。
- **替代方案对比**：1) `FB_DALIV2Down`：连续 `Down` 命令（200 ms 内连续步进）；2) `FB_DALIV2DirectArcPowerControl` + 自算下个值：完全自定义；3) **本 FB**：单步精确调光。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.4.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142779275.html
- **相关**：[`FB_DALIV2StepDownAndOff`](FB_DALIV2StepDownAndOff.md)、[`FB_DALIV2StepUp`](FB_DALIV2StepUp.md)、[`FB_DALIV2Down`](FB_DALIV2Down.md)、[`FB_DALIV2SetFadeRate`](../part102_low_config/FB_DALIV2SetFadeRate.md)
