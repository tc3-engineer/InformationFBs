# FB_DALIV2RemoveFromGroup

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
| Example | [`examples/P_Demo_FB_DALIV2RemoveFromGroup.TcPOU`](../examples/P_Demo_FB_DALIV2RemoveFromGroup.TcPOU) |

---

## 1. 功能简述

**把镇流器从 DALI 组中移除的配置命令**——`FB_DALIV2AddToGroup` 的对应反向操作。本 FB 把 `nAddr` 寻址到的镇流器从 `nGroup` 指定的组（0..15）中移除。镇流器原本属于的其它组归属保留——本命令只清这一组成员。

运行时调整 DALI 分组的核心命令（工程上线后某盏灯被改作他用 / 房间合并改造等场景）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart           : BOOL;
    nAddr            : BYTE;
    eAddrType        : E_DALIV2AddrType        := eDALIV2AddrTypeShort;
    eCommandPriority : E_DALIV2CommandPriority := eDALIV2CommandPriorityMiddle;
    nGroup           : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿 |
| `nAddr` | `BYTE` | — | 目标地址：单灯 short address 0..63，或组号 0..15，或 `eAddrType = Broadcast` 时忽略 |
| `eAddrType` | `E_DALIV2AddrType` | `eDALIV2AddrTypeShort` | 寻址类型：`eDALIV2AddrTypeShort`（单灯）/ `eDALIV2AddrTypeGroup`（组）/ `eDALIV2AddrTypeBroadcast`（全线广播） |
| `eCommandPriority` | `E_DALIV2CommandPriority` | `eDALIV2CommandPriorityMiddle` | 命令优先级：`High` / `Middle` / `Low`，决定本命令在 `FB_KL68x1Communication` 三优先级队列中的派发顺序 |
| `nGroup` | `BYTE` | — | 要从该组中移除的组号（0..15） |

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

**调用方式**：`bStart` 上升沿；本 FB 写 DTR0 = `nGroup`，下发 `REMOVE FROM GROUP n` 命令，灯具更新内部 16-bit 组归属位图（清除对应 bit）写回 EEPROM。

**EEPROM 写次数**：与 `FB_DALIV2AddToGroup` 一样，EEPROM 额定 10 万次写入；分组调整应是低频操作，不应循环调用。

**与 `FB_DALIV2AddToGroup` 的对偶**：本 FB 只清这一组的 bit；其它组归属保留。要让镇流器从所有组移除可循环调用本 FB 16 次（每次一个 nGroup），或更简单地用 `FB_DALIV2Reset` 复位灯具到出厂状态（同时也清除其它配置如 `FADE TIME` / 短地址，慎用）。

**广播 / 组寻址下的语义**：`eAddrType := Broadcast` + `nGroup := 5` 让全线所有灯都退出组 5，用于运行时收回某组成员资格。

**典型陷阱**：① 在循环里改不同组要等 `bBusy = FALSE` 才下一次上升沿；② 写完后用 `FB_DALIV2QueryGroups` 确认实际生效。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- EEPROM 写次数有限，分组调整应低频。
- 本 FB 只清 `nGroup` 一组；其它组归属不变。
- `nGroup > 15` 灯具忽略，本 FB 不报错。
- 写完用 `FB_DALIV2QueryGroups0UpTo7` / `_8UpTo15` 验证实际生效。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2RemoveFromGroup.TcPOU`](../examples/P_Demo_FB_DALIV2RemoveFromGroup.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：DALI 工程运行时调整：某盏灯原本属于走廊照明组（组 1），后来房间改造把它划入会议室组（组 5），本 FB 把它从组 1 移除，再用 `FB_DALIV2AddToGroup` 加到组 5。
- **价值**：运行时灵活调整 DALI 分组不需要重置灯具；保留 `FADE TIME` 等其它配置不变。
- **替代方案对比**：1) `FB_DALIV2Reset`：复位灯具到出厂状态，所有配置清空，过于激进；2) 手动用厂家工具：运维成本高；3) **本 FB**：运行时调整组归属的标准工具。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142787979.html
- **相关**：[`FB_DALIV2AddToGroup`](FB_DALIV2AddToGroup.md)、[`FB_DALIV2QueryGroups`](../part102_low_queries/FB_DALIV2QueryGroups.md)、[`FB_DALIV2Reset`](FB_DALIV2Reset.md)
