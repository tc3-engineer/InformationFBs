# FB_DMXGetSensorValue

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DMX` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Sensor Parameter Messages` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/2670486283.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DMXGetSensorValue.TcPOU`](../examples/P_Demo_FB_DMXGetSensorValue.TcPOU) |

---

## 1. 功能简述

读取某个 DMX 设备内指定传感器的当前值。按传感器编号返回 `ST_DMXSensorValue` 结构（含当前值及该传感器记录的最低 / 最高值）。配合 `FB_DMXGetSensorDefinition` 的单位 / 量程即可换算成带物理含义的读数。

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
| `bySensorNumber` | `BYTE` | `0` | 要读取的传感器编号，默认 0。 |
| `dwOptions` | `DWORD` | `0` | 选项（当前未使用）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  udiErrorId              : UDINT;
  stDMXSensorValue        : ST_DMXSensorValue;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 功能块激活后置位，直到命令执行完成。对某些错误（如参数错误），`bError` 会在 `bStart` 上升沿后立即置位而 `bBusy` 不切到 TRUE。 |
| `bError` | `BOOL` | 命令执行出错时置 TRUE，命令专用错误码在 `udiErrorId`。仅当 `bBusy` 为 FALSE 时有效。 |
| `udiErrorId` | `UDINT` | 最近一次命令的命令专用错误码。仅当 `bBusy` 为 FALSE 时有效（见 §4 错误码）。 |
| `stDMXSensorValue` | `ST_DMXSensorValue` | 返回的传感器值结构（当前值 / 最低值 / 最高值，见 `ST_DMXSensorValue`）。 |

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

`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET SENSOR_VALUE 命令（携带 `bySensorNumber`）排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `stDMXSensorValue` 给出该传感器的当前值及记录的最低 / 最高值，`bError` 与 `udiErrorId` 才有效。返回的是原始整数值，需结合 `FB_DMXGetSensorDefinition` 的单位与量程换算成实际物理量。可周期触发以监控传感器趋势。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。

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

- `bySensorNumber` 默认 0；超出设备传感器数会返回错误码 `0x801B`。
- 返回原始值：要配合 `FB_DMXGetSensorDefinition` 的单位 / 前缀换算成实际物理量。
- 结构里含最低 / 最高值，可用于判断传感器是否曾越限。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DMXGetSensorValue.TcPOU`](../examples/P_Demo_FB_DMXGetSensorValue.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：灯具过温保护监控：周期读取每盏灯的温度传感器当前值，超过阈值时在 PLC 里降功率或报警，防止灯具过热损坏。
- **价值**：把灯具内部传感器（温度 / 电压 / 风扇等）实时值接入 PLC，实现基于真实物理量的保护与预测性维护。
- **替代方案对比**：
  - 不监控传感器：过温 / 风扇故障只能等灯坏了才发现。
  - 外接独立温度探头：要额外硬件接线。
  - **本 FB**：直接读灯具自带传感器值。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf) §4.1.2.8.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/2670486283.html
- **相关 FB / FC**：`FB_DMXGetSensorDefinition`（传感器定义 / 单位 / 量程）、`ST_DMXSensorValue`（返回结构）、`FB_DMXGetStatusMessages`（设备状态 / 错误）
