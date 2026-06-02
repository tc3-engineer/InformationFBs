# MC_SetCamOnlineChangeMode

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Camming` |
| Library Version | `1.9.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5050_TC3_NC_Camming_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclibmc2_camming/460424971.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_SetCamOnlineChangeMode.TcPOU`](../examples/P_Demo_MC_SetCamOnlineChangeMode.TcPOU) |

---

## 1. 功能简述

**配置后续 cam 表写入操作（`MC_WriteMotionFunction` / `MC_WriteMotionFunctionPoint`）的生效时机和缩放模式**的功能块。本 FB **不实际写 cam 数据**，只告诉 NC："从现在起，再来的 cam 写入命令，请按以下规则决定何时生效、是否缩放"。

由 `ActivationMode` 选定激活模式（立即生效 / 主轴到达指定位置才生效 / 主轴下次过零位才生效 / ...），由 `MasterScalingMode` / `SlaveScalingMode` 选定主从轴缩放方式（不缩放 / 等比缩放等）。`ActivationPosition` 用于"到达位置才激活"类模式的目标位置；`CamTableID` 指定本配置作用于哪张 cam 表。

由于"设置一次后影响后续所有写入"，工程上通常在系统初始化阶段调用一次或在每次配方切换前调用一次，**不必每次写 cam 前都调用**。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute            : BOOL;
    ActivationMode     : MC_CamActivationMode;
    ActivationPosition : LREAL;
    MasterScalingMode  : MC_CamScalingMode;
    SlaveScalingMode   : MC_CamScalingMode;
    CamTableID         : MC_CAM_ID;
    Options            : ST_SetOnlineChangeModeOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次配置 |
| `ActivationMode` | `MC_CamActivationMode` | — | 决定 cam 写入数据何时、如何生效的枚举。例如 `MC_CAMACTIVATION_NOW`（立即）、`MC_CAMACTIVATION_ATMASTERCAMPOS`（主轴到达指定 cam 表位置时切）等。完整枚举见 PDF §8.2 `MC_CamActivationMode` |
| `ActivationPosition` | `LREAL` | — | 可选的主轴位置参数。当 `ActivationMode` 为按位置激活类（如 `MC_CAMACTIVATION_ATMASTERCAMPOS`）时，指主轴到达该位置时执行切换；该位置参考**未缩放**的 cam 表。若应用层位置参考已缩放的 cam，请在调用前先除以 `MasterScaling` |
| `MasterScalingMode` | `MC_CamScalingMode` | — | 主轴缩放方式的枚举（如不缩放、等比缩放等）。完整枚举见 PDF §8.2 `MC_CamScalingMode` |
| `SlaveScalingMode` | `MC_CamScalingMode` | — | 从轴缩放方式的枚举 |
| `CamTableID` | `MC_CAM_ID` | — | 本配置作用的凸轮表 ID（`UDINT` 别名）。每张表可有独立的激活策略 |
| `Options` | `ST_SetOnlineChangeModeOptions` | — | 额外选项结构。当前已知字段：`SynchronousAccess`（`BOOL`）— `TRUE` 表示走同步访问（无时延），仅在极端时序敏感场景下用 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done    : BOOL;
    Busy    : BOOL;
    Error   : BOOL;
    ErrorID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `Done` | `BOOL` | 配置成功下发到 NC 置 `TRUE`；与 `Error` 互斥 |
| `Busy` | `BOOL` | `Execute` 上升沿后立即置 `TRUE`，结束后变 `FALSE`；`Busy = FALSE` 才能接受新命令 |
| `Error` | `BOOL` | 配置过程出错置 `TRUE`，与 `Done` 互斥 |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号 |

### VAR_IN_OUT

无

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次配置下发——FB 向 NC 发送"今后对 `CamTableID` 这张表的 cam 写入，按 `ActivationMode` 等配置处理"。`Busy := TRUE`，配置应用后 `Done := TRUE`、`Busy := FALSE`。

**重点：本 FB 不改 cam 形状**，也不立即产生从轴可见的变化；它只是**改变下一次 / 后续 `MC_WriteMotionFunction` / `MC_WriteMotionFunctionPoint` 调用的激活规则**。所以"调了本 FB 但没看到从轴动"是正常现象。

**激活模式的语义**：
- **立即生效类**：cam 写入后立刻影响从轴运动；适合从轴静止或机械上可容忍跳变的场景；动态运行时改 cam 用这种容易出冲击
- **主轴到达指定位置激活类**（`MC_CAMACTIVATION_ATMASTERCAMPOS`）：cam 写入后排队，等主轴到达 `ActivationPosition` 才切换；适合周期循环的应用（如包装机一个换型周期到了再换 cam）
- 其他模式见 `MC_CamActivationMode` PDF §8.2

**`ActivationPosition` 的参考系**：PDF 明确说"该位置参考**未缩放**的 cam 表"。如果应用层算的是缩放后的位置，调用前要除以 `MasterScaling` 反算回未缩放位置。常见错误是直接传缩放后的物理坐标，导致激活点错位。

**缩放模式作用**：`MasterScalingMode` / `SlaveScalingMode` 决定 cam 表的主从轴坐标是否按 `MC_CamIn` 调用时给的 scaling 参数线性变换；不缩放即"按 cam 表里写的原坐标"。具体枚举见 PDF §8.2 `MC_CamScalingMode`。

**典型用法**：
1. 系统初始化或配方切换时调用本 FB，把激活模式配为应用工艺要求的形态
2. 后续 `MC_WriteMotionFunction*` 调用都按本配置走
3. 中途想改激活规则再调本 FB 一次（参数变了重新 `Execute`）

**典型陷阱**：忘了调本 FB → 用了 NC 默认的激活策略（一般是立即生效），动态写 cam 产生机械冲击；`ActivationPosition` 传成缩放后位置；以为本 FB 会立即影响从轴运动。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出，`ErrorID` 是 TwinCAT NC 错误号（不是 HRESULT）。常见错误类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4Bxx` 段（NC cam 表错） | `CamTableID` 无效 / 表未加载 / `ActivationMode` 或 scaling 枚举值越界 | 确认表已 `MC_CamTableSelect` 加载、枚举值是 PDF 列出的有效成员 |
| `16#4260`、`16#4261` 等 | NC 通道命令错（参数检查失败、通道未 ready） | 检查 NC 通道状态 |

> ⚠️ 待人工确认：PDF 第 7.5 节未列出本 FB 专属的具体错误码值。完整 NC 错误号请参见 `Tc2_MC2` PDF 附录《Overview of axis error codes》或 InfoSys 主题 `E_AxisErrorCodes`。

**清错**：本 FB 自身无 reset 入口；`Error / ErrorID` 在下一次 `Execute` 上升沿自动清零。NC 通道级错误需 `MC_Reset` 清除。

## 5. 使用注意 / 常见坑

- **本 FB 是"配置类"，不是"动作类"**：调用它不会让任何 cam 形状变化；只影响后续写入命令的生效规则。
- **`ActivationPosition` 是未缩放位置**：见 §3；最常见的坑就是传成缩放后位置。
- **每张 cam 表独立配置**：`CamTableID` 决定本配置作用于哪张；多张表混用要为每张分别调用。
- **不必每次写 cam 前调用**：配一次后所有后续写入都按这配置走，重复调用浪费 NC 通信带宽。
- **配置和实际写入之间不要有竞态**：本 FB 也是异步的，`Done = TRUE` 之前不要发 `MC_WriteMotionFunction`；否则前一个写入可能仍按旧规则生效。
- **`Options.SynchronousAccess` 谨慎用**：与其他 cam FB 一样，仅在极端时序敏感才打开（工程经验补充）。
- **激活模式选择要看机械特性**：高速主轴 + 大惯量从轴 → 选"到达位置激活"避免冲击；低速人工调试 → 立即生效更简单。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_SetCamOnlineChangeMode.TcPOU`](../examples/P_Demo_MC_SetCamOnlineChangeMode.TcPOU)

例程演示"系统初始化时为生产凸轮表配置激活策略：cam 写入后排队等主轴到达 0 位才切换"。

## 7. 业务场景与实际价值

- **场景**：所有动态修改 cam 形状的工程都先调本 FB 一次决定生效策略：
  - 包装机配方切换 → 选"到达主轴 0 位才切"，确保不在产品中间换 cam
  - 调试期 → 选立即生效便于观察
  - 高精度卷绕机 → 选"主轴下个零点周期切换"避免相位跳
- **价值**：把"写 cam 数据"和"激活时机"两件事分开，PLC 程序写 cam 时不用每次都判断"现在能不能切"——由 NC 内核按本配置统一决策。这是 cam runtime API 安全使用的核心机制。
- **替代方案对比**：
  - **不调本 FB**：用 NC 默认激活模式（一般是立即生效）；动态写 cam 极容易冲击机械
  - **PLC 自己判断主轴位置再写 cam**：判断逻辑复杂、延迟不可控；用本 FB 让 NC 内核以微秒级时序做切换更可靠
  - **本 FB 是唯一干净的解决方案**

## 8. 参考资料

- **PDF**：[TF5050_TC3_NC_Camming_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5050_TC3_NC_Camming_EN.pdf) §7.5（第 42 页）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclibmc2_camming/460424971.html
- **相关 FB**：`MC_WriteMotionFunction`、`MC_WriteMotionFunctionPoint`（被本 FB 配置影响的写入操作）、`MC_CamIn`（建立 cam 耦合）
- **相关 DUT**：`MC_CamActivationMode`、`MC_CamScalingMode`、`MC_CAM_ID`、`ST_SetOnlineChangeModeOptions`（PDF §8.2、§8.x）
- **状态字段**：`Axis.Status.CamDataQueued`（`AXIS_REF`）
