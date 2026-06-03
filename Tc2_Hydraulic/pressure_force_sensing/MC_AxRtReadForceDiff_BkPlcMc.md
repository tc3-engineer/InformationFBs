# MC_AxRtReadForceDiff_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Pressure / Force sensing` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599756939.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_AxRtReadForceDiff_BkPlcMc.TcPOU`](../examples/P_Demo_MC_AxRtReadForceDiff_BkPlcMc.TcPOU) |

---

## 1. 功能简述

从**双路模拟量输入终端**读取液压缸 A/B 两侧压力，按各自活塞面积计算两侧作用力，求差并扣除滑动摩擦得到**作用在负载上的真实力**的功能块。每周期写入 `fActPressure`（名虽是 pressure 但承载的是 N）。差动缸（活塞两侧面积比 ≠ 1）做精确力闭环必备。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    AdcValueA:      INT:=0;
    AdcValueB:      INT:=0;
    ScaleFactorA:   LREAL:=0.0;
    ScaleOffsetA:   LREAL:=0.0;
    ScaleFactorB:   LREAL:=0.0;
    ScaleOffsetB:   LREAL:=0.0;
    SlippingOffset: LREAL:=0.0;
    ReadingMode:    E_TcMcPressureReadingMode:=iTcHydPressureReadingDefault;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `AdcValueA` | `INT` | `0` | A 侧（大面积端）压力传感器 ADC 原始值 |
| `AdcValueB` | `INT` | `0` | B 侧（小面积端）压力传感器 ADC 原始值 |
| `ScaleFactorA` | `LREAL` | `0.0` | A 侧标定系数，单位 N/ADC_INC（含面积转换） |
| `ScaleOffsetA` | `LREAL` | `0.0` | A 侧零点偏移 |
| `ScaleFactorB` | `LREAL` | `0.0` | B 侧标定系数 |
| `ScaleOffsetB` | `LREAL` | `0.0` | B 侧零点偏移 |
| `SlippingOffset` | `LREAL` | `0.0` | 滑动摩擦补偿值，单位 N |
| `ReadingMode` | `E_TcMcPressureReadingMode` | `iTcHydPressureReadingDefault` | 决定结果写到哪个字段 |

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
    Error:          BOOL;
    ErrorID:        UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Error` | `BOOL` | 出错指示 |
| `ErrorID` | `UDINT` | 编码错误号 |

## 3. 行为说明

本功能块**每周期调用**，与其它 cyclic 实际值采集功能块同步运行。它要求被调用的位置必须在所有压力闭环 / 力闭环功能块（`MC_AxCtrlPressure_BkPlcMc` 等）和上层读出功能块（`MC_ReadActualTorque_BkPlcMc`）之前，否则下游消费者读到的将是上一周期的旧值，会差一拍影响闭环稳定性。

**力差计算流程**：
- A 侧力：`F_A = AdcValueA × ScaleFactorA + ScaleOffsetA`（系数已含活塞面积换算）
- B 侧力：`F_B = AdcValueB × ScaleFactorB + ScaleOffsetB`
- 净力（含摩擦补偿）：`F_net = F_A - F_B - SlippingOffset`（具体方向视活塞结构）
- 把净力结果写入 `Axis.pStAxRtData^.fActPressure`（库内字段命名遗留——名字虽是 pressure，本 FB 写入的实际是 N）

**标定的关键要点**：计算 `ScaleFactor` 时如果用于"实际压力"，A/B 侧 `ScaleArea` 应设 1.0；如果用于"实际力"，要给出 A/B 各自活塞面积（mm²）。PDF §4.4.3.2 给出三种 commissioning option，A 方案适合高质量 ±10V 传感器（无需运动）、B 方案需要全系统压力推到两端死点采集 ADC 值、C 方案不需要轴控制但精度低。

**典型用法**涵盖差动缸精密力闭环（注塑、压铸、深冲）和双向力测量（活塞两侧都可能承力的可逆工况）。

**典型陷阱**：与 ForceSingle 同——单位是 N 而非 bar，HMI 显示别误标；活塞面积参数需另在轴参数里配；`SlippingOffset` 直接影响实际力精度，不做摩擦补偿会有 5-15% 系统性偏差。

## 4. 错误码 / 返回值

PDF 未列具体 `ErrorID` 数值；⚠️ 待人工确认。

## 5. 使用注意 / 常见坑

- **必须每周期调**：cyclic 实际值采集。
- **顺序在闭环之前**：与 Pressure 同。
- **A/B 侧分别标定**：每侧独立校准。
- **`SlippingOffset` 是 N**：与 ForceSingle 同。
- **`ReadingMode` 决定写哪个字段**：默认 fActPressure。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_AxRtReadForceDiff_BkPlcMc.TcPOU`](../examples/P_Demo_MC_AxRtReadForceDiff_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：液压压铸机注射缸（差动结构）。注射时活塞两侧压力都会变化（A 侧推油 100 bar、B 侧反油 30 bar），活塞面积比 2:1，真实推力 = A 侧推力 - B 侧推力 - 摩擦。本 FB 算出真实推力供注射段力闭环和过载报警使用。
- **价值**：差动缸力测量必备；单路 ReadForceSingle 看不到对侧压力变化导致的力变化。
- **替代方案对比**：
  - ReadForceSingle：只看一侧，差动缸不行
  - ReadPressureDiff + 自算力：能用但要自己做面积换算和摩擦补偿
  - **本 FB**：差动力测量标准接口

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.4.3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599756939.html
- **相关 FB**：`MC_AxRtReadForceSingle_BkPlcMc`（单路力）、`MC_AxRtReadPressureDiff_BkPlcMc`（双路压力）、`MC_AxCtrlPressure_BkPlcMc`（消费力的闭环）

## 9. 待确认项 (⚠️)

- PDF 未列具体 `ErrorID` 数值。
- PDF 中提到的 `ScaleArreaA` 拼写错误（应为 `ScaleAreaA`），这是 PDF 文档错误，FB 实际行为依赖正确参数；本仓库严格按 PDF 字面（"ScaleArreaA"出现在描述段）。
