# UInt64Sub64

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35166603.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UInt64Sub64.xml`](../examples/P_Demo_UInt64Sub64.xml) |

---

## 1. 功能简述

两个 `T_ULARGE_INTEGER` 相减。**不检测下溢**：当 `ui64b > ui64a` 时按模 2⁶⁴ 回绕，结果是个非常大的数（类似无符号 C 减法）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt64Sub64 : T_ULARGE_INTEGER
VAR_INPUT
    ui64a : T_ULARGE_INTEGER;
    ui64b : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `ui64a` | `T_ULARGE_INTEGER` | - | 被减数 |
| `ui64b` | `T_ULARGE_INTEGER` | - | 减数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_ULARGE_INTEGER` —— 差值，模 2⁶⁴。

## 3. 行为说明

结果 = `(ui64a - ui64b) mod 2⁶⁴`。下溢时静默回绕、无错误码。例如 `ULARGE_INTEGER(0,1) - ULARGE_INTEGER(0,2) = ULARGE_INTEGER(16#FFFFFFFF, 16#FFFFFFFF)`。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_ULARGE_INTEGER` —— 差值，模 2⁶⁴。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **静默下溢**：被减数 < 减数时返回一个非常大的数，调用方必须先用 `UInt64Cmp64` 判 a ≥ b
- Tc2_Utilities 没有 Ex 版本检测下溢；要安全减法只能前置比较
- 金额、时间差等场景务必前置 `UInt64Cmp64(a, b) >= 0` 校验

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt64Sub64.xml`](../examples/P_Demo_UInt64Sub64.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_UInt64Sub64
VAR
    uliEnd       : T_ULARGE_INTEGER;       // 结束时间戳
    uliStart     : T_ULARGE_INTEGER;       // 起始时间戳
    uliDuration  : T_ULARGE_INTEGER;       // 持续时间
    bCompute     : BOOL;
END_VAR

IF bCompute AND UInt64Cmp64(uliEnd, uliStart) >= 0 THEN
    // 前置校验避免下溢回绕到一个超大数
    uliDuration := UInt64Sub64(uliEnd, uliStart);
    bCompute := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：算两个 64 位时间戳的差值（ts_end − ts_start），前置校验 end ≥ start 避免回绕。
- **价值**：替代手写双倍长减法 + 借位；一次调用搞定。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.27
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35166603.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
