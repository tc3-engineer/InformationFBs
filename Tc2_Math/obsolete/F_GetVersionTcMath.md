# F_GetVersionTcMath
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Math` |
| Library Version | `1.3.3` |
| Type | `FUNCTION` |
| Category | `[obsolete functions]` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetVersionTcMath.xml`](../examples/P_Demo_F_GetVersionTcMath.xml) |

---
## 1. 功能简述

⚠️ **已废弃**——请改用全局常量 `stLibVersion_Tc2_Math`。

旧 API：返回 PLC 库的某个版本元素。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_GetVersionTcMath : UINT
VAR_INPUT
    nVersionElement : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nVersionElement` | `INT` | 1=major、2=minor、3=revision |

### 返回值

`UINT` —— 函数计算结果。

### VAR_IN_OUT

无。
## 3. 行为说明

- `F_GetVersionTcMath(1)` = `返回 major number`

## 4. 错误码 / 返回值

返回 `UINT` 类型的计算结果。无错误码。
## 5. 使用注意 / 常见坑

- **已废弃**——新代码请直接用 `stLibVersion_Tc2_Math`（GVL）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetVersionTcMath.xml`](../examples/P_Demo_F_GetVersionTcMath.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_GetVersionTcMath
VAR
    rResult : UINT;
    bRun    : BOOL;
END_VAR

IF bRun THEN
    rResult := F_GetVersionTcMath(1);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Math README`](../README.md) 同库其他条目

## 8. 待确认项

- 本函数已废弃，仅供兼容旧代码使用。
