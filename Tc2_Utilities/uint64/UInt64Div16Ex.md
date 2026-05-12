# UInt64Div16Ex

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934153483.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UInt64Div16Ex.xml`](../examples/P_Demo_UInt64Div16Ex.xml) |

---

## 1. 功能简述

64 位无符号被除数除以 16 位无符号除数，返回商（`T_ULARGE_INTEGER`），余数通过 VAR_IN_OUT `remainder` 输出。专为'被除数远大于除数、商不会回退到几乎全 0'的场景做硬件加速优化。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt64Div16Ex : T_ULARGE_INTEGER
VAR_INPUT
    dividend : T_ULARGE_INTEGER;
    divisor : WORD;
END_VAR
VAR_IN_OUT
    remainder : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `dividend` | `T_ULARGE_INTEGER` | - | 被除数 |
| `divisor` | `WORD` | - | 除数（16 位无符号） |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `remainder` | `T_ULARGE_INTEGER` | - | 余数（输出）；调用方需要传一个左值变量来接收 |

### 返回值

`T_ULARGE_INTEGER` —— 商；`remainder` 输出余数。

## 3. 行为说明

函数在底层使用 32×64→64 除法或 16×64→64 除法序列。商 = `dividend / divisor`（向零截断），余数 = `dividend mod divisor`（始终 0..divisor-1）。当 `divisor = 0` 时 PDF 未定义结果 ⚠️（实际可能触发硬件异常或返回 0），**调用前必须自检**。`remainder` 即便是 VAR_IN_OUT 也会被函数完全覆盖，调用前无须初始化。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_ULARGE_INTEGER` —— 商；`remainder` 输出余数。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **除以 0 PDF 未定义** ⚠️ —— 调用前必加 `IF divisor &lt;&gt; 0 THEN ... END_IF;`
- 余数是 VAR_IN_OUT，参数侧必须能取地址；常量不行
- 向零截断（与 C/C++ unsigned 除法一致），不是四舍五入
- 性能比 `UInt64Div64Ex` 略快（除数只有 16 位）；若除数动态超过 65535 改用 64-bit 版

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt64Div16Ex.xml`](../examples/P_Demo_UInt64Div16Ex.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_UInt64Div16Ex
VAR
    uliNanos     : T_ULARGE_INTEGER;       // 纳秒时间戳
    wDivider     : WORD := 1000;           // 转毫秒的除数
    uliMillis    : T_ULARGE_INTEGER;       // 商：毫秒数
    uliRemainder : T_ULARGE_INTEGER;       // 余数：剩余纳秒
    bDivide      : BOOL;
END_VAR

IF bDivide AND wDivider <> 0 THEN
    // 除 0 PDF 未定义 → 前置校验
    uliMillis := UInt64Div16Ex(uliNanos, wDivider, uliRemainder);
    bDivide := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：64 位时钟戳（ns）除以 1000 转毫秒、再除以 1000 转秒等小除数链。
- **价值**：替代手写 64 位除法链；硬件指令一次搞定，性能可预测。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.11
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934153483.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
