# STRING_TO_CSVFIELD
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
| Example | [`examples/P_Demo_STRING_TO_CSVFIELD.xml`](../examples/P_Demo_STRING_TO_CSVFIELD.xml) |

---
## 1. 功能简述

**字符串 → CSV 字段（字符串）**：单引号转双引号，可选加外层引号。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION STRING_TO_CSVFIELD : T_MaxString
VAR_INPUT
    in : T_MaxString;
    bQM : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `T_MaxString` | 源字符串 |
| `bQM` | `BOOL` | TRUE = 加双引号包围 |

### 返回值

`T_MaxString` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `T_MaxString`。

## 5. 使用注意 / 常见坑

- 源不能含 NUL；二进制数据用 `ARG_TO_CSVFIELD`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_STRING_TO_CSVFIELD.xml`](../examples/P_Demo_STRING_TO_CSVFIELD.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_STRING_TO_CSVFIELD
VAR
    rResult : T_MaxString;
    bRun    : BOOL;
    s : T_MaxString := 'a,b,c';
END_VAR

IF bRun THEN
    rResult := STRING_TO_CSVFIELD(s, TRUE);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
