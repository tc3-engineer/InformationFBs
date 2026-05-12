# LINT_TO_LARGE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit functions (signed)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934107275.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_LINT_TO_LARGE.xml`](../examples/P_Demo_LINT_TO_LARGE.xml) |

---

## 1. 功能简述

把 TC3 原生 `LINT` 转回 legacy 结构体 `T_LARGE_INTEGER`。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LINT_TO_LARGE : T_LARGE_INTEGER
VAR_INPUT
    in : LINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `LINT` | - | 待转换的 TC3 原生有符号 64 位整数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_LARGE_INTEGER` —— 与 `in` 数值相等。

## 3. 行为说明

按位拆分高 32 / 低 32 位写入结构体字段。数值不变。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit functions (signed)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_LARGE_INTEGER` —— 与 `in` 数值相等。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- 纯表示形式转换，无副作用
- 要交给只接受 legacy 的旧库函数时常用

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LINT_TO_LARGE.xml`](../examples/P_Demo_LINT_TO_LARGE.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_LINT_TO_LARGE
VAR
    liNative     : LINT := -123456789;
    liLegacy     : T_LARGE_INTEGER;
    bConvert     : BOOL;
END_VAR

IF bConvert THEN
    liLegacy := LINT_TO_LARGE(liNative);
    bConvert := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：本地用 LINT 做算术，调用一个只接 T_LARGE_INTEGER 的旧 FB 前转一下。
- **价值**：替代手写 SHR/AND/拼装。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit functions (signed)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.8.13
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934107275.html
- **同组相关 FC**：见库分类 `64 bit functions (signed)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
