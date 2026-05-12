# Int64Sub64

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit functions (signed)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35209483.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_Int64Sub64.xml`](../examples/P_Demo_Int64Sub64.xml) |

---

## 1. 功能简述

两个有符号 64 位整数相减，**不检测溢出**。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION Int64Sub64 : T_LARGE_INTEGER
VAR_INPUT
    i64a : T_LARGE_INTEGER;
    i64b : T_LARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `i64a` | `T_LARGE_INTEGER` | - | 被减数 |
| `i64b` | `T_LARGE_INTEGER` | - | 减数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_LARGE_INTEGER` —— 差。

## 3. 行为说明

按二进制补码相减；溢出（两正减两负、或两负减两正越界）时静默 wrap-around，符号位翻转。Tc2_Utilities 没有 `Int64Sub64Ex`，需要溢出检测得自己组合：`Add64Ex(a, Negate(b))` 但要小心 `Negate(INT64_MIN)`。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit functions (signed)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_LARGE_INTEGER` —— 差。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **静默有符号溢出**
- 没有 Ex 版本检测溢出 —— 工程上需要自己包
- 想算两个时间戳差值用 ULARGE 系列比 LARGE 顺手（时间戳通常非负）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Int64Sub64.xml`](../examples/P_Demo_Int64Sub64.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_Int64Sub64
VAR
    liA          : T_LARGE_INTEGER;
    liB          : T_LARGE_INTEGER;
    liDiff       : T_LARGE_INTEGER;
    bSubtract    : BOOL;
END_VAR

IF bSubtract THEN
    liDiff := Int64Sub64(liA, liB);
    bSubtract := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：算两个有符号扭矩积分的差值。
- **价值**：替代手写有符号双倍长减法 + 借位。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit functions (signed)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.8.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35209483.html
- **同组相关 FC**：见库分类 `64 bit functions (signed)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
