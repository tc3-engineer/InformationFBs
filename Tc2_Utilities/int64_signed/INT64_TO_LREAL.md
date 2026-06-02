# INT64_TO_LREAL

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit functions (signed)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35220235.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_INT64_TO_LREAL.TcPOU`](../examples/P_Demo_INT64_TO_LREAL.TcPOU) |

---

## 1. 功能简述

把 TwinCAT 2 旧式 `T_LARGE_INTEGER`（有符号 64 位结构体）转换为 LREAL 浮点。供 HMI 显示、报表、与浮点算法接口。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION INT64_TO_LREAL : LREAL
VAR_INPUT
    in : T_LARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `T_LARGE_INTEGER` | - | 待转换的 legacy 有符号 64 位整数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`LREAL` —— 数值上等于 `in`；大于 2⁵³ 时是最近的浮点近似。

## 3. 行为说明

按结构体语义解读为有符号 64 位（最高位为符号位），再赋给 LREAL。LREAL 尾数 52 位，绝对值大于 2⁵³ 时丢精度。不会异常、不会 NaN。负数会被正确还原（取决于结构体字段的符号约定，PDF 视作两个 DWORD 拼接的二进制补码）。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit functions (signed)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`LREAL` —— 数值上等于 `in`；大于 2⁵³ 时是最近的浮点近似。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **大于 2⁵³ 丢精度**（≈ 9E15）
- 用于显示无影响；用于算术建议保持整数域
- T_LARGE_INTEGER 的字段虽是 DWORD（无符号），但拼起来按二进制补码解读为有符号

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_INT64_TO_LREAL.TcPOU`](../examples/P_Demo_INT64_TO_LREAL.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_INT64_TO_LREAL
VAR
    liTorqueInt  : T_LARGE_INTEGER;        // 有符号 64 位扭矩积分
    lrTorqueDisp : LREAL;                  // HMI 显示
    bConvert     : BOOL;
END_VAR

IF bConvert THEN
    lrTorqueDisp := INT64_TO_LREAL(liTorqueInt);
    bConvert := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：把 64 位有符号扭矩积分（可正可负）转 LREAL 在 HMI 显示。
- **价值**：替代手写有符号双倍长转浮点；一行调用。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit functions (signed)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.8.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35220235.html
- **同组相关 FC**：见库分类 `64 bit functions (signed)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
