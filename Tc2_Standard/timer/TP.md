# TP

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Timer` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74407947.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_TP.xml`](../examples/P_Demo_TP.xml) |

---

## 1. 功能简述

TP 是**脉冲定时器**（pulse generator），用于产生固定宽度的脉冲。`IN` 上升沿时 `Q` 置 TRUE 并保持 `PT` 时长，`ET` 同时累加；脉冲期内 `IN` 状态变化不影响 `Q`，直到 `PT` 时间走完。

数据占用：**14 字节**。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    IN     : BOOL; (* Trigger for Start of the Signal *)
    PT     : TIME; (* The length of the High-Signal in ms *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `IN` | `BOOL` | 上升沿：启动脉冲、`Q` 置 TRUE |
| `PT` | `TIME` | 脉冲宽度（高电平时长） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q   : BOOL; (* The pulse *)
    ET  : TIME; (* The current phase of the High-Signal *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | `IN` 上升沿后保持 `PT` 的脉冲 |
| `ET` | `TIME` | 自脉冲启动起经过的时间 |

### VAR_IN_OUT

无。

## 3. 行为说明

- `IN = FALSE` 且 `Q = FALSE`：`ET = 0`
- `IN` **上升沿**：`Q := TRUE`，`ET` 开始累加
- 脉冲期内（`Q = TRUE`）：`ET` 继续累加到 `PT`，**不受 `IN` 状态影响**
- `ET = PT`：`Q := FALSE`

## 4. 错误码 / 返回值

PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- 脉冲不可被打断、不可重新触发——这与某些 PLC 厂商的 TP 实现不同。
- `PT` 上限约 49.7 天，需要纳秒级用 `LTP`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TP.xml`](../examples/P_Demo_TP.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_TP
VAR
    fbTP       : TP;
    bSensor     : BOOL;   // 传感器到位（一瞬间 TRUE）
    bPulse      : BOOL;   // 200ms 输出脉冲
    tInPulse    : TIME;   // 脉冲已经过时间
END_VAR

fbTP(
    IN := bSensor,
    PT := T#200MS,
    Q  => bPulse,
    ET => tInPulse
);

// 1. bSensor 给一次上升沿 → bPulse 立即 TRUE 持续 200ms 后自动 FALSE
// 2. 脉冲期内 bSensor 再给上升沿 → **被忽略**（PDF 行为：脉冲完成前不再触发）
// 3. 脉冲期内 bSensor := FALSE 也不会缩短 bPulse
```

## 7. 相关

- TON
- TOF
- LTP（LTIME 版）

## 8. 待确认项

无。
