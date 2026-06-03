# FB_FTR_ActualValue

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Filter` |
| Library Version | `1.8.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF3680_TC3_Filter_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf3680_tc3_filter/11315822091.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_FTR_ActualValue.TcPOU`](../examples/P_Demo_FB_FTR_ActualValue.TcPOU) |

---

## 1. 功能简述

对一路测量输入做合理性检查（plausibility check）并滤波。若相邻两个采样值之差超过配置结构 `ST_FTR_ActualValue` 中指定的窗口 `fDeltaMax`，则当前输入被判为野值并最多抑制三个周期，其间输出由之前的输入值线性外推；若超限持续超过三个周期，输出重新跟随输入。

> 类别归属：测量值合理性检查（野值抑制）滤波器。属于 TF3680（TwinCAT 3 Filter）的数字滤波器函数块族，全族共用相同的『配置结构 + Configure/Call/Reset』接口范式。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION_BLOCK FB_FTR_ActualValue
VAR_INPUT
    stConfig        : ST_FTR_ActualValue;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `stConfig` | `ST_FTR_ActualValue` | 滤波器配置结构。承载该滤波器全部参数（见下方『配置结构』小节） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError          : BOOL;
    bConfigured     : BOOL;
    ipResultMessage : I_TCMessage;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bError` | `BOOL` | 出错时为 `TRUE`（多为配置非法或运行期数组/指针错误） |
| `bConfigured` | `BOOL` | 配置成功后为 `TRUE`；只有该位为 `TRUE` 时 `Call()`/`Reset()` 才可用 |
| `ipResultMessage` | `I_TCMessage` | 消息接口，提供查看错误/事件详情的属性和方法（对接 TwinCAT 3 EventLogger） |

### VAR_IN_OUT

无。

### 方法（METHOD）

本 FB 通过三个方法工作（`FB_FTR_ActualValue` 另有两个查询方法，见下）。其入参逐字照搬 PDF：

```iecst
METHOD Configure : BOOL   // 加载初始 / 新配置；返回 TRUE 表示配置成功
VAR_INPUT
    stConfig : ST_FTR_ActualValue;
END_VAR

METHOD Call : BOOL        // 按当前配置对输入信号算出输出信号；返回 TRUE 表示已计算
VAR_INPUT
    pIn        : POINTER TO LREAL;   // 输入数组地址（用 ADR(aInput)）
    nSizeIn    : UDINT;              // 输入数组字节长度（用 SIZEOF(aInput)）
    pOut       : POINTER TO LREAL;   // 输出数组地址
    nSizeOut   : UDINT;              // 输出数组字节长度
END_VAR

METHOD Reset : BOOL       // 复位内部历史状态，回到上次配置后的初始状态；返回 TRUE 表示成功
```

> **PDF 原文如实记录（含笔误）**：PDF §5.1.14.1 的 `Configure` 示例把入参类型印成了下面这样——这是从其它滤波器复制粘贴遗留的**错误**，正确类型应为 `ST_FTR_ActualValue`（与上面 FB 定义、InfoSys topic 页一致）。下面这段仅用于忠实呈现 PDF 文本，请勿照抄：

```iecst
METHOD Configure : BOOL
VAR_INPUT
    stConfig : ST_FTR_Median;   // ← PDF 笔误，应为 ST_FTR_ActualValue
END_VAR
```

另外两个查询方法（仅 `FB_FTR_ActualValue` 提供）：

```iecst
METHOD GetFilterActive : BOOL              // 回查上次 Call() 后哪些采样点被滤波器改写
VAR_INPUT
    pFilterActive        : POINTER TO BOOL;  // 结果数组地址（ARRAY ... OF BOOL）
    nSizeGetFilterActive : UDINT;            // 结果数组字节长度
END_VAR

METHOD GetFilterActiveTimestamps : BOOL    // 回查滤波器最近一次起作用的时间戳
VAR_INPUT
    pFilterActiveTimestamps     : POINTER TO BOOL;   // 结果数组地址（实际写入 ULINT 时间戳）
    nSizeFilterActiveTimestamps : UDINT;             // 结果数组字节长度
END_VAR
```

> ⚠️ PDF 中 `GetFilterActiveTimestamps` 的入参 `pFilterActiveTimestamps` 在方法签名里写作 `POINTER TO BOOL`，而其 Inputs 表与示例数组写作 `POINTER TO ULINT`（`ARRAY ... OF ULINT`，存放时间戳）。二者在 PDF 内不一致，本文如实保留 PDF 文本；按语义应传 `ULINT` 时间戳数组（以 InfoSys 为准）。

### 配置结构 `ST_FTR_ActualValue`（PDF §5.2.1.14）

滤波器的全部参数通过 `stConfig` 这一个入参传入。结构定义（逐字照搬 PDF）：

```iecst
TYPE ST_FTR_ActualValue :
STRUCT
    fDeltaMax : LREAL;
    nOversamples       : UDINT;
    nChannels          : UDINT;
    pInitialValues     : POINTER TO LREAL;
    nInitialValuesSize : UDINT;
END_STRUCT
END_TYPE
```

| 成员 | 类型 | 说明（中文） |
|---|---|---|
| `fDeltaMax` | `LREAL` | 相邻两个输入值之间允许的最大差值（必须大于等于 0）。超过则当前值被判为野值并抑制 |
| `fSamplingRate` | `LREAL` | 采样率 fs（单位 Hz，必须大于 0）。即调用 `Call()` 的频率，一般等于采集该信号的任务频率 |
| `nOversamples` | `UDINT` | 过采样数（必须大于 0）。每个通道、每次 `Call()` 调用所提交的采样点数 |
| `nChannels` | `UDINT` | 通道数（必须大于 0 且小于 101）。并行处理的信号通道数量 |
| `pInitialValues` | `POINTER TO LREAL` | 指向初始值数组的指针（可选）。用于预置滤波器历史状态、缩短建立时间；填 `0` 表示历史值全部清零 |
| `nInitialValuesSize` | `UDINT` | 初始值数组的字节长度（可选）。与 `pInitialValues` 配套，填 `0` 表示不使用初始值 |


> **关于 PDF 笔误**：PDF §5.1.14.1 的 Configure 示例把入参类型误写成 `stConfig : ST_FTR_Median`（系从其它滤波器复制粘贴遗留），FB 定义中的 `stConfig` 与 InfoSys topic 页均为正确的 `ST_FTR_ActualValue`——以 InfoSys 为准。

## 3. 行为说明

**配置 → 调用 → 复位三段式**：本 FB 不在每个周期『自动跑』，而是由调用方在每个采样周期主动调用 `Call()` 方法推进一步。典型生命周期分三步：

1. **配置（Configure）**：可以在声明时直接传入 `stConfig`（`fbFilter : FB_FTR_ActualValue(stConfig := stParams);`），也可以在运行时调用 `fbFilter.Configure(stConfig := stParams)` 初始化或重新配置。**未成功配置（`bConfigured = FALSE`）时 `Call()` 与 `Reset()` 不可用。**
2. **调用（Call）**：每个采样周期调一次 `fbFilter.Call(ADR(aIn), SIZEOF(aIn), ADR(aOut), SIZEOF(aOut))`，传入/传出的是 `ARRAY [1..nChannels] OF ARRAY [1..nOversamples] OF LREAL` 形式的数组（用指针 + 字节长度传递）。输入数组元素数必须等于 `nOversamples × nChannels`，输出数组不得小于输入数组。
3. **复位（Reset）**：调用 `fbFilter.Reset()` 把内部历史值 x[n-k]、y[n-k] 清零，使滤波器回到上次配置后的初始状态（消除过去输入的影响）。

判据：当 `|x[k] − x[k-1]| > fDeltaMax` 时计数器 n 自增，该次输入被抑制、输出改用线性外推；连续抑制最多 3 个周期，超过 3 个周期则认为这是真实变化而非野值，输出重新跟随输入（避免长期偏离真值）。本 FB 除标准的 `Configure`/`Call`/`Reset` 外，还提供两个查询方法：`GetFilterActive()` 返回上次 `Call()` 后哪些采样点被滤波器改写过（写入一个 `ARRAY ... OF BOOL`）；`GetFilterActiveTimestamps()` 返回滤波器最近一次起作用的时间戳（写入一个 `ARRAY ... OF ULINT`）。另有可写属性 `nTimestamp`（下次 `Call()` 中最旧输入值的时间戳）与 `tSamplePeriod : LTIME`（两个输入值间的时间差）。

**运行时重配**：要在运行中改参数，先改 `stParams` 的字段再调 `Configure`。若把结构里的 `bReset`（仅 IIRCoeff/IIRSos 有）设为 `FALSE`，重配时会保留历史状态、实现无扰切换。

**典型陷阱**：①忘了先 `Configure` 就 `Call`，会因 `bConfigured = FALSE` 失败（事件码 `16#3002`）；②`Call()` 的调用频率必须与 `fSamplingRate` 一致，否则滤波器的时间常数/截止频率与实际不符；③输入/输出数组维度与 `nOversamples × nChannels` 不匹配会报 `16#3004`/`16#3005`；④传 `ADR()` 前要保证数组实际存在（空指针报 `16#3006`/`16#3007`）。

## 4. 错误码 / 返回值

本库的功能块不通过返回值报错，而是通过 `bError`（出错置 `TRUE`）配合 `ipResultMessage`（`I_TCMessage` 接口，承载 TwinCAT 3 EventLogger 事件）给出详细原因。各方法（`Configure`/`Call`/`Reset`/…）的返回值都是 `BOOL`，`TRUE` 表示该次调用成功。配置/运行期常见事件码（`nEventId`，十六进制，来自 PDF §7.1 / 附录）：

| `nEventId` | 含义 | 处理建议 |
|---|---|---|
| 16#2003 | 配置错误：`fT1` 必须大于零 | 检查时间常数赋值 |
| 16#2004 | 配置错误：`fSamplingrate` 必须大于零 | 填入正确的采样率 |
| 16#2005 | 配置错误：`fCutoff` 必须大于 0 且小于 `fSamplingrate/2` | 调整截止频率到奈奎斯特频率以内 |
| 16#2006 | 配置错误：`fBandwidth` 必须大于 0 且小于 `fSamplingrate/2 - fCutoff` | 缩小带宽或调整截止频率 |
| 16#2009 | 配置错误：`nChannels` 必须大于 0 且小于 101 | 通道数取 1..100 |
| 16#200A | 配置错误：`nOversamples` 必须大于零 | 过采样数取正整数 |
| 16#200B | 配置错误：`nFilterOrder` 越界（带通/带阻 1..10，低通/高通 1..20） | 按类型选择合法阶数 |
| 16#2011 | 配置错误：`nSamplesToFilter` 必须大于零 | 窗口长度取正整数 |
| 16#201B | 配置错误：滤波器参数导致不稳定，请改用其它参数 | 检查自定义系数/极点是否在单位圆内 |
| 16#201E | 配置错误：`fNotchfrequency` 必须大于 0 且小于 `fSamplingrate/2` | 调整陷波频率 |
| 16#201F | 配置错误：`fQ` 必须大于零 | 品质因数取正 |
| 16#2020 | 配置错误：`fTheta` 必须大于零 | 阻尼系数取正 |
| 16#2021 | 配置错误：`fTt` 必须大于 0 且为 `1/fSamplingRate` 的整数倍 | 死区时间取采样周期整数倍 |
| 16#2022 | 配置错误：`fDeltaMax` 必须大于等于零 | 野值窗口取非负 |
| 16#3002 | 运行错误：缺少配置（未调用 `Configure` 就调 `Call`） | 先成功配置再调用 `Call` |
| 16#3004 | 运行错误：`fIn` 数组大小与 `nOversamples*nChannels` 不符 | 核对输入数组维度 |
| 16#3005 | 运行错误：`fOut` 数组不能小于 `fIn` 数组 | 放大输出数组 |
| 16#3006 | 运行错误：`pIn` 为空指针 | 检查 `ADR(...)` 是否传了有效数组 |
| 16#3007 | 运行错误：`pOut` 为空指针 | 检查输出数组地址 |

> 完整事件码表见 PDF §7.1（附录 Return codes）。错误发生时可通过 `ipResultMessage`（`I_TCMessage`）读取事件文本，或在 TwinCAT 3 EventLogger 在线窗口查看。各方法的 `BOOL` 返回值：`TRUE` = 本次调用成功，`FALSE` = 失败（此时查 `bError` 与 `ipResultMessage`）。

## 5. 使用注意 / 常见坑

- **先配置后调用**：`bConfigured` 为 `TRUE` 才能 `Call()`/`Reset()`；声明时用 `fbFilter : FB_FTR_ActualValue(stConfig := stParams);` 可在初始化阶段直接配好。
- **`Call()` 频率 = `fSamplingRate`**：滤波器的时间常数、截止频率都是相对采样率定义的。务必让调用本 FB 的任务周期与 `fSamplingRate` 一致，否则实际滤波特性会偏离设计值。（工程经验补充）
- **数组用指针 + 字节长度传递**：`Call(ADR(aIn), SIZEOF(aIn), ADR(aOut), SIZEOF(aOut))`，数组形状为 `ARRAY [1..nChannels] OF ARRAY [1..nOversamples] OF LREAL`；元素数须等于 `nOversamples × nChannels`。
- **单通道也要用数组**：即使 `nChannels = 1`、`nOversamples = 1`，`Call()` 的输入/输出仍是数组（一维一元素即可），不能直接传标量。（工程经验补充）
- **复位 vs 重配**：`Reset()` 只清历史状态、保留参数；`Configure()` 换参数。需要无扰换参时优先用支持 `bReset := FALSE` 的结构。
- **稳定性自负**：仅对 `FB_FTR_IIRCoeff`/`FB_FTR_IIRSos`——自定义系数可能让 IIR 失稳，库会在明显非法时报 `16#201B`，但并不能保证所有系数组合都被拦截。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_FTR_ActualValue.TcPOU`](../examples/P_Demo_FB_FTR_ActualValue.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：一路 4-20 mA 压力变送器偶发电气尖峰（瞬时跳到满量程），用本 FB 设 `fDeltaMax` 为合理的单周期最大变化量，把这种跳变在 1-3 个周期内用外推值顶住，等确认是持续变化再放行，避免误触发联锁。
//   本 demo 用一个合成信号（正弦基波 + 周期性尖峰扰动）喂给 FB_FTR_ActualValue，
//   在线观察 fFilteredOut 如何平滑/跟随 fNoisyIn。
// 价值：把『野值检测 + 短时外推 + 超时放行』这套逻辑封装好，并能用 `GetFilterActive()` 回查到底哪些点被改写过，便于诊断。比单纯限幅更智能（限幅会一直钳住真实大变化，本 FB 超 3 周期就放行）。
// 验证步骤：
//   1. 右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选本 .TcPOU 文件
//   2. 引用 Tc2_Filter（References → Add library），并把本 PROGRAM 加入一个 1ms 任务
//      （fSamplingRate 取 1000，故任务周期应为 1ms，使采样率与调用频率一致）
//   3. 编译 → 登录 → 运行
//   4. 在线 monitor 同时看 fNoisyIn（带噪输入）与 fFilteredOut（滤波输出）：
//      - bConfigured 上电后应为 TRUE（声明时已配置）
//      - fFilteredOut 应是 fNoisyIn 的平滑/相位校正版本（尖峰被削弱、毛刺变平）
//   5. 在线把 bInjectSpike 写 TRUE，给 fNoisyIn 叠加阶跃式尖峰扰动，
//      观察 fFilteredOut 不会立刻跟随尖峰、而是被滤波器抑制后缓慢响应
//      （验证『滤波器真的在做事』，而不只是把输入原样透传）
VAR
    fbFilter      : FB_FTR_ActualValue;                  // 被演示的滤波器实例
    stParams      : ST_FTR_ActualValue := (fDeltaMax := 5.0, nOversamples := 1, nChannels := 1);
    // Call() 用指针 + 字节长度传数组；单通道单过采样 → 1x1 数组
    aIn           : ARRAY [1..1] OF ARRAY [1..1] OF LREAL;  // 输入缓冲
    aOut          : ARRAY [1..1] OF ARRAY [1..1] OF LREAL;  // 输出缓冲
    fNoisyIn      : LREAL;                    // 在线 monitor：合成的带噪输入
    fFilteredOut  : LREAL;                    // 在线 monitor：滤波后输出
    bInjectSpike  : BOOL := FALSE;            // 在线写 TRUE 注入尖峰扰动
    bConfigured   : BOOL;                     // 配置状态（应为 TRUE）
    bCallOk       : BOOL;                     // Call() 返回值
    nPhase        : UDINT;                    // 正弦相位计数（0..999，每周期 1000 点）
    fSig          : LREAL;                    // 临时：基波正弦值
END_VAR

// ---- 1) 合成一个『正弦基波 + 可选尖峰』的测试信号 ----
// 基波：幅值 10、频率 = fSamplingRate/1000 = 1 Hz（每 1000 个 1ms 周期一圈）
nPhase := (nPhase + 1) MOD 1000;
fSig := 10.0 * SIN(6.2831853 * UDINT_TO_LREAL(nPhase) / 1000.0);

// 周期性尖峰扰动：相位 500 处叠加一个大幅值脉冲，模拟野值/噪声
IF bInjectSpike AND (nPhase = 500) THEN
    fNoisyIn := fSig + 50.0;          // 突然蹦出的尖峰
ELSE
    fNoisyIn := fSig;
END_IF

// ---- 2) 把带噪输入送入滤波器，取出平滑输出 ----
aIn[1][1]    := fNoisyIn;
bCallOk      := fbFilter.Call(ADR(aIn), SIZEOF(aIn), ADR(aOut), SIZEOF(aOut));
fFilteredOut := aOut[1][1];

// 读配置状态（声明时已用 stConfig 配置，正常应为 TRUE）
bConfigured := fbFilter.bConfigured;
```

## 7. 业务场景与实际价值

- **场景**：一路 4-20 mA 压力变送器偶发电气尖峰（瞬时跳到满量程），用本 FB 设 `fDeltaMax` 为合理的单周期最大变化量，把这种跳变在 1-3 个周期内用外推值顶住，等确认是持续变化再放行，避免误触发联锁。
- **价值**：把『野值检测 + 短时外推 + 超时放行』这套逻辑封装好，并能用 `GetFilterActive()` 回查到底哪些点被改写过，便于诊断。比单纯限幅更智能（限幅会一直钳住真实大变化，本 FB 超 3 周期就放行）。
- **替代方案对比**：自己写『差值判超限 + 计数 + 外推』：逻辑零碎易错且无法回查被改写点；中值滤波只能剔除离群点、不会外推也不告诉你哪些点被动过。

## 8. 参考资料

- **PDF**：[TF3680_TC3_Filter_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF3680_TC3_Filter_EN.pdf) §5.1.14（功能块）、§5.2.1.14（配置结构）、§4.1-4.2（数字滤波器原理与参数化）、§7.1（错误码）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf3680_tc3_filter/11315822091.html
- **相关 FB**：同库 `FB_FTR_*` 滤波器族；上下游常配 `Tc2_Standard` 信号发生、`Tc3_EventLogger`（读 `ipResultMessage`）
