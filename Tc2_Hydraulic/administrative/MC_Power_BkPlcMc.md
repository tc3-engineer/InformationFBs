# MC_Power_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Administrative` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599672203.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_Power_BkPlcMc.TcPOU`](../examples/P_Demo_MC_Power_BkPlcMc.TcPOU) |

---

## 1. 功能简述

控制液压轴外部执行器（valve 输出级 / 变频器 / 伺服驱动器）使能信号的 PLCopen 风格功能块。`Enable` 给出主使能，`Enable_Positive` / `Enable_Negative` 给出方向性使能（用于支持双向独立闸门的硬件）。使能同时激活该轴的错误监视；输出 `Status` 反映外部硬件就绪状态（`bPowerOk`），出错则 `Error` + `ErrorID` 给码（错误码以 `dwTcHydErrCd…` 系列常量定义在库的全局常量中）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Enable:             BOOL;
    Enable_Positive:    BOOL;
    Enable_Negative:    BOOL;
    BufferMode:         MC_BufferMode_BkPlcMc:=Aborting_BkPlcMc;  //from V3.0.8
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Enable` | `BOOL` | — | 主使能。`TRUE` 激活轴的外部执行器；同时打开错误监视通道 |
| `Enable_Positive` | `BOOL` | — | 正向方向使能。`TRUE` 允许执行器输出"正方向"动作；对仅支持单向使能的硬件可固定为 `TRUE` |
| `Enable_Negative` | `BOOL` | — | 负向方向使能。`TRUE` 允许执行器输出"负方向"动作；对仅支持单向使能的硬件可固定为 `TRUE` |
| `BufferMode` | `MC_BufferMode_BkPlcMc` | `Aborting_BkPlcMc` | 保留，为未来扩展预留。当前版本仅允许 `Aborting_BkPlcMc`（默认值），不要传其他常量（自 V3.0.8 起加入） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis:       AXIS_REF_BkPlcMc;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF_BkPlcMc` | 轴接口结构。包含轴参数指针、I/O 设备指针、运行时数据等全部上下文。必须以 `VAR_IN_OUT` 方式传引用（地址语义） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Busy:       BOOL;
    Status:     BOOL;
    Error:      BOOL;
    ErrorID:    UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | 表示命令正在执行中。本 FB 不需任何时间，`Busy` 永远为 `FALSE`，仅为 PLCopen 兼容性保留 |
| `Status` | `BOOL` | 就绪状态。`TRUE` 表示外部执行器已上电且无故障（来源依硬件类型分别为 `Enable` 回采 / `bTerminalState` / `bPowerOk`，详见 §3）。⚠️ 注意：PDF 的描述表中此字段被写作 `State`（与代码块 `Status` 不一致），InfoSys 一致写作 `State`；以代码块名为准 |
| `Error` | `BOOL` | 出错指示。`TRUE` 时同时给出 `ErrorID` |
| `ErrorID` | `UDINT` | 编码后的错误号。具体值见 §4 |

## 3. 行为说明

**调用模式**：每个 PLC 周期都应调用一次。本 FB 不是边沿触发，而是**电平**式（持续 `Enable := TRUE` 来维持使能输出）。撤回 `Enable` 即关执行器。

**驱动器类型分支**：FB 根据 `Axis.pStAxParams^.nDrive_Type` 选择三种处理路径之一。

1. **`iTcMc_DriveAx2000_XXXXX`（AX 系列伺服）**：
   - 先校验 `pStDeviceInput` 和 `pStDeviceOutput` 指针是否初始化。未初始化 → `Error := TRUE`、`ErrorID := dwTcHydErrCdPtrPlcDriveIn` 或 `dwTcHydErrCdPtrPlcDriveOut`、`Status := FALSE`
   - 与 AX 设备通讯出错 / `pStDeviceInput` 报错 → `Error := TRUE`、`ErrorID` 为库全局常量定义的对应码、`Status := FALSE`，并把轴置入错误状态（轴错误为 `dwTcHydErrCdDriveNotReady`）
   - 正常情况下 `Status := Enable`（即把使能命令回采为就绪信号）
2. **`iTcMc_DriveKL2531` / `iTcMc_DriveKL2541`（步进端子）**：
   - 同样校验设备指针；未初始化处理同上
   - `Enable` 写入 `pStDeviceOutput.bTerminalCtrl` 的相应 bit 激活端子输出级，`Status := pStDeviceInput.bTerminalCtrl.bTerminalState`（端子就绪反馈）
   - `Enable_Positive` 经 `dwTcHydDcDwFdPosEna` mask 写入 `pStAxRtData.nDeCtrlDWord`，`Enable_Negative` 经 `dwTcHydDcDwFdNegEna` mask 写入同字段
3. **其他驱动类型**（默认分支）：
   - 同样先校验设备指针
   - `Status := pStDeviceInput.bPowerOk`（外部硬件 ready 反馈）
   - `Enable` 经 `dwTcHydDcDwCtrlEnable` mask 写入 `pStAxRtData.nDeCtrlDWord`
   - `Enable_Positive` / `Enable_Negative` 经各自 mask 写入同字段

**典型时序**：开机后先调用 `MC_Power_BkPlcMc(Enable := TRUE, Enable_Positive := TRUE, Enable_Negative := TRUE, Axis := axHyd)`，等 `Status = TRUE` 后再发任何运动命令（MC_MoveAbsolute 等）。运动结束后通常保持 `Enable` 一段时间以承载停留力；停机时撤 `Enable`。

**典型陷阱**：
- 把本 FB 当成"一次性触发"调用 → 撤掉 `Enable` 即失能。要持续动作就要每周期调用且 `Enable` 保持高
- `Enable_Positive` 与 `Enable_Negative` 都填 `FALSE` 而 `Enable := TRUE` → 主使能开了但方向被锁，运动命令会"原地不动"或报跟随误差超时

## 4. 错误码 / 返回值

`Error = TRUE` 时 `ErrorID` 给出编码错误号，定义在库全局常量（PDF §5.2，InfoSys 主题 `1599826187.html`）中。常见值：

| 错误码常量 | 含义 | 处理建议 |
|---|---|---|
| `dwTcHydErrCdPtrPlcDriveIn` | `pStDeviceInput` 指针未初始化 | 检查 AXIS_REF_BkPlcMc 中 `pStDeviceInput` 是否在 PROGRAM_INIT 阶段正确指向硬件映像变量 |
| `dwTcHydErrCdPtrPlcDriveOut` | `pStDeviceOutput` 指针未初始化 | 同上，对 `pStDeviceOutput` |
| `dwTcHydErrCdDriveNotReady` | AX/KL 端子通讯错或端子报错 | 检查 EtherCAT/K-bus 状态、端子诊断 bit；驱动复位后再 `MC_Reset_BkPlcMc` |

⚠️ PDF 与 InfoSys 均未在本 FB 章节穷举具体的数值常量；完整码表参见 PDF §5.2 全局常量章节或 InfoSys 主题 `1599826187.html`。

## 5. 使用注意 / 常见坑

- **`Status` 与 `State` 字段名不一致**（PDF 描述表与代码块自身矛盾，InfoSys 跟描述表）：以代码块名 `Status` 为准（即应用代码用 `fbPower.Status`），仓库严格按 PDF 代码块字面搬运。
- **必须每周期调用**：不像运动命令是边沿触发，`MC_Power_BkPlcMc` 是电平驱动；漏调一帧立即失能。建议放在轴标准调用块（`MC_AxStandardBody_BkPlcMc`）之前。
- **方向使能也是电平**：要把单向锁住可单独撤 `Enable_Positive` 或 `Enable_Negative`；不要试图通过"沿"切方向。
- **`BufferMode` 当前无效**：尽管接口允许，传任何非 `Aborting_BkPlcMc` 的常量都属"未来保留"，会被忽略或在更高版本可能行为变化（工程经验补充）。
- **AX 系列硬件路径**：`Status` 是 `Enable` 自身回采而非真实驱动器 ready 信号。要做"驱动真的上电"判断，需另读 `pStDeviceInput` 中 AX 的状态字。
- **撤 `Enable` 不等于安全停车**：失能瞬间执行器输出归 0，对液压轴可能造成保持力丢失、负载下坠。安全停车应先发 `MC_Stop_BkPlcMc` 减速、待 `Done`，再撤 `Enable`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_Power_BkPlcMc.TcPOU`](../examples/P_Demo_MC_Power_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机液压锁模轴。上电后必须先给比例阀输出级"使能 + 双向使能"信号，输出级 ready 反馈回到 PLC 才允许发"合模到 350 mm"运动命令；急停时先撤 `Enable_Positive` / `Enable_Negative` 锁住运动方向，再 `MC_Stop_BkPlcMc` 减速到 0。
- **价值**：手写时需要：① 设置 `pStAxRtData.nDeCtrlDWord` 的 `dwTcHydDcDwCtrlEnable` bit；② 读 `pStDeviceInput.bPowerOk`；③ 在 AX / KL2531 / 其他 三种硬件分支下写不同的 bit。本 FB 把硬件分支封进去，业务代码只需 `fb(Enable, Enable_Positive, Enable_Negative)` 三个布尔信号即可，硬件换型只改轴参数 `nDrive_Type` 而不动 PLC 代码。
- **替代方案对比**：
  - 直接写 `nDeCtrlDWord` bit：需熟悉 `dwTcHydDcDwCtrlEnable` 等掩码，每加一种新驱动器都要改业务代码
  - 不调本 FB 直接发运动命令：在大多数硬件路径下运动 FB 会因 "drive not ready" 报错；调用本 FB 是 Beckhoff 推荐入口
  - **本 FB**：标准 PLCopen 风格使能流程，硬件无关，错误监视一并打开

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599672203.html
- **相关 FB**：`MC_Reset_BkPlcMc`（清错）、`MC_Stop_BkPlcMc`（安全停车后再失能）、`MC_AxStandardBody_BkPlcMc`（轴循环骨架）、`AXIS_REF_BkPlcMc`（轴接口结构）

## 9. 待确认项 (⚠️)

- PDF 输出表把字段命名为 `State`，但代码块写 `Status`；InfoSys 沿用 `State`。本仓库严格按 PDF 代码块字面 `Status` 搬运（应用代码也是 `fbPower.Status`），仅在 §2 描述中点明 PDF 内部不一致。
