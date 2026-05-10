# SYSTEMTIME_TO_DT
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_SYSTEMTIME_TO_DT.xml`](../examples/P_Demo_SYSTEMTIME_TO_DT.xml) |

---
## 1. 功能简述

TIMESTRUCT 转 PLC 的 `DT`。**毫秒会被向上取整**到秒；如不希望取整，请把 `wMilliseconds` 设 0。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION SYSTEMTIME_TO_DT : DT
VAR_INPUT
    TIMESTR : TIMESTRUCT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `TIMESTR` | `TIMESTRUCT` | Windows SYSTEMTIME 结构 |

### 返回值

`DT` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `SYSTEMTIME_TO_DT(stIn)`，返回 `DT`。
- 期望：`DT#2024-01-01-12:00:00`

## 4. 错误码 / 返回值

返回 `DT`。无独立错误码（部分函数用 0/全 0 结构表示参数无效）。

## 5. 使用注意 / 常见坑

- **毫秒向上取整**：500ms 会变下一秒——如不要取整须先清零。
- 反向：`DT_TO_SYSTEMTIME`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SYSTEMTIME_TO_DT.xml`](../examples/P_Demo_SYSTEMTIME_TO_DT.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_SYSTEMTIME_TO_DT
VAR
    rResult : DT;
    bRun    : BOOL;
    stIn : TIMESTRUCT;
END_VAR

stIn.wYear := 2024; stIn.wMonth := 1; stIn.wDay := 1; stIn.wHour := 12;
IF bRun THEN
    rResult := SYSTEMTIME_TO_DT(stIn);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
