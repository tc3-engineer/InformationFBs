# FB_DALIV2StoreActualLevelInDTR0

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
| Example | [`examples/P_Demo_FB_DALIV2StoreActualLevelInDTR0.TcPOU`](../examples/P_Demo_FB_DALIV2StoreActualLevelInDTR0.TcPOU) |

---

## 1. 功能简述

**把灯具当前实际亮度存到 DTR0 寄存器**——灯具读取自身 `ACTUAL DIM LEVEL` 寄存器值（即此刻物理亮度索引）并存入 DTR0。常用于把当前亮度作为新的 `POWER ON LEVEL` / `MAX VALUE` / 场景值——一气呵成完成调到舒服位置后定为某属性这套操作。

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

**调用方式**：`bStart` 上升沿；本 FB 下发 `STORE ACTUAL LEVEL IN DTR` 命令；灯具内部把 `ACTUAL DIM LEVEL` 复制到 DTR0。DTR0 是灯具的临时寄存器，本身不失电保护，但可作为后续 `STORE DTR AS ...` 命令的源。

**典型连贯用法**：（1）用户调光到舒适位置 → 调 `FB_DALIV2DirectArcPowerControl` 设亮度 →（2）调本 FB 把当前亮度存入 DTR0 → （3）调 `FB_DALIV2StoreDTRAsScene` 把 DTR0 写为某场景值。这套流程让用户调到喜欢的位置后告诉系统这就是场景 5 的亮度。

**与 `FB_DALIV2QueryActualLevel` 区别**：后者读出来给 PLC，本 FB 只在灯具内部移动（DTR0 → 灯具寄存器链）。本 FB 不返回亮度值。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- DTR0 本身不失电保护——本 FB 后必须跟随 `STORE DTR AS ...` 命令才能持久化。
- 组 / 广播下发时所有灯都把各自亮度存入各自 DTR0，跨灯亮度不汇总（DTR0 是每灯独立的）。
- 本 FB 不返回亮度值——要读到 PLC 用 `FB_DALIV2QueryActualLevel`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2StoreActualLevelInDTR0.TcPOU`](../examples/P_Demo_FB_DALIV2StoreActualLevelInDTR0.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：智能家居记录当前亮度为场景功能：用户调光到舒适位置（用面板或 HMI），按保存为场景 3 按钮，PLC 先调本 FB 把当前亮度存到 DTR0，再调 `FB_DALIV2StoreDTRAsScene`（不在本仓库范围，用 `FB_DALIV2SetScene` 等效）把场景 3 设为该亮度。
- **价值**：替代『先查亮度 再下发 SetScene』两步操作，灯具内部一气呵成。
- **替代方案对比**：1) `FB_DALIV2QueryActualLevel` + 应用层拿到值 + `FB_DALIV2SetScene` 写场景：两次命令更慢；2) **本 FB** + 后续 `StoreDTRAsScene`：灯具内一气呵成。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.3.13
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142804875.html
- **相关**：[`FB_DALIV2QueryActualLevel`](../part102_low_queries/FB_DALIV2QueryActualLevel.md)、[`FB_DALIV2SetScene`](FB_DALIV2SetScene.md)、[`FB_DALIV2SetDTR0`](../part102_low_special/FB_DALIV2SetDTR0.md)
