# MC_SetReferenceFlag_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Administrative` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599685515.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_SetReferenceFlag_BkPlcMc.TcPOU`](../examples/P_Demo_MC_SetReferenceFlag_BkPlcMc.TcPOU) |

---

## 1. 功能简述

设置液压轴**参考标志**（referenced / not referenced）的非 PLCopen 扩展功能块。`Execute` 上升沿把 `pStAxRtData.nStateDWord` 的 `dwTcHydNsDwReferenced` bit 按 `ReferenceFlag` 输入设位或清位。本 FB 由 Beckhoff 在 PLCopen 标准外扩展，用于"使用绝对编码器的轴免归零开机即认为已参考"或"维护期间手动标记已参考"等场景。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute:        BOOL;
    ReferenceFlag:  BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次参考标志写入 |
| `ReferenceFlag` | `BOOL` | — | 参考标志的新值：`TRUE` = 已参考；`FALSE` = 未参考 |

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
| `Done` | `BOOL` | 写入成功 |
| `Busy` | `BOOL` | 命令处理中 |
| `Error` | `BOOL` | 出错指示 |
| `ErrorID` | `UDINT` | 错误码 |

## 3. 行为说明

本功能块是**边沿触发**型，需要在 `Execute` 上有上升沿才会启动一次参考标志写入；写入完成后置 `Done := TRUE`；`Execute` 下降沿清所有输出回到空闲。本质操作非常简单：根据 `ReferenceFlag` 输入设位或清位 `pStAxRtData.nStateDWord` 中的 `dwTcHydNsDwReferenced` bit。

该 bit 的语义直接影响上层运动控制是否允许执行：上层运动 FB（如 `MC_MoveAbsolute_BkPlcMc`）通常要求"轴已参考"才允许执行绝对定位命令，未参考则直接报错拒绝执行。

**典型用法**包括三种：
- **绝对编码器免归零**：开机后立即 `ReferenceFlag := TRUE; Execute := TRUE`，认为绝对编码器读到的位置就是真实坐标，无需再 `MC_Home_BkPlcMc` 物理归零
- **维护标记**：技师手动调整后人工确认坐标系正确，按 HMI 按钮触发本 FB 标记"已参考"
- **强制重新归零**：`ReferenceFlag := FALSE; Execute := TRUE` 清掉参考标志，下一次绝对运动命令会被拒绝，强制业务流程走归零

**与 `MC_Home_BkPlcMc` 的本质区别**：`MC_Home_BkPlcMc` 是物理动作归零（轴去找零点信号 / 限位 / 编码器零脉冲），而 `MC_SetReferenceFlag_BkPlcMc` 只改标志位，不让轴动。两者在使用绝对编码器场景下可以互相替代。

**典型陷阱**：误标"已参考"但实际位置错误时，后续绝对定位按错误坐标系执行可能撞模具；另外本 FB 是非 PLCopen 扩展，从 PLCopen 标准平台移植代码时找不到对应函数需要做兼容封装。

## 4. 错误码 / 返回值

PDF 与 InfoSys 在本 FB 章节都未列具体 `ErrorID` 数值；行为说明里仅描述置位/清位逻辑。⚠️ 待人工确认具体错误码。

## 5. 使用注意 / 常见坑

- **不是 PLCopen 标准 FB**：PDF 头部明确标注 "(Function is not defined by PLCopen)"；写跨平台代码时要做兼容封装。
- **本 FB 不验证坐标系正确性**：仅修改 bit；操作员必须自己保证当前位置真的是机械参考点。
- **绝对编码器场景常用**：上电后调一次置 TRUE 跳过 `MC_Home_BkPlcMc`。
- **HMI 触发要做边沿处理**：本 FB 边沿触发，长按 HMI 按钮等同一次触发；可用 `R_TRIG` 边沿检测器避免反复触发期间输出跳变误导 HMI。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_SetReferenceFlag_BkPlcMc.TcPOU`](../examples/P_Demo_MC_SetReferenceFlag_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：液压锁模轴使用绝对编码器（如 SSI / EnDat），开机后位置读数本来就是绝对值，无需物理归零。但 PLC 内部默认 "未参考" 状态，任何 `MC_MoveAbsolute_BkPlcMc` 会被拒绝。开机后调本 FB（`ReferenceFlag := TRUE`）一次跳过归零流程，让业务代码直接发绝对定位命令。
- **价值**：手写需要找 `dwTcHydNsDwReferenced` mask 位置并直接操作 `nStateDWord` 的 bit；本 FB 封装了 bit 操作，避免代码里出现"魔数 mask"。
- **替代方案对比**：
  - 物理跑 `MC_Home_BkPlcMc`：增加开机时间，且绝对编码器不需要
  - 直接 OR mask 改 `nStateDWord`：能用但语义不明
  - **本 FB**：标准接口，意图清晰

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.1.14
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599685515.html
- **相关 FB**：`MC_Home_BkPlcMc`（物理归零）、`MC_SetPosition_BkPlcMc`（设位置）、`MC_ReadStatus_BkPlcMc`（读 `Errorstop` 等其它状态位）

## 9. 待确认项 (⚠️)

- PDF + InfoSys 在本 FB 章节均未列具体 `ErrorID` 数值。
