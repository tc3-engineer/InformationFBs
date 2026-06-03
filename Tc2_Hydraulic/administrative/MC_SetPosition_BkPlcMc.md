# MC_SetPosition_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Administrative` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599684491.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_SetPosition_BkPlcMc.TcPOU`](../examples/P_Demo_MC_SetPosition_BkPlcMc.TcPOU) |

---

## 1. 功能简述

修改液压轴**实际位置**坐标的功能块（非物理动作，而是改变 encoder 偏移）。`Execute` 上升沿触发：依据 `Mode` 把轴的实际位置**置为** `Position`（`Mode = FALSE`）或**叠加** `Position`（`Mode = TRUE`）。本质上修改的是 `pStAxRtData.fEnc_RefShift` 或 `pStAxParams.fEnc_ZeroShift`（具体哪个由编码器类型决定）。常用于"手动归零"或"重新校准坐标系"。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute:    BOOL;
    Position:   LREAL;
    Mode:       BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次位置修改 |
| `Position` | `LREAL` | — | 新的位置值或偏移量，单位 mm |
| `Mode` | `BOOL` | — | 操作模式：`TRUE` = 在当前位置上叠加 `Position`（增量）；`FALSE` = 把实际位置直接设为 `Position`（绝对） |

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
    Done:       BOOL;
    Busy:       BOOL;
    Error:      BOOL;
    ErrorID:    UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 位置修改成功 |
| `Busy` | `BOOL` | 命令处理中 |
| `Error` | `BOOL` | 出错（编码器类型不支持或未知） |
| `ErrorID` | `UDINT` | 错误码 |

## 3. 行为说明

**调用模式**：边沿触发。`Execute` 上升沿启动修改；下降沿清所有输出。

**修改逻辑**：
- 根据 `Axis.pStAxParams^.nEnc_Type`（编码器类型）选择修改 `pStAxRtData.fEnc_RefShift` 或 `pStAxParams.fEnc_ZeroShift`
- 若编码器类型未知或不支持坐标修改 → `Error := TRUE`、`ErrorID := dwTcHydErrCdEncType`
- 修改成功后所有相关字段（包括目标位置、设定位置等）都被同步更新；可对正在运动的轴使用
- 若 `fEnc_ZeroShift` 改变了 → `pStAxRtData^.bParamsUnsave := TRUE`（标记参数需保存）

**`Mode` 语义详解**：
- `Mode = FALSE`（**置位**）：把轴的实际位置直接设成 `Position`。最常用，例如"把当前位置定义为 0"（`Position := 0.0; Mode := FALSE`）
- `Mode = TRUE`（**叠加**）：把当前实际位置 + `Position` 作为新位置。例如"把当前位置往前偏移 10 mm"（`Position := 10.0; Mode := TRUE`）

**⚠️ 软限位风险**：本 FB 可能让"当前位置"或"运动目标"落在激活的软限位之外，FB 自身**不监视**这一情况。修改后务必检查 / 重置软限位。

**典型用法**：
- 设置参考点：到达机械零位后 `Position := 0.0; Mode := FALSE`
- 多工位机械手：在每个工位重新定义坐标系
- 校准偏差：测出实际坐标偏 +0.3 mm → `Position := -0.3; Mode := TRUE`

**典型陷阱**：
- 运动中修改：FB 允许，但目标位置会自动跟着平移，运动可能突然到达"到位"或"过位"
- 编码器类型不支持：增量编码器、绝对编码器各自支持的设置方式不同
- `bParamsUnsave` 标记被忽略：长期改 `fEnc_ZeroShift` 不保存 → 重启后回到旧零点
- 软限位失效：修改坐标后软限位检查的是新坐标系下的边界，原物理位置可能已超新边界

## 4. 错误码 / 返回值

| `Error` | `ErrorID` | 含义 | 处理建议 |
|---|---|---|---|
| `FALSE` | `0` | 成功 | 继续 |
| `TRUE` | `dwTcHydErrCdEncType` | 编码器类型未知或不支持坐标修改 | 检查轴参数 `nEnc_Type` |

⚠️ `dwTcHydErrCdEncType` 具体数值见 PDF §5.2 全局常量。

## 5. 使用注意 / 常见坑

- **本 FB 不改变物理位置**：只修改 PLC 内的"坐标定义"；执行器不会动。要让轴**物理上去到**某位置用 `MC_MoveAbsolute_BkPlcMc`。
- **运动中调用谨慎**：允许，但所有依赖位置的判断（"到位"、"软限位"）瞬间跳变，业务逻辑可能误判。
- **改了 `fEnc_ZeroShift` 要保存**：本 FB 把 `bParamsUnsave := TRUE`，业务侧应调 `MC_AxParamSave_BkPlcMc` 持久化否则重启丢失。
- **Mode 容易混淆**：FALSE = 设置，TRUE = 叠加。HMI 控件可考虑用 enum 显式提示。
- **修改后软限位未自动调整**：业务侧应在修改坐标后重新设置软限位。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_SetPosition_BkPlcMc.TcPOU`](../examples/P_Demo_MC_SetPosition_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机维护后机械结构有微调，导致软零位偏差。技师手动 jog 到模具上的"机械参考点"，按 HMI "设零"按钮触发本 FB（`Position := 0.0; Mode := FALSE`）把当前位置定为新零点。
- **价值**：手写需要：① 判 `nEnc_Type`；② 改 `fEnc_RefShift` 或 `fEnc_ZeroShift`；③ 同步更新 `fActPosition` / `fSetPosition` / `fTargetPosition` 等 5+ 个字段。本 FB 一次调用完成全部更新。
- **替代方案对比**：
  - 直接写 `pStAxRtData^.fEnc_RefShift`：要熟悉编码器类型分支
  - `MC_Home_BkPlcMc`：物理归零（轴去找零信号），慢且需机械参考；本 FB 是"软归零"瞬时完成
  - **本 FB**：软归零标准接口，几个周期内完成

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.1.13
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599684491.html
- **相关 FB**：`MC_Home_BkPlcMc`（物理归零）、`MC_SetReferenceFlag_BkPlcMc`（设参考标志）、`MC_AxParamSave_BkPlcMc`（保存参数避免重启丢失）
