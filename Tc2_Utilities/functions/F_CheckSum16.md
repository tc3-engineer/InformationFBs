# F_CheckSum16
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
| Example | [`examples/P_Demo_F_CheckSum16.xml`](../examples/P_Demo_F_CheckSum16.xml) |

---
## 1. 功能简述

**任意数据 16-bit 校验和**：简单累加式校验。可分段累计调用。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_CheckSum16 : WORD
VAR_INPUT
    dwSrcAddr : POINTER TO BYTE;
    cbLen : UDINT;
    wChkSum : WORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `dwSrcAddr` | `POINTER TO BYTE` | 源缓冲指针 |
| `cbLen` | `UDINT` | 源字节数 |
| `wChkSum` | `WORD` | 初始值（0 或上次校验和） |

### 返回值

`WORD` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `WORD`。

## 5. 使用注意 / 常见坑

- 非密码学安全的简易 checksum；安全场景请用 CRC 或 hash。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CheckSum16.xml`](../examples/P_Demo_F_CheckSum16.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_CheckSum16
VAR
    rResult : WORD;
    bRun    : BOOL;
    ar : ARRAY[0..3] OF BYTE := [1,2,3,4];
END_VAR

IF bRun THEN
    rResult := F_CheckSum16(ADR(ar), SIZEOF(ar), 0);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
