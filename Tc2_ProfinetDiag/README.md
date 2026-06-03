# Tc2_ProfinetDiag（PROFINET 诊断 / I&M / 命名）

> Beckhoff TwinCAT 3 PROFINET 诊断 PLC 库。
> 面向 PROFINET RT Controller（TF6271 / CCAT M930-B930 / EL6631 等）与 PROFINET Device（EL6631-0010 / CCAT / TF6270），
> 提供诊断报警读取、I&M（Identification & Maintenance，标识与维护）读写、设备命名/复位、网络扫描、端口统计/诊断等功能块。

## 概览

| 字段 | 值 |
|---|---|
| 库版本 | `1.0.2` |
| 来源 PDF | [TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf)（2024-11-21, Version 1.0.2） |
| InfoSys 根 | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/ |
| 文档进度 | 27 / 27（全部为 FUNCTION_BLOCK；DUT/枚举仅作引用，不单独成文） |
| 验证基线 | verify_doc 27/27 PASS，lint_tcpou 27/27 PASS（2026-06-02） |

**库定位**：本库不是 PROFINET 通讯运行时（循环 IO 由 TF6271 / EL6631 驱动承担），而是 PROFINET 的**诊断与配置辅助 API**——读诊断报警、读写设备电子铭牌（I&M）、给设备命名/复位、扫描网络、读端口质量统计。几乎所有 FB 都是基于 ADS 的异步功能块：上升沿 / 电平触发 → `bBusy` 期间忙 → 完成后输出数据，出错经 `bError` + 错误号反馈。

**双侧视角**：
- **Controller 侧**（§3.1）：PLC 作为 PROFINET 控制器，去读/写/命名下挂的从站。`PORT = Device ID + 16#1000` 寻址设备。
- **Device 侧**（§3.2）：PLC 作为 PROFINET 设备（EL6631-0010 / CCAT / TF6270），管理自身 I&M、名称、并能主动向上级控制器发报警。

## 典型用法模板

### 设备发现 → 命名（投运自动化）
`FB_PN_SCAN`（或 `FB_PN_SCAN_UpTo255`）扫到 MAC/名 → `FB_SET_PN_NAME`（按 MAC 命名） →（如需）`FB_RESET_PN_TO_FACTORY_SETTINGS`（按 MAC 复位重来）

### 电子铭牌读写（I&M，Controller 侧）
读：`FB_PN_IM0_READ`（出厂标识，只读）/ `FB_PN_IM1_READ`~`FB_PN_IM4_Read`
写：`FB_PN_IM1_WRITE`~`FB_PN_IM4_WRITE`（I&M0 不可写）

### 网络健康监控
`FB_PN_ReadStateOfDevices`（全网计数总览）→ 异常时 `FB_PN_ReadCompleteInfoOfDevices`（逐台明细）

### 诊断报警联动
Controller 侧：`FB_PN_ALARM_DIAG`（监听 `PnIoBoxDiag` 读出报警明细）
Device 侧：`FB_PN_SEND_ALARM`（设备主动向控制器报警）

### 端口/物理层诊断
`FB_PN_GET_PORT_STATISTIC`（端口流量/坏包统计，含 link 标志）+ `FB_PN_READ_PORT_DIAG`（端口诊断/拓扑）

## Function Blocks（27）

### Controller — 诊断报警（1）

| 名称 | 用途 | 文档 |
|---|---|---|
| `FB_PN_ALARM_DIAG` | 读 PROFINET 设备诊断报警（带 `PnIoBoxDiag` 硬件输入） | [controller_alarmdiag/FB_PN_ALARM_DIAG.md](controller_alarmdiag/FB_PN_ALARM_DIAG.md) |

### Controller — I&M 标识与维护（9）

| 名称 | 用途 | 文档 |
|---|---|---|
| `FB_PN_IM0_READ` | 读 I&M0 出厂标识（厂商/订货号/序列号，只读，0xAFF0） | [controller_im/FB_PN_IM0_READ.md](controller_im/FB_PN_IM0_READ.md) |
| `FB_PN_IM1_READ` | 读 I&M1 功能/位置标签（0xAFF1） | [controller_im/FB_PN_IM1_READ.md](controller_im/FB_PN_IM1_READ.md) |
| `FB_PN_IM1_WRITE` | 写 I&M1 功能/位置标签 | [controller_im/FB_PN_IM1_WRITE.md](controller_im/FB_PN_IM1_WRITE.md) |
| `FB_PN_IM2_READ` | 读 I&M2 安装日期（0xAFF2） | [controller_im/FB_PN_IM2_READ.md](controller_im/FB_PN_IM2_READ.md) |
| `FB_PN_IM2_WRITE` | 写 I&M2 安装日期 | [controller_im/FB_PN_IM2_WRITE.md](controller_im/FB_PN_IM2_WRITE.md) |
| `FB_PN_IM3_READ` | 读 I&M3 厂商描述（0xAFF3） | [controller_im/FB_PN_IM3_READ.md](controller_im/FB_PN_IM3_READ.md) |
| `FB_PN_IM3_WRITE` | 写 I&M3 厂商描述 | [controller_im/FB_PN_IM3_WRITE.md](controller_im/FB_PN_IM3_WRITE.md) |
| `FB_PN_IM4_Read` | 读 I&M4 厂商签名（0xAFF4） | [controller_im/FB_PN_IM4_Read.md](controller_im/FB_PN_IM4_Read.md) |
| `FB_PN_IM4_WRITE` | 写 I&M4 厂商签名 | [controller_im/FB_PN_IM4_WRITE.md](controller_im/FB_PN_IM4_WRITE.md) |

### Controller — PROFINET RT Controller（2）

| 名称 | 用途 | 文档 |
|---|---|---|
| `FB_PN_ReadStateOfDevices` | 读全网设备状态总览（组态/异常/诊断计数，需驱动 v03/V00.21+） | [controller_rt/FB_PN_ReadStateOfDevices.md](controller_rt/FB_PN_ReadStateOfDevices.md) |
| `FB_PN_ReadCompleteInfoOfDevices` | 读全网逐台设备完整信息（名/IP/循环时间，需库 >= v1.4.1.0） | [controller_rt/FB_PN_ReadCompleteInfoOfDevices.md](controller_rt/FB_PN_ReadCompleteInfoOfDevices.md) |

### Controller — 命名 / 复位 / 扫描（4）

| 名称 | 用途 | 文档 |
|---|---|---|
| `FB_SET_PN_NAME` | 按 MAC 给设备分配 PROFINET 名称 | [controller/FB_SET_PN_NAME.md](controller/FB_SET_PN_NAME.md) |
| `FB_RESET_PN_TO_FACTORY_SETTINGS` | 按 MAC 把设备复位到出厂设置 | [controller/FB_RESET_PN_TO_FACTORY_SETTINGS.md](controller/FB_RESET_PN_TO_FACTORY_SETTINGS.md) |
| `FB_PN_SCAN` | 扫描网络返回设备列表（≤100 台） | [controller/FB_PN_SCAN.md](controller/FB_PN_SCAN.md) |
| `FB_PN_SCAN_UpTo255` | 扫描网络返回设备列表（≤255 台，需库 >= v1.5.2.0） | [controller/FB_PN_SCAN_UpTo255.md](controller/FB_PN_SCAN_UpTo255.md) |

### Device — EL6631-0010（3）

| 名称 | 用途 | 文档 |
|---|---|---|
| `FB_READ_PROFINET_NAME` | 读 EL6631-0010 的 PROFINET 名（含虚拟设备） | [device_el6631/FB_READ_PROFINET_NAME.md](device_el6631/FB_READ_PROFINET_NAME.md) |
| `FB_Write_IuM_EL6631_0010` | EL6631 设备端按位掩码写 I&M1~I&M4 | [device_el6631/FB_Write_IuM_EL6631_0010.md](device_el6631/FB_Write_IuM_EL6631_0010.md) |
| `FB_Read_IuM_EL6631_0010` | EL6631 设备端一次读齐 I&M1~I&M4 | [device_el6631/FB_Read_IuM_EL6631_0010.md](device_el6631/FB_Read_IuM_EL6631_0010.md) |

### Device — via CCAT (CX-B930, TF6270)（5）

| 名称 | 用途 | 文档 |
|---|---|---|
| `FB_PROFINET_READ_IM` | 读设备 I&M 数据结构 | [device_ccat/FB_PROFINET_READ_IM.md](device_ccat/FB_PROFINET_READ_IM.md) |
| `FB_PROFINET_READ_NAME` | 读设备名 + 是否可改标志（需库 >= v1.5.1.0） | [device_ccat/FB_PROFINET_READ_NAME.md](device_ccat/FB_PROFINET_READ_NAME.md) |
| `FB_PROFINET_READ_PRM` | 读设备 PROFINET/IP 参数设置 | [device_ccat/FB_PROFINET_READ_PRM.md](device_ccat/FB_PROFINET_READ_PRM.md) |
| `FB_PROFINET_WRITE_IM` | 写设备 I&M 数据结构 | [device_ccat/FB_PROFINET_WRITE_IM.md](device_ccat/FB_PROFINET_WRITE_IM.md) |
| `FB_PROFINET_SET_NAME` | 设备端自改 PROFINET 名（需驱动 06/V00.34+、TF6270、CCAT B930） | [device_ccat/FB_PROFINET_SET_NAME.md](device_ccat/FB_PROFINET_SET_NAME.md) |

### Device — 报警发送（1）

| 名称 | 用途 | 文档 |
|---|---|---|
| `FB_PN_SEND_ALARM` | 设备端向控制器主动发 PROFINET 报警 | [device/FB_PN_SEND_ALARM.md](device/FB_PN_SEND_ALARM.md) |

### Port diagnosis — 端口诊断（2）

| 名称 | 用途 | 文档 |
|---|---|---|
| `FB_PN_GET_PORT_STATISTIC` | 读端口流量统计（速率/收发计数/坏包/丢帧 + link 标志） | [port_diagnosis/FB_PN_GET_PORT_STATISTIC.md](port_diagnosis/FB_PN_GET_PORT_STATISTIC.md) |
| `FB_PN_READ_PORT_DIAG` | 读端口诊断 / 拓扑邻居信息 | [port_diagnosis/FB_PN_READ_PORT_DIAG.md](port_diagnosis/FB_PN_READ_PORT_DIAG.md) |

## 数据结构（DUT / 枚举，未单独成文档）

以下类型在 PDF §4「Data structures」定义，作为上述 FB 的参数/返回类型被引用；按本仓库流程不单独成 .md，在引用它们的 FB 文档中按需说明字段：

| 名称 | 类型 | 用途 |
|---|---|---|
| `str_SW_Rec` | STRUCT | 设备软件版本（前缀/功能扩展/Bug Fix/内部变更），含在 `str_IM_0xAFF0` |
| `str_IM_0xAFF0` | STRUCT | I&M0 帧（厂商 ID/订货号/序列号/硬件软件版本等），`FB_PN_IM0_READ` 输出 |
| `str_IM_0xAFF1` | STRUCT | I&M1 帧（功能/位置标签），I&M1 读写引用 |
| `str_IM_0xAFF2` | STRUCT | I&M2 帧（安装日期） |
| `str_IM_0xAFF3` | STRUCT | I&M3 帧（厂商描述） |
| `str_IM_0xAFF4` | STRUCT | I&M4 帧（厂商签名） |
| `str_PN_Scan` | STRUCT | 扫描结果（IP/掩码/网关/MAC/厂商 ID/设备 ID/PN 名），`FB_PN_SCAN(_UpTo255)` 数组元素 |
| `ST_PN_DiagMessage` | STRUCT | 诊断报文裸数据流（300 字节），由 `FB_PN_ALARM_DIAG` 内部解析 |
| `ST_PN_Diag` | STRUCT | 单条诊断明细（槽/子槽/报警类型/通道错误等） |
| `ST_PN_AlarmDiagData` | STRUCT | 可读诊断数据（时间戳/站名/`ST_PN_Diag`/用户数据标志），`FB_PN_ALARM_DIAG` 输出 |
| `ST_PN_DeviceInfo` | STRUCT | 设备信息（BOX 地址/名/IP/状态/CR 数/循环时间），`FB_PN_ReadCompleteInfoOfDevices` 数组元素 |
| `str_Diag_PN_Settings` | STRUCT | 设备永久 IP 设置（IP/掩码/网关/PN 名），`FB_PROFINET_READ_PRM` 输出 |
| `str_IuM_Data` | STRUCT | I&M 数据集合（功能/位置/日期/描述/签名），CCAT 设备组 I&M 读写引用 |
| `E_PN_ALARM_TYP` | ENUM | PROFINET 报警类型枚举（`PN_ALARM_PROCESS` / `PN_ALARM_PULL` / `PN_ALARM_PLUG` …），`FB_PN_SEND_ALARM` 输入 |
| `RecStruct` | STRUCT | PROFINET record（非循环参数）数据映射 |
| `str_GetPortStatistic` | STRUCT | 端口统计（速率/收发字节包/坏包/丢帧），端口诊断 FB 输出 |
| `str_PortDiag` | STRUCT | 端口诊断（PortId/邻居名/描述/ChassisId 等拓扑信息） |

## 错误码概览

库内除 `FB_PN_GET_PORT_STATISTIC` / `FB_PN_READ_PORT_DIAG`（无错误号输出）与 `FB_READ_PROFINET_NAME`（仅 `bError`）外，其余 FB 都通过 `iErrorID`（或 `nErrorID`）输出标准 **ADS 返回码**（PDF §5.1）。常见取值：

| 码（dec） | Hex | 名称 | 含义 |
|---|---|---|---|
| `0` | `0x0` | `ERR_NOERROR` | 成功 |
| `6` | `0x6` | `ERR_TARGETPORTNOTFOUND` | 目标端口未找到（`PORT` 错 / 服务未启动） |
| `7` | `0x7` | `ERR_TARGETMACHINENOTFOUND` | 目标设备未找到（`NETID` / 路由错） |
| `16` | `0x10` | `ERR_LOWINSTLEVEL` | 授权等级过低 |
| `1280`+ | `0x500`+ | `ROUTERERR_*` | 路由错误段 |
| `1792`+ | `0x700`+ | 一般 ADS 错误 | 命令相关错误（设备拒绝/参数非法等） |

> 完整四组（Global / Router / General ADS / RTime）返回码见 PDF §5.1「ADS Return Codes」。⚠️ PDF 与 InfoSys 均未给出本库各 FB 专属错误码子集，上表为 ADS 通用码。

## 例程导入

每篇文档配套 `examples/P_Demo_<Name>.TcPOU`（TwinCAT 3 原生 .TcPOU）：

1. 在 TwinCAT 3 XAE 中右键 PLC 项目下 POUs 文件夹 → **Add → Existing Item…**
2. 选择 `P_Demo_<Name>.TcPOU`
3. 引用 `Tc2_ProfinetDiag`（References → Add library）
4. 编译 → 登录 → 运行；按文档 §6 / §7 中的"验证步骤"在线写值观察
5. 注：例程中 `PORT := 16#1001`、`NETID := ''`、MAC 等为占位示例值，实际须按现场 PROFINET 组态填写；`FB_PN_ALARM_DIAG` 的 `PnIoBoxDiag` 硬件输入须在 TwinCAT I/O 映射中链接到设备。

## 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf)
- **InfoSys 根**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/
- **相关库**：`Tc2_System`（ADS 基础 FB）、PROFINET 控制器/设备文档（TF6271 / TF6270 / EL6631-EL6632）
