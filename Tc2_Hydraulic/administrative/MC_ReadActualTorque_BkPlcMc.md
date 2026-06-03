# MC_ReadActualTorque_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Administrative` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599674251.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_ReadActualTorque_BkPlcMc.TcPOU`](../examples/P_Demo_MC_ReadActualTorque_BkPlcMc.TcPOU) |

---

## 1. 功能简述

读取液压轴当前实际**力**或**压力**值的 PLCopen 风格功能块。尽管 PLCopen 把这个 FB 的输出字段命名为 `Torque`（力矩），但在液压库里它实际承载的是 `pStAxRtData` 中由压力反馈/力反馈 FB（`MC_AxRtReadPressureSingle_BkPlcMc` 等）刷新的"实际力或实际压力"——具体语义由 `E_TcMcPressureReadingMode` 决定。`Enable` 上升沿触发刷新，`Valid` 标志可用，`Error` + `ErrorID` 在编码器故障时给码。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Enable:     BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Enable` | `BOOL` | — | 上升沿触发一次实际值刷新；下降沿清所有输出 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis:       AXIS_REF_BkPlcMc;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF_BkPlcMc` | 轴接口结构。必须以 `VAR_IN_OUT` 方式传引用 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Valid:      BOOL;
    Busy:       BOOL;
    Error:      BOOL;
    ErrorID:    UDINT;
    Torque:     LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Valid` | `BOOL` | 实际值已成功读取，`Torque` 字段有效 |
| `Busy` | `BOOL` | 命令处理中。本 FB 不需任何时间，`Busy` 永远为 `FALSE`，仅为 PLCopen 兼容性保留 |
| `Error` | `BOOL` | 出错指示。编码器侧有问题时置 `TRUE` |
| `ErrorID` | `UDINT` | 编码错误号 |
| `Torque` | `LREAL` | 实际力（N / kN）或实际压力（bar / MPa）。具体物理含义由轴参数和压力反馈 FB 决定 |

## 3. 行为说明

**调用模式**：每周期调用，`Enable` 是电平触发。

**校验路径**：`Enable` 上升沿时检查轴接口；若轴处于编码器相关错误状态 → `Error := TRUE`、`ErrorID := 编码器错误码`、`Valid := FALSE`。否则读出力/压力值写入 `Torque` 并 `Valid := TRUE`。

**数据来源**：`Torque` 实际是 `pStAxRtData` 中由 `MC_AxRtReadPressureSingle_BkPlcMc` / `MC_AxRtReadPressureDiff_BkPlcMc` / `MC_AxRtReadForceSingle_BkPlcMc` / `MC_AxRtReadForceDiff_BkPlcMc` 在每周期更新的字段。读哪个字段由轴的 `E_TcMcPressureReadingMode` 配置决定。

**典型用法**：注塑保压段实时显示活塞压力；冲压设备力矩闭环监控；液压系统过载报警。

**典型陷阱**：
- 没有先调任何 `MC_AxRtReadPressureXxx_BkPlcMc` 就读本 FB：`Torque` 字段是 0 或上次值，因为没人在更新它
- 把 `Torque` 当 N·m（电机力矩）理解：在液压库里实际是液压力或压力反馈，单位由你硬件传感器决定

## 4. 错误码 / 返回值

| `Error` | `ErrorID` | 含义 | 处理建议 |
|---|---|---|---|
| `FALSE` | `0` | 正常 | 使用 `Torque` 值 |
| `TRUE` | = 轴编码器错误码 | 编码器侧故障 | 修复编码器后 `MC_Reset_BkPlcMc` |

⚠️ 具体编码器错误码未在本 FB 章节列出；参见 PDF §5.2 全局常量。

## 5. 使用注意 / 常见坑

- **`Torque` 字段名误导**：PLCopen 命名继承自电机轴库，液压库里实际承载力 / 压力反馈，不是力矩。读数前先确定轴用的是哪种 `E_TcMcPressureReadingMode`。
- **数据流依赖**：必须先在轴 cyclic body 里调用至少一个 `MC_AxRtReadPressureXxx_BkPlcMc` 把数据写进 `pStAxRtData`，本 FB 才能读到真实值。
- **`Busy` 总为 FALSE**：判完成看 `Valid`。
- **单位由传感器决定**：`Torque` 是浮点数，物理单位（N / kN / bar / MPa）由你硬件标定后通过压力反馈 FB 的标定系数决定，PDF 不强制。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_ReadActualTorque_BkPlcMc.TcPOU`](../examples/P_Demo_MC_ReadActualTorque_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机锁模到位后切换到"保压"控制段，实时显示活塞压力（bar）做闭环；超 250 bar 触发"过保压"报警。
- **价值**：屏蔽编码器故障期间的旧值，避免显示假数据让操作员误判。
- **替代方案对比**：
  - 直接读 `pStAxRtData^.fActTorque`（或对应字段）：性能略好但要自己处理编码器错误
  - 用 IO 终端原始 AD 值：需自己做线性化、标定、滤波，与轴反馈链不一致
  - **本 FB**：标准 PLCopen 接口，与轴 runtime data 链一致

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599674251.html
- **相关 FB**：`MC_AxRtReadPressureSingle_BkPlcMc`、`MC_AxRtReadPressureDiff_BkPlcMc`、`MC_AxRtReadForceSingle_BkPlcMc`、`MC_AxRtReadForceDiff_BkPlcMc`（提供数据源）、`E_TcMcPressureReadingMode`（决定取哪个字段）
