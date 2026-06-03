# FB_DMXDiscUnMute

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DMX` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Discovery Messages` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/55177227.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DMXDiscUnMute.TcPOU`](../examples/P_Demo_FB_DMXDiscUnMute.TcPOU) |

---

## 1. 功能简述

复位某个 DMX 设备的 mute（静音）标志。mute 标志决定该设备是否响应 `FB_DMXDiscUniqueBranch()` 命令：mute 未置位时响应，置位后不响应。本 FB 把标志清掉，使设备重新参与二分发现搜索。

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
  bBusy         : BOOL;
  bError        : BOOL;
  udiErrorId    : UDINT;
  wControlField : WORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 功能块激活后置位，直到命令执行完成。对某些错误（如参数错误），`bError` 会在 `bStart` 上升沿后立即置位而 `bBusy` 不切到 TRUE。 |
| `bError` | `BOOL` | 命令执行出错时置 TRUE，命令专用错误码在 `udiErrorId`。仅当 `bBusy` 为 FALSE 时有效。 |
| `udiErrorId` | `UDINT` | 最近一次命令的命令专用错误码。仅当 `bBusy` 为 FALSE 时有效（见 §4 错误码）。 |
| `wControlField` | `WORD` | 命令完成（`bBusy` 为 FALSE）后给出设备返回的控制字段（control field），其各位含义见 PDF 中的位定义表。 |

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

`bStart` 上升沿启动：`bBusy` 置 TRUE，功能块把 DISCOVERY UN-MUTE 命令排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令完成后 `bBusy` 落回 FALSE，`wControlField` 给出设备控制字段，`bError` / `udiErrorId` 可读。复位 mute 后设备重新响应 UniqueBranch 搜索，常用于开始一轮全新发现前把所有设备恢复到可被发现状态。通常由高层 `FB_DMXDiscovery` 自动调用。必须给 `bStart` 上升沿，活动期间后续上升沿被忽略；发送时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`）。

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

- **通常无需手动调用**：高层 `FB_DMXDiscovery` 已封装整套发现流程，仅在自写发现逻辑时才用本 FB。
- 与 `FB_DMXDiscMute` 配对：本 FB 复位 mute，置位用 Mute 版。
- 开始全新一轮发现前，对广播地址 UnMute 可让所有设备重新可被发现。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DMXDiscUnMute.TcPOU`](../examples/P_Demo_FB_DMXDiscUnMute.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：自定义发现流程结束后，要把先前 mute 掉的设备全部恢复，以便下一轮搜索或让其它控制器也能发现它们。
- **价值**：把 RDM 发现协议中的 un-mute 步骤暴露为单独 FB，配合 Mute / UniqueBranch 实现完全自定义的发现策略。
- **替代方案对比**：
  - 直接用 `FB_DMXDiscovery`：自动管理 mute / un-mute，多数场景首选。
  - 自己拼 `FB_DMXSendRDMCommand` 发 DISCOVERY UN-MUTE：可行但要手填 CC/PID。
  - **本 FB**：发现协议中 un-mute 步骤的专用封装。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf) §4.1.2.3.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/55177227.html
- **相关 FB / FC**：`FB_DMXDiscMute`（置位 mute）、`FB_DMXDiscUniqueBranch`（区间搜索）、`FB_DMXDiscovery`（高层自动发现）
