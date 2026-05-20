# UInt64Cmp64

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35177355.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UInt64Cmp64.xml`](../examples/P_Demo_UInt64Cmp64.xml) |

---

## 1. 功能简述

比较两个 `T_ULARGE_INTEGER`，返回 -1 / 0 / 1 三态结果，对应小于 / 等于 / 大于。结构体 `=` 比较在 IEC 里不可靠，必须用这个函数。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt64Cmp64 : DINT
VAR_INPUT
    ui64a : T_ULARGE_INTEGER;
    ui64b : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `ui64a` | `T_ULARGE_INTEGER` | - | 左操作数；返回 -1 表示 ui64a 小于 ui64b |
| `ui64b` | `T_ULARGE_INTEGER` | - | 右操作数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`DINT` —— `-1` / `0` / `1`，对应小于 / 等于 / 大于。

## 3. 行为说明

函数先比较 dwHighPart，相等再比较 dwLowPart。返回 `-1` (ui64a &lt; ui64b)、`0` (ui64a = ui64b)、`1` (ui64a &gt; ui64b)。无符号比较语义：`ULARGE_INTEGER(16#80000000, 0)` &gt; `ULARGE_INTEGER(0, 0)`（最高位置 1 视为正大数，不是负数）。无错误码、无副作用、单周期完成。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`DINT` —— `-1` / `0` / `1`，对应小于 / 等于 / 大于。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- 返回 DINT 不是 BOOL；分支判断用 `IF UInt64Cmp64(a, b) &lt; 0 THEN`
- **不要用结构体 `a = b` 直接比较**：IEC 对结构体 `=` 未规定行为；要等于判断请用 `UInt64Cmp64(a, b) = 0`
- 无符号语义，没有负数概念；从 DINT/LINT 转来的负值实际是大数
- 排序场景可直接喂给 STL/链表排序回调

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt64Cmp64.xml`](../examples/P_Demo_UInt64Cmp64.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_UInt64Cmp64
VAR
    uliBatchA    : T_ULARGE_INTEGER;       // A 线产量
    uliBatchB    : T_ULARGE_INTEGER;       // B 线产量
    diResult     : DINT;                   // 比较结果
    bCompare     : BOOL;                   // 触发比较
END_VAR

IF bCompare THEN
    // -1: A 少 / 0: 持平 / 1: A 多
    diResult := UInt64Cmp64(uliBatchA, uliBatchB);
    bCompare := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：把两个生产批次的产量计数器排序，决定哪条线产量更高。
- **价值**：替代手写两次 DWORD 比较 + 嵌套 IF；一次调用 + DINT 比较一目了然。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35177355.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
