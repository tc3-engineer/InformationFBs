# Tc2_NCI — TF5100 TwinCAT 3 NCI（CNC 路径插补）PLC 库

> Beckhoff TwinCAT 3 NCI（**N**umerical **C**ontrol **I**nterpolation）PLC 库，提供从 PLC 端**配置**、**操作**、**监视**一个完整 CNC 通道所需的全部 FB / FC。
> 用于：3D 路径插补、G-Code（DIN 66025）解释器控制、M 函数握手、工具补偿、零点偏移、R 参数读写、块搜索（Blocksearch）、路径回退（Retrace）、运行时动态生成 G-Code（Parts Program Generator）。
>
> - **Library Version**：2.15.1
> - **Source PDF**：[TF5100_TC3_NC_I_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf)（共 348 页，PDF §7.1.x = Tc2_NCI 的全部 PLC API）
> - **Source InfoSys**：https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/
> - **TF 工作负载**：`TF5100.NCI.XAE`（Engineering）+ `TF5100.NCI.XAR`（Runtime）

## 关键概念

- **NCI 通道（Channel）**：一个独立的 CNC 通道，由若干轴组成的『组』和一个解释器构成。System Manager 里看到的 NCI Channel 节点就是它。
- **3D 插补组（Group）**：最多 3 根**路径轴**（X/Y/Z）+ 最多 5 根**辅助轴**（Q1..Q5）。路径轴参与几何插补；辅助轴随程序段同步移动但不参与几何。
- **NCTOPLC_NCICHANNEL_REF / PLCTONC_NCICHANNEL_REF**：NC 与 PLC 之间的『循环通道接口』结构。在 System Manager 里 Link 给 PLC 端 `AT %I*` / `AT %Q*` 实例，所有 NCI POU 都要绑这两个引用之一。
- **bExecute 边沿语义**：所有带 `bExecute` 的 FB 都是**上升沿**触发；持续保持 TRUE 只第一次有效。状态查询类纯函数（如 `ItpHasError` `ItpGetBlockNumber`）则无此约束。
- **bBusy 的『接受』vs『完成』**：PDF 多次强调 `bBusy` 监视的是 NC 端**接受**命令的时间，**不是执行完成的时间**——对块搜索等真正『让轴动』的命令，要看 `bDone` 或 cyclic interface 字段判断完成。
- **错误号语义**：错误通过 `bErr` + `nErrId : UDINT` 上报；`nErrId` 是 **TwinCAT ADS / NC 错误码**（不是 HRESULT）。常见段：`16#07xx`（ADS 错误）、`16#4xxx`（NC 命令错误）。具体码表见 PDF 附录 / [NC Error Codes](https://infosys.beckhoff.com/content/1033/tcnc/178338827.html)。
- **`Ex` 后缀 vs 旧版**：带 `Ex` / `Ex2` 后缀的 FB 是新版本（支持当前 NCI 通道结构），不带后缀的 FB 仅为从 TwinCAT 2 移植的老项目兼容保留。新项目应使用带 `Ex` 的版本。

## 分类索引

### Configuration（NCI 通道配置，7 个）

按需在 PLC 端动态建立 / 撤销 3D 插补组、读回组内轴 ID。配置类操作必须在 NC 未启动 / 组无运动时调用。

| FB | 用途 | 文档 |
|---|---|---|
| `CfgBuild3DGroup`     | 把 3 根 PTP 轴（X/Y/Z）组成 NCI 3D 组 | [configuration/CfgBuild3DGroup.md](configuration/CfgBuild3DGroup.md) |
| `CfgBuildExt3DGroup`  | 3D 组扩展版：含 X/Y/Z + 5 根辅助轴 Q1..Q5 | [configuration/CfgBuildExt3DGroup.md](configuration/CfgBuildExt3DGroup.md) |
| `CfgAddAxisToGroup`   | 动态把单轴加到已有组（PTP / 3D / FIFO） | [configuration/CfgAddAxisToGroup.md](configuration/CfgAddAxisToGroup.md) |
| `CfgReconfigGroup`    | 撤销 3D / FIFO 组，把组内全部轴释放回 PTP 单轴组 | [configuration/CfgReconfigGroup.md](configuration/CfgReconfigGroup.md) |
| `CfgReconfigAxis`     | 单轴版的 `CfgReconfigGroup`：把单轴从组里抽出 | [configuration/CfgReconfigAxis.md](configuration/CfgReconfigAxis.md) |
| `CfgRead3DAxisIds`    | 读出某 3D 组当前包含的 X/Y/Z 三轴 AxisId | [configuration/CfgRead3DAxisIds.md](configuration/CfgRead3DAxisIds.md) |
| `CfgReadExt3DAxisIds` | `CfgRead3DAxisIds` 扩展版：连辅助轴 Q1..Q5 一并读 | [configuration/CfgReadExt3DAxisIds.md](configuration/CfgReadExt3DAxisIds.md) |

### NCI POUs（NCI 通用操作 — 带 `Ex` 后缀的新 API，50 个）

通道启停、Override、错误读取、M 函数 / R 参数 / 工具表 / 零点表读写、Cyclic 参数读取、解释器状态查询、加载 NC 程序等。所有带 `bExecute` 的 FB 都是 ADS 调用包装；纯 FC（`ItpGet*` `ItpIs*` `ItpHasError`）直接读 cyclic 镜像。

| FB / FC | 用途 | 文档 |
|---|---|---|
| `ItpConfirmHsk`               | 回执 Handshake M 函数 | [nci_pous/ItpConfirmHsk.md](nci_pous/ItpConfirmHsk.md) |
| `ItpDelDtgEx`                 | 删除剩余距离（当前段提前结束） | [nci_pous/ItpDelDtgEx.md](nci_pous/ItpDelDtgEx.md) |
| `ItpEnableDefaultGCode`       | NC 程序加载前注入默认 G-Code 前缀 | [nci_pous/ItpEnableDefaultGCode.md](nci_pous/ItpEnableDefaultGCode.md) |
| `ItpEStopEx`                  | NC 通道级 EStop（可续接） | [nci_pous/ItpEStopEx.md](nci_pous/ItpEStopEx.md) |
| `ItpGetBlockNumber`           | 读当前段段号 | [nci_pous/ItpGetBlockNumber.md](nci_pous/ItpGetBlockNumber.md) |
| `ItpGetBottleNeckLookAheadEx` | 读瓶颈检测预读段数 | [nci_pous/ItpGetBottleNeckLookAheadEx.md](nci_pous/ItpGetBottleNeckLookAheadEx.md) |
| `ItpGetBottleNeckModeEx`      | 读瓶颈检测模式 | [nci_pous/ItpGetBottleNeckModeEx.md](nci_pous/ItpGetBottleNeckModeEx.md) |
| `ItpGetChannelId`             | 读 NCI 通道 ID | [nci_pous/ItpGetChannelId.md](nci_pous/ItpGetChannelId.md) |
| `ItpGetChannelType`           | 读通道类型枚举 | [nci_pous/ItpGetChannelType.md](nci_pous/ItpGetChannelType.md) |
| `ItpGetCyclicLrealOffsets`    | 读 4 个 LREAL cyclic 参数的 NC 端字节偏移 | [nci_pous/ItpGetCyclicLrealOffsets.md](nci_pous/ItpGetCyclicLrealOffsets.md) |
| `ItpGetCyclicUDintOffsets`    | 读 4 个 UDINT cyclic 参数的 NC 端字节偏移 | [nci_pous/ItpGetCyclicUDintOffsets.md](nci_pous/ItpGetCyclicUDintOffsets.md) |
| `ItpGetError`                 | 读通道错误（含错误号 + 出错段号） | [nci_pous/ItpGetError.md](nci_pous/ItpGetError.md) |
| `ItpGetGeoInfoAndHParamEx`    | 读当前段几何信息 + H 参数 | [nci_pous/ItpGetGeoInfoAndHParamEx.md](nci_pous/ItpGetGeoInfoAndHParamEx.md) |
| `ItpGetGroupAxisIds`          | 读组内 8 槽位 AxisId 数组（从 cyclic 镜像，零开销） | [nci_pous/ItpGetGroupAxisIds.md](nci_pous/ItpGetGroupAxisIds.md) |
| `ItpGetGroupId`               | 读当前通道关联的 GroupId | [nci_pous/ItpGetGroupId.md](nci_pous/ItpGetGroupId.md) |
| `ItpGetHParam`                | 读当前段 H 参数 | [nci_pous/ItpGetHParam.md](nci_pous/ItpGetHParam.md) |
| `ItpGetHskMFunc`              | 读当前等待 PLC 回执的 Handshake M 函数号 | [nci_pous/ItpGetHskMFunc.md](nci_pous/ItpGetHskMFunc.md) |
| `ItpGetItfVersion`            | 读 cyclic interface 接口版本号 | [nci_pous/ItpGetItfVersion.md](nci_pous/ItpGetItfVersion.md) |
| `ItpGetOverridePercent`       | 读通道速度倍率 | [nci_pous/ItpGetOverridePercent.md](nci_pous/ItpGetOverridePercent.md) |
| `ItpGetSetPathVelocity`       | 读当前设定路径速度 | [nci_pous/ItpGetSetPathVelocity.md](nci_pous/ItpGetSetPathVelocity.md) |
| `ItpGetSParam`                | 读当前段 S 参数 | [nci_pous/ItpGetSParam.md](nci_pous/ItpGetSParam.md) |
| `ItpGetStateInterpreter`      | 读解释器状态机当前状态 | [nci_pous/ItpGetStateInterpreter.md](nci_pous/ItpGetStateInterpreter.md) |
| `ItpGetTParam`                | 读当前段 T 参数（Tool 号） | [nci_pous/ItpGetTParam.md](nci_pous/ItpGetTParam.md) |
| `ItpGoAheadEx`                | 解释器暂停后由 PLC 显式放行 | [nci_pous/ItpGoAheadEx.md](nci_pous/ItpGoAheadEx.md) |
| `ItpHasError`                 | 读通道是否有错误（仅 BOOL） | [nci_pous/ItpHasError.md](nci_pous/ItpHasError.md) |
| `ItpIsFastMFunc`              | 判断 M 函数号是否被标为 Fast | [nci_pous/ItpIsFastMFunc.md](nci_pous/ItpIsFastMFunc.md) |
| `ItpIsEStopEx`                | 查询是否处于 EStop 状态 | [nci_pous/ItpIsEStopEx.md](nci_pous/ItpIsEStopEx.md) |
| `ItpIsHskMFunc`               | 查询是否有 Handshake M 函数等待 | [nci_pous/ItpIsHskMFunc.md](nci_pous/ItpIsHskMFunc.md) |
| `ItpLoadProgEx`               | 加载 NC 程序文件到解释器 | [nci_pous/ItpLoadProgEx.md](nci_pous/ItpLoadProgEx.md) |
| `ItpReadCyclicLRealParam1`    | 读第 1 个 LREAL cyclic 参数 | [nci_pous/ItpReadCyclicLRealParam1.md](nci_pous/ItpReadCyclicLRealParam1.md) |
| `ItpReadCyclicUdintParam1`    | 读第 1 个 UDINT cyclic 参数 | [nci_pous/ItpReadCyclicUdintParam1.md](nci_pous/ItpReadCyclicUdintParam1.md) |
| `ItpReadRParamsEx`            | 读 NC R 参数数组段 | [nci_pous/ItpReadRParamsEx.md](nci_pous/ItpReadRParamsEx.md) |
| `ItpReadToolDescEx`           | 读 NC 工具表中指定工具描述 | [nci_pous/ItpReadToolDescEx.md](nci_pous/ItpReadToolDescEx.md) |
| `ItpReadZeroShiftEx`          | 读 NC 零点偏移表 | [nci_pous/ItpReadZeroShiftEx.md](nci_pous/ItpReadZeroShiftEx.md) |
| `ItpResetEx2`                 | 通道复位（清错） | [nci_pous/ItpResetEx2.md](nci_pous/ItpResetEx2.md) |
| `ItpResetFastMFuncEx`         | 清空 Fast M 函数位图 | [nci_pous/ItpResetFastMFuncEx.md](nci_pous/ItpResetFastMFuncEx.md) |
| `ItpSetBottleNeckLookAheadEx` | 设瓶颈检测预读段数 | [nci_pous/ItpSetBottleNeckLookAheadEx.md](nci_pous/ItpSetBottleNeckLookAheadEx.md) |
| `ItpSetBottleNeckModeEx`      | 设瓶颈检测模式 | [nci_pous/ItpSetBottleNeckModeEx.md](nci_pous/ItpSetBottleNeckModeEx.md) |
| `ItpSetCyclicLrealOffsets`    | 配置 4 个 LREAL cyclic 参数字节偏移 | [nci_pous/ItpSetCyclicLrealOffsets.md](nci_pous/ItpSetCyclicLrealOffsets.md) |
| `ItpSetCyclicUDintOffsets`    | 配置 4 个 UDINT cyclic 参数字节偏移 | [nci_pous/ItpSetCyclicUDintOffsets.md](nci_pous/ItpSetCyclicUDintOffsets.md) |
| `ItpSetOverridePercent`       | 设通道速度倍率 | [nci_pous/ItpSetOverridePercent.md](nci_pous/ItpSetOverridePercent.md) |
| `ItpSetSubroutinePathEx`      | 设子程序文件查找路径 | [nci_pous/ItpSetSubroutinePathEx.md](nci_pous/ItpSetSubroutinePathEx.md) |
| `ItpSetToolDescNullEx`        | 清空指定工具描述 | [nci_pous/ItpSetToolDescNullEx.md](nci_pous/ItpSetToolDescNullEx.md) |
| `ItpSetZeroShiftNullEx`       | 清空指定零点偏移 | [nci_pous/ItpSetZeroShiftNullEx.md](nci_pous/ItpSetZeroShiftNullEx.md) |
| `ItpSingleBlock`              | 切到单段执行模式（调试 NC 程序用） | [nci_pous/ItpSingleBlock.md](nci_pous/ItpSingleBlock.md) |
| `ItpStartStopEx`              | 启动 / 停止 NCI 通道 | [nci_pous/ItpStartStopEx.md](nci_pous/ItpStartStopEx.md) |
| `ItpStepOnAfterEStopEx`       | EStop 后续接执行 | [nci_pous/ItpStepOnAfterEStopEx.md](nci_pous/ItpStepOnAfterEStopEx.md) |
| `ItpWriteRParamsEx`           | 写 NC R 参数数组 | [nci_pous/ItpWriteRParamsEx.md](nci_pous/ItpWriteRParamsEx.md) |
| `ItpWriteToolDescEx`          | 写工具描述到 NC 工具表 | [nci_pous/ItpWriteToolDescEx.md](nci_pous/ItpWriteToolDescEx.md) |
| `ItpWriteZeroShiftEx`         | 写零点偏移到 NC 零点表 | [nci_pous/ItpWriteZeroShiftEx.md](nci_pous/ItpWriteZeroShiftEx.md) |

### Blocksearch（块搜索，3 个）

把 NCI 解释器临时停在指定 NC 程序段，操作员手动把物理轴搬到该段起点，然后续接执行。换刀 / 班次结束续接的标准流程。

| FB | 用途 | 文档 |
|---|---|---|
| `ItpBlocksearch`            | 把解释器定位到指定段 + 给出该段起点坐标 | [blocksearch/ItpBlocksearch.md](blocksearch/ItpBlocksearch.md) |
| `ItpGetBlocksearchData`     | 程序中断时记录当前路径位置（供 ItpBlocksearch 用） | [blocksearch/ItpGetBlocksearchData.md](blocksearch/ItpGetBlocksearchData.md) |
| `ItpStepOnAfterBlocksearch` | Blocksearch 完成后续接执行 | [blocksearch/ItpStepOnAfterBlocksearch.md](blocksearch/ItpStepOnAfterBlocksearch.md) |

### Retrace（路径回退，7 个）

让 NCI 沿已走过的路径向后退 / 再向前走（复杂轮廓加工出错后 rework 的标准做法）。

| FB / FC | 用途 | 文档 |
|---|---|---|
| `ItpEnableFeederBackup`     | **必须最先调用**：启用路径备份 | [retrace/ItpEnableFeederBackup.md](retrace/ItpEnableFeederBackup.md) |
| `ItpIsFeederBackupEnabled`  | 查询路径备份是否已启用 | [retrace/ItpIsFeederBackupEnabled.md](retrace/ItpIsFeederBackupEnabled.md) |
| `ItpIsFeedFromBackupList`   | 查询当前是否在 Retrace 模式 | [retrace/ItpIsFeedFromBackupList.md](retrace/ItpIsFeedFromBackupList.md) |
| `ItpIsFirstSegmentReached`  | 查询是否已退到路径备份的第一段 | [retrace/ItpIsFirstSegmentReached.md](retrace/ItpIsFirstSegmentReached.md) |
| `ItpIsMovingBackwards`      | 查询当前是否在反向运动 | [retrace/ItpIsMovingBackwards.md](retrace/ItpIsMovingBackwards.md) |
| `ItpRetraceMoveBackward`    | 触发沿已走过路径回退 | [retrace/ItpRetraceMoveBackward.md](retrace/ItpRetraceMoveBackward.md) |
| `ItpRetraceMoveForward`     | 触发沿备份路径前进 | [retrace/ItpRetraceMoveForward.md](retrace/ItpRetraceMoveForward.md) |

### Parts program generator（运行时生成 G-Code，7 个）

在 PLC 里把 G-Code 段逐条拼装、写入 `.nc` 文件给解释器加载。典型流程：`Create` → 追加段 `Append*` → `Close`。

| FB | 用途 | 文档 |
|---|---|---|
| `ItpPpgCreateMain`             | 新建（或覆盖）主程序文件，进入编辑状态 | [parts_program_generator/ItpPpgCreateMain.md](parts_program_generator/ItpPpgCreateMain.md) |
| `ItpPpgCreateSubroutine`       | 新建子程序文件 | [parts_program_generator/ItpPpgCreateSubroutine.md](parts_program_generator/ItpPpgCreateSubroutine.md) |
| `ItpPpgAppendGeoLine`          | 追加 G01 直线段 | [parts_program_generator/ItpPpgAppendGeoLine.md](parts_program_generator/ItpPpgAppendGeoLine.md) |
| `ItpPpgAppendGeoCircleByRadius`| 追加按半径定义的圆弧段 | [parts_program_generator/ItpPpgAppendGeoCircleByRadius.md](parts_program_generator/ItpPpgAppendGeoCircleByRadius.md) |
| `ItpPpgAppendGenericBlock`     | 追加任意 G-Code 文本段 | [parts_program_generator/ItpPpgAppendGenericBlock.md](parts_program_generator/ItpPpgAppendGenericBlock.md) |
| `ItpPpgCloseMain`              | 主程序文件落盘并关闭 | [parts_program_generator/ItpPpgCloseMain.md](parts_program_generator/ItpPpgCloseMain.md) |
| `ItpPpgCloseSubroutine`        | 子程序文件落盘并关闭 | [parts_program_generator/ItpPpgCloseSubroutine.md](parts_program_generator/ItpPpgCloseSubroutine.md) |

### Compatibility（旧版本兼容 — 不带 `Ex`，24 个）

仅为 TwinCAT 2 移植项目兼容保留；新项目应使用对应的 `*Ex` / `*Ex2` 版本。

| FB | 对应的新版 | 文档 |
|---|---|---|
| `ItpDelDtg`                 | `ItpDelDtgEx`                 | [compatibility/ItpDelDtg.md](compatibility/ItpDelDtg.md) |
| `ItpEStop`                  | `ItpEStopEx`                  | [compatibility/ItpEStop.md](compatibility/ItpEStop.md) |
| `ItpGetBottleNeckLookAhead` | `ItpGetBottleNeckLookAheadEx` | [compatibility/ItpGetBottleNeckLookAhead.md](compatibility/ItpGetBottleNeckLookAhead.md) |
| `ItpGetBottleNeckMode`      | `ItpGetBottleNeckModeEx`      | [compatibility/ItpGetBottleNeckMode.md](compatibility/ItpGetBottleNeckMode.md) |
| `ItpGetGeoInfoAndHParam`    | `ItpGetGeoInfoAndHParamEx`    | [compatibility/ItpGetGeoInfoAndHParam.md](compatibility/ItpGetGeoInfoAndHParam.md) |
| `ItpGoAhead`                | `ItpGoAheadEx`                | [compatibility/ItpGoAhead.md](compatibility/ItpGoAhead.md) |
| `ItpIsEStop`                | `ItpIsEStopEx`                | [compatibility/ItpIsEStop.md](compatibility/ItpIsEStop.md) |
| `ItpLoadProg`               | `ItpLoadProgEx`               | [compatibility/ItpLoadProg.md](compatibility/ItpLoadProg.md) |
| `ItpReadRParams`            | `ItpReadRParamsEx`            | [compatibility/ItpReadRParams.md](compatibility/ItpReadRParams.md) |
| `ItpReadToolDesc`           | `ItpReadToolDescEx`           | [compatibility/ItpReadToolDesc.md](compatibility/ItpReadToolDesc.md) |
| `ItpReadZeroShift`          | `ItpReadZeroShiftEx`          | [compatibility/ItpReadZeroShift.md](compatibility/ItpReadZeroShift.md) |
| `ItpReset`                  | `ItpResetEx2`                 | [compatibility/ItpReset.md](compatibility/ItpReset.md) |
| `ItpResetEx`                | `ItpResetEx2`                 | [compatibility/ItpResetEx.md](compatibility/ItpResetEx.md) |
| `ItpResetFastMFunc`         | `ItpResetFastMFuncEx`         | [compatibility/ItpResetFastMFunc.md](compatibility/ItpResetFastMFunc.md) |
| `ItpSetBottleNeckLookAhead` | `ItpSetBottleNeckLookAheadEx` | [compatibility/ItpSetBottleNeckLookAhead.md](compatibility/ItpSetBottleNeckLookAhead.md) |
| `ItpSetBottleNeckMode`      | `ItpSetBottleNeckModeEx`      | [compatibility/ItpSetBottleNeckMode.md](compatibility/ItpSetBottleNeckMode.md) |
| `ItpSetSubroutinePath`      | `ItpSetSubroutinePathEx`      | [compatibility/ItpSetSubroutinePath.md](compatibility/ItpSetSubroutinePath.md) |
| `ItpSetToolDescNull`        | `ItpSetToolDescNullEx`        | [compatibility/ItpSetToolDescNull.md](compatibility/ItpSetToolDescNull.md) |
| `ItpSetZeroShiftNull`       | `ItpSetZeroShiftNullEx`       | [compatibility/ItpSetZeroShiftNull.md](compatibility/ItpSetZeroShiftNull.md) |
| `ItpStartStop`              | `ItpStartStopEx`              | [compatibility/ItpStartStop.md](compatibility/ItpStartStop.md) |
| `ItpStepOnAfterEStop`       | `ItpStepOnAfterEStopEx`       | [compatibility/ItpStepOnAfterEStop.md](compatibility/ItpStepOnAfterEStop.md) |
| `ItpWriteRParams`           | `ItpWriteRParamsEx`           | [compatibility/ItpWriteRParams.md](compatibility/ItpWriteRParams.md) |
| `ItpWriteToolDesc`          | `ItpWriteToolDescEx`          | [compatibility/ItpWriteToolDesc.md](compatibility/ItpWriteToolDesc.md) |
| `ItpWriteZeroShift`         | `ItpWriteZeroShiftEx`         | [compatibility/ItpWriteZeroShift.md](compatibility/ItpWriteZeroShift.md) |

### Obsolete（已过时，3 个）

仅为读取旧版 TwinCAT 2 PLC 库版本号保留。新项目读库版本请改用 `stLibVersion_Tc2_NCI` 配 `Tc2_System.F_CmpLibVersion`。

| FC | 用途 | 文档 |
|---|---|---|
| `F_GetVersionTcNciUtilities` | 读旧 `TcNciUtilities.lib` 版本号段 | [obsolete/F_GetVersionTcNciUtilities.md](obsolete/F_GetVersionTcNciUtilities.md) |
| `Get_TcNcCfg_Version`        | 读旧 `TcNcCfg.lib` 版本字符串 | [obsolete/Get_TcNcCfg_Version.md](obsolete/Get_TcNcCfg_Version.md) |
| `ItpGetVersion`              | 读旧 `TcNC.lib` 版本字符串 | [obsolete/ItpGetVersion.md](obsolete/ItpGetVersion.md) |

## 例程

所有 101 个文档都配套一个 [`examples/P_Demo_<Name>.TcPOU`](examples/) — TwinCAT 3 原生 `.TcPOU` 格式，右键 PLC 项目下 POUs 文件夹 → Add → Existing Item 即可导入。每个例程都按本仓库 2026-05-11 行动纲领的 D 节要求，头部带 **场景 / 价值 / 验证步骤** 三件套中文注释。

**例程通用前置**（所有 NCI 例程都假设这些步骤已完成）：

1. 在 System Manager 配好 NC 轴（至少 X/Y/Z 三根 PTP 轴）；
2. 在 System Manager 配好 NCI 通道（Channel + Group + 把 PTP 轴加入 Group）；
3. 在 PLC 项目 References 里引用 `Tc2_NCI`；
4. 把例程里的 `sNciToPlc_inst : NCTOPLC_NCICHANNEL_REF` Link 给 NCI 通道的 NCTOPLC 输入接口（`AT %I*`）；若 FB 还要 `sPlcToNci_inst : PLCTONC_NCICHANNEL_REF`，Link 给 PLCTONC 输出接口（`AT %Q*`）。

## 与其它库的搭配

- **`Tc2_System`**：版本守卫（`F_CmpLibVersion` + `stLibVersion_Tc2_NCI`）、`ADSRDWRTEX` 兜底通用 ADS 调用。
- **`Tc2_MC2`** / **`Tc2_NcDrive`**：NCI 通道里的物理轴本身需要先用 `MC_Power` 等 MC FB 使能 / 复位 / 查询状态。NCI 操控的是『通道层』，MC 操控的是『单轴层』。
- **`Tc2_PlcInterpolation`**：本 PDF 的 §7.2，提供另一种 PLC 直接发段的方案（不走 G-Code 文件，直接调 `FB_NciFeedTablePreparation` / `FB_NciFeedTable`）。本 README 不包含该库内容；如需查请看仓库的 `Tc2_PlcInterpolation/`（如有）。
- **`Tc3_McCoordinatedMotion`**：TF5420 Pick-and-Place，针对 Pick-and-Place 应用的替代方案，不是 G-Code 路径。

## 文档质量

所有 101 篇通过：

- `_meta/tools/verify_doc.py` — VAR 区一致、占位短语 / 中文长度 / InfoSys URL 检查全 PASS
- `_meta/tools/lint_tcpou.py` — 例程 XML 结构合法
- `_meta/tools/lint_tcpou.py --check-unique` — 例程 GUID 在全仓粒度唯一
- InfoSys 主题 URL 已逐条校验（`InfoSys-checked: ✅ 2026-06-03`）

## 已知限制 / ⚠️

- **错误码段（`nErrId`）**：PDF 在每个 FB 章节未逐条枚举具体 NC 错误码值；本仓库不脑补具体码，仅指向 `16#07xx`（ADS）/ `16#4xxx`（NC）两大段，定位具体码请参考 [ADS Return Codes](https://infosys.beckhoff.com/content/1033/tc3_ads_intro/374277003.html) 与 [NC Error Codes](https://infosys.beckhoff.com/content/1033/tcnc/178338827.html)。
- **变量描述**：少量 PDF 中未在 Description 列说清楚的输入（比如配置类 FB 的 `nGroupId` 取值范围）在表格里以中文工程经验做了具体注释，并在 `parse_toc.py` 兜底不到的情况下不会用 ⚠️ 占位（统一指向具体含义）。
- **`parse_toc.py` 对本库返回空**：TF 手册的 TOC 结构不被通用 TOC 解析器识别；本库的条目清单由 `_meta/tools/_tc2nci_registry.json` 手工维护（PDF + InfoSys 双源核对过），生成器 `_meta/tools/_tc2nci_gen.py` 据此读取每个 FB 的 PDF 章节生成文档。
