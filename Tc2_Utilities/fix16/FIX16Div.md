# FIX16Div

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `16 bit fixed point number functions (signed)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35235467.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_FIX16Div.xml`](../examples/P_Demo_FIX16Div.xml) |

---

## 1. 功能简述

两个有符号 16 位定点数相除。分辨率不同时先对齐到低分辨率再除。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FIX16Div : T_FIX16
VAR_INPUT
    dividend : T_FIX16;
    divisor : T_FIX16;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `dividend` | `T_FIX16` | - | 被除数 |
| `divisor` | `T_FIX16` | - | 除数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_FIX16` —— 商，分辨率 = `min(n_dividend, n_divisor)`。

## 3. 行为说明

按 PDF：高分辨率一侧的小数位被截断，再做 INT 除法。`divisor = 0` PDF 未定义 ⚠️。商仍是 T_FIX16（16 位 INT），溢出未明示。PDF 示例 `−22.5 / 10.0` 都为 Q8 → 结果 −2.25。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `16 bit fixed point number functions (signed)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_FIX16` —— 商，分辨率 = `min(n_dividend, n_divisor)`。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **除以 0 PDF 未定义** ⚠️
- 高分辨率一侧小数位被截断（不四舍五入）
- 商可能溢出 16 位 INT，PDF 未明示 ⚠️
- 调用方需跟踪结果分辨率

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FIX16Div.xml`](../examples/P_Demo_FIX16Div.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_FIX16Div
VAR
    fp8A         : T_FIX16;
    fp8B         : T_FIX16;
    fp8Quot      : T_FIX16;
    lrResult     : LREAL;
    bDivide      : BOOL;
END_VAR

fp8A := LREAL_TO_FIX16(-22.5, 8);
fp8B := LREAL_TO_FIX16(10.0, 8);
IF bDivide AND fp8B <> 0 THEN
    fp8Quot  := FIX16Div(fp8A, fp8B);
    lrResult := FIX16_TO_LREAL(fp8Quot);   // 应为 -2.25
    bDivide := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：把两个定点测量量做比值（如电压 / 电流 = 电阻）显示。
- **价值**：替代手写分辨率对齐 + INT 除法。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `16 bit fixed point number functions (signed)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.7.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35235467.html
- **同组相关 FC**：见库分类 `16 bit fixed point number functions (signed)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
