# UINT64_TO_LREAL

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35200395.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UINT64_TO_LREAL.xml`](../examples/P_Demo_UINT64_TO_LREAL.xml) |

---

## 1. 功能简述

把 TwinCAT 2 旧式 `T_ULARGE_INTEGER`（结构体）转换为 LREAL 浮点数，用于人机界面显示、报表导出或与浮点算法（如 PID）接口。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UINT64_TO_LREAL : LREAL
VAR_INPUT
    in : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `T_ULARGE_INTEGER` | - | 待转换的 64 位无符号整数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`LREAL` —— 数值上等于 `in`，但大于 2⁵³ 时只是最近的浮点近似。

## 3. 行为说明

函数把 dwHighPart × 2³² + dwLowPart 计算为一个 LREAL。LREAL 尾数 52 位（IEEE 754 双精度），所以小于 2⁵³ (≈ 9.007E15) 的整数可精确表达；2⁵³..2⁶⁴ 区间的值会丢精度，最低几位被舍入到最近的偶数（IEEE 754 默认 round-to-nearest-even）。本函数不报错、不抛异常；超过精度阈值只是结果不再'位级精确'。当需要'既要显示也要做精确算术'时，应把 LREAL 仅作显示，算术继续在 `T_ULARGE_INTEGER` 上做。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`LREAL` —— 数值上等于 `in`，但大于 2⁵³ 时只是最近的浮点近似。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- 大于 2⁵³ 时丢精度（被四舍五入到偶数尾数）
- 不要把 LREAL 再转回 `T_ULARGE_INTEGER` 后跟原始值比较；可能不相等
- 用于 HMI 显示时通常无影响；用于算术请保持在整数域
- 无 NaN / Inf 风险（输入是有界整数）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UINT64_TO_LREAL.xml`](../examples/P_Demo_UINT64_TO_LREAL.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_UINT64_TO_LREAL
VAR
    uliEnergy    : T_ULARGE_INTEGER;       // 累计电度（来自电表通讯）
    lrEnergyKWh  : LREAL;                  // HMI 显示用浮点
    bConvert     : BOOL;                   // 触发一次转换
END_VAR

IF bConvert THEN
    // 仅用于显示；精确算术保持在 T_ULARGE_INTEGER 域内
    lrEnergyKWh := UINT64_TO_LREAL(uliEnergy);
    bConvert := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：HMI 上要显示电表累计电度（64 位计数器），需要换成 LREAL 才能让 TPY 上的浮点显示控件正确处理小数位与单位换算。
- **价值**：替代手写 `LREAL(in.dwHighPart) * 4294967296.0 + LREAL(in.dwLowPart)`；一行调用，可读性更高。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35200395.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
