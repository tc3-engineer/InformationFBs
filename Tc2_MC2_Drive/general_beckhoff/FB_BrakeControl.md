# FB_BrakeControl

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `General Beckhoff` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/14430241419.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_BrakeControl.xml`](../examples/P_Demo_FB_BrakeControl.xml) |

---

## 1. 功能简述

手动控制 Beckhoff 伺服硬件上电机抱闸（brake / holding brake）的功能块（Function Block, FB）。正常情况下抱闸由驱动器的使能（Enable）自动联动——使能时松闸、失能时抱闸；本 FB 让你**绕过这套自动逻辑**，手动把抱闸锁死或强制松开。

通过 `Mode` 选择三种行为：`eBrakeMode_Automatic`（恢复自动控制）、`eBrakeMode_Lock`（永久抱死，即使 `MC_Power` 使能也不松）、`eBrakeMode_Unlock`（永久松开，即使 `MC_Power` 失能也不抱）。

⚠️ **安全警告（来自 PDF）**：手动松闸时垂直轴可能因重力下坠，务必采取防坠措施。官方建议——手动开/闭抱闸只在必要时段短暂使用，用完立即用本 FB 切回 `eBrakeMode_Automatic`。本 FB 是硬件无关入口，绑定具体型号可用 `FB_SoEAX5000SetMotorCtrlWord` / `FB_CoEAX8000BrakeControl` / `FB_CoEEL72xxBrakeControl`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute : BOOL;
    Mode    : E_BrakeMode;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次抱闸控制命令；不需保持高电平 |
| `Mode` | `E_BrakeMode` | — | 抱闸控制模式：`eBrakeMode_Automatic`（自动开闭）/ `eBrakeMode_Lock`（永久抱死，`MC_Power` 使能也不松）/ `eBrakeMode_Unlock`（永久松开，`MC_Power` 失能也不抱，⚠️ 见警告） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | 唯一标识系统中一根轴的数据结构，含位置、速度、错误状态等循环数据。**必须传引用**（VAR_IN_OUT 语义） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Busy    : BOOL;
    Error   : BOOL;
    ErrorID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | FB 激活后置位，直到收到反馈才复位 |
| `Error` | `BOOL` | `Busy` 复位后若传输命令时发生错误则置位 |
| `ErrorID` | `UDINT` | `Error = TRUE` 时返回 ADS 错误码（见 §4） |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次抱闸模式切换：FB 通过 ADS/SoE/CoE 把 `Mode` 写到驱动器，`Busy := TRUE`，异步等待驱动器确认，**跨多个 PLC 周期**，必须每周期循环调用直到 `Busy` 落回 `FALSE`。

**模式语义（这是核心，不是 Done/Active 状态机）**：
- `eBrakeMode_Lock`：抱闸**永久闭合**。此后即使调用 `MC_Power` 给轴使能，抱闸也不松开——轴被机械锁住无法运动。
- `eBrakeMode_Unlock`：抱闸**永久松开**。此后即使 `MC_Power` 失能，抱闸也不闭合——这意味着垂直/重力轴失去机械保持，⚠️ 有下坠风险。
- `eBrakeMode_Automatic`：恢复"使能联动"自动控制，即驱动器按 Enable 自动开闭抱闸。这是默认且安全的状态。

**完成与出错收敛**：本 FB 无 `Done` 输出。成功判据是 **`Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`**；出错则 `Busy` 复位后 `Error := TRUE`、`ErrorID` 给 ADS 错误码。

**典型用法时序**：手动开闸装夹工件 → 操作完成 → 立刻发 `eBrakeMode_Automatic` 还原。绝不要把轴长期停在 `Lock`/`Unlock` 状态，否则使能逻辑与抱闸状态脱节，下次自动运动时行为不可预测。`Execute` 是边沿触发，切模式必须制造新的上升沿。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 **ADS 错误码**（不是 NC 错误号、也不是 HRESULT）。

| 错误来源 | 含义 | 处理建议 |
|---|---|---|
| ADS 通信错误 | 与驱动器的 ADS 传输失败（超时、设备不可达、AmsNetId 错误等） | 检查 EtherCAT 总线 OP、轴 Link、`Axis` 引用有效性 |
| 驱动器/电机不支持抱闸控制 | 当前硬件无抱闸或固件版本不满足要求 | 核对硬件型号与固件（AX5xxx 需 FW ≥ v1.07 b0001；AX8xxx/AMP/MD8xxx 需 ≥ v1.04 b0001；EL72xx 仅带 OCT 且 FW ≥ v16） |

⚠️ PDF 与 InfoSys 在本 FB 章节未逐条列出具体 ADS 错误码，请参见 Beckhoff ADS Return Codes 总表。

**清错**：处理完外部原因后给 `Execute` 新的上升沿重试即可；本 FB 无独立清错入口。

## 5. 使用注意 / 常见坑

- **用完必须切回 `eBrakeMode_Automatic`**：这是 PDF 明确建议。停在 `Lock`/`Unlock` 会让抱闸与使能逻辑脱节，是事故高发点。
- **`eBrakeMode_Unlock` 对垂直轴是高危操作**：松开后失能不抱闸，重力轴会下坠，操作前必须有机械支撑或风险评估（PDF WARNING）。
- **`eBrakeMode_Lock` 下 `MC_Power` 使能不松闸**：会出现"使能成功但轴一动就报跟随误差"的现象，因为抱闸还锁着。
- **没有 `Done` 输出**：判完成靠 `Busy` 落回 `FALSE` 且 `Error = FALSE`。
- **`Execute` 是边沿触发**：切换模式必须制造新上升沿，一直拉高不会反复生效。
- **`Busy` 期间持续循环调用**：异步操作跨周期。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_BrakeControl.xml`](../examples/P_Demo_FB_BrakeControl.xml)

```iecst
// 场景：手动松闸用人力盘动电机做机械对位，盘完立即切回自动
rtBrakeTrig(CLK := bBrakeCmdReq);
fbBrakeCtrl(
    Execute := rtBrakeTrig.Q,
    Mode    := eRequestedBrakeMode,
    Axis    := axisLiftAxis,
    Busy    => bBrakeBusy,
    Error   => bBrakeError,
    ErrorID => nBrakeErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：维修时手动盘动电机做机械对位、抱闸保养检测、装夹工件时临时锁轴防移动；用完一律切回自动。
- **价值**：不必进驱动器参数手册改 SoE/CoE 抱闸字，一个 FB + 三种枚举即可手动接管抱闸，且硬件无关。
- **替代方案对比**：
  - 直接写驱动器 SoE/CoE 抱闸参数：需查具体型号参数号，代码与硬件耦合
  - `FB_SoEAX5000SetMotorCtrlWord`（AX5000）/ `FB_CoEAX8000BrakeControl`（AX8000）/ `FB_CoEEL72xxBrakeControl`（EL72xx）：型号专用，行为等价
  - **本 FB**：硬件无关统一入口，跨型号通用

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/14430241419.html
- **相关 FB**：`FB_SoEAX5000SetMotorCtrlWord` / `FB_CoEAX8000BrakeControl` / `FB_CoEEL72xxBrakeControl`（型号专用抱闸控制）、`MC_Power`（轴使能，正常情况下抱闸由它联动）
