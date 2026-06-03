# FB_PMLUnitModeConfig

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V3` |
| Library Version | `1.0.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Packaging Machine State` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003718411.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PMLUnitModeConfig.TcPOU`](../examples/P_Demo_FB_PMLUnitModeConfig.TcPOU) |

---

## 1. 功能简述

`FB_PMLUnitModeConfig` 用于**注册自定义 UnitMode**到 PackML 状态机。PackML 标准只预定义 3 种 UnitMode（Production=1 / Maintenance=2 / Manual=3）。当机器需要额外的工艺模式（如 "Cleaning 清洗" / "Calibration 标定" / "Loading 上料" 等编号 4-31 的模式）时，用本 FB 配置：(1) 该模式启用/禁用哪些 PML 状态；(2) 该模式与其他模式之间在哪些状态可以切换；(3) **V3 新增**：该模式下每个状态的 HMI 颜色 / 闪烁 / 文本色配置（自 V1.0.5.0 起）。

**V3 与 V2 的关键差异**：
- **FB 命名**：V2 叫 `PML_UnitModeConfig`，V3 改名 `FB_PMLUnitModeConfig`。
- **新增 3 个 ARRAY 输入**（自 V1.0.5.0 库版本起）：`aStateFlashing` / `aStateColor` / `aStateTextColor`——把状态可视化属性（HMI 闪烁、背景色、文本色）也封到配置里，HMI 不必另写颜色映射代码。

每个自定义模式实例化一个 `FB_PMLUnitModeConfig` 实例并赋好所有 `bDisableXxx` / `bEnableUnitModeChangeXxx` / `aStateXxx` 输入；状态机和 `FB_PMLUnitModeManager` 读取这些配置后用相同的逻辑驱动新模式。

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
    aStateFlashing                  : ARRAY [E_PMLState.Undefined..E_PMLState.Completed] OF BOOL := aStateFlashingDefault;
    aStateColor                     : ARRAY [E_PMLState.Undefined..E_PMLState.Completed] OF STRING[6] := aStateColorDefault;
    aStateTextColor                 : ARRAY [E_PMLState.Undefined..E_PMLState.Completed] OF STRING[6] := aStateTextColorDefault;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `eMode` | `DINT` | - | 新 PML UnitMode 编号，合法范围 4..31（1-3 是预留基础模式，0 是 Invalid）|
| `sName` | `STRING` | - | 新 UnitMode 的名称（如 'Cleaning' / 'Calibration'），用于 HMI 显示与 `F_PMLUnitModeToString` 反查 |
| `bDisableClearing` | `BOOL` | - | 禁用 `Clearing` PML 状态 |
| `bDisableStarting` | `BOOL` | - | 禁用 `Starting` PML 状态 |
| `bDisableSuspended` | `BOOL` | - | 禁用 `Suspended` PML 状态。禁用本稳态同时也禁用 `Suspending` 和 `Unsuspending` |
| `bDisableStopping` | `BOOL` | - | 禁用 `Stopping` PML 状态 |
| `bDisableAborting` | `BOOL` | - | 禁用 `Aborting` PML 状态 |
| `bDisableHolding` | `BOOL` | - | 禁用 `Holding` PML 状态 |
| `bDisableHeld` | `BOOL` | - | 禁用 `Held` PML 状态。禁用本稳态同时也禁用 `Holding` 和 `Unholding` |
| `bDisableUnholding` | `BOOL` | - | 禁用 `Unholding` PML 状态 |
| `bDisableSuspending` | `BOOL` | - | 禁用 `Suspending` PML 状态 |
| `bDisableUnsuspending` | `BOOL` | - | 禁用 `Unsuspending` PML 状态 |
| `bDisableResetting` | `BOOL` | - | 禁用 `Resetting` PML 状态 |
| `bDisableIdle` | `BOOL` | - | 禁用 `Idle` PML 状态。禁用本稳态同时也禁用 `Resetting` |
| `bDisableCompleting` | `BOOL` | - | 禁用 `Completing` PML 状态 |
| `bDisableComplete` | `BOOL` | - | 禁用 `Complete` PML 状态。禁用本稳态同时也禁用 `Completing` |
| `bEnableUnitModeChangeStopped` | `BOOL` | - | 允许在 `Stopped` 稳态切换 UnitMode |
| `bEnableUnitModeChangeIdle` | `BOOL` | - | 允许在 `Idle` 稳态切换 UnitMode |
| `bEnableUnitModeChangeSuspended` | `BOOL` | - | 允许在 `Suspended` 稳态切换 UnitMode |
| `bEnableUnitModeChangeExecute` | `BOOL` | - | 允许在 `Execute` 稳态切换 UnitMode |
| `bEnableUnitModeChangeAborted` | `BOOL` | - | 允许在 `Aborted` 稳态切换 UnitMode |
| `bEnableUnitModeChangeHeld` | `BOOL` | - | 允许在 `Held` 稳态切换 UnitMode |
| `bEnableUnitModeChangeComplete` | `BOOL` | - | 允许在 `Complete` 稳态切换 UnitMode |
| `aStateFlashing` | `ARRAY [E_PMLState.Undefined..E_PMLState.Completed] OF BOOL` | `aStateFlashingDefault` | （V1.0.5.0 新增）该模式下每个状态的 HMI 闪烁开关 |
| `aStateColor` | `ARRAY [E_PMLState.Undefined..E_PMLState.Completed] OF STRING[6]` | `aStateColorDefault` | （V1.0.5.0 新增）该模式下每个状态的 HMI 背景色（如 'RED' / 'GREEN' / 'YELLOW'）|
| `aStateTextColor` | `ARRAY [E_PMLState.Undefined..E_PMLState.Completed] OF STRING[6]` | `aStateTextColorDefault` | （V1.0.5.0 新增）该模式下每个状态的 HMI 文本色 |

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

> **PDF 文档命名小瑕疵**：PDF 输出表格里写的 `nErrorId`、变量声明里写的 `nErrorID`（大小写不一致）——以 VAR_OUTPUT 声明 `nErrorID` 为准。

### VAR_IN_OUT

无。

## 3. 行为说明

`FB_PMLUnitModeConfig` 是 PackML 状态机的**模式定义寄存器**——每个自定义模式（编号 4-31）实例化一个本 FB，配置好后由状态机和 `FB_PMLUnitModeManager` 读取。配置最终存到全局 `stPMLUnitModeConfiguration : ARRAY[0..cMaxUnitMode] OF ST_PMLUnitModeConfiguration`。

**子状态禁用规则**：每个 `bDisableXxx` 输入对应一个 PML 状态。例如设 `bDisableHolding := TRUE` 表示本模式下不存在 Holding 过渡。值得注意的是**禁用稳态会级联禁用相关过渡态**：禁用 `Suspended` 也禁用 `Suspending` 与 `Unsuspending`；禁用 `Held` 也禁用 `Holding` 与 `Unholding`；禁用 `Idle` 也禁用 `Resetting`；禁用 `Complete` 也禁用 `Completing`。

**模式切换允许规则**：`bEnableUnitModeChangeXxx` 控制在哪些稳态可以切换 UnitMode。例如设 `bEnableUnitModeChangeIdle := TRUE` 表示本模式可以在 Idle 稳态被切到/切走。`Stopped` 稳态对所有基础模式默认可切（PDF 中 Production/Maintenance/Manual 三态图均显示 Stopped 是公共切换点）。

**V1.0.5.0 新增视觉属性**：`aStateFlashing` / `aStateColor` / `aStateTextColor` 三个数组下标按 `E_PMLState` 枚举值（0..17），值为各状态在 HMI 上的呈现属性。默认值 `aStateFlashingDefault` / `aStateColorDefault` / `aStateTextColorDefault` 由库提供——如果只想用默认配色不用传这 3 个数组（IEC ST 会自动用默认值）。HMI 程序可以直接读取 `stPMLUnitModeConfiguration[eMode].aStateColor[StateCurrent]` 拿到当前色值，免去自己写颜色映射表。

**典型配置示例**：定义 "Cleaning"（清洗）模式 = 编号 4、名称 'Cleaning'、禁用 Holding/Held/Unholding（清洗时不允许暂停保持）、允许在 Stopped/Idle 切换模式、颜色配置成 Execute 蓝色等。这样状态机在 Cleaning 模式下不会触发 Hold 路径；切换到/从 Cleaning 必须在 Stopped 或 Idle；HMI 颜色随状态自动变化。

**注册时机**：建议在 PLC 上电的 `FB_init` 或第一次扫描内调用一次本 FB（一次性注册），之后状态机就能识别该模式。重复注册同一 eMode 会出错。

## 4. 错误码 / 返回值

PDF 标注 `nErrorID` 在 `bError = TRUE` 时给出错误号。PDF 未列具体码值。

常见出错场景：

| 出错场景 | 含义 | 处理建议 |
|---|---|---|
| `eMode` 越界 | 不在 4..31 | 检查初始化代码 |
| 重复注册同一 `eMode` | 已注册过 | 用 latch 跳过重复调用 |
| 配置冲突 | 例如禁用 Idle 同时启用 Idle 模式切换 | 检查 bDisable/bEnable 输入组合是否矛盾 |

⚠️ 待人工确认：具体 `nErrorID` 数值映射 PDF 未列。

## 5. 使用注意 / 常见坑

- `eMode` 合法范围 4..31（基础模式 1-3 不能重复定义，0 是 Invalid，32+ 越界）。
- `sName` 字符串建议简短（默认 `STRING` 即 80 字符）并与 HMI 显示一致。
- 禁用某个稳态会级联禁用相关过渡态——读规则后再设输入，避免做无效配置。
- 注册一次性完成、用 latch 包裹，避免周期调用造成内部状态机抖动。（工程经验补充）
- 自定义模式与 `FB_PMLUnitModeManager` 必须配合使用——只配 Config 而不在 Manager 里允许切换，HMI 切模式会被拒。（工程经验补充）
- V1.0.5.0+ 的颜色/闪烁数组：如果只想用默认值不传，IEC ST 函数调用时省略该参数即可，IEC 自动用 `:=` 默认。
- 与 V2 (`PML_UnitModeConfig`) 不同：V3 加了 3 个 ARRAY 输入；不传的话 IEC 仍能自动填默认值，向后兼容。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PMLUnitModeConfig.TcPOU`](../examples/P_Demo_FB_PMLUnitModeConfig.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：制药行业的灌装机要求增加 "Cleaning"（CIP 清洗）和 "Calibration"（标定）两种模式。清洗模式不允许暂停保持（必须连续清洗完整周期），标定模式只能在 Idle 切换以避免标定过程中混入生产任务。两个模式分别用本 FB 注册到状态机。V3 新增的颜色配置让 HMI 在 Cleaning 模式显示蓝色背景，Calibration 显示紫色，操作员一眼分辨。
- **价值**：标准 PackML 只给 3 种模式，本 FB 把这个上限扩展到 31 种，且每种模式都享受标准状态机的转移规则保护，不必另写 case 分支。V3 把 HMI 视觉配置也封装进来，省去自己写状态色映射代码。
- **替代方案对比**：自己写多套独立的状态机（每种模式一套）——代码重复、维护困难、不同模式间切换没有标准保护。本 FB 让所有模式共享同一个 `FB_PMLStateMachine` 实例，工艺差异通过配置而非代码体现。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003718411.html
- **相关**：`FB_PMLStateMachine`（消费本配置的中央状态机）、`FB_PMLUnitModeManager`（实际切换模式）、`E_PMLProtectedUnitMode`（受保护的基础模式枚举）、`F_PMLUnitModeToString`（按 eMode 反查模式名）、`ST_PMLUnitModeConfiguration`（最终存储配置的结构体）、`E_PMLState`（aStateXxx 数组下标用枚举）

## 9. 待确认项 (⚠️)

- `nErrorID` 数值与含义映射：PDF 未列。
- PDF 输出表头 `nErrorId` 与 `VAR_OUTPUT` 声明 `nErrorID` 大小写不一致；以 VAR_OUTPUT 声明为准。
