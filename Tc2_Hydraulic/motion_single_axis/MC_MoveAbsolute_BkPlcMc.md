# MC_MoveAbsolute_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion - Single axis` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599701771.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_MoveAbsolute_BkPlcMc.TcPOU`](../examples/P_Demo_MC_MoveAbsolute_BkPlcMc.TcPOU) |

---

## 1. 功能简述

PLCopen Motion Control 标准定义的**绝对定位运动**功能块（液压库实现）。`Execute` 上升沿启动一次到达 `Position` 绝对坐标的定位；速度由 `Velocity` 给出，加减速由 `Acceleration` / `Deceleration`（0 → 用轴参数默认）给出。在轨迹生成的同时监视轴的运动状态：到达目标 → `Done`；被另一命令打断 → `CommandAborted`；参数/状态错 → `Error` + `ErrorID`。`Jerk` 当前为保留字段（液压库目前不实现 jerk-limited）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute:        BOOL;
    Position:       LREAL;
    Velocity:       LREAL;
    Acceleration:   LREAL;
    Deceleration:   LREAL;
    Jerk:           LREAL;
    Direction:      MC_Direction_BkPlcMc:=MC_Shortest_Way_BkPlcMc;   //from V3.0.8
    BufferMode:     MC_BufferMode_BkPlcMc:=Aborting_BkPlcMc;        //from V3.0.8
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次定位命令 |
| `Position` | `LREAL` | — | 绝对目标位置，单位 mm（轴 fScale 工程单位） |
| `Velocity` | `LREAL` | — | 行进速度，单位 mm/s。要求 > 1% 参考速度，否则报 `dwTcHydErrCdSetVelo` |
| `Acceleration` | `LREAL` | — | 加速度，单位 mm/s²。给 0 用轴参数默认；过小（100 s 内达不到 Velocity）报 `dwTcHydErrCdAcc` |
| `Deceleration` | `LREAL` | — | 减速度，单位 mm/s²。给 0 用默认；过小同上 |
| `Jerk` | `LREAL` | — | 保留字段（液压库目前不实现 jerk-limited 控制），单位 mm/s³ |
| `Direction` | `MC_Direction_BkPlcMc` | `MC_Shortest_Way_BkPlcMc` | 保留，仅为兼容性。要么不赋值，要么传 `MC_Shortest_Way_BkPlcMc`（自 V3.0.8 起加入） |
| `BufferMode` | `MC_BufferMode_BkPlcMc` | `Aborting_BkPlcMc` | 保留，当前仅允许 `Aborting_BkPlcMc`（自 V3.0.8 起加入） |

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
    Done:           BOOL;
    CommandAborted: BOOL;
    Error:          BOOL;
    ErrorID:        UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | 命令处理中（运动还未结束/未出错/未被打断） |
| `Done` | `BOOL` | 成功到达 `Position` |
| `CommandAborted` | `BOOL` | 被另一运动 FB 打断（如 MC_Stop / MC_Halt / 另一 Move） |
| `Error` | `BOOL` | 启动检查失败或运动中算法报错 |
| `ErrorID` | `UDINT` | 编码错误号，常见值见 §4 |

## 3. 行为说明

**调用模式**：边沿触发。`Execute` 上升沿启动；下降沿清所有输出（但已启动的运动不停）。

**启动检查（按 PDF 列出顺序）**：
1. **软限位检查**：`Position` 越过激活的软限位 → `Error`、`ErrorID := dwTcHydErrCdSoftEnd`
2. **运动算法可启动性**：根据 `pStAxParams^.nProfile` 选择的运动算法，某些算法要求轴必须静止才能接受新命令，某些允许在运动中接收。如果当前不能接受 → `Error`、`ErrorID := dwTcHydErrCdNotStartable`
3. **轴状态检查**：轴在错误状态 / 停车进行中 → `Error`、`ErrorID := dwTcHydErrCdNotReady`
4. **速度合法性**：`Velocity` < 1% 参考速度 → `Error`、`ErrorID := dwTcHydErrCdSetVelo`
5. **加速度合法性**：`Acceleration` 太小（100 s 内达不到 Velocity）→ `Error`、`ErrorID := dwTcHydErrCdAcc`
6. **减速度合法性**：同上，`Deceleration` 太小 → `Error`、`ErrorID := dwTcHydErrCdAcc`
7. **算法错误码**：运动算法已经持有错误码 → `Error`、`ErrorID := 该算法错码`

**运动监视**：通过启动检查后，FB 把参数限到允许最大值传给运动算法，轴进入 `McState_DiscreteMotion`；FB 每周期监视轨迹。算法报错 → `Error` + 算法错码；被打断 → `CommandAborted`；到达目标 → `Done`。

**`Execute` 下降沿语义**：清所有输出，但**不停轴**。要停轴用 `MC_Stop_BkPlcMc`。若运动已在进行，下降沿不打断，最终的 Done/Error/CommandAborted 信号会在到达终态时保留一个周期供业务侧捕获。

**典型用法**：贴片机贴装头到 PCB 上某个绝对坐标；注塑机锁模到 350 mm；冲压设备压头到下死点上方 5 mm 待命位。

**典型陷阱**：
- 同一 FB 实例连续触发两次 `Execute`：第二次会被算法判 `dwTcHydErrCdNotStartable`（看算法策略），可能要等第一次 Done 后才能触发
- `Velocity = 0`：触发 `dwTcHydErrCdSetVelo`，不是"原地待命"
- `Direction` 是绝对运动里的保留字段，给 `MC_Shortest_Way_BkPlcMc`（默认）即可，不要传其它常量

## 4. 错误码 / 返回值

| `ErrorID` 常量 | 含义 | 处理建议 |
|---|---|---|
| `dwTcHydErrCdSoftEnd` | `Position` 越过软限位 | 检查 `Position` 范围 / 软限位设置 |
| `dwTcHydErrCdNotStartable` | 运动算法当前不可接受新命令 | 等待轴静止后重试，或检查 `nProfile` 配置 |
| `dwTcHydErrCdNotReady` | 轴在错误状态或正在停车 | 先 `MC_Reset_BkPlcMc` 清错 |
| `dwTcHydErrCdSetVelo` | `Velocity` 太小（< 1% refVelo） | 增大 `Velocity` |
| `dwTcHydErrCdAcc` | `Acceleration` 或 `Deceleration` 太小（100 s 内达不到速度） | 增大值 |
| (算法错码) | 运动中算法报错（跟随误差超限、阀响应异常等） | 查 PDF §5.2 全局常量；按错码具体处理 |

## 5. 使用注意 / 常见坑

- **`Execute` 边沿触发**：每次新命令都要重新触发上升沿；不要长拉电平期望"持续到位"。
- **`Velocity` 必须 > 1% 参考速度**：`fRefVelo` 在轴参数里。这是为防止速度太小不可控。
- **`Acceleration` / `Deceleration` 不能给 0 假装"瞬时变速"**：会被替换为轴默认参数。液压轴大惯量必须给合理加减速。
- **`Jerk` 保留无效**：液压库当前不实现 jerk-limited 控制；给值不报错但不生效。
- **`Direction` / `BufferMode` 都是保留**：传 `MC_Shortest_Way_BkPlcMc` / `Aborting_BkPlcMc`（默认即可）；传其它值未来版本可能行为变化。
- **下降沿不停轴**：撤 `Execute` 后运动继续；要停轴用 Stop/Halt。
- **错误码经常是算法层而非本 FB**：`ErrorID` 在运动过程中报的码大多是算法层（跟随误差、阀异常等），不是上面列的启动检查码；要排查需结合 `MC_ReadAxisError_BkPlcMc` 持续监视。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_MoveAbsolute_BkPlcMc.TcPOU`](../examples/P_Demo_MC_MoveAbsolute_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机液压锁模轴一周期内多次绝对定位：合模 350 mm 保压 → 开模 30 mm 静置 → 推出 60 mm 顶杆 → 复位回 0。每个目标都是工件坐标系下的已知绝对值。
- **价值**：手写需要直接操作 `pStAxRtData^.fTargetPosition` 等 5+ 字段并自己写状态机判完成；本 FB 一行调用 + PLCopen 标准状态收敛（Done/Error/CommandAborted）让代码简洁。
- **替代方案对比**：
  - `MC_MoveRelative_BkPlcMc`：相对距离，需自己累加位置，多次累计漂移
  - 直接写 NC/算法字段：要熟悉液压库内部状态机
  - **本 FB**：标准绝对定位，PLCopen 接口，最直观

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.2.13
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599701771.html
- **相关 FB**：`MC_MoveRelative_BkPlcMc`（相对距离）、`MC_MoveVelocity_BkPlcMc`（无目标恒速）、`MC_Stop_BkPlcMc` / `MC_Halt_BkPlcMc`（停车）、`MC_Power_BkPlcMc`（前置使能）、`MC_Reset_BkPlcMc`（清错）
