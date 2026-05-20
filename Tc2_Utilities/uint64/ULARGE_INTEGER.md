# ULARGE_INTEGER

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35161995.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_ULARGE_INTEGER.xml`](../examples/P_Demo_ULARGE_INTEGER.xml) |

---

## 1. 功能简述

构造一个 `T_ULARGE_INTEGER` 字面值：传入高 32 位与低 32 位 DWORD，返回拼装后的结构体。是构造 64 位无符号常量的标准入口。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION ULARGE_INTEGER : T_ULARGE_INTEGER
VAR_INPUT
    dwHighPart : DWORD;
    dwLowPart : DWORD;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `dwHighPart` | `DWORD` | - | 上位 32 位 |
| `dwLowPart` | `DWORD` | - | 下位 32 位 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_ULARGE_INTEGER` —— 由两个 DWORD 拼装而成的 64 位无符号整数。

## 3. 行为说明

函数把 dwHighPart 写入结构体的高字段、dwLowPart 写入低字段，并返回结构体。**这不是位移、不是相加**；构造的值在数值上等于 `dwHighPart * 2³² + dwLowPart`。最大值 `ULARGE_INTEGER(16#FFFFFFFF, 16#FFFFFFFF)` = 2⁶⁴−1。常用于在 IEC ST 里写 64 位字面常量（IEC 没有 64 位无符号字面）。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_ULARGE_INTEGER` —— 由两个 DWORD 拼装而成的 64 位无符号整数。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **参数顺序是 high, low**（不是 low, high）—— 写反会得到大小颠倒的数
- 想从纯十进制字符串构造请用 `STRING_TO_UINT64`
- 想从原生 LWORD 构造请用 `LWORD_TO_ULARGE`

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ULARGE_INTEGER.xml`](../examples/P_Demo_ULARGE_INTEGER.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_ULARGE_INTEGER
VAR
    uliThreshold : T_ULARGE_INTEGER;       // 1E12 字面常量
    bInit        : BOOL := TRUE;
END_VAR

IF bInit THEN
    // 1E12 = 0xE8D4A51000 = high 0x00 + low 0xE8D4A51000？
    // 实际 1E12 = 16#E8D4A51000 → high = 16#E8, low = 16#D4A51000
    uliThreshold := ULARGE_INTEGER(16#E8, 16#D4A51000);
    bInit := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：在 PLC 启动初始化时定义 64 位常量上限阈值 = 1E12。
- **价值**：替代手写结构体字段逐字段赋值；一行调用语义清晰。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.29
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35161995.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
