# LTON

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Timer (LTIME)` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/9007205317836171.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_LTON.xml`](../examples/P_Demo_LTON.xml) |

---

## 1. 功能简述

LTON 是 **64 位 LTIME 版的接通延时定时器**。语义同 `TON`，但 `PT/ET` 类型为 `LTIME`，纳秒精度。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    IN     : BOOL; (*starts imter with rising edge, resets timer with falling edge*)
    PT     : LTIME; (*time to pass before Q is set.*)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `IN` | `BOOL` | 上升沿启动；下降沿复位（PDF 原文 'imter' 系拼写错误） |
| `PT` | `LTIME` | 延时时长（纳秒精度） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q   : BOOL; (*is TRUE, PT seconds after IN had a rising edge*)
    ET  : LTIME; (*elapsed time since rising edge at IN*)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | `IN = TRUE` 经过 `PT` 后 TRUE |
| `ET` | `LTIME` | 自 `IN` 上升沿起经过的时间 |

### VAR_IN_OUT

无。

## 3. 行为说明

- `IN = FALSE`：`Q = FALSE`，`ET = LTIME#0ns`
- `IN` 上升沿 → `ET` 累加到 `PT` 时 `Q := TRUE`
- 计时未到 `IN` 下降 → `Q = FALSE`，`ET = 0`

## 4. 错误码 / 返回值

PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- PDF 中 VAR_INPUT 注释有拼写错误 `imter`（应为 `timer`），文档逐字保留。
- `PT` 必须用 `LTIME#` 字面量。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LTON.xml`](../examples/P_Demo_LTON.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_LTON
VAR
    fbLTON     : LTON;
    bRawIn      : BOOL;   // 原始输入（可能抖动）
    bStable     : BOOL;   // 稳定后输出
    ltElapsed   : LTIME;   // 已稳定时间
END_VAR

fbLTON(
    IN := bRawIn,
    PT := LTIME#50US,
    Q  => bStable,
    ET => ltElapsed
);

// 1. bRawIn 持续 TRUE 满 50 μs → bStable = TRUE
// 2. bRawIn 中途变 FALSE → ltElapsed 立刻归零，bStable 保持 FALSE
```

## 7. 相关

- TON（32 位 TIME 版）
- LTOF
- LTP

## 8. 待确认项

无。
