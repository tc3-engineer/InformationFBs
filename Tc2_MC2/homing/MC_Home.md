# MC_Home

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Homing` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70117515.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_Home.xml`](../examples/P_Demo_MC_Home.xml) |

---


## 1. 功能简述

PLCopen 标准定义的**轴归零（参考运行）FB**。把轴从"未校准"状态变为"已校准"——通过参考运行序列（搜索原点开关 / 编码器 Z 信号 / 用户直接设位置等）确立轴的绝对零点。

参考模式由 System Manager 中编码器参数"Reference Mode"决定，本 FB 只是**触发**这个过程，具体序列取决于编码器硬件。`HomingMode` 输入可在多种模式间切换：默认归零、直接置位、强制标记已校准、复位校准状态等。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute         : BOOL;
    Position        : LREAL         := DEFAULT_HOME_POSITION;
    HomingMode      : MC_HomingMode;
    BufferMode      : MC_BufferMode;
    Options         : ST_HomingOptions;
    bCalibrationCam : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次定位命令；命令进入运动队列后即开始执行，不需保持高电平 |
| `Position` | `LREAL` | `DEFAULT_HOME_POSITION` | 归零完成后轴的绝对位置；取常量 `DEFAULT_HOME_POSITION` 表示采用 System Manager 里配的"参考位置" |
| `HomingMode` | `MC_HomingMode` | — | 归零模式：`MC_DefaultHoming`（默认序列）/ `MC_Direct`（直接置位不运动）/ `MC_ForceCalibration`（强制标记已校准不动）/ `MC_ResetCalibration`（清除已校准标志） |
| `BufferMode` | `MC_BufferMode` | — | 队列模式：当轴正在执行另一命令时本命令的接入方式（`MC_Aborting` / `MC_Buffered` / `MC_BlendingLow` / `MC_BlendingPrevious` / `MC_BlendingNext` / `MC_BlendingHigh`）；耦合从轴只允许 `Aborting` |
| `Options` | `ST_HomingOptions` | — | 归零序列选项（保留扩展） |
| `bCalibrationCam` | `BOOL` | — | 校准凸轮（原点开关）信号，由用户接入；归零序列在凸轮信号上升/下降沿做触发 |

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
    Done           : BOOL;
    Busy           : BOOL;
    Active         : BOOL;
    CommandAborted : BOOL;
    Error          : BOOL;
    ErrorID        : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 归零完成置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 上升沿后立即变 `TRUE`，结束（无论 Done/Aborted/Error）才变 `FALSE`；FB 可接受新命令的前提是 `Busy = FALSE` |
| `Active` | `BOOL` | 表示**当前正在执行**本 FB 的命令；若被 `BufferMode` 缓冲则要等前一命令完成才变 `TRUE` |
| `CommandAborted` | `BOOL` | 命令未完成就被中止（被另一 Move 抢占 / `MC_Stop` 停掉）时置 `TRUE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4） |

## 3. 行为说明

**触发**：`Execute` 上升沿启动归零序列。具体序列依赖编码器配置：

- **增量编码器 + 原点开关**：轴先按 System Manager 中"Reference Velocity (Sync)" 反方向找凸轮 → 找到后反向用"Reference Velocity (Cal)" 慢速过凸轮 → 在凸轮信号边沿（或下一个编码器 Z 信号）锁定零点 → 设位置为 `Position`
- **绝对编码器**：通常直接读编码器绝对值并设为 `Position`
- **MC_Direct**：不动轴，直接把当前位置设为 `Position`（适合手动校准后告诉 NC "我现在在哪"）
- **MC_ForceCalibration**：不动轴，强制把"轴已校准"标志置 TRUE（适合诊断 / 跳过参考运行）
- **MC_ResetCalibration**：不动轴，把"轴已校准"标志清 FALSE（用于强制下次必须归零）

**`bCalibrationCam` 信号接入**：通常把外部原点接近开关（NPN/PNP）的 PLC 输入直接连到本入口；NC 在归零序列中读这个位。

**与轴使能的关系**：归零通常要求轴 `MC_Power` 后处于 Standstill 状态；未使能轴无法运动归零（`MC_Direct` 等不动的模式除外）。

**归零完成后 `Axis.Status.HomingDone = TRUE`**（NC 内部状态）。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- **`Position` 留默认 = 用 System Manager 配置**：常量 `DEFAULT_HOME_POSITION` 由 Beckhoff 定义；不要传字面值 0 替代，因为很多轴的零点是非零绝对值（比如龙门机床的工件坐标原点）。
- **`HomingMode` 选错代价大**：`MC_ResetCalibration` 会让轴失去校准状态，再发任何位置类 Move 都报错；误用了要再 `MC_Home(HomingMode := MC_DefaultHoming)` 重新归。
- **`MC_Direct` 适合手动模式校准**：操作员手动把轴拖到已知位置后调 `MC_Direct(Position := knownPos)` 告诉 NC，省去再走一遍参考运行。
- **`bCalibrationCam` 信号必须与编码器"Reference Mode"匹配**：选错下降沿/上升沿模式会归零失败甚至撞极限。
- **归零进行中其它 Move 命令被锁**：和 `MC_Stop` 锁轴行为类似，归零期间发 Move 会被拒。
- **绝对编码器一般不需要每次开机归零**：但 TwinCAT 仍需要"知道编码器值映射到哪个绝对坐标"，开机第一次仍要 `MC_Direct` 或参数配置告诉 NC。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_Home.xml`](../examples/P_Demo_MC_Home.xml)

```iecst
// 场景：CNC 机床开机自动归零 X 轴 — 走到原点开关然后定零，定零位置取 System Manager 配置
PROGRAM P_Demo_MC_Home
VAR
    fbAxisHoming      : MC_Home;
    axisX             : AXIS_REF;
    rtHomeTrig        : R_TRIG;
    bRequestHoming    : BOOL;
    bHomeCamSignal    : BOOL;
    bHomingDone       : BOOL;
    bHomingActive     : BOOL;
    nErrorID          : UDINT;
END_VAR

rtHomeTrig(CLK := bRequestHoming);
fbAxisHoming(
    Execute         := rtHomeTrig.Q,
    Position        := DEFAULT_HOME_POSITION,
    HomingMode      := MC_DefaultHoming,
    BufferMode      := MC_Aborting,
    bCalibrationCam := bHomeCamSignal,
    Axis            := axisX,
    Done            => bHomingDone,
    Active          => bHomingActive,
    ErrorID         => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：开机首次启动设备前的轴归零、操作员替换工件 / 重定基准的工序、绝对编码器丢失零点后的恢复、设备故障复位后的强制重新校准。
- **价值**：把"找原点开关 → 锁编码器 Z → 设零位"三段标准化序列封装为一个 FB；切换编码器硬件代码不变。
- **替代方案对比**：
  - 直接写 NC 通道命令（`MC_HOME`）：要拼 NC 控制字 + 监视状态字，10+ 行代码
  - 操作员手动 jog + `MC_Direct`：能做但依赖操作员准度
  - **本 FB**：自动化归零的标准做法；`HomingMode` 切换覆盖所有变体

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70117515.html
- **相关 FB**：`MC_Power`（先使能再归零）、`MC_Reset`（清错后才能归零）、`MC_Stop`、`MC_HomingMode`（枚举定义）
