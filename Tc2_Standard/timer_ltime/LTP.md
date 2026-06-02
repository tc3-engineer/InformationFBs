# LTP

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Timer (LTIME)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/9007205317837579.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_LTP.TcPOU`](../examples/P_Demo_LTP.TcPOU) |

---

## 1. 功能简述

`LTP` 是 `TP` 的 **64 位 LTIME 版本**——脉冲发生器，纳秒精度脉宽。行为完全等同 `TP`：`IN` 上升沿触发一次定长脉冲，`Q := TRUE` 维持 `PT` 时长，期间 `IN` 状态被忽略，**不可重触发**。

适合需要 μs 级精确脉宽的场景：步进电机驱动信号、PWM 周期内的窗口脉冲、高速 IO 触发。

PT 类型 `LTIME`，字面量 `LTIME#10us`、`LTIME#100ms`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    IN : BOOL;    (*Trigger for Start of the Signal*)
    PT : LTIME;   (*The length of the High- Signal*)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `IN` | `BOOL` | 上升沿触发脉冲；脉冲进行中 `IN` 的变化被忽略 |
| `PT` | `LTIME` | 脉冲宽度，64 位纳秒精度 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q  : BOOL;    (*The pulse*)
    ET : LTIME    (*elapsed time since pulse start*)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | 脉冲输出，`IN` 上升沿后保持 `PT` 时长 |
| `ET` | `LTIME` | 当前脉冲已经过时间；脉冲结束后保持 `PT` 直到 `IN` 回 FALSE 才清零 |

### VAR_IN_OUT

无。

## 3. 行为说明

**完整时序**（与 `TP` 完全镜像，纳秒精度）：

1. **初始**：`Q = FALSE`，`ET = LTIME#0`
2. **`IN` 上升沿**：`Q := TRUE`，`ET` 累加
3. **`Q = TRUE` 期间**：忽略 `IN` 的任何变化
4. **`ET` 达到 `PT`**：`Q := FALSE`，`ET` 钳位
5. **`Q = FALSE` 且 `IN` 仍 TRUE**：等 `IN` 下降
6. **`IN` 下降沿（脉冲已结束）**：`ET := LTIME#0`，回到状态 1

**关键差异**（与 `TP` 比较）：

- 纳秒分辨率（实际仍受任务周期约束）
- 长上限 ~584 年
- `LTIME` 与 `TIME` 不兼容

**其余特性**（不可重触发、脉冲宽度固定、ET 不立即清零等）与 TP 完全一致。

## 4. 错误码 / 返回值

`LTP` 是标准定时器，**无错误码、无 HRESULT**。

## 5. 使用注意 / 常见坑

- **不可重触发**：脉冲进行中 IN 上升沿被屏蔽，与 TP 同。
- **精度受任务周期限制**：μs 任务下才能精确到 μs。常规 1 ms 任务里 LTP 和 TP 等效。
- **PT 类型必须 LTIME**：`PT := T#100ms` 编译失败。
- **`ET` 在脉冲结束后保持 `PT`**：监控 ET 时区分"正在脉冲"（< PT）与"等 IN 回落"（= PT）。
- **运行中改 PT 影响当前脉冲**：建议不改。
- **断电不保持**：脉冲丢失。
- **TP 够用别用 LTP**：内存大、无毫秒级精度优势。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LTP.TcPOU`](../examples/P_Demo_LTP.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：步进电机驱动器需要的脉冲宽度精确到 50 μs。普通 TP 在 1 ms 任务下做不到，
//       配合 NC 任务（50 μs 周期）的 LTP 可以输出 ±1 μs 内的精确脉冲。
PROGRAM P_Demo_LTP
VAR
    fbStepPulse        : LTP;
    bStepTrigger       : BOOL;
    tStepHighWidth     : LTIME := LTIME#50US;
    bStepPulseOut      : BOOL;
    tPulseElapsed      : LTIME;
END_VAR

fbStepPulse(
    IN := bStepTrigger,
    PT := tStepHighWidth,
    Q  => bStepPulseOut,
    ET => tPulseElapsed
);
```

## 7. 业务场景与实际价值

- **场景**：步进电机驱动 STEP 信号生成、激光发射触发脉冲、高速 IO 测试方波、PWM 周期内的窗口选通。
- **价值**：保留 TP 的"定长不可重入脉冲"语义，扩展到纳秒精度。NC / CNC 用户的常用工具。
- **替代方案对比**：
  - **TP**：常规 ms 脉冲首选
  - **NC PTP 输出**：硬件级脉冲串发生器，更精确但配置复杂
  - **本 FB**：软件实现的高精度脉冲，编程灵活

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §3.4.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/9007205317837579.html
- **相关 FB**：`TP`（32 位）、`LTON`、`LTOF`
