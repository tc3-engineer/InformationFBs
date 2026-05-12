# UInt64Add64

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35163531.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UInt64Add64.xml`](../examples/P_Demo_UInt64Add64.xml) |

---

## 1. 功能简述

两个 `T_ULARGE_INTEGER` 无符号 64 位整数相加，**不检测溢出**。如需检测溢出请改用 `UInt64Add64Ex`。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt64Add64 : T_ULARGE_INTEGER
VAR_INPUT
    ui64a : T_ULARGE_INTEGER;
    ui64b : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `ui64a` | `T_ULARGE_INTEGER` | - | 加数 A |
| `ui64b` | `T_ULARGE_INTEGER` | - | 加数 B |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_ULARGE_INTEGER` —— `(ui64a + ui64b) mod 2⁶⁴`，无溢出标志。

## 3. 行为说明

函数对两个 64 位结构体做无符号加法。当真实数值之和 ≥ 2⁶⁴ 时按模 2⁶⁴ 截断（wrap-around，等价于 C 语言 unsigned 加法语义）；调用方拿不到任何溢出指示。例如 `ULARGE_INTEGER(16#FFFFFFFF, 16#FFFFFFFF) + ULARGE_INTEGER(0, 1)` 返回 `ULARGE_INTEGER(0, 0)`。该截断行为在长时间计数器（如纳秒级 64 位时钟）里通常是有用的；在求差或求和有溢出风险的场景（金额累加、生产量累加）必须改用 Ex 版本。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_ULARGE_INTEGER` —— `(ui64a + ui64b) mod 2⁶⁴`，无溢出标志。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **静默 wrap-around**：和 ≥ 2⁶⁴ 时被截断，调用方无从感知 → 累加金额慎用
- 需要溢出指示请用 `UInt64Add64Ex`（多一个 `bOV` VAR_IN_OUT）
- 重复调用做累加时建议把上一周期的结果 latch 保存，本函数无内部状态
- 结果是结构体；继续做条件比较请用 `UInt64Cmp64` 而不是 `=`

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt64Add64.xml`](../examples/P_Demo_UInt64Add64.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_UInt64Add64
VAR
    uliRuntime   : T_ULARGE_INTEGER;       // 64 位运行时长（ns）累加器
    uliDelta     : T_ULARGE_INTEGER;       // 本周期增量
    bAccumulate  : BOOL;                   // 在线触发一次累加
END_VAR

IF bAccumulate THEN
    // 静默 wrap-around：纳秒计数 2⁶⁴ ns ≈ 584 年才回绕，工程上忽略
    uliRuntime := UInt64Add64(uliRuntime, uliDelta);
    bAccumulate := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：纳秒级 64 位时间戳累加：累计运行时间从 0 累加，2⁶⁴ ns ≈ 584 年才会回绕，工程上视为永不溢出。
- **价值**：替代手写双倍长加法（先低 32 位加 + 进位、再高 32 位加）的两行汇编风格代码；一次调用，可读性更高。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35163531.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
