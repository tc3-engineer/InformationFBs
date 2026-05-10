# F_TranslateFileTime64Bias
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
| Example | [`examples/P_Demo_F_TranslateFileTime64Bias.xml`](../examples/P_Demo_F_TranslateFileTime64Bias.xml) |

---
## 1. 功能简述

按指定 bias（分钟）做时区转换。可双向用：UTC↔本地。bias 推荐由 `FB_GetTimeZoneInformation` 取得。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_TranslateFileTime64Bias : T_FILETIME64
VAR_INPUT
    in : T_FILETIME64;
    bias : DINT;
    toUTC : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `T_FILETIME64` | 待转换的输入时间 |
| `bias` | `DINT` | 时区偏移（分钟，可正可负） |
| `toUTC` | `BOOL` | FALSE: UTC→本地（local := UTC - bias）；TRUE: 本地→UTC（UTC := local + bias） |

### 返回值

`T_FILETIME64` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `F_TranslateFileTime64Bias(ftIn, -60, FALSE)`（输入 UTC 10:00，bias=-60 代表 UTC+1 时区），返回 `T_FILETIME64`。
- 按 PDF 公式 `local := UTC - bias` → `10:00 - (-60min) = 11:00`，即对应本地时 11:00 的 FILETIME。
- ⚠️ **bias 的符号约定**：Beckhoff/Windows 用 `UTC = local + bias`，所以 UTC+1（西欧）= bias `-60`，UTC-5（美东）= bias `+300`。直觉上易错。

## 4. 错误码 / 返回值

返回 `T_FILETIME64`。无独立错误码（部分函数用 0/全 0 结构表示参数无效）。

## 5. 使用注意 / 常见坑

- **计算公式**（PDF 原表）：toUTC=FALSE → `local := UTC - bias`；toUTC=TRUE → `UTC := local + bias`。
- **bias 符号约定**：与 Beckhoff/Windows API 一致 `UTC = local + bias`：UTC+1（西欧）→ bias=-60；UTC-5（美东）→ bias=+300。**正负号易踩坑**：常见错误是把 UTC+1 写成 bias=+60，结果时间反向偏移。
- PDF 警告：转换函数计算量大；除非要在线监视才用 DT 类型。
- DST（夏令时）需自行加到 bias 中。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_TranslateFileTime64Bias.xml`](../examples/P_Demo_F_TranslateFileTime64Bias.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_TranslateFileTime64Bias
VAR
    rResult : T_FILETIME64;
    bRun    : BOOL;
    ftIn : T_FILETIME64;
END_VAR

ftIn := DT_TO_FILETIME64(DT#2024-07-15-10:00:00);
IF bRun THEN
    rResult := F_TranslateFileTime64Bias(ftIn, 60, FALSE);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
