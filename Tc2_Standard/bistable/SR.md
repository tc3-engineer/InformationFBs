# SR

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Bistable` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74396043.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_SR.TcPOU`](../examples/P_Demo_SR.TcPOU) |

---

## 1. 功能简述

`SR` 是 **IEC 61131-3 标准块**之一，**SET 主导双稳态触发器**（SR flip-flop）。与 `RS` 镜像：`SET1` 与 `RESET` 同时有效时 **SET1 赢**（输出被强制为 TRUE）。这是报警闩锁场景的标准选择——故障来了即闩锁，操作员按住"确认"按钮也无法让闩锁解除直到故障真正消失。

行为等价于布尔方程 `Q1 := (NOT RESET AND Q1) OR SET1;`。带 `1` 后缀的输入（`SET1`）表示优先输入。

典型用途：故障报警闩锁（一旦报警就锁住直到 SET1 自然回 FALSE）、消防联锁（火警信号一来必须置位且按消音键无效）、生产许可（许可信号必须能赢过持续的中断信号）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    SET1  : BOOL;
    RESET : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `SET1` | `BOOL` | 置位输入（**优先**）。有效时强制 `Q1 := TRUE`，覆盖 `RESET` |
| `RESET` | `BOOL` | 复位输入。有效时 `Q1` 清回 FALSE（前提是 `SET1` 未有效） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q1 : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q1` | `BOOL` | 锁存输出。`SET1` 有效置 TRUE；`RESET` 有效且 `SET1` 未有效置 FALSE；都无效时保持 |

### VAR_IN_OUT

无。

## 3. 行为说明

每个 PLC 周期 FB 执行内部赋值方程 `Q1 := (NOT RESET AND Q1) OR SET1;`。按这个方程，本周期 `Q1` 的新值是"取反的 RESET 与上一周期 Q1 的与"再或上"本周期 SET1"。与 RS 同样是组合逻辑表达式不是边沿触发——`SET1` 持续 TRUE 即可持续保持置位指令，无需先回落再上升。

真值表：

| `SET1` | `RESET` | `Q1`（上一周期） | `Q1`（本周期） |
|---|---|---|---|
| FALSE | FALSE | FALSE | FALSE |
| FALSE | FALSE | TRUE  | TRUE（保持）|
| FALSE | TRUE  | × | FALSE（复位）|
| TRUE  | × | × | TRUE（置位主导）|

`×` 表示任意值。**SET1 优先于 RESET**。

⚠️ **PDF 文档存在自相矛盾的描述**：PDF Inputs 表把 `SET1` 与 `RESET` 都描述为 "on a rising edge"（上升沿触发），但同一节后面的"Internal implementation"给出的等价方程 `Q1 := (NOT RESET AND Q1) OR SET1;` 是组合逻辑式没有边沿检测。InfoSys topic 74396043.html 完全沿用同样矛盾的描述。实测 TwinCAT 行为以**组合逻辑等价方程**为准（电平驱动）。这是和 RS 完全对称的 PDF 描述问题，已上报 Beckhoff（⚠️ 待人工确认）。

## 4. 错误码 / 返回值

`SR` 是纯逻辑双稳态，**无错误码、无 HRESULT**。

## 5. 使用注意 / 常见坑

- **SR vs RS 选哪个**：报警闩锁、消防联锁、生产许可等"启动信号必须赢过持续复位"的场景用 SR；安全相关、急停一律用 RS。**两者选错会出人命**——SR 用在急停场景下，急停按住时启动按钮还能把设备启起来。
- **不要用 SR 实现安全急停**。本 FB 是普通工艺逻辑，不是安全等级电路；安全场景必用 RS + 硬接线 TwinSAFE。
- **报警闩锁的典型用法**：`SET1 := bTempTooHigh; RESET := bOperatorAck;`——温度一过 SET1 锁，操作员确认后 Q1 才清零。但如果**确认期间温度仍然超**（SET1 仍为 TRUE），SET1 赢，Q1 保持 TRUE，操作员无法清除——这是设计意图。
- **PDF 双重描述歧义见 §3**：电平驱动而非边沿驱动。（工程经验补充）
- **首次扫描 Q1 = FALSE**：FB 实例非 retain；要跨断电保持业务侧的报警状态必须自己用 PERSISTENT 变量。
- **PLC 任务周期决定响应延迟**：1-10 ms 是常见任务周期，业务上别假设瞬时。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SR.TcPOU`](../examples/P_Demo_SR.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：温度过高报警闩锁。温度传感器读数超过 80°C 时报警位被闩锁置 TRUE；
//       操作员可以按"确认"按钮清除报警——但如果温度仍然超，确认无效（SET1 赢）。
PROGRAM P_Demo_SR
VAR
    fbAlarmLatch    : SR;
    bTempOverLimit  : BOOL;        // 温度超限即时信号
    bOperatorAck    : BOOL;        // 操作员确认按钮
    bAlarmLatched   : BOOL;        // 闩锁后的报警位
END_VAR

fbAlarmLatch(
    SET1  := bTempOverLimit,
    RESET := bOperatorAck,
    Q1    => bAlarmLatched
);

// bAlarmLatched 一旦置 TRUE 即闩锁，温度回落不会自动清除
// 必须 bOperatorAck := TRUE 并且 bTempOverLimit = FALSE 才能清除
// 若 bTempOverLimit 仍 TRUE，按 bOperatorAck 无效（SET1 赢）
```

## 7. 业务场景与实际价值

- **场景**：报警闩锁（一过即锁，必须双重条件清除）、消防/烟雾联锁、生产工艺许可信号（许可来了不许被外界中断信号取消）。
- **价值**：与 RS 同样的简洁封装，方向相反；选对一个比写好 50 行业务逻辑都重要。
- **替代方案对比**：
  - **手写**：`Q := (NOT R AND Q) OR S` 一行可写但易被改坏
  - **`RS`**：相反方向，业务场景错配可能出事故
  - **本 FB**：报警闩锁标准

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §3.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74396043.html
- **相关 FB**：`RS`（RESET 主导，镜像）、`R_TRIG`/`F_TRIG`、TwinSAFE 安全 FB
