# MC_Reset

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_DriveMotionControl` |
| Library Version | `1.5.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `Axis functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8278952075.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_Reset.TcPOU`](../examples/P_Demo_MC_Reset.TcPOU) |

---

## 1. 功能简述

PLCopen Motion Control 标准定义的**轴复位功能块（Function Block, FB）**。`Execute` 上升沿触发一次复位，把 NC 轴从故障状态（Errorstop）拉回可运行状态。

很多情况下该复位会**连带复位所连接的驱动器**；但取决于总线系统或驱动类型，有些场合驱动器仍需单独复位。本 FB 是清除轴错误、让 `MC_Power` 重新就绪的标准入口。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次复位命令 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | 轴数据结构，在系统中唯一标识一根轴；含当前轴状态，包括位置、速度、错误状态等。**必须传引用**（VAR_IN_OUT 语义） |

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
| `Done` | `BOOL` | 复位成功执行时置 `TRUE` |
| `Busy` | `BOOL` | 命令进行中为 `TRUE`（PDF 原文沿用模板写作 "as long as the function block is called with Enable = TRUE"，本 FB 实际是 `Execute` 触发型，含义为命令执行期间为 `TRUE`） |
| `Error` | `BOOL` | 发生错误时为 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出错误号（参见 §4） |

## 3. 行为说明

**触发语义**：`Execute` **上升沿**触发一次复位。和库内所有 `Execute` 型 FB 一样，上升沿后 `Busy` 立刻置 `TRUE`，复位完成后 `Done` 置 `TRUE`、`Busy` 落 `FALSE`；`Execute` 在空闲时落 `FALSE` 会把 `Done` / `Error` / `ErrorID` 一并复位。要再复位一次必须制造新的上升沿。

**状态收敛**：本 FB 输出遵循库的通用规则——`Busy` / `Done` / `Error` 互斥，同一时刻只有一个为 `TRUE`。复位成功 → `Done = TRUE`；复位本身失败 → `Error = TRUE` 并给 `ErrorID`。

**复位的作用范围**：复位把 NC 轴从 Errorstop 状态拉回 Standstill，从而让 `MC_Power` 能重新使能、运动 FB 能重新接受命令。多数情况下也会同时复位所连驱动器；但部分总线 / 驱动类型下，驱动器侧的故障需要另行单独复位（例如驱动器自身的硬件报警）——这种情况下仅 `MC_Reset` 不足以让轴恢复，还要清驱动器告警。

**典型用法**：故障处理流程中，操作员确认排除故障后按"复位"按钮，把按钮信号转上升沿喂给 `Execute`；`Done` 出现后再调 `MC_Power` 重新使能。复位不会让轴运动。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC/驱动错误号（不是 HRESULT）。

| 返回值 / 错误码 | 含义 | 处理建议 |
|---|---|---|
| `Done = TRUE` | 复位成功 | 轴回到 Standstill，可重新 `MC_Power` 使能 |
| `Error = TRUE` + `ErrorID ≠ 0` | 复位失败（驱动未响应复位、故障仍未排除、需驱动器单独复位等） | 检查故障根因是否真排除；部分驱动需单独清驱动器告警后再复位 |

PDF 与 InfoSys 在本 FB 章节均未逐条列出具体 `ErrorID` 码值，具体码值需对照 TwinCAT NC 错误码总表（⚠️ PDF + InfoSys 本章节未枚举）。

## 5. 使用注意 / 常见坑

- **复位是边沿触发**：`Execute` 一直拉高不会反复复位，只有上升沿那一次有效。复位按钮信号建议经 `R_TRIG` 转沿。
- **复位 ≠ 故障已排除**：若故障根因（如跟随误差超限的机械卡死）还在，复位后再发命令会立刻重新报错。复位只是"清状态"，不是"修故障"。
- **部分驱动需单独复位**：PDF 明确指出取决于总线 / 驱动类型，有些场合驱动器还要单独复位。仅 `MC_Reset` 没让轴恢复时，要去清驱动器侧告警。
- **复位后要重新使能**：复位把轴拉回 Standstill，但不会自动使能。`Done` 后通常要再走 `MC_Power` 流程。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_Reset.TcPOU`](../examples/P_Demo_MC_Reset.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：进给轴跟随误差超限报故障，操作员排除卡阻后按复位按钮恢复轴
PROGRAM P_Demo_MC_Reset
VAR
    fbResetAxis     : MC_Reset;
    axisFeed        : AXIS_REF;
    rtOperatorReset : R_TRIG;              // 把按钮电平转上升沿
    bOperatorAck    : BOOL := FALSE;       // 在线写 TRUE 模拟按复位按钮
    bResetDone      : BOOL;
    bResetBusy      : BOOL;
    bResetError     : BOOL;
    nResetErrorID   : UDINT;
END_VAR

// 复位按钮信号转上升沿喂给 Execute；Axis 是 VAR_IN_OUT 用 :=
rtOperatorReset(CLK := bOperatorAck);
fbResetAxis(
    Execute := rtOperatorReset.Q,
    Axis    := axisFeed,
    Done    => bResetDone,
    Busy    => bResetBusy,
    Error   => bResetError,
    ErrorID => nResetErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：所有用 Beckhoff 伺服端子做运动的设备，遇到跟随误差超限、急停后恢复、驱动报警等故障时，需要一个标准的"复位 → 恢复运行"入口。操作员按复位按钮、上位机下发复位命令都走这个 FB。
- **价值**：业务代码不必去拼 NC 轴控制字里的复位位、不必自己做复位状态握手，单个 FB 调用即把"发复位 + 上报结果"封装好；`Done` 出现即可继续重新使能。
- **替代方案对比**：
  - 直接写 NC 轴接口复位位：要手动 set/clear `nControl` 复位位并轮询，易出时序错误
  - 直接重新 `MC_Power`：轴在 Errorstop 状态下使能无效，必须先复位
  - **本 FB**：PLCopen 标准复位入口，与 `MC_Power` 配套形成"复位 → 使能"标准恢复链

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf) §5.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8278952075.html
- **相关 FB**：`MC_Power`（复位后重新使能）、`MC_Stop`（停轴并锁轴，需 `MC_Reset` 解锁）
