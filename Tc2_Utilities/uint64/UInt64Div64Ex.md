# UInt64Div64Ex

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35174283.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UInt64Div64Ex.TcPOU`](../examples/P_Demo_UInt64Div64Ex.TcPOU) |

---

## 1. 功能简述

带余数输出的 64 位无符号除法。一次调用同时拿到商（返回值）和余数（VAR_IN_OUT），效率高于'先 Div 再 Mod'的两次调用。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt64Div64Ex : T_ULARGE_INTEGER
VAR_INPUT
    dividend : T_ULARGE_INTEGER;
    divisor : T_ULARGE_INTEGER;
END_VAR
VAR_IN_OUT
    remainder : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `dividend` | `T_ULARGE_INTEGER` | - | 被除数 |
| `divisor` | `T_ULARGE_INTEGER` | - | 除数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `remainder` | `T_ULARGE_INTEGER` | - | 输出余数；调用方需提供左值变量 |

### 返回值

`T_ULARGE_INTEGER` —— 商；`remainder` 输出余数。

## 3. 行为说明

商 = `dividend / divisor` 向零截断；余数 = `dividend - 商 * divisor`，范围 0..divisor-1。`divisor = 0` PDF 未定义。`remainder` 由函数完全覆盖；调用前无须初始化。底层硬件除法指令一次返回商与余数，所以本函数比 `UInt64Div64` + `UInt64Mod64` 快约一倍。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_ULARGE_INTEGER` —— 商；`remainder` 输出余数。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **除以 0 PDF 未定义** ⚠️
- 余数是 VAR_IN_OUT，参数侧必须能取地址
- 已经一次取走余数，不要再二次调 `UInt64Mod64` 重复算
- 把 `remainder` 当临时变量复用要小心 —— 函数会覆盖原值

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt64Div64Ex.TcPOU`](../examples/P_Demo_UInt64Div64Ex.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_UInt64Div64Ex
VAR
    uliNanos     : T_ULARGE_INTEGER;       // 累计纳秒
    uliDivisor   : T_ULARGE_INTEGER;       // 1e9 = 一秒的纳秒数
    uliSeconds   : T_ULARGE_INTEGER;       // 秒数（商）
    uliSubNs     : T_ULARGE_INTEGER;       // 亚秒纳秒（余数）
    bCompute     : BOOL;
END_VAR

uliDivisor := ULARGE_INTEGER(0, 1000000000);   // 1e9
IF bCompute AND NOT UInt64isZero(uliDivisor) THEN
    uliSeconds := UInt64Div64Ex(uliNanos, uliDivisor, uliSubNs);
    bCompute := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：把累计纳秒数同时拆成秒数（商）+ 纳秒余数（亚秒部分）用于显示。
- **价值**：一次硬件除法同时拿商与余数，比两次调用快一倍。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.13
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35174283.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
