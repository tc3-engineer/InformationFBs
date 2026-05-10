# wsLiteral_TO_UTF8
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_wsLiteral_TO_UTF8.xml`](../examples/P_Demo_wsLiteral_TO_UTF8.xml) |

---
## 1. 功能简述

**WSTRING 字面量 → UTF-8 STRING(511)**。WSTRING 字符集（Unicode UTF-16）覆盖范围比 STRING 广，对德语/中文等非 ASCII 字面量首选用此函数。

## 2. 接口定义

### VAR_IN_OUT CONSTANT

```iecst
FUNCTION wsLiteral_TO_UTF8 : STRING(511)
VAR_IN_OUT CONSTANT
    wsLiteral : WSTRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `wsLiteral` | `WSTRING` | 要转换的 WSTRING 字面量 |

### 返回值

`STRING(511)` —— 函数计算结果。

### VAR_IN_OUT

（见 VAR_IN_OUT CONSTANT 节）

## 3. 行为说明

- 调用：`wsLiteral_TO_UTF8(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `STRING(511)`。无独立错误码。

## 5. 使用注意 / 常见坑

- 搭配 `{attribute 'TcEncoding' := 'UTF-8'}` pragma。
- 字面量过长 → 返回空字符串。
- STRING 字面量用 `sLiteral_TO_UTF8`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_wsLiteral_TO_UTF8.xml`](../examples/P_Demo_wsLiteral_TO_UTF8.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_wsLiteral_TO_UTF8
VAR
    rResult : STRING(511);
    bRun    : BOOL;
    sUtf8 : STRING(511);
END_VAR

IF bRun THEN
    rResult := wsLiteral_TO_UTF8(wsLiteral := "café");
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
