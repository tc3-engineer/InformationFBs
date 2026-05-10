# F_BIGTYPE
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `T_Arg help functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BIGTYPE.xml`](../examples/P_Demo_F_BIGTYPE.xml) |

---
## 1. 功能简述

**专用包装**：把 Struct / Array 这类复合类型变量按指针 + 长度形式包装为 `T_Arg`。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_BIGTYPE : T_Arg
VAR_INPUT
    pData : POINTER TO BYTE;
    cbLen : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pData` | `POINTER TO BYTE` | 数据起始地址（用 ADR 取） |
| `cbLen` | `DWORD` | 字节长度（用 SIZEOF 取） |

### 返回值

`T_Arg` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `F_BIGTYPE(ADR(stData), SIZEOF(stData))`，返回 `T_Arg`。
- 期望：`T_Arg{pData, len, type=BIG}`

## 4. 错误码 / 返回值

返回 `T_Arg`。无独立错误码。

## 5. 使用注意 / 常见坑

- 用法：`F_BIGTYPE(ADR(stMyStruct), SIZEOF(stMyStruct))`。
- 适合不能用 typed-wrapper 的复合类型。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BIGTYPE.xml`](../examples/P_Demo_F_BIGTYPE.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_BIGTYPE
VAR
    rResult : T_Arg;
    bRun    : BOOL;
    stData : ARRAY[0..3] OF DWORD;
END_VAR

IF bRun THEN
    rResult := F_BIGTYPE(ADR(stData), SIZEOF(stData));
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
