# UInt64isZero

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35195787.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UInt64isZero.TcPOU`](../examples/P_Demo_UInt64isZero.TcPOU) |

---

## 1. 功能简述

判断 `T_ULARGE_INTEGER` 是否为 0。结构体 `=` 比较不可靠，必须用本函数（或 `UInt64Cmp64(x, ULARGE_INTEGER(0,0)) = 0`）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt64isZero : BOOL
VAR_INPUT
    ui64 : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `ui64` | `T_ULARGE_INTEGER` | - | 待判定的 64 位无符号整数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`BOOL` —— TRUE = 整数为 0；FALSE = 任一位置 1。

## 3. 行为说明

函数检查 `ui64.dwHighPart = 0 AND ui64.dwLowPart = 0`，是则返回 TRUE，否则返回 FALSE。无副作用、单周期。常用于除法前判 0、累加结束判 0、空状态判断。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`BOOL` —— TRUE = 整数为 0；FALSE = 任一位置 1。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **不要写 `x = 0`** —— `0` 是 INT 字面量，与 T_ULARGE_INTEGER 类型不兼容，编译可能报错也可能匹配错误重载
- 判 0 后做除法仍要小心被除数为 0 的情形：除以 0 才是问题，被除数为 0 商也为 0
- 本函数是 FC，无内部状态；放在 IF 条件里反复调用也无开销问题

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt64isZero.TcPOU`](../examples/P_Demo_UInt64isZero.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_UInt64isZero
VAR
    uliDivisor   : T_ULARGE_INTEGER;       // 除数
    bIsZero      : BOOL;                   // 是否为 0
    bCheck       : BOOL;
END_VAR

IF bCheck THEN
    // 除法前的合法性校验
    bIsZero := UInt64isZero(uliDivisor);
    bCheck := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：除法前校验除数，避免除 0 PDF 未定义。
- **价值**：替代结构体 `=` 比较（在某些 TwinCAT 版本里不可靠或语义不明）。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.14
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35195787.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
