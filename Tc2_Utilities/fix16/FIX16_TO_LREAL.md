# FIX16_TO_LREAL

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `16 bit fixed point number functions (signed)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35227787.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_FIX16_TO_LREAL.TcPOU`](../examples/P_Demo_FIX16_TO_LREAL.TcPOU) |

---

## 1. 功能简述

把 `T_FIX16`（有符号 16 位定点数 / Q-format 定点 INT）转换为 LREAL 浮点。`T_FIX16` 实际是 `INT`：高几位整数 + 低几位小数；具体小数位数由配套的 `n` 参数（构造时）决定。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FIX16_TO_LREAL : LREAL
VAR_INPUT
    in : T_FIX16;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `T_FIX16` | - | 待转换的定点数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`LREAL` —— 解码后的浮点值。

## 3. 行为说明

`T_FIX16` 是 16 位整数，但解读时需要配套的小数位数 `n`。**本函数本身不需要 `n`，因为 PDF 标记 T_FIX16 自带 n 信息**（实际上是 `INT` 加约定）。返回 LREAL = `INT / 2ⁿ`。无溢出（INT 16 位最多 ±32767，LREAL 远大于此）。无 NaN / Inf 风险。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `16 bit fixed point number functions (signed)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`LREAL` —— 解码后的浮点值。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- `T_FIX16` 实际是 `INT`，配套的小数位数 `n` 在构造（`LREAL_TO_FIX16(v, n)`）时确定，无法从 INT 单独还原 —— 调用方必须自己跟踪 n
- PDF 示例里 `result := FIX16_TO_LREAL(FIX16Add(a, b))` 假设 a, b 已含相同 n 信息
- 如果原始 n 与现在解读用的 n 不一致，结果会差 2 的整次幂

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FIX16_TO_LREAL.TcPOU`](../examples/P_Demo_FIX16_TO_LREAL.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FIX16_TO_LREAL
VAR
    fp8Setpoint  : T_FIX16 := 154;        // 0.6 在 Q8 编码 ≈ 154/256 = 0.6015625
    lrDisp       : LREAL;
    bDecode      : BOOL;
END_VAR

IF bDecode THEN
    // 注：解码方必须知道 n（这里 n=8）；本函数不接受 n 参数
    lrDisp := FIX16_TO_LREAL(fp8Setpoint);
    bDecode := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：把 0.6 的定点数（Q8）转回 LREAL 显示，结果为 0.6015625（误差来自 0.6 不能精确表达）。
- **价值**：替代手写 `LREAL(in) / 256.0`；可读性更高，与 `LREAL_TO_FIX16` 对称使用。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `16 bit fixed point number functions (signed)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.7.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35227787.html
- **同组相关 FC**：见库分类 `16 bit fixed point number functions (signed)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
