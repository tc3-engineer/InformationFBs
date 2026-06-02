# STRING_TO_UINT64

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35198859.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_STRING_TO_UINT64.TcPOU`](../examples/P_Demo_STRING_TO_UINT64.TcPOU) |

---

## 1. 功能简述

把十进制字符串解析为 TwinCAT 2 旧式无符号 64 位整数 `T_ULARGE_INTEGER`。常用于把 HMI 输入框或文本文件里读到的大整数字符串还原为 PLC 可算术运算的二进制表示。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION STRING_TO_UINT64 : T_ULARGE_INTEGER
VAR_INPUT
    in : STRING(21);
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `STRING(21)` | - | 待转换的字符串；最长 21 字符（2⁶⁴−1 = 18446744073709551615 共 20 位 + 终止符） |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_ULARGE_INTEGER` —— 解析后的 64 位整数；解析失败时 PDF 未列错误码 ⚠️，调用方应在调用前用 `F_IsValidDecimalString` 之类的辅助函数校验。

## 3. 行为说明

函数从左到右扫描 `STRING(21)`，按 ASCII '0'..'9' 累加进 64 位累加器；遇到非数字字符或长度溢出时 PDF 未定义结果 ⚠️。最大支持值为 2⁶⁴−1，对应字符串 '18446744073709551615'。负号、十六进制前缀（0x）、千位分隔符、空白均不被解析。空字符串返回 0。STRING 容量 21 已为最大 20 位数字 + 结尾留 1，足够；如果输入来自 STRING(80) 也兼容（只读到前 21 字节）。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_ULARGE_INTEGER` —— 解析后的 64 位整数；解析失败时 PDF 未列错误码 ⚠️，调用方应在调用前用 `F_IsValidDecimalString` 之类的辅助函数校验。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- 非法字符 / 超长 / 负号 PDF 未定义结果 ⚠️ —— 调用前必须自检
- 字符串末尾的空白或回车会终止扫描（按 ASCII 0..9 判断），不会自动 trim
- 结果是 legacy 结构体；要继续算术请配合 `ULARGE_TO_ULINT`
- HMI 输入框常带 LF/CR/空格，建议先 `F_LTrim` + `F_RTrim`

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_STRING_TO_UINT64.TcPOU`](../examples/P_Demo_STRING_TO_UINT64.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_STRING_TO_UINT64
VAR
    sCountText   : STRING(21) := '18446744073709551615';   // 来自 CSV 报表的极大值
    uliCount     : T_ULARGE_INTEGER;                          // 解析后的整数
    bParse       : BOOL;                                      // 触发一次解析
END_VAR

IF bParse THEN
    // 上升沿触发：实际工程应先用 F_IsValidDecimalString 校验
    uliCount := STRING_TO_UINT64(sCountText);
    bParse := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：从 CSV 报表读到的产量计数字符串还原为 64 位整数用于累加。
- **价值**：替代手写 `WHILE i &lt;= LEN(s) DO ... END_WHILE` 累加循环；一次调用搞定，错误风险集中在校验上而不是解析上。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35198859.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
