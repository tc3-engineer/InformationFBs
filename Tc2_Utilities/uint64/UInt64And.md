# UInt64And

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35178891.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UInt64And.TcPOU`](../examples/P_Demo_UInt64And.TcPOU) |

---

## 1. 功能简述

两个 `T_ULARGE_INTEGER` 的按位与（AND）。常用于 64 位掩码屏蔽。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt64And : T_ULARGE_INTEGER
VAR_INPUT
    ui64a : T_ULARGE_INTEGER;
    ui64b : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `ui64a` | `T_ULARGE_INTEGER` | - | 操作数 A |
| `ui64b` | `T_ULARGE_INTEGER` | - | 操作数 B |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_ULARGE_INTEGER` —— 按位与结果，与位掩码同表示形式。

## 3. 行为说明

函数对 dwHighPart 与 dwHighPart、dwLowPart 与 dwLowPart 分别做 AND 后封装回结构体。位运算无溢出、无副作用、无错误码、单周期完成。常见用法：用 `ULARGE_INTEGER(0, 16#FF)` 做掩码取低 8 位；用 `ULARGE_INTEGER(16#FFFFFFFF, 16#00000000)` 取高 32 位等。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_ULARGE_INTEGER` —— 按位与结果，与位掩码同表示形式。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- 掩码必须也是 `T_ULARGE_INTEGER` 类型；常量请用 `ULARGE_INTEGER(high, low)` 构造
- 若只关心是否有任一位被置位，结合 `UInt64isZero` 判断结果即可
- 想取某段位的整数值，AND 后还需 `UInt64Shr` 右移
- 性能：两个 DWORD AND，等价于一条指令

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt64And.TcPOU`](../examples/P_Demo_UInt64And.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_UInt64And
VAR
    uliStatus    : T_ULARGE_INTEGER;       // 状态寄存器（64 位）
    uliMask      : T_ULARGE_INTEGER;       // 掩码：低 16 位
    uliFaultCode : T_ULARGE_INTEGER;       // 屏蔽后的故障码
    bMaskNow     : BOOL;                   // 触发屏蔽
END_VAR

uliMask := ULARGE_INTEGER(0, 16#0000FFFF);   // 取低 16 位的掩码
IF bMaskNow THEN
    uliFaultCode := UInt64And(uliStatus, uliMask);
    bMaskNow := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：ADS Raw 报文里把状态寄存器的 64 位状态位按掩码取出特定子位段（如故障码低 16 位）。
- **价值**：替代分别 AND 高低 DWORD 两行；语义更清晰。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35178891.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
