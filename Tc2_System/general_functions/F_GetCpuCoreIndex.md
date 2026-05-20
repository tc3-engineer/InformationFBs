# F_GetCpuCoreIndex

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/8824208779.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetCpuCoreIndex.xml`](../examples/P_Demo_F_GetCpuCoreIndex.xml) |

---

## 1. 功能简述

F_GetCpuCoreIndex 给定任务索引 `nTaskIndex`，返回该任务运行的 CPU 核心索引。若传 0，则返回当前调用任务自己所在的核心。无效任务索引返回 `-1`。用于诊断 PLC 任务的实际 CPU 绑定，配合 `F_GetCpuCoreInfo` 读取该核的基时与负载上限。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nTaskIndex : DINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nTaskIndex` | `DINT` | 任务索引。`0` = 当前调用任务；`1..n` = 指定任务。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**返回值含义**：`-1` 表示传入的 `nTaskIndex` 无效；`≥ 0` 是 CPU 核心索引，对应 TwinCAT SYSTEM 节点 Real-time 子节点 Core 列里的数值。

**典型用法**：多任务工程在线检查每个 PLC 任务的 CPU 分布是否符合预期；如果发现两个高频任务挤在同一核，可在 SYSTEM → Real-time 配置里重新分配。

**自查方便**：传 0 即可得到当前任务的核心，无需先查任务索引。

**与 `F_GetCpuCoreInfo` 区别**：本函数只返回核索引，`F_GetCpuCoreInfo` 进一步读出该核的详细配置参数。

## 4. 错误码 / 返回值

本函数返回 `DINT`：CPU 核心索引（≥ 0）；`-1` 表示任务索引无效。

## 5. 使用注意 / 常见坑

- **任务索引 0 是『自身』而不是『任务 0』**：调用方要查特定任务必须先用 `GETCURTASKINDEXEX` 拿到任务索引再传入。
- **返回 -1**：任务索引无效（超出 1..n 范围或任务未配置）；不要把 -1 当成『核心 0』使用。
- **Real-time 配置变更**：把任务从 Isolated CPU 切到 Shared CPU 不重启 TwinCAT 时，本函数返回值可能与配置面板显示一致但行为已变。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetCpuCoreIndex.xml`](../examples/P_Demo_F_GetCpuCoreIndex.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：启动时记录每个 PLC 任务的 CPU 绑定到日志，便于上线后远程诊断 CPU 调度问题。
- **价值**：替代去 SYSTEM 面板逐个看；PLC 代码自助查询。
- **替代方案对比**：
  - 看 SYSTEM 面板：要登工程在线。
  - 自己写 Windows API：太复杂。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/8824208779.html
- **相关 FB / FC**：`F_GetCpuCoreInfo`, `GETCURTASKINDEXEX`, `F_GetTaskInfo`
