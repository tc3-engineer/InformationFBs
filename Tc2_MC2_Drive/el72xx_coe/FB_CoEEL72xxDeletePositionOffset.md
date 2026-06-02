# FB_CoEEL72xxDeletePositionOffset

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `EL72xx CoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/7604208395.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_CoEEL72xxDeletePositionOffset.TcPOU`](../examples/P_Demo_FB_CoEEL72xxDeletePositionOffset.TcPOU) |

---

## 1. 功能简述

从 **EL72xx**（伺服端子）内存中删除**位置偏置（position offset）**的功能块（Function Block, FB）。与 `FB_CoEEL72xxSetPositionOffset` 对偶。功能与硬件无关的 `FB_DeletePositionOffset` 等价，但本 FB 是 EL72xx 专用版本（走 EL72xx CoE 通道）。

`Feedback` 选反馈系统，`Memory` 选从哪块内存删偏置。删偏置后轴的绝对位置参考改变，应在轴静止时操作。也可改用通用的 `FB_DeletePositionOffset`，行为等价。

> 注：PDF 在本 FB 的 VAR_INPUT 中同时列出 `Position`、`Relative`、`Feedback`、`Memory` 四个输入（与"设置"FB 同形），但功能为删除。下表逐字保留 PDF 列出的 VAR 区。

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
| `Execute` | `BOOL` | — | 上升沿触发一次删除；不需保持高电平 |
| `Position` | `LREAL` | — | NC 轴的位置显示（PDF 描述："New position of the NC axis is displayed"） |
| `Relative` | `BOOL` | — | 置位时把位置解释为相对 |
| `Feedback` | `E_PositionOffsetFeedback` | — | 指定考虑哪个反馈系统：`ePositionOffsetFeedback1`（= 0）/ `ePositionOffsetFeedback2`（= 1） |
| `Memory` | `E_PositionOffsetMemory` | — | 从哪块内存删偏置：`ePositionOffsetMemory_Drive`（= 1，驱动器内存）/ `ePositionOffsetMemory_Encoder`（= 0，编码器铭牌，⚠️ EL72xx 偏置通常不存这） |

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
| `Error` | `BOOL` | `Busy` 复位后若命令传输出错则置位 |
| `ErrorID` | `UDINT` | `Error = TRUE` 时返回 ADS 错误码 |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次删除：FB 向 EL72xx 发"删除位置偏置"命令，`Busy := TRUE`，异步执行，**跨多个 PLC 周期**，必须每周期循环调用直到 `Busy` 落回 `FALSE`。

**完成与出错收敛**：本 FB 无 `Done` 输出。成功判据是 **`Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`**，此后 `Memory` 中的偏置被清除。出错则 `Busy` 复位后 `Error := TRUE`、`ErrorID` 给 ADS 错误码。

**`Memory` 选择**：EL72xx 偏置通常存在驱动器内存（EL72xx 不支持编码器铭牌存储，见 `FB_CoEEL72xxSetPositionOffset`），删除时 `Memory` 选 `_Drive`。选错会"删了个空"。

**删偏置改变绝对位置参考**：删后轴 `ActPos` 含义改变，应在轴静止时操作，删完重新评估软限位/工件坐标。`Execute` 是边沿触发，再删需新上升沿。

⚠️ 本 FB VAR_INPUT 含 `Position`/`Relative` 字段，但功能为"删除"——PDF 对这两字段在删除场景下的具体作用未进一步说明，删除主要由 `Feedback`/`Memory` 决定。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 **ADS 错误码**（不是 NC 错误号、也不是 HRESULT）。

| 错误来源 | 含义 | 处理建议 |
|---|---|---|
| ADS 通信错误 | 与 EL72xx 的 ADS 传输失败 | 检查 EtherCAT OP、`Axis` Link |
| 不支持 / 内存位置无效 | 选了 EL72xx 不支持的存储位置、固件不满足 | `Memory` 选 `_Drive`；核对 EL72xx 固件与库版本要求 |

⚠️ PDF 与 InfoSys 在本 FB 章节未逐条列出具体 ADS 错误码，请参见 Beckhoff ADS Return Codes 总表。

**清错**：处理完外部原因后给 `Execute` 新上升沿重试；本 FB 无独立清错入口。

## 5. 使用注意 / 常见坑

- **`Memory` 选 `_Drive`**：EL72xx 偏置存在驱动器内存，删除选 `_Drive`；选 `_Encoder` 会删空。
- **没有 `Done` 输出 + `Busy` 期间持续循环调用**：异步跨周期。
- **删偏置改变绝对位置参考**：轴静止时删，删完重评软限位。
- **只适用于 EL72xx**：本 FB 走 EL72xx CoE 通道；其它型号用 `FB_DeletePositionOffset` 或对应型号 FB。
- **VAR 含 `Position`/`Relative` 但删除主要看 `Feedback`/`Memory`**：⚠️ PDF 未说明这两字段在删除时的作用，照常填即可。
- **删前确认偏置存放位置**：可结合调试记录确认（工程经验补充）。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CoEEL72xxDeletePositionOffset.TcPOU`](../examples/P_Demo_FB_CoEEL72xxDeletePositionOffset.TcPOU)

```iecst
// 场景：EL72xx 轴重新找正前，先删掉上次写进驱动器内存的位置偏置
rtDelTrig(CLK := bDeleteOffsetReq);
fbEL72xxDelOffset(
    Execute  := rtDelTrig.Q,
    Position := 0.0,
    Relative := FALSE,
    Feedback := ePositionOffsetFeedback1,
    Memory   := ePositionOffsetMemory_Drive,
    Axis     := axisServo,
    Busy     => bDelBusy,
    Error    => bDelError,
    ErrorID  => nDelErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：EL72xx 端子伺服轴维修后重新找正前清偏置、更换电机后清旧偏置、出厂前清调试期临时偏置。
- **价值**：偏置常驻 EL72xx 驱动器内存，要清理时 EL72xx 专用 FB 直达。
- **替代方案对比**：
  - `FB_DeletePositionOffset`（硬件无关）：更通用；本 FB 是 EL72xx 专用等价版本
  - DriveManager 手动删：人工、无法自动化
  - **本 FB**：EL72xx 位置偏置删除的专用入口

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.6.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/7604208395.html
- **相关 FB**：`FB_DeletePositionOffset`（硬件无关）、`FB_CoEEL72xxSetPositionOffset`（写 EL72xx 偏置）
