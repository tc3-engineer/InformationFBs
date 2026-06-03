# MC_AxRtReadForceSingle_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Pressure / Force sensing` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599757963.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_AxRtReadForceSingle_BkPlcMc.TcPOU`](../examples/P_Demo_MC_AxRtReadForceSingle_BkPlcMc.TcPOU) |

---

## 1. 功能简述

从**单路模拟量输入终端**读取液压缸**实际力**（含滑动摩擦补偿）的功能块。每周期把 `AdcValue`（实际是 PDF 写 A 和 B 但只用 A，PDF 文档错误）经标定换算为压力，再乘活塞面积、扣除滑动摩擦后得到作用在负载上的力，写入 `fActPressure`（注：液压库内部 fActPressure 字段名虽然是 pressure，但本 FB 计算出来的实际是 force——这是库的命名继承遗留问题）。

⚠️ **PDF VAR_INPUT 文档错误**：本 FB 的 VAR_INPUT 在 PDF 中被错抄成了 Diff 版的 8 个字段（`AdcValueA` / `AdcValueB` / `ScaleFactorA` / `ScaleFactorB` 等），但 FB 接口图和实际编译时的字段应该只有 4 个单路字段（`AdcValue` / `ScaleFactor` / `ScaleOffset` / `ReadingMode`）+ `SlippingOffset`。本仓库严格按 PDF VAR_INPUT 字面搬运。

## 2. 接口定义

### VAR_INPUT

PDF 章节 §4.4.3.3 的 VAR_INPUT 代码块字面如下（明显是从 ForceDiff 版错抄过来的）：

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
| `AdcValueA` | `INT` | `0` | ⚠️ PDF 列出，但 Single 版理论只用一路；实际用法是把这个当作"单路力传感器的 ADC 输入"使用 |
| `AdcValueB` | `INT` | `0` | ⚠️ PDF 文档错误字段；Single 版应该没有 B 路。实际编译可能允许传 0 |
| `ScaleFactorA` | `LREAL` | `0.0` | A 侧标定系数，单位 N/ADC_INC |
| `ScaleOffsetA` | `LREAL` | `0.0` | A 侧零点偏移 |
| `ScaleFactorB` | `LREAL` | `0.0` | ⚠️ PDF 文档错误字段 |
| `ScaleOffsetB` | `LREAL` | `0.0` | ⚠️ PDF 文档错误字段 |
| `SlippingOffset` | `LREAL` | `0.0` | 滑动摩擦补偿值，单位 N（计算"作用在负载上的真实力"时减去摩擦力） |
| `ReadingMode` | `E_TcMcPressureReadingMode` | `iTcHydPressureReadingDefault` | 决定结果写到哪个字段 |

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

**调用模式**：每周期调用。

**力计算**：PDF 描述 "evaluating the variables AdcValue" — Single 版只用 `AdcValueA` 一个值（PDF 的"AdcValueA"在 Single 版实际承载单路输入）：
- 计算压力：`P = AdcValueA × ScaleFactorA + ScaleOffsetA`
- 计算力：`F = P × A_piston - SlippingOffset`（活塞面积来自轴参数）
- 写入 `fActPressure`

**`SlippingOffset` 用法**：液压缸有静摩擦力（典型 5-15% 工作压力），实际"作用在工件上"的力 = 液压力 - 摩擦力。`SlippingOffset` 让结果反映真实工件受力，便于做精确力闭环。

**典型用法**：单只力传感器测量的力闭环；冲压机推力监控。

**典型陷阱**：
- PDF VAR_INPUT 字段错乱：编译时按实际字段写；如果非要保持 PDF 字面，`AdcValueB` / `ScaleFactorB` / `ScaleOffsetB` 设 0 即可
- 忽略 `SlippingOffset`：力数据有 5-15% 静摩擦偏差
- 单位混淆：`ScaleFactor` 单位是 N/ADC（不是 bar/ADC）

## 4. 错误码 / 返回值

PDF 未列具体 `ErrorID` 数值；按 ReadPressureSingle 类似，常见 `dwTcHydErrCdPtrMcPlc`。⚠️ 待人工确认。

## 5. 使用注意 / 常见坑

- **PDF VAR_INPUT 大概率有文档错误**：列了 Diff 版的 B 路字段；实际工程按 InfoSys 与编译时报错为准（InfoSys 同样列了这些字段，可能 Beckhoff 内部就是这么定义的——保留了所有字段，B 路传 0 不影响）。
- **单位 N/ADC_INC**：是力，不是压力。
- **`SlippingOffset` 不要忘**：影响力测量精度。
- **顺序在闭环之前**：同压力 FB。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_AxRtReadForceSingle_BkPlcMc.TcPOU`](../examples/P_Demo_MC_AxRtReadForceSingle_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：冲压机液压压头力反馈链。压头底部装一只力传感器（不是压力传感器）直接测施加在工件上的力。本 FB 把传感器 ADC 值换算为 N 并扣除液压缸自身的静摩擦力，得到"工件实际受力"用于过载保护。
- **价值**：手写需要 ADC → N 换算 + 静摩擦扣除；本 FB 一行调用搞定，且与液压库的标准压力闭环接口对接。
- **替代方案对比**：
  - 用压力传感器读 + 自己算 force：能用但摩擦力补偿复杂
  - `MC_AxRtReadForceDiff_BkPlcMc`：双路差动版，单路用不上
  - **本 FB**：单路力测量标准接口

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.4.3.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599757963.html
- **相关 FB**：`MC_AxRtReadForceDiff_BkPlcMc`（双路差动力）、`MC_AxRtReadPressureSingle_BkPlcMc`（单路压力）、`MC_AxCtrlPressure_BkPlcMc`（消费 force 的闭环）

## 9. 待确认项 (⚠️)

- PDF VAR_INPUT 字段列表包含 Diff 版的 `AdcValueB` / `ScaleFactorB` / `ScaleOffsetB`，但本 FB 名为 "Single" 版理论上不应该有 B 路字段。Beckhoff 可能保留这些字段以便 FB 内部兼容性切换，业务侧给 0 即可。
- PDF 未列具体 `ErrorID` 数值。
