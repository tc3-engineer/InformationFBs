# FB_DMXGetSensorDefinition

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DMX` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Sensor Parameter Messages` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/2670484363.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DMXGetSensorDefinition.TcPOU`](../examples/P_Demo_FB_DMXGetSensorDefinition.TcPOU) |

---

## 1. 功能简述

查询某个 DMX 设备内指定传感器的定义。一台设备可带多个传感器（温度、电压、风扇转速等），本 FB 按传感器编号读回该传感器的定义（类型、单位、量程上下限、是否支持记录最值等），填入 `ST_DMXSensorDefinition`，使控制器知道如何解释传感器读数。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  bStart                     : BOOL;
  wDestinationManufacturerId : WORD;
  dwDestinationDeviceId      : DWORD;
  byPortId                   : BYTE;
  bySensorNumber             : BYTE := 0;
  dwOptions                  : DWORD := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bStart` | `BOOL` | - | 本输入上升沿激活功能块（触发一次执行）。功能块活动期间（`bBusy = TRUE`）后续上升沿被忽略。 |
| `wDestinationManufacturerId` | `WORD` | - | 唯一厂商 ID，用于寻址目标 DMX 设备。 |
| `dwDestinationDeviceId` | `DWORD` | - | 唯一设备 ID，用于寻址目标 DMX 设备。 |
| `byPortId` | `BYTE` | - | 被寻址 DMX 设备内的通道；子设备（sub-device）通过 Port Id 寻址，根设备的 Port Id 恒为 0。 |
| `bySensorNumber` | `BYTE` | `0` | 要查询的传感器编号，默认 0。 |
| `dwOptions` | `DWORD` | `0` | 选项（当前未使用）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  udiErrorId              : UDINT;
  stSensorDefinition      : ST_DMXSensorDefinition;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 功能块激活后置位，直到命令执行完成。对某些错误（如参数错误），`bError` 会在 `bStart` 上升沿后立即置位而 `bBusy` 不切到 TRUE。 |
| `bError` | `BOOL` | 命令执行出错时置 TRUE，命令专用错误码在 `udiErrorId`。仅当 `bBusy` 为 FALSE 时有效。 |
| `udiErrorId` | `UDINT` | 最近一次命令的命令专用错误码。仅当 `bBusy` 为 FALSE 时有效（见 §4 错误码）。 |
| `stSensorDefinition` | `ST_DMXSensorDefinition` | 返回的传感器定义结构（见 `ST_DMXSensorDefinition`）。 |

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

`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET SENSOR_DEFINITION 命令（携带 `bySensorNumber`）排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `stSensorDefinition` 填入该传感器的元信息（类型、单位、单位前缀、量程上下限、归一值、文本描述等），`bError` 与 `udiErrorId` 才有效。它是解释传感器读数的前提：先读定义知道单位和量程，再用 `FB_DMXGetSensorValue` 读实际值。设备的传感器数量可从 `FB_DMXGetDeviceInfo` 得知。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。

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

- `bySensorNumber` 默认 0（第一个传感器）；超出设备实际传感器数会返回错误码 `0x801B`。
- 与 `FB_DMXGetSensorValue` 配合：先读定义拿单位 / 量程，再读值才能正确换算与显示。
- 设备传感器数量见 `FB_DMXGetDeviceInfo` 返回结构。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DMXGetSensorDefinition.TcPOU`](../examples/P_Demo_FB_DMXGetSensorDefinition.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：把灯具内置温度传感器接入监控：先读传感器定义拿到单位（摄氏度）和量程，HMI 才能把原始读数正确显示成带单位的温度。
- **价值**：把传感器的单位与量程从设备读出，使读数自带物理含义，免去为每个型号硬编码换算系数。
- **替代方案对比**：
  - 硬编码每个传感器的单位 / 量程：换设备就要改、易错。
  - 只显示原始数值：运维不知道是多少度 / 多少伏。
  - **本 FB**：从设备读权威传感器定义。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf) §4.1.2.8.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/2670484363.html
- **相关 FB / FC**：`FB_DMXGetSensorValue`（读传感器实时值）、`ST_DMXSensorDefinition`（返回结构）、`FB_DMXGetDeviceInfo`（传感器数量）
