# TOF

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Timer` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74404771.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_TOF.xml`](../examples/P_Demo_TOF.xml) |

---

## 1. 功能简述

TOF 是**断开延时定时器**（switch-off delay timer）。`IN = TRUE` 时 `Q = TRUE`、`ET = 0`；`IN` 下降沿后 `ET` 以毫秒累加，到达 `PT` 时 `Q` 置 FALSE。

数据占用：**15 字节**。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    IN     : BOOL; (* starts timer with falling edge, resets timer with rising edge *)
    PT     : TIME; (* time to pass, before Q is reset *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `IN` | `BOOL` | 下降沿启动计时；上升沿复位 |
| `PT` | `TIME` | 延时时长（达到此值后 `Q` 置 FALSE） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q   : BOOL; (* is FALSE, PT seconds after IN had a falling edge *)
    ET  : TIME; (* elapsed time *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | `IN = TRUE` 时 TRUE；`IN = FALSE` 且经过 `PT` 后 FALSE |
| `ET` | `TIME` | 自 `IN` 下降沿起经过的时间 |

### VAR_IN_OUT

无。

## 3. 行为说明

- `IN = TRUE`：`Q = TRUE`，`ET = T#0ms`
- `IN` **下降沿** 起：`ET` 累加到 `PT`
- `ET = PT` 且 `IN = FALSE`：`Q = FALSE`，`ET` 保持
- 计时过程中 `IN` 上升：`Q = TRUE`，`ET = T#0ms`（重置）

## 4. 错误码 / 返回值

PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- `PT` 必须用 TIME 字面量（`T#500ms` / `T#2s`）。
- `PT` 上限约 49.7 天（DWORD 毫秒）。需要更长用 `LTOF`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TOF.xml`](../examples/P_Demo_TOF.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_TOF
VAR
    fbTOF      : TOF;
    bMotorReq   : BOOL;   // 电机请求
    bRunning    : BOOL;   // 电机当前运行允许（带断电延时）
    tElapsed    : TIME;   // 下降沿后已经过时间
END_VAR

fbTOF(
    IN := bMotorReq,
    PT := T#5S,
    Q  => bRunning,
    ET => tElapsed
);

// 1. bMotorReq := TRUE → bRunning 立即 TRUE
// 2. bMotorReq := FALSE → bRunning 仍 TRUE，tElapsed 开始累加
// 3. 5 秒后 bRunning 变 FALSE
// 4. 5 秒未到时 bMotorReq 再变 TRUE → tElapsed 立即归零，bRunning 保持 TRUE
```

## 7. 相关

- TON（接通延时）
- TP（脉冲）
- LTOF（LTIME 64 位版）

## 8. 待确认项

无。
