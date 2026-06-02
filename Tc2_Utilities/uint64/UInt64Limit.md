# UInt64Limit

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35188107.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UInt64Limit.TcPOU`](../examples/P_Demo_UInt64Limit.TcPOU) |

---

## 1. 功能简述

对 64 位无符号整数做上下限限幅（saturate）：低于 `ui64min` 返回 `ui64min`，高于 `ui64max` 返回 `ui64max`，否则返回 `ui64in`。等价于 `MAX(ui64min, MIN(ui64in, ui64max))`，但一次调用更易读。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt64Limit : T_ULARGE_INTEGER
VAR_INPUT
    ui64min : T_ULARGE_INTEGER;
    ui64in : T_ULARGE_INTEGER;
    ui64max : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `ui64min` | `T_ULARGE_INTEGER` | - | 下界 |
| `ui64in` | `T_ULARGE_INTEGER` | - | 待限幅的输入 |
| `ui64max` | `T_ULARGE_INTEGER` | - | 上界 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_ULARGE_INTEGER` —— 裁剪后的值，保证落在 [ui64min, ui64max]。

## 3. 行为说明

函数先与下界比较再与上界比较，分支选择三态结果。要求 `ui64min ≤ ui64max`；若调用方传入颠倒的边界，PDF 未定义 ⚠️。无副作用、单周期。常用于工业设定值限幅（如电机速度上限）、ADS 数据回写前的安全裁剪、HMI 输入范围保护。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_ULARGE_INTEGER` —— 裁剪后的值，保证落在 [ui64min, ui64max]。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **调用方必须保证 `ui64min ≤ ui64max`** ⚠️ —— PDF 没说颠倒时行为
- 无符号语义，没有负边界
- 如果 `ui64min = 0` 且 `ui64max = MAX64`，函数永远返回 `ui64in`（恒等）
- 实际生产中常包一层 FB，把 min/max 当常量配置项

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt64Limit.TcPOU`](../examples/P_Demo_UInt64Limit.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_UInt64Limit
VAR
    uliRpmMin    : T_ULARGE_INTEGER;       // 转速下限 100
    uliRpmMax    : T_ULARGE_INTEGER;       // 转速上限 5000
    uliHmiInput  : T_ULARGE_INTEGER;       // 操作员输入
    uliRpmSafe   : T_ULARGE_INTEGER;       // 限幅后
    bLimit       : BOOL;
END_VAR

uliRpmMin := ULARGE_INTEGER(0, 100);
uliRpmMax := ULARGE_INTEGER(0, 5000);
IF bLimit THEN
    // 防止操作员误输入超界值打坏机械
    uliRpmSafe := UInt64Limit(uliRpmMin, uliHmiInput, uliRpmMax);
    bLimit := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：HMI 操作员输入电机转速设定值，必须裁剪到机械允许的最大转速 5000 rpm = 5000，最小 100。
- **价值**：替代手写两次 `UInt64Cmp64` + 嵌套 IF；一次调用语义清晰。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.15
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35188107.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
