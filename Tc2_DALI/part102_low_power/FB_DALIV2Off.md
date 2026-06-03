# FB_DALIV2Off

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
| Example | [`examples/P_Demo_FB_DALIV2Off.TcPOU`](../examples/P_Demo_FB_DALIV2Off.TcPOU) |

---

## 1. 功能简述

**关灯命令**——立即把目标 DALI 镇流器调到亮度 0（关）。无视 `MIN VALUE` 钳位（0 是关灯特例）。由 DALI 协议直接定义的标准命令。

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

**调用方式**：`bStart` 上升沿；本 FB 下发 `OFF` 命令（DALI 字节 `100x xxx0 0000 0000`，`x` 由 `nAddr` 与 `eAddrType` 编码决定）。灯具收到立即关灯。

**与 `DAPC = 0` 区别**：二者效果完全相同（都是关灯），但本 FB 用 DALI 协议显式 OFF 命令，语义更明确、网络流量略低（不需要额外的 DAPC 字节）。

**典型应用**：消防联动一键关灯（应急联动信号触发本 FB 给广播地址）、定时关灯、HMI 关灯按钮。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 与 `DAPC = 0` 等效；推荐用本 FB 因语义更清晰。
- 广播下发关灯整线所有灯立即关；运行时慎用（影响用户）。
- 本 FB 不带 FADE 渐变——`OFF` 命令是瞬时关，不受 `FADE TIME` 影响。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2Off.TcPOU`](../examples/P_Demo_FB_DALIV2Off.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：消防联动：消防中心一键触发，PLC 广播本 FB 给整楼层所有非应急灯，瞬间关闭节能。
- **价值**：替代手动检查每盏灯亮度再下发 DAPC=0；DALI 标准 OFF 命令一句话搞定。
- **替代方案对比**：1) `FB_DALIV2DirectArcPowerControl(nArcPowerLevel=0)`：等效；2) **本 FB**：语义清晰首选。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.4.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142773131.html
- **相关**：[`FB_DALIV2DirectArcPowerControl`](FB_DALIV2DirectArcPowerControl.md)（等效但要传 0）、[`FB_DALIV2RecallMaxLevel`](FB_DALIV2RecallMaxLevel.md)（一键全亮）
