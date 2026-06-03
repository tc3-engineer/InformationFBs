# MC_ReadActualPosition_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Administrative` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599673227.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_ReadActualPosition_BkPlcMc.TcPOU`](../examples/P_Demo_MC_ReadActualPosition_BkPlcMc.TcPOU) |

---

## 1. 功能简述

读取液压轴当前实际位置（单位 mm）的 PLCopen 风格功能块。`Enable` 上升沿触发一次刷新，`Valid = TRUE` 时 `Position` 字段是有效的实际位置；`Enable` 下降沿清所有输出。`Busy` 字段在本 FB 中永远为 `FALSE`（只为 PLCopen 兼容性保留），因为读位置不需要任何时间。出现编码器错误时 `Error` + `ErrorID` 给码（`ErrorID = 编码器错误码`）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Enable:     BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Enable` | `BOOL` | — | 上升沿触发一次位置值刷新；持续高电平等同于持续刷新；下降沿清所有输出 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis:       AXIS_REF_BkPlcMc;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF_BkPlcMc` | 轴接口结构。包含编码器指针、运行时数据等。必须以 `VAR_IN_OUT` 方式传引用 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Busy:       BOOL;
    Valid:      BOOL;
    Error:      BOOL;
    ErrorID:    UDINT;
    Position:   LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | 表示命令正在执行中。本 FB 不需任何时间，`Busy` 永远为 `FALSE`，仅为 PLCopen 兼容性保留 |
| `Valid` | `BOOL` | 实际位置已成功读取并写入 `Position` 字段 |
| `Error` | `BOOL` | 出错指示。编码器有问题时置 `TRUE` |
| `ErrorID` | `UDINT` | 编码错误号。出错时 = 该轴编码器错误码 |
| `Position` | `LREAL` | 实际位置，单位 mm（与轴 fScale 参数定义的物理单位一致） |

## 3. 行为说明

**调用模式**：每周期调用一次；`Enable` 是电平（持续高 = 持续刷新，下降沿清输出）。注意 PDF 文档中 `Enable` 描述写的是"上升沿触发一次刷新"，但后续行为说明又说"下降沿清所有输出"——实际工程使用中惯例是 `Enable := TRUE` 期间每周期刷新 `Position`。

**校验路径**：FB 每次调用都检查轴接口状态。若轴处于编码器相关的错误状态 → `Error := TRUE`、`ErrorID := 该编码器错误码`、`Valid := FALSE`。

**清错路径**：编码器错误需要先解决硬件问题（信号丢失 / 总线断开 / 计数溢出等），然后 `MC_Reset_BkPlcMc` 把轴拉回正常状态，再重新 `Enable`。

**典型用法**：HMI 实时显示轴位置；运动结束后做位置比对；位置触发的事件链（"轴到 100 mm 时启动夹爪"）。

**典型陷阱**：
- 不调本 FB 直接读 `Axis.pStAxRtData^.fActPosition`：原始值未经编码器错误屏蔽，故障时仍能读到旧值，可能造成"误以为到位"
- 把本 FB 当做"获取实时值"用：本 FB 是 PLCopen 兼容包装，开销略大；高频内部逻辑可直接读结构体字段，但要自己处理编码器错误

## 4. 错误码 / 返回值

| `Error` | `ErrorID` | 含义 | 处理建议 |
|---|---|---|---|
| `FALSE` | `0` | 正常，`Position` 有效 | 取用 `Position` 值 |
| `TRUE` | = 轴编码器错误码 | 编码器侧故障（断线 / 信号丢失 / 校验失败等） | 查 PDF §5.2 全局常量 `dwTcHydErrCdEnc*` 系列；硬件复位后 `MC_Reset_BkPlcMc` |

⚠️ 具体编码器错误码值未在本 FB 章节列出；参见 PDF §5.2 全局常量章节。

## 5. 使用注意 / 常见坑

- **`Busy` 总为 FALSE**：不要据 `Busy` 判断 FB 是否完成；位置读取是同步的，看 `Valid` 即可。
- **`Position` 单位由轴 fScale 决定**：PDF 注释为 mm，但实际单位是 `pStAxParams^.fScale` 把脉冲/分辨率转换出来的工程单位（线性轴一般是 mm，旋转可能是 ° 或 rev）。
- **不能取代连续位置控制**：本 FB 只是"读"，不参与控制环；位置反馈由 `MC_AxRtEncoder_BkPlcMc` 在每周期循环里完成。
- **多实例无影响**：可以同时多个 `MC_ReadActualPosition_BkPlcMc` 实例指向同一轴，互不干扰（都只读）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_ReadActualPosition_BkPlcMc.TcPOU`](../examples/P_Demo_MC_ReadActualPosition_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机锁模轴在合模到 350 mm 后启动注射程序。需要 HMI 实时显示位置 / 业务代码判断"到位"再触发下一步。
- **价值**：相比直接读 `pStAxRtData.fActPosition` 结构体字段，本 FB 自动屏蔽编码器故障期间的旧值，避免"老数据导致误触发"。
- **替代方案对比**：
  - 直接读结构体 `Axis.pStAxRtData^.fActPosition`：性能略好但需自己处理编码器错误标志
  - 通过 ADS 读 PLC 内变量：HMI 端常用，但在 PLC 内自己用更直接
  - **本 FB**：标准 PLCopen 接口，错误屏蔽内置，适合业务代码

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599673227.html
- **相关 FB**：`MC_ReadActualVelocity_BkPlcMc`（读速度）、`MC_ReadActualTorque_BkPlcMc`（读力/压力）、`MC_ReadAxisError_BkPlcMc`（读错误码）、`MC_ReadStatus_BkPlcMc`（读状态机）
