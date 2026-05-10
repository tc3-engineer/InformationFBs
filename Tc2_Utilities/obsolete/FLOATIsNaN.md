# FLOATIsNaN
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `[Obsolete]` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_FLOATIsNaN.xml`](../examples/P_Demo_FLOATIsNaN.xml) |

---
## 1. 功能简述

⚠️ **已废弃**——请改用 `LrealIsNaN`。

判断 LREAL 是否为 NaN。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FLOATIsNaN : BOOL
VAR_INPUT
    x : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `x` | `LREAL` | 待测值（值传递） |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。
## 3. 行为说明

- 调用 `FLOATIsNaN(rX)`，返回 `BOOL` 类型结果。
- 期望：`FALSE`

## 4. 错误码 / 返回值

返回 `BOOL`。无错误码。

## 5. 使用注意 / 常见坑

- **已废弃**——新代码请用 LrealIsNaN（按引用更高效）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FLOATIsNaN.xml`](../examples/P_Demo_FLOATIsNaN.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FLOATIsNaN
VAR
    bResult : BOOL;
    bRun    : BOOL;
    rX : LREAL;
END_VAR

rX := 3.14;
IF bRun THEN
    bResult := FLOATIsNaN(rX);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 本函数已废弃，仅供兼容旧代码。
