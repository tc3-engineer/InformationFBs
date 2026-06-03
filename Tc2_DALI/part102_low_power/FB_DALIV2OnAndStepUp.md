# FB_DALIV2OnAndStepUp

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
| Example | [`examples/P_Demo_FB_DALIV2OnAndStepUp.TcPOU`](../examples/P_Demo_FB_DALIV2OnAndStepUp.TcPOU) |

---

## 1. 功能简述

**关灯状态下开灯+递增一步；亮灯状态下仅递增**——灯具从 OFF 调用时先开到 `MIN VALUE` 然后递增一步；亮灯状态下等同 `StepUp`。提供一致的『按钮加亮总能让灯出现』UX。

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

**调用方式**：`bStart` 上升沿；下发 `ON AND STEP UP` 命令。

**关灯状态下的行为细节**：DALI 协议规定此命令在 OFF 状态先把灯调到 `MIN VALUE`，然后按 `FADE RATE` 步进一档。所以最终亮度大约是 `MIN VALUE + (254/FADE_RATE_steps)`。

**亮灯状态下的行为**：等同 `FB_DALIV2StepUp`——按 `FADE RATE` 单步递增，上限 `MAX VALUE`。

**典型陷阱**：关灯状态下调用，灯具会跳到 `MIN VALUE`（典型 1，几乎不可见）+ 一步，用户可能觉得『按了没反应』；要让按按钮就明显开灯应该用 `FB_DALIV2DirectArcPowerControl` 直接设到中等亮度。工程上常做法是首次按键直接 DAPC=200，后续按键才用本 FB 递增。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 关灯状态调用跳到 `MIN VALUE` + 一步，可能用户觉得反应不明显。
- 亮灯状态等同 `StepUp`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2OnAndStepUp.TcPOU`](../examples/P_Demo_FB_DALIV2OnAndStepUp.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：面板加亮按钮的开灯兼调光实现：灯关时按一下就开（且渐亮）；灯亮时按一下递增。
- **价值**：一行命令处理两种状态；UX 一致。
- **替代方案对比**：1) 应用层检测亮度然后选 `On` 或 `StepUp`：两步；2) **本 FB**：DALI 协议一行搞定。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.4.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142774667.html
- **相关**：[`FB_DALIV2StepUp`](FB_DALIV2StepUp.md)、[`FB_DALIV2RecallMaxLevel`](FB_DALIV2RecallMaxLevel.md)
