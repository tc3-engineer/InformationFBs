# MC_ReadAxisError_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Administrative` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599676299.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_ReadAxisError_BkPlcMc.TcPOU`](../examples/P_Demo_MC_ReadAxisError_BkPlcMc.TcPOU) |

---

## 1. 功能简述

读取液压轴当前**错误码**的 PLCopen 风格功能块。`Enable = TRUE` 时持续把轴的当前错误码（`pStAxRtData^.nErrorCode`）输出到 `AxisErrorID` 字段。本 FB 不需要执行时间且无前置条件，`Error` 和 `Busy` 永远为 `FALSE`（仅为 PLCopen 兼容性保留）。`Enable = FALSE` 时清所有输出。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Enable:     BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Enable` | `BOOL` | — | `TRUE` 触发错误码刷新；`FALSE` 清所有输出 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis:       AXIS_REF_BkPlcMc;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF_BkPlcMc` | 轴接口结构。必须以 `VAR_IN_OUT` 方式传引用 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Busy:       BOOL;
    Valid:      BOOL;
    Error:      BOOL;
    ErrorID:    UDINT;
    AxisErrorID:UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | 命令处理中。本 FB 不需任何时间，`Busy` 永远为 `FALSE`，仅为 PLCopen 兼容性保留 |
| `Valid` | `BOOL` | 当前错误码已成功读出 |
| `Error` | `BOOL` | 本 FB 自身出错指示。本 FB 不需前置条件，`Error` 永远为 `FALSE`，仅为兼容性保留 |
| `ErrorID` | `UDINT` | 本 FB 自身错误码（永远为 0） |
| `AxisErrorID` | `UDINT` | 轴当前错误码。`0` 表示无错；非零值参见 PDF 全局常量 `dwTcHydErrCd*` 系列 |

## 3. 行为说明

**调用模式**：每周期调用，电平触发。`Enable := TRUE` 期间每周期把 `pStAxRtData^.nErrorCode` 复制到 `AxisErrorID`。

**`Error` 与 `AxisErrorID` 的区别**：这是初学者最易混淆的点。
- `Error`：**本 FB 自己**是否出错。本 FB 永远不会自己出错（不需要任何前置条件），所以总是 `FALSE`
- `AxisErrorID`：**轴**当前的错误码。0 = 无错；非 0 = 轴在 ErrorStop 状态，错误号在 `dwTcHydErrCd*` 全局常量里查

**典型用法**：HMI 实时显示轴错误码（与 PLC 内部诊断信息一致）；业务代码判 `AxisErrorID <> 0` 决定是否进入维护模式；与错误码字典查表显示中文报警文本。

**典型陷阱**：
- 把 `Error` 当 "轴是否有错" 用 → `Error` 永远是 0；应用 `AxisErrorID <> 0` 判断
- 错误码不会自动消失：要清错必须调 `MC_Reset_BkPlcMc` 或 `MC_ResetAndStop_BkPlcMc`，轴本身不会主动复位

## 4. 错误码 / 返回值

`AxisErrorID` 是轴的错误码，常见类别（具体值见 PDF §5.2 全局常量）：

| 类别 | 常量前缀 | 含义 |
|---|---|---|
| 编码器错误 | `dwTcHydErrCdEnc*` | 编码器断线 / 信号丢失 / 校验失败 |
| 驱动器错误 | `dwTcHydErrCdDrive*` | 驱动器未 ready / 通讯错 |
| 运动错误 | `dwTcHydErrCdSoftEnd` / `dwTcHydErrCdFollowing*` | 软限位触发 / 跟随误差超限 |
| 指针错误 | `dwTcHydErrCdPtr*` | 设备指针未初始化 |
| 参数错误 | `dwTcHydErrCdParam*` | 参数越界 / 不合法 |

⚠️ 完整码表见 PDF §5.2 或 InfoSys 主题 `1599826187.html`。

## 5. 使用注意 / 常见坑

- **`Error` 永远 FALSE**：要判轴是否有错用 `AxisErrorID <> 0`，不要用 `Error`。
- **`Busy` 永远 FALSE**：判读取完成看 `Valid`。
- **错误码不自动清**：调本 FB 不会复位错误；要清错必须显式 `MC_Reset_BkPlcMc`。
- **可与其它 Read* 并行**：本 FB 只读 `nErrorCode` 一个字段，与其它 Read* FB 互不干扰。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_ReadAxisError_BkPlcMc.TcPOU`](../examples/P_Demo_MC_ReadAxisError_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机液压轴诊断面板：HMI 实时显示轴错误码，业务代码根据错误码类别决定是否允许继续运动；维护模式下显示中文报警文本。
- **价值**：标准 PLCopen 接口；与所有其它 Read* FB 配套使用语法一致；错误码可直接对照库的全局常量表。
- **替代方案对比**：
  - 直接读 `pStAxRtData^.nErrorCode`：性能略好但要自己处理 Enable 边界
  - 用 `MC_ReadStatus_BkPlcMc` 的 `Errorstop` 字段：只知"是否出错"不知"哪个错"
  - **本 FB**：直接拿到错误码数值，可对照码表查含义

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.1.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599676299.html
- **相关 FB**：`MC_ReadStatus_BkPlcMc`（读完整状态机）、`MC_Reset_BkPlcMc`（清错）、`MC_ResetAndStop_BkPlcMc`（清错并停车）
