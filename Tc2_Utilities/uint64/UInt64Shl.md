# UInt64Shl

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35189643.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UInt64Shl.TcPOU`](../examples/P_Demo_UInt64Shl.TcPOU) |

---

## 1. 功能简述

对 `T_ULARGE_INTEGER` 做逻辑左移。移出去的最高位**直接丢弃**，最低位补 0。等价于乘以 2ⁿ（不溢出检测）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt64Shl : T_ULARGE_INTEGER
VAR_INPUT
    ui64 : T_ULARGE_INTEGER;
    n : DWORD;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `ui64` | `T_ULARGE_INTEGER` | - | 待左移的操作数 |
| `n` | `DWORD` | - | 左移的位数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_ULARGE_INTEGER` —— 左移结果。

## 3. 行为说明

结果 = `ui64 * 2ⁿ mod 2⁶⁴`。n ≥ 64 PDF 未定义 ⚠️（多数实现等于 n mod 64）。常用作 2 的幂次乘法的高效替代。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_ULARGE_INTEGER` —— 左移结果。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **移出去的位丢失** —— 不是循环移位
- n ≥ 64 PDF 未定义 ⚠️
- 等价于乘以 2ⁿ 但不检测溢出

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt64Shl.TcPOU`](../examples/P_Demo_UInt64Shl.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_UInt64Shl
VAR
    uliValue     : T_ULARGE_INTEGER;
    dwShiftBits  : DWORD := 10;
    uliScaled    : T_ULARGE_INTEGER;       // = value × 2^10 = ×1024
    bScale       : BOOL;
END_VAR

IF bScale AND dwShiftBits < 64 THEN
    uliScaled := UInt64Shl(uliValue, dwShiftBits);
    bScale := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：把 nanos 转 PicoSec 需要乘 1000，但若是 1024（2¹⁰）可用 `Shl(n, 10)` 加速。
- **价值**：替代乘法操作，性能更好；与 Shr 配对实现 64 位整数的位级缩放。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.25
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35189643.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
