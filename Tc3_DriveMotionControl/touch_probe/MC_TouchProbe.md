# MC_TouchProbe

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_DriveMotionControl` |
| Library Version | `1.5.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `Touch probe` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8279463563.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_TouchProbe.TcPOU`](../examples/P_Demo_MC_TouchProbe.TcPOU) |

---

## 1. 功能简述

**测头采样（Touch Probe）功能块（Function Block, FB）**。在一个数字信号到来的瞬间，记录下轴的位置。该位置由**外部硬件锁存**捕获，因此精度极高且与 PLC 循环时间无关——这是它相比"软件读位置"的核心优势。

本 FB 负责控制这套硬件锁存机制并取出外部记录的位置。`Execute` 上升沿激活外部位置锁存启动一次采样周期；该周期只有在 `Done` / `Error` / `CommandAborted` 之一变 `TRUE` 时才结束。若要中途放弃，必须用同一个 `TriggerInput` 调用 `MC_AbortTrigger`，否则无法发起新周期。相关参数可能需要在驱动参数里设置（伺服端子见对象 DMC Setting (0x8030) / DMC Features (0x8031)）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute       : BOOL;
    WindowOnly    : BOOL;
    FirstPosition : LREAL;
    LastPosition  : LREAL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发命令，同时激活外部位置锁存 |
| `WindowOnly` | `BOOL` | — | `TRUE` 时只记录落在 `FirstPosition`~`LastPosition` 窗口内的位置；窗口外的位置被丢弃并自动重新激活锁存，只有落窗内才置 `Done`。窗口可按绝对值或模数值解释（由 `TriggerInput` 的 `ModuloPositions` 标志决定）：绝对值时窗口唯一；模数值时窗口在轴参数定义的模数周期内（如 0~360°）重复 |
| `FirstPosition` | `LREAL` | — | `WindowOnly = TRUE` 时记录窗口的起始位置。可按绝对值或模数值解释（由 `TriggerInput` 的 `ModuloPositions` 标志决定） |
| `LastPosition` | `LREAL` | — | `WindowOnly = TRUE` 时记录窗口的结束位置。可按绝对值或模数值解释（由 `TriggerInput` 的 `ModuloPositions` 标志决定） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis         : AXIS_REF;
    TriggerInput : TRIGGER_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | 轴数据结构 |
| `TriggerInput` | `TRIGGER_REF` | 描述触发源的数据结构。首次调用本 FB 前必须先对该结构参数化（设置触发源、边沿、是否模数等） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done             : BOOL;
    Busy             : BOOL;
    CommandAborted   : BOOL;
    Error            : BOOL;
    ErrorId          : UDINT;
    RecordedPosition : LREAL;
    RecordedData     : MC_TouchProbeRecordedData;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 成功检测到一个轴位置时置 `TRUE`，该位置输出到 `RecordedPosition` |
| `Busy` | `BOOL` | FB 处于激活状态时为 `TRUE`；处于默认（空闲）状态时为 `FALSE` |
| `CommandAborted` | `BOOL` | 过程被外部事件中断（例如被 `MC_AbortTrigger` 调用）时置 `TRUE` |
| `Error` | `BOOL` | 发生错误时为 `TRUE` |
| `ErrorId` | `UDINT` | `Error` 置位时给出错误号。注意 PDF 此输出名写作 `ErrorId`（小写 d） |
| `RecordedPosition` | `LREAL` | 记录到的轴位置 |
| `RecordedData` | `MC_TouchProbeRecordedData` | 记录数据结构，含本次采样的更详细信息 |

## 3. 行为说明

**触发与生命周期**：`Execute` **上升沿**激活外部位置锁存，启动一次采样周期。一旦启动，该周期只有在 `Done` / `Error` / `CommandAborted` 之一变 `TRUE` 时才终止。在此之前若要中止，**必须**用携带**同一个 `TriggerInput`** 的 `MC_AbortTrigger` 调用，否则无法发起新的采样周期。这是测头采样最关键的状态约束。

**硬件锁存的精度优势**：位置由驱动器硬件在触发信号沿到来的瞬间锁存，与 PLC 循环周期无关。因此即便 PLC 周期是毫秒级，记录的位置仍是触发瞬间的真实位置，没有"循环采样误差"。这是测头用于高精度边沿 / 标记定位的根本原因。

**`WindowOnly` 窗口过滤**：`WindowOnly = FALSE` 时，第一个触发信号到来就记录位置并 `Done`。`WindowOnly = TRUE` 时，只接受落在 `FirstPosition`~`LastPosition` 窗口内的触发：窗口外的触发被丢弃，锁存自动重新激活继续等，直到出现窗口内的触发才 `Done`。窗口的解释方式（绝对 / 模数）由 `TriggerInput.ModuloPositions` 决定——绝对值下窗口唯一；模数值下窗口在模数周期（如 0~360°）内重复，适合旋转轴每圈固定相位采样。

**`TriggerInput` 须预先参数化**：`TriggerInput` 是 VAR_IN_OUT，首次调用前必须设好（触发源、信号沿、是否模数窗口等）。它同时是 `MC_AbortTrigger` 识别"取消哪个采样"的依据，所以采样与取消要共用同一个 `TriggerInput` 实例。

**结果读取**：成功后 `Done = TRUE`，记录位置在 `RecordedPosition`，更详细信息在 `RecordedData`。被 `MC_AbortTrigger` 取消则 `CommandAborted = TRUE`。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorId : UDINT` 输出（注意 PDF 此处输出名为 `ErrorId`，小写 d）。`ErrorId` 为 TwinCAT NC/驱动错误号（不是 HRESULT）。

| 返回值 / 错误码 | 含义 | 处理建议 |
|---|---|---|
| `Done = TRUE` | 成功记录位置，见 `RecordedPosition` | 读取 `RecordedPosition` / `RecordedData` |
| `CommandAborted = TRUE` | 采样被外部中断（如 `MC_AbortTrigger`） | 视业务决定是否重发采样 |
| `Error = TRUE` + `ErrorId ≠ 0` | 采样出错（驱动不支持锁存、`TriggerInput` 未参数化、轴/对象配置缺失等） | 检查驱动 DMC Setting (0x8030) / DMC Features (0x8031) 参数、`TriggerInput` 是否预先设好 |

PDF 与 InfoSys 在本 FB 章节均未逐条列出具体 `ErrorId` 码值，具体码值需对照 TwinCAT NC 错误码总表（⚠️ PDF + InfoSys 本章节未枚举）。

## 5. 使用注意 / 常见坑

- **输出名是 `ErrorId`（小写 d）**：与库内其它 FB 的 `ErrorID`（大写 D）不一致。本仓库严格按 PDF 大小写搬运；引用该输出时注意拼写。
- **采样不结束就发不了新采样**：周期只在 `Done`/`Error`/`CommandAborted` 之一出现时才结束。卡住不动（既没触发也没取消）时，必须用 `MC_AbortTrigger` 取消才能重发。
- **`TriggerInput` 首次调用前必须参数化**：没设触发源 / 边沿就调用会出错。它还要和 `MC_AbortTrigger` 共用同一实例。
- **驱动参数要先配**：硬件锁存依赖驱动器对象（伺服端子 0x8030 / 0x8031）。参数没配好，采样无法工作。
- **窗口模数解释看 `TriggerInput.ModuloPositions`**：旋转轴每圈固定相位采样要用模数窗口；直线轴用绝对窗口。配错会导致窗口落点不符合预期。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_TouchProbe.TcPOU`](../examples/P_Demo_MC_TouchProbe.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：检测站用测头在工件边沿触发的瞬间高精度记录轴位置，用于尺寸测量
PROGRAM P_Demo_MC_TouchProbe
VAR
    fbTouchProbe    : MC_TouchProbe;
    axisMeasure     : AXIS_REF;
    trigInput       : TRIGGER_REF;         // 调用前须先参数化；与 Abort 共用同一实例
    rtStartProbe    : R_TRIG;              // 启动采样请求转上升沿
    bStartProbe     : BOOL := FALSE;       // 在线写 TRUE 启动一次采样
    bWholeRange     : BOOL := FALSE;       // FALSE=第一个触发即记录（不限窗口）
    lrEdgePosition  : LREAL;               // 记录到的边沿位置（结果）
    bProbeDone      : BOOL;
    bProbeBusy      : BOOL;
    bProbeAborted   : BOOL;
    bProbeError     : BOOL;
    nProbeErrorId   : UDINT;               // 注意 PDF 输出名为 ErrorId（小写 d）
END_VAR

// 启动请求转上升沿；Axis 与 TriggerInput 都是 VAR_IN_OUT 用 :=
rtStartProbe(CLK := bStartProbe);
fbTouchProbe(
    Execute          := rtStartProbe.Q,
    WindowOnly       := bWholeRange,
    FirstPosition    := 0.0,
    LastPosition     := 0.0,
    Axis             := axisMeasure,
    TriggerInput     := trigInput,
    Done             => bProbeDone,
    Busy             => bProbeBusy,
    CommandAborted   => bProbeAborted,
    Error            => bProbeError,
    ErrorId          => nProbeErrorId,
    RecordedPosition => lrEdgePosition
);
```

## 7. 业务场景与实际价值

- **场景**：在线尺寸测量、工件边沿找正、标记 / 缺口定位、贴标对位等需要"在某数字信号瞬间精确记录轴位置"的场合。例如玻璃切割前找边、卷料上的标记跟随、旋转轴每圈固定相位采样。
- **价值**：硬件锁存捕获位置，精度与循环周期无关；业务代码不必去操作驱动器对象字典、不必担心软件读位置的循环采样误差，单个 FB 调用即拿到高精度记录位置。`WindowOnly` 还能过滤掉窗口外的杂触发。
- **替代方案对比**：
  - 软件在 PLC 里轮询数字输入再读位置：精度受循环周期限制（毫秒级抖动），高速运动下误差大
  - 直接操作驱动器锁存对象：要熟悉对象字典且状态机要自己管
  - **本 FB**：PLCopen 标准测头入口，配 `MC_AbortTrigger` 形成完整采样 / 取消机制，精度高、状态清晰

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf) §5.2.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8279463563.html
- **相关 FB**：`MC_AbortTrigger`（取消本采样）；`TRIGGER_REF`（触发源结构）、`MC_TouchProbeRecordedData`（记录数据结构）
