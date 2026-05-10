# PTOD_TO_TOD
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
| Example | [`examples/P_Demo_PTOD_TO_TOD.xml`](../examples/P_Demo_PTOD_TO_TOD.xml) |

---
## 1. 功能简述

**指针解引用**：返回 `POINTER TO TOD` 指针所指变量的值（TOD 类型）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION PTOD_TO_TOD : TOD
VAR_INPUT
    in : POINTER TO TOD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `POINTER TO TOD` | 要解引用的指针 |

### 返回值

`TOD` —— 指针所指处的值。

### VAR_IN_OUT

无。

## 3. 行为说明

- 等价于 ST 操作：`result := PTOD_TO_TOD(ADR(v));` ≡ `result := v;`（直接复制）。
- 当指针非空且对齐时，返回所指内存内容；空指针/越界访问行为**未定义**。

## 4. 错误码 / 返回值

返回 `TOD`。**无错误码**——空指针访问会引发 PLC 异常。

## 5. 使用注意 / 常见坑

- **空指针 / 未对齐** → PLC 运行时异常或数据错乱，调用方负责保证指针有效。
- **生命期**：返回的是值拷贝，但若 `in` 指向局部变量，调用方需保证返回前该变量未被释放。
- ST 中等价写法：`PTOD_TO_TOD(ADR(v))` ≡ `v`——本函数主要用于**只能拿到指针的接口**（如 callback、ADS 数据回调）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_PTOD_TO_TOD.xml`](../examples/P_Demo_PTOD_TO_TOD.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_PTOD_TO_TOD
VAR
    rResult : TOD;
    bRun    : BOOL;
    v       : TOD;
END_VAR

IF bRun THEN
    rResult := PTOD_TO_TOD(ADR(v));
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
