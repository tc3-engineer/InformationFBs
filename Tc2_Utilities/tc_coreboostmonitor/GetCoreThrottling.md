# GetCoreThrottling

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `METHOD` |
| Category | `TC_CoreBoostMonitor` |
| Parent FB | [`TC_CoreBoostMonitor`](TC_CoreBoostMonitor.md) |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/16219549067.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_TC_CoreBoostMonitor.TcPOU`](../examples/P_Demo_TC_CoreBoostMonitor.TcPOU) |

---

## 1. 功能简述

`GetCoreThrottling` 是 [`TC_CoreBoostMonitor`](TC_CoreBoostMonitor.md) 的方法之一，查询 FB 构造时绑定的那个实时核（`nCoreId`）当前是否因温度或封装功耗超限而被限频。

与 `GetAllRtCoreThrottling` 的关键差别：本方法是**单核视角**——只看 `nCoreId` 指定的那一个核；`GetAllRtCoreThrottling` 是聚合视角——汇总所有实时核。哪个核被限频、哪个还好，必须用本方法逐核定位。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD GetCoreThrottling : HRESULT
VAR_INPUT
    bInThermalThrottling : REFERENCE TO BOOL;
    bInPowerThrottling   : REFERENCE TO BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bInThermalThrottling` | `REFERENCE TO BOOL` | 引用回填：该 CPU 核因温度上限被触发而正在限频则为 `TRUE` |
| `bInPowerThrottling` | `REFERENCE TO BOOL` | 引用回填：该 CPU 核因 platform package 功耗上限被触发而正在限频则为 `TRUE` |

### 返回值

`HRESULT`：`SUCCEEDED(hr) = TRUE` 表示读取成功，两个引用参数有效。

### VAR_IN_OUT

无。

## 3. 行为说明

被调用时方法同步查询 TwinCAT 实时层维护的"目标核 MSR 镜像"，立即写回两个布尔状态位。`bInThermalThrottling` 与 `bInPowerThrottling` 反映的是**调用瞬间**该核的限频状态。

两个状态位是**独立**的：可能两个都 `TRUE`、其中一个 `TRUE`、或都 `FALSE`。`bInPowerThrottling` 反映的是整个 platform package（CPU 封装）的功耗超限——同 package 内的所有核要么一起触发功耗限频，要么都不触发，所以同 package 各核读到的这个位通常相同。`bInThermalThrottling` 则是单核独立的——某个核温度高被限频，邻核可能还正常。

**与 `GetAllRtCoreThrottling` 的搭配模式**：
1. 先调 `GetAllRtCoreThrottling` 检测"有没有任何核被限频"
2. 若聚合结果显示有，再为每个核（每个 FB 实例）调本方法，定位具体哪些核被限频
3. 对限频的核进一步用 `GetCoreTemperature` / `GetCoreFrequency` 查具体温度 / 降频幅度

这种"先聚合检测、再单核定位"的模式比"上来逐核全查"更节省 MSR 读取开销。

绑定核 ID 由 FB 构造时的 `nCoreId` 决定，运行时不要随便修改。

## 4. 错误码 / 返回值

方法签名 `METHOD GetCoreThrottling : HRESULT`：

| HRESULT 判定 | 含义 |
|---|---|
| `SUCCEEDED(hr) = TRUE`（通常 `S_OK`） | 查询成功，两个状态位有效 |
| `FAILED(hr) = TRUE` | 查询失败，常见原因：CPU 不支持、`nCoreId` 越界 |

⚠️ 具体失败 `HRESULT` 编码表 PDF 与 InfoSys 均未列出。

## 5. 使用注意 / 常见坑

- 状态位是瞬时的，下一周期可能回落。要"过去 1 秒内是否限频过"必须自己做边沿锁存或滤波。
- 同 package 多核的 `bInPowerThrottling` 读数相同——这不是 bug，是硬件行为，不要重复报警。
- `bInThermalThrottling = TRUE` 时建议立刻调 `GetCoreTemperature` 看当前温度，作为诊断证据。
- 限频本身是硬件保护机制，正常工作；业务侧应据此降负载或报警，不要停机。
- 调用频率建议 ≥ 100 ms。
- FB 构造后改 `nCoreId` 是否生效 PDF 未说 ⚠️——保守做法是每个核一个 FB 实例。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TC_CoreBoostMonitor.TcPOU`](../examples/P_Demo_TC_CoreBoostMonitor.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 完整场景见 TC_CoreBoostMonitor.md；本片段聚焦 GetCoreThrottling
VAR
    fbBoostMonitor              : TC_CoreBoostMonitor := (nCoreId := 0);  // 绑实时核 0
    hrThrottleResult            : HRESULT;
    bCore0ThermalThrottle       : BOOL;
    bCore0PowerThrottle         : BOOL;
END_VAR

hrThrottleResult := fbBoostMonitor.GetCoreThrottling(
    bInThermalThrottling := bCore0ThermalThrottle,
    bInPowerThrottling   := bCore0PowerThrottle
);
```

## 7. 业务场景与实际价值

- **场景**：多核系统已检测到"有核被限频"（`GetAllRtCoreThrottling` 返回 `TRUE`），现在需要定位是哪一个核——给每个核一个 FB 实例，逐个调本方法判断。
- **价值**：精确定位故障核，避免"一锅端"——某个核因散热不均限频，其他核还好，只需要针对这一个核降负载。
- **替代方案对比**：
  - 只用 `GetAllRtCoreThrottling`：知道有问题，不知道是哪个核
  - **本方法**：精确到核
  - 用 `GetCoreFrequency` 比较当前 vs 配置：能间接判断但需自己写比较；本方法直接给布尔位更明确

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.83.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/16219549067.html
- **父 FB**：[`TC_CoreBoostMonitor`](TC_CoreBoostMonitor.md)
- **同 FB 其他方法**：[`GetAllRtCoreThrottling`](GetAllRtCoreThrottling.md) · [`GetCoreFrequency`](GetCoreFrequency.md) · [`GetCoreTemperature`](GetCoreTemperature.md) · [`GetPowerConsumption`](GetPowerConsumption.md)
