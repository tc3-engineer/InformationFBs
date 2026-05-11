# R_TRIG

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Trigger` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74412139.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_R_TRIG.xml`](../examples/P_Demo_R_TRIG.xml) |

---

## 1. 功能简述

`R_TRIG` 是 **IEC 61131-3 标准块**之一，**上升沿检测器**（rising edge trigger）。把电平型布尔信号转换为单周期脉冲：`CLK` 输入由 FALSE 变 TRUE 后，输出 `Q` 在那一个 PLC 周期内为 TRUE，之后立刻回 FALSE。`CLK` 持续 TRUE 期间 `Q` 始终保持 FALSE——必须 `CLK` 先回 FALSE 再 TRUE 才能再次触发。

这是 PLC 编程中最常用的"边沿提取"工具之一，几乎所有需要"按一次响应一次"的逻辑都依赖它。

典型用途：按钮按下检测（不管按多久都只算一次）、传感器边沿计数（每个工件计一次）、状态变化检测（"刚刚发生"的事件信号生成）、给 CTU/CTD 提供干净的计数脉冲。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    CLK : BOOL; (* Signal to detect *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `CLK` | `BOOL` | 待检测的布尔信号 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q : BOOL; (* Edge detected *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | `CLK` 上升沿后那一个 PLC 周期为 TRUE；其余时间均为 FALSE |

### VAR_IN_OUT

无。

## 3. 行为说明

每个 PLC 周期 FB 内部保存一份"上一周期 CLK"值（记为 `M`，IEC 标准实现中通常是 FB 实例内部一个 BOOL 变量）。本周期 `Q` 的产生逻辑等价于 `Q := CLK AND NOT M; M := CLK;`——即"本周期 CLK 为 TRUE 且上周期 CLK 为 FALSE"时输出一拍 TRUE，否则 FALSE。关键特征是 `Q` 持续时间恒为 1 个任务扫描周期，不论 `CLK` 持续多久。

首次扫描行为：FB 实例化后 `M` 初始为 FALSE，因此如果 `CLK` 在 PLC 上电瞬间已经是 TRUE，第一次扫描会被识别为"上升沿"，`Q` 输出一拍 TRUE。如果业务上不希望上电产生假触发，必须在 FB 调用前确保 `CLK` 至少经历过一次 FALSE，或者上电前几个周期屏蔽 Q 的下游使用。

与 TP 的关键区别：R_TRIG 输出的是一个**任务周期**宽的脉冲（1 ms 任务里就是 1 ms），TP 输出的是 PT 指定的固定宽度（可以是数秒）。R_TRIG 不可配置宽度，只能配合 `TP` 或其它定时器把单周期脉冲拉长到指定时长。

## 4. 错误码 / 返回值

`R_TRIG` 是边沿检测器，**无错误码、无 HRESULT**。仅通过 `Q` 输出反映状态。

## 5. 使用注意 / 常见坑

- **必须循环调用**：R_TRIG 依赖每周期更新内部状态。若放在 IF 分支里只在某条件成立时才调用，分支不被进入的周期 FB 不更新——下次进入时可能漏检或错检边沿。**正确做法是无条件每周期调用**。
- **每个被监视的信号要独立的 FB 实例**：用同一个 `fbRTrig` 监视两个不同信号会让内部 `M` 串扰。N 个信号 N 个实例。
- **首次扫描可能输出一拍**：CLK 上电默认 TRUE 时第一次调用会被识为上升沿（M 初始 FALSE）。若不希望，在程序启动头几个周期屏蔽 `Q`。
- **不可嵌套**：把 `R_TRIG.Q` 又接到另一个 `R_TRIG.CLK` 没意义——`Q` 本来就是单周期脉冲，再做一次上升沿检测得到的还是同一拍。
- **R_TRIG vs SR 用法不同**：R_TRIG 是"边沿转脉冲"，SR 是"双稳态锁存"。两者经常配合：按钮 → R_TRIG → 计数器 / 取反逻辑 → SR/RS 锁存。
- **断电不保持**：FB 实例内部 M 非 retain。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_R_TRIG.xml`](../examples/P_Demo_R_TRIG.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：按按钮一次切换灯的开关状态（toggle）。按钮持续按住不应反复切换，
//       只算一次；松开再按又算一次。用 R_TRIG 提取上升沿后做 XOR。
PROGRAM P_Demo_R_TRIG
VAR
    fbButtonEdge   : R_TRIG;
    bToggleButton  : BOOL;       // 按钮信号（持续按住为 TRUE）
    bEdgePulse     : BOOL;       // 按钮按下沿的单周期脉冲
    bLampState     : BOOL;       // 灯的开关状态（toggle 后变化）
END_VAR

// 每周期无条件调用：提取按钮上升沿
fbButtonEdge(CLK := bToggleButton, Q => bEdgePulse);

// 上升沿那一拍取反灯的状态：按一次切一次
IF bEdgePulse THEN
    bLampState := NOT bLampState;
END_IF
```

## 7. 业务场景与实际价值

- **场景**：按钮"按一次响应一次"（toggle、计数、单次触发）、传感器边沿计数（每件加 1）、报警边沿（"刚发生"信号用于日志记录）、状态变化时执行一次性动作（启动 ADS 通讯、写一次配置）。
- **价值**：1 行调用拿到"上升沿单周期脉冲"，手写需要 2-3 行（保存上一周期值 + 比较 + 更新）每个信号都写一遍很繁琐；FB 形式更安全（实例隔离、上电状态明确）。
- **替代方案对比**：
  - **手写 `bRise := bIn AND NOT bInPrev; bInPrev := bIn;`**：可行但每个信号要 3 行，散落
  - **`TP`**：能输出脉冲但宽度固定，不是"单周期"
  - **`F_TRIG`**：方向相反，下降沿
  - **本 FB**：IEC 标准，工业 PLC 最常用边沿块

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §3.5.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74412139.html
- **相关 FB**：`F_TRIG`（下降沿，镜像）、`CTU`/`CTD`/`CTUD`（搭配做边沿计数）、`TP`（脉冲发生）
