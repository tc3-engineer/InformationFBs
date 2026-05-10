# PSINT_TO_SINT
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `P[TYPE]_TO_[TYPE] converting functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_PSINT_TO_SINT.xml`](../examples/P_Demo_PSINT_TO_SINT.xml) |

---
## 1. 功能简述

**指针解引用**：返回 `POINTER TO SINT` 指针所指变量的值（SINT 类型）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION PSINT_TO_SINT : SINT
VAR_INPUT
    in : POINTER TO SINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `POINTER TO SINT` | 要解引用的指针 |

### 返回值

`SINT` —— 指针所指处的值。

### VAR_IN_OUT

无。

## 3. 行为说明

- 等价于 ST 操作：`result := PSINT_TO_SINT(ADR(v));` ≡ `result := v;`（直接复制）。
- 当指针非空且对齐时，返回所指内存内容；空指针/越界访问行为**未定义**。

## 4. 错误码 / 返回值

返回 `SINT`。**无错误码**——空指针访问会引发 PLC 异常。

## 5. 使用注意 / 常见坑

- **空指针 / 未对齐** → PLC 运行时异常或数据错乱，调用方负责保证指针有效。
- **生命期**：返回的是值拷贝，但若 `in` 指向局部变量，调用方需保证返回前该变量未被释放。
- ST 中等价写法：`PSINT_TO_SINT(ADR(v))` ≡ `v`——本函数主要用于**只能拿到指针的接口**（如 callback、ADS 数据回调）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_PSINT_TO_SINT.xml`](../examples/P_Demo_PSINT_TO_SINT.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_PSINT_TO_SINT
VAR
    rResult : SINT;
    bRun    : BOOL;
    v       : SINT;
END_VAR

IF bRun THEN
    rResult := PSINT_TO_SINT(ADR(v));
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
