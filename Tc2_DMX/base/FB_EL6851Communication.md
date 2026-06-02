# FB_EL6851Communication

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DMX` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Base` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/55166859.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EL6851Communication.TcPOU`](../examples/P_Demo_FB_EL6851Communication.TcPOU) |

---

## 1. 功能简述

EL6851 DMX 端子的通讯核心功能块（**已过时 / Outdated**，新工程请改用 `FB_EL6851CommunicationEx`）。功能与 Ex 版本相同：所有对 EL6851 的访问都经过它，既循环发送 DMX 数据，也把各 DMX/RDM 命令功能块排入 `ST_DMXCommandBuffer` 缓冲区后逐条转发给端子。每个 EL6851 对应一个本功能块实例和一个 `ST_DMXCommandBuffer`。它与 Ex 版的关键差异是：对超长 RDM 应答（参数数据过长，错误码 `0x801C`）支持不全，因此被 Ex 版取代。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  wSourceManufacturerId : WORD := 16#42_41;
  dwSourceDeviceId      : DWORD := 16#12_13_14_15;
  bEnableSendingData    : BOOL := TRUE;
  bSetCycleMode         : BOOL := TRUE;
  bSendDefaultData      : BOOL;
  uiDataLength          : UINT;
  dwOptions             : DWORD;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `wSourceManufacturerId` | `WORD` | `16#42_41` | DMX 主站的唯一厂商 ID。按 ESTA 规定 Beckhoff 为 `0x4241`。 |
| `dwSourceDeviceId` | `DWORD` | `16#12_13_14_15` | DMX 主站的唯一设备 ID，可自由分配。 |
| `bEnableSendingData` | `BOOL` | `TRUE` | 端子处于 CycleMode（`bCycleMode` 输出为 TRUE）时，用本输入开启（TRUE）或阻断（FALSE）数据发送。 |
| `bSetCycleMode` | `BOOL` | `TRUE` | 激活 CycleMode。CycleMode 下才能发循环过程数据；发 RDM/DMX 命令前必须关闭 CycleMode。 |
| `bSendDefaultData` | `BOOL` | - | 该输入为 TRUE 时，在 CycleMode 下发送默认值。 |
| `uiDataLength` | `UINT` | - | 仅在 CycleMode 激活时有意义，指定 DMX512 帧长度（字节数）。 |
| `dwOptions` | `DWORD` | - | 选项（当前未使用）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  bError                     : BOOL;
  udiErrorId                 : UDINT;
  bCycleMode                 : BOOL;
  byBufferDemandMeter        : BYTE;
  byBufferMaximumDemandMeter : BYTE;
  uiBufferOverflowCounter    : UINT;
  bLineIsBusy                : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | 命令执行出错时置 TRUE，命令专用错误码在 `udiErrorId`。仅当 `bBusy` 为 FALSE 时有效。 |
| `udiErrorId` | `UDINT` | 最近一次执行命令的命令专用错误码。仅当 `bBusy` 为 FALSE 时有效（见 §4 错误码）。 |
| `bCycleMode` | `BOOL` | CycleMode 激活时为 TRUE（参见 `bSetCycleMode` 输入）。 |
| `byBufferDemandMeter` | `BYTE` | 对应缓冲区当前占用率（0 - 100%）。 |
| `byBufferMaximumDemandMeter` | `BYTE` | 对应缓冲区历史最大占用率（0 - 100%）。 |
| `uiBufferOverflowCounter` | `UINT` | 迄今为止的缓冲区溢出次数。 |
| `bLineIsBusy` | `BOOL` | 本功能块正在处理 DMX/RDM 命令期间保持置位。 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
  stEL6851InData  : ST_EL6851InData;
  stEL6851OutData : ST_EL6851OutData;
  stCommandBuffer : ST_DMXCommandBuffer;
  arrProcessData  : ARRAY [1..512] OF BYTE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stEL6851InData` | `ST_EL6851InData` | EL6851 输入过程映像中的结构，用于 EL6851 到 PLC 的通讯。需与端子输入过程数据链接。 |
| `stEL6851OutData` | `ST_EL6851OutData` | EL6851 输出过程映像中的结构，用于 PLC 到 EL6851 的通讯。需与端子输出过程数据链接。 |
| `stCommandBuffer` | `ST_DMXCommandBuffer` | 命令缓冲区结构的引用；各 DMX/RDM 命令功能块与本功能块通过它交换命令。 |
| `arrProcessData` | `ARRAY [1..512] OF BYTE` | 要循环发给灯具的数据通过该变量传入。需先激活 CycleMode（见 `bSetCycleMode`）。 |

## 3. 行为说明

本功能块需在 PLC 任务中**每周期调用一次**（电平驱动，无上升沿触发），行为与 `FB_EL6851CommunicationEx` 完全一致。两种工作模式互斥：循环发送 DMX 灯光数据时置 `bEnableSendingData := TRUE`、`bSetCycleMode := TRUE`、`bSendDefaultData := FALSE`、`uiDataLength` 设为帧长，数据写入 `arrProcessData`；发送 RDM 命令时置 `bEnableSendingData := FALSE`、`bSetCycleMode := FALSE`，此时各 RDM 命令功能块把命令排入 `stCommandBuffer`，本功能块逐条取出转发，`bLineIsBusy` 在处理期间为 TRUE。缓冲区占用率由 `byBufferDemandMeter`（当前）与 `byBufferMaximumDemandMeter`（峰值）反映，`uiBufferOverflowCounter` 持续增长说明命令产生过快需借助 System Manager 分析任务负载，必要时把本功能块放到更快的高优先级任务。出错时 `bError := TRUE`、`udiErrorId` 给出错误码，输出仅在 `bLineIsBusy` 为 FALSE 时有效。**与 Ex 版的实质区别**：本（旧）版对超长 RDM 应答处理不全，遇到参数数据过长会返回 `0x801C` 并截断数据，新工程一律改用 `FB_EL6851CommunicationEx`。

## 4. 错误码 / 返回值

本功能块通过 `bError` + `udiErrorId` 报告错误。`udiErrorId = 0` 表示无错。Tc2_DMX 全库共用同一张命令专用错误码表（PDF §4.1.3 Error codes），常见值：

| 错误码（hex） | 十进制 | 含义 |
|---|---|---|
| `0x0000` | 0 | 无错误。 |
| `0x8001` | 32769 | DMX 端子无应答。 |
| `0x8002` | 32770 | DMX 设备无应答。 |
| `0x8003` | 32771 | 通讯缓冲区溢出。 |
| `0x8004` | 32772 | 通讯功能块无应答。 |
| `0x800A` | 32778 | 端子处于 CycleMode，无法发送 RDM 命令。 |
| `0x800D` | 32781 | 端子不在 CycleMode，无法发送过程数据。 |
| `0x801C` | 32796 | RDM 应答参数数据过长，无法收全，须改用 `FB_EL6851CommunicationEx()`。 |
| `0x801D` | 32797 | 访问 PDO 的 ADS 地址无效（是否把 KL6851 的 `AdsAddr` 结构映射到了对应变量？）。 |
| `0x801E` | 32798 | 读 PDO 时发生 ADS 错误。 |

> 完整错误码表（含 `0x8005`–`0x801B` 等参数越界与 RDM 应答类错误）见本库 §4 错误码专页与 PDF §4.1.3。`0x801C` 正是本旧版被 Ex 版取代的原因。

## 5. 使用注意 / 常见坑

- **已过时**：新工程一律用 `FB_EL6851CommunicationEx`；本文档仅为维护使用旧版的存量工程提供参考。
- **每个 EL6851 只能有一个本功能块实例 + 一个 `ST_DMXCommandBuffer`**：多实例同时访问会导致命令错乱。
- **CycleMode 与 RDM 互斥**：CycleMode 下发 RDM 得 `0x800A`，非 CycleMode 下发循环数据得 `0x800D`。
- **遇到 `0x801C`（应答数据过长）必须迁移到 Ex 版**：旧版无法收全超长 RDM 应答。（工程经验补充）
- `stEL6851InData` / `stEL6851OutData` 须在 I/O 里和 EL6851 过程数据正确链接，否则出现 `0x801D` / `0x801E`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EL6851Communication.TcPOU`](../examples/P_Demo_FB_EL6851Communication.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：维护一套早期用 `FB_EL6851Communication` 搭建的舞台灯光系统，需要看懂 / 改动其循环数据与 RDM 转发逻辑，但暂不重构。
- **价值**：提供旧版功能块的完整中文接口与行为说明，便于维护存量工程；同时明确指出迁移到 Ex 版的收益（超长 RDM 应答支持）。
- **替代方案对比**：
  - **`FB_EL6851CommunicationEx`**：官方推荐，超长 RDM 应答支持完整——所有新工程的正确选择。
  - 多个功能块各自直接读写 EL6851 过程映像：会相互踩踏，命令丢失。
  - **本（旧）功能块**：仅用于不改动旧工程的维护场景。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf) §4.1.2.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/55166859.html
- **相关 FB / FC**：`FB_EL6851CommunicationEx`（推荐替代版本）、`FB_DMXSendRDMCommand`（往缓冲区排 RDM 命令）、`FB_DMXDiscovery`（设备搜索）
