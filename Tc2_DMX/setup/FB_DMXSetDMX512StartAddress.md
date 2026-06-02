# FB_DMXSetDMX512StartAddress

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DMX` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Setup Messages` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/55193739.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DMXSetDMX512StartAddress.TcPOU`](../examples/P_Demo_FB_DMXSetDMX512StartAddress.TcPOU) |

---

## 1. 功能简述

设置某个 DMX 设备的 DMX512 起始地址，范围 1–512。每个子设备和根设备各占用不同的起始地址。它是把灯具编入 DMX 帧的关键——决定该设备从帧的哪个通道开始取自己的控制数据。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  bStart                     : BOOL;
  wDestinationManufacturerId : WORD;
  dwDestinationDeviceId      : DWORD;
  byPortId                   : BYTE;
  iDMX512Startadresse        : INT;
  dwOptions                  : DWORD := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bStart` | `BOOL` | - | 本输入上升沿激活功能块（触发一次执行）。功能块活动期间（`bBusy = TRUE`）后续上升沿被忽略。 |
| `wDestinationManufacturerId` | `WORD` | - | 唯一厂商 ID，用于寻址目标 DMX 设备。 |
| `dwDestinationDeviceId` | `DWORD` | - | 唯一设备 ID，用于寻址目标 DMX 设备。 |
| `byPortId` | `BYTE` | - | 被寻址 DMX 设备内的通道；子设备（sub-device）通过 Port Id 寻址，根设备的 Port Id 恒为 0。 |
| `iDMX512Startadresse` | `INT` | - | 要设置的 DMX512 起始地址（1–512）。⚠️ 该形参名在 PDF 与库中拼作 `iDMX512Startadresse`（德式拼写，非 `iDMX512StartAddress`），调用时须按此拼写。 |
| `dwOptions` | `DWORD` | `0` | 选项（当前未使用）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  bBusy         : BOOL;
  bError        : BOOL;
  udiErrorId    : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 功能块激活后置位，直到命令执行完成。对某些错误（如参数错误），`bError` 会在 `bStart` 上升沿后立即置位而 `bBusy` 不切到 TRUE。 |
| `bError` | `BOOL` | 命令执行出错时置 TRUE，命令专用错误码在 `udiErrorId`。仅当 `bBusy` 为 FALSE 时有效。 |
| `udiErrorId` | `UDINT` | 最近一次命令的命令专用错误码。仅当 `bBusy` 为 FALSE 时有效（见 §4 错误码）。 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
  stCommandBuffer : ST_DMXCommandBuffer;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stCommandBuffer` | `ST_DMXCommandBuffer` | 与通讯功能块 `FB_EL6851Communication()` / `FB_EL6851CommunicationEx()` 交换命令的缓冲区结构引用。 |

## 3. 行为说明

`bStart` 上升沿启动：`bBusy` 置 TRUE，功能块把 SET DMX_START_ADDRESS 命令（携带目标起始地址）排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `bError` 与 `udiErrorId` 才有效，设备起始地址被改写。起始地址必须落在 1–512，越界会返回错误码 `0x800B`，设置失败会返回 `0x800C`。本 FB 的目标地址形参在 PDF 与库中拼作 `iDMX512Startadresse`（德式拼写）。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。

## 4. 错误码 / 返回值

本功能块通过 `bError` + `udiErrorId` 报告错误。`udiErrorId = 0` 表示无错。Tc2_DMX 全库共用同一张命令专用错误码表（PDF §4.1.3 Error codes），常见值：

| 错误码（hex） | 十进制 | 含义 |
|---|---|---|
| `0x0000` | 0 | 无错误。 |
| `0x8001` | 32769 | DMX 端子无应答。 |
| `0x8002` | 32770 | DMX 设备无应答。 |
| `0x8003` | 32771 | 通讯缓冲区溢出。 |
| `0x8004` | 32772 | 通讯功能块无应答。 |
| `0x8005` | 32773 | `byPortId` 参数超出有效范围。 |
| `0x8006` | 32774 | 校验和错误。 |
| `0x8008` | 32776 | 超时。 |
| `0x800A` | 32778 | 端子处于 CycleMode，无法发送 RDM 命令。 |
| `0x800F` | 32783 | RDM 应答：RDM 报文应答无效。 |
| `0x8010` | 32784 | RDM 应答：设备未实现该命令，无法响应。 |
| `0x8016` | 32790 | RDM 应答：给定参数的值超范围或不支持。 |
| `0x801C` | 32796 | RDM 应答：参数数据（PD）过长，无法收全，需改用 `FB_EL6851CommunicationEx()`。 |

> 完整错误码表（含 `0x8007`–`0x801E` 等参数越界与 RDM 应答类错误）见本库 §4 错误码专页与 PDF §4.1.3。`0x800B` 表示地址超出 1–512；`0x800C` 表示设置 DMX512 起始地址失败。

## 5. 使用注意 / 常见坑

- **形参名是德式拼写 `iDMX512Startadresse`**（不是 `iDMX512StartAddress`）——这是 PDF 与库里的实际命名，写代码要照抄。
- 与 `FB_DMXGetDMX512StartAddress` 配对：设完用 Get 版回读确认。
- 地址范围 1–512，越界 `0x800B`；批量自动编址可改用高层 `FB_DMXDiscovery` 的 `SET_START_ADDRESS` 选项。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DMXSetDMX512StartAddress.TcPOU`](../examples/P_Demo_FB_DMXSetDMX512StartAddress.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：新装或更换灯具后手动编址：按图纸给某盏灯设定它在 DMX 帧里的起始通道（如第 45 通道），使调光台对该地址段的控制落到这盏灯上。
- **价值**：把单台设备的 DMX512 编址做成一次 PLC 调用，配合回读实现可验证的地址配置，免去进设备菜单手拨。
- **替代方案对比**：
  - 进设备本地菜单手设地址：逐台操作、易设错。
  - 用高层 `FB_DMXDiscovery` 自动连续编址：适合批量，但不适合给单台设指定地址。
  - **本 FB**：精确给指定设备设指定地址。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf) §4.1.2.9.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/55193739.html
- **相关 FB / FC**：`FB_DMXGetDMX512StartAddress`（读起始地址）、`FB_DMXDiscovery`（批量自动编址）、`FB_DMXGetSlotInfo`（槽功能）

## 9. 待确认项 (⚠️)

- `FB_DMXSetDMX512StartAddress` 的起始地址形参在 PDF 与库中拼作 `iDMX512Startadresse`（德式拼写），而对应的读取 FB `FB_DMXGetDMX512StartAddress` 输出却拼作 `iDMX512StartAddress`（英式）。两者拼写不一致是 Beckhoff 命名遗留，本文档按 PDF 原文逐字保留。
