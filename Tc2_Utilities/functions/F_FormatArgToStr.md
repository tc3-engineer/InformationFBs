# F_FormatArgToStr

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35116043.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_FormatArgToStr.xml`](../examples/P_Demo_F_FormatArgToStr.xml) |

---

## 1. 功能简述

格式化辅助函数（format helper）。把一个 `T_Arg` 描述的 PLC 变量按 C 风格的格式控制（宽度、精度、对齐、零填充、符号位、`#` 前缀、类型字段 `eFmtType`）转成字符串，写入 `sOut`（`VAR_IN_OUT`）。`FB_FormatString` 内部就是循环调本函数来处理 `%X` `%d` `%5.2f` 等占位符的每一个，再串成最终格式串。

直接调本函数适用于"我自己控制好格式参数、单独格式化一个字段"的场景；做整段格式化模板（`'X = %d, Y = %.2f'`）更建议用 `FB_FormatString`，参数语义更直观。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
   bSign      : BOOL;(* Sign prefix flag *)
   bBlank     : BOOL;(* Blank prefix flag *)
   bNull      : BOOL;(* Null prefix flag *)
   bHash      : BOOL;(* Hash prefix flag *)
   bLAlign    : BOOL;(* FALSE => Right align (default), TRUE => Left align *)
   bWidth     : BOOL;(* FALSE => no width padding, TRUE => blank or zeros padding enabled *)
   iWidth     : INT;(* Width length parameter *)
   iPrecision : INT;(* Precision length parameter *)
   eFmtType   : E_TypeFieldParam;    (* Format type field parameter *)
   arg        : T_Arg;(* Format argument *)
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bSign` | `BOOL` | — | 符号 flag：`TRUE` 时正数前显式加 `+`（对应 `%+d`）。 |
| `bBlank` | `BOOL` | — | 空白 flag：`TRUE` 时正数前留一个空格（对应 `% d`）。 |
| `bNull` | `BOOL` | — | 零填充 flag：`TRUE` 时宽度不足部分用 `0` 填充（对应 `%0d`）。 |
| `bHash` | `BOOL` | — | `#` 前缀 flag：`TRUE` 时按类型加前缀（对应 `%#x` → `0x...`）。 |
| `bLAlign` | `BOOL` | — | 对齐：`FALSE` 右对齐（默认），`TRUE` 左对齐。 |
| `bWidth` | `BOOL` | — | 是否启用宽度：`FALSE` 不填充；`TRUE` 时按 `iWidth` + `bNull` 填充。 |
| `iWidth` | `INT` | — | 字段最小宽度。 |
| `iPrecision` | `INT` | — | 精度：浮点小数位数；字符串截断长度等。 |
| `eFmtType` | `E_TypeFieldParam` | — | 类型字段（枚举）：选择 d/x/X/o/b/f/e/g/s 等格式（详见 `E_TypeFieldParam` 文档）。 |
| `arg` | `T_Arg` | — | 待格式化的变量描述（用 `F_BYTE` / `F_WORD` / `F_DWORD` / `F_LWORD` / `F_SINT` / `F_INT` / `F_DINT` / `F_LINT` / `F_USINT` / `F_UINT` / `F_UDINT` / `F_ULINT` / `F_STRING` / `F_REAL` / `F_LREAL` 等辅助函数构造）。 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
   sOut     : T_MaxString;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `sOut` | `T_MaxString` | 输出格式化后的字符串；调用前不必清空，函数内部按宽度策略写入。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `UDINT` | 格式化错误码（详见 `E_FormatErrorCodes` / "Format error codes" 表）；成功时为 0。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数按以下顺序处理：

1. **读取 `arg`**：从 `T_Arg` 取变量地址 + 类型 enum + 容量。
2. **按 `eFmtType` 选格式器**：`d` 用十进制、`x` / `X` 用十六进制、`f` / `e` / `g` 用浮点等。
3. **应用前缀 flag**：`bSign` / `bBlank` 处理符号；`bHash` 处理 `0x` / `0b` / `0` 等前缀。
4. **应用宽度策略**：`bWidth = TRUE` 时按 `iWidth` 补齐；`bNull = TRUE` 用 `0` 填，否则空格；`bLAlign = TRUE` 时左对齐（填充在右）。
5. **应用精度**：浮点按 `iPrecision` 小数位；字符串按 `iPrecision` 截断；整数 `iPrecision` 决定最小位数（不足补 `0`）。
6. **写入 `sOut`**：覆盖式写入；`sOut` 容量不足时返回错误码。
7. **返回**：成功返回 0；错误时返回相应错误码（精度无效、类型与 arg 不匹配等）。

`E_TypeFieldParam` 与 `printf` 的 conversion specifier 一一对应；具体枚举值见 PDF "E_TypeFieldParam" 章节。

应用建议：除非要做超细粒度控制（按业务规则动态切对齐 / 宽度），普通格式化用 `FB_FormatString` 写 `'X=%5.2f Y=%-10s'` 这类模板可读性更好；本函数面向 `FB_FormatString` 内部及高级用户。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| `0` | 成功 |
| 非 0 | 格式错误码（参见 PDF / InfoSys 的 "Format error codes" 章节，含精度溢出、宽度超过 `T_MaxString` 容量、类型 mismatch 等） |

## 5. 使用注意 / 常见坑

- **必须用 `F_xxx` 辅助函数构造 `T_Arg`**：手填 `T_Arg` 字段易在类型 enum 上出错；`F_INT(myInt)` 等更安全。
- **`sOut` 是 `VAR_IN_OUT`**：调用方提供一个 `T_MaxString` 变量（容量 255）；不要传字面量字符串。
- **`bWidth = FALSE` 时 `iWidth` / `bNull` / `bLAlign` 全部失效**：要用宽度策略必须先打开 `bWidth`。
- **`eFmtType` 必须和 `arg` 的实际类型匹配**：用 `F_REAL(x)` 但 `eFmtType = E_TypeFieldParam.d`（整数）会返回错误码（工程经验补充）。
- **优先选 `FB_FormatString`**：业务侧多字段格式化用模板字符串可读性强；本函数主要给库内部 / 高级用户用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_FormatArgToStr.xml`](../examples/P_Demo_F_FormatArgToStr.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_FormatArgToStr
VAR
    rTemp        : LREAL := 25.376;
    sOut         : T_MaxString;
    nFormatError : UDINT;
END_VAR

nFormatError := F_FormatArgToStr(
    bSign      := FALSE, bBlank := FALSE, bNull := FALSE, bHash := FALSE,
    bLAlign    := FALSE,
    bWidth     := TRUE,
    iWidth     := 8,
    iPrecision := 2,
    eFmtType   := E_TypeFieldParam.fix_e,    // 'f' 小数格式
    arg        := F_LREAL(rTemp),
    sOut       := sOut);
// sOut 大致是 '   25.38'，长度 8，右对齐
```

## 7. 业务场景与实际价值

- **场景**：日志行需要按固定宽度对齐温度值（用于眼睛对齐查表）：`'CH1: 25.38°C'` `'CH2:  5.10°C'` 都占同样宽度。
- **价值**：替代手写 `LREAL_TO_FMTSTR` + 空格补齐 + 截断的多步代码；单调用完成宽度/精度/对齐三件事。
- **替代方案对比**：
  - `LREAL_TO_FMTSTR(rTemp, 2, TRUE)`：只能控制精度和小数，不能控制宽度
  - 手写 `CONCAT` + 空格补齐：5-10 行，易在边界（负数符号位）出错
  - `FB_FormatString`：业务推荐，模板字符串可读性更好
  - 本函数：精细控制单字段格式时用

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.35 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35116043.html
- **相关 FB / 类型**：`FB_FormatString`（用模板字符串调本函数）、`E_TypeFieldParam`（格式类型枚举）、`T_Arg`（变量描述）、`F_BYTE` / `F_WORD` / `F_DWORD` / `F_LWORD` / `F_SINT` / `F_INT` / `F_DINT` / `F_LINT` / `F_USINT` / `F_UINT` / `F_UDINT` / `F_ULINT` / `F_STRING` / `F_REAL` / `F_LREAL`（`T_Arg` 构造辅助）
