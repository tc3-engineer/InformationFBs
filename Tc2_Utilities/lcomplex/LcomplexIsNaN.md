# LcomplexIsNaN

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `LCOMPLEX functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/2572609163.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_LcomplexIsNaN.xml`](../examples/P_Demo_LcomplexIsNaN.xml) |

---

## 1. 功能简述

判断一个 `LCOMPLEX`（实部 + 虚部均为 LREAL）是否含有 NaN。返回 TRUE 表示**实部或虚部至少一个是 NaN**。常用于矢量控制 d-q 变换、阻抗计算后做合法性校验。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LcomplexIsNaN : BOOL
VAR_INPUT
    Z : REFERENCE TO LCOMPLEX;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `Z` | `REFERENCE TO LCOMPLEX` | - | 待测试的复数引用；本函数检查实部或虚部是否为 NaN |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`BOOL` —— TRUE = 实部或虚部为 NaN。

## 3. 行为说明

函数对实部与虚部分别做 IEEE 754 NaN 测试（参考 `LrealIsNaN`），任一为 NaN 则返回 TRUE。无副作用、单周期。需要 TwinCAT ≥ 3.1.4020 + Tc2_Utilities ≥ 3.3.16.0。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `LCOMPLEX functions` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`BOOL` —— TRUE = 实部或虚部为 NaN。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **REFERENCE TO LCOMPLEX**：传址要真实左值
- 本函数把'任一为 NaN'视为 NaN，不区分实虚
- 复数算术中除以 0（如 1/(0+0j)）会让结果有 NaN，要在传播到下游前拦截

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LcomplexIsNaN.xml`](../examples/P_Demo_LcomplexIsNaN.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_LcomplexIsNaN
VAR
    lcCurrent    : LCOMPLEX;       // d-q 反变换电流
    bHasNaN      : BOOL;
    bCheck       : BOOL;
END_VAR

IF bCheck THEN
    bHasNaN := LcomplexIsNaN(lcCurrent);
    bCheck := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：矢量控制 d-q 反变换后，电流复数若含 NaN 必须切回上一周期值以保险。
- **价值**：替代手写 `LrealIsNaN(Z.re) OR LrealIsNaN(Z.im)`；一次调用语义清晰。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `LCOMPLEX functions` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.5.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/2572609163.html
- **同组相关 FC**：见库分类 `LCOMPLEX functions`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
