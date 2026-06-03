# FB_DALIV2SetScene

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
| Example | [`examples/P_Demo_FB_DALIV2SetScene.TcPOU`](../examples/P_Demo_FB_DALIV2SetScene.TcPOU) |

---

## 1. 功能简述

**设置镇流器某个场景预设亮度值**——DALI 镇流器内部存 16 个场景寄存器（`SCENE 0..15`），每个场景对应一个亮度。本 FB 把 `nAddr` 寻址到的灯具的 `nScene` 场景值设为 `nLevel`。之后 `FB_DALIV2GoToScene` 触发该场景时该灯就会调到此亮度。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart           : BOOL;
    nAddr            : BYTE;
    eAddrType        : E_DALIV2AddrType        := eDALIV2AddrTypeShort;
    eCommandPriority : E_DALIV2CommandPriority := eDALIV2CommandPriorityMiddle;
    nSceneLevel      : BYTE;
    nScene           : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿 |
| `nAddr` | `BYTE` | — | 目标地址：单灯 short address 0..63，或组号 0..15，或 `eAddrType = Broadcast` 时忽略 |
| `eAddrType` | `E_DALIV2AddrType` | `eDALIV2AddrTypeShort` | 寻址类型：`eDALIV2AddrTypeShort`（单灯）/ `eDALIV2AddrTypeGroup`（组）/ `eDALIV2AddrTypeBroadcast`（全线广播） |
| `eCommandPriority` | `E_DALIV2CommandPriority` | `eDALIV2CommandPriorityMiddle` | 命令优先级：`High` / `Middle` / `Low`，决定本命令在 `FB_KL68x1Communication` 三优先级队列中的派发顺序 |
| `nSceneLevel` | `BYTE` | — | ⚠️ 待人工确认 |
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

**调用方式**：`bStart` 上升沿；本 FB 写 DTR0 = `nLevel`，下发 `STORE THE DTR AS SCENE n` 命令把对应场景寄存器写入 EEPROM。

**与 `FB_DALIV2RemoveFromScene` 的区别**：本 FB 设具体亮度；后者直接清成 MASK（实际等同于本 FB 的 `nLevel = 255`）。设值含义：0 = 调场景时灯关；255 = 不参与场景；其它 = 调到该亮度。

**批量配置流程**：工程初始化时按场景表逐个调本 FB——例如配置场景 0 = 会议开始（全亮）：对每盏灯调`SetScene(nScene=0, nLevel=254)`；配置场景 1 = 演示模式（只亮投影附近）：对投影附近灯调`SetScene(nScene=1, nLevel=200)`，对其它灯调 `SetScene(nScene=1, nLevel=0)`。

**典型陷阱**：① 场景配置忘了所有灯都设——未设的灯 SCENE 值是 MASK（不参与），调场景时不变化；② 改场景值后应立即用 `FB_DALIV2QuerySceneLevel` 验证；③ 不要混用场景值 0 与 MASK——前者调场景时强制关灯，后者保持原状，行为完全不同。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- `nLevel = 0` 强制关灯；`nLevel = 255 (MASK)` 不参与场景；其它值调到该亮度。
- `nScene > 15` 灯具忽略。
- 工程上线批量配置后用 `FB_DALIV2QuerySceneLevel` 逐一验证。
- EEPROM 写次数有限。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2SetScene.TcPOU`](../examples/P_Demo_FB_DALIV2SetScene.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：会议室预设场景：场景 0 = 全亮（会议开场）、场景 1 = 演示模式（仅投影附近灯亮 200）、场景 2 = 休息（所有灯调到 100）、场景 3 = 离场（所有灯关）。本 FB 给每盏灯配置每个场景对应亮度。
- **价值**：替代手动给灯具贴标签 + 用厂家工具点选；批量 PLC 代码一次配置失电保护。
- **替代方案对比**：**本 FB**：场景预设配置标准方法。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.3.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142800267.html
- **相关**：[`FB_DALIV2RemoveFromScene`](FB_DALIV2RemoveFromScene.md)、[`FB_DALIV2GoToScene`](../part102_low_power/FB_DALIV2GoToScene.md)、[`FB_DALIV2QuerySceneLevel`](../part102_low_queries/FB_DALIV2QuerySceneLevel.md)
