# FB_DALIV2SetFadeTime

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
| Example | [`examples/P_Demo_FB_DALIV2SetFadeTime.TcPOU`](../examples/P_Demo_FB_DALIV2SetFadeTime.TcPOU) |

---

## 1. 功能简述

**设置镇流器 `FADE TIME` 寄存器**——决定 DAPC 命令、`GoToScene`、`RecallMaxLevel` 等绝对目标命令的渐变总时间。值 0 = 瞬时跳变；越大渐变越慢。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart           : BOOL;
    nAddr            : BYTE;
    eAddrType        : E_DALIV2AddrType        := eDALIV2AddrTypeShort;
    eCommandPriority : E_DALIV2CommandPriority := eDALIV2CommandPriorityMiddle;
    nFadeTime        : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿 |
| `nAddr` | `BYTE` | — | 目标地址：单灯 short address 0..63，或组号 0..15，或 `eAddrType = Broadcast` 时忽略 |
| `eAddrType` | `E_DALIV2AddrType` | `eDALIV2AddrTypeShort` | 寻址类型：`eDALIV2AddrTypeShort`（单灯）/ `eDALIV2AddrTypeGroup`（组）/ `eDALIV2AddrTypeBroadcast`（全线广播） |
| `eCommandPriority` | `E_DALIV2CommandPriority` | `eDALIV2CommandPriorityMiddle` | 命令优先级：`High` / `Middle` / `Low`，决定本命令在 `FB_KL68x1Communication` 三优先级队列中的派发顺序 |
| `nFadeTime` | `BYTE` | — | 目标 `FADE TIME` 索引值 0..15。0 = 瞬时跳变；1..15 对应非线性时间表（1 ≈ 707 ms / 8 ≈ 8 s / 15 ≈ 90.5 s）。控制 `DAPC` 命令从当前亮度变化到目标亮度的总时间 |

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

**调用方式**：`bStart` 上升沿；本 FB 写 DTR0 = `nFadeTime`，下发 `STORE THE DTR AS FADE TIME` 把 DTR0 写入灯具 EEPROM。

**FADE TIME 数值与实际时间关系**（DALI 规范 Table）：0 = 瞬时；1 = 0.707 s；2 = 1.0 s；3 = 1.414 s；4 = 2.0 s（出厂默认）；5 = 2.828 s；6 = 4.0 s；7 = 5.657 s；8 = 8.0 s；9 = 11.314 s；10 = 16.0 s；11 = 22.627 s；12 = 32.0 s；13 = 45.255 s；14 = 64.0 s；15 = 90.510 s。

**与 `FADE RATE` 区别**：本字段控制 DAPC 类绝对命令的总时间；`FADE RATE` 控制 Up/Down 类步进命令的速率。

**典型场景**：办公照明 `FADE TIME = 2` (1 s)；剧院 `FADE TIME = 8` (8 s)；HMI 滑块实时调光 `FADE TIME = 0`（瞬时跟手）。

**典型陷阱**：① 上线时 FADE TIME 默认 0，从 DAPC 看上去像瞬时跳变，看似无渐变功能 → 设到非零；② 改 FADE TIME 后立即 DAPC，下一次 DAPC 才用新值。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- FADE TIME = 0 时 DAPC 瞬时跳变。
- FADE TIME 是非线性的，不是秒数——查上表换算。
- 改完用 `FB_DALIV2QueryFadeTimeFadeRate` 验证。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2SetFadeTime.TcPOU`](../examples/P_Demo_FB_DALIV2SetFadeTime.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：电影院散场灯——观众散场时灯渐渐亮起，从 0 用 8 秒渐变到 200。本 FB 把 FADE TIME 设为 8 (8 s)，然后 DAPC(200) 触发渐变。
- **价值**：灯具内部硬件完成渐变，PLC 端不用写循环；渐变曲线由 DALI 协议保证平滑。
- **替代方案对比**：1) PLC 循环连续 DAPC 实现渐变：可行但占用通信带宽；2) `FB_DALIV2SetFadeRate` 配 Up/Down 步进调光：粒度有限；3) **本 FB**：绝对命令渐变标准配置。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.3.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142794123.html
- **相关**：[`FB_DALIV2SetFadeRate`](FB_DALIV2SetFadeRate.md)、[`FB_DALIV2QueryFadeTimeFadeRate`](../part102_low_queries/FB_DALIV2QueryFadeTimeFadeRate.md)、[`FB_DALIV2DirectArcPowerControl`](../part102_low_power/FB_DALIV2DirectArcPowerControl.md)、[`FB_DALIV2GoToScene`](../part102_low_power/FB_DALIV2GoToScene.md)
