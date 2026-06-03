# MC_GearIn_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion - Multiple axis` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599695627.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_GearIn_BkPlcMc.TcPOU`](../examples/P_Demo_MC_GearIn_BkPlcMc.TcPOU) |

---

## 1. 功能简述

PLCopen 风格**电子齿轮耦合**功能块。`Execute` 上升沿启动两轴耦合：从轴速度 = 主轴速度 × (`RatioNumerator` / `RatioDenominator`)。**当前实现限制**：主从必须都在静止时才能启动耦合（不支持飞行同步）。`InGear` 表示首次同步成功——一旦置 TRUE 后即使后续短暂跟不上也不清。要解耦用 `MC_GearOut_BkPlcMc`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute:                BOOL;
    RatioNumerator:         INT;
    RatioDenominator:       INT;
    Acceleration:           LREAL;
    Deceleration:           LREAL;
    Jerk:                   LREAL;  //from V3.0.5
    BufferMode:             MC_BufferMode_BkPlcMc:=Aborting_BkPlcMc;    //from V3.0.8
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿启动耦合 |
| `RatioNumerator` | `INT` | — | 齿比分子（无量纲） |
| `RatioDenominator` | `INT` | — | 齿比分母（无量纲）。`= 0` 报 `dwTcHydErrCdIllegalGearFactor` |
| `Acceleration` | `LREAL` | — | 同步过程允许的加速度，单位 mm/s² |
| `Deceleration` | `LREAL` | — | 同步过程允许的减速度，单位 mm/s² |
| `Jerk` | `LREAL` | — | jerk，单位 mm/s³（自 V3.0.5 起加入） |
| `BufferMode` | `MC_BufferMode_BkPlcMc` | `Aborting_BkPlcMc` | 保留（自 V3.0.8 起加入） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Master:         AXIS_REF_BkPlcMc;
    Slave:          AXIS_REF_BkPlcMc;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Master` | `AXIS_REF_BkPlcMc` | 主轴接口结构 |
| `Slave` | `AXIS_REF_BkPlcMc` | 从轴接口结构 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Busy:           BOOL;
    InGear:         BOOL;
    CommandAborted: BOOL;
    Error:          BOOL;
    ErrorID:        UDINT;
    Active:         BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | 命令处理中 |
| `InGear` | `BOOL` | 首次同步成功标志（latched）；置 TRUE 后即使后续跟不上也不清 |
| `CommandAborted` | `BOOL` | 耦合被打断 |
| `Error` | `BOOL` | 启动检查或运行中错 |
| `ErrorID` | `UDINT` | 错误码 |
| `Active` | `BOOL` | 命令活动中 |

## 3. 行为说明

**调用模式**：边沿触发。`Execute` 上升沿启动耦合；下降沿清输出但耦合不解除（要解除调 `MC_GearOut_BkPlcMc`）。

**启动检查**：
1. `RatioDenominator = 0` → `Error`、`ErrorID := dwTcHydErrCdIllegalGearFactor`
2. **主或从不静止** → `Error`、`ErrorID := dwTcHydErrCdNotStartable`（**当前实现限制**：飞行同步未支持）
3. 轴在错误/停车中 → `Error`、`ErrorID := dwTcHydErrCdNotReady`
4. 算法已持错码 → `Error` + 算法错码

**耦合启动**：检查通过后从轴进入 `McState_Synchronizedmotion`，FB 监视耦合。因为只能在静止时启动，所以同步立即完成，`InGear := TRUE` 立刻置位。

**`InGear` 是 latched**：第一次到达耦合所需速度时置 TRUE 并保持。即使后续从轴因压力波动 / 跟随误差短暂跟不上主轴，`InGear` 也不清。

**典型用法**：
- 包装机主滚筒带料带，从轴推送轴以 2 倍速度同步推袋（齿比 2:1）
- 双 Y 轴龙门：两个液压轴必须保持 1:1 速度同步
- 多缸液压同步：一主多从

**典型陷阱**：
- 主或从在运动中触发：失败；先 Halt 都停了再触发
- `RatioDenominator = 0`：明确报错
- 期望解耦后从轴自动停：错；GearOut 解耦后从轴保持当前速度做 ContinuousMotion，必须额外 `MC_Halt_BkPlcMc` / `MC_Stop_BkPlcMc` 才停
- `InGear` 的 latched 语义误用：作为"实时同步状态"判断会失误，要看实时跟随用 `Master.Position - Slave.Position * Den / Num` 自己算

## 4. 错误码 / 返回值

| `ErrorID` 常量 | 含义 | 处理建议 |
|---|---|---|
| `dwTcHydErrCdIllegalGearFactor` | `RatioDenominator = 0` | 检查齿比参数 |
| `dwTcHydErrCdNotStartable` | 主或从不静止 | 先把两轴都停下 |
| `dwTcHydErrCdNotReady` | 轴在错误/停车中 | Reset |
| (算法错码) | 运行中算法错 | 查 PDF §5.2 |

## 5. 使用注意 / 常见坑

- **仅静止启动**：当前版本飞行同步未实现；主或从在动就报 NotStartable。
- **`InGear` 是 latched**：实时同步状态需自己算。
- **解耦不停轴**：`MC_GearOut_BkPlcMc` 把耦合转成 ContinuousMotion（保持当前速度），从轴会继续走；必须接 Halt/Stop 才停。
- **同步参数对动力学限制**：Acceleration/Deceleration 限制从轴跟随主轴变化时的最大加减速。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_GearIn_BkPlcMc.TcPOU`](../examples/P_Demo_MC_GearIn_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：包装机主滚筒带动料带前行，推送轴必须以主滚筒 2 倍速度同步把袋子推出（齿比 2:1）。建立耦合后 PLC 不用周期性发推送命令，主滚筒动从轴自动跟。
- **价值**：手写需要在每周期算 `slave_pos := master_pos × ratio` 并发位置命令，对实时性要求极高；本 FB 在算法层做耦合，业务侧只需启停。
- **替代方案对比**：
  - 自己周期性计算并发位置命令：实时性差，PLC 抖动会引入跟随误差
  - `MC_CamIn_BkPlcMc`：凸轮表耦合，齿比非线性
  - **本 FB**：线性恒齿比耦合最直接

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.2.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599695627.html
- **相关 FB**：`MC_GearInPos_BkPlcMc`（飞行同步耦合）、`MC_GearOut_BkPlcMc`（解耦）、`MC_CamIn_BkPlcMc`（凸轮表耦合）
