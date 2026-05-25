# Tc2_Drive

> Beckhoff 伺服驱动器通讯库：通过 EtherCAT 的 SoE（Sercos over EtherCAT）/ CoE（CANopen over EtherCAT）做驱动器参数读写、命令执行、状态机使能与简单速度控制。版本 `1.4.8`。

- [官方 InfoSys](https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/)
- [官方 PDF](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf)

## 索引（12 条 · 全部 ✅ verified）

| Category | Name | 文档 | 例程 |
|---|---|---|---|
| General SoE | FB_SoEReset_ByDriveRef | [✅ verified](general_soe/FB_SoEReset_ByDriveRef.md) | [P_Demo_FB_SoEReset_ByDriveRef.xml](examples/P_Demo_FB_SoEReset_ByDriveRef.xml) |
| General SoE | FB_SoEWritePassword_ByDriveRef | [✅ verified](general_soe/FB_SoEWritePassword_ByDriveRef.md) | [P_Demo_FB_SoEWritePassword_ByDriveRef.xml](examples/P_Demo_FB_SoEWritePassword_ByDriveRef.xml) |
| General SoE | FB_SoEExecuteCommand_ByDriveRef | [✅ verified](general_soe/FB_SoEExecuteCommand_ByDriveRef.md) | [P_Demo_FB_SoEExecuteCommand_ByDriveRef.xml](examples/P_Demo_FB_SoEExecuteCommand_ByDriveRef.xml) |
| AX5000 SoE | FB_SoEAX5000ReadActMainVoltage_ByDriveRef | [✅ verified](ax5000_soe/FB_SoEAX5000ReadActMainVoltage_ByDriveRef.md) | [P_Demo_FB_SoEAX5000ReadActMainVoltage_ByDriveRef.xml](examples/P_Demo_FB_SoEAX5000ReadActMainVoltage_ByDriveRef.xml) |
| AX5000 SoE | FB_SoEAX5000SetMotorCtrlWord_ByDriveRef | [✅ verified](ax5000_soe/FB_SoEAX5000SetMotorCtrlWord_ByDriveRef.md) | [P_Demo_FB_SoEAX5000SetMotorCtrlWord_ByDriveRef.xml](examples/P_Demo_FB_SoEAX5000SetMotorCtrlWord_ByDriveRef.xml) |
| AX5000 SoE | FB_SoEAX5000ParkAxis_ByDriveRef | [✅ verified](ax5000_soe/FB_SoEAX5000ParkAxis_ByDriveRef.md) | [P_Demo_FB_SoEAX5000ParkAxis_ByDriveRef.xml](examples/P_Demo_FB_SoEAX5000ParkAxis_ByDriveRef.xml) |
| AX5000 SoE | FB_SoEAX5000FirmwareUpdate_ByDriveRef | [✅ verified](ax5000_soe/FB_SoEAX5000FirmwareUpdate_ByDriveRef.md) | [P_Demo_FB_SoEAX5000FirmwareUpdate_ByDriveRef.xml](examples/P_Demo_FB_SoEAX5000FirmwareUpdate_ByDriveRef.xml) |
| Functions | F_GetVersionTcDrive | [✅ verified](version/F_GetVersionTcDrive.md) | [P_Demo_F_GetVersionTcDrive.xml](examples/P_Demo_F_GetVersionTcDrive.xml) |
| SimplePlcMotion | FB_CoEDriveEnable | [✅ verified](simple_plc_motion/FB_CoEDriveEnable.md) | [P_Demo_FB_CoEDriveEnable.xml](examples/P_Demo_FB_CoEDriveEnable.xml) |
| SimplePlcMotion | FB_CoEDriveMoveVelocity | [✅ verified](simple_plc_motion/FB_CoEDriveMoveVelocity.md) | [P_Demo_FB_CoEDriveMoveVelocity.xml](examples/P_Demo_FB_CoEDriveMoveVelocity.xml) |
| SimplePlcMotion | FB_SoEDriveEnable | [✅ verified](simple_plc_motion/FB_SoEDriveEnable.md) | [P_Demo_FB_SoEDriveEnable.xml](examples/P_Demo_FB_SoEDriveEnable.xml) |
| SimplePlcMotion | FB_SoEDriveMoveVelocity | [✅ verified](simple_plc_motion/FB_SoEDriveMoveVelocity.md) | [P_Demo_FB_SoEDriveMoveVelocity.xml](examples/P_Demo_FB_SoEDriveMoveVelocity.xml) |

## 用法套路

### 1. SoE `_ByDriveRef` 系列（General SoE + AX5000 SoE）

这类 FB 通过 **ADS 服务通道**异步访问 SoE 驱动器参数（IDN 寻址，如 `S-0-0099` 标准参数、`P-0-0200` 厂商参数）：

- 统一接口：`stDriveRef`（驱动器引用）+ `bExecute`（上升沿触发）+ `tTimeout`，输出 `bBusy` / `bError` / `iAdsErrId` / `iSercosErrId`。
- `stDriveRef` 初始化套路：把 System Manager 链接的 `ST_PlcDriveRef`（`AT %I*`）用 `F_CreateAmsNetId` 转 NetID，逐字段填进 `ST_DriveRef`，等 `sNetId <> ''` 且 `nSlaveAddr <> 0` 再放行触发。
- 调用范式：`bExecute` 上升沿触发 → `bBusy` 期间不改输入 → `bBusy` 落下后补一次 `bExecute := FALSE` 收尾。

### 2. SimplePlcMotion 系列（CoE / SoE Drive Enable + MoveVelocity）

这类 FB 通过 **过程映像（PDO）** 直接驱动，不走 ADS，实时性好，用于无需 NC 的纯调速：

- 先用 `FB_*DriveEnable` 把驱动器使能到运行使能态（电平型 `bEnable`，每周期调用推进状态机），`bStatus = TRUE` 后再用 `FB_*DriveMoveVelocity` 喂速度曲线。
- 两个配套 FB 必须共用**同一个**过程映像结构实例（`ST_CoeDriveIoInterface` / `ST_SoeDriveIoInterface`，VAR_IN_OUT 必传）。
- CoE 版 `FB_CoEDriveEnable` 带 `bReset`（CiA 402 控制字 Bit 7）；SoE 版 `FB_SoEDriveEnable` 无 `bReset`，故障复位另用 `FB_SoEReset_ByDriveRef`。

## 注意

- `FB_SoEAX5000ParkAxis_ByDriveRef`、`FB_CoEDriveEnable`、`FB_CoEDriveMoveVelocity` 三篇的具体 topic 页未在 InfoSys（1033）英文树检索到，标 `⚠️ not-on-infosys`，接口以 PDF 为准（元信息 `Source InfoSys` 指向同库 / 同类最接近的已收录 topic）。
- `FB_*DriveMoveVelocity` 的 VAR 区第 4 个输入在 PDF 中字面拼作 `fAccelaration2`（少个 e），文档与例程均按库字面保留，写成 `fAcceleration2` 会编译报错。
- SoE / CoE 错误码（`iAdsErrId` / `iSercosErrId` / `iErrorID` / `iDiagNumber`）PDF 与 InfoSys 均未逐条列表，需对照通用 ADS Return Codes 与具体驱动器（AX5000 等）厂商 Sercos 错误码 / 诊断手册。
