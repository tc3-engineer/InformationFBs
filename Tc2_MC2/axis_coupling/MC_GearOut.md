# MC_GearOut

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Axis coupling` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70126475.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_GearOut.xml`](../examples/P_Demo_MC_GearOut.xml) |

---


## 1. 功能简述

PLCopen 标准定义的**电子齿轮解耦 FB**。把由 `MC_GearIn` / `MC_GearInDyn` / `MC_GearInMultiMaster` / `MC_CamIn` 建立的主从耦合**解开**。

⚠️ **解耦不停轴**：从轴解耦后**仍保持当前速度无限走**，与主轴无关。PDF 明确以 `DANGER` / `WARNING` 标识此风险。必须显式接 `MC_Halt` / `MC_Stop` 才能停从轴。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute : BOOL;
    Options : ST_GearOutOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次定位命令；命令进入运动队列后即开始执行，不需保持高电平 |
| `Options` | `ST_GearOutOptions` | — | 解耦选项（保留扩展） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Slave : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Slave` | `AXIS_REF` | 要解耦的从轴；解耦后该轴从耦合状态变成"已解耦但仍在走"状态 |

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
| `Done` | `BOOL` | 解耦完成置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 上升沿后立即 `TRUE`，FB 完成后 `FALSE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4） |

## 3. 行为说明

**触发**：`Execute` 上升沿启动解耦。瞬时完成，`Done` 短暂置 TRUE。

**Setpoint generator type 影响**：PDF 明确指出，若轴设定值发生器类型为 "7 phases (optimized)"（TwinCAT 2.11 起的默认），从轴解耦后进入**无加速度状态**并以解耦瞬间的恒速继续走，行为等同于 `MC_MoveVelocity` 启动后的"放手"状态。TwinCAT 2.10 用户可自选发生器类型，但 2.11+ 已固定。

**`MC_GearInDyn` 持续耦合时**：若 `MC_GearInDyn` 的 `Enable` 仍为 TRUE 状态下调用本 FB，从轴**短暂解耦后立即重新耦合**（因为 `MC_GearInDyn` 持续要求耦合）。要彻底解耦顺序：`Enable := FALSE` → `MC_GearOut(Slave)`。

**与 `MC_GearInMultiMaster` 互动相同**：见上一条。

**典型用法**：
1. 工艺段结束需要从轴单独继续走或停下时，先 `MC_GearOut` 再 `MC_Halt`
2. 模式切换：从"耦合跟随"切换到"独立定位"

⚠️ **解耦后必须管住从轴**：永远不要单独发 `MC_GearOut` 不接停车命令。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- ⚠️ **解耦后从轴不停**：是本 FB 最大的"坑"。必须显式 `MC_Halt(Slave)` 或 `MC_Stop(Slave)`。
- **`MC_GearInDyn` 持续 Enable = TRUE 时解不掉**：见 §3。顺序必须先关 Enable 再 GearOut。
- **解耦速度等于解耦瞬间从轴速度**：不是主轴速度 × 齿比，而是从轴实际速度（受加速度限制可能略小于理论值）。
- **没耦合状态调用会出错**：`MC_GearOut` 期望轴当前在耦合中，否则 `Error := TRUE`。
- **解耦后再耦合需重新调 `MC_GearIn`**：解耦不是"暂停"，是终止耦合关系。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_GearOut.xml`](../examples/P_Demo_MC_GearOut.xml)

```iecst
// 场景：工艺段结束 — 从轴脱开主轴跟随，然后立刻平稳停车避免冲极限
PROGRAM P_Demo_MC_GearOut
VAR
    fbDecouple        : MC_GearOut;
    fbHaltSlave       : MC_Halt;
    axisSlave         : AXIS_REF;
    rtDecoupleTrig    : R_TRIG;
    bRequestDecouple  : BOOL;
    bDecoupleDone     : BOOL;
    bSlaveStopDone    : BOOL;
    nErrorID          : UDINT;
END_VAR

rtDecoupleTrig(CLK := bRequestDecouple);
fbDecouple(
    Execute := rtDecoupleTrig.Q,
    Slave   := axisSlave,
    Done    => bDecoupleDone,
    ErrorID => nErrorID
);

// 解耦完成立刻发停车命令 — 否则从轴会无限走
fbHaltSlave(
    Execute      := bDecoupleDone,
    Deceleration := 2000.0,
    Jerk         := 20000.0,
    Axis         := axisSlave,
    Done         => bSlaveStopDone
);
```

## 7. 业务场景与实际价值

- **场景**：耦合工艺段完成后切换到独立运动、故障检测要求"脱开主轴单独停"、多工艺模式切换。
- **价值**：把"解耦"动作标准化为单次 FB 调用；不必直接操作 NC 通道控制字。
- **替代方案对比**：
  - 自己写 NC 命令解耦：要拼 `MC_DECOUPLE` 控制字，10+ 行
  - 用 `MC_Stop(Slave)`：停轴但**不解耦**，主轴动从轴仍试图跟，会跟错位
  - **本 FB + `MC_Halt`**：解耦 + 停车的标准两步法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.5.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70126475.html
- **相关 FB**：`MC_GearIn`、`MC_GearInDyn`、`MC_GearInMultiMaster`、`MC_Halt`、`MC_Stop`
