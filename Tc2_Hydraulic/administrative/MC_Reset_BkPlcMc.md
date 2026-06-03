# MC_Reset_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Administrative` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599681419.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_Reset_BkPlcMc.TcPOU`](../examples/P_Demo_MC_Reset_BkPlcMc.TcPOU) |

---

## 1. 功能简述

清除液压轴错误状态、把轴重置到可操作状态（`Errorstop → StandStill`）的 PLCopen 风格功能块。`Execute` 上升沿触发一次复位；成功后 `Done := TRUE`。某些驱动器类型需要与外部设备做信号握手才能复位，复位过程中 `Busy := TRUE`（**这是少数 `Busy` 真会高的情况**）。若错误不可恢复（仍有故障源、握手失败）→ `Error := TRUE`、`ErrorID := 轴的错误码`。`Execute` 下降沿清所有输出。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute:    BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次轴复位；命令开始执行后撤回不影响进行中的复位 |

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
    Busy:       BOOL;
    Done:       BOOL;
    Error:      BOOL;
    ErrorID:    UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | 复位进行中。某些驱动器需要握手时该位为 `TRUE`，等握手结束才出 `Done` / `Error` |
| `Done` | `BOOL` | 复位成功；轴已回到 StandStill 状态 |
| `Error` | `BOOL` | 复位失败（错误源未消除或握手失败） |
| `ErrorID` | `UDINT` | 复位失败时给出轴的错误码 |

## 3. 行为说明

**调用模式**：边沿触发。`Execute` 上升沿启动一次复位，命令进入处理后即可撤回 `Execute`（不影响进行中的复位）。`Execute` 下降沿清所有输出（`Done` / `Error` / `ErrorID`）。

**典型时序**（伺服 / 比例阀典型场景）：
1. `Execute := FALSE → TRUE`：FB 检查轴是否处于 Errorstop
2. 若错误源已消除（编码器接好、限位脱离）：把 `pStAxRtData^.nErrorCode := 0`、状态 → StandStill → `Done := TRUE`
3. 若错误源未消除：`Error := TRUE`、`ErrorID := 当前轴错误码`
4. 若驱动器类型需握手（如某些步进端子要发"清错"命令）：`Busy := TRUE`，等握手结束才出 `Done` / `Error`
5. `Execute := TRUE → FALSE`：清所有输出

**和 `MC_ResetAndStop_BkPlcMc` 的区别**：本 FB 只清错，**不**做停车动作；若轴在错误时还在运动（异常情况），调本 FB 后运动可能继续。若需要"先停车再清错"用 `MC_ResetAndStop_BkPlcMc`。

**典型用法**：HMI 上"清错"按钮接 `MC_Reset_BkPlcMc.Execute`；自动恢复程序在确认故障源消除后调本 FB。

**典型陷阱**：
- 错误源未消除就反复点清错按钮：`Done` 永远不出，`Error` 一直循环；要先解决物理问题
- 清错后立即发运动命令：可能轴还没真正进入 StandStill（特别是需要握手的驱动）；建议等 `Done = TRUE` 或读 `MC_ReadStatus_BkPlcMc.StandStill = TRUE` 再发新命令
- 在 `Busy = TRUE` 期间再次触发 `Execute` 上升沿：行为未定义，应等当前复位结束

## 4. 错误码 / 返回值

| `Done` | `Busy` | `Error` | `ErrorID` | 含义 | 处理建议 |
|---|---|---|---|---|---|
| `TRUE` | `FALSE` | `FALSE` | `0` | 复位成功，轴回 StandStill | 可发新命令 |
| `FALSE` | `TRUE` | `FALSE` | `0` | 握手进行中 | 等 |
| `FALSE` | `FALSE` | `TRUE` | = 轴错误码 | 复位失败（故障源未除） | 先解决物理问题 |

⚠️ 具体 `ErrorID` 数值为该轴 `pStAxRtData^.nErrorCode`，见 PDF §5.2 全局常量。

## 5. 使用注意 / 常见坑

- **`Busy` 在某些驱动是真的 TRUE**：与其它读类 FB 不同，`MC_Reset_BkPlcMc` 的 `Busy` 是有意义的——某些端子（KL2531 等）需要时间清错。等 `Done` 或 `Error` 出来再认为复位结束。
- **复位 ≠ 上电使能**：复位只是清错；要让轴真正可动还需 `MC_Power_BkPlcMc.Enable := TRUE`。
- **复位前应先确认故障源消除**：如编码器线接好、限位开关脱离、油温正常等；否则一清错下个周期立即重新报错。
- **HMI 按钮要做边沿处理**：本 FB 是边沿触发，HMI 按钮一直按住等同只触发一次。可加 `R_TRIG` 边沿检测器使得"长按"不会重复触发。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_Reset_BkPlcMc.TcPOU`](../examples/P_Demo_MC_Reset_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机操作面板上"清错复位"按钮。操作员发现"急停"或"轴错误"指示亮，先检查物理原因（编码器、限位、油压），确认无误后按按钮触发本 FB 清错，等 `Done` 后才允许再开机循环。
- **价值**：标准 PLCopen 复位接口；自动处理驱动器握手时序；与 `MC_ReadStatus_BkPlcMc.Errorstop` 配套形成完整的"出错 → 报警 → 排查 → 清错 → 复运"循环。
- **替代方案对比**：
  - 直接清 `pStAxRtData^.nErrorCode`：跳过驱动器握手，对需握手的驱动会留下残余错
  - 用 `MC_ResetAndStop_BkPlcMc`：会强制减速停车；要"轴正常停了只是有错"场景多余
  - **本 FB**：纯清错，与运动命令解耦

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.1.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599681419.html
- **相关 FB**：`MC_ResetAndStop_BkPlcMc`（先停车再清错）、`MC_ReadAxisError_BkPlcMc`（读错误码确认原因）、`MC_ReadStatus_BkPlcMc`（看 Errorstop 触发清错）
