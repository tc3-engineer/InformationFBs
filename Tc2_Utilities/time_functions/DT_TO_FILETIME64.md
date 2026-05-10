# DT_TO_FILETIME64
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
| Example | [`examples/P_Demo_DT_TO_FILETIME64.xml`](../examples/P_Demo_DT_TO_FILETIME64.xml) |

---
## 1. 功能简述

把 PLC 的 `DT`（DATE_AND_TIME）变量转为 64-bit FILETIME（自 1601-01-01 起的 100ns 计数）。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION DT_TO_FILETIME64 : T_FILETIME64
VAR_INPUT
    DTIN : DT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `DTIN` | `DT` | DATE_AND_TIME 格式的日期时间 |

### 返回值

`T_FILETIME64` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `DT_TO_FILETIME64(dtIn)`，返回 `T_FILETIME64`。
- 期望：`对应 FILETIME64（约 17 位十进制数）`

## 4. 错误码 / 返回值

返回 `T_FILETIME64`。无独立错误码（部分函数用 0/全 0 结构表示参数无效）。

## 5. 使用注意 / 常见坑

- **T_FILETIME64** 是 LWORD 别名（高低位合并）；旧 `T_FILETIME` 是 lo/hi DWORD 结构。
- DT 仅秒级精度，转出的 FILETIME 毫秒位为 0。
- 反向转换用 `FILETIME64_TO_DT`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DT_TO_FILETIME64.xml`](../examples/P_Demo_DT_TO_FILETIME64.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_DT_TO_FILETIME64
VAR
    rResult : T_FILETIME64;
    bRun    : BOOL;
    dtIn : DT := DT#2024-01-01-12:00:00;
END_VAR

IF bRun THEN
    rResult := DT_TO_FILETIME64(dtIn);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
