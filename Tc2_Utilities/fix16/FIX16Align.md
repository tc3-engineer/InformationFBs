# FIX16Align

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `16 bit fixed point number functions (signed)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35233931.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_FIX16Align.TcPOU`](../examples/P_Demo_FIX16Align.TcPOU) |

---

## 1. 功能简述

改变 `T_FIX16` 的小数位数（resolution）：把当前的 Q-format 重新对齐到新的 n。例如把 Q8 转 Q4 会丢失低 4 位精度。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FIX16Align : T_FIX16
VAR_INPUT
    in : T_FIX16;
    n : BYTE(0..15);
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `T_FIX16` | - | 待改变分辨率的定点数 |
| `n` | `BYTE(0..15)` | - | 目标小数位数，范围 0..15 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_FIX16` —— 新分辨率的定点数。

## 3. 行为说明

函数对内部 INT 值做位移以适配新 n。若新 n 小于原 n，丢失低位（截断）；若大于原 n，左移补 0（精度名义提高但实际信息没增加）。`n` 必须在 0..15。PDF 示例：`LREAL_TO_FIX16(0.6, 8)` 得 154（≈ 0.6015625），`FIX16Align(154, 4)` 转 Q4 = 9（= 0.5625，丢精度）。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `16 bit fixed point number functions (signed)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_FIX16` —— 新分辨率的定点数。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **调用方需跟踪原 n**：本函数无法从 INT 单独推断当前 n
- **n 必须在 0..15** —— PDF 限定
- 降低 n 会丢精度（如示例 0.6015625 → 0.5625）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FIX16Align.TcPOU`](../examples/P_Demo_FIX16Align.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FIX16Align
VAR
    fp8Source    : T_FIX16;       // Q8 来源
    fp4Aligned   : T_FIX16;       // Q4 输出
    lrCheck      : LREAL;
    bAlign       : BOOL;
END_VAR

fp8Source := LREAL_TO_FIX16(0.6, 8);   // Q8: ~0.6015625
IF bAlign THEN
    fp4Aligned := FIX16Align(fp8Source, 4);          // Q4: 0.5625
    lrCheck    := FIX16_TO_LREAL(fp4Aligned);
    bAlign := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：不同子模块要求不同分辨率，需要把上游 Q8 信号转 Q4 喂给下游。
- **价值**：替代手写 SHR/SHL；语义清晰、符合 PDF 命名。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `16 bit fixed point number functions (signed)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.7.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35233931.html
- **同组相关 FC**：见库分类 `16 bit fixed point number functions (signed)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
