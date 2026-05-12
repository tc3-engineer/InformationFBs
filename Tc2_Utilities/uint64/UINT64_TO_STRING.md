# UINT64_TO_STRING

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35201931.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UINT64_TO_STRING.xml`](../examples/P_Demo_UINT64_TO_STRING.xml) |

---

## 1. 功能简述

把 TwinCAT 2 旧式 `T_ULARGE_INTEGER` 格式化为十进制字符串，便于在 HMI、CSV 报表、日志中显示。最大 20 位数字（2⁶⁴−1 = 18446744073709551615），加结尾零共 21 字节，匹配 `STRING(21)` 容量。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UINT64_TO_STRING : STRING(21)
VAR_INPUT
    in : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `T_ULARGE_INTEGER` | - | 待格式化为十进制字符串的 64 位无符号整数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`STRING(21)` —— 十进制表示，无前导零、无正负号；0..18446744073709551615 字符串长度 1..20。

## 3. 行为说明

函数对 `in.dwHighPart * 2³² + in.dwLowPart` 做反复除 10 取余，得到反向的十进制字符序列，再翻转写入返回 STRING。没有千位分隔符、没有前导零、没有正号；输入为 0 时返回 '0'。整段计算无内部状态、单 PLC 周期完成。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`STRING(21)` —— 十进制表示，无前导零、无正负号；0..18446744073709551615 字符串长度 1..20。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- 若把结果再写入更小的 STRING(10) 等容器会被截断，建议保留 STRING(21) 或更大
- 需要十六进制？用 `LWORD_TO_HEXSTR(ULARGE_TO_LWORD(in))` 组合
- 没有千位分隔；HMI 显示分隔符需要二次格式化

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UINT64_TO_STRING.xml`](../examples/P_Demo_UINT64_TO_STRING.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_UINT64_TO_STRING
VAR
    uliCounter   : T_ULARGE_INTEGER;       // 64 位数据包计数器
    sCounterText : STRING(21);             // CSV 列输出
    bFormat      : BOOL;                   // 触发一次格式化
END_VAR

IF bFormat THEN
    // 上升沿触发一次格式化，避免每个周期重做
    sCounterText := UINT64_TO_STRING(uliCounter);
    bFormat := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：把 64 位数据包计数器导出到 CSV 行，需要先转字符串。
- **价值**：替代手写 64 位除 10 取余循环；一行调用，无精度损失。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35201931.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
