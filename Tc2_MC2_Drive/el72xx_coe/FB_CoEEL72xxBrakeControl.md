# FB_CoEEL72xxBrakeControl

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `EL72xx CoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/14430113419.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_CoEEL72xxBrakeControl.xml`](../examples/P_Demo_FB_CoEEL72xxBrakeControl.xml) |

---

## 1. 功能简述

手动控制 **EL72xx**（伺服端子）上电机抱闸的功能块（Function Block, FB）。功能与硬件无关的 `FB_BrakeControl` 等价，但本 FB 是 EL72xx 专用版本（走 EL72xx CoE 通道）。

通过 `Mode`（`E_BrakeMode`）选择：`eBrakeMode_Automatic`（恢复使能自动联动）、`eBrakeMode_Lock`（永久抱死）、`eBrakeMode_Unlock`（永久松开）。抱闸通过 "Lock"/"Unlock" 永久闭合/打开；官方建议手动开/闭只在必要时段短暂使用，用完切回 `eBrakeMode_Automatic`。也可改用通用的 `FB_BrakeControl`，行为等价。

⚠️ **安全**：手动松闸时垂直轴可能下坠，须有防坠措施。EL72xx 抱闸控制要求 EL72xx 带 OCT 且固件 ≥ v16。

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
| `Mode` | `E_BrakeMode` | — | 抱闸控制模式：`eBrakeMode_Automatic`（自动开闭）/ `eBrakeMode_Lock`（永久抱死）/ `eBrakeMode_Unlock`（永久松开，⚠️ 垂直轴下坠风险） |

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

**触发**：`Execute` 上升沿启动一次抱闸模式切换：FB 通过 EL72xx CoE 把 `Mode` 写到端子，`Busy := TRUE`，异步执行，**跨多个 PLC 周期**，必须每周期循环调用直到 `Busy` 落回 `FALSE`。

**模式语义**：
- `eBrakeMode_Lock`：抱闸**永久闭合**，`MC_Power` 使能也不松，轴被机械锁住无法运动
- `eBrakeMode_Unlock`：抱闸**永久松开**，`MC_Power` 失能也不抱，垂直轴失去机械保持 ⚠️ 有下坠风险
- `eBrakeMode_Automatic`：恢复使能联动自动控制（默认且安全状态）

**完成与出错收敛**：本 FB 无 `Done` 输出。成功判据是 **`Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`**；出错则 `Busy` 复位后 `Error := TRUE`、`ErrorID` 给 ADS 错误码。

**典型用法时序**：手动开闸装夹工件 → 操作完成 → 立刻发 `eBrakeMode_Automatic` 还原。绝不要把轴长期停在 `Lock`/`Unlock`，否则使能逻辑与抱闸状态脱节。`Execute` 是边沿触发，切模式需新上升沿。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 **ADS 错误码**（不是 NC 错误号、也不是 HRESULT）。

| 错误来源 | 含义 | 处理建议 |
|---|---|---|
| ADS 通信错误 | 与 EL72xx 的 ADS 传输失败 | 检查 EtherCAT OP、`Axis` Link |
| 不支持抱闸控制 | EL72xx 非 OCT 型、固件不满足 | 核对 EL72xx 带 OCT 且固件 ≥ v16、TwinCAT ≥ 4024.48、库 ≥ V3.3.34.0 |

⚠️ PDF 与 InfoSys 在本 FB 章节未逐条列出具体 ADS 错误码，请参见 Beckhoff ADS Return Codes 总表。

**清错**：处理完外部原因后给 `Execute` 新上升沿重试；本 FB 无独立清错入口。

## 5. 使用注意 / 常见坑

- **用完必须切回 `eBrakeMode_Automatic`**：停在 `Lock`/`Unlock` 会让抱闸与使能逻辑脱节。
- **`eBrakeMode_Unlock` 对垂直轴高危**：松开后失能不抱闸，重力轴下坠，操作前要机械支撑。
- **`eBrakeMode_Lock` 下 `MC_Power` 使能不松闸**：会出现"使能成功但一动报跟随误差"。
- **没有 `Done` 输出 + `Busy` 期间持续循环调用**：异步跨周期。
- **只适用于带 OCT 的 EL72xx**：本 FB 走 EL72xx CoE 通道，非 OCT 型不支持；其它型号用 `FB_BrakeControl`。
- **接口仅 Execute/Mode**：无 `NetId`/`Timeout`，写代码注意 pin 名。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CoEEL72xxBrakeControl.xml`](../examples/P_Demo_FB_CoEEL72xxBrakeControl.xml)

```iecst
// 场景：EL72xx 驱动的轴手动松闸做机械对位，用完切回自动
rtBrakeTrig(CLK := bBrakeCmdReq);
fbEL72xxBrake(
    Execute := rtBrakeTrig.Q,
    Mode    := eRequestedBrakeMode,
    Axis    := axisLiftAxis,
    Busy    => bBrakeBusy,
    Error   => bBrakeError,
    ErrorID => nBrakeErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：EL72xx 端子伺服上维修盘动电机做机械对位、抱闸保养检测、装夹工件临时锁轴；用完一律切回自动。
- **价值**：EL72xx 专用抱闸手动控制入口，不必查 EL72xx CoE 抱闸对象，三态枚举即可接管。
- **替代方案对比**：
  - `FB_BrakeControl`（硬件无关）：更通用；本 FB 是 EL72xx 专用等价版本
  - 直接写 EL72xx CoE 抱闸对象：要查对象号，繁琐
  - **本 FB**：EL72xx 抱闸手动控制的专用入口

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.6.1，枚举 §5.5 `E_BrakeMode`
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/14430113419.html
- **相关 FB**：`FB_BrakeControl`（硬件无关）、`FB_CoEAX8000BrakeControl`（AX8000 专用）、`MC_Power`（使能联动抱闸）
