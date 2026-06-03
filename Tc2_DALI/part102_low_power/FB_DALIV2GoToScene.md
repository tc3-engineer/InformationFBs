# FB_DALIV2GoToScene

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
| Example | [`examples/P_Demo_FB_DALIV2GoToScene.TcPOU`](../examples/P_Demo_FB_DALIV2GoToScene.TcPOU) |

---

## 1. 功能简述

**触发场景调用命令**——灯具调到自身 `SCENE n` 寄存器存的亮度（n = `nScene`，0..15）。受 `FADE TIME` 渐变。配合 `FB_DALIV2SetScene` 使用——前者预设场景值，本 FB 触发。

场景是 DALI 协议的核心概念之一——把『每盏灯在某状态下的亮度』预存到灯具内部，调用一条命令即可整片灯同时切到该状态。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart           : BOOL;
    nAddr            : BYTE;
    eAddrType        : E_DALIV2AddrType        := eDALIV2AddrTypeShort;
    eCommandPriority : E_DALIV2CommandPriority := eDALIV2CommandPriorityMiddle;
    nScene           : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿 |
| `nAddr` | `BYTE` | — | 目标地址：单灯 short address 0..63，或组号 0..15，或 `eAddrType = Broadcast` 时忽略 |
| `eAddrType` | `E_DALIV2AddrType` | `eDALIV2AddrTypeShort` | 寻址类型：`eDALIV2AddrTypeShort`（单灯）/ `eDALIV2AddrTypeGroup`（组）/ `eDALIV2AddrTypeBroadcast`（全线广播） |
| `eCommandPriority` | `E_DALIV2CommandPriority` | `eDALIV2CommandPriorityMiddle` | 命令优先级：`High` / `Middle` / `Low`，决定本命令在 `FB_KL68x1Communication` 三优先级队列中的派发顺序 |
| `nScene` | `BYTE` | — | 目标场景号（0..15） |

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

**调用方式**：`bStart` 上升沿；下发 `GO TO SCENE n` 命令；灯具读取自身 `SCENE n` 寄存器值（用 `FB_DALIV2SetScene` 预设过），按该值调亮度。`FADE TIME` 决定渐变。

**广播触发的力量**：`eAddrType := Broadcast` + `nScene := 0` 让全线所有灯同时切到场景 0——每盏灯的场景 0 值不同（房间灯到 254、走廊灯到 100、地面灯到 50），但一条命令同步生效。**这是 DALI 协议相对 0..10V / DMX 等更高级的核心特性之一**。

**场景值的特殊语义**：`SCENE n = MASK (255)` 时本灯不参与该场景；`SCENE n = 0` 时本灯调用时被强制关灯。用 `FB_DALIV2RemoveFromScene` 设 MASK；用 `FB_DALIV2SetScene` 设具体亮度。

**典型陷阱**：① `nScene > 15` 灯具忽略；② 场景未预设的灯调用本 FB 后亮度不变（MASK 默认）或被关灯（0 默认，取决于灯具）——上线前必须先用 `FB_DALIV2SetScene` 给所有相关灯配场景值。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- `nScene` 必须 0..15。
- 调用前必须用 `FB_DALIV2SetScene` 预设每盏灯的该场景值，否则行为不确定。
- 渐变时长由 `FADE TIME` 决定。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2GoToScene.TcPOU`](../examples/P_Demo_FB_DALIV2GoToScene.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：会议室自动化：操作员触屏选『演示模式』，PLC 广播 GoToScene(nScene=1) 给整个会议室——所有灯按预设瞬间切到投影最舒适的亮度组合（投影区灯 200、其它区 50、窗边 0）。
- **价值**：替代 PLC 程序里写一堆条件判断把每盏灯设到固定亮度的代码；预设场景使逻辑与亮度数值解耦，运维改场景不用改 PLC。
- **替代方案对比**：1) PLC 直接发多个 DAPC 给每盏灯：能做但代码硬编码亮度数值，运维不便；2) **本 FB**：场景与代码解耦，运维只在 HMI 配场景值即可。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.4.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142772107.html
- **相关**：[`FB_DALIV2SetScene`](../part102_low_config/FB_DALIV2SetScene.md)、[`FB_DALIV2RemoveFromScene`](../part102_low_config/FB_DALIV2RemoveFromScene.md)、[`FB_DALIV2QuerySceneLevel`](../part102_low_queries/FB_DALIV2QuerySceneLevel.md)
