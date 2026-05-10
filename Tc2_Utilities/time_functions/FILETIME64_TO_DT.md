# FILETIME64_TO_DT
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
| Example | [`examples/P_Demo_FILETIME64_TO_DT.xml`](../examples/P_Demo_FILETIME64_TO_DT.xml) |

---
## 1. 功能简述

把 64-bit FILETIME 转为 PLC 的 `DT`（DATE_AND_TIME）格式。**值范围限制**：`DT#1970-01-01-00:00:00` ~ `DT#2106-02-06-06:28:15`；毫秒被向下取整丢弃。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FILETIME64_TO_DT : DT
VAR_INPUT
    fileTime : T_FILETIME64;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `fileTime` | `T_FILETIME64` | FILETIME 格式时间 |

### 返回值

`DT` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `FILETIME64_TO_DT(ftIn)`，返回 `DT`。
- 期望：`DT#2024-01-01-12:00:00`

## 4. 错误码 / 返回值

返回 `DT`。无独立错误码（部分函数用 0/全 0 结构表示参数无效）。

## 5. 使用注意 / 常见坑

- **值范围**：超出 1970..2106 的 FILETIME 转换会失败/截断（PDF 未明确）。
- 毫秒级精度丢失（DT 只到秒）。
- 反向：`DT_TO_FILETIME64`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FILETIME64_TO_DT.xml`](../examples/P_Demo_FILETIME64_TO_DT.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FILETIME64_TO_DT
VAR
    rResult : DT;
    bRun    : BOOL;
    ftIn : T_FILETIME64;
END_VAR

ftIn := DT_TO_FILETIME64(DT#2024-01-01-12:00:00);
IF bRun THEN
    rResult := FILETIME64_TO_DT(ftIn);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
