# GetAllRtCoreThrottling

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

`GetAllRtCoreThrottling` 是 [`TC_CoreBoostMonitor`](TC_CoreBoostMonitor.md) 的方法之一，返回**所有实时核**当前是否因温度超限或功耗超限而被自动限频（throttling）。它给的是**聚合视图**——只要任一实时核出现限频，对应输出位即为 `TRUE`。

与 `GetCoreThrottling` 的区别：本方法关注"系统层面是不是有任何一个核被限频了"，常用于全局健康巡检；而 `GetCoreThrottling` 针对 FB 构造时绑定的某一个核做"针对性"判断。运行时通常先用本方法快速判断"是否有事发生"，再用 `GetCoreThrottling` / `GetCoreTemperature` 进一步定位是哪个核 / 什么原因。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD GetAllRtCoreThrottling : HRESULT
VAR_INPUT
    bRtInThermalThrottling : REFERENCE TO BOOL;
    bRtInPowerThrottling   : REFERENCE TO BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bRtInThermalThrottling` | `REFERENCE TO BOOL` | 引用回填：若任一实时核因温度超限正在被限频则为 `TRUE`，否则 `FALSE`。这个状态会随硬件温度波动跳变 |
| `bRtInPowerThrottling` | `REFERENCE TO BOOL` | 引用回填：若任一实时核因封装功耗超限（platform package performance limit）正在被限频则为 `TRUE`，否则 `FALSE` |

### 返回值

`HRESULT`：`SUCCEEDED(hr) = TRUE` 表示读取成功，引用参数有效；失败时 FB 本体的 `bError` / `hrErrorCode` 被刷新，引用参数内容不可信。

### VAR_IN_OUT

无。

## 3. 行为说明

被调用时方法同步完成对 TwinCAT 实时层的查询并立即写回两个引用变量，不存在"异步等待 / busy"状态。该查询读取的是硬件 MSR 寄存器，TwinCAT 实时层维护其镜像。

`bRtInThermalThrottling` 与 `bRtInPowerThrottling` 反映的是调用瞬间的状态。硬件限频是瞬时行为——一旦温度回落到限值以下立即解除，状态可能在几个 PLC 周期内反复跳变。如果业务侧需要"过去 1 秒内是否出现限频"这种持续性判断，需要自己在监视任务里做下降沿计时或多周期滤波。

温度限频与功耗限频是独立通道：可能两个都是 `TRUE`、其中一个 `TRUE`、或都 `FALSE`。一般温度限频更常见，功耗限频通常出现在工业服务器型 CPU 或重负载情况。

无论 FB 构造时 `nCoreId` 是几，本方法都汇总所有实时核的状态，不受 `nCoreId` 限制——这点 InfoSys 与 PDF 描述一致。

## 4. 错误码 / 返回值

方法签名 `METHOD GetAllRtCoreThrottling : HRESULT`：

| HRESULT 判定 | 含义 |
|---|---|
| `SUCCEEDED(hr) = TRUE`（通常 `S_OK`） | 查询成功 |
| `FAILED(hr) = TRUE` | 查询失败，引用参数不可信；FB 本体的 `bError` / `hrErrorCode` 同步刷新 |

⚠️ 失败时具体 `HRESULT` 编码表 PDF 与 InfoSys 均未列出。典型可能值与父 FB 一致（参见 [`TC_CoreBoostMonitor`](TC_CoreBoostMonitor.md#4-错误码--返回值)）。

## 5. 使用注意 / 常见坑

- 输出是瞬时状态，不是历史：要"过去 N 秒内是否出现过限频"必须自己做边沿锁存。
- 同 PLC 周期内调用本方法多次会得到相同结果（硬件层不会一周期内变两次），不要重复调用——浪费 MSR 读取开销。
- 调用频率建议 ≥ 100 ms，不要塞进 1 ms 高频任务。
- 即使 Core Boost 未开启本方法依然有效，但通常两个输出永远为 `FALSE`（CPU 不会主动限频），监视意义有限。
- `bRtInPowerThrottling` 反映的是整个封装（package）的功耗超限——同 package 的所有核共享一个上限，所以任一核触发功耗限频会被算作"全部触发"。
- 不要把"任一核被限频"等价于"系统瘫了"——硬件自动限频本来就是保护机制，正常工作；只是说性能在下降。业务侧应据此降负载，而不是停机。
- 若工程对单核限频有强诉求，请改用 `GetCoreThrottling` 针对指定 `nCoreId` 查询。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TC_CoreBoostMonitor.TcPOU`](../examples/P_Demo_TC_CoreBoostMonitor.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 完整场景见 TC_CoreBoostMonitor.md 例程；本片段聚焦 GetAllRtCoreThrottling
VAR
    fbBoostMonitor              : TC_CoreBoostMonitor := (nCoreId := -1);
    hrThrottleResult            : HRESULT;
    bAnyRtCoreThermalThrottle   : BOOL;
    bAnyRtCorePowerThrottle     : BOOL;
END_VAR

// 100 ms 监视任务里调一次，把结果上抬给 HMI 报警逻辑
hrThrottleResult := fbBoostMonitor.GetAllRtCoreThrottling(
    bRtInThermalThrottling := bAnyRtCoreThermalThrottle,
    bRtInPowerThrottling   := bAnyRtCorePowerThrottle
);
```

## 7. 业务场景与实际价值

- **场景**：跨多核的全局健康巡检——把"系统中是否有任何核正在限频"作为一个布尔报警量传给 HMI / SCADA，操作员看到这个量为 `TRUE` 就知道"硬件已经在自降频，性能下降了"。
- **价值**：相比逐核分别调 `GetCoreThrottling` 后用 `OR` 聚合，本方法一次调用拿到聚合结果，省 N 次 MSR 读取。
- **替代方案对比**：
  - 用 `GetCoreThrottling` 逐核轮询再 `OR`：能实现但开销大，且代码丑
  - **本方法**：直接给聚合结果，推荐用法
  - 用 Windows 性能计数器：拿不到"硬件自动限频"事件，无法替代

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.83.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/16219549067.html
- **父 FB**：[`TC_CoreBoostMonitor`](TC_CoreBoostMonitor.md)
- **同 FB 其他方法**：[`GetCoreFrequency`](GetCoreFrequency.md) · [`GetCoreTemperature`](GetCoreTemperature.md) · [`GetCoreThrottling`](GetCoreThrottling.md) · [`GetPowerConsumption`](GetPowerConsumption.md)
