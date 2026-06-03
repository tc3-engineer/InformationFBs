# FB_DALIV2SetPowerOnLevel

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
| Example | [`examples/P_Demo_FB_DALIV2SetPowerOnLevel.TcPOU`](../examples/P_Demo_FB_DALIV2SetPowerOnLevel.TcPOU) |

---

## 1. 功能简述

**设置镇流器 `POWER ON LEVEL` 寄存器**——灯具供电恢复（如停电后来电）时自动调到的亮度。出厂默认 254（全亮）；可设为 MASK (255) 表示保持关灯（不自动开）。工程上常配置为 100..150 让来电后中等亮度（避免突然全亮刺眼）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart           : BOOL;
    nAddr            : BYTE;
    eAddrType        : E_DALIV2AddrType        := eDALIV2AddrTypeShort;
    eCommandPriority : E_DALIV2CommandPriority := eDALIV2CommandPriorityMiddle;
    nPowerOnLevel    : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿 |
| `nAddr` | `BYTE` | — | 目标地址：单灯 short address 0..63，或组号 0..15，或 `eAddrType = Broadcast` 时忽略 |
| `eAddrType` | `E_DALIV2AddrType` | `eDALIV2AddrTypeShort` | 寻址类型：`eDALIV2AddrTypeShort`（单灯）/ `eDALIV2AddrTypeGroup`（组）/ `eDALIV2AddrTypeBroadcast`（全线广播） |
| `eCommandPriority` | `E_DALIV2CommandPriority` | `eDALIV2CommandPriorityMiddle` | 命令优先级：`High` / `Middle` / `Low`，决定本命令在 `FB_KL68x1Communication` 三优先级队列中的派发顺序 |
| `nPowerOnLevel` | `BYTE` | — | 目标 `POWER ON LEVEL`（0..254 或 MASK=255）。灯具供电恢复时自动调到此亮度。MASK 表示供电恢复后保持关灯 |

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

**调用方式**：`bStart` 上升沿；写 DTR0 = `nPowerOnLevel`，下发 `STORE THE DTR AS POWER ON LEVEL`。

**`POWER ON LEVEL` 触发时机**：灯具上电（接到 220V AC）瞬间，灯具内部读 EEPROM 取 `POWER ON LEVEL`，如果 != MASK 则直接调到这个亮度；MASK 时保持关灯，等待 PLC 主动 DAPC。

**典型应用**：① 走廊灯 POWER ON = 200（停电恢复后中等亮度）；② 应急灯 POWER ON = 254（自动全亮）；③ 装饰灯 POWER ON = MASK（来电后保持关，由场景控制器决定）。

**典型陷阱**：① 默认 254 + 停电次数频繁时大量灯瞬间全亮，可能冲击电网；② MASK 后用户以为灯坏了，找不到原因（应在工程文档说明）。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- POWER ON LEVEL 0..254 或 MASK (255)；其它值灯具忽略。
- 默认 254 会在每次断电恢复时全亮，工程上常调到 100..150。
- MASK 设置后必须有 PLC 主动 DAPC 才能开灯。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2SetPowerOnLevel.TcPOU`](../examples/P_Demo_FB_DALIV2SetPowerOnLevel.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：办公楼夜间断电恢复——希望所有办公照明来电后调到 50% 亮度（POWER ON = 150）让保安巡夜，而不是突然全亮刺眼。
- **价值**：替代每次断电恢复都靠 PLC 程序识别 + DAPC 下发——硬件层面就解决。
- **替代方案对比**：1) PLC 上电时主动 DAPC：要等 PLC 启动好（可能几秒）；2) **本 FB**：灯具供电瞬间就生效，零延迟。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.3.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142798731.html
- **相关**：[`FB_DALIV2QueryPowerOnLevel`](../part102_low_queries/FB_DALIV2QueryPowerOnLevel.md)、[`FB_DALIV2QueryPowerFailure`](../part102_low_queries/FB_DALIV2QueryPowerFailure.md)、[`FB_DALIV2SetSystemFailureLevel`](FB_DALIV2SetSystemFailureLevel.md)
