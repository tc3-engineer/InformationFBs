# MC_AxCtrlSlowDownOnPressure_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Controllers` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599751051.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_AxCtrlSlowDownOnPressure_BkPlcMc.TcPOU`](../examples/P_Demo_MC_AxCtrlSlowDownOnPressure_BkPlcMc.TcPOU) |

---

## 1. 功能简述

液压轴**压力限制减速控制器**功能块。设定压力上限后，当运动期间实际压力（或力）即将超过限制时，本 FB 自动降低速度以确保压力不超限。`EnableP` 控正方向运动期间的限压、`EnableM` 控反方向；可单独启用某一方向（或两个都启用）。与 `MC_AxCtrlPressure_BkPlcMc`（直接控压力）不同，本 FB 是"运动 + 限压"的复合作用——主控目标是位置/速度，但压力超过一定值时优先保证不超。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    EnableP:          BOOL:=FALSE;
    EnableM:          BOOL:=FALSE;
    Reset:            BOOL:=TRUE;
    FirstAuxParamIdx: INT:=0.0;
    kP:               LREAL:=0.0;
    Tn:               LREAL:=0.0;
    PreSet:           LREAL:=0.0;
    ReadingMode:      E_TcMcPressureReadingMode:=iTcHydPressureReadingDefault;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `EnableP` | `BOOL` | `FALSE` | 正方向运动时启用限压控制器 |
| `EnableM` | `BOOL` | `FALSE` | 反方向运动时启用限压控制器 |
| `Reset` | `BOOL` | `TRUE` | 复位 I 部分 |
| `FirstAuxParamIdx` | `INT` | `0.0` | `fCustomerData` 接口起始索引（注意 PDF 默认值写 `0.0` 但类型是 `INT`——明显文档错误，按 PDF 字面搬运） |
| `kP` | `LREAL` | `0.0` | P 增益 |
| `Tn` | `LREAL` | `0.0` | I 积分时间（s） |
| `PreSet` | `LREAL` | `0.0` | I 初值 |
| `ReadingMode` | `E_TcMcPressureReadingMode` | `iTcHydPressureReadingDefault` | 被监控的实际值选择 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis:             AXIS_REF_BkPlcMc;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF_BkPlcMc` | 轴接口结构。必须以 `VAR_IN_OUT` 方式传引用 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Response:         LREAL;
    Active:           BOOL;
    Error:            BOOL;
    ErrorID:          UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Response` | `LREAL` | 压力控制器输出值（用于诊断观察当前控制器贡献多少减速量） |
| `Active` | `BOOL` | 控制器正在介入（即压力达到限制，正在降速）。`FALSE` 表示限压未触发，运动按原指令走 |
| `Error` | `BOOL` | 出错指示 |
| `ErrorID` | `UDINT` | 编码错误号 |

## 3. 行为说明

**调用模式**：每周期调用，电平触发（`EnableP` / `EnableM`）。

**`Reset` 优先级**：`Reset = TRUE` 时控制器进 idle，`Active := FALSE`、`Response := 0.0`，P/I 都清零。

**`EnableP` / `EnableM` 语义**：方向性使能。例如冲压轴只在向工件方向（正方向）运动时需要限压，反方向退回时不需要——这时只设 `EnableP := TRUE`。FB 内部用 `fSetSpeed` 的符号判断当前方向，决定是否激活控制器。

**控制逻辑**：
1. 根据 `EnableP` / `EnableM`、`fSetSpeed` 的符号、`fSetPressure` 与实际值的差判断是否要 Active
2. Active 时计算 P+I 控制器响应；`Response` 加到速度命令上减速
3. Active 转换瞬间 I 用 `PreSet` 初始化
4. 设定压力在 `Axis.pStAxRtData^.fSetPressure`

**`ReadingMode` 各值**：同 `MC_AxCtrlPressure_BkPlcMc`。

**典型用法**：
- 冲压：轴向工件推进时若工件硬度异常导致压力突然升高 → 自动减速避免损坏模具
- 装夹液压缸：夹紧到位前正常速度，接触工件压力达到 X bar 时自动减速到爬行速度
- 注射段：实际背压超过限值时自动降低注射速度

**典型陷阱**：
- `EnableP` / `EnableM` 都 FALSE：FB 永远不 Active
- 没设 `fSetPressure`：以 0 为目标，任何压力都触发减速 → 寸步难行
- `kP` / `Tn` 调试：与 PressureCtrl 类似的 PID 调参逻辑

## 4. 错误码 / 返回值

PDF 未在本 FB 章节列具体 `ErrorID` 数值；⚠️ 待人工补充。

## 5. 使用注意 / 常见坑

- **`FirstAuxParamIdx` 默认值 `0.0` 是 PDF 错误**：类型是 `INT`，应该是 `0`；编译时 IEC 会做隐式转换。
- **方向使能必须正确**：单向工艺只启一个方向，避免反向也减速。
- **本 FB 不替代位置控制器**：是叠加在正常运动控制之上的"安全限压"层；正常运动 FB（MoveAbsolute 等）继续工作。
- **`Response` 用于诊断**：调试时观察这个值看控制器贡献了多少减速量；调参的参考。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_AxCtrlSlowDownOnPressure_BkPlcMc.TcPOU`](../examples/P_Demo_MC_AxCtrlSlowDownOnPressure_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：冲压机液压压头向工件正方向推进。正常工件压力上升到 200 bar 时算冲压完成；但如果工件位置偏离或材料异硬，压力可能突然飙升到 350 bar 损坏模具。设 `fSetPressure := 250` 作为压力上限，本 FB 在压头向下时（`EnableP := TRUE`）监控压力，超 250 bar 时自动减速避免冲击。
- **价值**：手写需要每周期判压力 → 如果超限发 Halt → 等停 → 再发 MoveAbsolute；本 FB 把这套逻辑作为闭环平滑实现，不需要每次都 stop/restart。
- **替代方案对比**：
  - `MC_AxCtrlPressure_BkPlcMc`：纯压力闭环，主控目标是压力不是位置
  - 业务侧轮询压力 + Halt：粗暴，每次触发都 Stop-Restart 失去工艺连续性
  - **本 FB**：运动期间的"安全压力 cap"

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.4.1.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599751051.html
- **相关 FB**：`MC_AxCtrlPressure_BkPlcMc`（纯压力闭环）、`MC_AxRtReadPressureSingle_BkPlcMc` / Diff（压力数据源）、`MC_AxCtrlAutoZero_BkPlcMc`（阀零位补偿）

## 9. 待确认项 (⚠️)

- PDF VAR_INPUT 中 `FirstAuxParamIdx: INT:=0.0`——类型 INT 默认值 0.0 是 PDF 文档错误。
- PDF 未列具体 `ErrorID` 数值。
