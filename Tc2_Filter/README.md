# Tc2_Filter

> TwinCAT 3 信号滤波库（产品代号 **TF3680 | TwinCAT 3 Filter**）。提供 IIR/FIR、移动平均、中值、高斯、陷波，以及控制工程常用的 PT1/PT2/PT3/PTn/PT2oscillation/PTt/LeadLag 等数字滤波器函数块。版本 `1.8.0`。

- [官方 InfoSys](https://infosys.beckhoff.com/content/1033/tf3680_tc3_filter/index.html)
- [官方 PDF](https://download.beckhoff.com/download/document/automation/twincat3/TF3680_TC3_Filter_EN.pdf)

## 全族共用的接口范式

本库 15 个函数块**接口完全一致**，只是配置结构 `ST_FTR_<type>` 的参数不同：

- 输入 `stConfig : ST_FTR_<type>` —— 一个结构装下全部滤波参数（增益/时间常数/截止频率/阶数/通道/过采样…）。
- 输出 `bError : BOOL`、`bConfigured : BOOL`、`ipResultMessage : I_TCMessage`（错误经 EventLogger 报出）。
- 三个方法：`Configure()` 配置或重配；`Call()` 每个采样周期推进一步（数组用 `ADR()`+`SIZEOF()` 传）；`Reset()` 清历史状态。
- `FB_FTR_ActualValue` 额外提供 `GetFilterActive()` 与 `GetFilterActiveTimestamps()` 两个查询方法。

> 调用要点：`Call()` 的频率必须等于 `stConfig.fSamplingRate`（把本 POU 放进对应周期的任务）；先 `Configure`（`bConfigured = TRUE`）才能 `Call`/`Reset`。

## 索引（15 条 · 全部 ✅ verified）

### Function blocks（15）

| Category | Name | 滤波器类型 | 文档 | 例程 |
|---|---|---|---|---|
| Function blocks | FB_FTR_IIRCoeff | 自定义系数 IIR（可退化 FIR） | [✅ verified](function_blocks/FB_FTR_IIRCoeff.md) | [P_Demo_FB_FTR_IIRCoeff.TcPOU](examples/P_Demo_FB_FTR_IIRCoeff.TcPOU) |
| Function blocks | FB_FTR_IIRSos | 二阶节级联 IIR（SOS/biquad） | [✅ verified](function_blocks/FB_FTR_IIRSos.md) | [P_Demo_FB_FTR_IIRSos.TcPOU](examples/P_Demo_FB_FTR_IIRSos.TcPOU) |
| Function blocks | FB_FTR_IIRSpec | 标准型 IIR（Butterworth/Chebyshev/Bessel） | [✅ verified](function_blocks/FB_FTR_IIRSpec.md) | [P_Demo_FB_FTR_IIRSpec.TcPOU](examples/P_Demo_FB_FTR_IIRSpec.TcPOU) |
| Function blocks | FB_FTR_MovAvg | 移动平均（平滑） | [✅ verified](function_blocks/FB_FTR_MovAvg.md) | [P_Demo_FB_FTR_MovAvg.TcPOU](examples/P_Demo_FB_FTR_MovAvg.TcPOU) |
| Function blocks | FB_FTR_Median | 中值（抗脉冲噪声/野值） | [✅ verified](function_blocks/FB_FTR_Median.md) | [P_Demo_FB_FTR_Median.TcPOU](examples/P_Demo_FB_FTR_Median.TcPOU) |
| Function blocks | FB_FTR_Gaussian | 高斯（最小群延迟平滑） | [✅ verified](function_blocks/FB_FTR_Gaussian.md) | [P_Demo_FB_FTR_Gaussian.TcPOU](examples/P_Demo_FB_FTR_Gaussian.TcPOU) |
| Function blocks | FB_FTR_Notch | 窄带带阻（陷波，压工频/共振） | [✅ verified](function_blocks/FB_FTR_Notch.md) | [P_Demo_FB_FTR_Notch.TcPOU](examples/P_Demo_FB_FTR_Notch.TcPOU) |
| Function blocks | FB_FTR_PT1 | 一阶延迟（≈一阶低通） | [✅ verified](function_blocks/FB_FTR_PT1.md) | [P_Demo_FB_FTR_PT1.TcPOU](examples/P_Demo_FB_FTR_PT1.TcPOU) |
| Function blocks | FB_FTR_PT2 | 二阶延迟（两实极点） | [✅ verified](function_blocks/FB_FTR_PT2.md) | [P_Demo_FB_FTR_PT2.TcPOU](examples/P_Demo_FB_FTR_PT2.TcPOU) |
| Function blocks | FB_FTR_PT3 | 三阶延迟 | [✅ verified](function_blocks/FB_FTR_PT3.md) | [P_Demo_FB_FTR_PT3.TcPOU](examples/P_Demo_FB_FTR_PT3.TcPOU) |
| Function blocks | FB_FTR_PTn | n 阶延迟（时间常数相同，n≤10） | [✅ verified](function_blocks/FB_FTR_PTn.md) | [P_Demo_FB_FTR_PTn.TcPOU](examples/P_Demo_FB_FTR_PTn.TcPOU) |
| Function blocks | FB_FTR_PT2oscillation | 振荡型二阶延迟（带阻尼 θ） | [✅ verified](function_blocks/FB_FTR_PT2oscillation.md) | [P_Demo_FB_FTR_PT2oscillation.TcPOU](examples/P_Demo_FB_FTR_PT2oscillation.TcPOU) |
| Function blocks | FB_FTR_PTt | 纯延迟（死区时间） | [✅ verified](function_blocks/FB_FTR_PTt.md) | [P_Demo_FB_FTR_PTt.TcPOU](examples/P_Demo_FB_FTR_PTt.TcPOU) |
| Function blocks | FB_FTR_LeadLag | 一阶超前/滞后（相位校正） | [✅ verified](function_blocks/FB_FTR_LeadLag.md) | [P_Demo_FB_FTR_LeadLag.TcPOU](examples/P_Demo_FB_FTR_LeadLag.TcPOU) |
| Function blocks | FB_FTR_ActualValue | 测量值合理性检查（野值抑制+外推） | [✅ verified](function_blocks/FB_FTR_ActualValue.md) | [P_Demo_FB_FTR_ActualValue.TcPOU](examples/P_Demo_FB_FTR_ActualValue.TcPOU) |

## 快速选型（按用途）

| 需求 | 推荐 FB | 说明 |
|---|---|---|
| 通用平滑去高频噪声 | `FB_FTR_PT1` / `FB_FTR_MovAvg` / `FB_FTR_IIRSpec`(低通) | PT1 用时间常数；移动平均最简单；IIRSpec 可设阶数/截止频率 |
| 保形低相位失真平滑 | `FB_FTR_Gaussian` | 群延迟最小、无旁瓣振铃 |
| 剔除孤立尖峰/野值 | `FB_FTR_Median` / `FB_FTR_ActualValue` | 中值抗脉冲；ActualValue 还能短时外推并回查被改写点 |
| 压制单一干扰频率（工频/共振） | `FB_FTR_Notch` | 用品质因数 `fQ` 调陷波宽窄 |
| 标准型滤波器（低/高/带通/带阻） | `FB_FTR_IIRSpec` | Butterworth/Chebyshev/Bessel，免手算系数 |
| 任意外部系数 / 高阶稳定实现 | `FB_FTR_IIRCoeff` / `FB_FTR_IIRSos` | SOS 抗高阶量化失稳；稳定性自负 |
| 模拟被控对象动态 | `FB_FTR_PT2`/`PT3`/`PTn`/`PT2oscillation`/`PTt` | 惯性/振荡/纯延迟环节 |
| 回路相位补偿 | `FB_FTR_LeadLag` | 超前(`fT1>fT2`)/滞后(`fT1<fT2`)，直流增益保持 1 |

## 数据类型与枚举（被各 FB 引用，未单独成篇）

- **配置结构** `ST_FTR_<type>`（PDF §5.2.1）：各 FB 文档的『配置结构』小节已逐字给出对应结构的定义与参数说明。所有结构都含公共参数 `fSamplingRate` / `nOversamples` / `nChannels` / `pInitialValues` / `nInitialValuesSize`（`ST_FTR_PTt` 无后两项）。
- **`E_FTR_Name`**（PDF §5.2.2）：滤波器实现方式枚举 —— `eButterworth := 1`、`eChebyshev := 2`、`eBessel := 3`（UDINT 基类型）。
- **`E_FTR_Type`**（PDF §5.2.3）：滤波器类型枚举 —— `eLowPass := 1`、`eHighPass := 2`、`eBandPass := 3`、`eBandStop := 4`（UDINT 基类型）。

## 例程导入

每个 FB 配套一个 `examples/P_Demo_<Name>.TcPOU`（TwinCAT 3 原生格式）。统一套路：合成一个『正弦基波 + 可注入尖峰』测试信号喂入滤波器，在线对照观察带噪输入 `fNoisyIn` 与滤波输出 `fFilteredOut`。导入与验证步骤见 [`examples/README.md`](examples/README.md)。

> 注意：例程的 `fSamplingRate` 取 1000，因此应把 `P_Demo_*` 放进**周期为 1 ms** 的任务调用，使采样率与调用频率一致，滤波特性才与设计值相符。

## 验证基线

- 双源核对：PDF（缓存 `TF3680_TC3_Filter_EN.pdf`，版本 1.8.0）＋ InfoSys（slug `tf3680_tc3_filter`，语言 1033），访问日期 2026-06-02。
- 15/15 文档 `verify_doc.py` 退出 0；15/15 例程 `lint_tcpou.py` 退出 0。
- ⚠️ 已知 PDF 文本瑕疵（已在对应文档点明，不影响正确性）：
  - `FB_FTR_Gaussian` / `FB_FTR_ActualValue` 的 `Configure` 示例把 `stConfig` 类型分别误印为 `ST_FTR_PT1` / `ST_FTR_Median`（复制粘贴遗留）；正确类型以 FB 定义与 InfoSys 为准。
  - `FB_FTR_LeadLag` / `FB_FTR_PT2oscillation` 的结构定义把 `TYPE` 头误印为 `ST_FTR_PT2`，但成员清单正确。
  - `FB_FTR_ActualValue.GetFilterActiveTimestamps` 的入参 `pFilterActiveTimestamps` 在签名里写 `POINTER TO BOOL`、在 Inputs 表/示例里写 `POINTER TO ULINT`；按语义应传 `ULINT` 时间戳数组。
