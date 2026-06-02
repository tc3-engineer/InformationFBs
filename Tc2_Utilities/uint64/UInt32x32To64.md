# UInt32x32To64

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35168139.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UInt32x32To64.TcPOU`](../examples/P_Demo_UInt32x32To64.TcPOU) |

---

## 1. 功能简述

把两个 32 位无符号整数相乘，乘积以 64 位 `T_ULARGE_INTEGER` 返回。专门用于'两个 32 位相乘会溢出 32 位'的场景，避免手写时把结果截断到 32 位。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt32x32To64 : T_ULARGE_INTEGER
VAR_INPUT
    ui32a : DWORD;
    ui32b : DWORD;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `ui32a` | `DWORD` | - | 乘数 A（32 位无符号） |
| `ui32b` | `DWORD` | - | 乘数 B（32 位无符号） |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_ULARGE_INTEGER` —— 真正的 64 位乘积，永远不溢出。

## 3. 行为说明

本函数对两个 DWORD 做硬件级 32×32→64 乘法（x86 的 MUL EAX 指令、ARM 的 UMULL 指令一条搞定），结果范围 0..(2³²−1)² ≈ 1.8E19，不会溢出 64 位。任何输入组合都安全，包括两个 0xFFFFFFFF。结果先看 dwHighPart 是否为 0：若为 0，乘积可直接当 DWORD 用；不为 0 时必须当 64 位看待。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_ULARGE_INTEGER` —— 真正的 64 位乘积，永远不溢出。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- 不要直接写 `DWORD(a) * DWORD(b)` —— TwinCAT 会按 32 位截断，丢高位
- 结果若要继续乘加，先 `ULARGE_TO_ULINT` 转 ULINT 更顺手
- 两输入都是无符号；负的 DINT 必须先 `DINT_TO_DWORD` 显式转换并理解位模式含义
- 在 32 位 CPU 上单条指令完成，性能与一次 DWORD 乘法相当

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt32x32To64.TcPOU`](../examples/P_Demo_UInt32x32To64.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_UInt32x32To64
VAR
    dwCycleCount : DWORD := 16#FFFFFFFF;   // 接近 32 位上限的周期数
    dwPerCycle   : DWORD := 100;             // 每周期事件数
    uliTotal     : T_ULARGE_INTEGER;          // 64 位乘积
    bCompute     : BOOL;                     // 触发计算
END_VAR

IF bCompute THEN
    // 上升沿触发：避免反复算（PLC 周期内只调用一次）
    uliTotal := UInt32x32To64(dwCycleCount, dwPerCycle);
    bCompute := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：计算两个 32 位计数器（如周期计数 × 单周期事件数）相乘后的总事件数，可能超过 32 位上限。
- **价值**：替代手写 32×32 → 64 位的双倍长乘法；一行调用，性能等同于硬件单指令。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35168139.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
