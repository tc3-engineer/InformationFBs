# TON

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Timer` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74406539.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_TON.xml`](../examples/P_Demo_TON.xml) |

---

## 1. 功能简述

`TON` 是 **IEC 61131-3 标准块**之一，实现**接通延时定时器**（switch-on delay timer，又名"延时通"）。`IN` 输入维持 TRUE 累计达到设定时长 `PT` 之后，输出 `Q` 才置 TRUE；如果 `IN` 在到点前回落，定时器立即复位，已累加的 `ET` 清零。

每个 PLC 周期被调用一次时，定时器以**毫秒级**精度累加。`PT` 类型为 `TIME`（TwinCAT 中底层为 32 位毫秒 DWORD，上限约 49.7 天）。需要 64 位纳秒精度可改用 `LTON`。FB 实例数据占用 **15 字节**。

这是工业中最常用的功能块之一：电机启动确认、按键防抖、报警延时、阀门到位超时、加热升温等待——只要"信号持续 N 秒后才认账"的场景都用它。

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
| `IN` | `BOOL` | 上升沿启动计时；保持 TRUE 期间 `ET` 累加；下降沿立即复位（`ET := T#0ms`，`Q := FALSE`） |
| `PT` | `TIME` | 延时时长。`ET` 累加至该值后 `Q` 置 TRUE |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q  : BOOL;   (* is TRUE, PT seconds after IN had a rising edge *)
    ET : TIME;   (* elapsed time *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | `IN = TRUE` 且 `ET ≥ PT` 时为 TRUE；其余情况为 FALSE |
| `ET` | `TIME` | 自 `IN` 上升沿起累加的已过时间；`ET` 达到 `PT` 后保持不再增长；`IN` 回落时清零 |

### VAR_IN_OUT

无。

## 3. 行为说明

**完整时序**（每个 PLC 周期调用 FB 一次时）：

1. **初始状态** `IN = FALSE`：`Q = FALSE`，`ET = T#0ms`，定时器待命
2. **`IN` 上升沿**（FALSE → TRUE）：开始累加 `ET`；本周期 `ET` 仍为 0（或一个任务周期增量），`Q` 仍为 FALSE
3. **`IN` 持续 TRUE 但 `ET < PT`**：每周期 `ET` 增加约一个任务周期的时长；`Q = FALSE`
4. **`ET` 首次达到 `PT`**：当周期 `Q := TRUE`，`ET` 钳位在 `PT` 不再继续增加（**这是 IEC 标准行为**，避免溢出）
5. **`IN` 仍 TRUE 且 `ET = PT`**：`Q` 保持 TRUE，`ET` 保持 `PT`
6. **`IN` 下降沿**（任何时刻 TRUE → FALSE）：立即 `Q := FALSE`，`ET := T#0ms`；定时器复位回到状态 1

**关键语义**：

- **不到点中断 → 完全清零**：`IN` 高电平累计到 60% 后回落，下一次重新置位时 `ET` 从 0 重新开始数，不是从 60% 续计。这与"累积计时"（需要自己用 CTU + 减法实现）完全不同。
- **`Q` 是电平输出**：`Q` 一旦置 TRUE 会**持续保持** TRUE 直到 `IN` 回落，**不是一拍脉冲**。需要单拍脉冲请在 `Q` 输出后串一个 `R_TRIG`。
- **精度取决于任务周期**：1 ms 任务下 `PT := T#1ms` 才有意义；10 ms 任务下定时 5 ms 永远到不了——`PT` 必须 ≥ 任务周期，工程上建议 ≥ 2×任务周期留余量。

**时序示意**（PDF 配图的文字版）：

```
IN  ___|‾‾‾‾‾‾‾‾‾‾‾‾‾‾|________|‾‾‾|_______|‾‾‾‾‾‾‾‾‾‾
                |     |              中途回落，
                |--PT-|              ET 清零重数
ET  ___|/‾‾‾‾‾|‾‾‾‾‾‾|________|/‾‾|_______|/‾‾‾‾‾‾‾‾‾
              ↑钳位在 PT       ↑清零
Q   _________|‾‾‾‾‾‾‾|_______________________|‾‾‾‾‾
             ↑Q=TRUE   ↑Q=FALSE              ↑下一次到点
```

## 4. 错误码 / 返回值

`TON` 是标准定时器，**无 `bError` / `nErrorId` 输出，无 HRESULT 返回**。状态仅通过 `Q`（输出电平）与 `ET`（监视用）反映。若 `PT = T#0ms`，IEC 标准定义为 `IN` 上升沿后立即 `Q := TRUE`（零延时直通）。

## 5. 使用注意 / 常见坑

- **`PT` 必须用 TIME 字面量**：写 `T#500ms`、`T#2s500ms`、`T#1m30s`，不要传裸 INT/DINT；类型不匹配会编译失败（或者更糟：被隐式转换出奇怪值）。
- **`Q` 是电平不是脉冲**：常见坑是用 `IF fbTON.Q THEN nCounter := nCounter + 1; END_IF`，结果一秒钟内累加几千次。正确做法是在 `Q` 后接 `R_TRIG` 取上升沿。
- **运行中改 `PT` 不会重新触发**：`PT` 是即时比较量，运行中把 5s 改成 10s 不会让定时器"再等 10s"——只是把当前比较门限抬高。需要重启计时必须让 `IN` 走一次下降→上升沿。（工程经验补充）
- **PLC 周期决定精度**：1 ms 任务下能精确到约 1 ms；10 ms 任务下 `PT := T#3ms` 永远到不了，因为每次累加单位是 10 ms。一律 `PT ≥ 2 × 任务周期`。（工程经验补充）
- **TIME 上限 49.7 天**：底层 32 位毫秒 DWORD。需要月、年级别延时（比如设备保养周期）必须改用 `LTON`（LTIME，64 位纳秒，上限约 584 年）。
- **断电不保持**：FB 实例的内部计时状态不是 `VAR RETAIN`，掉电重启 `ET` 归零，已到时间的 `Q` 也回 FALSE。需要断电续延时必须自己用 RETAIN 变量保存计时进度。（工程经验补充）
- **首次扫描循环 `Q` 一定是 FALSE**：即便 `IN` 默认 TRUE，至少要走一个完整 PLC 周期才可能上升沿——上电后立刻判 `Q` 一定拿到 FALSE，业务侧别据此误判设备未就绪。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TON.xml`](../examples/P_Demo_TON.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：变频电机"启动确认"。操作员按下启动按钮后，必须保持 3 秒不松手才算
//       真正启动，避免误触。3 秒到点后输出 bMotorRun 通知后续逻辑。
PROGRAM P_Demo_TON
VAR
    fbStartupDelay   : TON;
    bMotorStartReq   : BOOL;            // 启动按钮 — 在线写值模拟
    tStartupHold     : TIME := T#3S;    // 必须持续按住 3 秒
    bMotorRun        : BOOL;            // 输出：电机允许启动
    tHoldElapsed     : TIME;            // 监视当前已按住时长
END_VAR

fbStartupDelay(
    IN := bMotorStartReq,
    PT := tStartupHold,
    Q  => bMotorRun,
    ET => tHoldElapsed
);
```

## 7. 业务场景与实际价值

- **场景**：电机启动按键防抖（操作员误碰一下不应启动）、加热到温确认（温度到点后再持续 5 秒才放行下一步）、报警延时（信号闪一下不报警，持续 2 秒才报）、阀门到位超时（开阀指令发出 10 秒还没收到到位信号 → 报警）。
- **价值**：业务代码只需 4 行（声明 + 调用），就拿到完整的"上升沿启动、电平保持、下降沿复位"语义。不用本 FB 就要自己写：
  ```
  IF bIn AND NOT bInPrev THEN tStart := F_GetSystemTime(); END_IF
  IF bIn AND (F_GetSystemTime() - tStart) >= tPT THEN bQ := TRUE; END_IF
  IF NOT bIn THEN bQ := FALSE; END_IF
  bInPrev := bIn;
  ```
  四行手写在边界条件（首次扫描、PT 改值、断电）下都容易踩坑。
- **替代方案对比**：
  - **手写计时**：能做但每个新功能都要重写一遍，难维护
  - **`TIMER` 旧式 IEC 块**：TwinCAT 3 已弃用，不再支持
  - **`TP`（脉冲）**：到点输出一段脉冲就回 FALSE，不能持续保持
  - **`TOF`（断开延时）**：上升沿立即 Q=TRUE，下降沿才开始计时——逻辑反向
  - **本 FB**：IEC 标准、跨平台、跨控制器（PLC、ESP、CODESYS 全兼容），首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §3.3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74406539.html
- **相关 FB**：`TOF`（断开延时）、`TP`（脉冲生成）、`LTON`（64 位 LTIME 版本）、`R_TRIG` / `F_TRIG`（边沿检测，常和 TON 配合用）
