# LWORD_TO_BASE36STR
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_LWORD_TO_BASE36STR.xml`](../examples/P_Demo_LWORD_TO_BASE36STR.xml) |

---
## 1. 功能简述

**LWORD → Base36 字符串**：使用数字 0-9 加字母 A-Z（共 36 个符号）编码。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LWORD_TO_BASE36STR : T_MaxString
VAR_INPUT
    in : LWORD;
    iPrecision : INT;
    bLoCase : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `LWORD` | 源 LWORD |
| `iPrecision` | `INT` | 最少位数 |
| `bLoCase` | `BOOL` | TRUE = 小写 |

### 返回值

`T_MaxString` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `T_MaxString`。

## 5. 使用注意 / 常见坑

- Base36 比 hex 更紧凑；用于序列号/短 ID 等场景。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LWORD_TO_BASE36STR.xml`](../examples/P_Demo_LWORD_TO_BASE36STR.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_LWORD_TO_BASE36STR
VAR
    rResult : T_MaxString;
    bRun    : BOOL;
    v : LWORD := 16#123456789;
END_VAR

IF bRun THEN
    rResult := LWORD_TO_BASE36STR(v, 8, FALSE);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
