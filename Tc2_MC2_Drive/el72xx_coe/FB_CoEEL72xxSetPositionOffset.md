# FB_CoEEL72xxSetPositionOffset

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `EL72xx CoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/7604235915.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_CoEEL72xxSetPositionOffset.xml`](../examples/P_Demo_FB_CoEEL72xxSetPositionOffset.xml) |

---

## 1. 功能简述

把**位置偏置（position offset）**写入 **EL72xx**（伺服端子）内存的功能块（Function Block, FB）。功能与硬件无关的 `FB_SetPositionOffset` 等价，但本 FB 是 EL72xx 专用版本（走 EL72xx CoE 通道）。

`Position` 给定 NC 轴的新实际位置；`Relative = TRUE` 解释为相对增量、`= FALSE` 为绝对新位置。`Feedback` 选反馈系统，`Memory` 选偏置存放位置。⚠️ **EL72xx 当前不支持把偏置存进电机编码器的数字铭牌**（PDF 明确"currently not planned"）——因此实际存放位置应选驱动器内存。也可改用通用的 `FB_SetPositionOffset`，行为等价。

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
| `Execute` | `BOOL` | — | 上升沿触发一次写偏置；不需保持高电平 |
| `Position` | `LREAL` | — | NC 轴的新实际位置（轴用户单位）；`Relative = TRUE` 时按相对增量解释 |
| `Relative` | `BOOL` | — | 置位时把 `Position` 解释为相对当前位置的增量；复位时按绝对位置解释 |
| `Feedback` | `E_PositionOffsetFeedback` | — | 参考哪个反馈系统：`ePositionOffsetFeedback1`（= 0）/ `ePositionOffsetFeedback2`（= 1） |
| `Memory` | `E_PositionOffsetMemory` | — | 新偏置存到哪：`ePositionOffsetMemory_Drive`（= 1，驱动器内存，EL72xx 实际可用）/ `ePositionOffsetMemory_Encoder`（= 0，编码器铭牌，⚠️ EL72xx 当前不支持） |

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

**触发**：`Execute` 上升沿启动一次写偏置：FB 算出新偏置并写入 EL72xx `Memory` 指定的存储位置，`Busy := TRUE`，异步执行，**跨多个 PLC 周期**，必须每周期循环调用直到 `Busy` 落回 `FALSE`。

**`Relative` 语义**：`Relative = FALSE`（绝对）写入后轴实际位置直接变成 `Position`（如 `0` 即设零点）；`Relative = TRUE`（相对）在当前位置上叠加 `Position` 增量。

**完成与出错收敛**：本 FB 无 `Done` 输出。成功判据是 **`Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`**。出错则 `Busy` 复位后 `Error := TRUE`、`ErrorID` 给 ADS 错误码。

**EL72xx 存储限制（重要）**：EL72xx **当前不支持把偏置存进编码器数字铭牌**——`Memory` 应选 `ePositionOffsetMemory_Drive`（驱动器内存）。选 `_Encoder` 大概率会失败或不生效。写偏置改变绝对位置参考，应在轴静止时操作。`Execute` 是边沿触发，再写需新上升沿。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 **ADS 错误码**（不是 NC 错误号、也不是 HRESULT）。

| 错误来源 | 含义 | 处理建议 |
|---|---|---|
| ADS 通信错误 | 与 EL72xx 的 ADS 传输失败 | 检查 EtherCAT OP、`Axis` Link |
| 不支持 / 存储位置无效 | 选了 `_Encoder`（EL72xx 不支持）、固件不满足 | `Memory` 选 `_Drive`；核对 EL72xx 固件与库版本要求 |

⚠️ PDF 与 InfoSys 在本 FB 章节未逐条列出具体 ADS 错误码，请参见 Beckhoff ADS Return Codes 总表。

**清错**：处理完外部原因后给 `Execute` 新上升沿重试；本 FB 无独立清错入口。

## 5. 使用注意 / 常见坑

- **`Memory` 选 `_Drive`，不要选 `_Encoder`**：EL72xx 当前不支持存编码器铭牌（PDF 明确），选错会失败/不生效——这是 EL72xx 版本特有的坑。
- **`Relative` 别弄反**：`FALSE` = 绝对、`TRUE` = 相对；回零用 `Relative = FALSE, Position = 0`。
- **没有 `Done` 输出 + `Busy` 期间持续循环调用**：异步跨周期。
- **必须轴静止时写**：写偏置改变绝对位置参考。
- **只适用于 EL72xx**：本 FB 走 EL72xx CoE 通道；其它型号用 `FB_SetPositionOffset` 或对应型号 FB。
- **接口仅 Execute/Position/Relative/Feedback/Memory**：无 `NetId`/`Timeout`，写代码注意 pin 名。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CoEEL72xxSetPositionOffset.xml`](../examples/P_Demo_FB_CoEEL72xxSetPositionOffset.xml)

```iecst
// 场景：EL72xx 轴回机械参考点后把当前点设为绝对零点，偏置存驱动器内存
rtSetTrig(CLK := bSetOffsetReq);
fbEL72xxSetOffset(
    Execute  := rtSetTrig.Q,
    Position := lrNewActualPosition,
    Relative := FALSE,
    Feedback := ePositionOffsetFeedback1,
    Memory   := ePositionOffsetMemory_Drive,
    Axis     := axisServo,
    Busy     => bSetBusy,
    Error    => bSetError,
    ErrorID  => nSetErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：EL72xx 端子伺服轴回参考点后设零、机械改造后对齐工件坐标、重建位置基准。
- **价值**：偏置常驻 EL72xx 驱动器内存，PLC 重启不丢；EL72xx 专用接口直达。
- **替代方案对比**：
  - `FB_SetPositionOffset`（硬件无关）：更通用；本 FB 是 EL72xx 专用等价版本
  - PLC 里维护软件偏置：重启/下载就丢
  - **本 FB**：EL72xx 位置偏置写入的专用入口

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.6.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/7604235915.html
- **相关 FB**：`FB_SetPositionOffset`（硬件无关）、`FB_CoEEL72xxDeletePositionOffset`（删 EL72xx 偏置）
