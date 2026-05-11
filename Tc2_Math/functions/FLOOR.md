# FLOOR

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Math` |
| Library Version | `1.3.3` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/68441739.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FLOOR.xml`](../examples/P_Demo_FLOOR.xml) |

---

## 1. 功能简述

向下取整函数。给一个 `LREAL` 浮点数 `lr_in`，返回**不大于** `lr_in` 的最大整数（数值上向 `-∞` 方向取），结果仍是 `LREAL` 类型，不受 `INT` / `DINT` 数值范围限制。

数学定义：`FLOOR(x) = ⌊x⌋ = max { n ∈ ℤ | n ≤ x }`。正数侧符合"丢掉小数"直觉（`FLOOR(2.8) = 2`）；**负数侧朝 `-∞`**，结果绝对值变大（`FLOOR(-2.8) = -3`），这是与 `LTRUNC`（朝零截断）在负数侧的根本区别。

与 IEC 标准 `TRUNC` 相比，本函数返回 `LREAL` 而非 `DINT`，对很大或很小的浮点数（绝对值超 `2³¹`）也能正确给出整数化结果而不溢出。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FLOOR : LREAL
VAR_INPUT
    lr_in : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `lr_in` | `LREAL` | 待向下取整的 64 位双精度浮点输入值 |

### 返回值

| 类型 | 说明 |
|---|---|
| `LREAL` | 不大于 `lr_in` 的最大整数值（以 `LREAL` 表示）。例：`FLOOR(2.8) = 2.0`，`FLOOR(-2.8) = -3.0`，`FLOOR(0.0) = 0.0` |

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

### VAR_IN_OUT

无。

## 3. 行为说明

**算法语义**：本函数对输入做"朝 `-∞` 方向取整"运算，等价于数学库的 `floor()`。PDF §3.2 原表（搬运）：

| `x` | `0` | `0.4` | `0.5` | `0.6` | `1.4` | `1.5` | `1.6` | `-0.4` | `-0.5` | `-1.4` | `-1.5` | `-1.78` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `FLOOR(x)` | `0` | `0` | `0` | `0` | `1` | `1` | `1` | `-1` | `-1` | `-2` | `-2` | `-2` |

**与三个兄弟函数的关系**：

- **`CEIL(x)`**：朝 `+∞` 取整；与 `FLOOR` 互为镜像。`x` 不是整数时 `CEIL(x) - FLOOR(x) = 1`，是整数时 `CEIL(x) = FLOOR(x) = x`
- **`LTRUNC(x)`**：朝 `0` 截断小数；正数与 `FLOOR` 同，负数与 `CEIL` 同
- **`TO_LINT(x)`**：四舍五入

**小数位截取技巧**（PDF §3.2 提供）：保留 `k` 位小数向下取，写 `FLOOR(x * POWER(10,k)) / POWER(10,k)`。同样存在二进制浮点表示误差（如 `0.1 ≠` 精确 `0.1`），HMI 显示需用格式化函数而非直接拼字符串。

**边界**：`lr_in` 已经是整数值（如 `5.0`）时 `FLOOR(5.0) = 5.0`，不会"再向下跳一格"。`NaN` / `±Inf` 行为 PDF 未明确定义，⚠️ 不可依赖。

**典型工程应用**：把连续位置量化到栅格（数控分度盘、像素坐标）；时间戳按整秒对齐；把 `LREAL` 价格丢掉分位（`FLOOR(price * 100) / 100` 保留 2 位小数）。

## 4. 错误码 / 返回值

本函数返回类型为 `LREAL`，无错误码、无 `bError` 输出、无 `HRESULT`。返回值语义见 §2「返回值」表。

PDF / InfoSys 均未规定 `NaN` / `±Inf` 等特殊输入的行为，需调用方保证输入合法。

## 5. 使用注意 / 常见坑

- **负数侧朝 `-∞` 不是朝 `0`**：`FLOOR(-2.3) = -3`（绝对值变大）。要"截断小数"语义应改用 `LTRUNC`。把它当 `LTRUNC` 用是新手最常踩的坑。
- **返回 `LREAL` 不是 `LINT`**：用作数组下标 / `FOR` 循环计数器时需 `LREAL_TO_DINT(FLOOR(x))`。直接使用编译器会报隐式类型转换警告。
- **大数精度衰减**：`|lr_in| > 2^53 ≈ 9.0e15` 时浮点表示间距 ≥ 1，`FLOOR` 与原值无差异；此时应改用 `LINT` 整数 `DIV`。
- **小数位截取的浮点误差**：`FLOOR(0.3 * 10) / 10` 不保证等于 `0.3`，可能 `0.29999...`。如果业务依赖精确小数（货币），最好用 `LINT` 整分计算后再除显示。（工程经验补充）
- **不要用作四舍五入**：`FLOOR(x + 0.5)` 在负数侧不对称（`FLOOR(-1.5 + 0.5) = -1`，但 `FLOOR(1.5 + 0.5) = 2`）；正确的四舍五入用 IEC `TO_LINT` / `LREAL_TO_LINT`。（工程经验补充）
- **与 IEC `TRUNC` 的区别**：标准 `TRUNC` 返回 `DINT`，输入 `1e10` 会溢出；`FLOOR` 返回 `LREAL`，无溢出但需要后续显式转 `DINT`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FLOOR.xml`](../examples/P_Demo_FLOOR.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：包装线对计件流量计读数做"整箱包装"判定——每 12 个为一箱。
//       已知本班次累计件数 lrAccumulatedPieces（LREAL，因温度补偿可能有小数），
//       要算出已完成的整箱数，触发下一箱包装单生成。
//
// 价值：FLOOR 一行表达"丢掉零头"，配合除法直接给出整箱数。
//       负数侧：退货抵扣时 FLOOR(-13.5/12) = -2（朝 -∞，绝对值偏大）。
//
// 验证：在线写 lrAccumulatedPieces = 35.7 → nCompleteBoxes = 2（35.7/12 = 2.97）；
//       写 36.0 → 3；写 47.99 → 3；写 -13.5 → -2（验证负数朝 -∞）。
PROGRAM P_Demo_FLOOR
VAR
    lrAccumulatedPieces : LREAL := 35.7;   // 在线写值模拟累计件数
    lrBoxesAsReal       : LREAL;            // FLOOR 中间结果
    nCompleteBoxes      : DINT;             // 最终送给 MES 的整箱数
END_VAR

// 单行调用：FLOOR 朝 -∞ 取整；35.7/12 = 2.975 → FLOOR = 2.0
lrBoxesAsReal := FLOOR(lrAccumulatedPieces / 12.0);

// 显式 LREAL → DINT，避免编译器隐式转换警告
nCompleteBoxes := LREAL_TO_DINT(lrBoxesAsReal);
```

## 7. 业务场景与实际价值

- **场景**：量化到固定栅格 / 整数倍计件 / 时间戳整秒对齐 / 像素坐标量化。典型工业例：包装线"每 N 个一箱"统计；CNC 圆周分度（`FLOOR(angle / 1.8) * 1.8` 把角度对齐到最近的较小 `1.8°` 倍）；时序记录"按整分钟分桶"。
- **价值**：替代手写"正负数分支 + 减去小数部分"逻辑，一行可靠。配合除法可做向下整数除法，避免 `LREAL DIV LREAL` 的精度问题。
- **替代方案对比**：
  - 用 `LTRUNC`：正数等价、负数语义不同（朝零截断）；切勿混用
  - 用 IEC `TRUNC`：返回 `DINT`，输入 `1e12` 直接溢出
  - 用 `LREAL_TO_DINT`：那是四舍五入而不是向下取
  - 自己写"`LTRUNC(x) - (1 if FRAC(x) < 0 else 0)`"等效式：能模拟但 5 行替代 1 行，易错
  - **本函数**：单语义、`LREAL` 入 `LREAL` 出，与数学 `floor()` 完全一致

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf) §3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/68441739.html
- **相关函数**：`CEIL`（向上取整）、`LTRUNC`（朝零截断）、`FRAC`（取小数部分）、IEC `TRUNC` / `TO_LINT`（标准库的取整 / 四舍五入）
