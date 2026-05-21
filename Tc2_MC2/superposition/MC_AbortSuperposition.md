# MC_AbortSuperposition

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Superposition` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70114571.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_AbortSuperposition.xml`](../examples/P_Demo_MC_AbortSuperposition.xml) |

---


## 1. 功能简述

PLCopen 标准定义的**叠加运动中止 FB**。提前结束由 `MC_MoveSuperImposed` 启动的叠加运动，**但不停止主运动**。叠加运动被中止后，已叠加的部分保留（位置差保留），剩余未完成的叠加被抛弃。

如果需要"主运动 + 叠加运动全停"应直接用 `MC_Stop` / `MC_Halt`，无需先调 `MC_AbortSuperposition`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发：立刻终止当前叠加运动，主运动继续 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | 轴数据结构，唯一标识系统中一根轴；含位置、速度、错误状态等全部循环数据。**必须传引用**（VAR_IN_OUT 语义） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done    : BOOL;
    Busy    : BOOL;
    Error   : BOOL;
    ErrorID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 叠加运动已成功中止时置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 上升沿后立即 `TRUE`，FB 完成后 `FALSE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4） |

## 3. 行为说明

**触发**：`Execute` 上升沿。立刻终止该轴上正在执行的 `MC_MoveSuperImposed` 叠加运动；主运动 FB 继续监视主运动，不受影响。

**已叠加位移保留**：例如叠加运动准备走 10 mm，已走完 6 mm 时被本 FB 中止，**6 mm 的位置差被保留**，未走的 4 mm 不再补。

**没有 `CommandAborted`、`Active` 等输出**：因为本 FB 自身是个"中止动作"，瞬时完成，没有"可被打断"的概念。

**典型用法**：业务在叠加运动启动后发现条件变了（例如套准检测发现叠加方向算错了），想立即终止叠加但不影响生产线主运动。

**已无叠加运动时调用**：若轴上当前并无叠加运动，本 FB 报错 `Error := TRUE`、`ErrorID` 给"无叠加可中止"码。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- **`MC_AbortSuperposition` 只中止叠加，不停主轴**：要全停应用 `MC_Stop` / `MC_Halt`。
- **没有叠加运行时调用会报错**：先确认 `MC_MoveSuperImposed` 实例的 `Busy = TRUE` 再触发本 FB。
- **不能"撤销"已叠加的位移**：本 FB 只是停止后续未完成的叠加段，已经叠加进去的位置差**永久保留**。要把"叠加的位置差减回去"得反向再发一次 `MC_MoveSuperImposed`。
- **不要把它当"叠加运动的 Reset"**：与 `MC_Reset` 无关，本 FB 不清错。
- **耦合从轴上的叠加**：从轴叠加被中止后从轴回到"按耦合公式跟主轴走"的状态。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_AbortSuperposition.xml`](../examples/P_Demo_MC_AbortSuperposition.xml)

```iecst
// 场景：套色检测系统在叠加运动启动后发现方向算错，立刻终止叠加避免错色印更多
PROGRAM P_Demo_MC_AbortSuperposition
VAR
    fbAbortShift       : MC_AbortSuperposition;
    axisPrintRoller    : AXIS_REF;
    rtAbortTrig        : R_TRIG;
    bRequestAbort      : BOOL;
    bAbortDone         : BOOL;
    bAbortBusy         : BOOL;
    bAbortError        : BOOL;
    nErrorID           : UDINT;
END_VAR

rtAbortTrig(CLK := bRequestAbort);
fbAbortShift(
    Execute  := rtAbortTrig.Q,
    Axis     := axisPrintRoller,
    Done     => bAbortDone,
    Busy     => bAbortBusy,
    Error    => bAbortError,
    ErrorID  => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：叠加运动启动后业务发现参数错了 / 检测信号变了 / 操作员按急停辅助键。需要"叠加段提前结束，但生产线主运动不能停"。
- **价值**：用一个 FB 精准中止叠加，不波及主运动。比"停掉所有运动再重新发主运动命令"的开销低几个数量级。
- **替代方案对比**：
  - 用 `MC_Stop`：把主运动也停了，生产线必停
  - 让叠加自己跑完：等待时间不可控，可能继续印更多废品
  - **本 FB**：精准中止叠加 + 主运动续行

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.2.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70114571.html
- **相关 FB**：`MC_MoveSuperImposed`（启动叠加）、`MC_Stop`、`MC_Halt`
