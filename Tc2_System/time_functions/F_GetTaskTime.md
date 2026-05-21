# F_GetTaskTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/3623060619.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetTaskTime.xml`](../examples/P_Demo_F_GetTaskTime.xml) |

---

## 1. 功能简述

F_GetTaskTime 是同步函数：读取**当前任务**的『计划开始时间』（任务应当开始的时间点）。返回 64-bit `ULINT`，以 100 ns 为单位，原点 1601-01-01 UTC。可用于时序测量、给本次任务循环里所有事件打统一时间戳。

## 2. 接口定义

### VAR_INPUT

```iecst
(* 函数无显式 VAR_INPUT *)
```

无 VAR_INPUT。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    F_GetTaskTime : ULINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `F_GetTaskTime` | `ULINT` | 当前任务的计划开始时间戳，64-bit，单位 100 ns，原点 1601-01-01 UTC。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用语义**：FUNCTION 类型，同步即出值。返回值是任务**应当**开始的时间（按任务周期计算），不是任务**实际**开始时间。例如任务周期 1 ms，理论上任务在 t=0, 1ms, 2ms, ... 开始；本函数返回的就是这些理论时刻。任务实际开始可能因抢占延迟 0.1ms，但本函数仍返回 t=1ms 而非 t=1.1ms。

**关键性质**：(1) 在同一任务循环里多次调用本函数得到**完全相同的值**；任务下一次循环才前进。这正是它适合『给本周期内所有事件打统一时间戳』的原因。(2) 与 `F_GetSystemTime` 区别：后者每次调用都用当前 OS 时间，同一周期内两次调用相差几个微秒；本函数保证一致。

**典型用法**：(1) 一个任务周期内产生 10 个事件，全部用同一个 `F_GetTaskTime` 值打时间戳，便于在日志里识别『同周期事件』；(2) 周期任务的『理论时间轴』生成（与抖动无关）。

**返回的是当前任务的时间**：在多任务工程里，本函数总返回调用者所在任务的开始时间——不能用它读别的任务的时间。

## 4. 错误码 / 返回值

本函数不暴露错误输出。

## 5. 使用注意 / 常见坑

- 本函数自 Tc2_System >= 3.4.17.0 起可用。
- 返回的是**理论**开始时间，不含抖动；要测真实开始用 `F_GetSystemTime` 减任务周期。
- 同一周期内多次调用值不变，是『一致时间戳』的特性。
- 时间原点同 F_GetSystemTime——1601-01-01 UTC（FILETIME）；要 Unix 时间减 `116444736000000000`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetTaskTime.xml`](../examples/P_Demo_F_GetTaskTime.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：1 ms 任务里需要给批量事件打『同周期』时间戳（HMI 显示 / MES 上报），用本函数一次取出全周期通用的时间戳，避免每个事件 timestamp 都差几微秒看起来像分散事件。
- **价值**：替代每次 `F_GetSystemTime` 取不同值；本函数同周期内保持一致。
- **替代方案对比**：`F_GetSystemTime` 给真实瞬时时间适合给瞬时事件打戳；`F_GetTaskTime` 给『周期标识时间戳』适合给同周期事件分组。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.6.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/3623060619.html
- **相关 FB / FC**：`F_GetSystemTime`（瞬时时间）、`F_GetTaskTotalTime`（任务执行时长）
