# FB_DeletePositionOffset

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `General Beckhoff` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2305793419.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DeletePositionOffset.TcPOU`](../examples/P_Demo_FB_DeletePositionOffset.TcPOU) |

---

## 1. 功能简述

删除存储在 Beckhoff 伺服硬件中**位置偏置（position offset）**的功能块（Function Block, FB）。位置偏置是工程调试时为了把"机械零点"和"编码器原点"对齐而写入驱动器/编码器铭牌的一个常驻偏移量；本 FB 把它清掉，让轴的位置回到无偏置状态。

本 FB 是**硬件无关的统一入口**：根据轴当前连接的是 AX5xxx、AX8xxx/AMP8xxx/MD8xxx 还是紧凑型驱动技术（servo），内部自动走对应的 SoE 或 CoE 通道，调用方不必关心底层总线协议。若需要绑定到具体硬件型号，也可改用 `FB_SoEAX5000DeletePositionOffset` / `FB_CoEAX8000DeletePositionOffset` / `FB_CoEEL72xxDeletePositionOffset`。

通过 `Feedback` 选哪个反馈系统（编码器 1 或 2），通过 `Memory` 选从编码器铭牌还是驱动器内存删除偏置。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute  : BOOL;
    Feedback : E_PositionOffsetFeedback;
    Memory   : E_PositionOffsetMemory;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次删除操作；不需保持高电平 |
| `Feedback` | `E_PositionOffsetFeedback` | — | 指定考虑哪个反馈系统：`ePositionOffsetFeedback1`（= 0，反馈系统 1）/ `ePositionOffsetFeedback2`（= 1，反馈系统 2） |
| `Memory` | `E_PositionOffsetMemory` | — | 指定从哪块内存删除偏置：`ePositionOffsetMemory_Encoder`（= 0，编码器铭牌）/ `ePositionOffsetMemory_Drive`（= 1，驱动器内存） |

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
| `Busy` | `BOOL` | FB 激活后置位，直到收到反馈（操作完成或出错）才复位 |
| `Error` | `BOOL` | `Busy` 复位后若传输命令时发生错误则置位 |
| `ErrorID` | `UDINT` | `Error = TRUE` 时返回 ADS 错误码（见 §4） |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次删除：FB 通过 ADS 向当前轴所连驱动器发出"删除位置偏置"命令，`Busy := TRUE`。命令是异步的——`Busy` 在等待驱动器/总线返回期间保持高电平，**跨多个 PLC 周期**，因此必须每周期循环调用本 FB 实例直到 `Busy` 变 `FALSE`。

**完成与出错收敛**：
- **成功**：驱动器确认删除 → `Busy := FALSE`、`Error := FALSE`，此后该 `Memory` 中的位置偏置被清除
- **出错**：ADS/驱动器通信失败、参数不被支持、内存位置无效等 → `Busy` 复位后 `Error := TRUE`、`ErrorID` 给出 ADS 错误码

注意本 FB 没有 `Done` 输出（与 `FB_ReadDriveInfo` 不同）；判断"成功完成"的方式是 **`Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`**。

**复位边沿**：标准用法是 `Busy = FALSE` 后把 `Execute` 拉回 `FALSE`（再置 `FALSE` 调用一次让 FB 复位内部状态），下次需要删除时再给一个新的上升沿。

**`Memory` 选择的影响**：选 `ePositionOffsetMemory_Encoder` 时删除的是写进编码器数字铭牌（digital nameplate）里的偏置——这块偏置随电机走，换控制器也保留；选 `ePositionOffsetMemory_Drive` 时删的是存在驱动器里的偏置。删除前要确认偏置当初是写在哪块内存，否则会"删错地方"导致偏置仍然生效。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 **ADS 错误码**（不是 NC 错误号、也不是 HRESULT）。

| 错误来源 | 含义 | 处理建议 |
|---|---|---|
| ADS 通信错误 | 与驱动器的 ADS 传输失败（超时、设备不可达、AmsNetId 错误等） | 检查 EtherCAT 总线 OP 状态、轴是否正确 Link、`Axis` 引用是否有效 |
| 驱动器不支持 / 参数无效 | 当前驱动器固件不支持该操作，或 `Memory` 指向不存在的内存位置 | 核对硬件型号与固件版本满足要求；确认偏置实际存放位置 |

⚠️ PDF 与 InfoSys 在本 FB 章节未逐条列出具体 ADS 错误码。ADS 错误码完整含义请参见 Beckhoff ADS Return Codes 总表（TwinCAT 系统手册）。

**清错**：本 FB 自身不带清错入口；通信类错误处理完外部原因后，给 `Execute` 新的上升沿重试即可。

## 5. 使用注意 / 常见坑

- **没有 `Done` 输出**：判完成靠 `Busy` 落回 `FALSE` 且 `Error = FALSE`，不要找 `Done`。
- **`Execute` 是边沿触发**：一直拉高不会反复删除，也不会"保持删除状态"；要再删一次必须制造新的上升沿。
- **`Busy` 期间必须持续循环调用**：异步操作跨周期，若某周期不调用本实例，状态机会卡住。
- **`Memory` 选错等于没删**：偏置写在编码器铭牌却选 `_Drive` 来删，会"删了个空"而真正的偏置还在生效，表现为"删除成功但位置没变"。
- **删除偏置会改变轴的绝对位置参考**：删后轴的 `ActPos` 含义改变，删除前后应停轴并重新评估软限位/工件坐标，避免删完直接运动撞极限（工程经验补充）。
- **硬件无关 vs 硬件专用**：本 FB 自动选通道；若你的工程明确只接 AX5000 / AX8000 / EL72xx，用对应 `FB_SoEAX5000...` / `FB_CoEAX8000...` / `FB_CoEEL72xx...` 也可，行为等价。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT，example 调用里必须把轴实参传进去。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DeletePositionOffset.TcPOU`](../examples/P_Demo_FB_DeletePositionOffset.TcPOU)

```iecst
// 场景：重新做机械找正前，先清掉上一次写进编码器铭牌的位置偏置
rtClearTrig(CLK := bClearOffsetReq);
fbDeleteOffset(
    Execute  := rtClearTrig.Q,
    Feedback := ePositionOffsetFeedback1,
    Memory   := ePositionOffsetMemory_Encoder,
    Axis     := axisRotaryTable,
    Busy     => bClearBusy,
    Error    => bClearError,
    ErrorID  => nClearErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：机械维修后重新做轴找正、更换编码器/电机后清理旧偏置、把调试期写入的临时偏置在出厂前清空。
- **价值**：偏置存在驱动器/编码器侧而非 PLC，PLC 重启或工程下载不会丢；要清理时一个统一 FB 即可，无需手动进 DriveManager 逐台操作。
- **替代方案对比**：
  - 在 DriveManager 里手动删：人工、易漏、无法在程序里自动化
  - 用 `FB_SoEAX5000DeletePositionOffset` / `FB_CoEAX8000DeletePositionOffset` / `FB_CoEEL72xxDeletePositionOffset`：绑定具体硬件型号，行为等价但代码与硬件耦合
  - **本 FB**：硬件无关，自动选 SoE/CoE 通道，跨型号通用

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.1.2
- **InfoSys topic**：本 FB 无独立 topic 页（仅检索到硬件专用变体），见库根 https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2305793419.html（⚠️ not-on-infosys）
- **相关 FB**：`FB_SetPositionOffset`（写偏置）、`FB_SoEAX5000DeletePositionOffset` / `FB_CoEAX8000DeletePositionOffset` / `FB_CoEEL72xxDeletePositionOffset`（硬件专用版本）
