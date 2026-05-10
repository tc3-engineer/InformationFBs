# TON

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Timer` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74406539.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_TON.xml`](../examples/P_Demo_TON.xml) |

---

## 1. 功能简述

TON 是**接通延时定时器**（switch-on delay timer）。`IN` 上升沿后开始计时（毫秒级，TIME 类型），累计达到设定时间 `PT` 后输出 `Q` 置 TRUE。`IN` 期间一旦下降则计时器立即复位。

数据占用：**15 字节**。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    IN : BOOL;   (* starts timer with rising edge, resets timer with falling edge *)
    PT : TIME;   (* time to pass, before Q is set *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `IN` | `BOOL` | 上升沿启动计时，下降沿复位 |
| `PT` | `TIME` | 延时时长（达到此值后 `Q` 置 TRUE） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q  : BOOL;   (* is TRUE, PT seconds after IN had a rising edge *)
    ET : TIME;   (* elapsed time *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | `IN = FALSE` 时 FALSE；`IN = TRUE` 且经过 `PT` 时间后 TRUE |
| `ET` | `TIME` | 自 `IN` 上升沿起经过的时间 |

### VAR_IN_OUT

无。

## 3. 行为说明

时序逻辑（PDF 原文规则）：

- `IN = FALSE`：`Q = FALSE`，`ET = T#0ms`
- `IN` **上升沿** 起：`ET` 以毫秒为单位累加，直到 `ET = PT`
- `ET = PT` 且 `IN = TRUE`：`Q = TRUE`，`ET` 保持不再增长
- 计时过程中 `IN` 下降：`Q = FALSE`，`ET = T#0ms`（**未到时间就被中断 → 复位**）

时序图（文字版）：

```
IN  ___|‾‾‾‾‾‾‾‾‾‾‾‾‾‾|________
                  PT
ET  ___|/‾‾‾‾‾‾|‾‾‾‾‾‾‾|________
              到达 PT 后保持
Q   _____________|‾‾‾‾‾|________
                到达 PT 才置 TRUE
```

## 4. 错误码 / 返回值

PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- **PT 必须用 TIME 字面量**：写成 `T#500ms` 或 `T#2s`，不要用裸 INT。
- **不要在 PT 上动态改值**：运行中改变 PT 不会重新开始计时；改变后比较的是当前 ET 与新 PT。需要"重新延时"应让 IN 走一次下降→上升沿。（工程经验补充）
- **TIME 精度**：TwinCAT 任务周期决定最小可观测精度。1ms 任务下定时 0.5ms 没有意义。（工程经验补充）
- **TwinCAT 中 TIME 上限约 49.7 天**（DWORD 毫秒）。需要更长用 `LTON`（LTIME，64 位纳秒）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TON.xml`](../examples/P_Demo_TON.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_TON
VAR
    fbTON      : TON;
    bMotorReq  : BOOL;     // 启动请求
    bRunOk     : BOOL;     // 启动延时完成
    tElapsed   : TIME;     // 已经过时间（监视用）
END_VAR

fbTON(
    IN := bMotorReq,
    PT := T#3S,            // 启动 3 秒后输出
    Q  => bRunOk,
    ET => tElapsed
);

// bMotorReq 持续 TRUE 满 3s → bRunOk 置 TRUE
// 中途 bMotorReq 变 FALSE → bRunOk 立刻 FALSE，ET 清零
```

## 7. 相关

- 同类：`TOF`（断开延时）、`TP`（脉冲）
- 64 位时间版：`LTON`（LTIME 纳秒精度）

## 8. 待确认项

无。
