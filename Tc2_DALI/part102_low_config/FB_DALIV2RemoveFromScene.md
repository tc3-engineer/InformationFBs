# FB_DALIV2RemoveFromScene

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
| Example | [`examples/P_Demo_FB_DALIV2RemoveFromScene.TcPOU`](../examples/P_Demo_FB_DALIV2RemoveFromScene.TcPOU) |

---

## 1. 功能简述

**清除镇流器某个场景预设的命令**——DALI 镇流器内部存 16 个场景寄存器（`SCENE 0..15`），每个场景对应一个亮度值。本 FB 把 `nAddr` 寻址到的镇流器的 `nScene`（0..15）场景值清成 `MASK`（表示该灯不参与该场景，调用此场景时不变化）。

场景预设的反向操作；`FB_DALIV2SetScene` 是设场景值，本 FB 是清场景值。

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
| `nScene` | `BYTE` | — | 要清除的场景号（0..15） |

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

**调用方式**：`bStart` 上升沿；本 FB 写 DTR0 = `MASK`（=255），下发 `STORE DTR AS SCENE n` 命令，灯具把第 n 个场景寄存器写为 `MASK`，等同于该灯不参与场景 n。

**场景调用时的影响**：之后 `FB_DALIV2GoToScene` 用 `nScene = n` 触发场景 n 时，本灯（被本 FB 清的灯）亮度不变（即忽略该场景）。其它灯不受影响。

**EEPROM 写次数**：与 Add/Remove Group 一样，分场景配置应是低频。

**典型陷阱**：① 与 `FB_DALIV2SetScene` 配合使用——先 SetScene 给一组灯设值，后 RemoveFromScene 把不应该响应该场景的灯清掉；② 不要在生产期循环清除。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 本 FB 把场景值写为 `MASK`（255），等同于该灯不参与此场景。
- EEPROM 写次数有限。
- `nScene > 15` 灯具忽略。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2RemoveFromScene.TcPOU`](../examples/P_Demo_FB_DALIV2RemoveFromScene.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：会议室场景调用配置：场景 0 = 会议开场全亮、场景 1 = 演示模式（只亮投影附近灯）。演示模式应让窗边灯不亮——用本 FB 把窗边灯 short addr 15 的场景 1 清成 MASK，调场景 1 时窗边灯保持原状。
- **价值**：替代手动给每盏灯都设场景值；不参与是更精准的语义。
- **替代方案对比**：1) `FB_DALIV2SetScene` 设为 0：表示灯关——但调用场景时灯会被主动关灭（如果原本亮就被关）；2) **本 FB** 设为 MASK：表示不参与——调用场景时不动；语义更精确。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.3.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142789515.html
- **相关**：[`FB_DALIV2SetScene`](FB_DALIV2SetScene.md)、[`FB_DALIV2GoToScene`](../part102_low_power/FB_DALIV2GoToScene.md)、[`FB_DALIV2QuerySceneLevel`](../part102_low_queries/FB_DALIV2QuerySceneLevel.md)
