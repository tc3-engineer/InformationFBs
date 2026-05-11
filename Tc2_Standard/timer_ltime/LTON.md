# LTON

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Timer (LTIME)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/9007205317836171.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_LTON.xml`](../examples/P_Demo_LTON.xml) |

---

## 1. 功能简述

`LTON` 是 `TON` 的 **64 位 LTIME 版本**——接通延时定时器，精度从毫秒提升到纳秒，时长上限从 49.7 天扩展到约 584 年。行为完全等同 `TON`：`IN` 上升沿启动，`ET` 累加到 `PT` 后 `Q` 置 TRUE，`IN` 下降沿立即复位。仅时间分辨率与上限不同。

由于内部用 `LTIME`（64 位无符号纳秒），适合**高精度长延时**场景：μs 级伺服时序、长周期保养计时（数月）、跨年累计运行时长统计。

PT 类型 `LTIME`，字面量写法 `LTIME#100us`、`LTIME#5s500ms`、`LTIME#365d`。注意 `LTIME` 与 `TIME` **不可隐式互转**，混用会编译失败。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    IN : BOOL;    (*starts imter with rising edge, resets timer with falling edge*)
    PT : LTIME;   (*time to pass before Q is set.*)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `IN` | `BOOL` | 上升沿启动计时；下降沿立即复位（`ET := LTIME#0`，`Q := FALSE`） |
| `PT` | `LTIME` | 延时时长，64 位纳秒精度，上限约 584 年 |

> 注：PDF 中的 `imter` 是原文拼写错误（应为 `timer`），此处逐字保留 PDF 原文。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q  : BOOL;    (*is TRUE, PT seconds after IN had a rising edge*)
    ET : LTIME    (*elapsed time since rising edge at IN*)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | `IN = TRUE` 且 `ET ≥ PT` 时为 TRUE；其余为 FALSE |
| `ET` | `LTIME` | 自 `IN` 上升沿起累加的纳秒数；达到 `PT` 后钳位 |

### VAR_IN_OUT

无。

## 3. 行为说明

整个时序逻辑与 `TON` 完全镜像，唯一差异在于时间分辨率与上限——LTIME 是 64 位无符号纳秒。`IN` 上升沿启动定时器开始累加 ET，`ET` 累加到等于或超过 `PT` 那一刻 `Q` 置 TRUE 同时 ET 被钳位不再增长；`IN` 下降沿瞬间复位定时器，`ET` 清零并且 `Q` 立刻回 FALSE。整个状态机不存在"暂停继续累计"语义，中途打断必然清零重新数。

实际精度由 PLC 任务周期决定：FB 是被调用时才更新 ET，10 ms 任务下即使 PT 写 `LTIME#100us` 也至少要 10 ms 才能更新一次 ET，精度上不去。LTON 的精度优势仅在 μs 级任务（典型为 NC/CNC 任务，常用 50–250 μs）才能发挥。注意 `LTIME` 与 `TIME` 是两个不能隐式互转的类型，业务里把 `T#5s` 直接赋给 LTON 的 PT 会编译报错，必须用 `TIME_TO_LTIME(T#5s)` 或写成 `LTIME#5s`。运行中改 PT 不会触发"重新计时"，仅是改比较门限。

**关键差异**（与 `TON` 比较）：

- **精度**：理论上纳秒级，但实际仍受 PLC 任务周期限制。1 ms 任务下即使用 LTON 也只能精确到 ~1 ms。
- **时长**：可设 `LTIME#365d`、`LTIME#10y` 等；TON 写 `T#365d` 会溢出。
- **不可重新触发**：与 TON 一样，`IN` 必须先下降再上升才能重新计时。
- **TIME 与 LTIME 不兼容**：业务里要用 `LREAL` 或 `ULINT` 中转时小心；`PT := T#5s` 会编译错。

**时序示意**（与 TON 同形）：

```
IN  ___|‾‾‾‾‾‾‾‾‾‾‾‾‾‾|________
                  PT(纳秒精度)
ET  ___|/‾‾‾‾‾‾|‾‾‾‾‾‾‾|________
              ↑钳位在 PT
Q   _____________|‾‾‾‾‾|________
                ↑到点置 TRUE
```

## 4. 错误码 / 返回值

`LTON` 是标准定时器，**无错误码、无 HRESULT**。状态仅通过 `Q`（电平）与 `ET`（监视）反映。

## 5. 使用注意 / 常见坑

- **PLC 任务周期才是精度瓶颈**：LTIME 类型本身能表达纳秒，但 FB 只在每次被调用时才更新 ET。10 ms 任务下 `PT := LTIME#500us` 永远到不了；想用纳秒级要把任务周期降到 μs 级（通常通过 NC/CNC 配置）。
- **LTIME 字面量必须带前缀**：写 `LTIME#100ms` 而不是 `T#100ms`；后者是 TIME 类型，编译报类型不匹配。
- **避免混 TIME**：项目里如果一部分用 TON 一部分用 LTON，传参时要确保 PT 的类型与目标 FB 匹配；做转换可用 `TIME_TO_LTIME`（隐式扩展不会丢精度）。
- **运行中改 PT 不重启**：与 TON 同样，PT 只是即时比较门限。
- **断电不保持**：LTON 实例不是 retain；长周期延时（如月度保养）如果要跨断电生效必须自己用 RETAIN 变量保存累计时间。
- **TON 已够用别强上 LTON**：LTON 占用更多内存且不会在 ms 任务里提供额外精度。日常电机启停、报警延时坚持用 TON。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LTON.xml`](../examples/P_Demo_LTON.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：伺服驱动器上电后必须等 500 微秒才能发指令；用 LTON 在亚毫秒任务里
//       计时 500us 后允许指令通行。1 ms 任务的 TON 做不到这个精度。
PROGRAM P_Demo_LTON
VAR
    fbServoReadyDelay   : LTON;
    bDrivePowerOn       : BOOL;
    tServoBootupTime    : LTIME := LTIME#500US;
    bServoReady         : BOOL;
    tBootupElapsed      : LTIME;
END_VAR

fbServoReadyDelay(
    IN := bDrivePowerOn,
    PT := tServoBootupTime,
    Q  => bServoReady,
    ET => tBootupElapsed
);
```

## 7. 业务场景与实际价值

- **场景**：伺服 / 步进驱动器μs 级时序（上电延时、相位对齐）、长周期统计（设备累计运行 10000 小时报保养）、跨日跨月计时（TIME 49.7 天溢出后必须用 LTIME）。
- **价值**：与 TON 同等的简洁调用接口，时间分辨率与上限大幅扩展，特别适合需要 μs 级时序的 NC/CNC 应用。
- **替代方案对比**：
  - **TON**：上限 49.7 天，精度毫秒；常规场景首选
  - **手写 ULINT 计数累加**：能做但要自己处理"从纳秒系统时钟取值并累加"，约 15 行
  - **本 FB**：长延时 / 高精度场景的标准选择

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §3.4.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/9007205317836171.html
- **相关 FB**：`TON`（32 位 TIME 版本）、`LTOF`（断开延时 LTIME）、`LTP`（脉冲 LTIME）
