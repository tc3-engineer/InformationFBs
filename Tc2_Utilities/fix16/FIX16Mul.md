# FIX16Mul

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `16 bit fixed point number functions (signed)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35237003.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_FIX16Mul.xml`](../examples/P_Demo_FIX16Mul.xml) |

---

## 1. 功能简述

两个有符号 16 位定点数相乘。分辨率不同时先对齐到低分辨率再乘。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FIX16Mul : T_FIX16
VAR_INPUT
    multiA : T_FIX16;
    multiB : T_FIX16;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `multiA` | `T_FIX16` | - | 第一乘数 |
| `multiB` | `T_FIX16` | - | 第二乘数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_FIX16` —— 积，分辨率 = `min(n_A, n_B)`。

## 3. 行为说明

高分辨率一侧截断小数位，再做 INT 乘法。结果仍 16 位 INT，可能溢出（如 0.25 * 0.25 在 Q4 下结果 = 1 / 16，但 25 * 25 = 625 在 Q4 编码里要表示 1/16 实际为 1，超过 Q4 表示范围则截断 ⚠️）。PDF 示例 `0.25 * 10.0` 都 Q8 → 2.5。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `16 bit fixed point number functions (signed)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_FIX16` —— 积，分辨率 = `min(n_A, n_B)`。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **积可能溢出 16 位 INT** —— 大数相乘前最好先做范围估计
- 高分辨率一侧小数位截断
- 调用方跟踪结果分辨率

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FIX16Mul.xml`](../examples/P_Demo_FIX16Mul.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_FIX16Mul
VAR
    fp8A         : T_FIX16;
    fp8B         : T_FIX16;
    fp8Prod      : T_FIX16;
    lrResult     : LREAL;
    bMul         : BOOL;
END_VAR

fp8A := LREAL_TO_FIX16(0.25, 8);
fp8B := LREAL_TO_FIX16(10.0, 8);
IF bMul THEN
    fp8Prod  := FIX16Mul(fp8A, fp8B);
    lrResult := FIX16_TO_LREAL(fp8Prod);   // 应为 2.5
    bMul := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：把 PID 的比例系数（定点）× 误差（定点）= 输出（定点）。
- **价值**：替代手写对齐 + INT 乘法。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `16 bit fixed point number functions (signed)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.7.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35237003.html
- **同组相关 FC**：见库分类 `16 bit fixed point number functions (signed)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
