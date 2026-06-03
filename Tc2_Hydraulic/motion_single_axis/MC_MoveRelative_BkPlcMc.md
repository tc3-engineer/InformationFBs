# MC_MoveRelative_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion - Single axis` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599703819.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_MoveRelative_BkPlcMc.TcPOU`](../examples/P_Demo_MC_MoveRelative_BkPlcMc.TcPOU) |

---

## 1. 功能简述

PLCopen 风格**相对定位**功能块（液压库实现）。`Execute` 上升沿启动一次"从当前位置往前/往后走 `Distance` mm"的定位。和 `MC_MoveAbsolute_BkPlcMc` 唯一差别是给的不是绝对坐标而是位移增量；其余启动检查、状态收敛、`Jerk`/`BufferMode` 保留语义完全一致。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute:        BOOL;
    Distance:       LREAL;
    Velocity:       LREAL;
    Acceleration:   LREAL;
    Deceleration:   LREAL;
    Jerk:           LREAL;
    BufferMode:     MC_BufferMode_BkPlcMc:=Aborting_BkPlcMc;    //from V3.0.8
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次相对定位 |
| `Distance` | `LREAL` | — | 相对距离，单位 mm。带符号：正 = 沿正方向、负 = 沿负方向 |
| `Velocity` | `LREAL` | — | 行进速度，单位 mm/s。要求 > 1% 参考速度 |
| `Acceleration` | `LREAL` | — | 加速度，单位 mm/s² |
| `Deceleration` | `LREAL` | — | 减速度，单位 mm/s² |
| `Jerk` | `LREAL` | — | 保留字段，单位 mm/s³ |
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
| `Busy` | `BOOL` | 命令处理中 |
| `Done` | `BOOL` | 成功完成相对位移 |
| `CommandAborted` | `BOOL` | 被另一运动 FB 打断 |
| `Error` | `BOOL` | 启动检查或运动算法错 |
| `ErrorID` | `UDINT` | 错误码 |

## 3. 行为说明

**调用模式**：边沿触发，与 `MC_MoveAbsolute_BkPlcMc` 同。`Execute` 上升沿启动；下降沿清输出但不停轴。

**启动检查（按 PDF 列出顺序）**：
1. **软限位**：若按 `Distance` 走会越过激活的软限位 → `Error`、`ErrorID := dwTcHydErrCdSoftEnd`
2. **运动算法可启动性**：当前不可启动 → `Error`、`ErrorID := dwTcHydErrCdNotStartable`
3. **轴状态**：错误状态 / 停车中 → `Error`、`ErrorID := dwTcHydErrCdNotReady`
4. **`Velocity` 太小**：< 1% 参考速度 → `Error`、`ErrorID := dwTcHydErrCdSetVelo`
5. **`Acceleration` 或 `Deceleration` 太小**：→ `Error`、`ErrorID := dwTcHydErrCdAcc`
6. **算法已持错码**：→ `Error`、`ErrorID := 算法错码`

**运动监视**：通过检查后参数被限到最大允许值并传给算法；轴进入 `McState_DiscreteMotion`；FB 监视轨迹直到 Done/Aborted/Error。

**`Distance` 起点的精确语义**：起点是 `Execute` 上升沿那一刻轴的"当前 NC 设定位置"（不是 `fActPosition` 实际位置）。如果轴当时已在运动，起点会"漂"。所以最稳妥的用法是轴静止时触发。

**典型用法**：物料推送（每按一次按钮往前推 100 mm）；钻孔加工每钻完一孔进给固定距离换孔位；液压顶杆每次顶出 60 mm。

**典型陷阱**：
- 多次相对定位累计误差：每次相对 `Distance` 都是浮点数；连续 100 次后总位置可能与"100 × 100 mm = 10000 mm 绝对值"差几个 µm。对累计精度敏感的场景用绝对定位。
- 在运动中触发：起点漂动可能导致 `Done` 时位置不符预期。

## 4. 错误码 / 返回值

| `ErrorID` 常量 | 含义 | 处理建议 |
|---|---|---|
| `dwTcHydErrCdSoftEnd` | `Distance` 会越过软限位 | 检查方向和距离 |
| `dwTcHydErrCdNotStartable` | 算法不可启动 | 等轴静止 |
| `dwTcHydErrCdNotReady` | 轴在错误或停车中 | `MC_Reset_BkPlcMc` 清错 |
| `dwTcHydErrCdSetVelo` | `Velocity` 太小 | 增大 `Velocity` |
| `dwTcHydErrCdAcc` | 加/减速度太小 | 增大 |

## 5. 使用注意 / 常见坑

- **累计漂移**：连续多次相对定位等于绝对定位累加误差；要求重复到同一坐标用 `MC_MoveAbsolute_BkPlcMc`。
- **`Distance` 带符号**：正 = 正向，负 = 反向；不要靠 `Direction` 输入（本 FB 没有该字段）。
- **起点是 NC 设定位置**：不是实际位置；轴静止时两者相等，运动中触发可能漂。
- **撤 `Execute` 不停轴**：与 Absolute 同。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_MoveRelative_BkPlcMc.TcPOU`](../examples/P_Demo_MC_MoveRelative_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：液压钻孔机床。每钻完一孔，工作台需要进给到下一个孔位（孔间距 100 mm 等距）。每次按"下一孔"按钮，触发本 FB 把工作台往前走 100 mm。
- **价值**：业务侧不需要维护"当前是第几个孔的绝对坐标"；操作员只关心"再前进一步"，本 FB 直接对应这种增量语义。
- **替代方案对比**：
  - `MC_MoveAbsolute_BkPlcMc`：业务侧自己维护"当前孔 + 1 的绝对坐标"，对累计精度要求高的场景更好
  - 用 `MC_MoveJog_BkPlcMc` 的 `MC_JOGMODE_INCHING`：寸动模式，单次按下进一步，更适合手动操作
  - **本 FB**：自动循环里"进一格"的最直接接口

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.2.15
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599703819.html
- **相关 FB**：`MC_MoveAbsolute_BkPlcMc`（绝对定位）、`MC_MoveJog_BkPlcMc`（寸动模式，类似但带 jog 语义）、`MC_Stop_BkPlcMc`（停车）
