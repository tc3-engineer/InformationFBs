# WORD_TO_FIX16

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `16 bit fixed point number functions (signed)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35229323.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_WORD_TO_FIX16.TcPOU`](../examples/P_Demo_WORD_TO_FIX16.TcPOU) |

---

## 1. 功能简述

把 WORD 按位模式解读为 `T_FIX16`，调用方提供小数位数 `n`。常用于 SDO / 报文里读回的 WORD 重新解读为定点。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION WORD_TO_FIX16 : T_FIX16
VAR_INPUT
    in : WORD;
    n : WORD(0..15);
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `WORD` | - | 16 位定点数的位模式 |
| `n` | `WORD(0..15)` | - | 小数位数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_FIX16` —— 定点数，分辨率为 `n`。

## 3. 行为说明

位模式直接转 INT；`n` 用于跟踪元数据（实际计算时配合 FIX16_TO_LREAL 才用到 n）。PDF 示例：`FIX16_TO_LREAL(WORD_TO_FIX16(2#0000110010000000, 8))` = 12.5。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `16 bit fixed point number functions (signed)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_FIX16` —— 定点数，分辨率为 `n`。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **位模式不变**：WORD 与 INT 在 IEC 等价
- **`n` 必须与编码侧一致** —— 否则数值解读错
- 工程上把 (WORD, n) 视为一个 pair，整段代码保持同 n

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WORD_TO_FIX16.TcPOU`](../examples/P_Demo_WORD_TO_FIX16.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_WORD_TO_FIX16
VAR
    wFromSdo     : WORD := 2#0000110010000000;   // PDF 示例值 = 12.5 in Q8
    fp8Decoded   : T_FIX16;
    lrCheck      : LREAL;
    bDecode      : BOOL;
END_VAR

IF bDecode THEN
    fp8Decoded := WORD_TO_FIX16(wFromSdo, 8);
    lrCheck    := FIX16_TO_LREAL(fp8Decoded);   // 应为 12.5
    bDecode := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：EtherCAT SDO 读回 16 位字，重新解读为 Q8 定点。
- **价值**：替代 `INT_TO_FIX16(WORD_TO_INT(...), n)` 两层转换。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `16 bit fixed point number functions (signed)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.7.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35229323.html
- **同组相关 FC**：见库分类 `16 bit fixed point number functions (signed)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
