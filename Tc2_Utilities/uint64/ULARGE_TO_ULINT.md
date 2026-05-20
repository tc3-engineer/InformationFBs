# ULARGE_TO_ULINT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934157323.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_ULARGE_TO_ULINT.xml`](../examples/P_Demo_ULARGE_TO_ULINT.xml) |

---

## 1. 功能简述

把 TwinCAT 2 旧式 `T_ULARGE_INTEGER`（结构体）转换为 TwinCAT 3 原生 `ULINT`（64 位无符号整数）。原生类型支持 IEC `+ - * / mod` 直接运算，比结构体更便利。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION ULARGE_TO_ULINT : ULINT
VAR_INPUT
    in : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `T_ULARGE_INTEGER` | - | 待转换的 legacy 64 位无符号结构体 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`ULINT` —— 与 `in` 数值完全相等的原生 64 位整数。

## 3. 行为说明

函数把结构体的 dwHighPart 左移 32 位 OR dwLowPart 拼成 64 位 ULINT。等价于 `LWORD(in.dwHighPart) * 16#100000000 + LWORD(in.dwLowPart)`。无溢出风险（值域完全一致）。返回 ULINT 后可直接做算术。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`ULINT` —— 与 `in` 数值完全相等的原生 64 位整数。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **类型边界**：从结构体过到原生类型，相当于换了一种表示，原值不变
- ULINT 可直接用 `+ - * /`，远比结构体好用
- 若结果还要回到 legacy 域请用 `LWORD_TO_ULARGE`（先经 `ULINT_TO_LWORD`）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ULARGE_TO_ULINT.xml`](../examples/P_Demo_ULARGE_TO_ULINT.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_ULARGE_TO_ULINT
VAR
    uliFromAds   : T_ULARGE_INTEGER;       // ADS 报文里读到的字段
    ulNative     : ULINT;                  // 业务侧原生 64 位
    bConvert     : BOOL;
END_VAR

IF bConvert THEN
    ulNative := ULARGE_TO_ULINT(uliFromAds);   // 转换后即可参与 IEC 算术
    bConvert := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：ADS Raw 报文里读到一个 T_ULARGE_INTEGER 字段，业务逻辑全用 ULINT 算术，需要一步转换。
- **价值**：替代手写位移 + 加法；一行调用。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.30
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934157323.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
