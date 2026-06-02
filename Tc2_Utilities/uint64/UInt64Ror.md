# UInt64Ror

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35194251.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UInt64Ror.TcPOU`](../examples/P_Demo_UInt64Ror.TcPOU) |

---

## 1. 功能简述

对 `T_ULARGE_INTEGER` 做循环右移：移出最低位的内容回卷到最高位。常用于哈希、加密。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt64Ror : T_ULARGE_INTEGER
VAR_INPUT
    ui64 : T_ULARGE_INTEGER;
    n : DWORD;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `ui64` | `T_ULARGE_INTEGER` | - | 待循环右移的操作数 |
| `n` | `DWORD` | - | 右移的位数（0..63；超过 64 PDF 未定义） |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_ULARGE_INTEGER` —— 循环右移结果。

## 3. 行为说明

结果 = `(ui64 SHR n) OR (ui64 SHL (64-n))`。n 应在 0..63，n=0 恒等，n≥64 PDF 未定义 ⚠️。无副作用。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_ULARGE_INTEGER` —— 循环右移结果。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **n 应在 0..63** ⚠️
- 循环移位不丢位
- 常用搭配 `UInt64Rol` 实现 bit 旋转链

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt64Ror.TcPOU`](../examples/P_Demo_UInt64Ror.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_UInt64Ror
VAR
    uliHashState : T_ULARGE_INTEGER;
    dwShiftBits  : DWORD := 29;
    uliRotated   : T_ULARGE_INTEGER;
    bRotate      : BOOL;
END_VAR

IF bRotate AND dwShiftBits < 64 THEN
    uliRotated := UInt64Ror(uliHashState, dwShiftBits);
    bRotate := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：SHA-256 / SHA-512 风格哈希里的 σ₀ / σ₁ 混淆函数。
- **价值**：替代 SHR+SHL+OR 三行。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.24
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35194251.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
