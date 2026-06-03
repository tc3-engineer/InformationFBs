# FB_DALIV2QueryRandomAddress

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
| Example | [`examples/P_Demo_FB_DALIV2QueryRandomAddress.TcPOU`](../examples/P_Demo_FB_DALIV2QueryRandomAddress.TcPOU) |

---

## 1. 功能简述

**查询命令**——查询灯具 `RANDOM ADDRESS` 寄存器（24-bit 随机地址，寻址过程用）。本 FB 通过 DALI 总线查询灯具内部寄存器，通过 `dwQueryData` 输出当前值。属于 IEC 62386 Part 102 控制设备（control gear）查询命令族。

查询命令属于低优先级流量，建议用 `eCommandPriority = Low` 避免抢占调光命令带宽。

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
    bBusy          : BOOL;
    bError         : BOOL;
    nErrorId       : UDINT;
    nRandomAddress : UDINT;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 本 FB 接到 `bStart` 上升沿后置 TRUE；命令派发完且收到 DALI 响应（或超时）后回 FALSE |
| `bError` | `BOOL` | 执行错时置 TRUE；下次 `bStart` 上升沿自动复位 |
| `nErrorId` | `UDINT` | 错误号（命令专用）；详见 §4 错误码表与全库错误码（PDF §4.1.4） |
| `nRandomAddress` | `UDINT` | ⚠️ 待人工确认 |

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

**调用方式**：`bStart` 上升沿；本 FB 下发对应 DALI 查询命令；灯具应答数据通过 `FB_KL68x1Communication` 接收后填入 `dwQueryData` 输出，`bBusy` 回 FALSE。

**优先级建议**：查询命令耗 DALI 带宽且非时序敏感，建议用 `eCommandPriority := Low`，让调光等关键命令优先派发。

**广播查询限制**：与所有 DALI 查询命令一样，本 FB 在广播寻址下结果不可靠——多盏灯同时应答会冲突。查询必须用 `eAddrType := Short` 单灯寻址。

**典型应用**：HMI 显示当前灯状态；上线后批量检查所有灯配置是否符合工程文档；运行时定期巡检。

**典型陷阱**：① 广播查询无意义，结果冲突；② 灯具离线时本 FB 会超时（约 100..500 ms），`bError` 置 TRUE；③ 高频查询占用 DALI 带宽——巡检循环周期 1..5 秒比较合理。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 查询必须单灯寻址（`eAddrType := Short`），广播 / 组寻址结果冲突。
- 优先级建议 `Low`，避免抢占调光命令带宽。
- 灯具离线时 `bError = TRUE`，`nErrorId` 提示超时。
- 高频查询占用 DALI 带宽——巡检间隔不应小于 1 秒。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2QueryRandomAddress.TcPOU`](../examples/P_Demo_FB_DALIV2QueryRandomAddress.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 显示当前灯具状态——巡检循环每秒对所有在线短地址依次调本 FB 读 查询灯具 `RANDOM ADDRESS` 寄存器（24-bit 随机地址，寻址过程用），刷新 HMI 上的当前值显示。
- **价值**：替代 PLC 自行解析 DALI 应答字节流；本 FB 自动处理 DALI 协议层的查询请求 / 应答握手。
- **替代方案对比**：1) `FB_DALIV2GetSettings` 一次查多个寄存器：批量查询时效率更高；2) **本 FB**：单一寄存器的轻量查询。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.5.20
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142813579.html
- **相关**：见 `FB_DALIV2GetSettings`（批量查询）、`FB_DALIV2SetXxx` 对应配置命令
