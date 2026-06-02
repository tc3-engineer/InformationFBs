# LMOD

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Math` |
| Library Version | `1.3.3` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/68444811.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_LMOD.TcPOU`](../examples/P_Demo_LMOD.TcPOU) |

---

## 1. 功能简述

带符号的浮点模运算（modulo division）。给定被除数 `lr_Value` 与模数 `lr_Arg`，返回 `lr_Value` 除以 `lr_Arg` 的"带符号余数"，结果保留 `lr_Value` 的符号。

数学上：`LMOD(v, m) = v - LTRUNC(v / m) * m`。例：`LMOD(400.56, 360) = 40.56`，`LMOD(-400.56, 360) = -40.56`（负被除数给负余数）。

与 IEC 标准 `MOD` 的关键区别：`MOD` 只接整数，而本函数接 `LREAL` 并能返回**非整数余数**。这正是它存在的理由——伺服轴的角度位置、信号采样的连续相位等都是浮点量。在 NC 轴语境下若需要"无符号 0..360 模值"应改用 `MODABS`。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LMOD : LREAL
VAR_INPUT
    lr_Value : LREAL;
    lr_Arg   : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `lr_Value` | `LREAL` | 被除数（输入值） |
| `lr_Arg` | `LREAL` | 模数范围（modulo range，通常为正数，如 `360.0`） |

### 返回值

| 类型 | 说明 |
|---|---|
| `LREAL` | 带符号余数，范围 `(-|lr_Arg|, +|lr_Arg|)`。符号跟随 `lr_Value`。例：`LMOD(400.56, 360) = 40.56`，`LMOD(-400.56, 360) = -40.56` |

### VAR_OUTPUT

无（本符号是 `FUNCTION`）。

### VAR_IN_OUT

无。

## 3. 行为说明

**算法语义**：`LMOD(v, m) = v - LTRUNC(v / m) * m`，即朝零截断商，再用 `余数 = 被除数 - 商 * 除数`。这是 C/C++ `fmod()` 的行为，也是 IEEE 754 `MOD` 的语义。

**取值表**：

| `(v, m)` | `LMOD(v, m)` | 说明 |
|---|---|---|
| `(400.56, 360.0)` | `40.56` | 正侧基本例 |
| `(-400.56, 360.0)` | `-40.56` | 负被除数 → 负余数 |
| `(0.0, 360.0)` | `0.0` | 零特例 |
| `(360.0, 360.0)` | `0.0` | 整模值 → 零 |
| `(720.7, 360.0)` | `0.7` | 多圈 |
| `(-720.7, 360.0)` | `-0.7` | 多圈反向 |

**与 `MODABS` 的对照**（同输入对比）：

| `v` | `LMOD(v, 360)` | `MODABS(v, 360)` |
|---|---|---|
| `400.56` | `40.56` | `40.56` |
| `-400.56` | `-40.56` | `319.44` |
| `-0.5` | `-0.5` | `359.5` |

—— **正被除数两者一致；负被除数 LMOD 给负、MODABS 给正**。NC 轴语境一般用 `MODABS`，控制理论 / 信号处理一般用 `LMOD`。

**与 `MOD` (IEC) 的区别**：

- IEC `MOD` 只接整数 `(DINT, DINT)`；输入浮点会编译失败
- `LMOD` 接 `(LREAL, LREAL)`，余数可以是 `0.56` 这样的非整数

**边界**：

- `lr_Arg = 0.0` 会除零，PDF / InfoSys 未规定行为；运行时通常返回 `NaN`（IEEE 754 浮点除零规则）。**必须由调用方保证模数非零**
- `lr_Arg` 为负数（如 `-360`）时行为 PDF 也未明说；按 `fmod` 标准结果符号还是跟 `lr_Value`，但工程上极不常见，⚠️ 建议总是传正模数

**精度**：当 `|lr_Value|` 远大于 `|lr_Arg|`（如 `LMOD(1e10, 0.1)`）时，浮点除法的低位精度损失会让余数与真实数学值差出几个 `ULP`（最低有效位）。在累加角度等场景需周期性归一化避免误差累积。

## 4. 错误码 / 返回值

本函数返回类型为 `LREAL`，无错误码、无 `bError` 输出、无 `HRESULT`。返回值语义见 §2「返回值」表。

特殊输入：

- `lr_Arg = 0.0`：除零，PDF 未明说，⚠️ 实测结果可能为 `NaN` 或 `±Inf`，业务侧需先判 `lr_Arg <> 0`
- `lr_Value = NaN` / `±Inf`：行为 PDF 未明说，⚠️ 不可依赖
- 大数：`|lr_Value| > 2^53` 时 `LREAL` 精度衰减，结果可能与数学预期偏离

## 5. 使用注意 / 常见坑

- **负被除数给负余数**：`LMOD(-1.0, 360.0) = -1.0`，不是 `359.0`。绝大多数 NC 轴/角度业务想要的是 `359.0`——那就该用 `MODABS`。把 LMOD 当 MODABS 用导致角度跳变是常见 bug。
- **不可作为"周期取整"用**：`LMOD` 给的是"被除数 - 朝零商 * 模数"。要"被除数 - 朝负无穷商 * 模数"（数学上的 modulo）需自己写 `LMOD(LMOD(v, m) + m, m)` 把负余数翻正，或直接用 `MODABS`。
- **模数为 0 必须先检查**：`LMOD(x, 0)` 触发浮点除零，给 `NaN`，后续 `LREAL_TO_DINT(NaN)` 会引发浮点异常。
- **累加场景需周期归一**：`v := v + step;  v := LMOD(v, period);` 每周期都归一化能保证 `v` 不越界；如果一直 `v := v + step` 不归一，几个月后 `v` 累加到 `1e10` 量级才归一，精度已损失到无法接受。（工程经验补充）
- **浮点精度限制**：`LMOD(1.0e10, 0.1)` 由于 `0.1` 不能精确二进制表示，结果与数学预期可能偏 `1e-7` 量级。需要精确模运算应改用整数缩放（`LREAL_TO_LINT(v * 1e6) MOD LREAL_TO_LINT(m * 1e6)` 再 `/ 1e6`）。
- **不是数学家眼里的 mod**：数学定义"`a mod m` 总是 `[0, m)`"——本函数不是。需要数学 mod 用 `MODABS`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LMOD.TcPOU`](../examples/P_Demo_LMOD.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：振动信号分析——一个连续运行的正弦激励器累计相位角 lrAccumulatedPhaseDeg
//       会随时间一直增长（300、600、900…度），FFT 前需要把它归一到一圈以内
//       便于落入查表区间 [0, 360) 或 (-180, 180]。控制理论里更喜欢 (-180,180]，
//       恰好就是 LMOD 在传 360 模数时的输出（保留符号）。
//
// 价值：LMOD 一行做带符号模运算；配合 IF 把 (-360, 360) 映射到 (-180, 180]
//       只需再 2 行。如果是 NC 轴想要 [0, 360) 改用 MODABS 即可。
//
// 验证：在线写 lrAccumulatedPhaseDeg = 400.56 → lrPhaseInOneTurnDeg = 40.56；
//       写 -400.56 → -40.56（验证负被除数给负余数）；
//       写 0 → 0；写 720 → 0；写 720.5 → 0.5。
PROGRAM P_Demo_LMOD
VAR
    lrAccumulatedPhaseDeg : LREAL := 400.56;   // 在线写值模拟累计相位
    lrTurnSizeDeg         : LREAL := 360.0;    // 一圈大小
    lrPhaseInOneTurnDeg   : LREAL;             // LMOD 输出：带符号余数
END_VAR

// 单行调用：LMOD 带符号取余；符号跟随被除数
lrPhaseInOneTurnDeg := LMOD(lrAccumulatedPhaseDeg, lrTurnSizeDeg);
```

## 7. 业务场景与实际价值

- **场景**：信号处理的相位归一化、控制理论中"角度归到 ±180" 的场景、累计计数器周期回绕。典型用例：FFT 输入前的连续相位归一、PID 控制器对角度 setpoint 取差时避免跳变（差值取 `LMOD` 后落入 `[-180, 180]` 比 `[0, 360]` 更接近真实最短路径）。
- **价值**：替代手写 `v - LTRUNC(v/m) * m`，避免重复计算 `v/m`；与 `MODABS` 共同覆盖"带符号"与"无符号"两种工程语义。
- **替代方案对比**：
  - IEC `MOD`：只接整数；浮点直接编译报错
  - 自己写 `v - LTRUNC(v/m) * m`：等价但 3 次浮点运算且易输入错
  - `MODABS`：无符号版本，业务语义不同
  - **本函数**：单调用、`LREAL` 输入输出、与 `fmod()` 一致，可移植到其他语言代码

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf) §3.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/68444811.html
- **相关函数**：`MODABS`（无符号模值，0..m）、`MODTURNS`（模运算的整数商部分）、IEC `MOD`（整数取余）
