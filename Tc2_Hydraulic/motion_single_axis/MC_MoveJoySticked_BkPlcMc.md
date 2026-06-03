# MC_MoveJoySticked_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion - Single axis` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599702795.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_MoveJoySticked_BkPlcMc.TcPOU`](../examples/P_Demo_MC_MoveJoySticked_BkPlcMc.TcPOU) |

---

## 1. 功能简述

非 PLCopen 标准的**摇杆式运动**功能块。`Execute` 维持高电平期间，根据 `JoyStick`（归一化到 ±1.0）持续控制轴的速度——速度 = `JoyStick × fRefVelo`。摇杆值平滑变化对应速度连续变化，是"恒速运动 + 实时调速"的组合。**前置要求**：轴的 `nProfileType` 必须配置为 `MC_AxRuntimeCtrlBased_BkPlcMc`（或未来 `MC_AxRunTimeTimeRamp_BkPlcMc`），其他生成器不支持本 FB。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute:        BOOL;
    JoyStick:       LREAL;
    Acceleration:   LREAL;
    Deceleration:   LREAL;
    Jerk:           LREAL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿启动摇杆模式；维持高电平期间持续响应 `JoyStick` 调速；下降沿减速停车 |
| `JoyStick` | `LREAL` | — | 归一化速度命令，范围 ±1.0（实际速度 = `JoyStick × fRefVelo`） |
| `Acceleration` | `LREAL` | — | 加速度，单位 mm/s²（限制 JoyStick 变化引起的加速） |
| `Deceleration` | `LREAL` | — | 减速度，单位 mm/s² |
| `Jerk` | `LREAL` | — | 保留字段，单位 mm/s³ |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis:           AXIS_REF_BkPlcMc;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF_BkPlcMc` | 轴接口结构。必须以 `VAR_IN_OUT` 方式传引用 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Busy:           BOOL;
    CommandAborted: BOOL;
    Error:          BOOL;
    ErrorID:        UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | 命令处理中 |
| `CommandAborted` | `BOOL` | 被另一 FB 打断 |
| `Error` | `BOOL` | 启动检查或运动算法报错 |
| `ErrorID` | `UDINT` | 错误码 |

**注意**：本 FB **没有 Done 字段**——摇杆模式没有"完成"概念，撤 `Execute` 时减速停车不报 Done。

## 3. 行为说明

**调用模式**：电平触发。`Execute` 维持高电平期间持续响应 `JoyStick` 变化。

**启动检查**：
1. 轴在错误/停车中 → `Error`、`ErrorID := dwTcHydErrCdNotReady`
2. 算法已持错码 → `Error` + 算法错码
3. **生成器不支持**：当前 `nProfileType` 不是 `MC_AxRuntimeCtrlBased_BkPlcMc` → `Error`、`ErrorID := dwTcHydErrCdNotCompatible`

**运动控制**：检查通过后算法切到 `iTcHydStateExtGenerated`、轴进入 `McState_Synchronizedmotion`。速度 = `JoyStick × ST_TcHydAxParam.fRefVelo`。`JoyStick` 变化引起的速度变化按 `ST_TcHydAxParam.fMaxAcc` 做斜坡限制。

**软限位行为**：当轴靠近激活的软限位时，FB 根据剩余距离限制速度（让轴正好停在限位上），避免冲过。

**撤 Execute 行为**：`Execute` 下降沿把算法置入 `iTcHydStateTcDecP` 或 `iTcHydStateTcDecM`（带方向的减速态），轴回 `McState_Standstill`。运动中撤 `Execute` 会用停车斜坡平滑减速到 0；之后算法回到 `iTcHydStateIdle`。

**典型用法**：
- 操作员手持摇杆控制液压轴：摇杆推到 +1.0 全速正向，回中 0 停车，推到 -1.0 全速反向
- HMI 上的"加速/减速"双向滑块
- 调试模式下的连续可变速度测试

**典型陷阱**：
- 错误的 `nProfileType`：返回 NotCompatible 错；先在轴参数里配 `MC_AxRuntimeCtrlBased`
- `JoyStick` 抖动：摇杆电位计模拟量本身抖，建议先低通滤波再喂给本 FB；否则 fMaxAcc 限速频繁触发可能不平滑
- 期望 Done：本 FB 没有 Done；撤 `Execute` 后看 `MC_ReadStatus_BkPlcMc.StandStill` 判停

## 4. 错误码 / 返回值

| `ErrorID` 常量 | 含义 | 处理建议 |
|---|---|---|
| `dwTcHydErrCdNotReady` | 轴在错误/停车中 | `MC_Reset_BkPlcMc` |
| `dwTcHydErrCdNotCompatible` | `nProfileType` 不支持 | 改用 `MC_AxRuntimeCtrlBased_BkPlcMc` |
| (算法错码) | 算法报错 | 查 PDF §5.2 |

## 5. 使用注意 / 常见坑

- **生成器类型必须对**：本 FB 只支持 `MC_AxRuntimeCtrlBased_BkPlcMc`；其它生成器调本 FB 直接报 NotCompatible。
- **无 Done 字段**：撤 `Execute` 后看 StandStill 判停。
- **`JoyStick` 是 ±1.0**：超出范围会被内部 saturate；HMI 端要在 0-100% 显示时做映射。
- **`fMaxAcc` 限速**：摇杆突变不会"瞬时变速"，按 `fMaxAcc` 平滑过渡。
- **不是 PLCopen 标准**：跨平台代码需自封装。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_MoveJoySticked_BkPlcMc.TcPOU`](../examples/P_Demo_MC_MoveJoySticked_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：液压挖掘机臂操作员摇杆。摇杆推到 +1 时挖斗以最高速度抬升，回中 0 停止，推 -0.3 慢速反向（精细动作）。本 FB 直接把摇杆模拟量翻译成轴速度。
- **价值**：手写需要切换算法状态、做加减速限幅、处理软限位接近；本 FB 一行调用全包。
- **替代方案对比**：
  - `MC_MoveVelocity_BkPlcMc`：恒速无法实时调
  - `MC_MoveJog_BkPlcMc`：寸动模式，固定速度无摇杆调
  - **本 FB**：摇杆 / 旋钮 / 操纵杆类输入设备最直接

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.2.14
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599702795.html
- **相关 FB**：`MC_MoveVelocity_BkPlcMc`（恒速）、`MC_MoveJog_BkPlcMc`（寸动）、`MC_AxRuntimeCtrlBased_BkPlcMc`（必需的轴 runtime）
