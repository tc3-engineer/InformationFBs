# TOF

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Timer` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74404771.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_TOF.TcPOU`](../examples/P_Demo_TOF.TcPOU) |

---

## 1. 功能简述

`TOF` 是 **IEC 61131-3 标准块**之一，实现**断开延时定时器**（switch-off delay timer，又名"延时断"）。其行为与 `TON` 镜像：`IN` 上升沿瞬间 `Q := TRUE`；`IN` 下降沿后并不立刻让 `Q` 回 FALSE，而是等待 `PT` 时长后才置 FALSE；若 `PT` 期间 `IN` 又变回 TRUE，本次"延时断"被取消、`ET` 清零，`Q` 始终保持 TRUE。

精度同 `TON`，毫秒级，PT 类型 `TIME`（约 49.7 天上限），FB 实例占 **15 字节**。需要纳秒精度用 `LTOF`。

典型用途：风机停机后延时关机（继续吹散热）、设备故障灯亮起后保持 5 秒便于操作员看清、传感器抖动滤波（信号失去后再等几十毫秒确认）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    IN : BOOL;   (* starts timer with falling edge, resets timer with rising edge *)
    PT : TIME;   (* time to pass, before Q is reset *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `IN` | `BOOL` | 上升沿：立即 `Q := TRUE`，`ET` 清零（也复位正在进行的延时断）；下降沿：启动断开延时计时 |
| `PT` | `TIME` | 断开延时时长。`IN` 下降后 `ET` 累加到该值时 `Q` 才置 FALSE |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q  : BOOL;   (* is FALSE, PT seconds after IN had a falling edge *)
    ET : TIME;   (* elapsed time *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | `IN = TRUE` 时为 TRUE；`IN = FALSE` 且 `ET` 累加未达 `PT` 时仍为 TRUE；`IN = FALSE` 且 `ET = PT` 时为 FALSE |
| `ET` | `TIME` | 自 `IN` 下降沿起累加的已过时间；达到 `PT` 后钳位；`IN` 重新上升时清零 |

### VAR_IN_OUT

无。

## 3. 行为说明

**完整时序**（每个 PLC 周期调用 FB 一次时）：

1. **初始状态** `IN = FALSE`、未被触发过：`Q = FALSE`，`ET = T#0ms`
2. **`IN` 上升沿**（FALSE → TRUE）：立即 `Q := TRUE`，`ET := T#0ms`；定时器不计数
3. **`IN` 持续 TRUE**：`Q` 保持 TRUE，`ET` 保持 0
4. **`IN` 下降沿**（TRUE → FALSE）：`Q` 仍 TRUE，`ET` 开始累加
5. **`IN = FALSE` 且 `ET < PT`**：`Q` 保持 TRUE（**延时断进行中**），`ET` 继续累加
6. **`ET` 首次达到 `PT`**：当周期 `Q := FALSE`，`ET` 钳位在 `PT`
7. **`PT` 计时期间 `IN` 又上升**：立即取消断开延时——`ET := T#0ms`，`Q` 保持 TRUE，回到状态 3

**关键语义**：

- **"立即通、延时断"**：与 `TON`"延时通、立即断"完全镜像。`IN` 任何上升沿都立即让 `Q := TRUE`，没有"等 PT 后才接通"的概念。
- **断开延时可被打断**：`PT` 期间 `IN` 任何一次重新上升都会让定时器复位，`Q` 会继续保持 TRUE 不会出现"虚假关闭"。这是抗抖动的核心机制。
- **首次上电状态**：未经任何 `IN` 边沿前，`Q = FALSE`、`ET = 0`；必须 `IN` 上升一次才能进入"通"状态。
- **`PT = T#0ms`**：IEC 标准定义为 `IN` 下降沿后立即 `Q := FALSE`（零延时透传）。

**时序示意**（PDF 配图的文字版）：

```
IN  ___|‾‾‾‾‾‾‾|__________|‾‾‾|__|‾‾‾‾‾‾‾‾‾‾|________
                |          |       ↑PT 内重新上升
                |---PT-----|       延时断被取消
ET  _______________|/‾‾‾‾‾|_____________________|/‾‾‾‾
                   ↑ET 累加               中间不累加
Q   ___|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|___|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|___
       ↑立即通             ↑延时到，断  ↑保持通直到下降+PT
```

## 4. 错误码 / 返回值

`TOF` 是标准定时器，**无错误码、无 HRESULT**。状态仅通过 `Q`（电平）与 `ET`（监视）反映。

## 5. 使用注意 / 常见坑

- **方向相反，别和 `TON` 混淆**：`TON` 延时通、`TOF` 延时断。新手最常见的错是把电机停机延时关机用 `TON` 写，结果按下停止后还要等延时才"开始"关——逻辑完全反掉。
- **`Q` 在 `IN` 下降后仍是 TRUE 这是设计意图**不是 bug：业务侧别看到 `IN = FALSE` 就以为 `Q` 也应该 FALSE。
- **`PT` 期间 `IN` 抖动会无限延后关闭**：如果 `IN` 在 PT 倒数最后几毫秒又跳一下，定时器又从头开始数。生产现场如果信号源抖动严重，可能出现"永远关不掉"——上层应加保护逻辑或在 `IN` 前先做信号稳定化。（工程经验补充）
- **不要在运行中改 `PT`**：与 `TON` 一样，`PT` 是即时比较量；运行中改值只是改门限，不重新开始倒计时。
- **精度受任务周期限制**：与 `TON` 同样，1 ms 任务下能精确到 ~1 ms；不要在 10 ms 任务里设 `PT := T#3ms`。
- **断电不保持**：FB 内部状态非 retain，掉电再上电从初始状态开始；正在进行的延时断丢失。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TOF.TcPOU`](../examples/P_Demo_TOF.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：风冷电机停机后散热风扇延时关闭。电机运行时风扇随之运行；操作员发出
//       停机指令后，电机立刻停，但风扇还要继续转 60 秒散热，防止电机过热损坏。
PROGRAM P_Demo_TOF
VAR
    fbCoolDownDelay   : TOF;
    bMotorRun         : BOOL;             // 电机运行信号（在线置/清模拟）
    tCoolDownPeriod   : TIME := T#60S;    // 停机后散热 60 秒
    bFanOn            : BOOL;             // 风扇输出
    tCoolElapsed      : TIME;             // 已散热时长（监视用）
END_VAR

fbCoolDownDelay(
    IN := bMotorRun,
    PT := tCoolDownPeriod,
    Q  => bFanOn,
    ET => tCoolElapsed
);
```

## 7. 业务场景与实际价值

- **场景**：电机停机后延时关风扇散热、报警灯亮起后保持几秒确保操作员能注意到、电磁阀关闭后保持气压释放窗口、PLC 通讯断开延时报警（瞬时丢包不要立刻报警）。
- **价值**：用一次调用拿到"先通再延时断"的完整滞后逻辑，省下 8-10 行手写状态保存+计时+边界处理。镜像 `TON` 设计，IEC 61131-3 标准跨厂商兼容。
- **替代方案对比**：
  - **手写**：每个项目都要重复实现一遍，边界条件（PT 内重启、首次上电）容易出错
  - **`TON` 反逻辑**：把 `IN` 取反喂给 `TON` 也能实现类似效果，但 `IN` 上升沿瞬间 `Q` 不会立刻 TRUE——区别于 TOF "立即通"，多了一拍延迟
  - **本 FB**：IEC 标准，意图清晰；推荐首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §3.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74404771.html
- **相关 FB**：`TON`（接通延时，镜像）、`TP`（脉冲）、`LTOF`（64 位 LTIME 版本）
