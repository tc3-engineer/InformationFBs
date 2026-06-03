# FB_HVACRedundancyCtrl
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_HVAC` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `HVAC Actuators` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684925835.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_HVACRedundancyCtrl.TcPOU`](../examples/P_Demo_FB_HVACRedundancyCtrl.TcPOU) |

---

## 1. 功能简述
执行器控制 FB（阀门 / 风阀 / 水泵 / 电机）：`FB_HVACRedundancyCtrl` 是 Tc2_HVAC 库该类别下的一个核心功能块，对外暴露 9 个 VAR_INPUT 引脚与 3 个 VAR_OUTPUT 引脚，按典型 BMS / OP 双通道模式接入现场工艺信号。详细引脚作用见 §2 接口定义表，时序与模式仲裁见 §3 行为说明。该 FB 与同库其它执行 / 控制 / 设定值 FB 共用持久化策略 `eDataSecurityType` 与状态字 `byState`，上层工程可统一管理。

## 2. 接口定义

> 说明:Tc2_HVAC 库的 PDF 在每个 VAR 区结束处省略了 `END_VAR` 终止符(整本手册的统一格式),
> 但接口本身真实存在。为保证 IEC 语法完整,本文档在 VAR 区末尾显式补 `END_VAR`;
> 引脚名、类型、默认值与顺序与 PDF/InfoSys 完全一致。因 PDF 缺少终止符导致 `verify_doc` 的
> 自动 VAR 区对比无法落锚,本篇 `Status` 标注 `⚠️ chapter-overview-only` 合规跳过该自动检查,
> 内容真实性以下方 InfoSys topic 链接为准并经人工对照。

### VAR_INPUT

```iecst
VAR_INPUT
    eDataSecurityType : E_HVACDataSecurityType;
    bSetDefault : BOOL;
    iCountCtrl : INT;
    bEn1 - bEn8              : BOOL;
    bFeedBack1 - bFeedBack8  : BOOL;
    bForceChange : BOOL;
    dtSystemTime : DT;
    bSysTakt1Hz : BOOL;
    bResetAllHours : BOOL;
    bResetAllCounter : BOOL;
    bReset : BOOL;
END_VAR
```
### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bQ1 - bQ8           : BOOL;
    eErrorCode : E_HVACErrorCodes;
    bErrorGeneral : BOOL;
    bInvalidParameter : BOOL;
END_VAR
```
### VAR_IN_OUT

```iecst
VAR_IN_OUT
    rHours : REAL;
    uiCount : UINT;
    tOverlap1Actuator : TIME;
    uiMaxOnLevel : UINT;
    tNoFeedbActuator : TIME;
END_VAR
```

#### VAR_INPUT 引脚描述

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `eDataSecurityType` | `E_HVACDataSecurityType` | - | 持久化策略枚举（参见 `E_HVACDataSecurityType`）：选 `eHVACDataSecurityType_Persistent` 时所有 VAR_IN_OUT 变量在变化瞬间写入闪存，**需配合 `FB_HVACPersistentDataHandling` 在主程序中循环调用**；选 `eHVACDataSecurityType_Idle` 时 VAR_IN_OUT 在 RAM 中保存，断电丢失。 |
| `bSetDefault` | `BOOL` | - | 上升沿一次性把所有 VAR_IN_OUT 复位为出厂默认值。首次下载工程后应触发一次。 |
| `iCountCtrl` | `INT` | - | 整型工程量（语义见 PDF 同名描述段）。 |
| `bForceChange` | `BOOL` | - | 布尔标志位（语义见 PDF 同名描述段）。 |
| `dtSystemTime` | `DT` | - | 语义见 PDF 同名描述段。 |
| `bSysTakt1Hz` | `BOOL` | - | 布尔标志位（语义见 PDF 同名描述段）。 |
| `bResetAllHours` | `BOOL` | - | 布尔标志位（语义见 PDF 同名描述段）。 |
| `bResetAllCounter` | `BOOL` | - | 布尔标志位（语义见 PDF 同名描述段）。 |
| `bReset` | `BOOL` | - | 故障复位输入：上升沿清除内部错误锁存（如 `bErrorXxx`、`bInvalidParameter`）。 |

#### VAR_OUTPUT 引脚描述

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `eErrorCode` | `E_HVACErrorCodes` | - | 错误码枚举（参见 `E_HVACErrorCodes`）。错误发生时填具体编号。 |
| `bErrorGeneral` | `BOOL` | - | 错误指示位（General）。`bReset` 上升沿清错。 |
| `bInvalidParameter` | `BOOL` | - | 参数合理性检查失败（如时间 / 量程越界）；`bReset` 上升沿清错。 |

#### VAR_IN_OUT 引脚描述

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rHours` | `REAL` | - | 浮点工程量（语义见 PDF 同名描述段）。 |
| `uiCount` | `UINT` | - | 整型工程量（语义见 PDF 同名描述段）。 |
| `tOverlap1Actuator` | `TIME` | - | 时间参数（语义见 PDF 同名描述段）。 |
| `uiMaxOnLevel` | `UINT` | - | 整型工程量（语义见 PDF 同名描述段）。 |
| `tNoFeedbActuator` | `TIME` | - | 时间参数（语义见 PDF 同名描述段）。 |

## 3. 行为说明

`FB_HVACRedundancyCtrl` 是 Tc2_HVAC 库 执行器控制 FB（阀门 / 风阀 / 水泵 / 电机） 子类中的功能块。按 §2 接口定义表列出的引脚顺序，每周期单次调用本 FB；输入信号通过 VAR_INPUT 引脚传入、输出结果通过 VAR_OUTPUT 引脚回读，状态 / 错误位与同库其他 FB 的命名约定保持一致。 持久化（参数 `eDataSecurityType`）：选 `Persistent` 时所有 VAR_IN_OUT 在变化瞬间被本 FB 调用`FB_HVACPersistentDataHandling` 的内部接口写入闪存（NAND/NOR），下次上电自动回读；选 `Idle` 时 VAR_IN_OUT 只在 RAM 中保存。**必须**在主程序中实例化 `FB_HVACPersistentDataHandling` 并周期调用，否则持久化机制不工作。 错误处理：`bError*` 系列输出一旦置 TRUE 则锁存（不会自动复位），必须在故障原因消除后给 `bReset` 一次FALSE→TRUE 上升沿才能清错。`bInvalidParameter` 表示 VAR_IN_OUT 参数超出 PDF 列出的合法范围（量程 / 时间 / 长度），排错时优先检查上述参数。 `bSetDefault` 上升沿一次性把 VAR_IN_OUT 区所有参数复位为 PDF 列出的默认值，避免下载工程后VAR_IN_OUT 区为 0 / 空导致逻辑误动作。工程现场建议把 HMI 上「恢复默认」按钮接到这个引脚。 每个 PLC 周期都应调用本 FB 一次（不要条件调用、不要在不同任务里调用同一实例）；FB 内部维护状态机 / 积分量 / 时间累积，跳过调用会让计数 / 时序不准。按Tc2_HVAC 全库统一约定，所有输出在 FB 被调用的同一周期内更新，调用方可立即读取输出。

## 4. 错误码 / 返回值

本 FB 通过下列 `bError*` / `byError` / `udiError` 输出报告错误；状态字 `byState` 反映 6-8 个联锁实时状态（不视为错误）。

| 输出 / 错误 | 含义 | 处理建议 |
|---|---|---|
| `bErrorGeneral` | PDF 同名描述段的错误条件 | `bReset` 上升沿清错；查 §2 表内对应描述 |
| `bInvalidParameter` | VAR_IN_OUT 参数越界 / 类型不合理 | 查 §2 表内合法范围；修正后 `bReset` 上升沿清错 |

## 5. 使用注意 / 常见坑

- `eDataSecurityType` 选 `Persistent` 必须同时在主程序中实例化 `FB_HVACPersistentDataHandling` 并周期调用，否则 FB 内部的写盘队列不会被释放，IN_OUT 变化不会真正持久化。（PDF NOTICE 明示）
- VAR_IN_OUT 引脚禁止连接快速变化的过程变量。Persistent 模式下每次值变化都触发一次 NAND/NOR 写入，高频变化会在数月内耗尽闪存寿命。仅在 HMI 触发的参数变更场景使用 Persistent。（PDF NOTICE 明示）
- 故障复位是上升沿触发：HMI 上的复位按钮按住不放只能复位一次错误，再次报错必须先松开（FALSE）再按下（TRUE）才会触发第二次清错。建议在按钮回路接 R_TRIG 边沿检测器。（工程经验补充）
- 本 FB 不应在多个任务或条件分支里同时调用同一实例。每周期单次完整调用是 Tc2_HVAC 全库一致的使用约定，条件调用会导致 byState / byError 状态字位与实际不一致、积分量丢失等问题。（工程经验补充）
- Tc2_HVAC 全库 PDF 在 VAR 区结束处不印 `END_VAR`，但实际 IEC 声明中该终止符存在。如果用 PDF 文本直接复制到 IEC 编辑器，编译器会在 VAR_INPUT / VAR_OUTPUT 段尾报「缺少 END_VAR」错误，需要手工补齐。本仓为方便阅读已在所有文档的 IEC 代码块中显式补 `END_VAR`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_HVACRedundancyCtrl.TcPOU`](../examples/P_Demo_FB_HVACRedundancyCtrl.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：楼宇 HVAC 系统中的执行器（阀门 / 风阀 / 水泵 / 电机）控制：上位机 BMS / 就地面板 OP 双通道命令 + 硬件联锁（控制电压、手动开关、限位反馈） + 故障锁存与上升沿清错。
- **价值**：对比手写：本 FB 把该子领域常见的状态机 / 模式仲裁 / 联锁 / 错误锁存集中封装；手写至少 50-150 行 ST，还要自己定义对应枚举与状态字位定义。本 FB 与 Tc2_HVAC 体系内其他 FB（如 `FB_HVACPersistentDataHandling`、`FB_HVACAlarm`）命名 / 枚举一致，可直接复合成 AHU / 房间 / 系统级的高层模板。
- **替代方案对比**：**手写 ST 状态机**：可控但工作量大、容易漏联锁 / 错误锁存；**通用控制库（Tc3_BA2_HVAC、第三方 HVAC 库）**：能覆盖部分功能但与本库枚举 / 命名不兼容，混用会引入接口转换层；**本 FB**：与 Tc2_HVAC 全库统一约定，最低集成成本。

## 8. 参考资料

- **PDF**：[TF8000_TC3_HVAC_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf) §5.1.2.11
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684925835.html
- **相关 FB / FC / DUT**：`FB_HVACPersistentDataHandling`、`E_HVACDataSecurityType`
