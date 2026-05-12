# UInt64Mul64

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35169675.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UInt64Mul64.xml`](../examples/P_Demo_UInt64Mul64.xml) |

---

## 1. 功能简述

两个 64 位无符号整数相乘，**不检测溢出**。要溢出检测请改用 `UInt64Mul64Ex`。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt64Mul64 : T_ULARGE_INTEGER
VAR_INPUT
    multiplicand : T_ULARGE_INTEGER;
    multiplier : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `multiplicand` | `T_ULARGE_INTEGER` | - | 被乘数 |
| `multiplier` | `T_ULARGE_INTEGER` | - | 乘数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_ULARGE_INTEGER` —— `(a * b) mod 2⁶⁴`，无溢出指示。

## 3. 行为说明

函数返回真实积的低 64 位（即按模 2⁶⁴ 截断的 wrap-around 结果）。当真实积 ≥ 2⁶⁴ 时高位被静默丢弃。例如 `2^33 * 2^33 = 2^66` 返回 0。底层硬件 64×64→64 乘法指令一次完成（x86-64 MUL，几个周期）。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_ULARGE_INTEGER` —— `(a * b) mod 2⁶⁴`，无溢出指示。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **静默 wrap-around** —— 任一操作数 > 2³² 都有溢出风险，应改用 Ex 版本
- 如果只是 32×32→64，更省心的是 `UInt32x32To64`（永不溢出）
- 性能：一条硬件指令

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt64Mul64.xml`](../examples/P_Demo_UInt64Mul64.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_UInt64Mul64
VAR
    uliA         : T_ULARGE_INTEGER;       // 操作数
    uliB         : T_ULARGE_INTEGER;       // 操作数
    uliProduct   : T_ULARGE_INTEGER;       // 乘积
    bMultiply    : BOOL;
END_VAR

IF bMultiply THEN
    // 调用方已确保不溢出 → 跳过 Ex 版本的检测开销
    uliProduct := UInt64Mul64(uliA, uliB);
    bMultiply := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：低位 32 位以下的两个计数器相乘（确认不会溢出）求合并指标。
- **价值**：替代 Ex 版本在已知安全的快路径上节省一个 VAR_IN_OUT 参数。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.19
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35169675.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
