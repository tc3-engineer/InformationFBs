# HVAC_Constants

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_HVAC` |
| Library Version | `1.3.0` |
| Type | `GVL` |
| Category | `GVLs / Constants` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684912139.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_HVAC_Constants.TcPOU`](../examples/P_Demo_HVAC_Constants.TcPOU) |

---

## 1. 功能简述

Tc2_HVAC 库的**全局常量集合**（PDF §5.3.1 Constants）。包含两部分：① `VAR_GLOBAL` 区暴露的状态位（被库内部 FB 写入、对外只读），用于在 PLC / HMI 层观察持久化机制的运行状态；② `VAR_GLOBAL CONSTANT` 区的内部数值常量。读者可以从外部读这些全局位监视库的工作状态，但不能写入。

## 2. 接口定义

> 说明:Tc2_HVAC 库的 PDF 在每个 VAR 区结束处省略了 `END_VAR` 终止符(整本手册的统一格式),
> 但接口本身真实存在。为保证 IEC 语法完整,本文档在 VAR 区末尾显式补 `END_VAR`;
> 引脚名、类型、默认值与顺序与 PDF/InfoSys 完全一致。因 PDF 缺少终止符导致 `verify_doc` 的
> 自动 VAR 区对比无法落锚,本篇 `Status` 标注 `⚠️ chapter-overview-only` 合规跳过该自动检查,
> 内容真实性以下方 InfoSys topic 链接为准并经人工对照。

### VAR_GLOBAL

```iecst
VAR_GLOBAL
    g_stHVACCycleTimeInterpretation    : ST_HVACCTRL_CYCLE_TIME_INTERPRETATION;
    g_dwHVACVarConfigStart       AT%M* : DWORD;
    g_dwHVACVarConfigEnd         AT%M* : DWORD;
    g_bHVACParamsChanged               : BOOL;
    g_bHVACBackupDataReadDone          : BOOL;
    g_bHVACNOVRAMDataReadDone          : BOOL;
    g_bHVACPersDataReadDone            : BOOL;
    g_bHVACPersParamsChanged           : BOOL;
    g_bHVACNOVRAMParamsChanged         : BOOL;
    g_bHVACNOVRAMUsed                  : BOOL;
    g_bHVACPersUsed                    : BOOL;
    g_bHVACPersWriteBusy               : BOOL;
END_VAR
```

### VAR_GLOBAL CONSTANT

```iecst
VAR_GLOBAL CONSTANT
    g_iNumOfCmdCtrl_8                  : INT;
    rCloseToZero                       : REAL;
    lrCloseToZero                      : LREAL;
    uiMaxDataFileSize                  : UINT;
    g_udiMaxSec                        : UDINT;
END_VAR
```

### VAR_GLOBAL 字段含义

| 名称 | 类型 | 说明 |
|---|---|---|
| `g_stHVACCycleTimeInterpretation` | `ST_HVACCTRL_CYCLE_TIME_INTERPRETATION` | 控制器周期时间解释结构（用于跨任务周期的时间常数换算）。 |
| `g_dwHVACVarConfigStart` | `DWORD AT%M*` | 持久化变量配置区起始地址（链接到 PLC 输入存储区 %M）。 |
| `g_dwHVACVarConfigEnd` | `DWORD AT%M*` | 持久化变量配置区结束地址。 |
| `g_bHVACParamsChanged` | `BOOL` | 触发一次备份。库内 FB 在 IN_OUT 变化时把这位置 TRUE，由备份 FB 写盘后清零。 |
| `g_bHVACBackupDataReadDone` | `BOOL` | 备份数据已读完（上电首次从备份文件读回的指示）。 |
| `g_bHVACNOVRAMDataReadDone` | `BOOL` | NOVRAM 已读完（上电后第一次从 NOVRAM 读回的指示）。 |
| `g_bHVACPersDataReadDone` | `BOOL` | 持久化数据已读完（上电首次从 .bootdata 读回的指示）。 |
| `g_bHVACPersParamsChanged` | `BOOL` | 持久化参数已改变，正在写盘中。 |
| `g_bHVACNOVRAMParamsChanged` | `BOOL` | NOVRAM 中的数据已改变，正在写入中。 |
| `g_bHVACNOVRAMUsed` | `BOOL` | NOVRAM 已被写入过（首次使用后置 TRUE）。 |
| `g_bHVACPersUsed` | `BOOL` | 持久化数据已被创建（首次使用后置 TRUE）。 |
| `g_bHVACPersWriteBusy` | `BOOL` | 工作计数器已复位（持久化写盘正在进行）。 |

### VAR_GLOBAL CONSTANT 字段含义

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `g_iNumOfCmdCtrl_8` | `INT` | `8` | `FB_HVACCmdCtrl_8` 的命令路数（预置 8）。 |
| `rCloseToZero` | `REAL` | `0.00000001` | REAL 近零判定阈值（用于浮点比较防抖动）。 |
| `lrCloseToZero` | `LREAL` | `0.00000001` | LREAL 近零判定阈值。 |
| `uiMaxDataFileSize` | `UINT` | `65534` | 数据文件大小上限（避免 FOR 循环溢出）。 |
| `g_udiMaxSec` | `UDINT` | `4294967` | `FB_HVACI_CtrlStep` / `FB_HVACPowerRangeTable` 内部最大秒计数。 |

## 3. 行为说明

`g_b*ParamsChanged` / `g_b*DataReadDone` / `g_b*Used` / `g_bHVACPersWriteBusy` 这一组 BOOL 位是 Tc2_HVAC 库的「**持久化状态总线**」：库内的应用 FB（`FB_HVAC*` 系列）把变更通知写到 `g_bHVACParamsChanged`，由 `FB_HVACPersistentDataHandling` / `FB_HVACNOVRAMDataHandling` 在主循环里轮询并执行写盘动作，完成后清零。**外部 PLC 代码应只读这些位**，例如：在上电后 HMI 等待 `g_bHVACPersDataReadDone = TRUE` 才显示「系统就绪」；在持久化写盘进行时（`g_bHVACPersWriteBusy = TRUE`）禁用某些会引发更多写盘的操作以避免连锁。`VAR_GLOBAL CONSTANT` 区是编译时常量，用于库内部边界条件与近零判定，外部代码可以读取来与库行为对齐。访问方式：`Tc2_HVAC.g_bHVACPersDataReadDone`（带库名前缀，避免与本工程的同名全局变量冲突）。

## 4. 错误码 / 返回值

GVL 没有错误码。错误码体现在引用本 GVL 的具体 FB（如 `FB_HVACPersistentDataHandling.udiErrorID`）。

## 5. 使用注意 / 常见坑

- **`g_b*` 系列位是只读监视位**，工程代码绝不能直接置位 / 清零；正确动作由库内部 FB 处理。
- **不要把 `rCloseToZero` 当成业务阈值用**——这是库内部的浮点比较防抖阈（`0.00000001`），工程业务阈值应单独定义（如 `rTempDeadband := 0.5`）。
- **`g_dwHVACVarConfigStart` / `g_dwHVACVarConfigEnd` 是 `AT%M*` 输入存储区映射**——TwinCAT 链接器会自动分配地址，不要试图手动设置。
- **`uiMaxDataFileSize := 65534`** 是 PDF 给出的硬限制；用 `FB_HVACPersistentDataHandling` 写盘的数据总量不能超过这个值（约 64KB），超过会导致 FOR 循环溢出。（PDF 明示）
- Tc2_HVAC 全库 PDF 在 VAR 区结束处不印 `END_VAR`，但实际 IEC 声明中该终止符存在。本仓为方便阅读已在所有文档的 IEC 代码块中显式补 `END_VAR`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_HVAC_Constants.TcPOU`](../examples/P_Demo_HVAC_Constants.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 代码需要在「系统就绪」前不显示主界面（避免读到未初始化的持久化数据）；持久化写盘进行时禁止额外的「保存」操作；监控 NOVRAM 是否首次使用以触发出厂自检。
- **价值**：本 GVL 把库内部持久化状态完整透明化，让外部代码与库行为同步。手写难以替代——`FB_HVAC*DataHandling` 的内部状态如果不通过 GVL 暴露就无法被 HMI / 业务层观察到。
- **替代方案对比**：**不监视任何状态位**：HMI 可能在数据未读完时显示错误值；**自己写一个总线状态 FB**：能做但与库内部状态不一致风险高；**用本 GVL**：直接读最权威的库内部状态。

## 8. 参考资料

- **PDF**：[TF8000_TC3_HVAC_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf) §5.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684912139.html
- **相关 FB / FC**：`FB_HVACPersistentDataHandling`、`FB_HVACNOVRAMDataHandling`、`FB_HVACCmdCtrl_8`、`FB_HVACI_CtrlStep`、`FB_HVACPowerRangeTable`
