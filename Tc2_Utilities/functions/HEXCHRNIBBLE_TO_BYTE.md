# HEXCHRNIBBLE_TO_BYTE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934088715.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_HEXCHRNIBBLE_TO_BYTE.xml`](../examples/P_Demo_HEXCHRNIBBLE_TO_BYTE.xml) |

---

## 1. 功能简述

把表示 hex nibble（半字节）的单字符字符串（`STRING(1)`）转成其十进制数值（0..15）。例如 `'A'` 返回 10、`'9'` 返回 9。识别范围：`'0'..'9'`、`'a'..'f'`、`'A'..'F'`；其他输入返回 `255`。

与 `HEXASCNIBBLE_TO_BYTE` 的区别仅在入参类型：本函数接受 `STRING(1)`（字符串字面量），后者接受 `BYTE`（ASCII 数值）。从 `STRING` 字面拆字符解析时本函数语义更直观；从字节 buffer 逐字节解析用 `HEXASCNIBBLE_TO_BYTE` 性能更好。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    chr : STRING(1);
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `chr` | `STRING(1)` | — | 单字符字符串，应是 `'0'-'9'` / `'a'-'f'` / `'A'-'F'` 中之一。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BYTE` | 0..15 表示成功；`255` 表示输入非 hex 字符。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数对 `chr` 的首字符按 ASCII 表区段判断：`'0'-'9'` 减 `'0'` 得 0..9；`'A'-'F'` 减 `'A'` 加 10 得 10..15；`'a'-'f'` 减 `'a'` 加 10 得 10..15；其他返回 `255`。

接受的 `STRING(1)` 通常是 `MID(sHex, 1, i)` 抽出的子串或字面量 `'A'`。本函数比 `HEXASCNIBBLE_TO_BYTE` 多一层"字符串到字节"的开销（PLC 字符串首字节就是 ASCII 码，理论上等价，但语义层多一层），所以从大段字节 buffer 解析时优先用 `HEXASCNIBBLE_TO_BYTE`；从 `STRING` 字面或 `MID` 子串解析时本函数更易读，不必显式取 `arHex[0]`。

边界：大小写不敏感；多字符 `STRING(N>1)` 只看首字符；空串 `''` 触发"非 hex" → 255。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| `0` - `15` | 成功，对应 nibble 值 |
| `255` | 输入非 hex 字符（含空串） |

## 5. 使用注意 / 常见坑

- **错误码 255 不是 0**：合法 `'0'` 也返回 0；用 255 判错。
- **`STRING(N>1)` 只看首字符**：传整段 `'1A'` 只解析 `'1'`，调用方要自己 `MID`。
- **`HEXASCNIBBLE_TO_BYTE` 性能更优**：批量解析字节 buffer 用 ASCII 版。
- **`STRING(1)` 字面量要单引号**：`HEXCHRNIBBLE_TO_BYTE('A')` 合法；用双引号 `"A"` 会编译错。
- **整段 hex 用 `HEXSTR_TO_DATA`**：本函数是单 nibble 版。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_HEXCHRNIBBLE_TO_BYTE.xml`](../examples/P_Demo_HEXCHRNIBBLE_TO_BYTE.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_HEXCHRNIBBLE_TO_BYTE
VAR
    sChar : STRING(1) := 'A';
    bVal  : BYTE;                  // 期望 10
END_VAR

bVal := HEXCHRNIBBLE_TO_BYTE(chr := sChar);
```

## 7. 业务场景与实际价值

- **场景**：MES 下发以字符串形式表达的 hex 配置（如 `'FF01'`），PLC 用 `MID` 拆字符再调本函数解析。
- **价值**：从 `STRING` 字面解析时语义更直观（不必显式转字节数组）；大小写不敏感、错误统一返回 255。
- **替代方案对比**：
  - 手写 `IF chr = '0' THEN bVal := 0; ELSIF ...`：16 分支
  - `HEXASCNIBBLE_TO_BYTE` + `arBuffer[i]`：性能更好但代码层多一层
  - 本函数：从 `STRING` 字面解析的首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.48 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934088715.html
- **相关函数**：`HEXASCNIBBLE_TO_BYTE`（接受 `BYTE` 版）、`HEXSTR_TO_DATA`（整段 hex 串转字节数组）
