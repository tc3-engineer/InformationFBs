# LWORD_TO_ULARGE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934116875.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_LWORD_TO_ULARGE.TcPOU`](../examples/P_Demo_LWORD_TO_ULARGE.TcPOU) |

---

## 1. 功能简述

把 TwinCAT 3 原生的 `LWORD`（64 位无符号位串）按位重新打包成 TwinCAT 2 旧式 `T_ULARGE_INTEGER` 结构体。便于把 TC3 代码里的 64 位寄存器值喂给只接受 legacy 类型的旧库函数。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LWORD_TO_ULARGE : T_ULARGE_INTEGER
VAR_INPUT
    in : LWORD;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `LWORD` | - | 待转换的 TwinCAT 3 原生 64 位无符号值 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`T_ULARGE_INTEGER` —— 与 `in` 数值完全相等的结构体表示。

## 3. 行为说明

本函数只是把 64 位的 LWORD 按高 32 位写入 dwHighPart、低 32 位写入 dwLowPart，不改变数值意义，也没有溢出风险。等价于手写 `result.dwHighPart := DWORD(SHR(in, 32)); result.dwLowPart := DWORD(in);`，但避免读者反复确认位移方向。在与 ADS 报文中按 T_ULARGE_INTEGER 描述的 8 字节字段交互时常用。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `64 bit integer functions (unsigned)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`T_ULARGE_INTEGER` —— 与 `in` 数值完全相等的结构体表示。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- 纯位串重打包：不丢精度，但也不做端序转换；wire 上来的大端字节流必须先 `BE64_TO_HOST` 之类处理
- 把转换结果当 ULINT 用前需调 `ULARGE_TO_ULINT`，直接看 dwHighPart/dwLowPart 容易看错
- 传入 LWORD 表达式时注意优先级，例如 `LWORD_TO_ULARGE(a OR b)` 比拆开两行更清晰

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LWORD_TO_ULARGE.TcPOU`](../examples/P_Demo_LWORD_TO_ULARGE.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_LWORD_TO_ULARGE
VAR
    lwTickCount  : LWORD := 16#FEDCBA9876543210;   // 硬件计数器读回值
    uliResult    : T_ULARGE_INTEGER;                  // 重打包后的结构体
    bRepack      : BOOL;                              // 在线触发
END_VAR

IF bRepack THEN
    // 数值不变只换表示形式，无须额外校验
    uliResult := LWORD_TO_ULARGE(lwTickCount);
    bRepack := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：把硬件计数器累计值（64 位寄存器读回的 LWORD）写入一个按 T_ULARGE_INTEGER 定义的报警阈值结构体里。
- **价值**：替代手写两次位移与 DWORD 强转；函数语义清晰，单元测试覆盖一行就够。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `64 bit integer functions (unsigned)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.9.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934116875.html
- **同组相关 FC**：见库分类 `64 bit integer functions (unsigned)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
