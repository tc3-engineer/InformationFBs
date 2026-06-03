# FB_DALIV2AddToGroup

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
| Example | [`examples/P_Demo_FB_DALIV2AddToGroup.TcPOU`](../examples/P_Demo_FB_DALIV2AddToGroup.TcPOU) |

---

## 1. 功能简述

**把镇流器加入 DALI 组的配置命令**——DALI Part 102 控制设备支持 16 个组（0..15），每个镇流器可同时属于多个组。本 FB 把 `nAddr`（短地址 / 组 / 广播）寻址到的镇流器加入由 `nGroup` 指定的组（0..15）。加入后该镇流器会响应针对该组的所有 DALI 命令（如组调光、组关灯、组场景调用）。

调试阶段批量配置 DALI 网络分组的核心 FB——通常在工程初始化时按楼层 / 房间 / 功能区批量调用一组本 FB，把镇流器分到对应的 DALI 组里。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart           : BOOL;
    nAddr            : BYTE;
    eAddrType        : E_DALIV2AddrType := eDALIV2AddrTypeShort;
    eCommandPriority : E_DALIV2CommandPriority := eDALIV2CommandPriorityMiddle;
    nGroup           : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿 |
| `nAddr` | `BYTE` | — | 目标镇流器地址：单灯 short address 0..63，或目标组号（让组内所有灯加入新组）|
| `eAddrType` | `E_DALIV2AddrType` | `eDALIV2AddrTypeShort` | 寻址类型；最常用 `Short` 给单灯加组，也可 `Group` / `Broadcast` 批量操作 |
| `eCommandPriority` | `E_DALIV2CommandPriority` | `eDALIV2CommandPriorityMiddle` | 命令优先级 |
| `nGroup` | `BYTE` | — | 目标组号（0..15）。镇流器原本属于的其它组保留——本命令只"加入新组"，不"清除旧组成员"|

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
| `bBusy` | `BOOL` | 命令派发中 |
| `bError` | `BOOL` | 执行错时 TRUE |
| `nErrorId` | `UDINT` | 错误号 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stCommandBuffer : ST_DALIV2CommandBuffer;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `stCommandBuffer` | `ST_DALIV2CommandBuffer` | 与对应 KL68x1 通信 FB 共享 |

## 3. 行为说明

**调用方式**：`bStart` 上升沿触发；本 FB 在 DTR0 寄存器里写入 `nGroup`（用 SetDTR0 命令），然后下发 `STORE DTR AS GROUPS 0-7` 或 `STORE DTR AS GROUPS 8-15` 命令（按 `nGroup` < 8 还是 ≥ 8 分两次寻址），让灯具把分组位图写入 EEPROM。命令派发完 `bBusy → FALSE`。

**多组归属**：DALI 镇流器内部用一个 16-bit 位图记录"我属于哪些组"——bit `n` 置位表示属于组 n。本 FB 仅 "set bit `nGroup`"，原本属于的其它组不动。要清除某组归属用 `FB_DALIV2RemoveFromGroup`。

**EEPROM 写次数限制**：DALI 镇流器 EEPROM 通常额定 10 万次写入。频繁调用本 FB 可能损耗 EEPROM——工程上分组应该是一次性配置（工程上线时执行），不应循环 / 周期性调用。一旦写入失电保护。

**批量配置流程**：工程初始化阶段，按"每盏灯属于哪几组"的设计表，循环对每盏灯（短地址 0..63）调本 FB 多次（每次一个组号）。例如灯 #5 应属于组 1 / 组 3 → 调两次本 FB（`nAddr := 5`, `nGroup := 1`）和（`nAddr := 5`, `nGroup := 3`）。

**广播 / 组寻址下的语义**：`eAddrType := eDALIV2AddrTypeBroadcast` + `nGroup := 0` 让所有灯加入组 0（"全员组"），用于快速一键控所有灯；`eAddrType := eDALIV2AddrTypeGroup` + `nAddr := 1` + `nGroup := 5` 让组 1 中所有灯也加入组 5（用于"扩展归属"）。

**典型陷阱**：① `nGroup > 15` 命令仍下发但灯具忽略，本 FB 不报错（建议 PLC 编译期校验）；② 在循环中连续对同一灯调用本 FB 改不同组 → 注意每次都要等 `bBusy = FALSE` 才能下一次上升沿（典型 50..100 ms）；③ 不知道当前灯的分组状况就 Add → 灯可能属于不该属于的组（先用 `FB_DALIV2QueryGroups` 查询当前状态再决定操作）。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 缓冲区溢出 | 任务节拍 |
| `16#1xxx` | 设备无响应 | `nAddr` 确认 |
| `16#2xxx` | EEPROM 写失败（极少见）| 检查灯具供电与寿命 |

## 5. 使用注意 / 常见坑

- **分组是一次性配置**，避免周期性调用本 FB 损耗 EEPROM。
- **本 FB 不清除原有组归属**——只"加"。清除用 `FB_DALIV2RemoveFromGroup`；要完全重设分组用 `FB_DALIV2Reset` 把灯具复位再分组。
- **`nGroup` 必须 0..15**；越界灯具忽略不报错，PLC 端要自校验。
- **写完后立即查询分组状态**用 `FB_DALIV2QueryGroups` / `FB_DALIV2QueryGroups0UpTo7` / `FB_DALIV2QueryGroups8UpTo15` 确认写入成功（工程经验补充）。
- **DTR0 寄存器在多 FB 间是共享的**——本 FB 写 DTR0 时若同时有其它 FB（如 `FB_DALIV2SetFadeTime`）也在写 DTR0，两次操作之间需等待第一条完成。同优先级队列按 FIFO 派发能保证顺序，但跨优先级（一个 High、一个 Middle）顺序不确定。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2AddToGroup.TcPOU`](../examples/P_Demo_FB_DALIV2AddToGroup.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：DALI 工程初始化阶段——把刚装上线、还没分组的镇流器按设计文档分配到组里。后续业务命令几乎全部基于组（`eAddrType := Group`），所以分组质量直接决定整套系统好不好用。
- **价值**：替代手动用 KS2000 工具或厂家专用 DALI 配置软件（每个镇流器都要单独点选）；PLC 程序里一次性批量配，工程版本控制与重现都简单。
- **替代方案对比**：1) 厂家 DALI 配置工具（如 Tridonic masterCONFIGURATOR）：可视化 GUI，但工程参数与 PLC 项目分家，运维复杂；2) `FB_DALIV2RemoveFromGroup` + 重新加：用于运行时调整；3) `FB_DALIV2Reset` 复位灯具后重分组：用于完全重新规划；4) **本 FB**：工程上线批量分组的标准工具。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142786443.html
- **相关**：[`FB_DALIV2RemoveFromGroup`](FB_DALIV2RemoveFromGroup.md)（移出组）、[`FB_DALIV2QueryGroups`](../part102_low_queries/FB_DALIV2QueryGroups.md)（查询当前组归属）、[`FB_DALIV2Reset`](FB_DALIV2Reset.md)（复位灯具到出厂状态）
