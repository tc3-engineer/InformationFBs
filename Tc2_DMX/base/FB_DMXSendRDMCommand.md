# FB_DMXSendRDMCommand

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DMX` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Base` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/2670016523.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DMXSendRDMCommand.TcPOU`](../examples/P_Demo_FB_DMXSendRDMCommand.TcPOU) |

---

## 1. 功能简述

通用 RDM 命令发送功能块：由命令号（Command Class + Parameter Id）和可选的传输参数自由组装并发送任意一条 RDM 命令。当某个具体功能（如读传感器、设地址）没有现成的专用 FB，或需要发厂商自定义 PID 时，用它直接构造原始 RDM 报文。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  bStart                     : BOOL;
  wDestinationManufacturerId : WORD;
  dwDestinationDeviceId      : DWORD;
  byPortId                   : BYTE;
  wSubDevice                 : WORD;
  eCommandClass              : E_DMXCommandClass;
  eParameterId               : E_DMXParameterId;
  byParameterDataLength      : BYTE;
  arrParameterData           : ARRAY [0..255] OF BYTE;
  dwOptions                  : DWORD := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bStart` | `BOOL` | - | 本输入上升沿激活功能块（触发一次执行）。功能块活动期间（`bBusy = TRUE`）后续上升沿被忽略。 |
| `wDestinationManufacturerId` | `WORD` | - | 唯一厂商 ID，用于寻址目标 DMX 设备。 |
| `dwDestinationDeviceId` | `DWORD` | - | 唯一设备 ID，用于寻址目标 DMX 设备。 |
| `byPortId` | `BYTE` | - | 被寻址 DMX 设备内的通道；子设备（sub-device）通过 Port Id 寻址，根设备的 Port Id 恒为 0。 |
| `wSubDevice` | `WORD` | - | 子设备号。带重复模块的设备（如调光柜）用子设备寻址，使参数命令可发给设备内某个具体模块以读 / 设其属性。 |
| `eCommandClass` | `E_DMXCommandClass` | - | 命令类别（CC），指示报文动作（见 `E_DMXCommandClass`）。 |
| `eParameterId` | `E_DMXParameterId` | - | 参数 Id，16 位数字，标识某种参数数据的类型（见 `E_DMXParameterId`）。 |
| `byParameterDataLength` | `BYTE` | - | 参数数据长度（PDL），即参数数据区中后续的字节数；为 `0x00` 时表示无参数数据。 |
| `arrParameterData` | `ARRAY [0..255] OF BYTE` | - | 可变长度的参数数据，内容格式取决于 PID。 |
| `dwOptions` | `DWORD` | `0` | 选项（当前未使用）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  bBusy                  : BOOL;
  bError                 : BOOL;
  udiErrorId             : UDINT;
  byResponseMessageCount : BYTE;
  byResponseDataLength   : BYTE;
  arrResponseData        : ARRAY [0..255] OF BYTE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 功能块激活后置位，直到命令执行完成。对某些错误（如参数错误），`bError` 会在 `bStart` 上升沿后立即置位而 `bBusy` 不切到 TRUE。 |
| `bError` | `BOOL` | 命令执行出错时置 TRUE，命令专用错误码在 `udiErrorId`。仅当 `bBusy` 为 FALSE 时有效。 |
| `udiErrorId` | `UDINT` | 最近一次命令的命令专用错误码。仅当 `bBusy` 为 FALSE 时有效（见 §4 错误码）。 |
| `byResponseMessageCount` | `BYTE` | 指示 DMX 从设备还有更多消息；用 RDM 命令 Get: QUEUED_MESSAGE 读取这些消息。 |
| `byResponseDataLength` | `BYTE` | RDM 命令返回的字节数。 |
| `arrResponseData` | `ARRAY [0..255] OF BYTE` | RDM 命令应答数据，长度可变，格式取决于具体 RDM 命令。 |

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

`bStart` 上升沿启动：`bBusy` 置 TRUE，功能块按 `wDestinationManufacturerId` / `dwDestinationDeviceId` / `byPortId` / `wSubDevice` 寻址目标（子设备），按 `eCommandClass`（GET/SET/DISCOVERY 等）+ `eParameterId`（PID）+ `byParameterDataLength` + `arrParameterData` 组装一条完整 RDM 报文，排入 `stCommandBuffer` 由通讯功能块发出。完成后 `bBusy` 落回 FALSE，应答数据在 `arrResponseData[0..byResponseDataLength-1]`，`byResponseMessageCount` 提示设备是否还有排队消息。这是所有专用 RDM FB 的底层基础——专用 FB 本质上就是预设好 CC/PID 后对它的封装。必须给 `bStart` 上升沿，活动期间后续上升沿被忽略；发送时通讯功能块须处于非 CycleMode。

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

> 完整错误码表（含 `0x8007`–`0x801E` 等参数越界与 RDM 应答类错误）见本库 §4 错误码专页与 PDF §4.1.3。`0x800F`–`0x8019` 是各类 RDM 应答错误（命令未实现、参数越界、子设备未知等），含义取决于所发 PID。

## 5. 使用注意 / 常见坑

- **这是最底层的通用 RDM 接口**：要自己查 RDM/ESTA E1.20 标准确定 CC、PID、参数数据格式，比专用 FB 难用但最灵活。
- 应答可能超长（`0x801C`）：参数数据过长时必须用 `FB_EL6851CommunicationEx` 做通讯核心，旧版 `FB_EL6851Communication` 收不全。
- `byResponseMessageCount > 0` 表示设备还有排队消息，需再用 Get: QUEUED_MESSAGE 取出。（工程经验补充）
- 优先用专用 FB（如 `FB_DMXGetSensorValue`）：它们已经把 CC/PID 设好，不易出错。仅在没有专用 FB 时才用本 FB。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DMXSendRDMCommand.TcPOU`](../examples/P_Demo_FB_DMXSendRDMCommand.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：某品牌灯具支持一个非标准的厂商自定义 PID（例如读取灯具内部温度曲线），Tc2_DMX 没有对应的专用 FB。
- **价值**：无需等 Beckhoff 出专用 FB，直接按 RDM 标准填 CC/PID/参数即可发任意命令并取回原始应答，覆盖全部 RDM 能力。
- **替代方案对比**：
  - 等 / 找专用 FB：覆盖不到厂商自定义 PID。
  - 外接 RDM 控台发命令：进不了 PLC 逻辑。
  - **本 FB**：PLC 内构造任意 RDM 报文，最灵活。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf) §4.1.2.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/2670016523.html
- **相关 FB / FC**：`FB_EL6851CommunicationEx`（通讯核心）、各专用 RDM FB（`FB_DMXGet*` / `FB_DMXSet*`，都是本 FB 的封装）、`E_DMXCommandClass` / `E_DMXParameterId`（枚举）
