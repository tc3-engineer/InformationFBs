# PML_UnitModeConfig

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Packaging Machine State` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/1336141323.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_PML_UnitModeConfig.TcPOU`](../examples/P_Demo_PML_UnitModeConfig.TcPOU) |

---

## 1. 功能简述

`PML_UnitModeConfig` 用于**注册自定义 UnitMode**到 PackML 状态机。PackML 标准只预定义 3 种 UnitMode（Production=1 / Maintenance=2 / Manual=3）。当机器需要额外的工艺模式（如 "Cleaning 清洗" / "Calibration 标定" / "Loading 上料" 等编号 4-31 的模式）时，用本 FB 配置：(1) 该模式启用/禁用哪些 PML 状态；(2) 该模式与其他模式之间在哪些状态可以切换。

每个自定义模式实例化一个 `PML_UnitModeConfig` 实例并赋好所有 `bDisableXxx` / `bEnableUnitModeChangeXxx` 输入；状态机和 `PML_UnitModeManager` 读取这些配置后用相同的逻辑驱动新模式。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    eMode                           : DINT;
    sName                           : STRING;
    bDisableClearing                : BOOL;
    bDisableStarting                : BOOL;
    bDisableSuspended               : BOOL;
    bDisableStopping                : BOOL;
    bDisableAborting                : BOOL;
    bDisableHolding                 : BOOL;
    bDisableHeld                    : BOOL;
    bDisableUnholding               : BOOL;
    bDisableSuspending              : BOOL;
    bDisableUnsuspending            : BOOL;
    bDisableResetting               : BOOL;
    bDisableIdle                    : BOOL;
    bDisableCompleting              : BOOL;
    bDisableComplete                : BOOL;
    bEnableUnitModeChangeStopped    : BOOL;
    bEnableUnitModeChangeIdle       : BOOL;
    bEnableUnitModeChangeSuspended  : BOOL;
    bEnableUnitModeChangeExecute    : BOOL;
    bEnableUnitModeChangeAborted    : BOOL;
    bEnableUnitModeChangeHeld       : BOOL;
    bEnableUnitModeChangeComplete   : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `eMode` | `DINT` | 新 PML UnitMode 编号，合法范围 4..31（1-3 是预留基础模式，0 是 Invalid）|
| `sName` | `STRING` | 新 UnitMode 的名称（如 'Cleaning' / 'Calibration'），用于 HMI 显示与 `F_UnitModeToString` 反查 |
| `bDisableClearing` | `BOOL` | 禁用 `Clearing` PML 状态 |
| `bDisableStarting` | `BOOL` | 禁用 `Starting` PML 状态 |
| `bDisableSuspended` | `BOOL` | 禁用 `Suspended` PML 状态。禁用本稳态同时也禁用 `Suspending` 和 `Unsuspending` |
| `bDisableStopping` | `BOOL` | 禁用 `Stopping` PML 状态 |
| `bDisableAborting` | `BOOL` | 禁用 `Aborting` PML 状态 |
| `bDisableHolding` | `BOOL` | 禁用 `Holding` PML 状态 |
| `bDisableHeld` | `BOOL` | 禁用 `Held` PML 状态。禁用本稳态同时也禁用 `Holding` 和 `Unholding` |
| `bDisableUnholding` | `BOOL` | 禁用 `Unholding` PML 状态 |
| `bDisableSuspending` | `BOOL` | 禁用 `Suspending` PML 状态 |
| `bDisableUnsuspending` | `BOOL` | 禁用 `Unsuspending` PML 状态 |
| `bDisableResetting` | `BOOL` | 禁用 `Resetting` PML 状态 |
| `bDisableIdle` | `BOOL` | 禁用 `Idle` PML 状态。禁用本稳态同时也禁用 `Resetting` |
| `bDisableCompleting` | `BOOL` | 禁用 `Completing` PML 状态 |
| `bDisableComplete` | `BOOL` | 禁用 `Complete` PML 状态。禁用本稳态同时也禁用 `Completing` |
| `bEnableUnitModeChangeStopped` | `BOOL` | 允许在 `Stopped` 稳态切换 UnitMode |
| `bEnableUnitModeChangeIdle` | `BOOL` | 允许在 `Idle` 稳态切换 UnitMode |
| `bEnableUnitModeChangeSuspended` | `BOOL` | 允许在 `Suspended` 稳态切换 UnitMode |
| `bEnableUnitModeChangeExecute` | `BOOL` | 允许在 `Execute` 稳态切换 UnitMode |
| `bEnableUnitModeChangeAborted` | `BOOL` | 允许在 `Aborted` 稳态切换 UnitMode |
| `bEnableUnitModeChangeHeld` | `BOOL` | 允许在 `Held` 稳态切换 UnitMode |
| `bEnableUnitModeChangeComplete` | `BOOL` | 允许在 `Complete` 稳态切换 UnitMode |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError     : BOOL;
    nErrorID   : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | 注册失败时置 TRUE（如 eMode 越界、重复注册等）|
| `nErrorID` | `UDINT` | `bError = TRUE` 时给出错误号 |

> **PDF 文档命名小瑕疵**：PDF 输出表格里写的 `nErrorId`、变量声明里写的 `nErrorID`（大小写不一致）。verify_doc 以 `nErrorID` 为准。

### VAR_IN_OUT

无。

## 3. 行为说明

`PML_UnitModeConfig` 是 PackML 状态机的**模式定义寄存器**——每个自定义模式（编号 4-31）实例化一个本 FB，配置好后由状态机和 `PML_UnitModeManager` 读取。

**子状态禁用规则**：每个 `bDisableXxx` 输入对应一个 PML 状态。例如设 `bDisableHolding := TRUE` 表示本模式下不存在 Holding 过渡。值得注意的是**禁用稳态会级联禁用相关过渡态**：禁用 `Suspended` 也禁用 `Suspending` 与 `Unsuspending`；禁用 `Held` 也禁用 `Holding` 与 `Unholding`；禁用 `Idle` 也禁用 `Resetting`；禁用 `Complete` 也禁用 `Completing`。

**模式切换允许规则**：`bEnableUnitModeChangeXxx` 控制在哪些稳态可以切换 UnitMode。例如设 `bEnableUnitModeChangeIdle := TRUE` 表示本模式可以在 Idle 稳态被切到/切走。`Stopped` 稳态对所有基础模式默认可切（PDF 中 Production/Maintenance/Manual 三态图均显示 Stopped 是公共切换点）。

**典型配置示例**：定义 "Cleaning"（清洗）模式 = 编号 4、名称 'Cleaning'、禁用 Holding/Held/Unholding（清洗时不允许暂停保持）、允许在 Stopped/Idle 切换模式。这样状态机在 Cleaning 模式下不会触发 Hold 路径；切换到/从 Cleaning 必须在 Stopped 或 Idle。

**注册时机**：建议在 PLC 上电的 `FB_init` 或第一次扫描内调用一次本 FB（一次性注册），之后状态机就能识别该模式。重复注册同一 eMode 会出错。

## 4. 错误码 / 返回值

PDF 标注 `nErrorID` 在 `bError = TRUE` 时给出错误号。PDF + InfoSys 均未列具体码值。

常见出错场景：

| 出错场景 | 含义 | 处理建议 |
|---|---|---|
| `eMode` 越界 | 不在 4..31 | 检查初始化代码 |
| 重复注册同一 `eMode` | 已注册过 | 用 latch 跳过重复调用 |
| 配置冲突 | 例如禁用 Idle 同时启用 Idle 模式切换 | 检查 bDisable/bEnable 输入组合是否矛盾 |

⚠️ 待人工确认：具体 `nErrorID` 数值映射 PDF + InfoSys 均未列。

## 5. 使用注意 / 常见坑

- `eMode` 合法范围 4..31（基础模式 1-3 不能重复定义，0 是 Invalid，32+ 越界）。
- `sName` 字符串建议简短（默认 `STRING` 即 80 字符）并与 HMI 显示一致。
- 禁用某个稳态会级联禁用相关过渡态——读规则后再设输入，避免做无效配置。
- 注册一次性完成、用 latch 包裹，避免周期调用造成内部状态机抖动。（工程经验补充）
- 自定义模式与 `PML_UnitModeManager` 必须配合使用——只配 Config 而不在 Manager 里允许切换，HMI 切模式会被拒。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_PML_UnitModeConfig.TcPOU`](../examples/P_Demo_PML_UnitModeConfig.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：制药行业的灌装机要求增加 "Cleaning"（CIP 清洗）和 "Calibration"（标定）两种模式。清洗模式不允许暂停保持（必须连续清洗完整周期），标定模式只能在 Idle 切换以避免标定过程中混入生产任务。两个模式分别用本 FB 注册到状态机。
- **价值**：标准 PackML 只给 3 种模式，本 FB 把这个上限扩展到 31 种，且每种模式都享受标准状态机的转移规则保护，不必另写 case 分支。HMI 上多一个模式选择下拉框就能切换工艺。
- **替代方案对比**：自己写多套独立的状态机（每种模式一套）——代码重复、维护困难、不同模式间切换没有标准保护。本 FB 让所有模式共享同一个 `PML_StateMachine` 实例，工艺差异通过配置而非代码体现。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/1336141323.html
- **相关**：`PML_StateMachine`（消费本配置的中央状态机）、`PML_UnitModeManager`（实际切换模式）、`E_PMLProtectedUnitMode`（受保护的基础模式枚举）、`F_UnitModeToString`（按 eMode 反查模式名）

## 9. 待确认项 (⚠️)

- `nErrorID` 数值与含义映射：PDF + InfoSys 均未列。
- PDF 输出表头 `nErrorId` 与 `VAR_OUTPUT` 声明 `nErrorID` 大小写不一致；以 VAR_OUTPUT 声明为准。
