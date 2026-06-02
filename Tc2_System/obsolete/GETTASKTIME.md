# GETTASKTIME

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `[Obsolete]` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30962443.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified · deprecated` |
| Example | [`examples/P_Demo_GETTASKTIME.TcPOU`](../examples/P_Demo_GETTASKTIME.TcPOU) |

---

## 1. 功能简述

**⚠️ 已废弃**：GETTASKTIME 是功能块，读取**当前任务的预期启动时间**（64 位时间戳，1601-01-01 起算，单位 100 ns）。PDF 明确建议**改用 `F_GetTaskTime` 函数**。保留本 FB 仅为兼容老代码；新工程禁用。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    timeLoDW : UDINT;
    timeHiDW : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `timeLoDW` | `UDINT` | **输出**：任务启动时间戳低 32 位。 |
| `timeHiDW` | `UDINT` | **输出**：任务启动时间戳高 32 位。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**已废弃，不建议在新代码中使用。**

**与 `GETSYSTEMTIME` 区别**：GETSYSTEMTIME 返回当前实际时刻；本 FB 返回当前 PLC 任务的『预期启动时间』——这个时刻是 TwinCAT 调度器为本周期任务规划的开始时间，可能略早于 `GETSYSTEMTIME`（任务延迟时差更大）。

**返回 64 位拆两段**：与 GETSYSTEMTIME 同结构（`timeLoDW` + `timeHiDW`）。

**典型用法**：测量任务延迟 / 抖动——`GETSYSTEMTIME - GETTASKTIME` 即为本周期任务实际延迟。

**替代方案**：`F_GetTaskTime()` 函数。

## 4. 错误码 / 返回值

本函数无错误码 / 无返回值，状态由输出参数自行反映。

## 5. 使用注意 / 常见坑

- **已废弃**：用 `F_GetTaskTime()` 函数替代。
- **返回的是『预期启动』而不是『当前实际』**：与 GETSYSTEMTIME 不同；测量抖动时要两者差值。
- **手拼高低 32 位**：同 GETSYSTEMTIME 的坑。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GETTASKTIME.TcPOU`](../examples/P_Demo_GETTASKTIME.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：**仅老代码维护场景**：维护用了 GETTASKTIME 的工程。新工程改用 `F_GetTaskTime()` 函数。
- **价值**：无新价值；已被函数版本取代。
- **替代方案对比**：
  - `F_GetTaskTime()`：**推荐**，一行调用。
  - `F_GetTaskInfo()`：获取更全的任务信息（含 lastExecTime 等）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.7.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30962443.html
- **相关 FB / FC**：`GETSYSTEMTIME`
