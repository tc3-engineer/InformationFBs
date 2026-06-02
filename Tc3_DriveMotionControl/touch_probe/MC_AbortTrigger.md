# MC_AbortTrigger

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_DriveMotionControl` |
| Library Version | `1.5.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `Touch probe` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8279533067.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_AbortTrigger.TcPOU`](../examples/P_Demo_MC_AbortTrigger.TcPOU) |

---

## 1. 功能简述

**取消测头（Touch Probe）采样周期的功能块（Function Block, FB）**。它配合 `MC_TouchProbe` 使用：`MC_TouchProbe` 通过激活驱动器硬件里的位置锁存启动一次测头采样，而 `MC_AbortTrigger` 用于在触发信号尚未锁存位置之前**提前终止**这次采样。

如果测头采样已经成功完成，则**无需**调用本 FB。它解决的是"采样发了但触发信号迟迟不来，要主动放弃这次采样、释放硬件锁存"的场景。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发命令，同时禁用（关闭）外部位置锁存 |

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
| `TriggerInput` | `TRIGGER_REF` | 描述触发源的数据结构。**必须与要取消的那次 `MC_TouchProbe` 调用使用同一个 `TriggerInput` 结构**，否则取消的不是同一个采样周期 |

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
| `Done` | `BOOL` | 测头采样周期成功终止时置 `TRUE` |
| `Busy` | `BOOL` | FB 处于激活状态时为 `TRUE`；处于默认（空闲）状态时为 `FALSE` |
| `Error` | `BOOL` | 发生错误时为 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出错误号（参见 §4） |

## 3. 行为说明

**触发语义**：`Execute` **上升沿**触发一次取消，并同时禁用外部位置锁存。上升沿后 `Busy` 置 `TRUE`，取消完成后 `Done` 置 `TRUE`。输出遵循库通用规则（`Busy` / `Done` / `Error` 互斥）。

**与 `MC_TouchProbe` 的配对关系**：`MC_TouchProbe` 上升沿启动采样后，只有 `Done` / `Error` / `CommandAborted` 之一变 `TRUE` 才算这一次采样结束；在结束之前若想中途放弃，**必须**用 `MC_AbortTrigger` 携带**同一个 `TriggerInput` 结构**调用一次。被取消的 `MC_TouchProbe` 此时会把 `CommandAborted` 置 `TRUE`。如果不取消而直接想重发采样，会因"上一个采样还占着硬件锁存"而无法发起新周期。

**`TriggerInput` 必须一致**：`Axis` 和 `TriggerInput` 都是 VAR_IN_OUT，必须传引用。取消操作靠 `TriggerInput` 来识别"取消哪一个采样"，因此 `MC_AbortTrigger` 和被取消的 `MC_TouchProbe` 必须共享同一个 `TriggerInput` 变量实例。

**采样已成功则无需调用**：若 `MC_TouchProbe` 已经 `Done`，硬件锁存已正常释放，不需要也不应该再调 `MC_AbortTrigger`。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC/驱动错误号（不是 HRESULT）。

| 返回值 / 错误码 | 含义 | 处理建议 |
|---|---|---|
| `Done = TRUE` | 采样周期成功终止、硬件锁存已释放 | 可发起新的 `MC_TouchProbe` 采样 |
| `Error = TRUE` + `ErrorID ≠ 0` | 取消失败 | 检查 `TriggerInput` 是否与原采样一致、轴/驱动是否支持该锁存 |

PDF 与 InfoSys 在本 FB 章节均未逐条列出具体 `ErrorID` 码值，具体码值需对照 TwinCAT NC 错误码总表（⚠️ PDF + InfoSys 本章节未枚举）。

## 5. 使用注意 / 常见坑

- **`TriggerInput` 必须是同一个实例**：取消的对象由 `TriggerInput` 标识。用了不同的 `TriggerInput` 变量，取消的就不是你想要的那次采样。
- **采样成功后别再 Abort**：`MC_TouchProbe` 已 `Done` 时不需要取消；多此一举可能扰乱下一次采样的锁存状态。
- **不取消就发新采样会失败**：若上一次采样还没结束（既没等到触发也没取消），硬件锁存被占用，新的 `MC_TouchProbe` 无法发起。超时未触发的采样要么等、要么用本 FB 取消。
- **`Execute` 是边沿触发**：上升沿取消一次；建议用 `R_TRIG` 转沿，避免一直拉高。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_AbortTrigger.TcPOU`](../examples/P_Demo_MC_AbortTrigger.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：测头采样等触发信号超时，主动取消这次采样以便重新发起
PROGRAM P_Demo_MC_AbortTrigger
VAR
    fbAbortTrigger  : MC_AbortTrigger;
    axisMeasure     : AXIS_REF;
    trigInput       : TRIGGER_REF;         // 必须与对应 MC_TouchProbe 同一个实例
    rtAbort         : R_TRIG;              // 取消请求转上升沿
    bAbortRequest   : BOOL := FALSE;       // 在线写 TRUE：放弃当前采样
    bAbortDone      : BOOL;
    bAbortBusy      : BOOL;
    bAbortError     : BOOL;
    nAbortErrorID   : UDINT;
END_VAR

// 取消请求转上升沿；Axis 和 TriggerInput 都是 VAR_IN_OUT 用 :=
rtAbort(CLK := bAbortRequest);
fbAbortTrigger(
    Execute      := rtAbort.Q,
    Axis         := axisMeasure,
    TriggerInput := trigInput,
    Done         => bAbortDone,
    Busy         => bAbortBusy,
    Error        => bAbortError,
    ErrorID      => nAbortErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：用测头功能在线测量工件边沿 / 标记位置时，若触发信号因工件缺失、传感器遮挡等迟迟不来，采样会一直挂着占用硬件锁存。本 FB 用于"放弃这次采样、释放锁存、准备重测"。常见于检测站、贴标对位、边缘找正等。
- **价值**：业务代码不必去操作驱动器对象字典里的锁存使能位，单个 FB 调用即安全终止采样并释放硬件；配 `TriggerInput` 精确指定取消对象。
- **替代方案对比**：
  - 直接清驱动器锁存对象（如 0x8030/0x8031 里的相关位）：要熟悉对象字典，且容易和 `MC_TouchProbe` 的内部状态打架
  - 干等触发信号 / 重启轴：要么阻塞流程，要么代价过大
  - **本 FB**：与 `MC_TouchProbe` 配套的标准取消入口，状态干净

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf) §5.2.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8279533067.html
- **相关 FB**：`MC_TouchProbe`（启动测头采样，本 FB 取消它）；`TRIGGER_REF`（触发源数据结构）
