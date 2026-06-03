# FB_DALIV2QueryPowerFailure

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DALI` |
| Library Version | `2.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Part 102 / Low-Level / Queries` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/index.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DALIV2QueryPowerFailure.TcPOU`](../examples/P_Demo_FB_DALIV2QueryPowerFailure.TcPOU) |

---

## 1. 功能简述

**查询命令（布尔结果）**——查询灯具是否经历过电源故障（自上次查询以来）。TRUE = 灯具检测到电源中断（自检读位后自动清零）。属于 IEC 62386 Part 102 控制设备查询命令族。建议用低优先级避免抢占调光命令带宽。

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
    bBusy         : BOOL;
    bError        : BOOL;
    nErrorId      : UDINT;
    bPowerFailure : BOOL;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 本 FB 接到 `bStart` 上升沿后置 TRUE；命令派发完且收到 DALI 响应（或超时）后回 FALSE |
| `bError` | `BOOL` | 执行错时置 TRUE；下次 `bStart` 上升沿自动复位 |
| `nErrorId` | `UDINT` | 错误号（命令专用）；详见 §4 错误码表与全库错误码（PDF §4.1.4） |
| `bPowerFailure` | `BOOL` | ⚠️ 待人工确认 |

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

**调用方式**：`bStart` 上升沿；本 FB 下发查询命令；灯具应答（YES / NO）填入`bQueryData` 输出。

**用 Yes/No 应答的 DALI 查询特殊性**：DALI 协议对布尔查询用前向应答机制——灯具在收到查询命令的瞬间用一个固定字节（`0xFF` = YES，无应答 = NO）回应。所以即便灯具不在线（无应答），本 FB 也会 `bQueryData = FALSE`——区分『灯具不在线』与『灯具说 NO』需要配合 `FB_DALIV2QueryControlGearPresent`。

**广播查询**：本 FB 也可广播——如果总线上至少有一盏灯应答 YES 则 `bQueryData = TRUE`。适合『有没有任何灯具故障』这种群体诊断查询。

**典型应用**：HMI 显示灯故障指示灯；运行时巡检；上线时检测所有灯是否在线。

**典型陷阱**：① 不能区分『不在线』与『说 NO』——必要时先用 `QueryControlGearPresent` 确认在线；② 某些状态位读后自动清零（如 `QueryPowerFailure`），读完再读得到 FALSE。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 本 FB 返回 FALSE 不能区分『不在线』与『说 NO』——配合 `FB_DALIV2QueryControlGearPresent` 区分。
- 部分查询读后自动清零（PowerFailure 等）。
- 广播查询返回『总线上任一灯具说 YES』，适合群体诊断。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2QueryPowerFailure.TcPOU`](../examples/P_Demo_FB_DALIV2QueryPowerFailure.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：运行时巡检 / HMI 灯故障指示——查询灯具是否经历过电源故障（自上次查询以来）。
- **价值**：替代 PLC 自行解析 DALI 应答帧；自动处理 YES/NO 应答语义。
- **替代方案对比**：1) `FB_DALIV2QueryStatus`：一次读全部 8 个状态位；2) **本 FB**：单独读某个状态位（语义清晰）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.5.18
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142810507.html
- **相关**：[`FB_DALIV2QueryStatus`](FB_DALIV2QueryStatus.md)（一次读全部状态）
