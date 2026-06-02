# F_TRIG

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Trigger` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74410731.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_TRIG.TcPOU`](../examples/P_Demo_F_TRIG.TcPOU) |

---

## 1. 功能简述

`F_TRIG` 是 **IEC 61131-3 标准块**之一，**下降沿检测器**（falling edge trigger）。是 `R_TRIG` 的镜像版本：`CLK` 输入由 TRUE 变 FALSE 后，输出 `Q` 在那一个 PLC 周期内为 TRUE，之后立刻回 FALSE。`CLK` 持续 FALSE 期间 `Q` 始终为 FALSE——必须 `CLK` 先回 TRUE 再 FALSE 才能再次触发。

典型用途：按钮松开检测（"释放"动作触发逻辑）、信号丢失检测（"刚消失"事件）、传感器断开瞬时报警（边沿事件比电平报警更适合做日志）、状态变化的反向边沿（与 R_TRIG 配合判断完整脉冲）。

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
| `Q` | `BOOL` | `CLK` 下降沿后那一个 PLC 周期为 TRUE；其余时间均为 FALSE |

### VAR_IN_OUT

无。

## 3. 行为说明

每个 PLC 周期 FB 内部保存一份"上一周期 CLK"值（记为 `M`）。本周期 `Q` 的产生逻辑等价于 `Q := NOT CLK AND M; M := CLK;`——即"本周期 CLK 为 FALSE 且上周期 CLK 为 TRUE"时输出一拍 TRUE，否则 FALSE。`Q` 持续宽度恒为 1 个任务扫描周期。

首次扫描行为：与 R_TRIG 对称，FB 实例化后 `M` 初始为 FALSE。如果 `CLK` 上电时已为 FALSE，**不会**误触发（M 也是 FALSE，NOT CLK AND M = TRUE AND FALSE = FALSE）。这与 R_TRIG 的"CLK 上电默认 TRUE 会误发一拍"行为相反——F_TRIG 上电更安全，不会有"假下降沿"假触发。

与 R_TRIG 配合使用：监视同一个信号时，R_TRIG 检测"按下"、F_TRIG 检测"松开"，两者输出加起来可以测量信号 TRUE 持续时长、识别长按短按、检测脉宽异常。

## 4. 错误码 / 返回值

`F_TRIG` 是边沿检测器，**无错误码、无 HRESULT**。

## 5. 使用注意 / 常见坑

- **必须循环调用**：与 R_TRIG 同坑，放在 IF 分支里只在某条件下调用会导致内部状态错乱。无条件每周期调用。
- **每个信号独立实例**：复用实例监视多个信号会串扰。
- **上电不会误触发**：与 R_TRIG 相反，F_TRIG 上电默认 M=FALSE，CLK 即使是 FALSE 也不会发"假下降沿"。
- **不可嵌套**：`F_TRIG.Q` 接到另一个 `F_TRIG.CLK` 无意义。
- **断开通讯 / 看门狗超时常用 F_TRIG**：监视"链路活"信号的下降沿即"刚刚断了"，用于触发报警和日志记录。
- **按钮松开做事**：电脑端按钮通常按下触发，但 PLC 上有些场景要按钮**松开**才执行（避免按住时反复触发）。F_TRIG 正是用来取"松开沿"。
- **PLC 任务周期决定脉冲宽度**：1 ms 任务下 Q 宽度 1 ms；下游 FB 必须在同任务里抢拍读取，否则可能错过。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_TRIG.TcPOU`](../examples/P_Demo_F_TRIG.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：传感器信号断开告警。料位传感器正常时为 TRUE，掉线或料用完时变 FALSE；
//       业务关心的是"刚刚断"那一拍（用于触发报警日志写入），而不是"持续断"。
PROGRAM P_Demo_F_TRIG
VAR
    fbSensorLossEdge   : F_TRIG;
    bLevelSensorOk     : BOOL := TRUE;   // 料位传感器（默认 OK = TRUE）
    bSensorLostPulse   : BOOL;           // "刚断开"单周期脉冲
    nAlarmLogCount     : UDINT;          // 累计断线告警次数
END_VAR

// 每周期无条件调用提取下降沿
fbSensorLossEdge(CLK := bLevelSensorOk, Q => bSensorLostPulse);

// 下降沿那一拍累加告警计数（可换成 ADS 写日志、报警上报 SCADA 等）
IF bSensorLostPulse THEN
    nAlarmLogCount := nAlarmLogCount + 1;
END_IF
```

## 7. 业务场景与实际价值

- **场景**：按钮松开事件、信号丢失边沿（"刚断了"）、传感器掉线告警一次性触发、ADS 通讯心跳超时的状态切换"事件"信号、完成脉冲（任务结束信号回落时执行清理）。
- **价值**：与 R_TRIG 同等简洁，方向相反；上电更安全（不会误触发）。
- **替代方案对比**：
  - **手写 `bFall := NOT bIn AND bInPrev; bInPrev := bIn;`**：可行但每个信号 3 行散落
  - **`R_TRIG`**：方向相反，上升沿
  - **本 FB**：IEC 标准

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §3.5.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74410731.html
- **相关 FB**：`R_TRIG`（上升沿，镜像）
