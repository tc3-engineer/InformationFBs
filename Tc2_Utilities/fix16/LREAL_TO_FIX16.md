# LREAL_TO_FIX16

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `16 bit fixed point number functions (signed)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35226251.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_LREAL_TO_FIX16.xml`](../examples/P_Demo_LREAL_TO_FIX16.xml) |

---

## 1. 功能简述

把 LREAL 浮点数转换为 `T_FIX16` 定点数，调用方指定小数位数 `n`。是定点编码的标准入口。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LREAL_TO_FIX16 : T_FIX16
VAR_INPUT
    in : LREAL;
    n : WORD(0..15) := 15;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `LREAL` | - | 待转换的 LREAL 浮点数 |
| `n` | `WORD(0..15)` | 15 | 目标小数位数（默认 15，最高精度） |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_FIX16` —— 定点编码值，分辨率由 `n` 决定。

## 3. 行为说明

算法：`result := INT(in * 2ⁿ)`（PDF 文末提示'可能产生舍入误差'）。`n` 必须在 0..15；超出 PDF 未定义 ⚠️。`in * 2ⁿ` 若超出 −32768..32767 范围，结果按 INT 截断 ⚠️。PDF 示例：0.6 / 0.25 / 0.75 / 50000.5 在不同 n 下的输出，最大 q15 可能溢出（50000 不能用 Q15 表达）。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `16 bit fixed point number functions (signed)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_FIX16` —— 定点编码值，分辨率由 `n` 决定。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **`|in * 2ⁿ|` 超过 32767 会溢出** —— PDF 未明示 ⚠️
- **舍入误差**：0.6 / 0.1 等无法精确二进制表达的常数会引入误差
- `n` 默认 15，最高精度但范围最小（±1.0）；`n = 0` 范围最大（±32767）但无小数
- 工程上对每路信号固定 n，全局一致以避免运算时频繁 Align

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LREAL_TO_FIX16.xml`](../examples/P_Demo_LREAL_TO_FIX16.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_LREAL_TO_FIX16
VAR
    lrKp         : LREAL := 0.5;
    fp8Kp        : T_FIX16;
    bEncode      : BOOL;
END_VAR

IF bEncode THEN
    // 工程统一使用 Q8 → n = 8
    fp8Kp := LREAL_TO_FIX16(lrKp, 8);
    bEncode := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：HMI 输入 0.5 的比例系数转 Q8 定点供 PID 用。
- **价值**：替代手写 `INT(in * 256)`；附带范围提示和默认 n。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `16 bit fixed point number functions (signed)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.7.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35226251.html
- **同组相关 FC**：见库分类 `16 bit fixed point number functions (signed)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
