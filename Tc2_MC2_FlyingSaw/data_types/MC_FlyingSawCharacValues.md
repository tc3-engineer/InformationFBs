# MC_FlyingSawCharacValues

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_FlyingSaw` |
| Library Version | `1.6.1` |
| Type | `STRUCT` (DUT) |
| Category | `Data types` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5055_TC3_NC_Flying_Saw_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5055_tc3_nc_flying_saw/1004162059.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_FlyingSawCharacValues.xml`](../examples/P_Demo_MC_FlyingSawCharacValues.xml) |

---

## 1. 功能简述

飞锯（Flying Saw）同步特征参数的**结构体类型定义**（DUT，`STRUCT`）。它不是功能块而是一个数据载体：由 `MC_ReadFlyingSawCharacteristics` 读取并填充，描述一次飞锯同步轮廓（cam-table）的全部特征量——同步起点/终点的主从位置、速度、加速度、Jerk，以及同步过程中从轴位置/速度/加速度/Jerk 的最大最小极值和均值/有效值，外加轮廓表的组织信息（表 ID、行列数、表类型、是否周期）。

工程上用它来**定量校核同步轮廓是否在机械允许范围内**（如最大从轴速度是否超限），或记录/诊断同步过程。

## 2. 接口定义

本条目是结构体类型，不含 VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT；以下为 `STRUCT` 成员（与 PDF 逐字一致，含原始注释序号）。

### STRUCT 成员

```iecst
TYPE MC_FlyingSawCharacValues :
STRUCT
    fMasterVeloNom     : LREAL; (* 1. master nominal velocity (normed:=> 1.0) *)
    fMasterPosStart    : LREAL; (* 2. master start position*)
    fSlavePosStart     : LREAL; (* 3. slave start position *)
    fSlaveVeloStart    : LREAL; (* 4. slave start velocity *)
    fSlaveAccStart     : LREAL; (* 5. slave start acceleration *)
    fSlaveJerkStart    : LREAL; (* 6. slave start jerk *)
    fMasterPosEnd      : LREAL; (* 7. master end position *)
    fSlavePosEnd       : LREAL; (* 8. slave end position *)
    fSlaveVeloEnd      : LREAL; (* 9. slave end velocity *)
    fSlaveAccEnd       : LREAL; (* 10. slave end acceleration *)
    fSlaveJerkEnd      : LREAL; (* 11. slave end jerk *)
    fMPosAtSPosMin     : LREAL; (* 12. master position AT slave minimum position *)
    fSlavePosMin       : LREAL; (* 13. slave minimum position *)
    fMPosAtSVeloMin    : LREAL; (* 14. master position AT slave minimum velocity *)
    fSlaveVeloMin      : LREAL; (* 15. slave minimum velocity *)
    fMPosAtSAccMin     : LREAL; (* 16. master position AT slave minimum acceleration *)
    fSlaveAccMin       : LREAL; (* 17. slave minimum acceleration *)
    fSVeloAtSAccMin    : LREAL; (* 18. slave velocity AT slave minimum acceleration *)
    fSlaveJerkMin      : LREAL; (* 19. slave minimum jerk *)
    fSlaveDynMomMin    : LREAL; (* 20. slave minimum dynamic momentum: min[v(t)*a(t)] (NOT SUPPORTED YET !) *)
    fMPosAtSPosMax     : LREAL; (* 21. master position AT slave maximum position *)
    fSlavePosMax       : LREAL; (* 22. slave maximum position *)
    fMPosAtSVeloMax    : LREAL; (* 23. master position AT slave maximum velocity *)
    fSlaveVeloMax      : LREAL; (* 24. slave maximum velocity *)
    fMPosAtSAccMax     : LREAL; (* 25. master position AT slave maximum acceleration *)
    fSlaveAccMax       : LREAL; (* 26. slave maximum acceleration *)
    fSVeloAtSAccMax    : LREAL; (* 27. slave velocity AT slave maximum acceleration *)
    fSlaveJerkMax      : LREAL; (* 28. slave maximum jerk *)
    fSlaveDynMomMax    : LREAL; (* 29. slave maximum dynamic momentum: max[v(t)*a(t)] (NOT SUPPORTED YET !) *)
    fSlaveVeloMean     : LREAL; (* 30. slave mean absolute velocity (unsigned value) *)
    fSlaveAccEff       : LREAL; (* 31. slave effective acceleration (unsigned value) *)
    reserved           : ARRAY[32..47] OF LREAL;
    CamTableID         : UDINT;
    NumberOfRows       : UDINT; (* number of cam table entries, e.g. number of points *)
    NumberOfColumns    : UDINT; (* number of table columns, typically 1 or 2 *)
    TableType          : UINT; (* MC_TableType *)
    Periodic           : BOOL;
    reserved2          : ARRAY[1..121] OF BYTE;
END_STRUCT
END_TYPE
```

| 成员（组） | 类型 | 说明 |
|---|---|---|
| `fMasterVeloNom` | `LREAL` | 主轴标称速度（归一化为 1.0） |
| `fMasterPosStart` / `fSlavePosStart` | `LREAL` | 同步起点的主轴 / 从轴位置（cam-table 起点） |
| `fSlaveVeloStart` / `fSlaveAccStart` / `fSlaveJerkStart` | `LREAL` | 同步起点从轴速度 / 加速度 / Jerk |
| `fMasterPosEnd` / `fSlavePosEnd` | `LREAL` | 同步终点的主轴 / 从轴位置（cam-table 终点） |
| `fSlaveVeloEnd` / `fSlaveAccEnd` / `fSlaveJerkEnd` | `LREAL` | 同步终点从轴速度 / 加速度 / Jerk |
| `fMPosAtSPosMin` / `fSlavePosMin` | `LREAL` | 从轴位置取最小时的主轴位置 / 从轴最小位置 |
| `fMPosAtSVeloMin` / `fSlaveVeloMin` | `LREAL` | 从轴速度取最小时的主轴位置 / 从轴最小速度 |
| `fMPosAtSAccMin` / `fSlaveAccMin` / `fSVeloAtSAccMin` | `LREAL` | 从轴加速度取最小时的主轴位置 / 从轴最小加速度 / 该点从轴速度 |
| `fSlaveJerkMin` | `LREAL` | 从轴最小 Jerk |
| `fSlaveDynMomMin` | `LREAL` | 从轴最小动态动量 min[v(t)·a(t)]（⚠️ 当前尚未支持 / NOT SUPPORTED YET） |
| `fMPosAtSPosMax` / `fSlavePosMax` | `LREAL` | 从轴位置取最大时的主轴位置 / 从轴最大位置 |
| `fMPosAtSVeloMax` / `fSlaveVeloMax` | `LREAL` | 从轴速度取最大时的主轴位置 / 从轴最大速度 |
| `fMPosAtSAccMax` / `fSlaveAccMax` / `fSVeloAtSAccMax` | `LREAL` | 从轴加速度取最大时的主轴位置 / 从轴最大加速度 / 该点从轴速度 |
| `fSlaveJerkMax` | `LREAL` | 从轴最大 Jerk |
| `fSlaveDynMomMax` | `LREAL` | 从轴最大动态动量 max[v(t)·a(t)]（⚠️ 当前尚未支持 / NOT SUPPORTED YET） |
| `fSlaveVeloMean` | `LREAL` | 从轴平均绝对速度（无符号值） |
| `fSlaveAccEff` | `LREAL` | 从轴有效加速度（无符号值） |
| `reserved` | `ARRAY[32..47] OF LREAL` | 保留，供未来扩展 |
| `CamTableID` | `UDINT` | cam-table 的 ID |
| `NumberOfRows` | `UDINT` | cam-table 条目数（点数） |
| `NumberOfColumns` | `UDINT` | cam-table 列数（通常 1 或 2） |
| `TableType` | `UINT` | 表类型（对应 `MC_TableType`） |
| `Periodic` | `BOOL` | 是否周期性表 |
| `reserved2` | `ARRAY[1..121] OF BYTE` | 保留 |

## 3. 行为说明

本结构体是**输出数据载体**，本身没有行为/时序——它的填充由 `MC_ReadFlyingSawCharacteristics` 完成：在飞锯同步启动后调用该 FB，`Done = TRUE` 时本结构各字段被写入有效值。读出后这些字段即代表本次同步轮廓的特征。

**字段语义组织**：可分为三类。(1) 起止点量：`*Start` / `*End` 给同步段两端的位置/速度/加速度/Jerk；(2) 极值量：`fSlave*Min` / `fSlave*Max` 给同步段内从轴位置/速度/加速度/Jerk 的极值，配套的 `fMPosAtS*` 给出取得该极值时的主轴位置，便于定位极值发生在轮廓哪一处；(3) 统计量与表结构：`fSlaveVeloMean` / `fSlaveAccEff` 给均值/有效值，`CamTableID` / `NumberOfRows` / `NumberOfColumns` / `TableType` / `Periodic` 描述轮廓表本身。

**未支持字段**：`fSlaveDynMomMin` / `fSlaveDynMomMax`（动态动量 v·a）PDF 标注 "NOT SUPPORTED YET"，当前版本不要依赖这两个字段的值。

**典型用法**：读出后用 `fSlaveVeloMax` / `fSlaveAccMax` 与轴机械允许的最大速度/加速度比较，判断同步轮廓是否安全；或用起止位置做诊断记录。

## 4. 错误码 / 返回值

本条目是结构体类型，无返回值、无错误码。读取过程中的错误由 `MC_ReadFlyingSawCharacteristics` 的 `Error` / `ErrorID` 输出反映，见该 FB 文档。

## 5. 使用注意 / 常见坑

- **本身只是数据结构**：不能"调用"它；要拿到有效值必须经 `MC_ReadFlyingSawCharacteristics` 在飞锯启动后读取。
- **动态动量字段当前无效**：`fSlaveDynMomMin` / `fSlaveDynMomMax` 标注 NOT SUPPORTED YET，别用其值做判断。
- **极值字段要配主轴位置一起看**：`fSlaveVeloMax` 的发生位置由 `fMPosAtSVeloMax` 给出，单看极值不知道在轮廓哪处。
- **`reserved` / `reserved2` 不要写**：是为未来扩展预留的，按保留处理。
- **单位与轴定标一致**：所有位置/速度量的单位跟随该从轴的 NC 定标。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_FlyingSawCharacValues.xml`](../examples/P_Demo_MC_FlyingSawCharacValues.xml)

```iecst
// 场景：飞锯调试，声明特征值结构供 MC_ReadFlyingSawCharacteristics 填充，读出后取关键极值做安全校核
PROGRAM P_Demo_MC_FlyingSawCharacValues
VAR
    fbReadCharac    : MC_ReadFlyingSawCharacteristics;
    axisCrossSaw    : AXIS_REF;
    charValues      : MC_FlyingSawCharacValues;   // 本结构体：特征值载体
    bReadReq        : BOOL;
    rtRead          : R_TRIG;
    bDone           : BOOL;
    bBusy           : BOOL;
    bErr            : BOOL;
    nErrID          : UDINT;
    fVeloMax        : LREAL;     // 从结构读出的从轴最大速度
    fAccMax         : LREAL;     // 从结构读出的从轴最大加速度
    bWithinLimit    : BOOL;      // 是否在机械限值内
END_VAR

rtRead(CLK := bReadReq);
fbReadCharac(
    Execute        := rtRead.Q,
    Slave          := axisCrossSaw,
    CamTableCharac := charValues,
    Done           => bDone,
    Busy           => bBusy,
    Error          => bErr,
    ErrorID        => nErrID
);
IF bDone THEN
    fVeloMax     := charValues.fSlaveVeloMax;
    fAccMax      := charValues.fSlaveAccMax;
    bWithinLimit := (fVeloMax <= 1000.0) AND (fAccMax <= 5000.0);   // 与机械限值比对
END_IF;
IF NOT bBusy THEN
    bReadReq := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：飞锯/横切的同步轮廓安全校核、投产前定量评估、运行诊断与追溯、自适应调参的数据来源。
- **价值**：把 NC 内部计算的同步轮廓特征以一个结构化类型暴露给 PLC，让"同步段从轴最大速度/加速度是否超限"这类问题可以在程序里量化判断，而不必靠经验或示波器盲看。
- **替代方案对比**：
  - 自己用 ADS 读 NC cam-table 原始数据并解析：底层、需懂 NC 内部布局
  - **本结构** + `MC_ReadFlyingSawCharacteristics`：官方封装，字段语义清晰

## 8. 参考资料

- **PDF**：[TF5055_TC3_NC_Flying_Saw_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5055_TC3_NC_Flying_Saw_EN.pdf) §6.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5055_tc3_nc_flying_saw/1004162059.html
- **相关 FB / DUT**：`MC_ReadFlyingSawCharacteristics`（读取并填充本结构）、`MC_GearInVelo` / `MC_GearInPos`（建立飞锯同步）
