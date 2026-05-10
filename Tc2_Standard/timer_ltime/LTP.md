# LTP

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Timer (LTIME)` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/9007205317837579.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_LTP.xml`](../examples/P_Demo_LTP.xml) |

---

## 1. 功能简述

LTP 是 **64 位 LTIME 版的脉冲定时器**。语义同 `TP`，但 `PT/ET` 类型为 `LTIME`，可生成纳秒级窄脉冲。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    IN     : BOOL; (*Trigger for Start of the Signal*)
    PT     : LTIME; (*The length of the High- Signal*)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `IN` | `BOOL` | 上升沿启动脉冲 |
| `PT` | `LTIME` | 脉冲宽度 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q   : BOOL; (*The pulse*)
    ET  : LTIME; (*elapsed time since pulse start*)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | 脉冲输出 |
| `ET` | `LTIME` | 自脉冲启动起经过的时间 |

### VAR_IN_OUT

无。

## 3. 行为说明

- `IN = FALSE` 且 `Q = FALSE` → `ET = LTIME#0ns`
- `IN` 上升沿 → `Q := TRUE`，`ET` 累加
- 脉冲期内 `IN` 变化不影响 `Q`，直到 `ET = PT` 才 `Q := FALSE`

## 4. 错误码 / 返回值

PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- 脉冲一旦启动不可中断、不可重新触发。
- 实际可观测精度受任务周期限制。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LTP.xml`](../examples/P_Demo_LTP.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_LTP
VAR
    fbLTP      : LTP;
    bTrigger    : BOOL;   // 触发输入
    bPulse      : BOOL;   // 100 μs 脉冲输出
    ltInPulse   : LTIME;   // 脉冲已经过时间
END_VAR

fbLTP(
    IN := bTrigger,
    PT := LTIME#100US,
    Q  => bPulse,
    ET => ltInPulse
);

// 1. bTrigger 上升沿 → bPulse TRUE 持续 100 μs 后自动 FALSE
// 2. 脉冲期内再触发会被忽略
```

## 7. 相关

- TP（32 位 TIME 版）
- LTON
- LTOF

## 8. 待确认项

无。
