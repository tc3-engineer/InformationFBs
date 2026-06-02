# TC_CoreBoostMonitor

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/16219549067.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_TC_CoreBoostMonitor.TcPOU`](../examples/P_Demo_TC_CoreBoostMonitor.TcPOU) |

---

## 1. 功能简述

`TC_CoreBoostMonitor` 是 TwinCAT Core Boost 功能的监视器功能块（Function Block, FB）。Core Boost 是 TwinCAT 提供的"实时核（real-time core）单核加速"特性：把某个实时核的时钟频率单独提高，让对时延敏感的运动控制 / 测量任务跑得更快——代价是该核的功耗与发热都上升。

本 FB 不开启或调节 Core Boost（开关在 TwinCAT 实时设置 → Settings 标签页），它只**查询**特定 CPU 核当前的频率、温度、功耗以及"是否正在被自动限频（throttling）"。典型用法是把它放进低优先级监视任务里周期性轮询，发现温度逼近上限或功耗持续超标就报警 / 切到非加速档位，避免硬件长期超规工作。

OO 设计：FB 本体只携带"核 ID 选择"与"最近一次方法调用的错误"，所有真正的数据通过 5 个方法以 `REFERENCE TO ...` 引用参数回填。每次方法调用都返回 `HRESULT`，方便上层做错误聚合。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nCoreId : DINT := -1;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nCoreId` | `DINT` | `-1` | 要查询的 CPU 核 ID。0 起算（0..n）。特殊值 `-1`：自动取"当前调用本 FB 的实时核"——常用于"自我监视"。多核监视通常实例化多个 FB，每个绑定一个 `nCoreId` |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError      : BOOL;
    hrErrorCode : HRESULT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | 最近一次方法调用出错时为 `TRUE`。注意：这是"上一次结果"的快照——下次调一个成功的方法后会被刷掉。如要追踪每个方法的错误，请用每次方法返回的 `HRESULT` |
| `hrErrorCode` | `HRESULT` | 与 `bError` 配对的错误码。具体取值表 PDF 与 InfoSys 均未列出 ⚠️；属于 Windows 标准 `HRESULT`，可用 `SUCCEEDED(hr)` / `FAILED(hr)` 宏判定 |

### VAR_IN_OUT

无。

### 方法（Methods）

| 方法 | 返回 | 描述 |
|---|---|---|
| [`GetAllRtCoreThrottling`](GetAllRtCoreThrottling.md) | `HRESULT` | 查询"任一实时核"当前是否因温度或功耗被限频 |
| [`GetCoreFrequency`](GetCoreFrequency.md) | `HRESULT` | 读取 `nCoreId` 指定核的当前频率与配置频率（限频时两者不同） |
| [`GetCoreTemperature`](GetCoreTemperature.md) | `HRESULT` | 读取指定核的当前温度、自启动以来的最高温、以及温度上限阈值 |
| [`GetCoreThrottling`](GetCoreThrottling.md) | `HRESULT` | 查询指定核是否因温度 / 功耗被限频（与 `GetAllRt...` 的区别：单核 vs 全核聚合） |
| [`GetPowerConsumption`](GetPowerConsumption.md) | `HRESULT` | 读取 platform package（封装层级）当前功耗与功耗上限——同 package 内所有核共享一个值 |

## 3. 行为说明

硬件门槛：仅支持 Intel® Core™ i 系列第 11 代及以上 CPU。低于 11 代的 i 系列、Atom / Celeron / ARM 平台均不支持，相关方法将返回错误（具体 `HRESULT` 编码 PDF 与 InfoSys 均未列出 ⚠️）。

核 ID 语义：构造时传 `nCoreId := -1` 让 FB 自动绑到调用所在核——这里"调用所在核"指的是首次执行本 FB 调用代码的实时核。若希望显式指定，传 0 / 1 / 2 ...，对应 TwinCAT 实时设置里的"Real-time Cores"编号，并不是 Windows 任务管理器看到的逻辑核号。

调用形式：FB 本体不需要每周期"调一次实例"，而是直接调方法。方法内部完成与 TwinCAT 实时层的通讯，把结果通过 `REFERENCE TO` 引用参数写回调用者的局部变量。方法返回 `HRESULT`：`SUCCEEDED(hrCB)` 表示读取成功；失败时 FB 本体 `bError` 与 `hrErrorCode` 也会被刷为这次失败信息。

典型监视流程：在 PLC 启动后建立 FB 实例（或按核数量建多个），在监视任务里依次调 `GetCoreTemperature` 与 `GetAllRtCoreThrottling`；把当前温度与 `nTempLimit - 5°C` 比较，逼近上限时触发降负载或报警；若检测到 `bRtInThermalThrottling = TRUE` 即说明 CPU 已自动降频——业务循环周期会变长，建议在 HMI 上提示"核已限频，性能下降"。

与"开关 Core Boost"无关：本 FB 不能修改 Core Boost 开关，开关只能在 XAE 项目的实时设置里勾选。本 FB 只观察当前状态。

## 4. 错误码 / 返回值

FB 本体没有"调用入口的返回值"——它本身不被周期性调用。方法各自返回 `HRESULT`：

| HRESULT 判定 | 含义 |
|---|---|
| `SUCCEEDED(hr) = TRUE`（如 `S_OK` / `0x00000000`） | 读取成功，引用参数有效 |
| `FAILED(hr) = TRUE` | 读取失败，FB 本体 `bError = TRUE`，`hrErrorCode = hr`；引用参数内容不可信 |

⚠️ PDF 与 InfoSys 均未列出具体失败 `HRESULT` 编码表。基于 Windows `HRESULT` 通用习惯，常见可能错误：
- `E_NOTIMPL` (0x80004001)：CPU 不支持（非 11 代 i 系列）
- `E_INVALIDARG` (0x80070057)：`nCoreId` 越界（超过实际实时核数）
- `E_FAIL` (0x80004005)：TwinCAT 实时层未能读到硬件寄存器

实际定位错误时把 `hrErrorCode` 的 32 位整数贴给 Beckhoff 支持。

## 5. 使用注意 / 常见坑

- 没启用 Core Boost 也可以查询，但温度 / 功耗本来就低，限频几乎不会触发，监视意义不大；本 FB 的价值主要体现在 Core Boost 启用后对超载的预警。
- `nCoreId` 不要随便传 `-1` 后再换值：FB 是在第一次执行时把 `-1` 解析为当前核 ID 并锁定的（PDF 描述）；后续修改 `nCoreId` 输入是否生效，PDF 与 InfoSys 均未明确 ⚠️。保守做法是构造时一次性传入，之后不动。
- 同 package 多核共享功耗读数：`GetPowerConsumption` 在同一 package 的核上调用结果相同——不要错把"每核功耗"等同于"分别测出来的"。
- 方法返回 `HRESULT`，FB 的 `bError` 是"上一次结果"的快照：连续调多个方法时只看 `bError` 容易把"第一个方法失败、第二个成功"误判为整体成功。建议每个方法调用立刻判断本次返回的 `HRESULT`，不要依赖 FB 本体的 `bError`。
- 温度单位是 `°C`（PDF 明确），功耗单位是瓦（W）；频率单位 PDF 未明示 ⚠️，按 InfoSys 描述以 MHz 解读。
- 数据通过 `REFERENCE TO` 参数返回：传入的局部变量必须先声明且仍在作用域内。把 `ADR(...)` 或临时表达式当引用参数传是非法调用。
- 不要在高频任务里调（工程经验补充）：硬件 MSR 寄存器读取有开销，建议放进 ≥ 100 ms 的低优先级监视任务，不要塞进 1 ms 控制环。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TC_CoreBoostMonitor.TcPOU`](../examples/P_Demo_TC_CoreBoostMonitor.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：CX2040 工控机启用了 TwinCAT Core Boost 给运动控制实时核加速。需要在
//       监视任务里轮询该核的温度与"是否被限频"，逼近上限时给 HMI 报警，避免
//       在长时间满负载场景下硬件降速影响运动周期稳定性。
//
// 价值：不用本 FB 时需要绕 CIPC API 或读 MSR 寄存器——业务工程师没权限也不该
//       碰。本 FB 把硬件查询封装成一个方法调用，PLC 周期内即可拿到温度 / 限
//       频状态，配合 HMI 报警可在硬件还没出错前就提示降负载。
//
// 验证：登录目标后在线监视 nCurrentTemperatureC（应在 40-70°C 之间）；
//       打开 Core Boost、加大 PlcTask 负载（如插入空循环 1e6 次）→ 观察温度
//       上升、bAnyRtCoreThermalThrottle 在逼近上限时翻 TRUE；停止压力后
//       温度回落、bAnyRtCoreThermalThrottle 回 FALSE。
PROGRAM P_Demo_TC_CoreBoostMonitor
VAR
    fbBoostMonitor              : TC_CoreBoostMonitor := (nCoreId := -1);
    hrTempResult                : HRESULT;
    hrThrottleResult            : HRESULT;
    nCurrentTemperatureC        : UDINT;
    nMaxObservedTemperatureC    : UDINT;
    nTemperatureLimitC          : UDINT;
    bAnyRtCoreThermalThrottle   : BOOL;
    bAnyRtCorePowerThrottle     : BOOL;
    bTemperatureNearLimit       : BOOL;
END_VAR

hrTempResult := fbBoostMonitor.GetCoreTemperature(
    nCurrentTemp := nCurrentTemperatureC,
    nMaxTemp     := nMaxObservedTemperatureC,
    nTempLimit   := nTemperatureLimitC
);

hrThrottleResult := fbBoostMonitor.GetAllRtCoreThrottling(
    bRtInThermalThrottling := bAnyRtCoreThermalThrottle,
    bRtInPowerThrottling   := bAnyRtCorePowerThrottle
);

IF SUCCEEDED(hrTempResult) AND nTemperatureLimitC > 5 THEN
    bTemperatureNearLimit := nCurrentTemperatureC >= (nTemperatureLimitC - 5);
END_IF
```

## 7. 业务场景与实际价值

- **场景**：高速运动控制 / 视觉同步 / 测量反馈类任务对 PLC 周期抖动极敏感。Core Boost 把某个实时核频率拉高带来更稳的周期，但代价是该核长期高温运行。生产线 24×7 运转一段时间后，环境温度上升 + 散热下降可能触发硬件自动限频，控制周期突然变长——表现为运动抖动 / 节拍丢失。
- **价值**：周期性读温度与限频状态，让"硬件即将顶不住"这件事在它真正发生前几十秒到几分钟就被 HMI 看到，运营人员有机会清扫风道 / 降负载 / 切换非加速模式，避免生产线节拍异常。
- **替代方案对比**：
  - 不监视：硬件限频时 PLC 周期被动变长，运动抖动出现才反应，已经晚了
  - 用 Windows 性能计数器 / 厂家 SDK 读 CPU 温度：跨 Beckhoff 实时层不可靠，且不能反映"是否被实时层自动限频"
  - **本 FB**：直接读 TwinCAT 实时层暴露的 MSR 数据，温度与限频状态都拿到，是官方推荐的监视入口

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.83
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/16219549067.html
- **相关方法**：[`GetAllRtCoreThrottling`](GetAllRtCoreThrottling.md) · [`GetCoreFrequency`](GetCoreFrequency.md) · [`GetCoreTemperature`](GetCoreTemperature.md) · [`GetCoreThrottling`](GetCoreThrottling.md) · [`GetPowerConsumption`](GetPowerConsumption.md)
- **相关概念**：TwinCAT Real-time Settings → Core Boost 开关
