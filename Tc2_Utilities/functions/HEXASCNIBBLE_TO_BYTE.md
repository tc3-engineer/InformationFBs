# HEXASCNIBBLE_TO_BYTE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934086795.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_HEXASCNIBBLE_TO_BYTE.xml`](../examples/P_Demo_HEXASCNIBBLE_TO_BYTE.xml) |

---

## 1. 功能简述

把一个表示十六进制 nibble（半字节）字符的 ASCII 码（`BYTE` 类型）转成其十进制数值（0..15）。例如 `asc = 16#41`（即 `'A'`）返回 10；`asc = 16#39`（即 `'9'`）返回 9。识别范围：`'0'..'9'`、`'a'..'f'`、`'A'..'F'`；不在此范围内的输入返回 `255`（错误标志）。

与 `HEXCHRNIBBLE_TO_BYTE` 的区别仅在入参类型：本函数接受 `BYTE`（ASCII 数值），后者接受 `STRING(1)`（单字符字符串）。性能本函数更优，从字节 buffer 逐字节解析 hex 时首选本函数。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    asc : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `asc` | `BYTE` | — | 待转换的 ASCII 码，必须在 `16#30`-`16#39`（`'0'`-`'9'`）或 `16#41`-`16#46`（`'A'`-`'F'`）或 `16#61`-`16#66`（`'a'`-`'f'`）范围内。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BYTE` | 0..15 为成功值；`255` 为错误码（输入超出 hex 字符范围）。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数按 ASCII 表逐区段判断：

- `'0'`(16#30) - `'9'`(16#39) → 返回 `asc - 16#30`，得 0..9
- `'A'`(16#41) - `'F'`(16#46) → 返回 `asc - 16#41 + 10`，得 10..15
- `'a'`(16#61) - `'f'`(16#66) → 返回 `asc - 16#61 + 10`，得 10..15
- 其他 → 返回 `255`（错误）

`255` 作为错误码而不是 `0`，是为了和合法输出 0 区分开（输入 `'0'` 也返回 0，调用方不能用 0 判错）。

性能特性：常数时间、无内存分配，可放在高频解析循环里。常用于把 hex 字符串拆成字节数组（如 IPv6 地址、MAC 地址、协议帧解析）。

边界：
- 大写 / 小写都支持，结果一致
- 不识别 `'#'`、`' '`、`'\0'`：均返回 255
- 不接受 unicode / 多字节字符

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| `0` - `15` | 成功，为对应 nibble 值 |
| `255` | 输入非 hex 字符 |

## 5. 使用注意 / 常见坑

- **错误码是 255 不是 0**：用 `IF result = 255 THEN error` 判错，不能用 `> 15`（虽然实际只有 0..15 与 255 两种取值）。
- **接收 ASCII 数值不是字符串**：`asc := BYTE#(STRING_TO_BYTE('A'))` 错；应该 `asc := 16#41` 或 `asc := arBuffer[i]`。
- **解析 hex 字符串通常先把 STRING 当字节数组**：`arHex : ARRAY[0..N] OF BYTE; MEMCPY(ADR(arHex), ADR(sHex), LEN(sHex));` 后逐字节调本函数。
- **整段 hex 串到字节数组用 `HEXSTR_TO_DATA`**：本函数是单 nibble 版；整段转换用 `HEXSTR_TO_DATA` 更便利（支持空格分隔）。
- **拼字节需要两个 nibble**：高 nibble + 低 nibble；`byte := SHL(highNib, 4) OR lowNib`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_HEXASCNIBBLE_TO_BYTE.xml`](../examples/P_Demo_HEXASCNIBBLE_TO_BYTE.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_HEXASCNIBBLE_TO_BYTE
VAR
    bAsciiA : BYTE := 16#41;     // ASCII 'A'
    bValue  : BYTE;              // 期望 10
END_VAR

bValue := HEXASCNIBBLE_TO_BYTE(asc := bAsciiA);
```

## 7. 业务场景与实际价值

- **场景**：自定义协议帧的 hex 字符串字段（如 `'1A2B3C'`）需要逐 nibble 解析成字节数组，再写入控制寄存器。
- **价值**：单调用、常数时间、识别大小写；比手写 `CASE` 分支快、对错误统一返回 255。
- **替代方案对比**：
  - 手写 `IF asc >= '0' AND asc <= '9' THEN ... ELSIF ...`：5+ 行
  - 用 `STRING_TO_BYTE` 把单字符转换：不识别 hex，要先 `'$16'` 加前缀
  - 本函数：单调用、专为 hex nibble 优化

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.47 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934086795.html
- **相关函数**：`HEXCHRNIBBLE_TO_BYTE`（接受 `STRING(1)` 版）、`HEXSTR_TO_DATA`（整段 hex 串转字节数组）、`DATA_TO_HEXSTR`（反向）
