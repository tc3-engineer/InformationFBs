# LREAL_TO_FMTSTR
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
| Example | [`examples/P_Demo_LREAL_TO_FMTSTR.xml`](../examples/P_Demo_LREAL_TO_FMTSTR.xml) |

---
## 1. 功能简述

**LREAL → 格式化字符串**：`[ - ]dddd.dddd` 形式。特殊值：`'#INF'`/`'-#INF'`、`'#QNAN'`、`'#OVF'`/`'-#OVF'`（溢出）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LREAL_TO_FMTSTR : STRING(510)
VAR_INPUT
    in : LREAL;
    iPrecision : INT;
    bRound : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `LREAL` | 源浮点数 |
| `iPrecision` | `INT` | 小数位数（0 = 不显示小数） |
| `bRound` | `BOOL` | TRUE = 按精度四舍五入 |

### 返回值

`STRING(510)` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `STRING(510)`。

## 5. 使用注意 / 常见坑

- `iPrecision = 0` 不显示小数；`in = 0` 且 `iPrecision = 0` 返回 `'0'`。
- 四舍五入规则：末位 ≥ 5 进位。
- 结果长度超 510 → 返回 `'#OVF'`/`'-#OVF'`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LREAL_TO_FMTSTR.xml`](../examples/P_Demo_LREAL_TO_FMTSTR.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_LREAL_TO_FMTSTR
VAR
    rResult : STRING(510);
    bRun    : BOOL;
    f : LREAL := 0.46523;
END_VAR

IF bRun THEN
    rResult := LREAL_TO_FMTSTR(f, 2, TRUE);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
