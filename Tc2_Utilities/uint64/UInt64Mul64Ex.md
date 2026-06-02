# UInt64Mul64Ex

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35171211.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UInt64Mul64Ex.TcPOU`](../examples/P_Demo_UInt64Mul64Ex.TcPOU) |

---

## 1. 功能简述

带溢出检测的 64 位无符号乘法。乘积仍按模 2⁶⁴ 返回，但同时把 `bOV` 置 TRUE 让调用方决定饱和、报警或抛错。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt64Mul64Ex : T_ULARGE_INTEGER
VAR_INPUT
    multiplicand : T_ULARGE_INTEGER;
    multiplier : T_ULARGE_INTEGER;
END_VAR
VAR_IN_OUT
    bOV : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `multiplicand` | `T_ULARGE_INTEGER` | - | 被乘数 |
| `multiplier` | `T_ULARGE_INTEGER` | - | 乘数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bOV` | `BOOL` | - | 算术溢出标志：TRUE = 溢出（每周期需先清零） |

### 返回值

`T_ULARGE_INTEGER` —— 低 64 位积；`bOV` 反映溢出。

## 3. 行为说明

底层通常用 64×64→128 位乘法指令，检测高 64 位是否非零来判溢出，再返回低 64 位。`bOV` 是 VAR_IN_OUT，每周期开始处建议先清零避免跨周期残留。`bOV = TRUE` 时返回值仍是低 64 位，调用方需手动饱和到 `MAX64`。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_ULARGE_INTEGER` —— 低 64 位积；`bOV` 反映溢出。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- `bOV` 每周期开始处清零
- 饱和需调用方实现：`IF bOV THEN result := ULARGE_INTEGER(16#FFFFFFFF, 16#FFFFFFFF); END_IF;`
- VAR_IN_OUT 不可传立即值
- 性能略低于无 Ex 版（多一条比较），可忽略

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt64Mul64Ex.TcPOU`](../examples/P_Demo_UInt64Mul64Ex.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_UInt64Mul64Ex
VAR
    uliTorque    : T_ULARGE_INTEGER;
    uliAngle     : T_ULARGE_INTEGER;
    uliWork      : T_ULARGE_INTEGER;       // 累计做功
    bOverflow    : BOOL;                   // 溢出报警
    bCompute     : BOOL;
END_VAR

bOverflow := FALSE;                                    // 每周期先清零
IF bCompute THEN
    uliWork := UInt64Mul64Ex(uliTorque, uliAngle, bOverflow);
    IF bOverflow THEN
        // 工程响应：饱和并触发上层报警
        uliWork := ULARGE_INTEGER(16#FFFFFFFF, 16#FFFFFFFF);
    END_IF;
    bCompute := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：计算累计扭矩 × 累计转角，结果可能超 64 位，需溢出报警。
- **价值**：替代手写'先转 LREAL 估算溢出再走整数路径'的判断；一次调用拿乘积 + 溢出位。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.20
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35171211.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
