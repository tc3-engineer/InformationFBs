# RS

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Bistable` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74394507.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_RS.TcPOU`](../examples/P_Demo_RS.TcPOU) |

---

## 1. 功能简述

`RS` 是 **IEC 61131-3 标准块**之一，**RESET 主导双稳态触发器**（RS flip-flop）。`SET` 输入有效时把内部锁存输出 `Q1` 置 TRUE，`RESET1` 输入有效时清回 FALSE；两者同时有效时 **RESET1 赢**（输出被强制为 FALSE）。这是安全相关电路里"急停永远赢过启动"的标准选择。

行为等价于布尔方程 `Q1 := NOT RESET1 AND (Q1 OR SET);`。其中名称含 `1` 的输入（这里是 `RESET1`）按 IEC 命名约定表示"优先输入"。

典型用途：急停闩锁（按下即停、必须显式复位）、安全门联锁、互锁（一次只允许一个通道运行）、操作员按钮的"按下即生效，必须显式取消"语义。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    SET    : BOOL;
    RESET1 : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `SET` | `BOOL` | 置位输入。有效时 `Q1` 被置 TRUE（前提是 `RESET1` 未有效） |
| `RESET1` | `BOOL` | 复位输入（**优先**）。有效时强制 `Q1 := FALSE`，覆盖 `SET` |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q1 : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q1` | `BOOL` | 锁存输出。`SET` 有效（且 `RESET1` 未有效）置 TRUE；`RESET1` 有效置 FALSE；两者都无效时保持上一周期值 |

### VAR_IN_OUT

无。

## 3. 行为说明

每个 PLC 周期 FB 执行内部赋值方程 `Q1 := NOT RESET1 AND (Q1 OR SET);`。按这个方程，本周期 `Q1` 的新值由"上一周期 Q1 与本周期 SET 之或"再与"本周期 RESET1 取反"做与运算决定。这是组合逻辑表达式而不是边沿触发——`SET` 持续 TRUE 即可保持置位指令，`RESET1` 持续 TRUE 即可保持复位指令，输入不需要先回落再上升。这与 IEC 1131-3 上严格"边沿触发"语义略有出入，是 TwinCAT 的实现选择。

真值表：

| `RESET1` | `SET` | `Q1`（上一周期） | `Q1`（本周期） |
|---|---|---|---|
| FALSE | FALSE | FALSE | FALSE（无置位也无锁存）|
| FALSE | FALSE | TRUE  | TRUE（锁存保持）|
| FALSE | TRUE  | × | TRUE（置位）|
| TRUE  | × | × | FALSE（复位主导）|

`×` 表示任意值。**RESET1 优先于 SET**。

⚠️ **PDF 文档存在自相矛盾的描述**：PDF Inputs 表把 `SET` 与 `RESET1` 都描述为 "on a rising edge"（上升沿触发），但同一节后面的"Internal implementation"给出的等价方程 `Q1 := NOT RESET1 AND (Q1 OR SET);` 是组合逻辑式，没有边沿检测。InfoSys topic 74394507.html 完全沿用同样矛盾的描述。实测 TwinCAT 行为以**组合逻辑等价方程**为准（电平驱动）。PDF Inputs 表的"on a rising edge"措辞可能是早期 IEC 描述习惯遗留，**不要按字面理解**。已上报 Beckhoff（⚠️ 待人工确认 PDF 描述何时更正）。

## 4. 错误码 / 返回值

`RS` 是纯逻辑双稳态，**无错误码、无 HRESULT**。状态仅通过 `Q1` 反映。

## 5. 使用注意 / 常见坑

- **RS vs SR 选哪个**：安全相关（急停、安全门、互锁）一律用 **RS**——复位永远赢；普通报警闩锁、状态保持用 **SR**——置位永远赢。误用会导致急停按下后启动信号仍能把设备启起来——人命关天。
- **不能替代硬件安全继电器**：本 FB 只是 PLC 程序逻辑，断电 / PLC 死机时 Q1 不可控。涉及人身安全必须叠加硬接线 Safety PLC（TwinSAFE）+ 经认证的安全继电器。
- **PDF 双重描述的歧义见 §3**：把 `SET` / `RESET1` 当电平驱动用（与等价方程一致），不要相信"上升沿触发"的字面表达。（工程经验补充）
- **首次扫描 `Q1 = FALSE`**：FB 实例非 retain，断电重启 Q1 清零；需要保留状态请声明业务 BOOL 加 RETAIN/PERSISTENT 属性。
- **不要传递相同信号到 SET 和 RESET1**：会得到 `Q1 := NOT x AND (Q1 OR x)` = `(Q1 AND NOT x)`，相当于受 x 控制的"非门 + 锁存"，是错误用法。
- **PLC 任务周期决定响应延迟**：SET 在 10ms 任务里最大延迟约 10ms 才反映到 Q1，急停场景如需 ms 级响应必须把 RS 放进高优先级任务。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_RS.TcPOU`](../examples/P_Demo_RS.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：电机启动 + 急停联锁。操作员按"启动"按钮置位运行允许，按"急停"按钮
//       复位运行允许；任何时刻急停按下都立刻停机（即使操作员同时按住启动）。
PROGRAM P_Demo_RS
VAR
    fbRunInterlock    : RS;
    bStartPressed     : BOOL;       // 启动按钮（按下时 TRUE）
    bEmergencyStop    : BOOL;       // 急停按钮（按下时 TRUE = 急停触发）
    bMotorEnabled     : BOOL;       // 输出：运行允许
END_VAR

fbRunInterlock(
    SET    := bStartPressed,
    RESET1 := bEmergencyStop,
    Q1     => bMotorEnabled
);

// bMotorEnabled = TRUE 时电机才允许运行
// 即便操作员按住 bStartPressed，bEmergencyStop = TRUE 立即让 bMotorEnabled = FALSE
```

## 7. 业务场景与实际价值

- **场景**：急停闩锁（按下停止必须显式复位才能继续）、安全门联锁、单工位互锁（A 站工作时 B 站不能开）、报警闭锁（故障锁住运行许可直到操作员确认）。
- **价值**：1 次调用拿到"复位主导锁存"完整语义，逻辑明确无歧义；手写需 1 行 `Q := NOT R AND (Q OR S)` 但放在大段业务逻辑里容易被改坏，FB 形式更安全。
- **替代方案对比**：
  - **手写 `Q := NOT R AND (Q OR S)`**：可行但散落在业务代码里维护麻烦
  - **`SR`**：方向相反，安全场景一定不能用
  - **TwinSAFE 安全 FB**：硬件认证级别，人身安全场景必用
  - **本 FB**：普通工艺联锁标准选择

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §3.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74394507.html
- **相关 FB**：`SR`（SET 主导）、`R_TRIG`/`F_TRIG`（边沿，搭配做"按一次切换"）、TwinSAFE 系列安全 FB
