# LREAL_TO_UINT64

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35197323.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_LREAL_TO_UINT64.TcPOU`](../examples/P_Demo_LREAL_TO_UINT64.TcPOU) |

---

## 1. 功能简述

把 LREAL 浮点数转换为 TwinCAT 2 的旧式无符号 64 位整数 `T_ULARGE_INTEGER`（高低各 32 位结构体）。当 PLC 里用 TwinCAT 2 移植代码、或与 ADS 报文里以 T_ULARGE_INTEGER 形式定义的字段交互时需要从浮点回到这种结构体表示。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LREAL_TO_UINT64 : T_ULARGE_INTEGER
VAR_INPUT
    in : LREAL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `LREAL` | - | 待转换的浮点数；超出 0..2⁶⁴−1 的部分按 PDF 未定义 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_ULARGE_INTEGER` —— 结构体表示的 64 位无符号整数。

## 3. 行为说明

本函数把 64 位浮点近似四舍五入或截断（PDF 未明确舍入模式 ⚠️）为一个 0..2⁶⁴−1 的整数，并按 dwHighPart/dwLowPart 写入 T_ULARGE_INTEGER 结构体。需要注意三个边界：第一，输入为负数时 PDF 未定义结果，工程实践应在调用前判断 `IF in < 0`；第二，输入大于 1.8E19（约 2⁶⁴）时 PDF 未定义溢出行为；第三，LREAL 在大于 2⁵³ 后只能表达整数的近似值，超过 9.007E15 的值会丢精度。返回结构体本身字段是 DWORD，可用 `ULARGE_TO_ULINT` 转换为原生 `ULINT` 后再做算术。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_ULARGE_INTEGER` —— 结构体表示的 64 位无符号整数。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- 负数 / 超出 2⁶⁴ 的输入 PDF 未定义 — 调用前自检
- LREAL 精度上限 2⁵³ ≈ 9E15，再大就只能近似
- 结果是 legacy 结构体，下一步算术建议先用 `ULARGE_TO_ULINT` 转为 ULINT
- 舍入模式 PDF 未列 ⚠️，与浮点四舍五入或截断行为相关的工程不要依赖此函数

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LREAL_TO_UINT64.TcPOU`](../examples/P_Demo_LREAL_TO_UINT64.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_LREAL_TO_UINT64
VAR
    lrSetpoint   : LREAL := 1.5E12;   // 业务侧浮点（如累计产量上限）
    uliConverted : T_ULARGE_INTEGER;       // 转换结果（写入 ADS Raw 报文）
    bConvert     : BOOL;                   // 在线置 TRUE 触发一次转换
END_VAR

IF bConvert AND lrSetpoint >= 0 THEN
    // 上升沿触发：先校验非负，避免命中 PDF 未定义行为
    uliConverted := LREAL_TO_UINT64(lrSetpoint);
    bConvert := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：把 PID 控制器算出的速度上限（LREAL）写入 ADS Raw 报文中按 T_ULARGE_INTEGER 定义的累计计数字段。
- **价值**：不用本函数得手写 LREAL 拆 DWORD 高低位再赋值给结构体两次，本函数一次返回；与 `Tc2_Utilities` 其它 64 位函数风格统一。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35197323.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
