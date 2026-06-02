# Int64Negate

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit functions (signed)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35215627.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_Int64Negate.TcPOU`](../examples/P_Demo_Int64Negate.TcPOU) |

---

## 1. 功能简述

对有符号 64 位整数取负（求相反数）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION Int64Negate : T_LARGE_INTEGER
VAR_INPUT
    i64 : T_LARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `i64` | `T_LARGE_INTEGER` | - | 待取负的有符号 64 位整数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_LARGE_INTEGER` —— −`i64`。

## 3. 行为说明

按二进制补码取负：`-x = NOT(x) + 1`。**边界**：`-(-2⁶³)` 数学上等于 2⁶³，但 2⁶³ 不可由 `T_LARGE_INTEGER` 表达（最大正数是 2⁶³−1），PDF 未定义 ⚠️（实际多数实现仍返回 −2⁶³，因为 NOT+1 周期性回绕）。其余值无风险。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit functions (signed)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_LARGE_INTEGER` —— −`i64`。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **−INT64_MIN PDF 未定义** ⚠️（数学不可表达）
- 负负得正、零取负仍为零
- 无溢出标志输出，调用前要确认输入不是 INT64_MIN

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Int64Negate.TcPOU`](../examples/P_Demo_Int64Negate.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_Int64Negate
VAR
    liValue      : T_LARGE_INTEGER;
    liNegated    : T_LARGE_INTEGER;
    bNegate      : BOOL;
END_VAR

IF bNegate THEN
    // 应保证 liValue <> INT64_MIN，否则 PDF 未定义
    liNegated := Int64Negate(liValue);
    bNegate := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：把累加器一次性'反向'应用到补偿量上：`error_sum := Int64Negate(error_sum)`。
- **价值**：替代手写 NOT + Add64 两步。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit functions (signed)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.8.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35215627.html
- **同组相关 FC**：见库分类 `64 bit functions (signed)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
