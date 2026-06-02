# Int64Add64Ex

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit functions (signed)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35207947.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_Int64Add64Ex.TcPOU`](../examples/P_Demo_Int64Add64Ex.TcPOU) |

---

## 1. 功能简述

带溢出检测的有符号 64 位加法。`bOV` 在和超出 [−2⁶³, 2⁶³−1] 时置 TRUE。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION Int64Add64Ex : T_LARGE_INTEGER
VAR_INPUT
    augend : T_LARGE_INTEGER;
    addend : T_LARGE_INTEGER;
END_VAR
VAR_IN_OUT
    bOV : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `augend` | `T_LARGE_INTEGER` | - | 被加数 |
| `addend` | `T_LARGE_INTEGER` | - | 加数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bOV` | `BOOL` | - | 算术溢出标志：TRUE = 溢出（每周期需先清零） |

### 返回值

`T_LARGE_INTEGER` —— 低 64 位和；`bOV` 反映有符号溢出。

## 3. 行为说明

检测有符号溢出（与无符号不同：两正相加变负、或两负相加变正都算溢出）。返回值仍是 wrap-around 的低 64 位。`bOV` 是 VAR_IN_OUT，每周期开始处清零。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit functions (signed)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_LARGE_INTEGER` —— 低 64 位和；`bOV` 反映有符号溢出。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **有符号溢出**：两正变负、两负变正
- `bOV` 每周期清零
- 饱和需手写：`IF bOV THEN result := <正/负 MAX>; END_IF;`

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Int64Add64Ex.TcPOU`](../examples/P_Demo_Int64Add64Ex.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_Int64Add64Ex
VAR
    liAccum      : T_LARGE_INTEGER;
    liDelta      : T_LARGE_INTEGER;
    bOverflow    : BOOL;
    bAdd         : BOOL;
END_VAR

bOverflow := FALSE;                                    // 每周期先清
IF bAdd THEN
    liAccum := Int64Add64Ex(liAccum, liDelta, bOverflow);
    IF bOverflow THEN
        ;   // 业务层报警与饱和
    END_IF;
    bAdd := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：工业计量场景里有符号差值累加，溢出代表传感器故障要报警。
- **价值**：替代手写符号位检测；一次调用同时拿和与溢出位。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit functions (signed)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.8.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35207947.html
- **同组相关 FC**：见库分类 `64 bit functions (signed)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
