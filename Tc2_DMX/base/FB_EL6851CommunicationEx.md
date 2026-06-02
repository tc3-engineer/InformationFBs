# FB_EL6851CommunicationEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DMX` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Base` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/2669681803.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EL6851CommunicationEx.TcPOU`](../examples/P_Demo_FB_EL6851CommunicationEx.TcPOU) |

---

## 1. 功能简述

EL6851 DMX 端子的通讯核心功能块（推荐版本，取代已过时的 `FB_EL6851Communication`）。所有对 EL6851 的访问都必须经过它，既负责把循环 DMX 数据帧发给灯具，也负责把 RDM 命令逐条发出。各类 DMX/RDM 命令功能块不直接访问 EL6851 过程映像，而是把命令写进一个 `ST_DMXCommandBuffer` 缓冲区；本功能块从缓冲区里按顺序取出命令转发给 EL6851，从而避免多个功能块同时抢占过程映像。每个 EL6851 对应**一个**本功能块实例和**一个** `ST_DMXCommandBuffer` 变量。

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
| `wSourceManufacturerId` | `WORD` | `16#42_41` | DMX 主站（master）的唯一厂商 ID。按 ESTA 规定，Beckhoff 的厂商 ID 为 `0x4241`。 |
| `dwSourceDeviceId` | `DWORD` | `16#12_13_14_15` | DMX 主站的唯一设备 ID，可自由分配。 |
| `bEnableSendingData` | `BOOL` | `TRUE` | 当端子处于 CycleMode（`bCycleMode` 输出为 TRUE）时，用本输入开启（TRUE）或阻断（FALSE）数据发送。 |
| `bSetCycleMode` | `BOOL` | `TRUE` | 激活 CycleMode。只有在 CycleMode 下才能把循环过程数据发给灯具；要发 RDM/DMX 命令则必须先关闭 CycleMode。 |
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
| `bError` | `BOOL` | 命令执行出错时置 TRUE，命令专用错误码在 `udiErrorId` 中。仅当 `bBusy` 为 FALSE 时有效。 |
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

本功能块需在 PLC 任务中**每周期调用一次**（电平驱动，无上升沿触发）。两种工作模式由输入位决定，且互斥：要循环发送 DMX 灯光数据时，置 `bEnableSendingData := TRUE`、`bSetCycleMode := TRUE`、`bSendDefaultData := FALSE`、`uiDataLength` 设为帧长（字节），灯光数据写入 `arrProcessData`；要发送 RDM 命令时，置 `bEnableSendingData := FALSE`、`bSetCycleMode := FALSE`，此时各 RDM 命令功能块把命令排入 `stCommandBuffer`，本功能块从缓冲区按先后顺序逐条取出转发，`bLineIsBusy` 在处理命令期间保持 TRUE。缓冲区占用率可通过 `byBufferDemandMeter`（当前）与 `byBufferMaximumDemandMeter`（历史峰值）观察；若 `uiBufferOverflowCounter` 持续增长，说明命令产生速度超过转发速度，应借助 TwinCAT System Manager 分析 PLC 任务负载。必要时可把本功能块放到一个更快、优先级更高的独立任务里调用，使其优先级高于产生 RDM 命令的任务。出错时 `bError := TRUE`、`udiErrorId` 给出命令专用错误码，这些输出仅在 `bLineIsBusy`/`bBusy` 为 FALSE 时才有效。

## 4. 错误码 / 返回值

本功能块通过 `bError` + `udiErrorId` 报告错误。`udiErrorId = 0` 表示无错。Tc2_DMX 全库共用同一张命令专用错误码表（PDF §4.1.3 Error codes）：

| 错误码（hex） | 十进制 | 含义 |
|---|---|---|
| `0x0000` | 0 | 无错误。 |
| `0x8001` | 32769 | DMX 端子无应答。 |
| `0x8002` | 32770 | DMX 设备无应答。 |
| `0x8003` | 32771 | 通讯缓冲区溢出。 |
| `0x8004` | 32772 | 通讯功能块无应答。 |
| `0x8005` | 32773 | `byPortId` 参数超出有效范围。 |
| `0x8006` | 32774 | 校验和错误。 |
| `0x800A` | 32778 | 端子处于 CycleMode，无法发送 RDM 命令。 |
| `0x800D` | 32781 | 端子不在 CycleMode，无法发送过程数据。 |
| `0x801D` | 32797 | 访问 PDO 的 ADS 地址无效（是否把 KL6851 的 `AdsAddr` 结构映射到了对应变量？）。 |
| `0x801E` | 32798 | 读 PDO 时发生 ADS 错误。 |

> 完整错误码表（含 `0x8007`–`0x801C` 等 RDM 应答类错误）见本库 §4 错误码专页与 PDF §4.1.3。与本通讯功能块最相关的是 `0x8003`（缓冲区溢出）、`0x800A`/`0x800D`（模式冲突）和 `0x801D`/`0x801E`（端子映射/ADS）。

## 5. 使用注意 / 常见坑

- **每个 EL6851 只能有一个本功能块实例 + 一个 `ST_DMXCommandBuffer`**：多实例同时访问同一端子过程映像会导致命令错乱。
- **CycleMode 与 RDM 互斥**：在 CycleMode 下发 RDM 命令会得到错误码 `0x800A`；不在 CycleMode 下发循环过程数据会得到 `0x800D`。切换模式时通过 `bSetCycleMode` 控制。
- **缓冲区溢出要当作设计问题处理**：`uiBufferOverflowCounter` 增长说明 RDM 命令产生过快或 PLC 任务太慢，应把本功能块移到更快的高优先级任务，而不是简单忽略。（工程经验补充）
- `udiErrorId` 仅在 `bLineIsBusy` 落回 FALSE 后才反映最近一次命令的真实结果，命令处理期间读到的值无意义。（工程经验补充）
- `stEL6851InData` / `stEL6851OutData` 必须在 System Manager / TwinCAT I/O 里和 EL6851 端子的过程数据正确链接，否则会出现 `0x801D` / `0x801E`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EL6851CommunicationEx.TcPOU`](../examples/P_Demo_FB_EL6851CommunicationEx.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：剧场 / 舞台灯光系统用一块 EL6851 接 DMX512 总线驱动几十路调光器与染色灯。PLC 每周期把各灯通道亮度写进 `arrProcessData` 循环发出；调试 / 维护阶段临时切到 RDM 模式给某盏灯改起始地址或读灯泡寿命。
- **价值**：把"灯光数据循环发送"和"RDM 命令排队转发"统一收敛到一个功能块，业务代码只管写 `arrProcessData` 或调用各 RDM 功能块，不必自己处理过程映像争用、命令排队、缓冲区计量。
- **替代方案对比**：
  - 用已过时的 `FB_EL6851Communication`：可工作，但对超长 RDM 应答（参数数据过长，错误码 `0x801C`）支持不全，新工程不应再用。
  - 多个功能块各自直接读写 EL6851 过程映像：会相互踩踏，命令丢失，无法保证时序。
  - **本功能块**：官方推荐的单点通讯入口，自带缓冲区计量与溢出计数。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf) §4.1.2.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/2669681803.html
- **相关 FB / FC**：`FB_EL6851Communication`（已过时的旧版）、`FB_DMXSendRDMCommand`（往缓冲区排 RDM 命令）、`FB_DMXDiscovery`（设备搜索）
