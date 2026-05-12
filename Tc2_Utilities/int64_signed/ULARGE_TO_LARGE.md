# ULARGE_TO_LARGE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit functions (signed)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35221771.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_ULARGE_TO_LARGE.xml`](../examples/P_Demo_ULARGE_TO_LARGE.xml) |

---

## 1. 功能简述

把 `T_ULARGE_INTEGER` 重新解读为 `T_LARGE_INTEGER`：位模式不变，符号约定改变。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION ULARGE_TO_LARGE : T_LARGE_INTEGER
VAR_INPUT
    in : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `T_ULARGE_INTEGER` | - | 待转换的无符号结构体 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_LARGE_INTEGER` —— 与 `in` 位模式相同。

## 3. 行为说明

字段直接复制到有符号结构体。`MAX64`（无符号）变成 `−1`（有符号），高位置 1 的无符号大数变成有符号负数。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit functions (signed)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_LARGE_INTEGER` —— 与 `in` 位模式相同。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **数值含义会变** —— 大无符号数变小负数
- 若 `in` ≤ INT64_MAX（高位 0）则数值不变
- 需要真实截断到有符号：先 `UInt64Min(in, ULARGE_INTEGER(16#7FFFFFFF, 16#FFFFFFFF))`

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ULARGE_TO_LARGE.xml`](../examples/P_Demo_ULARGE_TO_LARGE.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_ULARGE_TO_LARGE
VAR
    uliRaw       : T_ULARGE_INTEGER;
    liSigned     : T_LARGE_INTEGER;
    bConvert     : BOOL;
END_VAR

IF bConvert THEN
    liSigned := ULARGE_TO_LARGE(uliRaw);
    bConvert := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：无符号读回的位串希望按有符号显示（比如负温度的差值表示）。
- **价值**：替代字段复制。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit functions (signed)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.8.15
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35221771.html
- **同组相关 FC**：见库分类 `64 bit functions (signed)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
