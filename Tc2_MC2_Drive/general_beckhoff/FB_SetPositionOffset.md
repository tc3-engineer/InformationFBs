# FB_SetPositionOffset

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `General Beckhoff` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/14430264587.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SetPositionOffset.xml`](../examples/P_Demo_FB_SetPositionOffset.xml) |

---

## 1. 功能简述

把**位置偏置（position offset）**写入 Beckhoff 伺服硬件的功能块（Function Block, FB）。位置偏置让你把当前的物理位置"重命名"为一个指定的位置值——典型用于回参考点后设零、或把机械实际位置与工件坐标系对齐，且这个偏置常驻在驱动器/编码器侧，PLC 重启或工程下载都不丢。

`Position` 给定 NC 轴的新实际位置；`Relative = TRUE` 时把 `Position` 解释为相对当前位置的增量，`= FALSE` 时解释为绝对的新位置。`Feedback` 选反馈系统，`Memory` 选偏置存放位置——可存进驱动器内存，也可存进电机编码器的数字铭牌（digital nameplate）。存进铭牌的偏置随电机走，换控制器仍保留。

⚠️ 注意：偏置须先在 DriveManager 里配置好同一存放位置（编码器 / 驱动器），FB 里必须用与配置一致的 `Memory`。本 FB 是硬件无关入口，型号专用版本为 `FB_SoEAX5000SetPositionOffset` / `FB_CoEAX8000SetPositionOffset` / `FB_CoEEL72xxSetPositionOffset`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute  : BOOL;
    Position : LREAL;
    Relative : BOOL;
    Feedback : E_PositionOffsetFeedback;
    Memory   : E_PositionOffsetMemory;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次写偏置操作；不需保持高电平 |
| `Position` | `LREAL` | — | NC 轴的新实际位置（单位为轴用户单位）；`Relative = TRUE` 时按相对增量解释 |
| `Relative` | `BOOL` | — | 置位时把 `Position` 解释为相对当前位置的增量；复位时按绝对位置解释 |
| `Feedback` | `E_PositionOffsetFeedback` | — | 指定参考哪个反馈系统：`ePositionOffsetFeedback1`（= 0）/ `ePositionOffsetFeedback2`（= 1） |
| `Memory` | `E_PositionOffsetMemory` | — | 新偏置存到哪：`ePositionOffsetMemory_Encoder`（= 0，编码器铭牌）/ `ePositionOffsetMemory_Drive`（= 1，驱动器内存） |

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

**触发**：`Execute` 上升沿启动一次写偏置：FB 算出新偏置（依据 `Position`、`Relative` 与当前实际位置）并通过 ADS/SoE/CoE 写入 `Memory` 指定的存储位置，`Busy := TRUE`，异步等待驱动器确认，**跨多个 PLC 周期**，必须每周期循环调用直到 `Busy` 落回 `FALSE`。

**`Relative` 语义**：
- `Relative = FALSE`（绝对）：写入后轴的实际位置直接变成 `Position`。例如 `Position = 0` 即"当前点设为零点"。
- `Relative = TRUE`（相对）：把当前实际位置叠加 `Position` 的增量。例如 `Position = 10` 表示在原有位置基础上 +10。

**完成与出错收敛**：本 FB 无 `Done` 输出。成功判据是 **`Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`**；出错则 `Busy` 复位后 `Error := TRUE`、`ErrorID` 给 ADS 错误码。

**`Memory` / DriveManager 一致性要求**：PDF 明确——偏置须先在 DriveManager 里配置好同一存放位置，FB 里的 `Memory` 必须与之一致，否则偏置不会按预期生效。存进编码器铭牌的偏置随电机迁移，存进驱动器的偏置随驱动器留。

**写偏置改变绝对位置参考**：写入后轴的 `ActPos` 含义改变，应在轴静止时操作，写完重新核对软限位与工件坐标，避免位置跳变引发误动作。`Execute` 是边沿触发，再写一次需新的上升沿。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 **ADS 错误码**（不是 NC 错误号、也不是 HRESULT）。

| 错误来源 | 含义 | 处理建议 |
|---|---|---|
| ADS 通信错误 | 与驱动器的 ADS 传输失败（超时、设备不可达、AmsNetId 错误等） | 检查 EtherCAT 总线 OP、轴 Link、`Axis` 引用有效性 |
| 驱动器不支持 / 配置不一致 | 当前固件不支持，或 `Memory` 与 DriveManager 配置不一致 | 核对硬件型号与固件（AX5xxx ≥ FW v2.11 b0001；AX8xxx/AMP/MD8xxx ≥ v1.04 b0001；紧凑型 ≥ v01）；核对 DriveManager 偏置存放位置 |

⚠️ PDF 与 InfoSys 在本 FB 章节未逐条列出具体 ADS 错误码，请参见 Beckhoff ADS Return Codes 总表。

**清错**：处理完外部原因后给 `Execute` 新上升沿重试；本 FB 无独立清错入口。

## 5. 使用注意 / 常见坑

- **`Memory` 必须与 DriveManager 配置一致**：PDF 硬性要求，配置不一致写了等于没写或写错地方。
- **`Relative` 别弄反**：`FALSE` = 绝对（当前点设成 `Position`），`TRUE` = 相对（在当前位置上 ±增量）。回零设 0 用 `Relative = FALSE, Position = 0`。
- **没有 `Done` 输出**：判完成靠 `Busy` 落回 `FALSE` 且 `Error = FALSE`。
- **必须轴静止时写**：写偏置改变绝对位置参考，运动中写会导致位置跳变 / 跟随误差。
- **`Execute` 是边沿触发 + `Busy` 期间持续循环调用**：异步跨周期。
- **存编码器铭牌 vs 驱动器**：铭牌随电机走，换控制器保留；驱动器内存随驱动器留。换电机/换驱动器场景选错会丢偏置（工程经验补充）。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SetPositionOffset.xml`](../examples/P_Demo_FB_SetPositionOffset.xml)

```iecst
// 场景：手动回到机械参考点后，把当前点设为绝对零点（Position=0, Relative=FALSE）
rtSetTrig(CLK := bSetOffsetReq);
fbSetOffset(
    Execute  := rtSetTrig.Q,
    Position  := lrNewActualPosition,
    Relative  := FALSE,
    Feedback  := ePositionOffsetFeedback1,
    Memory    := ePositionOffsetMemory_Drive,
    Axis      := axisGantryX,
    Busy      => bSetBusy,
    Error     => bSetError,
    ErrorID   => nSetErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：回参考点后设零、机械改造后把实际位置对齐到工件坐标、更换电机/驱动器后重建位置基准。
- **价值**：偏置存在驱动器/编码器侧，PLC 重启不丢；不用每次上电重新找零。
- **替代方案对比**：
  - 在 PLC 里自己维护一个软件偏置变量：PLC 重启 / 工程下载就丢，每次上电要重设
  - `FB_SoEAX5000SetPositionOffset` / `FB_CoEAX8000SetPositionOffset` / `FB_CoEEL72xxSetPositionOffset`：型号专用，行为等价
  - **本 FB**：硬件无关，偏置常驻驱动器/编码器，跨型号通用

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.1.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/14430264587.html
- **相关 FB**：`FB_DeletePositionOffset`（删偏置）、`FB_SoEAX5000SetPositionOffset` / `FB_CoEAX8000SetPositionOffset` / `FB_CoEEL72xxSetPositionOffset`（型号专用）
