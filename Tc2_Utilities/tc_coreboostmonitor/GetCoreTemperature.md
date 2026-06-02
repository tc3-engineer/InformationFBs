# GetCoreTemperature

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

`GetCoreTemperature` 是 [`TC_CoreBoostMonitor`](TC_CoreBoostMonitor.md) 的方法之一，一次性读取 FB 构造时绑定的实时核（`nCoreId`）的三个温度量：当前温度、自 TwinCAT XAR 启动以来该核观测到的最高温、以及硬件层面的温度上限（超过即触发自动限频）。

这是本 FB 最常用的方法。把"当前温度"与"温度上限"做差，可以算出还有多少余量；把"最高温"留存做趋势分析或事后报告。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD GetCoreTemperature : HRESULT
VAR_INPUT
    nCurrentTemp : REFERENCE TO UDINT;
    nMaxTemp     : REFERENCE TO UDINT;
    nTempLimit   : REFERENCE TO UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nCurrentTemp` | `REFERENCE TO UDINT` | 引用回填：该核当前温度，单位 `°C`（PDF 明确） |
| `nMaxTemp` | `REFERENCE TO UDINT` | 引用回填：自 TwinCAT XAR 启动以来该核观察到的最高温（°C）。XAR 重启后会清零并重新累计 |
| `nTempLimit` | `REFERENCE TO UDINT` | 引用回填：该核的温度上限（°C）。CPU 温度超过这个值就会自动限频以散热保护 |

### 返回值

`HRESULT`：`SUCCEEDED(hr) = TRUE` 表示读取成功，三个引用参数有效。

### VAR_IN_OUT

无。

## 3. 行为说明

被调用时方法同步查询 TwinCAT 实时层维护的温度数据并立即回填三个引用变量，不存在异步等待状态。底层是 Intel CPU 的 DTS（Digital Thermal Sensor）读数，TwinCAT 实时层抓取并缓存。

`nCurrentTemp` 是**实时**温度，会随负载和散热条件波动；典型工业 PC 在常温环境 / 中等负载下读到 50–75 °C，重负载 + 高环境温度可能逼近 90 °C 甚至更高。`nMaxTemp` 是**累积最大值**：FB 内部不重置它，只在 XAR 启动时被实时层清零并随时间单调上升。`nTempLimit` 是硬件能承受的最高温（业内叫 Tjmax）——Intel 桌面级 i 系列通常 100 °C，工业级 / 嵌入式 SKU 可能更低，PDF 与 InfoSys 都不固定数值。

**典型监视策略**：
- 启动时调用一次缓存 `nTempLimit`（运行时不会变），后续不用每周期读
- 100 ms 周期读 `nCurrentTemp`，与 `nTempLimit - 5°C` 比较：到达预警阈值就触发 HMI 报警 / 降负载
- 班次结束时把 `nMaxTemp` 写进日志，做长期趋势

**与"是否限频"的关系**：CPU 在 `nCurrentTemp >= nTempLimit` 时硬件自动限频；但 `nCurrentTemp` 略低于 `nTempLimit` 也未必不限频——硬件可能预判性降频。判限频以 `GetCoreThrottling` / `GetAllRtCoreThrottling` 为准，温度只是辅助。

绑定核 ID 由 FB 构造时的 `nCoreId` 决定。

## 4. 错误码 / 返回值

方法签名 `METHOD GetCoreTemperature : HRESULT`：

| HRESULT 判定 | 含义 |
|---|---|
| `SUCCEEDED(hr) = TRUE`（通常 `S_OK`） | 查询成功，三个温度值有效 |
| `FAILED(hr) = TRUE` | 查询失败，常见原因：CPU 不支持 DTS、`nCoreId` 越界 |

⚠️ 具体失败 `HRESULT` 编码表 PDF 与 InfoSys 均未列出。

## 5. 使用注意 / 常见坑

- 单位 `°C`（PDF 明确）——不要再做 K / °F 转换。
- `nMaxTemp` 只在 XAR 启动时清零，PLC 程序里不能复位它；要做"按班次清零"必须自己在程序里保存基准值再求差。
- `nTempLimit` 不要硬编码 100 °C：工业 CPU SKU 不同，限值不同；从本方法读出来才准。
- 读到 0 °C 几乎肯定是查询失败 + 引用变量没被写——务必先看 `HRESULT`。
- 不要把"`nCurrentTemp = 75°C` 看上去还好"等价于"安全"——硬件可能已经在做预判性降频。判限频请用 `GetCoreThrottling`。
- 单核温度高不一定全机问题：核间温度可能差 10–20 °C。多核监视要分别建 FB 实例并各自调用。
- 调用频率建议 ≥ 100 ms。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TC_CoreBoostMonitor.TcPOU`](../examples/P_Demo_TC_CoreBoostMonitor.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 完整场景见 TC_CoreBoostMonitor.md；本片段聚焦 GetCoreTemperature
VAR
    fbBoostMonitor          : TC_CoreBoostMonitor := (nCoreId := -1);
    hrTempResult            : HRESULT;
    nCurrentTemperatureC    : UDINT;
    nMaxObservedTemperatureC: UDINT;
    nTemperatureLimitC      : UDINT;
    nThermalMarginC         : DINT;   // 余量 = 上限 - 当前
END_VAR

hrTempResult := fbBoostMonitor.GetCoreTemperature(
    nCurrentTemp := nCurrentTemperatureC,
    nMaxTemp     := nMaxObservedTemperatureC,
    nTempLimit   := nTemperatureLimitC
);

IF SUCCEEDED(hrTempResult) THEN
    // 余量算成 DINT 避免 UDINT 下溢
    nThermalMarginC := TO_DINT(nTemperatureLimitC) - TO_DINT(nCurrentTemperatureC);
END_IF
```

## 7. 业务场景与实际价值

- **场景**：把核温度作为生产线"健康度"指标之一上报 MES。班次结束时把 `nMaxTemp` 入库，长期趋势可以发现"散热风扇老化"或"机箱进风口积灰"——硬件还没坏，运营已经知道该停机维护。
- **价值**：把"硬件即将出问题"从事后处理变成事前预警；同时给问题诊断提供量化依据（具体多少度，对比历史）。
- **替代方案对比**：
  - 不监视：故障发生才查
  - 用 `lm-sensors` / Windows 系统温度：拿到的是"封装温度"或"主板传感器"，不是实时核的精确温度
  - **本方法**：每个实时核独立精确读数，跟"是否被限频"对应得上

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.83.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/16219549067.html
- **父 FB**：[`TC_CoreBoostMonitor`](TC_CoreBoostMonitor.md)
- **同 FB 其他方法**：[`GetAllRtCoreThrottling`](GetAllRtCoreThrottling.md) · [`GetCoreFrequency`](GetCoreFrequency.md) · [`GetCoreThrottling`](GetCoreThrottling.md) · [`GetPowerConsumption`](GetPowerConsumption.md)
