# LrealIsFinite

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `FLOAT functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/2570925451.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_LrealIsFinite.xml`](../examples/P_Demo_LrealIsFinite.xml) |

---

## 1. 功能简述

判断一个 LREAL 是否是**有限**值，即既不是 NaN（Not a Number）也不是 ±Inf。返回 TRUE 表示输入是普通浮点数，可参与后续算术 / 比较 / 显示。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LrealIsFinite : BOOL
VAR_INPUT
    x : REFERENCE TO LREAL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `x` | `REFERENCE TO LREAL` | - | 待测试的浮点引用；本函数检查它是否为有限值（非 NaN / 非 ±Inf） |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`BOOL` —— TRUE = 有限值；FALSE = NaN 或 ±Inf。

## 3. 行为说明

按 IEEE 754 双精度规范：指数全 1 且尾数非 0 即 NaN，指数全 1 且尾数为 0 即 ±Inf，二者均不算 Finite。输入用 `REFERENCE TO LREAL` 传址（无 8 字节拷贝开销）。无副作用、无错误码、单 PLC 周期完成。Tc2_Utilities 版本 ≥ 3.3.16.0、TwinCAT 编译器 ≥ 3.1.4020 才提供本函数。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `FLOAT functions` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`BOOL` —— TRUE = 有限值；FALSE = NaN 或 ±Inf。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **REFERENCE TO LREAL**：传址，参数侧必须是真实左值，不可传常量 / 表达式
- 等价于'`NOT LrealIsNaN(x) AND NOT (x = INFINITY)`'，但本函数是单次调用
- 对一个 NaN 用 `IF x > 0` 这种比较恒为 FALSE（NaN 比较语义），所以'判 finite 后再比较'是稳健写法
- 需要 TwinCAT ≥ 3.1.4020 + Tc2_Utilities ≥ 3.3.16.0

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LrealIsFinite.xml`](../examples/P_Demo_LrealIsFinite.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_LrealIsFinite
VAR
    lrPidOut     : LREAL;                  // PID 输出
    bFinite      : BOOL;                   // 是否安全使用
    bCheck       : BOOL;
END_VAR

IF bCheck THEN
    // 必须用变量传址 —— REFERENCE TO 不接表达式
    bFinite := LrealIsFinite(lrPidOut);
    bCheck := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：PID 输出做电机命令前必须先 finite 校验，否则下游 LREAL_TO_INT64 命中 PDF 未定义。
- **价值**：替代手写 IEEE 754 位检测；一次调用语义清晰。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `FLOAT functions` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.4.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/2570925451.html
- **同组相关 FC**：见库分类 `FLOAT functions`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
