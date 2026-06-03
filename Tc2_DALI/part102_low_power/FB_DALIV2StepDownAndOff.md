# FB_DALIV2StepDownAndOff

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
| Example | [`examples/P_Demo_FB_DALIV2StepDownAndOff.TcPOU`](../examples/P_Demo_FB_DALIV2StepDownAndOff.TcPOU) |

---

## 1. 功能简述

**亮度递减一步并在最低时关灯**——与 `FB_DALIV2StepDown` 类似，但当亮度已是 `MIN VALUE` 时下一次调用直接关灯（亮度 0）。提供一致的『按钮按到底就关灯』UX。

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

**调用方式**：`bStart` 上升沿；下发 `STEP DOWN AND OFF` 命令。灯具按 `FADE RATE` 步进一档；如果当前已是 `MIN VALUE`，则关灯。

**与 `StepDown` 区别**：`StepDown` 最低停在 `MIN VALUE`；本 FB 在 `MIN VALUE` 状态下再调一次会关灯。

**典型应用**：面板长按减亮按钮的『一直按到关』实现——用户按住按钮 PLC 每 100 ms 触发本 FB，亮度逐步下降到 `MIN VALUE`，再触发一次直接关灯，松开按钮即停止。这种 UX 在楼宇 / 家用照明非常常见。

**典型陷阱**：① 用户期望『按一次关一次』时不要用本 FB，会一直递减；用 `FB_DALIV2Off`；② `MIN VALUE` 设得高（如 100）则用户感觉灯被『从中等亮度突然全黑』，体验不平滑——`MIN VALUE` 应设得较低（如 30 以下）配合本 FB。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 在已是 `MIN VALUE` 状态下调用本 FB 灯会关——给用户『按到底关灯』的体验。
- 其它行为同 `StepDown`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2StepDownAndOff.TcPOU`](../examples/P_Demo_FB_DALIV2StepDownAndOff.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：智能面板：用户长按减亮按钮直到关灯——本 FB 替代『先 StepDown 到 MIN 然后再 Off』两步逻辑。
- **价值**：一行命令实现『递减到底关灯』；PLC 端不需要检查当前亮度。
- **替代方案对比**：1) `FB_DALIV2StepDown` + 应用层检查到 MIN 再调 `Off`：两次命令 + 状态检查；2) **本 FB**：一行命令搞定。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.4.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142780811.html
- **相关**：[`FB_DALIV2StepDown`](FB_DALIV2StepDown.md)、[`FB_DALIV2Off`](FB_DALIV2Off.md)、[`FB_DALIV2StepUp`](FB_DALIV2StepUp.md)
