# DWORD_TO_LREALEX
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
| Example | [`examples/P_Demo_DWORD_TO_LREALEX.xml`](../examples/P_Demo_DWORD_TO_LREALEX.xml) |

---
## 1. 功能简述

**DWORD → LREAL（unsigned-safe）**：TC2 ARM 平台原生的 unsigned → LREAL 转换在最高位置 1 时可能错误转为负数。本函数显式保证按正数转换。

**TC3 已不需要这个函数**——TC3 总是把 unsigned 当正数转 LREAL。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION DWORD_TO_LREALEX : LREAL
VAR_INPUT
    in : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `DWORD` | 待转换 DWORD |

### 返回值

`LREAL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `LREAL`。

## 5. 使用注意 / 常见坑

- **仅 TwinCAT 2 ARM 平台需要**。新代码用普通 `<in_type>_TO_LREAL` 即可。
- 存在原因：可让 TC2 → TC3 移植项目编译通过，不必修改源代码。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DWORD_TO_LREALEX.xml`](../examples/P_Demo_DWORD_TO_LREALEX.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_DWORD_TO_LREALEX
VAR
    rResult : LREAL;
    bRun    : BOOL;
    v : DWORD := 16#FF;
END_VAR

IF bRun THEN
    rResult := DWORD_TO_LREALEX(v);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
