# F_GetTaskTotalTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/8830227851.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetTaskTotalTime.TcPOU`](../examples/P_Demo_F_GetTaskTotalTime.TcPOU) |

---

## 1. 功能简述

F_GetTaskTotalTime 是同步函数：返回指定任务在**上一周期**的总执行时间——即注册到该任务的所有模块上一周期累计运行多少 100 ns。`nTaskIndex = 0` 表示当前任务；非法 task index 返回 0。常用于任务负载剖析、容量评估。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nTaskIndex : DINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nTaskIndex` | `DINT` | - | 任务索引。`0` 表示当前调用所在任务；非法值返回 0。 |

### VAR_OUTPUT

```iecst
(* FUNCTION 返回 UDINT（100ns 单位）*)
FUNCTION F_GetTaskTotalTime: UDINT
```

FUNCTION 返回值类型：`UDINT`（详见 §4）。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用语义**：FUNCTION 类型，同步即出值。返回上一周期该任务内所有已注册模块的累计执行时长（100 ns 单位），不是当前周期还在执行的实时累计。

**`nTaskIndex` 语义**：`0` = 当前任务；其他正整数 = 项目里对应任务索引。非法（超出实际任务数或负数）返回 0。要查别的任务可结合 `GETCURTASKINDEXEX` 与 SystemInfoVarList 拿到目标任务索引。

**典型用法**：把 `F_GetTaskTotalTime` 与任务周期相除得到任务 CPU 利用率——例如返回 200000（200 us），任务周期 1 ms，则利用率 20 %。HMI 上做趋势曲线就能看任务负载随时间变化。

**与 `F_GetTaskTime` 的区别**：`F_GetTaskTime` 给任务开始的时间戳（用于打事件 timestamp）；本函数给任务执行耗时（用于负载分析）。

**与 Exceed Counter 配合**：`FB_ReadTaskExceedCounter` 给超限次数（离散事件），本函数给执行时长（连续量）；两者配合看任务是『偶尔超线』还是『接近超线』。

## 4. 错误码 / 返回值

本函数不暴露错误输出。非法 `nTaskIndex` 返回 0（与『任务存在但确实 0 耗时』不可区分；工程上认为 0 耗时不可能，所以 0 视为非法索引信号）。

## 5. 使用注意 / 常见坑

- 本函数自 Tc2_System >= 3.4.24.0 起可用。
- 返回上一周期累计，非当前周期实时累加。
- 返回 0 通常意味着 `nTaskIndex` 非法；任务存在但完全空闲返回值也是 0，所以 0 需结合是否确实空闲判断。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetTaskTotalTime.TcPOU`](../examples/P_Demo_F_GetTaskTotalTime.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：1 ms 高优先级任务负载随生产规模逐渐上升，需要做容量预警；每秒一次取 `F_GetTaskTotalTime` 推到 HMI 趋势曲线，提前发现接近 1 ms 周期上限。
- **价值**：替代 System Manager 里 Task 属性窗口手工巡检；本函数让负载监控可自动化、可告警。
- **替代方案对比**：`FB_ReadTaskExceedCounter` 给超限离散事件；本函数给连续量。两者结合更全面。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.6.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/8830227851.html
- **相关 FB / FC**：`GETCURTASKINDEX`（取当前任务索引）、`FB_ReadTaskExceedCounter`（超限计数）
