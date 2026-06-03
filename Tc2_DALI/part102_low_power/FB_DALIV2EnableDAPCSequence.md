# FB_DALIV2EnableDAPCSequence

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
| Example | [`examples/P_Demo_FB_DALIV2EnableDAPCSequence.TcPOU`](../examples/P_Demo_FB_DALIV2EnableDAPCSequence.TcPOU) |

---

## 1. 功能简述

**启用 DAPC 序列模式命令**——告诉灯具接下来一段时间会收到连续多次 DAPC 命令（间隔 ≤ 200 ms），灯具进入连续接受模式：所有 DAPC 立即应用、不做 FADE TIME 渐变、不响应其它命令。常用于 PLC 自己写平滑长渐变（用 PLC 定时器每 100 ms 算一个目标亮度、通过 DAPC 下发）的场景。

**注意时序**：本 FB 触发后必须在 200 ms 内开始连续 DAPC；超时灯具自动退出序列模式。

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

**调用方式**：`bStart` 上升沿；下发 `ENABLE DAPC SEQUENCE` 命令；灯具进入序列模式持续 200 ms。

**序列内的 DAPC 时序约束**：每两次 DAPC 命令间隔必须 ≤ 200 ms。超时灯具自动退出。退出后再 DAPC 按普通模式（受 FADE TIME 影响）。

**典型应用**：① PLC 自己实现非标准渐变曲线（如 S 曲线、三角波）——每 100 ms 算一个亮度发 DAPC；② 舞台特效——精确控制每帧亮度；③ 与音乐同步的呼吸效果。

**典型陷阱**：① 启用后超 200 ms 没下 DAPC，灯具退出，下一次 DAPC 按普通模式生效（用户感知突变）；② 序列期间下发非 DAPC 命令（如 RecallMax）→ 灯具退出序列模式后处理，时序不确定。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 启用后必须 200 ms 内开始下 DAPC，且 DAPC 间隔 ≤ 200 ms。
- 序列期间不要混入其它命令。
- 渐变需要 PLC 端实现（FADE TIME 在序列模式被忽略）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2EnableDAPCSequence.TcPOU`](../examples/P_Demo_FB_DALIV2EnableDAPCSequence.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：舞台音乐节奏调光——PLC 按 100 ms 节拍计算下一个亮度，通过 DAPC 下发；启用序列模式让灯具立即响应。
- **价值**：替代灯具自己的 FADE TIME 渐变（曲线固定、时间档位有限）；PLC 可实现任意自定义曲线。
- **替代方案对比**：1) 单纯 DAPC 不启序列：每条 DAPC 经过 FADE TIME 渐变，多次 DAPC 看上去是断断续续的跳变；2) **本 FB** + 连续 DAPC：平滑连续的自定义曲线。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.4.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142770571.html
- **相关**：[`FB_DALIV2DirectArcPowerControl`](FB_DALIV2DirectArcPowerControl.md)、[`FB_DALIV2SetFadeTime`](../part102_low_config/FB_DALIV2SetFadeTime.md)
