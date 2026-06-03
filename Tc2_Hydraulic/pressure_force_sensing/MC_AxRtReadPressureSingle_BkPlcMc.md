# MC_AxRtReadPressureSingle_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Pressure / Force sensing` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599760011.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_AxRtReadPressureSingle_BkPlcMc.TcPOU`](../examples/P_Demo_MC_AxRtReadPressureSingle_BkPlcMc.TcPOU) |

---

## 1. 功能简述

从**单路模拟量输入终端**读取液压轴**实际压力**的功能块。每周期把 `AdcValue`（来自 EL30xx / KL30xx 系列模拟量端子的原始 INT 值）通过 `ScaleFactor` / `ScaleOffset` 线性换算到工程单位（bar）写入 `ST_TcHydAxRtData.fActPressure`（默认）或 `fActForce`（由 `ReadingMode` 决定）。是 `MC_AxCtrlPressure_BkPlcMc` 等压力闭环 FB 的**数据源前置**，必须每周期调用且在闭环 FB 之前。差动双路压力传感器用 `MC_AxRtReadPressureDiff_BkPlcMc`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    AdcValue:       INT:=0;
    ScaleFactor:    LREAL:=0.0;
    ScaleOffset:    LREAL:=0.0;
    ReadingMode:    E_TcMcPressureReadingMode:=iTcHydPressureReadingDefault;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `AdcValue` | `INT` | `0` | 模拟量端子原始 ADC 值（16 位 INT，例如 EL3024 ±10V → ±32767） |
| `ScaleFactor` | `LREAL` | `0.0` | 标定系数，单位 bar/ADC_INC。决定每 ADC 增量对应的压力增量。例：250 bar / 32767 ≈ 0.00763 |
| `ScaleOffset` | `LREAL` | `0.0` | 零点偏移，单位 bar。修正传感器零点误差 |
| `ReadingMode` | `E_TcMcPressureReadingMode` | `iTcHydPressureReadingDefault` | 决定结果写到哪个字段。Default → `fActPressure` |

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

**调用模式**：每周期调用（与其它 cyclic 实际值采集 FB 同）。

**调用顺序**：必须在压力闭环 FB（`MC_AxCtrlPressure_BkPlcMc` / `MC_AxCtrlSlowDownOnPressure_BkPlcMc`）和 `MC_ReadActualTorque_BkPlcMc` 之前调用，否则它们读到的是上一周期的旧值。

**计算**：每周期算 `fActPressure := AdcValue × ScaleFactor + ScaleOffset`（具体公式取决于 `ReadingMode`）。

**指针检查**：若 `pStAxRtData` 指针未初始化 → `Error := TRUE`、`ErrorID := dwTcHydErrCdPtrMcPlc`。此时**不**把轴置错误状态（避免压力采集失败导致整个轴 down）。

**标定步骤（PDF 推荐 A 方案）**：
1. 无需运动轴
2. `ScaleFactor := 传感器额定压力 / AdcValue_MAX`
   - 例：传感器 250 bar 满量程 + EL3024 ±10V → `ScaleFactor := 250.0 / 32767 ≈ 0.00763`
3. `ScaleOffset := -ScaleFactor × AdcValue_at_zero`（修正零点）

**标定 B 方案（需要运动）**：
1. 让活塞分别开到上下死点，记录两端 `AdcValue` 和实测压力
2. `ScaleFactor := (P_max - P_min) / (Adc_max - Adc_min)`
3. `ScaleOffset := P_min - ScaleFactor × Adc_min`

**典型用法**：把 EL3024 模拟量端子上压力传感器读数变换成 PLC 内可用的 bar 值，供压力闭环 / HMI 显示 / 报警判断使用。

**典型陷阱**：
- 漏调用：`fActPressure` 永远是 0（或上次值），导致压力闭环失控
- 调用顺序错：闭环 FB 用到的是旧值，差一拍影响稳定性
- 单位混淆：`ScaleFactor` 是 bar/ADC，不是 V/ADC；如果传感器输出已是 0-10V，要先想清 0-10V 对应多少 bar
- ⚠️ `ScaleOffset` 单位 PDF 写 `[N/ADC_INC]` 但本 FB 输出是 bar——PDF 文档错误，单位应为 bar

## 4. 错误码 / 返回值

| `ErrorID` 常量 | 含义 | 处理建议 |
|---|---|---|
| `dwTcHydErrCdPtrMcPlc` | `pStAxRtData` 指针未初始化 | 检查轴初始化 |

## 5. 使用注意 / 常见坑

- **必须每周期调**：cyclic 实际值采集；漏调闭环失控。
- **必须在压力闭环 FB 之前**：保证 fActPressure 是当前周期新值。
- **标定要校准**：开机前用 A 方案算出 ScaleFactor + ScaleOffset 写入轴参数 `fCustomerData[]` 持久化。
- **`ScaleOffset` 单位 PDF 错**：本 FB 是压力（bar），不是力（N）。PDF 写 `N/ADC_INC` 是从 ForceSingle 错抄过来。
- **错误时不置轴错**：PDF 明确，避免压力故障让整个液压系统停。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_AxRtReadPressureSingle_BkPlcMc.TcPOU`](../examples/P_Demo_MC_AxRtReadPressureSingle_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：液压注塑机注射缸压力反馈链。EL3024 模拟量端子接 0-250 bar 压力变送器（输出 0-10V），本 FB 把 PLC 内 ADC 值 0-32767 换算到 bar 写入轴 runtime，供保压段的 `MC_AxCtrlPressure_BkPlcMc` 闭环使用。
- **价值**：手写需要每周期算 `bar := raw × factor + offset`，要小心 INT vs REAL 类型转换、Saturation 等；本 FB 把这套逻辑封装并与液压库其它压力 FB 的数据流接口对齐。
- **替代方案对比**：
  - 业务侧手算赋值给 `fActPressure`：能用但与库的标准数据流不匹配
  - 用通用 `Tc2_Standard` 的 SCALE 函数：通用但要自己写 dispatch
  - **本 FB**：液压库原生压力数据源

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.4.3.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599760011.html
- **相关 FB**：`MC_AxRtReadPressureDiff_BkPlcMc`（双路差动版）、`MC_AxRtReadForceSingle_BkPlcMc`（读力版）、`MC_AxCtrlPressure_BkPlcMc`（消费数据的闭环）、`MC_ReadActualTorque_BkPlcMc`（业务侧读 fActPressure）、`E_TcMcPressureReadingMode`（决定写哪个字段）

## 9. 待确认项 (⚠️)

- PDF 中 `ScaleOffset` 单位写 `[N/ADC_INC]` 实际应为 `[bar]`（疑似从 ForceSingle 章节复制错）。
