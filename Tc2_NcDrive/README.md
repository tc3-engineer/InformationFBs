# Tc2_NcDrive — NC 轴 ↔ 驱动器接口库

> Beckhoff TwinCAT 3 标准库。提供通过 **NC 轴引用（`NCTOPLC_AXIS_REF`）访问伺服驱动器**的功能块（FB）与函数（FC）。
> 这些 FB 是对 Tc2_Drive 底层 SoE/CoE 访问的封装，让 PLC 不必直接管 IDN 寻址即可读写驱动器参数、复位、控制抱闸、更新固件。
>
> - **Library Version**：1.2.9
> - **Source PDF**：[TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf)
> - **Source InfoSys**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ncdrive/

## 关键概念

- 所有 FB 的轴接口都是 `Axis : NCTOPLC_AXIS_REF` 作为 **VAR_IN_OUT**（必须传引用，通常映射在 `%I*` 输入过程映像上）
- 命令类 FB 统一遵循 `bExecute`（边沿触发）→ `bBusy`（进行中）→ `bError` + `iAdsErrId` / `iSercosErrId`（错误）的反馈模式
- 错误分两路：`iAdsErrId` 是 ADS 传输层错误码，`iSercosErrId` 是 Sercos/SoE 协议层错误码，定位时先分清是链路问题还是驱动器拒绝
- **复位驱动器 ≠ 复位 NC 轴**：`FB_SoEReset` 只清驱动器错误；NC 通道错误需用 Tc2_MC2 的 `MC_Reset`
- AX5000 专用 FB 前缀为 `FB_SoEAX5000*`，操作的是 AX5000 厂商参数（P-0-xxxx）

## 分类索引

### General SoE（通用 SoE）

| FB / FC | 说明 | 文档 |
|---|---|---|
| `FB_SoEReset` | 通过 S-0-0099 复位驱动器（不复位 NC 轴） | [general_soe/FB_SoEReset.md](general_soe/FB_SoEReset.md) |
| `FB_SoEWritePassword` | 通过 S-0-0267 写驱动器密码，解锁受保护参数 | [general_soe/FB_SoEWritePassword.md](general_soe/FB_SoEWritePassword.md) |

### AX5000 SoE（AX5000 专用）

| FB / FC | 说明 | 文档 |
|---|---|---|
| `FB_SoEAX5000ReadActMainVoltage` | 读 AX5000 当前主电源电压峰值（P-0-0200） | [ax5000_soe/FB_SoEAX5000ReadActMainVoltage.md](ax5000_soe/FB_SoEAX5000ReadActMainVoltage.md) |
| `FB_SoEAX5000SetMotorCtrlWord` | 通过 P-0-0096 强制锁/松电机抱闸（独立于 Enable） | [ax5000_soe/FB_SoEAX5000SetMotorCtrlWord.md](ax5000_soe/FB_SoEAX5000SetMotorCtrlWord.md) |
| `FB_SoEAX5000FirmwareUpdate` | 检查并自动更新 AX5000 固件 | [ax5000_soe/FB_SoEAX5000FirmwareUpdate.md](ax5000_soe/FB_SoEAX5000FirmwareUpdate.md) |

### 库版本

| FB / FC | 说明 | 文档 |
|---|---|---|
| `F_GetVersionTcNcDrive` | 读取本库版本号的一个分量（major/minor/revision） | [library_version/F_GetVersionTcNcDrive.md](library_version/F_GetVersionTcNcDrive.md) |

## 例程

所有 `P_Demo_*.xml` 例程在 [`examples/`](examples/) 目录，PLCopenXML 格式，可直接右键 PLC 项目 → Import PLCopenXML 导入 TwinCAT 3 XAE。

## 备注

本仓库覆盖的是 parse_toc 在本库 TOC 中识别出的 6 个顶层条目。Tc2_NcDrive 还包含一组通用 SoE/CoE 命令与诊断 FB（如 `FB_SoERead`/`FB_SoEWrite`/`FB_CoERead` 等，分布在 §3.1.3–3.1.5、§3.2），它们在 PDF 中以子分组标题归类，本批次未单独成文。
