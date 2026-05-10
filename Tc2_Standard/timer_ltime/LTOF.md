# LTOF

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Timer (LTIME)` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/9007205317834763.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_LTOF.xml`](../examples/P_Demo_LTOF.xml) |

---

## 1. 功能简述

LTOF 是 **64 位 LTIME 版的断开延时定时器**。语义同 `TOF`，但 `PT/ET` 类型为 `LTIME`（纳秒精度），上限远高于 49.7 天。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    IN     : BOOL; (*starts timer with falling edge, resets timer with rising edge*)
    PT     : LTIME; (*time to pass before Q is reset*)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `IN` | `BOOL` | 下降沿启动；上升沿复位 |
| `PT` | `LTIME` | 延时时长（纳秒精度） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q   : BOOL; (*is FALSE, PT seconds after IN had a falling edge*)
    ET  : LTIME; (*elapsed time since falling edge at IN*)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | `IN = TRUE` 时 TRUE；`IN` 下降沿后经过 `PT` 时 FALSE |
| `ET` | `LTIME` | 自 `IN` 下降沿起经过的时间 |

### VAR_IN_OUT

无。

## 3. 行为说明

- `IN = TRUE`：`Q = TRUE`，`ET = LTIME#0ns`
- `IN` 下降沿 → `ET` 以纳秒累加，到 `PT` 时 `Q := FALSE`
- 计时过程中 `IN` 上升：`Q = TRUE`，`ET = 0`（重置）

## 4. 错误码 / 返回值

PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- `PT` 必须用 `LTIME#` 字面量（如 `LTIME#100US`、`LTIME#3MS`）。
- 实际可观测精度受 PLC 任务周期限制——1ms 任务下纳秒颗粒不可见。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LTOF.xml`](../examples/P_Demo_LTOF.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_LTOF
VAR
    fbLTOF     : LTOF;
    bEnable     : BOOL;   // 使能输入
    bRunning    : BOOL;   // 断电延时输出
    ltElapsed   : LTIME;   // 已经过时间（纳秒）
END_VAR

fbLTOF(
    IN := bEnable,
    PT := LTIME#3MS,
    Q  => bRunning,
    ET => ltElapsed
);

// 1. bEnable := TRUE → bRunning 立即 TRUE
// 2. bEnable := FALSE → ltElapsed 累加
// 3. 3 ms（LTIME#3MS）后 bRunning 变 FALSE
```

## 7. 相关

- TOF（32 位 TIME 版）
- LTON
- LTP

## 8. 待确认项

无。
