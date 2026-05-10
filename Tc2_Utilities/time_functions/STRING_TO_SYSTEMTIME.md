# STRING_TO_SYSTEMTIME
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
| Example | [`examples/P_Demo_STRING_TO_SYSTEMTIME.xml`](../examples/P_Demo_STRING_TO_SYSTEMTIME.xml) |

---
## 1. 功能简述

把字符串解析为 `TIMESTRUCT`。**输入字符串必须是固定格式** `YYYY-MM-DD-hh:mm:ss.xxx`（年 1601..9999、月 01..12、日 01..31、时 00..23、分秒 00..59、毫秒 000..999）。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION STRING_TO_SYSTEMTIME : TIMESTRUCT
VAR_INPUT
    in : STRING(23);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `STRING(23)` | 格式必须为 `YYYY-MM-DD-hh:mm:ss.xxx` |

### 返回值

`TIMESTRUCT` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `STRING_TO_SYSTEMTIME(sIn)`，返回 `TIMESTRUCT`。
- 期望：`TIMESTRUCT(wYear=2024, ...)`

## 4. 错误码 / 返回值

返回 `TIMESTRUCT`。无独立错误码（部分函数用 0/全 0 结构表示参数无效）。

## 5. 使用注意 / 常见坑

- **格式必须严格匹配**——任何分隔符或位数不对都会得到无效结果（PDF 未明确错误返回）。
- 反向：`SYSTEMTIME_TO_STRING`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_STRING_TO_SYSTEMTIME.xml`](../examples/P_Demo_STRING_TO_SYSTEMTIME.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_STRING_TO_SYSTEMTIME
VAR
    rResult : TIMESTRUCT;
    bRun    : BOOL;
    sIn : STRING(23) := '2024-01-01-12:00:00.000';
END_VAR

IF bRun THEN
    rResult := STRING_TO_SYSTEMTIME(sIn);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
