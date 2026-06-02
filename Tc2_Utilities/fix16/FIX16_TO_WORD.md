# FIX16_TO_WORD

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `16 bit fixed point number functions (signed)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35230859.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_FIX16_TO_WORD.TcPOU`](../examples/P_Demo_FIX16_TO_WORD.TcPOU) |

---

## 1. 功能简述

把 `T_FIX16` 按位模式直接复制为 `WORD`（用于报文打包、SDO 写入等需要'原始 16 位字'的场合）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FIX16_TO_WORD : WORD
VAR_INPUT
    in : T_FIX16;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `T_FIX16` | - | 待转换的定点数（视为 INT 位模式） |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`WORD` —— 16 位位串，与 `in` 位模式相同。

## 3. 行为说明

位模式不变（INT 与 WORD 在 IEC 中位级等价，仅符号语义不同）。负的 T_FIX16 转为 WORD 后得到一个高位置 1 的大无符号数。常配合 `WORD_TO_FIX16` 反向使用，用于 SDO 通讯里把定点编码值放进 WORD 容器。

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `16 bit fixed point number functions (signed)` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

`WORD` —— 16 位位串，与 `in` 位模式相同。

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

- **位模式不变，数值含义变** —— 负定点变大无符号数
- PDF 示例 `LREAL_TO_FIX16(12.5, 8)` 得到的 INT 经 FIX16_TO_WORD 后是 `2#0000110010000000` (= 0x0C80 = 3200)，对应 12.5×256

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FIX16_TO_WORD.TcPOU`](../examples/P_Demo_FIX16_TO_WORD.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FIX16_TO_WORD
VAR
    fp8Kp        : T_FIX16;
    wSdoData     : WORD;                  // 写入 SDO 的 16 位字
    bPack        : BOOL;
END_VAR

// 假设上游已用 LREAL_TO_FIX16(0.5, 8) 得到 fp8Kp
fp8Kp := LREAL_TO_FIX16(0.5, 8);
IF bPack THEN
    wSdoData := FIX16_TO_WORD(fp8Kp);   // 写到 SDO
    bPack := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：把 PID 比例系数（定点）写入 EtherCAT SDO 16 位字段。
- **价值**：替代 `INT_TO_WORD` 显式转换；语义上更明确（来源是定点而非普通整数）。
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `16 bit fixed point number functions (signed)` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.7.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35230859.html
- **同组相关 FC**：见库分类 `16 bit fixed point number functions (signed)`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
