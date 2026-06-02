# UInt64Add64Ex

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35165067.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UInt64Add64Ex.TcPOU`](../examples/P_Demo_UInt64Add64Ex.TcPOU) |

---

## 1. 功能简述

带溢出检测的 64 位无符号加法。当真实和 ≥ 2⁶⁴ 时仍按 wrap-around 返回结构体，但同时把 `bOV` 置 TRUE，让调用方决定是饱和、报警还是抛错。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt64Add64Ex : T_ULARGE_INTEGER
VAR_INPUT
    augend : T_ULARGE_INTEGER;
    addend : T_ULARGE_INTEGER;
END_VAR
VAR_IN_OUT
    bOV : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `augend` | `T_ULARGE_INTEGER` | - | 被加数 |
| `addend` | `T_ULARGE_INTEGER` | - | 加数 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bOV` | `BOOL` | - | 算术溢出标志：TRUE = 溢出，FALSE = 无溢出（调用方必须每周期初始化为 FALSE） |

### 返回值

`T_ULARGE_INTEGER` —— 低 64 位和；溢出与否由 `bOV` 反映。

## 3. 行为说明

函数行为与 `UInt64Add64` 完全一致（同样按模 2⁶⁴ 截断），区别在于 VAR_IN_OUT 的 `bOV` 标志：发生溢出时函数把 `bOV` 设为 TRUE，未溢出时设为 FALSE。**重要**：`bOV` 是 VAR_IN_OUT 引用变量；下一次调用前如果不显式重置，旧值会被覆盖（OK），但如果在多处函数共享一个 `bOV`，应该在每个 PLC 周期开始处统一清零以避免跨周期残留。返回值始终是 wrap-around 的低 64 位，需要饱和效果须自行根据 `bOV` 切换到 2⁶⁴−1。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_ULARGE_INTEGER` —— 低 64 位和；溢出与否由 `bOV` 反映。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- `bOV` 是 VAR_IN_OUT，每周期开始处先清零再调用，避免跨周期残留
- 调用方需自行处理饱和：`IF bOV THEN result := ULARGE_INTEGER(16#FFFFFFFF, 16#FFFFFFFF); END_IF;`
- 性能略低于无 Ex 版本（多一条比较），但可忽略
- VAR_IN_OUT 引用类型变量必须能取地址（即真实左值），不能传立即常量

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt64Add64Ex.TcPOU`](../examples/P_Demo_UInt64Add64Ex.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_UInt64Add64Ex
VAR
    uliMoneyAccum : T_ULARGE_INTEGER;     // 累计金额（10⁻⁶ 分）
    uliMoneyAdd   : T_ULARGE_INTEGER;     // 本笔金额
    bOverflow     : BOOL;                 // 溢出报警标志
    bAccumulate   : BOOL;                 // 触发一次累加
END_VAR

// 周期开始处清零溢出标志，避免上周期残留误报
bOverflow := FALSE;
IF bAccumulate THEN
    uliMoneyAccum := UInt64Add64Ex(uliMoneyAccum, uliMoneyAdd, bOverflow);
    IF bOverflow THEN
        // 工程响应：饱和到上限 + 触发报警（业务层处理）
        uliMoneyAccum := ULARGE_INTEGER(16#FFFFFFFF, 16#FFFFFFFF);
    END_IF;
    bAccumulate := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：金额累加（10⁻⁶ 分单位）需要检测溢出报警，避免长期累计静默回绕。
- **价值**：替代手写比较 `IF a &gt; (MAX - b) THEN bOV := TRUE; END_IF;` 一段；调用一次同时拿到和与溢出位。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35165067.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
