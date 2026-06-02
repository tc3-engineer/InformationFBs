# TP

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Timer` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74407947.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_TP.TcPOU`](../examples/P_Demo_TP.TcPOU) |

---

## 1. 功能简述

`TP` 是 **IEC 61131-3 标准块**之一，实现**脉冲发生器**（pulse timer）。`IN` 上升沿触发一次定长脉冲：`Q := TRUE` 并维持恰好 `PT` 时长，然后自动 `Q := FALSE`——不管这期间 `IN` 是 TRUE 还是 FALSE。脉冲进行中 `IN` 的状态变化**完全不影响**输出，这是 TP 的核心特征：**不可重触发的固定宽度脉冲**。

精度毫秒级，PT 类型 `TIME`（上限 49.7 天），FB 实例占 **14 字节**（比 TON/TOF 少 1 字节）。需要纳秒精度用 `LTP`。

典型用途：按钮短按发出固定时长信号、报警闪烁的"一闪"、电磁阀开 100 ms 关、PLC 内部产生固定占空比时基。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    IN : BOOL;   (* Trigger for Start of the Signal *)
    PT : TIME;   (* The length of the High-Signal in ms *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `IN` | `BOOL` | 上升沿触发一次脉冲；脉冲进行中 `IN` 的任何变化都被忽略 |
| `PT` | `TIME` | 脉冲宽度（`Q` 保持 TRUE 的时长） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q  : BOOL;   (* The pulse *)
    ET : TIME;   (* The current phase of the High-Signal *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | 脉冲输出。`IN` 上升沿后变 TRUE 维持 `PT` 时长，然后自动回 FALSE |
| `ET` | `TIME` | 当前脉冲已经过的时间；`Q = TRUE` 时从 0 累加到 `PT`；`Q = FALSE` 后保持 `PT` 直到 `IN` 回 FALSE 才清零 |

### VAR_IN_OUT

无。

## 3. 行为说明

**完整时序**（每个 PLC 周期调用 FB 一次时）：

1. **初始状态** `IN = FALSE`、`Q = FALSE`、`ET = T#0ms`，等待触发
2. **`IN` 上升沿**：`Q := TRUE`，`ET` 开始累加
3. **`Q = TRUE` 期间**：`ET` 持续累加；**忽略 `IN` 的任何变化**（即使 `IN` 已经变 FALSE，脉冲也继续走完）
4. **`ET` 达到 `PT`**：`Q := FALSE`，`ET` 保持 `PT` 不变
5. **`Q = FALSE` 但 `IN` 仍为 TRUE**：`ET` 保持 `PT`，等待 `IN` 下降
6. **`IN` 下降沿**（脉冲已结束的情况下）：`ET := T#0ms`，回到状态 1，可接受下次上升沿触发
7. **`IN` 在脉冲期间下降**：完全无效，脉冲走完后再看 `IN`；若那时 `IN` 已 FALSE，立刻清零 ET 回状态 1；若 `IN` 仍 TRUE 等其下降

**关键语义**：

- **不可重触发**（non-retriggerable）：脉冲进行中再次给 `IN` 上升沿（哪怕 `IN` 先回落再上升），定时器**不重启**，因为脉冲期间 `IN` 的边沿被屏蔽。这是 TP 与某些 PLC 厂商"可重触发单稳态"块的关键区别。
- **脉冲宽度固定**：无论 `IN` 多短或多长，`Q` 一定恰好 TRUE 持续 `PT` 时长。短按一下按钮可以产生 500 ms 输出脉冲。
- **`ET` 不在结束时立刻清零**：脉冲结束后 `ET` 保持 `PT` 直到 `IN` 回 FALSE。监控 `ET` 时注意区分"正在走"（小于 PT）与"已结束等输入回落"（等于 PT）两种状态。

**时序示意**（PDF 配图的文字版）：

```
IN  ___|‾‾|__________|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|____
       ↑短按       ↑长按（脉冲期间 IN 状态被忽略）
ET  ___|/‾‾‾|‾‾‾|___|/‾‾‾‾‾‾‾‾‾‾‾|‾‾‾‾‾‾‾‾‾‾‾|____
           ↑保持 PT 等 IN 下降    ↑PT 到，Q 落，ET 保持
Q   ___|‾‾‾‾‾‾‾|___|‾‾‾‾‾‾‾‾‾‾‾|_________________
       |--PT---|   |----PT----|
```

## 4. 错误码 / 返回值

`TP` 是标准定时器，**无错误码、无 HRESULT**。状态仅通过 `Q`（脉冲电平）与 `ET`（监视）反映。`PT = T#0ms` 时不产生脉冲（IEC 标准）。

## 5. 使用注意 / 常见坑

- **TP 不是"可重触发单稳态"**：常见误解是"短按按钮发一次脉冲，再短按又发一次"，期望脉冲被新触发重启。实际上脉冲期间所有 `IN` 边沿都被忽略，**第二次触发只能等当前脉冲走完且 `IN` 回 FALSE 之后才生效**。
- **`Q` 必然恰好持续 `PT`**：即使 `IN` 在脉冲期间提前回 FALSE，`Q` 也不会跟着 FALSE——这是"脉冲宽度恒定"的设计意图，不是 bug。
- **要"边沿触发的瞬时脉冲"用 R_TRIG**：如果业务上只想要 "IN 上升沿那一拍"（一个 PLC 周期的 TRUE）作信号，用 `R_TRIG` 而非 `TP`；TP 的最短脉冲也是 `PT` 不能小于一个任务周期。
- **`PT` 必须 ≥ 任务周期**：1 ms 任务下能产生 ≥1 ms 的脉冲；10 ms 任务下 `PT := T#3ms` 实际会被舍入为 10 ms（一个 PLC 周期）。
- **运行中改 `PT` 影响当前脉冲**：脉冲进行中把 PT 改大会延长当前脉冲；改小且当前 `ET` 已超过新 PT，下一周期 `Q` 立即落。建议运行中**不改 PT**。
- **断电不保持**：FB 内部状态非 retain；断电时正在走的脉冲丢失，上电后等下一次 `IN` 上升沿。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TP.TcPOU`](../examples/P_Demo_TP.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：脉冲式电磁阀控制。短按按钮发出一次固定 200 ms 的开阀指令脉冲，
//       不管按钮按多久，阀都只开 200 ms（机械寿命/能耗约束）。
PROGRAM P_Demo_TP
VAR
    fbValvePulse      : TP;
    bOpenValveReq     : BOOL;             // 操作员按钮（在线模拟）
    tValveOpenWidth   : TIME := T#200MS;  // 脉宽固定 200 ms
    bValveCoilEnergize: BOOL;             // 电磁阀线圈驱动
    tPulseElapsed     : TIME;             // 已脉冲时长（监视）
END_VAR

fbValvePulse(
    IN := bOpenValveReq,
    PT := tValveOpenWidth,
    Q  => bValveCoilEnergize,
    ET => tPulseElapsed
);
```

## 7. 业务场景与实际价值

- **场景**：脉冲电磁阀（强制定时开关）、按钮短按发固定信号、报警蜂鸣器响一声、PLC 周期产生固定占空比时基、电容器充电触发后必须维持 100 ms。
- **价值**：业务代码 1 行就拿到"边沿触发、固定宽度、不可重入"的完整脉冲语义；手写需要约 10 行 IF + 上升沿检测 + 计时累加 + 输入屏蔽逻辑。
- **替代方案对比**：
  - **手写**：要正确实现"脉冲期间忽略 IN"需要额外的状态机标志位
  - **`R_TRIG`**：只产生一个 PLC 周期的脉冲，无法定制宽度
  - **`TON` 配置组合**：能近似实现但行为细节（脉冲期间 IN 屏蔽）需要额外逻辑
  - **本 FB**：IEC 标准，定时脉冲首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §3.3.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74407947.html
- **相关 FB**：`TON`、`TOF`、`LTP`（64 位 LTIME 版本）、`R_TRIG`（单周期脉冲）、`BLINK`（连续方波，在 Tc2_Utilities）
