# Tc2_DMX

Beckhoff TwinCAT 3 **Tc2_DMX** 库的中文技术文档与可导入演示例程。
本库通过 Beckhoff EL6851 DMX/RDM EtherCAT 端子，让 TwinCAT 3 PLC 直接驱动专业舞台与效果灯光设备：既能循环发送 DMX512 灯光数据，又能用 RDM（Remote Device Management）远程发现设备、读写灯具参数、读传感器、配置 DMX512 起始地址等。

| 字段 | 值 |
|---|---|
| Library | Tc2_DMX |
| Library Version | `1.8.1` |
| PDF | [TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf) |
| InfoSys 入口 | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/index.html |
| 文档总数 | **34 个 FB = 34 篇** |
| 例程总数 | **34 个 P_Demo_*.TcPOU** |
| Verify 状态 | 全部 PASS（2026-06-02） |
| Lint 状态 | 全部 PASS（2026-06-02） |

## 库结构与使用要点

- **通讯核心是入口**：所有功能块都不直接访问 EL6851 过程映像，而是把命令排进一个 `ST_DMXCommandBuffer` 缓冲区。每个 EL6851 端子必须配**一个** `FB_EL6851CommunicationEx` 实例（旧版 `FB_EL6851Communication` 已过时）和**一个** `ST_DMXCommandBuffer`，由通讯功能块每周期调用、逐条转发命令。
- **CycleMode 与 RDM 互斥**：循环发送灯光数据需开启 CycleMode；发送 RDM 命令前必须关闭 CycleMode（`bSetCycleMode := FALSE`），否则所有 RDM 命令返回错误码 `0x800A`。
- **RDM 命令功能块都是上升沿触发**：`bStart` 给一次上升沿启动，`bBusy` 期间忽略后续上升沿；要每周期调用并等 `bBusy` 落回 FALSE 后再读结果。
- **设备 UID**：每台 DMX 设备有唯一 48 位 UID = 16 位厂商 ID（ESTA 分配，Beckhoff 为 `0x4241`）+ 32 位设备 ID。
- **错误码全库统一**：所有功能块通过 `udiErrorId` 输出命令专用错误码，码表见 PDF §4.1.3（`0x0000` 无错，`0x8001`–`0x801E` 各类错误）。

## 分类导航

### High Level（高层设备搜索，2 个）

一键完成 RDM 二分发现协议，自动搜索设备并可选连续编址。

| FB | 用途 |
|---|---|
| [FB_DMXDiscovery](high_level/FB_DMXDiscovery.md) | 搜索最多 50 个 DMX 设备 + 可选自动编址 |
| [FB_DMXDiscovery512](high_level/FB_DMXDiscovery512.md) | 搜索最多 512 个 DMX 设备 + 可选自动编址（大型总线） |

### Base（通讯与通用命令，3 个）

EL6851 通讯核心与通用 RDM 命令发送。

| FB | 用途 |
|---|---|
| [FB_EL6851CommunicationEx](base/FB_EL6851CommunicationEx.md) | **通讯核心（推荐）**，每 EL6851 一个实例，循环数据 + RDM 命令转发 |
| [FB_EL6851Communication](base/FB_EL6851Communication.md) | 通讯核心（**已过时**，超长 RDM 应答支持不全，新工程改用 Ex 版） |
| [FB_DMXSendRDMCommand](base/FB_DMXSendRDMCommand.md) | 通用 RDM 命令发送（自由构造 CC/PID/参数，所有专用 FB 的底层基础） |

### Device Control（设备控制参数，3 个）

识别 / 复位单台设备。

| FB | 用途 |
|---|---|
| [FB_DMXGetIdentifyDevice](device_control/FB_DMXGetIdentifyDevice.md) | 读设备识别（闪烁）状态 |
| [FB_DMXSetIdentifyDevice](device_control/FB_DMXSetIdentifyDevice.md) | 置 / 复位设备识别（用于现场定位灯具） |
| [FB_DMXSetResetDevice](device_control/FB_DMXSetResetDevice.md) | 远程复位单台设备（热 / 冷复位） |

### Discovery Messages（底层发现命令，3 个）

RDM 二分发现协议的底层步骤（通常由 High Level FB 自动调用）。

| FB | 用途 |
|---|---|
| [FB_DMXDiscMute](discovery/FB_DMXDiscMute.md) | 置位设备 mute 标志（排除已找到的设备） |
| [FB_DMXDiscUnMute](discovery/FB_DMXDiscUnMute.md) | 复位设备 mute 标志（恢复可被发现） |
| [FB_DMXDiscUniqueBranch](discovery/FB_DMXDiscUniqueBranch.md) | UID 区间查询（二分发现核心命令） |

### Power and Lamp Setting（电源与灯泡参数，4 个）

灯泡寿命统计与开灯行为配置。

| FB | 用途 |
|---|---|
| [FB_DMXGetLampHours](power_lamp/FB_DMXGetLampHours.md) | 读灯泡累计点亮小时数 |
| [FB_DMXSetLampHours](power_lamp/FB_DMXSetLampHours.md) | 写灯泡点亮小时数（换灯清零） |
| [FB_DMXGetLampOnMode](power_lamp/FB_DMXGetLampOnMode.md) | 读开灯模式 |
| [FB_DMXSetLampOnMode](power_lamp/FB_DMXSetLampOnMode.md) | 写开灯模式（批量配置上电行为） |

### Product Information（产品信息，7 个）

设备型号 / 厂商 / 版本 / 标签 / 类别等信息。

| FB | 用途 |
|---|---|
| [FB_DMXGetDeviceInfo](product_info/FB_DMXGetDeviceInfo.md) | 读设备综合信息（型号 / 协议版本 / 占用槽 / 子设备 / 传感器数等） |
| [FB_DMXGetDeviceLabel](product_info/FB_DMXGetDeviceLabel.md) | 读设备标签（自定义名字） |
| [FB_DMXSetDeviceLabel](product_info/FB_DMXSetDeviceLabel.md) | 写设备标签（给灯具命名） |
| [FB_DMXGetDeviceModelDescription](product_info/FB_DMXGetDeviceModelDescription.md) | 读设备型号描述文本 |
| [FB_DMXGetManufacturerLabel](product_info/FB_DMXGetManufacturerLabel.md) | 读厂商描述文本 |
| [FB_DMXGetSoftwareVersionLabel](product_info/FB_DMXGetSoftwareVersionLabel.md) | 读固件版本描述文本 |
| [FB_DMXGetProductDetailIdList](product_info/FB_DMXGetProductDetailIdList.md) | 读产品类别列表（最多 6 类） |

### Queued and Status Messages（队列与状态消息，3 个）

设备状态 / 错误信息的集中诊断闭环。

| FB | 用途 |
|---|---|
| [FB_DMXGetStatusMessages](status/FB_DMXGetStatusMessages.md) | 读设备状态 / 错误消息（最多 25 条） |
| [FB_DMXGetStatusIdDescription](status/FB_DMXGetStatusIdDescription.md) | 把状态 ID 翻译成可读文本 |
| [FB_DMXClearStatusId](status/FB_DMXClearStatusId.md) | 清设备消息缓冲（故障闭环末尾用） |

### RDM Information（RDM 参数元信息，2 个）

自描述式参数访问，适配任意品牌设备。

| FB | 用途 |
|---|---|
| [FB_DMXGetParameterDescription](rdm_info/FB_DMXGetParameterDescription.md) | 读厂商自定义 PID 的定义 |
| [FB_DMXGetSupportedParameters](rdm_info/FB_DMXGetSupportedParameters.md) | 读设备支持的 PID 列表（最多 115 个） |

### Sensor Parameter（传感器参数，2 个）

读灯具内置传感器（温度 / 电压 / 风扇等）。

| FB | 用途 |
|---|---|
| [FB_DMXGetSensorDefinition](sensor/FB_DMXGetSensorDefinition.md) | 读传感器定义（类型 / 单位 / 量程） |
| [FB_DMXGetSensorValue](sensor/FB_DMXGetSensorValue.md) | 读传感器当前值（含最低 / 最高值） |

### Setup Messages（设置消息，5 个）

DMX512 起始地址、personality（工作模式）、槽功能配置。

| FB | 用途 |
|---|---|
| [FB_DMXGetDMX512StartAddress](setup/FB_DMXGetDMX512StartAddress.md) | 读 DMX512 起始地址 |
| [FB_DMXSetDMX512StartAddress](setup/FB_DMXSetDMX512StartAddress.md) | 写 DMX512 起始地址（形参德式拼写 `iDMX512Startadresse`） |
| [FB_DMXGetDMX512PersonalityDescription](setup/FB_DMXGetDMX512PersonalityDescription.md) | 读 personality（工作模式）描述 |
| [FB_DMXGetSlotDescription](setup/FB_DMXGetSlotDescription.md) | 读单个槽的功能文本 |
| [FB_DMXGetSlotInfo](setup/FB_DMXGetSlotInfo.md) | 读各槽功能信息（最多 46 个） |

## 例程目录

所有 34 篇文档配套的 TcPOU 演示程序在 [`examples/`](examples/) 下，文件名 `P_Demo_<Name>.TcPOU`。

导入方式：
1. 右键 TwinCAT 3 PLC 项目 → **Add → Existing Item**
2. 选 `examples/P_Demo_<Name>.TcPOU`
3. 引用 Tc2_DMX 库（References → Add library），并在 I/O 中链接 EL6851 过程数据
4. 编译 → 登录 → 按文档 §7 与例程头部「验证」注释执行测试

> 注意：除 `P_Demo_FB_EL6851Communication(Ex).TcPOU` 演示循环数据外，各 RDM 命令例程都需要在同一项目里再放一个 `FB_EL6851CommunicationEx` 实例并与例程**共用同一个 `ST_DMXCommandBuffer`**，且通讯功能块处于非 CycleMode，命令才能真正发出。

## 文档遵循的硬规则

详见仓库根目录的 [`CLAUDE.md`](../CLAUDE.md)，要点：
- 中文叙述、IEC 关键字 / 类型名保留英文
- 不出现「详见 PDF」「见上方」等占位短语
- 每篇含 PDF + InfoSys 双源 URL，VAR 区逐字照搬 PDF 并与 InfoSys 双源核对
- 例程含「场景 / 价值 / 验证步骤」三件套
- 例程注释 ≥ 1/3 代码行，解释 WHY 不复述 WHAT
- 例程是纯 TwinCAT 3 原生 .TcPOU，直接拖入 XAE 即可使用

## 已知偏差与待人工确认 ⚠️

1. **`FB_DMXSetDMX512StartAddress` 的起始地址形参为德式拼写 `iDMX512Startadresse`**（非 `iDMX512StartAddress`），而对应读取 FB `FB_DMXGetDMX512StartAddress` 的输出却拼作 `iDMX512StartAddress`（英式）。两者拼写不一致是 Beckhoff 命名遗留，PDF 与 InfoSys 双源一致，本仓库按原文逐字保留。
2. **`FB_EL6851Communication` 已过时（Outdated）**：PDF 明确标注，新工程应改用 `FB_EL6851CommunicationEx`。本仓库仍为其建档，供维护存量旧工程参考。
3. **部分 RDM 参数 FB（如 LAMP_HOURS / LAMP_ON_MODE / 各 LABEL）并非所有灯具都实现**：访问不支持的 PID 会返回 RDM 应答类错误码（`0x8010` / `0x8015` 等），属设备实现差异，非库缺陷。
