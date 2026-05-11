# DWORD_TO_BINSTR

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35085323.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_DWORD_TO_BINSTR.xml`](../examples/P_Demo_DWORD_TO_BINSTR.xml) |

---

## 1. 功能简述

把一个 `DWORD` 整数转成二进制 (base 2)的字符串表示，返回类型为 `T_MaxString`。通过 `iPrecision` 控制**最小显示位数**：实际位数不足时左侧补零，超出时**不截断**完整输出；`in = 0` 且 `iPrecision = 0` 这一组合用作「约定的空输出」——返回 `''`。

内部算法可视为标准的进制转换：反复对 `in` 取模 / 整除 2，将得到的数字位拼接，再前补零至 `iPrecision`。输入位宽 32 决定了能表达的最大值范围（DWORD 最大值约 2^32-1），超过 `T_MaxString = 255` 容量时由调用方保证结果可容纳。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in         : DWORD;
    iPrecision : INT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `DWORD` | — | 待转换的无符号整数值。 |
| `iPrecision` | `INT` | — | 最少显示位数；若实际有效位数少于 `iPrecision` 则左侧补 0；多于 `iPrecision` 则**不截断**完整保留。当 `iPrecision = 0` 且 `in = 0` 时，返回空字符串。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `T_MaxString` | 包含 `in` 的二进制 (base 2)表示的字符串。`in = 0 AND iPrecision = 0` 时为 `''`。 |

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

调用即返回，无内部状态。把 `in` 当作无符号整数解析后，按 2 进制反复取余 / 整除得到每一位字符，再根据 `iPrecision` 决定左侧补零数量。**截断规则**：当数值的实际有效位数大于 `iPrecision` 时，返回值**保留全部有效位**而**非**截断高位——这与许多语言里 printf `%0Nd` 的行为一致。**空输出规则**：仅当 `in = 0` 且 `iPrecision = 0` 时返回空字符串 `''`，便于业务侧用空串判定「零值不显示」。结果字符串最长不超过 `T_MaxString`（255 字节）。

## 4. 错误码 / 返回值

本函数返回类型为 `T_MaxString`（即 `STRING(255)`），无 `bError`、无 `HRESULT`、无错误码。特殊返回值：`in = 0` 且 `iPrecision = 0` 时返回空串 `''`；其他情况下永远返回一个非空的二进制 (base 2)表示。

PDF / InfoSys 均未声明对无效输入的特殊处理。

## 5. 使用注意 / 常见坑

- **`iPrecision` 不是最大长度而是最小长度**：即使设 `iPrecision = 4`，`in = 16#FFFF` 仍会返回完整 `'FFFF'`，业务上想「硬限长」必须自己 `LEFT(s, 4)` 后处理。
- **空字符串特例**：`in = 0 AND iPrecision = 0` 返回 `''`。若业务需要 `'0'` 显示，至少令 `iPrecision = 1`。
- **结果是 `T_MaxString` 不是 `STRING`**：赋给本地 `sBuf : STRING(20)` 等较短字符串变量时编译器会按短长度截断，超出部分丢失（工程经验补充）。
- **不补「0x/16#」前缀**：返回的是裸数字字符串，要前缀需自己 `CONCAT('16#', s)`。


## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DWORD_TO_BINSTR.xml`](../examples/P_Demo_DWORD_TO_BINSTR.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_DWORD_TO_BINSTR
VAR
    nValue       : DWORD := 43981;   // 在线写值改测试输入
    sFormatted   : T_MaxString;     // 主输出（在线 monitor）
END_VAR

// 单行调用：得到至少 6 位的二进制 (base 2)字符串，左侧补 0
sFormatted := DWORD_TO_BINSTR(nValue, 6);

```

## 7. 业务场景与实际价值

- **场景**：日志 / 报表 / HMI 显示 / 通讯协议帧封包时需要把整数转为定长二进制 (base 2)字符串。典型工业用例：MES 上报订单号必须 8 位定长十进制；Modbus ASCII 帧体必须 4 位 hex；故障掩码以 binary 形式打印调试日志。
- **价值**：替代手写 `CONCAT(INT_TO_STRING(x DIV 10), INT_TO_STRING(x MOD 10), ...)` 多步拼装；一行调用搞定补零、保留全长、大小写、空值这四种边界。
- **替代方案对比**：
  - IEC 标准 `DWORD_TO_STRING(x)`：无补零、无进制选择，仅得到十进制无补零形式
  - 手写循环：能做但 5-10 行，易在「`in = 0` 时输出空还是 `'0'`」上踩坑
  - **本函数**：单行、补零规则确定、PDF 列出 4-5 个边界用例

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.25 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35085323.html
- **相关函数**：`BYTE_TO_BINSTR` / `WORD_TO_BINSTR` / `DWORD_TO_BINSTR` / `LWORD_TO_BINSTR` / `PVOID_TO_BINSTR`
