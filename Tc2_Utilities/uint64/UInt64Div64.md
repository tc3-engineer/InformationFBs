# UInt64Div64

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35172747.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UInt64Div64.xml`](../examples/P_Demo_UInt64Div64.xml) |

---

## 1. 功能简述

两个 64 位无符号整数相除，返回商。仅返回商不返回余数；要余数请改用 `UInt64Mod64`，或选 `UInt64Div64Ex`（同时给商和余数）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt64Div64 : T_ULARGE_INTEGER
VAR_INPUT
    dividend : T_ULARGE_INTEGER;
    divisor : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `dividend` | `T_ULARGE_INTEGER` | - | 被除数 |
| `divisor` | `T_ULARGE_INTEGER` | - | 除数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_ULARGE_INTEGER` —— 整数商，向零截断。

## 3. 行为说明

商 = `dividend / divisor`（向零截断）。当 `divisor = 0` 时 PDF 未定义结果 ⚠️，必须前置校验。函数无内部状态、单周期完成、性能取决于硬件 64 位除法指令（x86-64 单条 DIV，约 20-100 周期，比加减慢）。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_ULARGE_INTEGER` —— 整数商，向零截断。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **除以 0 PDF 未定义** ⚠️
- 丢失余数 —— 余数信息要用 `UInt64Mod64` 单独求或改用 Ex 版本
- 向零截断不是四舍五入；19/10 = 1，−19 在无符号语义下不存在
- 性能比加法慢一个数量级（一条 DIV 指令），频繁调用时考虑预计算

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt64Div64.xml`](../examples/P_Demo_UInt64Div64.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_UInt64Div64
VAR
    uliTotalBytes: T_ULARGE_INTEGER;       // 累计字节数
    uliCycles    : T_ULARGE_INTEGER;       // 周期数
    uliAvgBytes  : T_ULARGE_INTEGER;       // 平均吞吐
    bCompute     : BOOL;
END_VAR

IF bCompute AND NOT UInt64isZero(uliCycles) THEN
    // 除 0 校验：除数是结构体，用 UInt64isZero 不是 = 0
    uliAvgBytes := UInt64Div64(uliTotalBytes, uliCycles);
    bCompute := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：把累计字节数 / 周期数 = 平均每周期字节数（吞吐率），用于在 HMI 显示。
- **价值**：替代手写双倍长除法；一次调用直接拿商。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.12
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35172747.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
