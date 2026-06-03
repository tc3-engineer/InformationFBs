# FB_BACnet_Loop

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Control Loop` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_Loop.TcPOU`](../examples/P_Demo_FB_BACnet_Loop.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Control Loop」对象类型(BACnet Object_Type = 8 / Loop)。把一个 PI / PID 控制回路的参数(P / I / D / Bias / Setpoint / Output / Action 等)以 BACnet 标准属性暴露给 BMS,允许 BMS 在线整定参数。本库 Loop 对象的实际 PID 算法由 `Tc3_BA2_Common` 库的 FB_BA_PIDCtrl 实现,本对象只是把 PID 的输入 / 参数 / 输出绑到 BACnet 标准属性。本库提供两个变体:`FB_BACnet_Loop`(setpoint/process/output 都用 FB 内部 REAL 变量)与`FB_BACnet_Loop_Ref`(也写作 FB_BACnet_LoopRef,这三个量通过 ObjectPropertyReference 引用别的 AV/AI/AO 对象,让 BMS 也能看到 setpoint 与 process value 作为独立 BACnet 对象,见 PDF §6.2.6 + §9.7)。

## 2. 接口定义

> PDF §6.1.1 / §6.1.2 把所有对象 FB 统一用对象类型表 + 后缀规则描述,**未**针对单个 FB 列 `VAR_INPUT` / `VAR_OUTPUT` 区;以下表把 PDF/InfoSys 在 §6.1.1 / §6.1.2 / §9.x 提及的成员按 BACnet 标准属性分类整理。

### VAR_INPUT

```iecst
VAR_INPUT
END_VAR
```

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_INPUT` 区;成员见下表。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
END_VAR
```

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_OUTPUT` 区;运行状态以 FB 成员形式暴露,见下表。

### VAR_IN_OUT

无。

### 关键属性 / 成员(分组)

| 类别 | FB 成员 | 类型 | 含义 |
|---|---|---|---|
| 基本信息 | `iParent` / `sObjectName` / `sDescription` / `bEn` | `I_BACnet_View` / `STRING(*)` / `BOOL` | DPAD + 名称 + 使能 |
| PID 参数 | `fProportionalConstant` / `fIntegralConstant` / `fDerivativeConstant` / `fBias` | `REAL` | Proportional_Constant / Integral_Constant / Derivative_Constant / Bias |
| 输出单位 | `eOutputUnit` | `E_BA_Unit` | Output_Units(典型 `eOther_Percent`) |
| 控制动作方向 | `eAction` | `E_BA_Action` | Action(`eDirect` / `eReverse`,Reverse 适合制冷:误差正向时输出反向降) |
| 内部变量(Loop 基础类) | `fSetpoint` / `fCtrlVal` / `fOutput` | `REAL` | 内部 setpoint / process value / output |
| 外部引用(Loop_Ref) | `stSetpointReference` / `stControlledVariableReference` / `stManipulatedVariableReference` | `ST_BACnet_ObjectPropertyReference` | Setpoint_Reference / Controlled_Variable_Reference / Manipulated_Variable_Reference(用 `F_BACnet_Reference(...)` 帮助函数构造) |
| 上下限 | `fMaximumOutput` / `fMinimumOutput` | `REAL` | Maximum_Output / Minimum_Output |

### 后缀变体(PDF §6.1.2)

| 变体 | 增/删的成员 | 用途 |
|---|---|---|
| `FB_BACnet_Loop` | — | Setpoint / Process / Output 用 FB 内部 REAL,适合简单回路 |
| `FB_BACnet_Loop_Ref` / `FB_BACnet_LoopRef` | 用 stSetpointReference / stControlledVariableReference / stManipulatedVariableReference 引用别的 AV/AI/AO 对象 | 让 BMS 看到 setpoint/process/output 作为独立 BACnet 对象(增加 3 个 BACnet 对象但 BMS 操作 / 趋势可视化方便) |

## 3. 行为说明

FB_BACnet_Loop 每周期调用一次。基础类下,PLC 把当前过程值送到 `fCtrlVar`(注意:variable 名是 fCtrlVar,见 PDF §9.7 示例),回路内部按 `fSetpoint` 与 PID 参数算输出送到 `fOutput`(可读),PLC 端再把 fOutput 写到物理输出端子。`Loop_Ref` 下,PLC 不直接喂 fCtrlVar,而是通过 stControlledVariableReference 把外部 AI 对象的 PresentValue 作为过程值;setpoint 和 output 同理引用外部 AV/AO 对象。stack 在 PID 调用时自动用 stack 内的引用解算后写到目标对象。`eAction := eReverse` 时,误差(SP - PV)正向触发输出降低,适合「制冷:温度高于设定点要开冷却」;`eDirect` 适合「加热:温度低于设定点要开加热」。Loop 对象自身不发报警,但可通过 EE 监测 fCtrlVal / fOutput 做超调报警。

## 4. 错误码 / 返回值

无返回值。⚠️ PDF + InfoSys 未列具体 error 常量。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **PDF 中 LoopRef 引脚名同时使用 `FB_BACnet_Loop_Ref` 与 `FB_BACnet_LoopRef`**:两者为同一 FB(命名争议,版本迭代痕迹);用哪个 token 编译都通过,推荐 `FB_BACnet_Loop_Ref`(下划线版,与 PDF §6.1 表一致)。
- **PID 参数从积分时间 Ti(秒)转换**:`fIntegralConstant := 180` 表示积分时间常数 180 秒(即 1/3 分钟积分);不要直接传 Ki(增益)否则物理量不对。
- **Loop_Ref 要计算被引用对象的优先级槽位**:PID 输出写下游 AO 时占用槽位 16(默认),会与 BMS 的手动覆盖冲突;实际工程中通常用 _5P 变体 + 把 PID 写到 Critical 优先级。
- **`eAction` 写反等于失稳**:制冷接 `eDirect` 时温度越高输出越大,加重过热 → 系统发散。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_Loop.TcPOU`](../examples/P_Demo_FB_BACnet_Loop.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_Loop
VAR
    fbLoopInternal : FB_BACnet_Loop := (
        bEn := TRUE,
        sDescription := 'Loop using internal control parameters',
        eOutputUnit := E_BA_Unit.eOther_Percent,
        eAction := E_BA_Action.eReverse,           // 制冷:温度↑ → 阀位↓
        fProportionalConstant := 5.0,
        fIntegralConstant := 180,                  // 积分时间 180 秒
        fSetpoint := 20.0);
    fCtrlVal : REAL := 18.0;                       // 过程值,PLC 喂入
END_VAR

fbLoopInternal.fCtrlVar := fCtrlVal;
fbLoopInternal();
```

## 7. 业务场景与实际价值

- **场景**:房间温度 PID 控温 — 每个房间一只 PT1000 温度传感器 + 一只 0..10V 阀门,运维想在 BMS 上在线整定 PID(房间负载随季节变化,需要调 P 和 Ti)。
- **价值**:Loop 对象把 PID 参数 BACnet 标准化暴露,运维在 BMS 上直接调参,不用每次登录 PLC 改代码;Loop_Ref 变体进一步让 setpoint / process / output 都作为独立 BACnet 对象可见,方便做 setpoint schedule 和 process value trend log。
- **替代方案对比**:用 Tc3_Controller 内置 PID:Beckhoff 自家,BMS 看不到参数;用 Loop 标准对象,跨厂商 BMS 一致。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1(Loop / Loop_Ref = Control Loop)、§6.2.6(Control Loops 综述)、§9.7(完整 Loop / Loop_Ref 示例),依赖 Tc3_BA2_Common 库的 FB_BA_PIDCtrl
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_AI`(process value 源)、`FB_BACnet_AV` / `AV_Setp`(setpoint 源)、`FB_BACnet_AO` / `AO_5P`(output 目标);`F_BACnet_Reference(...)` 用来构造 ObjectPropertyReference
