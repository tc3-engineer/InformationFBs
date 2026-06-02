# GETCPUACCOUNT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Time function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30965515.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_GETCPUACCOUNT.TcPOU`](../examples/P_Demo_GETCPUACCOUNT.TcPOU) |

---

## 1. 功能简述

GETCPUACCOUNT 读取 **PLC 任务**的 cycle ticker（任务执行计时器）。该计数器只在所在任务被执行时累加，与 CPU 内部时钟无关，统一以 100 ns 为单位输出。每次任务调用都会刷新到 100 ns 精度，适用于任务内部精确计时（性能剖析、超时判断、时序测量）。本 FB 不支持 Windows CE。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
(*none*)
END_VAR
```

无 VAR_INPUT。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    cpuAccountDW : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `cpuAccountDW` | `UDINT` | 当前 PLC 任务 ticker 值。单位 100 ns。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用语义**：调用即出值。任务每次被调度执行时 ticker 加上自上次执行以来累计的时间（以 100 ns 为单位）。

**关键性质**：与 `GETCPUCOUNTER` 不同——`GETCPUACCOUNT` 只记录任务自身被调度的累计时长，任务**不在运行**时不增长；这正适合度量『任务内某段代码花了多少时间』。两次调用差值乘以 100 ns 即为这段代码的任务时间消耗。

**典型用法**：性能剖析——`udwTickStart := udwTickEnd;` 之类的差值法对一段循环精确计时；任务超时判断——记录上次循环开始的 ticker，下次进入时计算 elapsed。

**陷阱**：UDINT 是 32-bit，每 100 ns 自增 1 单位的 ticker 大约 429 秒后回卷（4_294_967_295 × 100 ns ≈ 429.5 s），跨 429 秒的差值会得到错误结果，长时间计时改用 `GETCPUCOUNTER` 拿 64-bit 值。本 FB 不支持 Windows CE。

## 4. 错误码 / 返回值

本 FB 不暴露错误输出。`cpuAccountDW` 始终为当前 ticker 值。在 Windows CE 上本功能不可用，调用结果未定义。

## 5. 使用注意 / 常见坑

- Windows CE 不支持。
- UDINT ticker 约 429 秒回卷，超过该窗口的差值计算需手动处理回卷或改用 64-bit 的 `GETCPUCOUNTER`。
- ticker 只记任务被调度的时长，不是墙钟时间——任务因高优先级抢占暂停期间不计入。这是它适合做『代码花了多少 CPU』的原因。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GETCPUACCOUNT.TcPOU`](../examples/P_Demo_GETCPUACCOUNT.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：1 ms 快速任务里有一段轨迹生成代码偶尔卡顿；用 GETCPUACCOUNT 在前后取两次 ticker，差值给出 100 ns 精度耗时，输出到 HMI 趋势曲线定位真正慢的那次。
- **价值**：替代外接 logic analyzer 或在代码里插延时打印；FB 内置 100 ns 精度且不需外设。
- **替代方案对比**：`GETCPUCOUNTER` 给 64-bit 累计（不回卷）但是墙钟时间，包含被抢占时长；本 FB 给纯任务执行时长更适合代码 profiling。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.7.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30965515.html
- **相关 FB / FC**：`GETCPUCOUNTER`（64-bit 墙钟 CPU 计数器）、`F_GetTaskTime`、`F_GetTaskTotalTime`
