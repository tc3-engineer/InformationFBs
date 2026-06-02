# GetCoreFrequency

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

`GetCoreFrequency` 是 [`TC_CoreBoostMonitor`](TC_CoreBoostMonitor.md) 的方法之一，读取 FB 构造时绑定的那个实时核（`nCoreId`）的"**当前实际频率**"与"**配置频率（设定频率）**"。

正常情况下两者相等（CPU 跑在设定的目标频率），但当硬件触发限频时实际频率会低于配置频率——这就是判断"该核当前是不是在限频运行"的物理依据，比 `GetCoreThrottling` 的布尔位多一层量化信息（具体降到多少 MHz）。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD GetCoreFrequency : HRESULT
VAR_INPUT
    nCurrentCoreFrequency    : REFERENCE TO UDINT;
    nConfiguredCoreFrequency : REFERENCE TO UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nCurrentCoreFrequency` | `REFERENCE TO UDINT` | 引用回填：CPU 核**当前**频率。单位 PDF 未明示 ⚠️，按 InfoSys 与 Intel 硬件惯例以 MHz 解读 |
| `nConfiguredCoreFrequency` | `REFERENCE TO UDINT` | 引用回填：CPU 核**配置**频率（设定目标频率）。Core Boost 启用后这里是 boost 后的目标值 |

### 返回值

`HRESULT`：`SUCCEEDED(hr) = TRUE` 表示读取成功，两个引用参数有效。

### VAR_IN_OUT

无。

## 3. 行为说明

被调用时方法同步查询 TwinCAT 实时层维护的"目标核 MSR 镜像"，立即写回两个 `UDINT`：当前频率与配置频率。配置频率在 Core Boost 启用后被设到 boost 值（如 4800 MHz）；当前频率则反映 CPU 真实在跑多少（4800 / 3200 / 800 MHz 等）。

**判定是否限频**：若 `nCurrentCoreFrequency < nConfiguredCoreFrequency` 即说明该核正被自动降频。这个判断与 `GetCoreThrottling` 给出的布尔位是冗余信息——一个直接告诉你"是否限频"，一个让你看到具体降到多少。**配合用最稳**：用 `GetCoreThrottling` 知道"是否限频"，用本方法看"降到多少 MHz"以判断严重程度。

**频率粒度**：硬件层的频率台阶通常按 100 MHz 离散；不要期望读到连续值。某些低功耗节能态下 CPU 可能降到 800 MHz 甚至更低，与"被限频"的运行限频是两回事——但单纯看本方法的两个数值无法区分，需要结合 `GetCoreThrottling` 判断。

绑定的核 ID 由 FB 构造时的 `nCoreId` 决定。构造时传 `-1` 让 FB 绑到调用所在核；构造后通常不再改 `nCoreId`（其再生效语义 PDF 未明确）。

## 4. 错误码 / 返回值

方法签名 `METHOD GetCoreFrequency : HRESULT`：

| HRESULT 判定 | 含义 |
|---|---|
| `SUCCEEDED(hr) = TRUE`（通常 `S_OK`） | 查询成功，两个频率值有效 |
| `FAILED(hr) = TRUE` | 查询失败，引用参数不可信；常见原因：CPU 不支持本特性、`nCoreId` 越界 |

⚠️ 具体 `HRESULT` 编码表 PDF 与 InfoSys 均未列出。

## 5. 使用注意 / 常见坑

- 单位不明：PDF 没写单位 ⚠️。InfoSys 描述与 Intel 硬件惯例都倾向 MHz。建议先在已知 boost 频率的台架上调一次验证（如 4800 MHz boost，应读到 ~4800）。
- 不要把"`nCurrentCoreFrequency == nConfiguredCoreFrequency`"等价于"系统没问题"：低功耗节能态也会让两者保持相等（都在低频）。要判限频请结合 `GetCoreThrottling`。
- 频率读数在 100 MHz 量级跳变是正常的，硬件层就是离散台阶，不是误差。
- 调用频率建议 ≥ 100 ms。
- 不能改频率，只能读：要调整频率得改 TwinCAT 实时设置（Core Boost 开关 + 实时核配置），不是本方法的职责。
- `nConfiguredCoreFrequency` 在运行时**通常不变**：除非有人在线改实时设置并 reload PLC，否则启动后这个值就是常量；不要每周期读它做"目标"——应在启动时读一次缓存。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TC_CoreBoostMonitor.TcPOU`](../examples/P_Demo_TC_CoreBoostMonitor.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 完整场景见 TC_CoreBoostMonitor.md；本片段聚焦 GetCoreFrequency
VAR
    fbBoostMonitor       : TC_CoreBoostMonitor := (nCoreId := -1);
    hrFreqResult         : HRESULT;
    nCurrentFreqMHz      : UDINT;
    nConfiguredFreqMHz   : UDINT;
    nFreqDropPercent     : UDINT;     // 业务侧的"频率掉了多少 %"
END_VAR

hrFreqResult := fbBoostMonitor.GetCoreFrequency(
    nCurrentCoreFrequency    := nCurrentFreqMHz,
    nConfiguredCoreFrequency := nConfiguredFreqMHz
);

IF SUCCEEDED(hrFreqResult) AND nConfiguredFreqMHz > 0 THEN
    // 当前频率相对配置频率掉了百分之几 — 给 HMI 显示用
    nFreqDropPercent := 100 - ((nCurrentFreqMHz * 100) / nConfiguredFreqMHz);
END_IF
```

## 7. 业务场景与实际价值

- **场景**：诊断"为什么 PLC 周期突然变长"。先用 `GetCoreThrottling` 看是否限频，再用 `GetCoreFrequency` 看降了多少——降 100 MHz 与降 2 GHz 是完全不同量级的问题，处理紧迫度不同。
- **价值**：把"是否限频"这一布尔转换为"降频幅度"这一数量指标，让运维有依据判断严重性、决定是否立即停机散热。
- **替代方案对比**：
  - 只用 `GetCoreThrottling`：知道发生了，但不知道严重程度
  - **本方法 + GetCoreThrottling**：完整诊断信息
  - 用 Windows `Get-Counter`：拿不到实时核的精确状态

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.83.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/16219549067.html
- **父 FB**：[`TC_CoreBoostMonitor`](TC_CoreBoostMonitor.md)
- **同 FB 其他方法**：[`GetAllRtCoreThrottling`](GetAllRtCoreThrottling.md) · [`GetCoreTemperature`](GetCoreTemperature.md) · [`GetCoreThrottling`](GetCoreThrottling.md) · [`GetPowerConsumption`](GetPowerConsumption.md)
