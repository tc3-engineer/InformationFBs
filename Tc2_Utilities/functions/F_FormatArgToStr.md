# F_FormatArgToStr
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
| Example | [`examples/P_Demo_F_FormatArgToStr.xml`](../examples/P_Demo_F_FormatArgToStr.xml) |

---
## 1. 功能简述

**格式化 helper**：`FB_FormatString` 内部使用。把 `T_Arg` 按格式规范输出为字符串（写到 `sOut`）。一般不直接调用。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_FormatArgToStr : UDINT
VAR_INPUT
    bSign : BOOL; (* Sign prefix flag *)
    bBlank : BOOL; (* Blank prefix flag *)
    bNull : BOOL; (* Null prefix flag *)
    bHash : BOOL; (* Hash prefix flag *)
    bLAlign : BOOL; (* FALSE => Right align (default), TRUE => Left align *)
    bWidth : BOOL; (* FALSE => no width padding, TRUE => blank or zeros padding enabled *)
    iWidth : INT; (* Width length parameter *)
    iPrecision : INT; (* Precision length parameter *)
    eFmtType : E_TypeFieldParam;
    arg : T_Arg; (* Format argument *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bSign` | `BOOL` | 强制带符号前缀 |
| `bBlank` | `BOOL` | 正数前补空格 |
| `bNull` | `BOOL` | 前补零 |
| `bHash` | `BOOL` | 0x / 0 前缀（C #） |
| `bLAlign` | `BOOL` | 左对齐标志 |
| `bWidth` | `BOOL` | 启用宽度补齐 |
| `iWidth` | `INT` | 宽度 |
| `iPrecision` | `INT` | 精度（小数位数） |
| `eFmtType` | `E_TypeFieldParam` | 格式类型 |
| `arg` | `T_Arg` | 要格式化的参数 |

### 返回值

`UDINT` —— 函数计算结果。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    sOut : T_MaxString;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sOut` | `T_MaxString` | **输出**：格式化后的字符串（按引用写入） |

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `UDINT`。

## 5. 使用注意 / 常见坑

- 对应 C printf 的格式控制位。
- 用 `F_<type>(value)` 把变量包装为 T_Arg。
- `sOut` 是 VAR_IN_OUT——传变量本身，FB 写入。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_FormatArgToStr.xml`](../examples/P_Demo_F_FormatArgToStr.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_FormatArgToStr
VAR
    rResult : UDINT;
    bRun    : BOOL;
    n : DINT := 42;
    sOut : T_MaxString;
END_VAR

IF bRun THEN
    rResult := F_FormatArgToStr(FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, 0, 0, E_TypeFieldParam.eTypeFieldParam_d, F_DINT(n), sOut := sOut);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
