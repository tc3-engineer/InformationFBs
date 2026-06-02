# FRAC

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Math` |
| Library Version | `1.3.3` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/68443275.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FRAC.TcPOU`](../examples/P_Demo_FRAC.TcPOU) |

---

## 1. 功能简述

取小数部分函数。给一个 `LREAL` 浮点数 `lr_in`，返回它的"小数部分"：等价于 `lr_in - LTRUNC(lr_in)`，结果在 `(-1.0, 1.0)` 开区间内。

数学上：正数侧 `FRAC(2.8) = 0.8`，负数侧 `FRAC(-2.8) = -0.8`，结果**保留原符号**（与 `MOD` 取余的"被除数符号"行为一致）。

典型用途是配合 `LTRUNC` / `FLOOR` 实现"整数 + 小数"拆分（如把 LREAL 时间戳拆为整秒 + 纳秒部分），或者判断"有没有零头"（`FRAC(x) <> 0` 表示 `x` 不是整数值）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FRAC : LREAL
VAR_INPUT
    lr_in : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `lr_in` | `LREAL` | 待取小数部分的 64 位双精度浮点输入值 |

### 返回值

| 类型 | 说明 |
|---|---|
| `LREAL` | `lr_in` 的小数部分（带原符号），范围 `(-1.0, 1.0)`。例：`FRAC(2.8) = 0.8`，`FRAC(-2.8) = -0.8`，`FRAC(5.0) = 0.0` |

### VAR_OUTPUT

无（本符号是 `FUNCTION`）。

### VAR_IN_OUT

无。

## 3. 行为说明

**算法语义**：`FRAC(x) = x - LTRUNC(x)`，即先朝零截断得到整数部分，再用原值减去得到小数部分。这是与多数 C 标准库 `modf()` 一致的行为。

| `x` | `2.8` | `-2.8` | `0.0` | `5.0` | `-5.0` | `0.5` | `-0.1` | `100.25` |
|---|---|---|---|---|---|---|---|---|
| `FRAC(x)` | `0.8` | `-0.8` | `0.0` | `0.0` | `0.0` | `0.5` | `-0.1` | `0.25` |

**符号保留语义**：与 `FLOOR` / `CEIL` 不同，`FRAC` 不"统一往一个方向走"。`FRAC(-2.8)` 给的是 `-0.8`，不是 `0.2`。这意味着：

- 想要"距离最近的较小整数的差距"（数学上更常用，配合 `FLOOR`）应该写 `x - FLOOR(x)`，结果总是 `[0.0, 1.0)`
- 想要"被除数符号的小数余量"，本函数直接给

**浮点精度限制**（重要）：`FRAC(1234567890.123)` 由于 `LREAL` 尾数 52 位的限制，整数部分占用了大部分有效位，小数部分精度会衰减到约 6-7 位有效位。`|x| > 2^53 ≈ 9e15` 时 `FRAC` 一律返回 `0.0`（输入已经无小数表示能力）。

**与 IEC 库 `MOD` 的关系**：本函数等价于 `MOD(lr_in, 1.0)` 在 IEEE 754 语义下，但 IEC `MOD` 不接 `LREAL`、得用 `LMOD`，所以 `FRAC(x) ≡ LMOD(x, 1.0)`。

**与 `MODTURNS` 配合**：`MODTURNS(x, m) * m + LMOD(x, m) ≡ x`；`FRAC(x) + LTRUNC(x) ≡ x`（在 LREAL 精度范围内）。

## 4. 错误码 / 返回值

本函数返回类型为 `LREAL`，无错误码、无 `bError` 输出、无 `HRESULT`。返回值语义见 §2「返回值」表。

PDF / InfoSys 均未规定 `NaN` / `±Inf` 等特殊输入的行为，需调用方保证输入合法。

## 5. 使用注意 / 常见坑

- **负数侧小数带符号**：`FRAC(-2.8) = -0.8`（不是 `+0.2`）。判断"有没有零头"用 `ABS(FRAC(x)) > eps` 而不是 `FRAC(x) > eps`，否则负数全部漏判。
- **不要直接用 `=` 比较小数部分**：`FRAC(0.1 + 0.2)` 可能是 `0.30000000000000004`，与 `0.3` 不相等。比较小数零头用容差：`ABS(FRAC(x)) < 1.0e-9` 才视为"整数"。
- **大数失精**：`FRAC(1e16) = 0.0`，并不代表 `1e16` 是整数，只是 `LREAL` 在这个量级已无小数表示能力。需要保留小数信息的大数算法应预先把整数部分剥离再算。
- **`FRAC(x) ≠ MOD(x, 1)` 仅在符号约定上不同的语言**：在 TwinCAT 这两者结果一致（都跟被除数符号）。从 Python（`math.fmod` vs `%`）等迁移代码时要注意。（工程经验补充）
- **不可作为周期取余的通用方案**：要"角度归一到 0..360"应该用 `MODABS`，要"信号采样在一个周期内的相位"应该用 `LMOD`。`FRAC` 只是 `LMOD(x, 1.0)` 的特化版本。
- **`FRAC(x)` 仅在 `x` 严格整数（如 `5.0` 由 `LREAL_TO_LREAL(5)` 得来）时严格返回 `0.0`**：经过浮点运算（`0.1 * 50.0`）的"看起来整数"结果可能给非零小数残差。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FRAC.TcPOU`](../examples/P_Demo_FRAC.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：高精度时间戳处理——上位机送下来一个 LREAL 秒数 lrUnixTimeSec（如
//       1715433600.123456789），要拆成"整秒"+"纳秒部分"两份存档：整秒做
//       MES 主键，纳秒部分给质量分析做时序对齐。
//
// 价值：FRAC 一行给出小数部分；再乘 1e9 转纳秒。整套拆分逻辑 2 行就够。
//
// 验证：在线写 lrUnixTimeSec = 1715433600.5 → lrFractionalSec = 0.5、
//       nNanosecondPart = 500_000_000；改 1715433600.0 → 0.0、0；
//       改 -1.25 → -0.25、-250_000_000（验证符号保留）。
PROGRAM P_Demo_FRAC
VAR
    lrUnixTimeSec      : LREAL := 1715433600.5;   // 在线写值模拟外部时间戳
    lrFractionalSec    : LREAL;                    // FRAC 输出
    lrIntegerSec       : LREAL;                    // LTRUNC 输出，演示两者互补
    nNanosecondPart    : DINT;                     // 小数 × 1e9 转纳秒
END_VAR

// 单行调用：FRAC 取带符号的小数部分；LTRUNC 取朝零截断的整数部分
lrFractionalSec := FRAC(lrUnixTimeSec);
lrIntegerSec   := LTRUNC(lrUnixTimeSec);

// 把秒的小数部分转换成纳秒（× 1_000_000_000）
// 注：此处 LREAL 精度限制使得当 lrUnixTimeSec 整数部分 > 2^53 时
//     小数部分会失精；典型 Unix 时间戳（约 1.7e9）远未触发，安全
nNanosecondPart := LREAL_TO_DINT(lrFractionalSec * 1.0E9);
```

## 7. 业务场景与实际价值

- **场景**：拆分浮点为整数 + 小数（时间戳秒/纳秒、米/毫米、度/角分）、判断量是否"刚好整数"、模 1 取相位（信号采样落在 `[0,1)` 周期内的位置）。
- **价值**：替代两步 `LTRUNC(x); x - LTRUNC(x)`，一行完成；与 `LTRUNC` / `FLOOR` 构成完整的"整数 + 小数"拆分对。
- **替代方案对比**：
  - 自己写 `x - LTRUNC(x)`：两次调用，可读性低
  - 用 `LMOD(x, 1.0)`：等价但语义不直观（程序员看到 `MOD 1.0` 不会立刻想到"取小数"）
  - 用 `LREAL_TO_LINT` 取整再相减：四舍五入而非截断，行为不同
  - **本函数**：单语义、`LREAL` 入 `LREAL` 出，与 C `modf()` 一致

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf) §3.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/68443275.html
- **相关函数**：`LTRUNC`（取整数部分，与本函数互补）、`LMOD`（一般化的浮点取余）、`FLOOR` / `CEIL`（朝定向取整）
