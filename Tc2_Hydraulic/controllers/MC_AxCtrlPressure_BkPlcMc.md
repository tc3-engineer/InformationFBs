# MC_AxCtrlPressure_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Controllers` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599750027.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_AxCtrlPressure_BkPlcMc.TcPOU`](../examples/P_Demo_MC_AxCtrlPressure_BkPlcMc.TcPOU) |

---

## 1. 功能简述

液压轴**压力闭环 PI 控制器**功能块。`Enable = TRUE` 时控制器把 `ST_TcHydAxRtData.fSetPressure`（设定压力）与 `ReadingMode` 指定的实际值（`fActPressure` / `fActForce`）做差，经 `kP` × P + 1/`Tn` × I 计算后输出到 `fSetSpeed`（代替正常位置控制器作为控制值生成器）。`WindupLimit` 限制 I 部分防止积分饱和。本 FB 是液压库的核心闭环控件之一，做"压力建立 + 保持"控制。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Enable:     BOOL:=FALSE;
    Reset:      BOOL:=TRUE;
    FirstAuxParamIdx: INT:=0;
    kP:         LREAL:=0.0;
    Tn:         LREAL:=0.0;
    ReadingMode:E_TcMcPressureReadingMode:=iTcHydPressureReadingDefault;
    PreSet:     LREAL:=0.0;
    WindupLimit:LREAL:=0.0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Enable` | `BOOL` | `FALSE` | `TRUE` 激活控制器；上升沿时 I 部分用 `PreSet` 初始化 |
| `Reset` | `BOOL` | `TRUE` | `TRUE` 复位控制器到 idle 状态；P 与 I 部分都清零 |
| `FirstAuxParamIdx` | `INT` | `0` | 在 `ST_TcHydAxParam.fCustomerData` 中选一段作为参数接口（高级用法） |
| `kP` | `LREAL` | `0.0` | P 部分增益系数 |
| `Tn` | `LREAL` | `0.0` | I 部分积分时间常数（s） |
| `ReadingMode` | `E_TcMcPressureReadingMode` | `iTcHydPressureReadingDefault` | 选择被控的实际值：Default/ActPressure 控 `fActPressure`、ActForce 控 `fActForce` |
| `PreSet` | `LREAL` | `0.0` | I 部分初值；`Enable` 上升沿时把 I 预加载为该值，可加速达到平衡 |
| `WindupLimit` | `LREAL` | `0.0` | I 部分饱和限幅；防止"无响应"场景下 I 无限增长 |

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
    Error:      BOOL;
    ErrorID:    UDINT;
    InWindup:   UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Error` | `BOOL` | 出错指示 |
| `ErrorID` | `UDINT` | 编码错误号 |
| `InWindup` | `UDINT` | I 部分被 `WindupLimit` 限幅时为 `TRUE`。⚠️ PDF 代码块声明类型为 `UDINT` 但描述说"becomes TRUE"——类型语义不一致；按 PDF 字面搬运 |

## 3. 行为说明

**调用模式**：每周期调用。位置上必须在"实际值/压力采集"FB 之后、`MC_AxRtFinish_BkPlcMc` 之前。

**`Reset` 优先级**：`Reset = TRUE` 时控制器无视其它信号进入 idle，P/I 都清零。`Reset = FALSE` 才看 `Enable`。

**`ReadingMode` 决定被控变量**：
- `iTcHydPressureReadingDefault` / `iTcHydPressureReadingActPressure` → 控 `fActPressure`
- `iTcHydPressureReadingActForce` → 控 `fActForce`
- 其它值 → 控制器**禁用**

**设定值传递**：设定压力必须由业务代码写入 `Axis.pStAxRtData^.fSetPressure`（不是本 FB 输入）。本 FB 算的是 setpoint - actual 的误差。

**控制流**：
1. `Enable` 上升沿：I 部分 = `PreSet`
2. 每周期：P 部分 = `kP × error`、I 部分累加 `error × dt / Tn`、I 部分被 `WindupLimit` 限幅
3. 输出 = `(P + I)` 写入 `ST_TcHydAxRtData.fSetSpeed`
4. 控制器同时清掉 `fLagCtrlOutput`（避免位置控制器的输出叠加）
5. 后续 `MC_AxRtFinish_BkPlcMc` 把 `fSetSpeed` 转为阀输出电压

**`Enable` 撤销**：P 与 I 都清零，控制器回到 idle 状态。

**典型用法**：
- 注塑保压段：压力闭环维持 100 bar 直到保压定时器到时
- 冲压力控：恒力顶压工件
- 液压试压：维持指定压力一段时间

**典型陷阱**：
- 没写 `fSetPressure`：控制器以 0 为目标，会把压力降到 0
- `Reset` 与 `Enable` 都 TRUE：`Reset` 赢，控制器不工作
- `kP` 过大：振荡
- `Tn` 过小：积分太快导致超调
- `WindupLimit = 0`：可能解释为"无限幅"或"积分总是 0"（行为依实现），调试时设合理值
- 没在 PressureReading FB 之后调：fActPressure 是上一周期的值，差一拍

## 4. 错误码 / 返回值

PDF 未在本 FB 章节列具体 `ErrorID` 数值；⚠️ 待人工补充。

## 5. 使用注意 / 常见坑

- **必须每周期调**：闭环 FB，漏调就失控
- **位置必须正确**：在压力读取 FB 后、Finish 之前
- **`fSetPressure` 是业务代码的责任**：本 FB 只算偏差
- **`InWindup` 类型矛盾**：声明 UDINT 但描述说 TRUE/FALSE；按 BOOL 语义用（非 0 即 TRUE）
- **接管位置控制器**：激活时 `fLagCtrlOutput` 被清，意味着位置控制器输出被替代；切回位置控制要 Reset

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_AxCtrlPressure_BkPlcMc.TcPOU`](../examples/P_Demo_MC_AxCtrlPressure_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机锁模到位后切换到"保压"控制段。模具内塑料压力必须稳定在 100 bar 维持 5 秒（保压时间），等塑料凝固。本 FB 把比例阀输出从位置控制切到压力闭环：业务侧写 `fSetPressure := 100.0`，PI 控制器自动调阀开度让 fActPressure 收敛到 100 bar 且稳定。
- **价值**：手写 PI 控制器需要自己处理 `dt` 计算、积分饱和、控制器切换、阀输出标定；本 FB 集成了液压库的"控制值生成器"接口，与位置控制器协同切换无冲突。
- **替代方案对比**：
  - 自己写 PI：能用但与位置控制器切换时有"输出跳变"风险
  - 用通用 `Tc2_Filter` 库的 PID：与液压库的控制值流程不集成
  - **本 FB**：液压库原生压力闭环

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.4.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599750027.html
- **相关 FB**：`MC_AxRtReadPressureSingle_BkPlcMc` / `MC_AxRtReadPressureDiff_BkPlcMc`（提供 fActPressure）、`MC_AxCtrlSlowDownOnPressure_BkPlcMc`（压力达到时减速）、`MC_AxCtrlAutoZero_BkPlcMc`（零位补偿）、`MC_AxRtFinish_BkPlcMc`（输出阶段）

## 9. 待确认项 (⚠️)

- `InWindup` 字段 PDF 声明类型 `UDINT` 但描述写 "becomes TRUE"；类型不一致，本仓库按 PDF 代码块字面保留 `UDINT`。
- PDF 未列具体 `ErrorID` 数值。
