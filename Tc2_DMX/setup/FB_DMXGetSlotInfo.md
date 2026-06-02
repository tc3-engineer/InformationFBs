# FB_DMXGetSlotInfo

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DMX` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Setup Messages` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/2670492043.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DMXGetSlotInfo.TcPOU`](../examples/P_Demo_FB_DMXGetSlotInfo.TcPOU) |

---

## 1. 功能简述

查询某个 DMX 设备各 DMX512 槽（slot）的基本功能信息。一次性返回一个最多 46 元素的 `ST_DMXSlotInfo` 数组，描述设备占用的每个槽的功能类型（如颜色、强度、位置等），使控制器了解每个 DMX 通道控制什么。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  bStart                     : BOOL;
  wDestinationManufacturerId : WORD;
  dwDestinationDeviceId      : DWORD;
  byPortId                   : BYTE;
  dwOptions                  : DWORD := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bStart` | `BOOL` | - | 本输入上升沿激活功能块（触发一次执行）。功能块活动期间（`bBusy = TRUE`）后续上升沿被忽略。 |
| `wDestinationManufacturerId` | `WORD` | - | 唯一厂商 ID，用于寻址目标 DMX 设备。 |
| `dwDestinationDeviceId` | `DWORD` | - | 唯一设备 ID，用于寻址目标 DMX 设备。 |
| `byPortId` | `BYTE` | - | 被寻址 DMX 设备内的通道；子设备（sub-device）通过 Port Id 寻址，根设备的 Port Id 恒为 0。 |
| `dwOptions` | `DWORD` | `0` | 选项（当前未使用）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  bBusy             : BOOL;
  bError            : BOOL;
  udiErrorId        : UDINT;
  arrSlotInfos      : ARRAY [0..45] OF ST_DMXSlotInfo;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 功能块激活后置位，直到命令执行完成。对某些错误（如参数错误），`bError` 会在 `bStart` 上升沿后立即置位而 `bBusy` 不切到 TRUE。 |
| `bError` | `BOOL` | 命令执行出错时置 TRUE，命令专用错误码在 `udiErrorId`。仅当 `bBusy` 为 FALSE 时有效。 |
| `udiErrorId` | `UDINT` | 最近一次命令的命令专用错误码。仅当 `bBusy` 为 FALSE 时有效（见 §4 错误码）。 |
| `arrSlotInfos` | `ARRAY [0..45] OF ST_DMXSlotInfo` | 设备各 DMX512 槽的功能信息数组（最多 46 个，索引 0..45，见 `ST_DMXSlotInfo`）。 |

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

`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET SLOT_INFO 命令排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `arrSlotInfos[0..45]` 填入设备各槽的功能信息（每项含槽类型、槽定义等），`bError` 与 `udiErrorId` 才有效。它一次给出全部槽的功能类型枚举，是把 DMX 帧通道映射到具体功能的基础；要拿可读文本名则配合 `FB_DMXGetSlotDescription`。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。

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

> 完整错误码表（含 `0x8007`–`0x801E` 等参数越界与 RDM 应答类错误）见本库 §4 错误码专页与 PDF §4.1.3。

## 5. 使用注意 / 常见坑

- **最多 46 个槽**：数组上界 45；占用槽更多的设备需结合 personality 信息分析。
- 给的是功能类型枚举；可读文本名用 `FB_DMXGetSlotDescription` 逐槽读取。
- 与 personality 相关：切换 personality 后槽功能可能变化。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DMXGetSlotInfo.TcPOU`](../examples/P_Demo_FB_DMXGetSlotInfo.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：自动构建通道映射表：一次读出某灯所有槽的功能类型，PLC 据此自动把各 DMX 通道关联到颜色 / 强度 / 位置等控制变量，无需人工逐通道配置。
- **价值**：一次调用拿到全部槽功能，自动化通道映射，比逐槽 `FB_DMXGetSlotDescription` 更快地建立通道—功能对应关系。
- **替代方案对比**：
  - 逐槽用 `FB_DMXGetSlotDescription`：要发多条命令、慢。
  - 人工查手册配通道映射：型号多时工作量大。
  - **本 FB**：一次读全部槽功能类型。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf) §4.1.2.9.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/2670492043.html
- **相关 FB / FC**：`FB_DMXGetSlotDescription`（单槽可读文本）、`FB_DMXGetDMX512PersonalityDescription`（工作模式）、`ST_DMXSlotInfo`（返回结构）
