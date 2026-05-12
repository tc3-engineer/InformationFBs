# GetPowerConsumption

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
| Example | [`examples/P_Demo_TC_CoreBoostMonitor.xml`](../examples/P_Demo_TC_CoreBoostMonitor.xml) |

---

## 1. 功能简述

`GetPowerConsumption` 是 [`TC_CoreBoostMonitor`](TC_CoreBoostMonitor.md) 的方法之一，读取 CPU **封装层（platform package）**当前总功耗以及功耗上限。注意它是**整个封装**的数据，不是单核——同 package 内所有实时核调用本方法读到的两个值相同。

`nCurrentPackagePowerConsumption` 反映瞬时功耗（瓦），`nPackagePowerLimit` 是当前生效的功耗上限（瓦），CPU 持续超过这个上限就会自动限频（即 `bRtInPowerThrottling = TRUE`）。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD GetPowerConsumption : HRESULT
VAR_INPUT
    nCurrentPackagePowerConsumption : REFERENCE TO UDINT;
    nPackagePowerLimit              : REFERENCE TO UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nCurrentPackagePowerConsumption` | `REFERENCE TO UDINT` | 引用回填：platform package 当前总功耗，单位瓦（W）。所有实时核共享同一封装时读数相同 |
| `nPackagePowerLimit` | `REFERENCE TO UDINT` | 引用回填：platform package 功耗上限（W）。超过此限会触发自动降频 |

### 返回值

`HRESULT`：`SUCCEEDED(hr) = TRUE` 表示读取成功，两个引用参数有效。

### VAR_IN_OUT

无。

## 3. 行为说明

被调用时方法同步查询 TwinCAT 实时层维护的 RAPL（Running Average Power Limit）寄存器镜像并立即写回两个引用变量。底层是 Intel CPU 的 RAPL 计数器，由硬件累计能量然后换算成瞬时功耗。

**Package 维度的含义**：现代 CPU 把多个核封装在同一硅片或同一封装基板内，共享主电源、共享供电环。所以"功耗"是 package 级别的总和，而不是逐核分摊。这导致同 package 的所有实时核调用本方法读到的两个数值都一样——这不是 bug，是物理事实。

**功耗上限的含义**：CPU 的功耗包络分两个层次——短期高峰（PL2）与长期持续（PL1）。`nPackagePowerLimit` 反映的是当前生效的上限。BIOS / 厂商 SKU 出厂时设定，运行时通常不变。CPU 在长时间高功耗运行后会自动触发限频以保证不超过 PL1。

**与温度限频的关系**：功耗限频与温度限频是独立的硬件保护通路。功耗高未必温度高（短期突发负载，散热还来得及），温度高未必功耗高（散热差但负载低）。监视两者都重要。

**典型监视策略**：把当前功耗与上限做比值，超 90 % 就提示"接近 PL1，可能被限频"。配合 `GetCoreThrottling` 看是否真的被限频以验证判断。

## 4. 错误码 / 返回值

方法签名 `METHOD GetPowerConsumption : HRESULT`：

| HRESULT 判定 | 含义 |
|---|---|
| `SUCCEEDED(hr) = TRUE`（通常 `S_OK`） | 查询成功，两个功耗值有效 |
| `FAILED(hr) = TRUE` | 查询失败，常见原因：CPU 不支持 RAPL、`nCoreId` 越界 |

⚠️ 具体失败 `HRESULT` 编码表 PDF 与 InfoSys 均未列出。

## 5. 使用注意 / 常见坑

- 单位是瓦（W）（PDF 明确，"power in watts"）——不要做 mW 单位换算。
- 同 package 各核读数相同：不要逐核累加成"总功耗"，那是错的。整个 package 调一次本方法就够。
- 功耗变化比温度更剧烈：负载切换时功耗瞬间从 30 W 涨到 100 W 很正常；温度因热惯性不会跳那么快。
- `nPackagePowerLimit` 通常是常量：启动时读一次缓存，运行时不必每周期读。
- 功耗超限不等于温度超限：要分别监视，不要混用判断。
- 调用频率建议 ≥ 100 ms；过快的轮询并不会得到更准的数据，RAPL 计数器本身就是滑动平均。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TC_CoreBoostMonitor.xml`](../examples/P_Demo_TC_CoreBoostMonitor.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 完整场景见 TC_CoreBoostMonitor.md；本片段聚焦 GetPowerConsumption
VAR
    fbBoostMonitor          : TC_CoreBoostMonitor := (nCoreId := -1);
    hrPowerResult           : HRESULT;
    nPackagePowerW          : UDINT;
    nPackagePowerLimitW     : UDINT;
    nPowerUtilizationPercent: UDINT;
END_VAR

hrPowerResult := fbBoostMonitor.GetPowerConsumption(
    nCurrentPackagePowerConsumption := nPackagePowerW,
    nPackagePowerLimit              := nPackagePowerLimitW
);

IF SUCCEEDED(hrPowerResult) AND nPackagePowerLimitW > 0 THEN
    // 当前功耗占上限百分比，HMI 用
    nPowerUtilizationPercent := (nPackagePowerW * 100) / nPackagePowerLimitW;
END_IF
```

## 7. 业务场景与实际价值

- **场景**：评估机柜风道与电源冗余设计是否够用。生产线运行高峰时观测 `nPackagePowerW` 稳定在多少瓦，配合机柜进风温度，可以验证机柜散热裕度是否合规。
- **价值**：把"我家机柜散热够不够"从定性变定量。供应商提供的 CPU TDP 通常是参考值，实际负载下的真实功耗只有用本方法才能拿到。
- **替代方案对比**：
  - 用电源监视设备：测的是整机功耗，含外设、风扇、屏，不能反映 CPU 单独功耗
  - 用 Windows `powercfg`：消费级 OS 工具，工业 TwinCAT 系统未必能跑且数据未必准
  - **本方法**：直接读 CPU RAPL 寄存器，最准

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.83.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/16219549067.html
- **父 FB**：[`TC_CoreBoostMonitor`](TC_CoreBoostMonitor.md)
- **同 FB 其他方法**：[`GetAllRtCoreThrottling`](GetAllRtCoreThrottling.md) · [`GetCoreFrequency`](GetCoreFrequency.md) · [`GetCoreTemperature`](GetCoreTemperature.md) · [`GetCoreThrottling`](GetCoreThrottling.md)
