# CTU

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Counter` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74400779.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_CTU.xml`](../examples/P_Demo_CTU.xml) |

---

## 1. 功能简述

`CTU` 是 **IEC 61131-3 标准块**之一，实现**向上递增计数器**（Counter Up）。每次 `CU` 输入出现上升沿，内部计数变量 `CV` 加 1；当 `CV` 达到（或超过）门限 `PV` 时输出 `Q` 置 TRUE。`RESET` 任何时刻置 TRUE 都会把 `CV` 清零并让 `Q` 回 FALSE。

计数值类型 `WORD`（16 位无符号），范围 0–65535。**PDF / InfoSys 均未说明 `CV` 达到 65535 后的后续行为（⚠️ 待官方确认）**——可能继续递增到回卷为 0，也可能在 65535 处饱和不再递增。业务上需要超过 65535 的累计计数请用 `UDINT` 手写自加循环，不要依赖 CTU 内部回卷/饱和的任一假设。

典型用途：产品累计计数、按键按下次数统计、报警发生次数、工序步进、电机启停次数寿命统计。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    CU    : BOOL; (* Count Up on Rising Edge*)
    RESET : BOOL; (* Reset Counter to 0 *)
    PV    : WORD; (* Counter Limit *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `CU` | `BOOL` | 计数输入。**上升沿**（FALSE → TRUE）时 `CV` 加 1；电平保持 TRUE 不会持续累加 |
| `RESET` | `BOOL` | 复位输入。TRUE 时 `CV := 0`、`Q := FALSE`，并屏蔽 `CU`（即使同周期 CU 上升也不计数） |
| `PV` | `WORD` | 计数门限。`CV >= PV` 时 `Q := TRUE` |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q  : BOOL; (* Counter reached Limit *)
    CV : WORD; (* Current Counter Value *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | `CV >= PV` 时为 TRUE，否则为 FALSE |
| `CV` | `WORD` | 当前计数值，范围 0–65535 |

### VAR_IN_OUT

无。

## 3. 行为说明

每个 PLC 周期 FB 被调用时按"复位优先、其次边沿、最后比较"三个阶段依次处理：先看复位输入是否有效，有效则强制把计数变量清零并屏蔽本周期的计数边沿；其次比较 `CU` 当前值与上一周期保存的值，若发生 FALSE→TRUE 的跃迁则把 `CV` 加 1（注意是边沿不是电平）；最后用 `CV >= PV` 判断决定输出 `Q`。整个过程不存在"减"的语义——CTU 单方向只向上走，需要双向请用 CTUD。计数变量 `CV` 是 16 位无符号，**达 65535 后再来 CU 上升沿的行为 PDF / InfoSys 均未明确（⚠️ 待官方确认；不同实现可能回卷为 0 或饱和在 65535）**——业务代码不要依赖这一行为。FB 实例的 CV 不是 retain 型变量，断电重启会清零。

**完整状态机**（每个 PLC 周期调用 FB 一次时）：

1. **`RESET = TRUE`**：无论 `CU` 状态如何，本周期 `CV := 0`，`Q := FALSE`；RESET 在 IEC 标准中**优先于 CU**
2. **`RESET = FALSE` 且 `CU` 上升沿**（CU 上一周期 FALSE、本周期 TRUE）：`CV := CV + 1`（⚠️ `CV` 已达 65535 时的后续行为 PDF / InfoSys 均未明确）
3. **`RESET = FALSE` 且 `CU` 无上升沿**（CU 持续 TRUE 或持续 FALSE）：`CV` 不变
4. **每周期末**：`Q := (CV >= PV)`

**关键语义**：

- **边沿触发而非电平触发**：把 `CU` 永久接在 TRUE 上，计数器只会在第一次进入 TRUE 时加 1 一次，之后不会持续累加。要让计数器持续走，必须让 `CU` 反复发生 FALSE → TRUE 的边沿（典型做法是接传感器脉冲或 `R_TRIG` 输出）。
- **`Q` 是电平比较**：到达 `PV` 后只要不复位 `Q` 一直保持 TRUE；继续递增 `CV` 超过 `PV`（如 PV=10，CV=15）`Q` 仍为 TRUE。
- **`RESET` 优先级最高**：与 `CU` 同周期上升时，`RESET` 赢——`CV` 归零，本次 CU 边沿丢失。
- **首次扫描 `CV = 0`、`Q = FALSE`**：FB 实例的 CV 不是 retain，断电重启清零。

## 4. 错误码 / 返回值

`CTU` 是标准计数器，**无错误码、无 HRESULT**。状态通过 `Q`（达到门限）与 `CV`（当前值）反映。`PV = 0` 时 `CV >= PV` 永远为 TRUE（计数器一上电 Q 就是 TRUE）。

## 5. 使用注意 / 常见坑

- **`CU` 必须是脉冲不是电平**：常见错误是把传感器信号直接长接到 `CU`，结果只数到 1。要么用脉冲信号，要么前面串 `R_TRIG`：
  ```
  fbRTrig(CLK := bSensor);
  fbCTU(CU := fbRTrig.Q, RESET := bReset, PV := 100);
  ```
- **`CV` 是 WORD 上限 65535**：达到 65535 后的行为 PDF / InfoSys 均未明确（⚠️ 待官方确认；不同实现可能回卷为 0 或饱和）。业务上想数 100 万件务必自己用 UDINT 累加：`IF fbRTrig.Q THEN nProductCount := nProductCount + 1; END_IF`，不要依赖 CTU 的回卷/饱和行为。
- **RESET 和 CU 同周期来时 RESET 赢**：要数复位后的第一次边沿必须等 RESET 回 FALSE 之后才送 CU 上升沿。
- **PV 改值可让 `Q` 即时翻转**：运行中把 PV 从 100 改成 5，如果当前 CV=20，`Q` 立即 TRUE。这可用作"门限动态调整"。
- **断电不保持**：FB 实例的 CV 不是 RETAIN；要跨断电累计必须自己声明 `nCount : UDINT;` 加 `{attribute 'TcRetain'}` 或者用 PERSISTENT。
- **`Q` 到达后不会自动清零**：必须显式 `RESET := TRUE` 一拍才能让 `Q` 回 FALSE。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CTU.xml`](../examples/P_Demo_CTU.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：传送带上每过一个工件，光电传感器输出一个上升沿；累计满 100 件后输出
//       "满箱"信号通知打包工位换箱子，操作员换完按"换箱完成"复位计数器。
PROGRAM P_Demo_CTU
VAR
    fbBoxCounter      : CTU;
    bProductSensor    : BOOL;             // 光电传感器（每个工件一个上升沿）
    bBoxChangedAck    : BOOL;             // 操作员"换箱完成"按钮
    nBoxCapacity      : WORD := 100;      // 满箱产品数
    bBoxFull          : BOOL;             // 满箱信号输出
    nCurrentCount     : WORD;             // 当前箱内已数件数（监视用）
END_VAR

fbBoxCounter(
    CU    := bProductSensor,
    RESET := bBoxChangedAck,
    PV    := nBoxCapacity,
    Q     => bBoxFull,
    CV    => nCurrentCount
);
```

## 7. 业务场景与实际价值

- **场景**：传送带上产品计数（满箱报警）、按钮按下次数统计（设备寿命管理）、报警发生计数（重复 5 次后升级为严重故障）、批次生产数量统计、工序步骤计数。
- **价值**：1 次调用拿到"边沿检测 + 自加 + 门限比较 + 复位"完整状态机，省去手写约 6-8 行（含上一周期值保存）。IEC 标准，跨控制器移植无需改逻辑。
- **替代方案对比**：
  - **手写 + R_TRIG**：能做但要管理边缘状态保存，约 8 行
  - **`CTUD`**：可上可下计数器，功能更全但接口复杂；只数上行用 CTU 更简洁
  - **手写 UDINT 累加**：突破 WORD 上限场景必用，但仍可在 CTU 的 Q 边沿处递增 UDINT
  - **本 FB**：上行计数标准块，IEC 跨平台

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §3.2.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74400779.html
- **相关 FB**：`CTD`（向下计数）、`CTUD`（上下双向）、`R_TRIG`（边沿检测，常配合 CTU 使用）
