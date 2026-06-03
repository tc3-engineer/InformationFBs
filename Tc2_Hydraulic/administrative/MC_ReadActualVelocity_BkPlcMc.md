# MC_ReadActualVelocity_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Administrative` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599675275.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_ReadActualVelocity_BkPlcMc.TcPOU`](../examples/P_Demo_MC_ReadActualVelocity_BkPlcMc.TcPOU) |

---

## 1. 功能简述

读取液压轴当前实际速度（单位 mm/s）的 PLCopen 风格功能块。`Enable` 上升沿触发刷新，`Valid` 为 `TRUE` 时 `Velocity` 字段是有效值；`Enable` 下降沿清所有输出。`Busy` 永远为 `FALSE`（不需要时间）。出现编码器故障时 `Error` + `ErrorID` 给码。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Enable:     BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Enable` | `BOOL` | — | 上升沿触发一次速度值刷新；下降沿清所有输出 |

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
    Velocity:   LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Valid` | `BOOL` | 速度已成功读取，`Velocity` 有效 |
| `Busy` | `BOOL` | 本 FB 不需任何时间，`Busy` 永远为 `FALSE`，仅为 PLCopen 兼容性保留 |
| `Error` | `BOOL` | 出错指示（编码器故障） |
| `ErrorID` | `UDINT` | 编码错误号 |
| `Velocity` | `LREAL` | 实际速度，单位 mm/s |

## 3. 行为说明

**调用模式**：每周期调用，电平触发（`Enable` 持续高即持续刷新）。

**校验路径**：`Enable` 上升沿检查轴接口；若轴处于编码器相关错误状态 → `Error := TRUE`、`ErrorID := 编码器错误码`、`Valid := FALSE`。否则读取实际速度写入 `Velocity` 并 `Valid := TRUE`。

**速度计算源**：液压轴的实际速度由 `MC_AxRtEncoder_BkPlcMc` 在每周期通过对位置做数值微分计算（按 `pStAxParams^.fTcCycle` 的循环周期），结果存入 `pStAxRtData^.fActVelocity`。本 FB 读这个字段并做错误屏蔽。由于液压轴的实际速度信号噪声大，建议在轴参数里设置 `nVelo_FiltFactor` 做一阶低通滤波。

**典型用法**：监控加减速段的速度跟随；保压段判断"是否真停了"（速度 ≈ 0）；位置反馈链问题诊断（位置在走但速度恒为 0 → 速度滤波器卡住或位置变化太小被微分噪声掩盖）。

**典型陷阱**：
- 速度噪声未滤波 → `Velocity` 值跳变剧烈；调 `pStAxParams^.nVelo_FiltFactor` 或 `pStAxParams^.fVelo_Filter`
- 判断"轴已停"用 `Velocity = 0` → 浮点比较不可靠，应用 `ABS(Velocity) < 阈值`（阈值取传感器分辨率 ÷ 周期）

## 4. 错误码 / 返回值

| `Error` | `ErrorID` | 含义 | 处理建议 |
|---|---|---|---|
| `FALSE` | `0` | 正常 | 使用 `Velocity` 值 |
| `TRUE` | = 轴编码器错误码 | 编码器侧故障 | 修复编码器后 `MC_Reset_BkPlcMc` |

⚠️ 具体编码器错误码未在本 FB 章节列出；参见 PDF §5.2 全局常量。

## 5. 使用注意 / 常见坑

- **噪声大要先滤波**：液压轴位置反馈通常用磁致伸缩或 SSI 编码器，速度由位置微分得到，噪声极大。务必在轴参数里设置速度滤波器，否则 `Velocity` 看着跳变剧烈难以使用。
- **`Velocity` 方向有符号**：正向运动 > 0，反向运动 < 0；判"运动方向"用符号，判"速度大小"用 `ABS()`。
- **`Busy` 总为 FALSE**：判读取完成看 `Valid`。
- **"轴停"判定不要用 `=0`**：浮点比较应该用阈值；典型阈值 0.5 mm/s 或更小，取决于速度滤波器和编码器精度。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_ReadActualVelocity_BkPlcMc.TcPOU`](../examples/P_Demo_MC_ReadActualVelocity_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机合模过程实时显示锁模头速度做 HMI 图表；合模到位前需要判断"真的停下来了"再切换到保压段。
- **价值**：自动屏蔽编码器故障期间的旧值；标准 PLCopen 接口与其它 Read* FB 一致。
- **替代方案对比**：
  - 直接读 `pStAxRtData^.fActVelocity`：性能略好但需自己处理编码器错误
  - PLC 自己对位置做微分：噪声更大，且与轴 cyclic 反馈链不一致
  - **本 FB**：标准接口，自带错误屏蔽

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.1.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599675275.html
- **相关 FB**：`MC_ReadActualPosition_BkPlcMc`（读位置）、`MC_ReadActualTorque_BkPlcMc`（读力/压力）、`MC_AxRtEncoder_BkPlcMc`（实际速度数据源）
