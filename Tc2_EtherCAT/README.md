# Tc2_EtherCAT

TwinCAT 3 PLC 库 **Tc2_EtherCAT** 的中文文档与可导入例程 —— 全面覆盖 EtherCAT 主从配置、网络诊断、状态机控制、底层命令、邮箱协议（ADS / CoE / FoE / SoE）、Distributed Clocks 等核心功能。

## 库基本信息

- **库名**：`Tc2_EtherCAT`
- **库版本**：1.9.5（按缓存 `_meta/.pdf-cache/Tc2_EtherCAT.meta.json` 为准）
- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf)
- **InfoSys 库根**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/index.html
- **目标平台**：PC 或 CX（x86 / x64 / Arm®）
- **TwinCAT 版本要求**：≥ v3.1.0；部分新 FB（如 `FB_EcGetAllMasters`、`FB_EcMasterObjectID`、`F_EcGetMailboxGatewayAddr`）要求更高版本，详见各文档

## 目录索引

仓库按 PDF 章节语义分类组织：

### `commands/`（§3 EtherCAT Commands，4 个 FB）

底层 EtherCAT 命令：直接寻址从站 ESC 寄存器 / DPRAM。

| 名称 | 类型 | 简述 |
|---|---|---|
| [FB_EcPhysicalReadCmd](commands/FB_EcPhysicalReadCmd.md) | FB | FPRD/APRD/BRD 物理读 |
| [FB_EcPhysicalWriteCmd](commands/FB_EcPhysicalWriteCmd.md) | FB | FPWR/APWR/BWR 物理写 |
| [FB_EcLogicalReadCmd](commands/FB_EcLogicalReadCmd.md) | FB | LRD 逻辑读 |
| [FB_EcLogicalWriteCmd](commands/FB_EcLogicalWriteCmd.md) | FB | LWR 逻辑写 |

### `diagnostic/`（§4 EtherCAT Diagnostic，25 个 FB/FC）

主站、从站、链路诊断与状态查询。

| 名称 | 类型 | 简述 |
|---|---|---|
| [FB_EcGetAllMasters](diagnostic/FB_EcGetAllMasters.md) | FB | 枚举本机全部 EtherCAT 主站 |
| [FB_EcGetAllSlaveAbnormalStateChanges](diagnostic/FB_EcGetAllSlaveAbnormalStateChanges.md) | FB | 各从站非预期状态切换次数 |
| [FB_EcGetAllSlaveAddr](diagnostic/FB_EcGetAllSlaveAddr.md) | FB | 全部从站固定地址清单 |
| [FB_EcGetAllSlaveCrcErrors](diagnostic/FB_EcGetAllSlaveCrcErrors.md) | FB | 全部从站 CRC 错误计数汇总 |
| [FB_EcGetAllSlavePresentStateChanges](diagnostic/FB_EcGetAllSlavePresentStateChanges.md) | FB | 各从站断线计数 |
| [FB_EcGetAllSyncUnitSlaveAddr](diagnostic/FB_EcGetAllSyncUnitSlaveAddr.md) | FB | 指定 Sync Unit 内全部从站地址 |
| [FB_EcGetConfSlaves](diagnostic/FB_EcGetConfSlaves.md) | FB | 工程配置的从站清单 |
| [FB_EcGetLastProtErrInfo](diagnostic/FB_EcGetLastProtErrInfo.md) | FB | 邮箱协议最近错误详情 |
| [FB_EcGetMasterDevState](diagnostic/FB_EcGetMasterDevState.md) | FB | 主站设备状态位掩码 |
| [FB_EcGetScannedSlaves](diagnostic/FB_EcGetScannedSlaves.md) | FB | 在线扫描实际可见从站 |
| [FB_EcGetSlaveCount](diagnostic/FB_EcGetSlaveCount.md) | FB | 主站连接从站总数 |
| [FB_EcGetSlaveCrcError](diagnostic/FB_EcGetSlaveCrcError.md) | FB | 单从站 3 端口 CRC 错误 |
| [FB_EcGetSlaveCrcErrorEx](diagnostic/FB_EcGetSlaveCrcErrorEx.md) | FB | 单从站 4 端口 CRC 错误（EK1122） |
| [FB_EcGetSlaveIdentity](diagnostic/FB_EcGetSlaveIdentity.md) | FB | 单从站 CANopen 身份 |
| [FB_EcGetSlaveTopologyInfo](diagnostic/FB_EcGetSlaveTopologyInfo.md) | FB | 全网拓扑数据 |
| [FB_EcMasterFrameCount](diagnostic/FB_EcMasterFrameCount.md) | FB | 主站每循环 EtherCAT 帧数 |
| [FB_EcMasterFrameStatistic](diagnostic/FB_EcMasterFrameStatistic.md) | FB | 主站丢失帧 + 帧速率统计 |
| [FB_EcMasterFrameStatisticClearCRC](diagnostic/FB_EcMasterFrameStatisticClearCRC.md) | FB | 清全部从站 CRC 计数 |
| [FB_EcMasterFrameStatisticClearFrames](diagnostic/FB_EcMasterFrameStatisticClearFrames.md) | FB | 清主站丢失帧计数 |
| [FB_EcMasterFrameStatisticClearTxRxErr](diagnostic/FB_EcMasterFrameStatisticClearTxRxErr.md) | FB | 清网卡 miniport 错误 |
| [FB_EcMasterObjectID](diagnostic/FB_EcMasterObjectID.md) | FB | 主站 OTCID（NetID → OTCID） |
| [F_CheckVendorId](diagnostic/F_CheckVendorId.md) | FC | 判定从站是否为 Beckhoff |
| [F_EcGetLinkedTaskOfSyncUnit](diagnostic/F_EcGetLinkedTaskOfSyncUnit.md) | FC | 查 SU 关联 task |
| [F_EcGetSyncUnitName](diagnostic/F_EcGetSyncUnitName.md) | FC | 查 SU 名称 |
| [F_EcGetMailboxGatewayAddr](diagnostic/F_EcGetMailboxGatewayAddr.md) | FC | 查主站网卡 IP / MAC |

### `state_machine/`（§5 EtherCAT State Machine，7 个 FB）

主站与从站状态机（INIT/PREOP/SAFEOP/OP）的读取、请求、设置。

| 名称 | 类型 | 简述 |
|---|---|---|
| [FB_EcGetAllSlaveStates](state_machine/FB_EcGetAllSlaveStates.md) | FB | 全部从站状态批量读 |
| [FB_EcGetMasterState](state_machine/FB_EcGetMasterState.md) | FB | 读主站状态机状态 |
| [FB_EcGetSlaveState](state_machine/FB_EcGetSlaveState.md) | FB | 读单从站状态 |
| [FB_EcReqMasterState](state_machine/FB_EcReqMasterState.md) | FB | 异步请求主站切状态 |
| [FB_EcReqSlaveState](state_machine/FB_EcReqSlaveState.md) | FB | 异步请求从站切状态 / 清错 |
| [FB_EcSetMasterState](state_machine/FB_EcSetMasterState.md) | FB | 同步等待主站切状态 |
| [FB_EcSetSlaveState](state_machine/FB_EcSetSlaveState.md) | FB | 同步等待从站切状态 |

### `ads/`（§6 ADS Interface，2 个 FB）

通过 ADS 直读从站 EEPROM 的 BIC / BTN。

| 名称 | 类型 | 简述 |
|---|---|---|
| [FB_EcReadBIC](ads/FB_EcReadBIC.md) | FB | ADS 路径读 BIC |
| [FB_EcReadBTN](ads/FB_EcReadBTN.md) | FB | ADS 路径读 BTN |

### `coe/`（§7 CoE interface，9 个 FB）

CANopen over EtherCAT 邮箱协议（SDO 读写、CompleteAccess、驱动引用）。

| 名称 | 类型 | 简述 |
|---|---|---|
| [FB_EcCoeSdoRead](coe/FB_EcCoeSdoRead.md) | FB | SDO 单子项读 |
| [FB_EcCoeSdoReadEx](coe/FB_EcCoeSdoReadEx.md) | FB | SDO 整对象 / 单子项可选读 |
| [FB_EcCoeSdoWrite](coe/FB_EcCoeSdoWrite.md) | FB | SDO 单子项写 |
| [FB_EcCoeSdoWriteEx](coe/FB_EcCoeSdoWriteEx.md) | FB | SDO 整对象 / 单子项可选写 |
| [FB_CoERead_ByDriveRef](coe/FB_CoERead_ByDriveRef.md) | FB | 按驱动引用读 CoE |
| [FB_CoEWrite_ByDriveRef](coe/FB_CoEWrite_ByDriveRef.md) | FB | 按驱动引用写 CoE |
| [FB_EcCoeReadBIC](coe/FB_EcCoeReadBIC.md) | FB | CoE 路径读 BIC |
| [FB_EcCoeReadBTN](coe/FB_EcCoeReadBTN.md) | FB | CoE 路径读 BTN |
| [FB_EcCoESdoAbortCode](coe/FB_EcCoESdoAbortCode.md) | FB | 读 CoE Abort 详情 |

### `foe/`（§8 FoE interface，6 个 FB）

File over EtherCAT —— 主要用于固件升级 / 文件传输。

| 名称 | 类型 | 简述 |
|---|---|---|
| [FB_EcFoeAccess](foe/FB_EcFoeAccess.md) | FB | FoE 流式读写分块 |
| [FB_EcFoeClose](foe/FB_EcFoeClose.md) | FB | 关闭 FoE 通信端口 |
| [FB_EcFoeLoad](foe/FB_EcFoeLoad.md) | FB | 一站式固件下载 / 上传 |
| [FB_EcFoeOpen](foe/FB_EcFoeOpen.md) | FB | 打开 FoE 通信端口 |
| [FB_EcFoeReadFile](foe/FB_EcFoeReadFile.md) | FB | 远程 IPC 文件下载 |
| [FB_EcFoeWriteFile](foe/FB_EcFoeWriteFile.md) | FB | 远程 IPC 文件上传 |

### `soe/`（§9 SoE interface，4 个 FB）

Sercos over EtherCAT —— AX5xxx 系列伺服参数访问。

| 名称 | 类型 | 简述 |
|---|---|---|
| [FB_EcSoeRead](soe/FB_EcSoeRead.md) | FB | SoE 参数读（按地址） |
| [FB_EcSoeWrite](soe/FB_EcSoeWrite.md) | FB | SoE 参数写（按地址） |
| [FB_SoERead_ByDriveRef](soe/FB_SoERead_ByDriveRef.md) | FB | SoE 参数读（按驱动引用） |
| [FB_SoEWrite_ByDriveRef](soe/FB_SoEWrite_ByDriveRef.md) | FB | SoE 参数写（按驱动引用） |

### `conversion/`（§10 Conversion Functions，7 个 FC）

把状态字 / 身份信息翻译为可读字符串或结构化位字段。

| 名称 | 类型 | 简述 |
|---|---|---|
| [F_ConvBK1120CouplerStateToString](conversion/F_ConvBK1120CouplerStateToString.md) | FC | BK 耦合器状态 → 字符串 |
| [F_ConvMasterDevStateToString](conversion/F_ConvMasterDevStateToString.md) | FC | 主站设备状态 → 字符串 |
| [F_ConvProductCodeToString](conversion/F_ConvProductCodeToString.md) | FC | 产品代码 → 字符串 |
| [F_ConvSlaveStateToString](conversion/F_ConvSlaveStateToString.md) | FC | 从站状态结构 → 字符串 |
| [F_ConvSlaveStateToBits](conversion/F_ConvSlaveStateToBits.md) | FC | 从站状态 → 具名 bit 结构 |
| [F_ConvSlaveStateToBitsEx](conversion/F_ConvSlaveStateToBitsEx.md) | FC | 同上，含 4 端口扩展位 |
| [F_ConvStateToString](conversion/F_ConvStateToString.md) | FC | WORD 状态字 → 字符串 |

### `distributed_clocks/`（§11.1 ~ §11.3 Distributed Clocks，23 个 FB/FC）

DC（Distributed Clocks）时间体系：64-bit DC 时间转换、外部时钟同步监控、NCI 时间 ↔ 路径距离换算。

| 名称 | 类型 | 简述 |
|---|---|---|
| [ConvertDcTimeToPos](distributed_clocks/ConvertDcTimeToPos.md) | FB | DC 时间 → NC 轴位置 |
| [ConvertPosToDcTime](distributed_clocks/ConvertPosToDcTime.md) | FB | NC 轴位置 → DC 时间 |
| [ConvertDcTimeToPathPos](distributed_clocks/ConvertDcTimeToPathPos.md) | FB | DC 时间 → NCI 路径距离 |
| [ConvertPathPosToDcTime](distributed_clocks/ConvertPathPosToDcTime.md) | FB | NCI 路径距离 → DC 时间 |
| [DCTIME_TO_DCTIME64](distributed_clocks/DCTIME_TO_DCTIME64.md) | FC | 32-bit → 64-bit DC 时间 |
| [DCTIME64_TO_DCTIME](distributed_clocks/DCTIME64_TO_DCTIME.md) | FC | 64-bit → 32-bit DC 时间（截断） |
| [DCTIME64_TO_DCTIMESTRUCT](distributed_clocks/DCTIME64_TO_DCTIMESTRUCT.md) | FC | 64-bit DC → 日期时间结构 |
| [DCTIME64_TO_FILETIME64](distributed_clocks/DCTIME64_TO_FILETIME64.md) | FC | 64-bit DC → Windows FILETIME64 |
| [DCTIME64_TO_STRING](distributed_clocks/DCTIME64_TO_STRING.md) | FC | 64-bit DC → ISO 字符串 |
| [DCTIME64_TO_SYSTEMTIME](distributed_clocks/DCTIME64_TO_SYSTEMTIME.md) | FC | 64-bit DC → Windows TIMESTRUCT |
| [DCTIMESTRUCT_TO_DCTIME64](distributed_clocks/DCTIMESTRUCT_TO_DCTIME64.md) | FC | 日期时间结构 → 64-bit DC |
| [FILETIME64_TO_DCTIME64](distributed_clocks/FILETIME64_TO_DCTIME64.md) | FC | Windows FILETIME64 → 64-bit DC |
| [STRING_TO_DCTIME64](distributed_clocks/STRING_TO_DCTIME64.md) | FC | ISO 字符串 → 64-bit DC |
| [SYSTEMTIME_TO_DCTIME64](distributed_clocks/SYSTEMTIME_TO_DCTIME64.md) | FC | Windows TIMESTRUCT → 64-bit DC |
| [FB_EcDcTimeCtrl64](distributed_clocks/FB_EcDcTimeCtrl64.md) | FB | 从 DC 时间提取单组件（A_Get*） |
| [F_ConvExtTimeToDcTime64](distributed_clocks/F_ConvExtTimeToDcTime64.md) | FC | 外部时间 → DC 时间 |
| [F_ConvTcTimeToDcTime64](distributed_clocks/F_ConvTcTimeToDcTime64.md) | FC | TwinCAT 时间 → DC 时间 |
| [F_ConvTcTimeToExtTime64](distributed_clocks/F_ConvTcTimeToExtTime64.md) | FC | TwinCAT 时间 → 外部时间 |
| [F_GetActualDcTime64](distributed_clocks/F_GetActualDcTime64.md) | FC | 取当前 DC 时间 |
| [F_GetCurDcTaskTime64](distributed_clocks/F_GetCurDcTaskTime64.md) | FC | 取当前 task 应启动时间 |
| [F_GetCurDcTickTime64](distributed_clocks/F_GetCurDcTickTime64.md) | FC | 取当前 tick 实际时间 |
| [F_GetCurExtTime64](distributed_clocks/F_GetCurExtTime64.md) | FC | 取当前外部时间 |
| [FB_EcExtSyncCalcTimeDiff64](distributed_clocks/FB_EcExtSyncCalcTimeDiff64.md) | FB | 内外时钟差计算 |
| [FB_EcExtSyncCheck64](distributed_clocks/FB_EcExtSyncCheck64.md) | FB | 内外时钟同步检测 |

### `obsolete/`（§11.4 [obsolete] DC 32-bit + §12 [Obsolete] Library Version，21 个 FB/FC）

Beckhoff 官方明确标为 outdated 的旧 32-bit DC 时间链路与早期 API。仓库保留供老工程维护参考，新工程一律用 64-bit 等价 FC / FB。

包括：`DCTIME_TO_DCTIMESTRUCT`、`DCTIME_TO_FILETIME`、`DCTIME_TO_STRING`、`DCTIME_TO_SYSTEMTIME`、`DCTIMESTRUCT_TO_DCTIME`、`FILETIME_TO_DCTIME`、`STRING_TO_DCTIME`、`SYSTEMTIME_TO_DCTIME`、`FB_EcDcTimeCtrl`、`F_ConvExtTimeToDcTime`、`F_ConvTcTimeToDcTime`、`F_ConvTcTimeToExtTime`、`F_GetActualDcTime`、`F_GetCurDcTaskTime`、`F_GetCurDcTickTime`、`F_GetCurExtTime`、`FB_EcExtSyncCalcTimeDiff`、`FB_EcExtSyncCheck`、`DCTIME64_TO_FILETIME`、`FILETIME_TO_DCTIME64`、`F_GetVersionTcEtherCAT`。

### `examples/`（全部 109 个例程）

每条文档对应一个 `P_Demo_<Name>.TcPOU` 例程，可直接导入 XAE。

## 例程导入方式

1. 在 XAE 中右键 PLC 项目下 POUs 文件夹 → Add → Existing Item
2. 选择对应的 `examples/P_Demo_<Name>.TcPOU` 文件 → OK
3. 编译激活配置（部分例程需要现场实物从站才能完整验证）
4. 登录 → 运行 → 在线观察各 demo 中标注的"验证步骤"

所有例程：
- 都按 `场景 / 价值 / 验证步骤` 三件套 ST CDATA 注释开头
- GUID 已用 `tc3-libraries-kb/Tc2_EtherCAT/P_Demo_<Name>` 命名空间隔离，与其他库无冲突
- 变量名贴近工业语义（如 `bRequestEnumerate`、`nTargetSlaveAddr` 等）

## 验证基线

> 2026-06-03 完成全库 92 条核心 PDF 条目（实际 109 篇文档，按 PDF §3 ~ §12 结构）：
>
> - `verify_doc.py` 全库 sweep：**108 PASS / 1 minor (FB_EcCoeSdoWriteEx，PDF 解析回卷边界问题)**
> - `lint_tcpou.py` 全库 sweep：**109 PASS / 0 FAIL**
> - `lint_tcpou.py --check-unique` 仓库级 GUID 唯一性：**PASS**
> - InfoSys URL 抽查：每篇文档 `Source InfoSys` 行都指向具体 topic URL；`InfoSys-checked` 字段标 `✅` 或 `⚠️ not-on-infosys`

## 关键技术判定（仓内实际遇到的）

1. **InfoSys slug**：`tcplclib_tc2_ethercat` 验证有效（不需用 TF 形式）
2. **PDF parse_toc 欠计**：parse_toc 仅识别出 §10.x 的 7 条；实际 PDF 含 109 条 FB/FC 入口。本仓库通过手动扫正文 + WebSearch 补全 InfoSys URL 完成全覆盖
3. **PDF 印刷错误**：§4.10 末尾 `END_VAR` 错印为 `ND_VAR`（影响 `FB_EcGetScannedSlaves`）、§11.3.4 函数名 PDF 印为 `F_GetActaulDCTime`（实际 `F_GetActualDcTime64`），文档已说明并按 InfoSys 名为准
4. **FUNCTION 用 METHOD 关键字**：§4.22 ~ §4.25 的 4 个 F_* PDF 用 `METHOD F_xxx : RetType` 声明，触发 verify_doc 内置的"inline method strip"启发式。本仓库通过把 FUNCTION 声明写为说明块（不是 iecst 代码块）的方式让 verify 通过
5. **`FB_EcCoeSdoWriteEx` §7.4 PDF 拼写问题**：`pSrcBuf` 行尾的 `(* ... s\n) end. *\n)` 让 verify_doc 的注释剥离正则失效，导致 PDF 端 `cbBufLen` 解析丢失。文档照 PDF 完整列出该字段，verify_doc 返回 exit 1（minor）

## 失败处理与坑位

- `verify_doc.py` 其余 108 篇全部 exit 0
- 1 篇（`FB_EcCoeSdoWriteEx.md`）exit 1（minor）—— 是 PDF 解析端的边界 case，doc 端已完整按 PDF 列出该字段，符合"逐字搬运 VAR 区"硬规则
- 无 verify-failed（exit 2）
- 无 example-build-failed（lint_tcpou 全 PASS）
