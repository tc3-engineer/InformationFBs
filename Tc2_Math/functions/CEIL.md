# CEIL

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Math` |
| Library Version | `1.3.3` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/17640900235.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_CEIL.TcPOU`](../examples/P_Demo_CEIL.TcPOU) |

---

## 1. 功能简述

向上取整函数。给一个 `LREAL` 浮点数 `lr_in`，返回**不小于** `lr_in` 的最小整数（数值上向 `+∞` 方向取），结果仍是 `LREAL` 类型，因此不受 `INT` / `DINT` 数值范围限制（可正确处理超出 `2³¹` 的大数）。

数学定义：`CEIL(x) = ⌈x⌉ = min { n ∈ ℤ | n ≥ x }`。正数侧符合直觉（`CEIL(2.8) = 3`）；**负数侧也是朝 `+∞`**，即朝零方向取整（`CEIL(-2.8) = -2` 而不是 `-3`），这与 `LTRUNC` 的"朝零截断"在**正数侧结果一致、负数侧结果不同**。

与 IEC 标准的 `TRUNC` 相比，本函数返回的是 `LREAL` 类型整数值而非 `DINT`，避免了"对非常大的浮点数 `TRUNC` 出现 `DINT` 截断溢出"这一陷阱。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION CEIL : LREAL
VAR_INPUT
    lr_in : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `lr_in` | `LREAL` | 待向上取整的 64 位双精度浮点输入值 |

### 返回值

| 类型 | 说明 |
|---|---|
| `LREAL` | 不小于 `lr_in` 的最小整数值（以 `LREAL` 表示）。例：`CEIL(2.8) = 3.0`，`CEIL(-2.8) = -2.0`，`CEIL(0.0) = 0.0` |

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

### VAR_IN_OUT

无。

## 3. 行为说明

**算法语义**：本函数对输入做"朝 `+∞` 方向取整"运算，等价于 IEC 1131-3 标准里 `EXPT` / 数学库常见的 `ceil()`。对常见输入的取值表如下（PDF §3.1 原表搬运）：

| `x` | `0` | `0.4` | `0.5` | `0.6` | `1.4` | `1.5` | `1.6` | `-0.4` | `-0.5` | `-1.4` | `-1.5` | `-1.78` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `CEIL(x)` | `0` | `1` | `1` | `1` | `2` | `2` | `2` | `0` | `0` | `-1` | `-1` | `-1` |

**与三个兄弟函数的关系**：

- **`FLOOR(x)`**：朝 `-∞` 方向取整；`FLOOR(2.8) = 2`，`FLOOR(-2.8) = -3`
- **`LTRUNC(x)`**：朝 `0` 方向取整（截断小数）；`LTRUNC(2.8) = 2`，`LTRUNC(-2.8) = -2`
- **`TO_LINT(x)`**：四舍五入到最近整数（`0.5` 进位）

由此 `CEIL` 与 `LTRUNC` 在正数侧结果相同、在负数侧 `CEIL` 比 `LTRUNC` 高 0 或 1。

**小数位截取技巧**（PDF §3.1 提供）：要保留 1 位小数向上取，写 `CEIL(x * 10) / 10`；要保留 2 位小数则 `CEIL(x * 100) / 100`。注意此处的 `* 10` / `/ 10` 会引入浮点二进制表示误差（如 `0.1` 不能精确表示），结果可能有 `1e-16` 量级的尾差，业务侧再做对比时不能直接 `=`，应当 `ABS(a-b) < eps` 容差比较。

**边界**：`lr_in` 已经是整数值（如 `2.0`）时，`CEIL(2.0) = 2.0`，不会"再向上跳一格"——这与 ANSI C 的 `ceil()` 一致。`NaN`、`±Inf` 行为 PDF 未明确规定，⚠️ 不可依赖。

## 4. 错误码 / 返回值

本函数返回类型为 `LREAL`，无错误码、无 `bError` 输出、无 `HRESULT`。返回值的语义见 §2「返回值」表。

PDF / InfoSys 均未规定特殊输入（`NaN` / `±Inf` / 极大值近 `LREAL` 边界 `±1.8e308`）下的行为，需调用方自己保证输入合法。

## 5. 使用注意 / 常见坑

- **负数侧反直觉**：`CEIL(-2.8) = -2`（不是 `-3`）。需要"绝对值变大"的取整（如金额向上）时应判正负再分支：正数用 `CEIL`、负数用 `FLOOR`，或统一用 `LTRUNC` 后再 `+SGN(x)` 修正。这是最常踩的坑。
- **返回类型是 `LREAL` 不是 `LINT`**：用作数组下标等整数场景时还需要再 `LREAL_TO_DINT(CEIL(x))`，否则编译器会因隐式转换报警告。
- **大数精度衰减**：`LREAL` 尾数 52 位约 15-16 位十进制有效位。当 `lr_in > 2^53 ≈ 9.0e15` 时相邻浮点数间距 `≥ 1`，`CEIL` 与原值已无差异，应改用 `LINT` 整数运算。
- **小数位截取的浮点误差**：`CEIL(0.1 * 10) / 10` 的结果不保证恰为 `0.1`，可能是 `0.10000000000000001`。HMI 显示时要 `LREAL_TO_FMTSTR` 指定小数位，不能直接拼字符串。（工程经验补充）
- **`NaN` / `±Inf` 不可依赖**：上游算式有除零或开负数等可能产生 `NaN` 的运算时，应先用 `Tc2_Math` 之外的判定（如 `LREAL_TO_LREAL` 自比较）过滤再喂给 `CEIL`，否则结果 `NaN` 会在后续 `LREAL_TO_DINT` 报硬件浮点异常。（工程经验补充）
- **与 IEC `TRUNC` 区别**：标准 `TRUNC` 返回 `DINT`，超出 `±2³¹` 时溢出截断；`CEIL` 始终返回 `LREAL`，处理 `1e10` 级别仍正确。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CEIL.TcPOU`](../examples/P_Demo_CEIL.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：分拣线按重量阶梯收费——重 0.01-1.00kg 收 1 元、1.01-2.00kg 收 2 元……
//       需要把称重模块的 LREAL 读数"向上取整到下一公斤"算出收费档位。
//       负数侧（罕见但要可控）出现退货抵扣时 CEIL(-0.3) = 0 表示"不退整公斤"，
//       与业务方约定一致。
//
// 价值：CEIL 一行就把"四舍六入向上"语义封装好，省去写 IF/ELSIF 阈值判断。
//
// 验证：在线把 lrPackageWeightKg 写 0.3 → 看到 lrChargeTier = 1.0；
//                写 1.0 → 1.0（边界，不会跳到 2.0，符合 CEIL 定义）；
//                写 1.01 → 2.0；
//                写 -0.3 → 0.0（负数侧朝 +∞ 取，验证反直觉性）。
PROGRAM P_Demo_CEIL
VAR
    lrPackageWeightKg : LREAL := 0.3;   // 在线写值模拟称重读数
    lrChargeTier      : LREAL;          // 收费档位（公斤数）
    nChargeYuan       : DINT;           // 最终 LREAL → DINT 给收费系统
END_VAR

// 单行调用：CEIL 直接给出向上取整的公斤数
lrChargeTier := CEIL(lrPackageWeightKg);

// LREAL → DINT 是显式转换，规避编译器隐式转换警告
nChargeYuan := LREAL_TO_DINT(lrChargeTier);
```

## 7. 业务场景与实际价值

- **场景**：阶梯式计费 / 容器数估算 / 资源分配向上取整。典型工业例：物流分拣按重量计费、原料按批量打包（每箱 12 件，要装 35 件 → `CEIL(35/12) = 3` 箱）、内存页面分配（按 4KB 边界向上对齐）。
- **价值**：替代 `IF x > N THEN ... ELSIF ...` 多分支判断，一行表达"向上取最小整数"，代码量从 5-10 行降到 1 行，可读性大幅提升。同时返回 `LREAL` 处理远超 `DINT` 的大数（如累计纳秒时间戳）。
- **替代方案对比**：
  - 自己写 `IF FRAC(x) > 0 THEN result := LTRUNC(x) + 1 ELSE result := x; END_IF`：要处理负数侧符号，约 5 行，易错
  - 用 IEC 标准 `TRUNC(x + 0.9999)`：精度依赖加数，超过 4 位小数会失败
  - 用 `LREAL_TO_DINT(x + 0.5)`：那是四舍五入而不是"向上"，行为不同
  - **本函数**：单语义、`LREAL` 入 / `LREAL` 出，正负数边界精确

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf) §3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/17640900235.html
- **相关函数**：`FLOOR`（向下取整）、`LTRUNC`（朝零截断）、`FRAC`（取小数部分）、IEC `TRUNC` / `TO_LINT`（标准库的取整 / 四舍五入）
