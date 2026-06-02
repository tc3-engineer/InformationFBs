# F_GetTaskInfo

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/18698480907.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetTaskInfo.TcPOU`](../examples/P_Demo_F_GetTaskInfo.TcPOU) |

---

## 1. 功能简述

F_GetTaskInfo 返回当前调用任务的 `PlcTaskSystemInfo` 结构，包含任务索引、周期时间、优先级、最大执行时长、抖动统计等字段。用于运行期监控任务负载、检测超周期、性能瓶颈分析。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：同步函数，立即返回 `PlcTaskSystemInfo` 结构副本。

**结构字段**：`PlcTaskSystemInfo` 包含 `taskIndex`、`cycleTime`（任务设置的周期）、`lastExecTime`（上次实际执行时间）、`maxExecTime`、`minExecTime`、`cycleTimeExceeded`（超周期标志）、`priority` 等。

**典型用法**：MAIN 周期里调用本函数把 `lastExecTime` 存到 HMI 可视化变量，运维直接看到 PLC 任务的实际开销。

**性能监控模式**：在 MAIN 任务里调用本函数取 `maxExecTime`，与 `cycleTime` 做比，超过 80% 即报警，能在真正超周期之前提前预警。配合 `F_GetCpuCoreIndex` 可知道任务被分配到哪个 CPU 核。

**调用即得**：本函数无任何输入参数，返回值是结构体副本；不需要额外的状态机或异步等待。

## 4. 错误码 / 返回值

本函数返回 `PlcTaskSystemInfo`：包含 cycleTime / lastExecTime / maxExecTime / cycleTimeExceeded / priority 等字段的结构体。

## 5. 使用注意 / 常见坑

- **返回的是『调用所在任务』的信息**：不能查别的任务；要查其他任务用 ADS 读 `Task` 节点。
- **结构副本开销**：`PlcTaskSystemInfo` 不算大，但每个 PLC 周期调用一次额外几十纳秒。（工程经验补充）
- **`cycleTimeExceeded` 一次性触发**：建议自己加 latch，否则错过一拍可能漏报。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetTaskInfo.TcPOU`](../examples/P_Demo_F_GetTaskInfo.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 监控页显示 PLC MAIN 任务的实际周期、最大执行时间、抖动；运维一眼看出是否超周期。
- **价值**：替代登工程看实时面板。
- **替代方案对比**：
  - 登工程 Real-time 面板：远程不方便。
  - ADS Read：可以但要拼报文。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.11
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/18698480907.html
- **相关 FB / FC**：`F_GetCpuCoreIndex`, `GETCURTASKINDEXEX`
