# FB_BA_PIDCtrl

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Controllers` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785038603.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_BA_PIDCtrl.TcPOU`](../examples/P_Demo_FB_BA_PIDCtrl.TcPOU) |

---

## 1. 功能简述

通用 PID 控制器，专为楼宇自动化（heating / cooling / 风量）场景设计。内部由两段串联组成：① PID 计算段，含 P、I、D 三部分与输出上下限 `fYMax` / `fYMin`；② 死区段（neutral zone），对控制器输出变化施加可配置滞回，避免阀门反复抖动。提供两种结构：`eP1ID`（P 上游 + ID 并联）与 `ePID`（P-I-D 并联）。具备完整的 anti-reset windup、反向控制、运行中同步（`bSync` / `fSync`）能力，常用于温度、压力、湿度等连续过程控制。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bEn                      : BOOL;
    fW                       : REAL;
    fX                       : REAL;
    eActn                    : E_BA_Action := E_BA_Action.eReverse;
    fYMax                    : REAL := 100;
    fYMin                    : REAL := 0;
    bSync                    : BOOL;
    fSync                    : REAL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bEn` | `BOOL` | - | 控制器总使能；`FALSE` 时输出 `fY` 强制为 0、所有内部累积量（I 部分、D 部分历史值）清零；`TRUE` 时进入正常 PID 计算。 |
| `fW` | `REAL` | - | 设定值（setpoint），被控对象的目标值。 |
| `fX` | `REAL` | - | 实际值（process value），被控对象的当前测量值。 |
| `eActn` | `E_BA_Action` | `E_BA_Action.eReverse` | 控制方向（参考 `E_BA_Action` 枚举）：`eDirect` 表示 `fE = fX − fW`（制冷方向）；`eReverse` 表示 `fE = fW − fX`（加热方向）。 |
| `fYMax` | `REAL` | `100` | 输出上限百分比 `[%]`；`fY` 不会超过此值。 |
| `fYMin` | `REAL` | `0` | 输出下限百分比 `[%]`；内部自动限制 `fYMin ≤ fYMax`。 |
| `bSync` | `BOOL` | - | 强制同步：上升沿生效。仅评估上升沿，要重新同步必须先 `FALSE` 再 `TRUE`。 |
| `fSync` | `REAL` | - | 同步目标值；内部被夹在 `[fYMin, fYMax]` 区间。`bSync` 上升沿时强制 `fY := fSync` 并反推 I 部分（若 I 部分被禁则反推 D 部分，再否则反推 P 部分）。 |

### VAR_INPUT CONSTANT PERSISTENT

```iecst
VAR_INPUT CONSTANT PERSISTENT
    nCycleCall               : UDINT := 5;
    eOperationMode           : E_BA_PIDMode := E_BA_PIDMode.eP1ID;
    fProportionalConstant    : REAL;
    TIntegralTime            : TIME;
    tDerivativeTime          : TIME;
    tDampingTime             : TIME;
    fNeutralZone             : REAL := 0.0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nCycleCall` | `UDINT` | `5` | 调用周期（按 PLC 任务周期的倍数）。例如任务周期 10 ms、`nCycleCall = 5` 则 PID 每 50 ms 实算一次。内部下限为 1，0 自动按 1 处理。 |
| `eOperationMode` | `E_BA_PIDMode` | `E_BA_PIDMode.eP1ID` | 控制器结构（参考 `E_BA_PIDMode` 枚举）：`eP1ID` 表示 P 在 I-D 之前（典型串联型）；`ePID` 表示 P/I/D 完全并联。 |
| `fProportionalConstant` | `REAL` | - | 比例增益 K\_p，仅影响 P 部分；内部下限为 0（负值会被截断）。 |
| `TIntegralTime` | `TIME` | - | 积分时间 T\_i `[ms]`；`T#0ms` 时 I 部分被禁用（变成 PD 控制器）。⚠️ PDF 印刷为 `TIntegralTime`（首字母大写），InfoSys 与库内实际签名都是 `tIntegralTime`（首字母小写）。本文档照 PDF 原样保留，使用时按 InfoSys/编译器接受的名字 `tIntegralTime` 引脚连接。 |
| `tDerivativeTime` | `TIME` | - | 微分时间 T\_d `[ms]`；`T#0ms` 时 D 部分被禁用（变成 PI 控制器）。 |
| `tDampingTime` | `TIME` | - | D 部分的阻尼滤波时间常数 `[s]`，用于抑制微分噪声放大。 |
| `fNeutralZone` | `REAL` | `0.0` | 死区宽度（neutral zone width）。`> 0` 时启用：当 PLC 周期内 PID 输出变化小于 `fNeutralZone / 2` 时保持上一周期输出不变；`= 0` 时禁用（信号原样透传）。用于减少阀门 / 风机的频繁微动。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    fY                       : REAL;
    fE                       : REAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `fY` | `REAL` | 控制输出 `[%]`，已按 `fYMin` / `fYMax` 限幅。`bEn = FALSE` 时强制为 0；`bSync` 上升沿时强制为 `fSync`。 |
| `fE` | `REAL` | 控制偏差，计算方向取决于 `eActn`：`eDirect` 时 `fE = fX − fW`（制冷）；`eReverse` 时 `fE = fW − fX`（加热）。即使 `bEn = FALSE`，`fE` 仍按当前 `fW` / `fX` 实时计算（便于运行外离线监视偏差）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

控制方向由 `eActn` 决定：`eReverse`（默认，加热模式）时偏差 `fE = fW − fX`——实际值低于设定值时输出朝正方向调节（开大加热阀）；`eDirect`（制冷模式）时 `fE = fX − fW`——实际值高于设定值时输出朝正方向调节（开大冷却阀）。被动行为：`bEn = FALSE` 时 `fY := 0.0`，所有内部 P / I / D 状态以及上一周期值都被清零；下次启动时第一个周期就像新调用一样（无历史值参与计算）。主动行为：`bEn = TRUE` 时按 `nCycleCall` 倍数周期实算 PID。Anti-reset windup（抗积分饱和）：当前周期实算前先做"预估输出"，若预估值小于 `fYMin` 则锁住 I 部分不允许进一步下降（仍允许上升）；若大于 `fYMax` 则锁住 I 部分不允许进一步上升（仍允许下降）。同步优先级（多个同步条件同时满足时按 Prio 1→5 处理）：① `bSync` 上升沿强制 `fY := fSync`（通过反向计算 I 部分实现）；② `fYMin` 改变且预估 `fY < fYMin` → 同步到 `fYMin`；③ `fYMax` 改变且预估 `fY > fYMax` → 同步到 `fYMax`；④ `eActn` 改变（控制方向反转）→ 同步到反转前的 `fY` 值（避免阀门反向冲击）；⑤ 触发 anti-reset windup。死区（neutral zone）：`fNeutralZone > 0` 时若本周期 PID 输出相对上周期变化的绝对值小于 `fNeutralZone / 2`，则保持上周期输出值——用于显著减少阀门微动次数。

## 4. 错误码 / 返回值

本 FB 无 `bError` / `nErrId` 输出；内部对越界参数（如 `fYMin > fYMax`、负的 `fProportionalConstant`）做静默裁剪。

| 现象 | 含义 | 处理建议 |
|---|---|---|
| `fY` 始终为 0 | `bEn = FALSE` 或 `fYMax = fYMin = 0` | 检查使能、检查输出上下限 |
| `fY` 限在 `fYMax` 或 `fYMin` 不动 | I 部分被 anti-reset windup 锁住 | 检查执行器是否物理饱和（阀已全开仍不到温度等） |
| `fY` 抖动剧烈 | D 部分对噪声过敏 | 加大 `tDampingTime`，或增大 `fNeutralZone` |
| `fY` 收敛慢 | I 时间过大 / K\_p 太小 | 减小 `TIntegralTime`，或提高 `fProportionalConstant` |
| `bSync` 设了不生效 | `bSync` 已是 `TRUE` 持续状态 | 仅评估上升沿，需先复位 `bSync := FALSE` 再设 `TRUE` |

PDF 未明确列错误码（控制器类 FB 不返回 ADS 错误，错误体现在控制行为上）。

## 5. 使用注意 / 常见坑

- `VAR_INPUT CONSTANT PERSISTENT` 段的参数（`fProportionalConstant` / `TIntegralTime` / `tDerivativeTime` / `tDampingTime` / `fNeutralZone` / `eOperationMode` / `nCycleCall`）是 **persistent**：值保存在 retain 区，重启后保留；新工程上电默认值为零，需要在 PLC 启动逻辑或通过 HMI 写入合理初值。（工程经验补充）
- ⚠️ **PDF 拼写错误**：`TIntegralTime`（首字母大写 T）。InfoSys 和库内实际为 `tIntegralTime`（小写 t）。如果 verify_doc / 编译报错不识别，请使用 `tIntegralTime`。（PDF 印刷错误）
- `nCycleCall` 是按 PLC 任务周期的倍数：任务周期 10 ms 时 `nCycleCall := 5` ⇒ PID 每 50 ms 计算一次；其余周期 `fY` 保持上次值。把它调大可降 CPU 占用，但会降低控制带宽，控制慢过程（温度）取大值（10-50），快过程（压力 / 流量）取小值（1-5）。（工程经验补充）
- `bSync` **仅评估上升沿**：要重新同步必须 `FALSE → TRUE` 的边沿。常用法是把 HMI 的"手 / 自切换"按钮接到 R\_TRIG 后再到 `bSync`。（工程经验补充）
- `fYMin > fYMax` 会被内部静默裁剪为 `fYMin := fYMax`——配错时输出会卡死在该值，难排查。建议组态时校验。（工程经验补充）
- `tDampingTime` 单位是 **秒**（[s]），而 `TIntegralTime` / `tDerivativeTime` 单位是 **毫秒**（[ms]）—— 三者单位不一致，写组态时容易搞错。（PDF 明确，工程提醒）
- `fNeutralZone` 是死区宽度（不是半宽）：内部按 `fNeutralZone / 2` 作单边阈值。设过大会出现"控制不动作"现象；推荐取实际控制精度的 2-3 倍。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_BA_PIDCtrl.TcPOU`](../examples/P_Demo_FB_BA_PIDCtrl.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：办公楼 VAV 终端温控：每个房间一个温度传感器（`fX`）、一个上位机设定值（`fW`）、一个 0-100% 阀门（`fY` 通过 0-10V 模拟量输出）。要求温度稳定 ±0.5℃，避免阀门频繁开合（延长执行器寿命）。
- **价值**：本 FB 一次性提供 PID + 限幅 + 死区 + anti-reset windup + 反向控制 + 运行中同步，所有楼宇控制场景需要的能力都已封装。对比手写 PID：① 不会出现阀门饱和后无法回退；② 死区机制自带，减少 50%+ 阀门动作次数；③ 模式切换（手 → 自）时 `bSync` 一行调用即可平滑过渡。
- **替代方案对比**：
  - **手写 PID**：易写漏 anti-reset windup，模式切换时 `fY` 跳变冲击执行器；
  - **Tc2_ControllerToolbox.FB_CTRL_PID**：通用 PID，但无 BA 优化（无死区、无 `bSync` 同步、`E_BA_Action` 命名约定不同）；
  - **本 FB**：BA 专用、与 Tc3_BA2_HVAC 等高层库直接对接，常作为后者的内部模块。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.2.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785038603.html
- **相关枚举 / 结构**：`E_BA_Action`、`E_BA_PIDMode`
- **相关 FB**：`FB_BA_Swi2P`（2 点切换控制）、`FB_BA_SwiHys2P`（带滞回的 2 点切换）

## 9. 待确认项 (⚠️)

- PDF `TIntegralTime` 与 InfoSys `tIntegralTime` 大小写不一致：本文档以 PDF 原样为准（首字母大写 T）。实际库内的 IEC 标识符以 InfoSys 为准（小写 t），编译器只接受小写形式。
