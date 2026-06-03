# MC_AxRtReadPressureDiff_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Pressure / Force sensing` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599758987.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_AxRtReadPressureDiff_BkPlcMc.TcPOU`](../examples/P_Demo_MC_AxRtReadPressureDiff_BkPlcMc.TcPOU) |

---

## 1. 功能简述

从**双路模拟量输入终端**读取液压缸 A/B 两侧压力并计算**差压**的功能块。每周期把 `AdcValueA` / `AdcValueB`（缸两侧各一只压力传感器的 ADC 原始值）经各自 `ScaleFactor` / `ScaleOffset` 标定后求差，写入 `ST_TcHydAxRtData.fActPressure`。适合差动缸（活塞两侧面积不同）需要看真实工作压差的场景。

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
    ReadingMode:    E_TcMcPressureReadingMode:=iTcHydPressureReadingDefault;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `AdcValueA` | `INT` | `0` | A 侧压力传感器 ADC 原始值 |
| `AdcValueB` | `INT` | `0` | B 侧压力传感器 ADC 原始值 |
| `ScaleFactorA` | `LREAL` | `0.0` | A 侧标定系数，单位 bar/ADC_INC |
| `ScaleOffsetA` | `LREAL` | `0.0` | A 侧零点偏移，单位 bar |
| `ScaleFactorB` | `LREAL` | `0.0` | B 侧标定系数，单位 bar/ADC_INC |
| `ScaleOffsetB` | `LREAL` | `0.0` | B 侧零点偏移，单位 bar |
| `ReadingMode` | `E_TcMcPressureReadingMode` | `iTcHydPressureReadingDefault` | 决定结果写到 `fActPressure` 或 `fActForce` |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis:           AXIS_REF_BkPlcMc;
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

**调用模式**：每周期调用。与 Single 版同样必须在压力闭环 FB 之前。

**指针检查**：`pStAxRtData` 未初始化 → `Error := TRUE`、`ErrorID := dwTcHydErrCdPtrMcPlc`。

**差压计算**：
- A 侧压力：`P_A = AdcValueA × ScaleFactorA + ScaleOffsetA`
- B 侧压力：`P_B = AdcValueB × ScaleFactorB + ScaleOffsetB`
- 差压：`fActPressure = P_A - P_B`（具体公式可能在 FB 内部考虑活塞面积比，本 FB 是纯差压版；要考虑面积比用 ForceDiff）

**标定方案 A**（推荐高质量 ±10V 传感器）：
- `ScaleFactorA := 传感器额定 / AdcValueA_MAX`、`ScaleFactorB` 同
- `ScaleOffset` 校零点

**标定方案 B**（需要运动）：分别开到两端推到系统压力 / 油箱压力，从测量值反算。

**典型用法**：
- 差动缸的真实工作压差监控
- 双向比例阀的双向压力补偿

**典型陷阱**：
- 用单路传感器但接到本 FB：B 侧无信号 → 差压计算错误；应换用 Single 版
- A/B 侧 ScaleFactor 不一致：实际值有偏差但 PLC 内看不到，因为标定不准

## 4. 错误码 / 返回值

| `ErrorID` 常量 | 含义 | 处理建议 |
|---|---|---|
| `dwTcHydErrCdPtrMcPlc` | `pStAxRtData` 指针未初始化 | 检查轴初始化 |

## 5. 使用注意 / 常见坑

- **必须每周期调**：与 Single 同。
- **顺序在闭环之前**：同。
- **A/B 侧独立校准**：每只传感器都要单独算 Scale。
- **差压方向**：A 侧高 B 侧低 → fActPressure > 0；反之 < 0。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_AxRtReadPressureDiff_BkPlcMc.TcPOU`](../examples/P_Demo_MC_AxRtReadPressureDiff_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：液压差动缸（活塞两侧面积比 2:1）的精密压力测量。A 侧（大面积）100 bar、B 侧（小面积）50 bar 实际工作差压 = 50 bar；如果用单路传感器只看一侧无法知道真实差压。本 FB 把两侧传感器读数都拿到并求差，反映真实工况。
- **价值**：精确控制差动缸压力的关键 — 单路传感器看不到差压，无法做精确闭环。
- **替代方案对比**：
  - 单路 ReadPressureSingle：只看一侧，差动缸不行
  - 业务侧自己读 2 路 + 算差：能用但与库的数据流不一致
  - **本 FB**：液压库差压采集标准接口

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.4.3.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599758987.html
- **相关 FB**：`MC_AxRtReadPressureSingle_BkPlcMc`（单路版）、`MC_AxRtReadForceDiff_BkPlcMc`（计算力差）、`MC_AxCtrlPressure_BkPlcMc`（消费差压的闭环）
