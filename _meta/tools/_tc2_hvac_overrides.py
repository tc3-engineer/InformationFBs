"""Per-FB hand-written prose overrides for the most commonly-used Tc2_HVAC FBs.

Loaded by _tc2_hvac_batch.py. Each key is an FB name; each value is a dict
that gets merged into the spec passed to emit_doc. Supported keys:

    brief, behavior, scene, value, alternatives,
    cautions (list[str]),
    related (list[str]),
    errors (list[tuple[str, str, str]]),  # (output_or_code, meaning, fix)
    error_intro (str),
    desc_in / desc_out / desc_io (dict[str, str]),
    example_vars (str),  # raw IEC ST decl body (4-space indent)
    example_st (str),    # raw IEC ST implementation body
"""
from __future__ import annotations

EXTRA_OVERRIDES: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# FB_HVAC2PointActuator — high-quality hand-written override (exemplar)
# ---------------------------------------------------------------------------
EXTRA_OVERRIDES["FB_HVAC2PointActuator"] = {
    "brief": (
        "用于控制**两点式（开 / 关）阀门或两点式风阀**。FB 接收数字开关命令（`bIn`），"
        "结合开 / 关到位反馈、控制电压、手动 / 紧急开关与运行模式枚举进行联锁判断后驱动 `bOut`；"
        "同时按可配置行程时间 `tStrokeTime` 监测到位开关，超时仍未到位即在 `bErrorLimitSwitch` 报错。"
        "提供可选的持久化存储（`eDataSecurityType`）让 IN_OUT 变量在断电后保留。"
    ),
    "behavior": (
        "上电后 FB 等待 `bEnable := TRUE` 才进入工作态；未使能时输出 `bOut` 强制 FALSE，阀门 / 风阀保持关位。"
        "进入工作态后按 `eCtrlModeActuator` 决定数据源：Auto_BMS / Auto_OP 模式跟随 `bIn` 自动控制；"
        "Open_BMS / Open_OP 强制开（`bOut := TRUE`）；Close_BMS / Close_OP 强制关（`bOut := FALSE`）；"
        "BMS（Building Management System）来自上位机命令通道，OP（Operator Panel）来自就地控制面板。"
        "`bManSwitch` 与 `bCtrlVoltage` 为最高优先级硬件联锁——只要其中之一为 FALSE，"
        "`bOut` 立即被拉低进入安全态。到位监测开关 `bEnableLimitSwitch` 启用时，FB 在每次驱动命令变化后"
        "启动内部倒计时 `tStrokeTime`；时限内若 `bLimitSwitchClose` 或 `bLimitSwitchOpen` 与命令方向匹配则正常，"
        "否则置位 `bErrorLimitSwitch`。任何故障位必须由 `bReset` 上升沿手动复位。"
        "`bSetDefault` 上升沿一次性把持久量 `bEnableLimitSwitch`、`tStrokeTime` 复位为出厂默认。"
        "`eDataSecurityType` 选 Persistent 时所有 VAR_IN_OUT 在变化的瞬间写入闪存（需配合 `FB_HVACPersistentDataHandling` 在主任务循环调用）。"
    ),
    "scene": (
        "新风机组（AHU）冷热水盘管的两通 / 二位电动阀控制：上位机给开 / 关命令（`bIn`），"
        "现场控制柜内有 24V 手 / 自切换开关（`bManSwitch`）和 24V 控制电压监视继电器（`bCtrlVoltage`），"
        "阀体自带全开 / 全关行程开关反馈（`bLimitSwitchOpen` / `bLimitSwitchClose`），"
        "并且要求所有手动 / 行程时间等参数掉电不丢。"
    ),
    "value": (
        "本 FB 把「自动 / 手动模式仲裁、控制电压联锁、到位监测、行程时间故障检测、参数持久化」"
        "5 块功能一次集成；手写至少 80-120 行 ST 才能等价实现。状态字 `byState` 直接对接 HMI 排错，"
        "避免每路阀门各自实现一套联锁逻辑导致风格不统一。"
    ),
    "alternatives": (
        "**手写 ST**：得自己实现状态机 + 持久化 + 到位监测，工程量大且容易漏；"
        "**FB_HVAC3PointActuator**：三点（开 / 关 / 停）阀适用，含位置反馈，但对二位阀过度设计；"
        "**纯 BOOL 输出**：最简陋，无监测无联锁，不适合带反馈的执行器。"
    ),
    "related": ["FB_HVAC3PointActuator", "FB_HVACPersistentDataHandling", "E_HVAC2PointActuatorMode", "E_HVACDataSecurityType"],
    "desc_in": {
        "bIn": "自动模式下的命令：FALSE = 关、TRUE = 开。",
        "eCtrlModeActuator": (
            "运行模式枚举：Auto_BMS / Open_BMS / Close_BMS / Auto_OP / Open_OP / Close_OP。"
            "BMS 来自上位机命令，OP 来自就地操作面板。"
        ),
        "bLimitSwitchClose": "「全关」到位反馈：阀门 / 风阀完全关到位时该引脚 TRUE。",
        "bLimitSwitchOpen": "「全开」到位反馈：阀门 / 风阀完全开到位时该引脚 TRUE。",
    },
    "desc_out": {
        "bOut": "驱动输出：FALSE = 关阀 / 关风阀，TRUE = 开阀 / 开风阀。",
        "byState": (
            "状态字（按位）：bit0 = Enable、bit1 = Manual Switch、bit2 = Enable Feedback Control、"
            "bit3 = Control Voltage、bit4 = Reset、bit5 = bOut。用于上位机统一回读各联锁状态。"
        ),
        "eStateModeActuator": "当前实际运行模式回显（与 `eCtrlModeActuator` 经内部仲裁后的结果可能不同）。",
        "bErrorLimitSwitch": "到位监测错误：在 `tStrokeTime` 行程时间内未检测到任何到位开关。`bReset` 上升沿清错。",
    },
    "desc_io": {
        "bEnableLimitSwitch": "持久量：是否启用到位反馈监测。TRUE = 启用（无到位反馈则报错）；FALSE = 不监测。",
        "tStrokeTime": "持久量：行程时间，全关 → 全开（或反向）的最长时间。范围 0..3600 s，默认 T#200S。超时未到位即 `bErrorLimitSwitch`。",
    },
    "cautions": [
        "`eDataSecurityType` 选 `Persistent` 必须同时在主程序中实例化 `FB_HVACPersistentDataHandling` 并周期调用，否则 FB 内部不会释放写盘资源，IN_OUT 变化不会持久化。",
        "切勿把循环变化的变量直接连到 VAR_IN_OUT 引脚——每次变化都触发一次闪存写入，会导致 NAND / NOR 寿命短期内耗尽。仅在 HMI 触发的参数变更场景使用 Persistent。（PDF NOTICE 明示）",
        "`bManSwitch` 在工程实践中一定要接现场控制柜的紧急复位 / 手动开关物理触点；硬件信号才能真正切到安全态。若用软件 BOOL 模拟则丢失硬件联锁的作用。（工程经验补充）",
        "`tStrokeTime` 建议比阀厂家行程时间表数据再多 50%；现场遇到风阀低温卡涩、长期氧化都会让实际开关时间变长，过紧的 `tStrokeTime` 会频繁误报错。（工程经验补充）",
        "`bCtrlVoltage` 应接控制电压检测继电器的辅助触点（如 24V 监视继电器）。这样市电瞬断或控制器供电故障时 FB 立刻进入安全态。（工程经验补充）",
    ],
    "example_vars": (
        "    // ---- 被演示 FB 实例 ----\n"
        "    fb2PtValve              : FB_HVAC2PointActuator;            // 二位阀控制 FB\n\n"
        "    // ---- 工艺信号：新风机组冷盘管二位阀 ----\n"
        "    bUnitEnable             : BOOL := FALSE;                    // 机组总使能（HMI 写 TRUE）\n"
        "    bValveOpenCmd           : BOOL := FALSE;                    // 上位机开阀命令（在线写 TRUE 触发开阀）\n"
        "    eValveMode              : E_HVAC2PointActuatorMode\n"
        "                              := E_HVAC2PointActuatorMode.eHVAC2PointActuatorMode_Auto_BMS;\n"
        "    // ---- 硬件联锁信号（接 DI 端子） ----\n"
        "    bManualSwitchOk         : BOOL := TRUE;                     // 24V 手 / 自切到自动\n"
        "    bClosedFeedback         : BOOL := TRUE;                     // 初始：全关到位\n"
        "    bOpenedFeedback         : BOOL := FALSE;                    // 初始：未到全开\n"
        "    bCtrlVoltageOk          : BOOL := TRUE;                     // 控制电压 24V OK\n"
        "    bAcknowledgeFault       : BOOL := FALSE;                    // 故障复位按钮\n\n"
        "    // ---- 持久化参数（首次上电用 bSetDefault 写默认） ----\n"
        "    bSetDefaultParams       : BOOL := FALSE;                    // 调试期间用 R_TRIG 触发一次\n"
        "    bEnableFeedbackMonitor  : BOOL := TRUE;                     // 启用到位监测\n"
        "    tValveStrokeTime        : TIME := T#90S;                    // 二位阀典型 60-120s\n\n"
        "    // ---- 输出（在线 monitor） ----\n"
        "    bValveDrive             : BOOL;                              // 给阀门的 24V DO 信号\n"
        "    byValveStateBits        : BYTE;                              // 状态字\n"
        "    eValveCurrentMode       : E_HVAC2PointActuatorMode;\n"
        "    bStrokeTimeError        : BOOL;                              // 到位超时\n"
        "    bParameterError         : BOOL;                              // 参数非法"
    ),
    "example_st": (
        "// =============================================================================\n"
        "// Tc2_HVAC.FB_HVAC2PointActuator 演示程序\n"
        "// =============================================================================\n"
        "// 场景：新风机组（AHU）冷水盘管二位电动阀。机组接收上位机开 / 关命令；现场配 24V\n"
        "//       手 / 自切换开关、控制电压监视继电器、阀门带全开 / 全关行程开关反馈。\n"
        "//\n"
        "// 价值：本 FB 一次性提供：自动 / 手动模式仲裁 + 硬件联锁 + 到位监测 + 故障锁存 + 参数\n"
        "//       持久化。对比手写：少写约 80-120 行状态机；联锁优先级（Manual / CtrlVoltage\n"
        "//       高于 BMS 命令）由 FB 内部保证，不会被误改。\n"
        "//\n"
        "// 验证步骤：\n"
        "//   1. 右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选本 .TcPOU 文件\n"
        "//   2. 引用 Tc2_HVAC（References → Add library）\n"
        "//   3. 编译 → 登录 → 运行\n"
        "//   4. 在线写 bSetDefaultParams := TRUE → 下一周期写 FALSE（边沿触发一次默认值写入）\n"
        "//   5. 在线写 bUnitEnable := TRUE；bValveOpenCmd := TRUE\n"
        "//      → 观察 bValveDrive 应变 TRUE\n"
        "//      → byValveStateBits 应显示 bit0 = bit5 = 1（Enable 与 bOut 都置位）\n"
        "//   6. 手动模拟硬件联锁断开：把 bCtrlVoltageOk 写 FALSE\n"
        "//      → bValveDrive 应立即变 FALSE（控制电压联锁优先）\n"
        "//   7. 模拟到位超时：保持 bValveOpenCmd = TRUE 但 bOpenedFeedback 保持 FALSE\n"
        "//      → 经过 tValveStrokeTime（90s）后 bStrokeTimeError 应变 TRUE\n"
        "//      → 给 bAcknowledgeFault 一个 FALSE→TRUE→FALSE 脉冲，bStrokeTimeError 复位\n"
        "// =============================================================================\n"
        "\n"
        "// 持久化模式：本例子用 Idle，避免反复写盘。生产环境改 eHVACDataSecurityType_Persistent\n"
        "// 并务必在主程序里实例化 FB_HVACPersistentDataHandling 周期调用。\n"
        "fb2PtValve(\n"
        "    eDataSecurityType   := E_HVACDataSecurityType.eHVACDataSecurityType_Idle,\n"
        "    bSetDefault         := bSetDefaultParams,\n"
        "    bEnable             := bUnitEnable,\n"
        "    bIn                 := bValveOpenCmd,\n"
        "    eCtrlModeActuator   := eValveMode,\n"
        "    bManSwitch          := bManualSwitchOk,\n"
        "    bLimitSwitchClose   := bClosedFeedback,\n"
        "    bLimitSwitchOpen    := bOpenedFeedback,\n"
        "    bCtrlVoltage        := bCtrlVoltageOk,\n"
        "    bReset              := bAcknowledgeFault,\n"
        "    bEnableLimitSwitch  := bEnableFeedbackMonitor,\n"
        "    tStrokeTime         := tValveStrokeTime,\n"
        "    bOut                => bValveDrive,\n"
        "    byState             => byValveStateBits,\n"
        "    eStateModeActuator  => eValveCurrentMode,\n"
        "    bErrorLimitSwitch   => bStrokeTimeError,\n"
        "    bInvalidParameter   => bParameterError\n"
        ");"
    ),
}


# ---------------------------------------------------------------------------
# FB_HVACPIDCtrl — the universal HVAC PID controller (hand-written)
# ---------------------------------------------------------------------------
EXTRA_OVERRIDES["FB_HVACPIDCtrl"] = {
    "brief": (
        "通用 HVAC PID 控制器，专为暖通空调中的连续过程（温度 / 压力 / 流量 / 湿度）设计。"
        "内部由 P + I + D 三部分构成（结构可在 P1ID / PID 两种串并联结构间切换），"
        "内置 anti-reset windup（积分饱和抑制）、输出限幅、反向控制方向、运行中同步等楼宇控制必备能力。"
        "可以与同库 `FB_HVACPIDCtrl_Ex` 配合（后者增加序列控制接口）或与执行器 FB 直接串联。"
    ),
    "scene": (
        "AHU 送风温度 PID 控制：盘管出水阀（0-100%）由本 FB 输出 `rY` 驱动，反馈来自送风温度传感器 `rX`，"
        "设定值 `rW` 来自房间温度控制器；要求温度稳定 ±0.5 ℃、阀位变化平滑（避免执行器频繁动作）。"
    ),
    "value": (
        "替代手写 PID：包含 anti-reset windup（阀全开 / 全闭后 I 部分不再累加，避免控制权切换时的"
        "「积分爆炸」）、bSync 平滑模式切换、反向控制（加热 vs 制冷一行代码切换）、"
        "持久化参数。手写至少 50-80 行 ST 而且容易漏掉 anti-reset windup。"
    ),
    "alternatives": (
        "**Tc2_ControllerToolbox.FB_CTRL_PID**：通用 PID，但无 HVAC 优化（无 anti-windup HVAC 风格、"
        "命名约定不同）；**Tc3_BA2_Common.FB_BA_PIDCtrl**：BA 2.0 风格，针对楼宇但与 Tc2_HVAC 系列枚举不互通；"
        "**本 FB**：与 Tc2_HVAC 全库统一约定，最低集成成本。"
    ),
    "related": ["FB_HVACPIDCtrl_Ex", "FB_HVAC2PointCtrl", "FB_HVACI_CtrlStep", "FB_HVACPIDCooling",
                "FB_HVACBasicSequenceCtrl", "E_HVACCtrlMode"],
}


# ---------------------------------------------------------------------------
# FB_HVACPersistentDataHandling — system FB for persistent storage
# ---------------------------------------------------------------------------
EXTRA_OVERRIDES["FB_HVACPersistentDataHandling"] = {
    "brief": (
        "**Tc2_HVAC 库的持久化基础设施 FB**。所有 `eDataSecurityType := Persistent` 的 FB 在内部"
        "把要持久化的变量入队，本 FB 在主循环里轮询出队并写入闪存（`.bootdata-old` 备份文件）；"
        "上电时自动从备份文件回读。**必须在主程序中实例化一次并周期调用**，否则其它 FB 的写盘队列不会被消费。"
    ),
    "scene": (
        "Tc2_HVAC 工程的全局基础架构：所有应用层 FB（执行器 / 控制器 / 设定值模块等）都依赖本 FB 把"
        "用户在 HMI 上设的参数（PID 增益、行程时间、限值等）写盘保留，断电不丢、上电自动恢复。"
    ),
    "value": (
        "**没有这个 FB，整个 Tc2_HVAC 体系的持久化机制都失效**：HMI 改 PID 参数不会落盘、断电重启所有参数归零。"
        "本 FB 自动处理：①周期写盘 ②双备份切换 ③写入冲突队列管理 ④断电瞬间数据完整性。"
    ),
    "alternatives": (
        "**直接用 TwinCAT PERSISTENT 关键字**：能保留变量但没有双备份，断电瞬间正好在写盘时数据可能损坏；"
        "**手写 NOVRAM 操作**：得自己处理写入 / 校验 / 切备份，工程量大；"
        "**本 FB**：Tc2_HVAC 全库内置约定，所有应用层 FB 自动接入。"
    ),
    "related": ["FB_HVACNOVRAMDataHandling", "FB_HVACPersistentDataFileCopy",
                "FB_HVAC2PointActuator", "FB_HVAC3PointActuator", "FB_HVACPIDCtrl",
                "E_HVACDataSecurityType"],
    "cautions": [
        "**必须在主循环里调用本 FB**，不能放在条件分支或不同任务里。否则其它 FB 的持久化队列不会被处理。",
        "本 FB 是 Tc2_HVAC 持久化机制的**单一实例**：整个工程只允许实例化一次，多实例会导致写盘冲突。",
        "写盘时机由本 FB 自动决定（典型 1 小时一次 + 触发式），不要尝试手动强制写盘。",
        "工程下载后第一次上电要等本 FB 完成首次回读（`g_bHVACPersDataReadDone := TRUE`）后再用持久化变量。",
        "Tc2_HVAC 全库 PDF 在 VAR 区结束处不印 `END_VAR`，但实际 IEC 声明中该终止符存在。如果用 PDF 文本直接复制到 IEC 编辑器，编译器会在 VAR_INPUT / VAR_OUTPUT 段尾报「缺少 END_VAR」错误，需要手工补齐。本仓为方便阅读已在所有文档的 IEC 代码块中显式补 `END_VAR`。（工程经验补充）",
    ],
}


# ---------------------------------------------------------------------------
# F_RoundLREAL / F_RoundLREAL_EX — pure functions
# ---------------------------------------------------------------------------
EXTRA_OVERRIDES["F_RoundLREAL"] = {
    "brief": (
        "把 `LREAL` 输入舍入到小数点后 1 位（即四舍五入到 0.1）。`REAL` 数据也可作为输入（自动隐式转换）。"
        "本 FC 是**无状态纯函数**，可在任何 PRG / FB / METHOD 中按值调用。"
    ),
    "behavior": (
        "调用形如 `F_RoundLREAL(lrIN := 3.14159)` 返回 3.1。负数同样按四舍五入处理（如 -3.16 → -3.2）。"
        "本 FC 是无状态纯函数，无内部缓存、无副作用，多任务并行调用安全。"
        "适用于 HMI 显示（避免显示 22.36789012 这种过精度值）、报表数据归一化（统一小数位数）、"
        "PID 输出小数截断（避免 LREAL 全精度变化反复刷新 HMI）等场景。"
        "调用时 `lrIN` 和返回值都是 `LREAL` 双精度浮点；如果传入 `REAL` 编译器会自动隐式转换，结果保持 1 位小数精度。"
    ),
    "errors_intro": "",
    "errors": [("返回值 `LREAL`", "舍入结果，小数点后 1 位。", "正常情况下不存在错误条件；无需排错")],
    "scene": (
        "HMI 显示场景：从 PID 控制器读到的温度过程值 (22.367891 ℃) 直接显示太长，"
        "把它通过 F_RoundLREAL 归一化为 22.4 ℃ 显示更友好。"
    ),
    "value": "一行调用替代手写 `LROUND(lrIN * 10.0) / 10.0` 表达式；避免常见的舍入边界 bug。",
    "alternatives": (
        "**手写表达式 `LROUND(lrIN * 10.0) / 10.0`**：可行但容易在边界值（如 0.05 / -0.05）出错；"
        "**STRING 拼接截断**：性能低且只能用于显示；"
        "**本 FC**：编译器内置 LTRUNC + 数值常量，性能最优。"
    ),
    "related": ["F_RoundLREAL_EX"],
}

EXTRA_OVERRIDES["F_RoundLREAL_EX"] = {
    "brief": (
        "把 `LREAL` 输入舍入到指定的小数位数（0..5 位）。`REAL` 数据也可作为输入。"
        "比 `F_RoundLREAL`（固定 1 位）灵活：用 `iPrecision` 指定保留几位小数。"
        "本 FC 内部使用 `TcMath.LTRUNC`，是**无状态纯函数**。"
    ),
    "behavior": (
        "返回值为 `iPrecision` 位小数的舍入结果。`iPrecision = 0` 返回整数（`22.4 → 22`）、"
        "`iPrecision = 2` 返回两位小数（`22.4 → 22.40`）、最大支持 5 位（`22.4 → 22.40000`）。"
        "**特殊语义**：当 `lrIN < 0.1 AND lrIN ≥ 0.05` 时返回 0.1（防止零下溢）。"
        "超出 `iPrecision` 范围（< 0 或 > 5）时行为未定义，PDF 未明确，工程上应自行检验入参。"
        "本 FC 是无状态纯函数，多任务并行调用安全；典型用法是把 PID 输出 / 模拟量读数按报表精度归一化。"
    ),
    "errors_intro": "",
    "errors": [
        ("返回值 `LREAL`", "舍入到 `iPrecision` 位小数。", "正常返回，无错误"),
        ("`iPrecision` 越界（< 0 / > 5）", "PDF 未明确行为", "工程上调用前自检 `iPrecision` 在 0..5 范围"),
    ],
    "scene": "报表 / Trend 数据归一化：把不同传感器的过程值按工程报表的统一精度（2 位 / 3 位）输出。",
    "value": "一行调用替代手写 `LROUND(lrIN * 10^iPrecision) / 10^iPrecision`；自动处理零下溢边界。",
    "alternatives": "手写表达式：需要自己实现 10^iPrecision 运算（实数指数较慢）；本 FC 内部用 LTRUNC，性能最优。",
    "related": ["F_RoundLREAL"],
}


# ---------------------------------------------------------------------------
# FB_HVAC2PointCtrl — 2-point on/off controller
# ---------------------------------------------------------------------------
EXTRA_OVERRIDES["FB_HVACNOVRAM_XX"] = {
    "brief": (
        "**`XX` 是一个占位符**——本 FB 实际是 14 个同构 FB 的家族，每个对应一种基本数据类型："
        "`FB_HVACNOVRAM_Bool` / `_Byte` / `_Int` / `_Dint` / `_Udint` / `_Uint` / `_Sint` / `_Usint` / "
        "`_Word` / `_Dword` / `_Real` / `_Lreal` / `_Time`。功能：把一个用户自定义的变量（VAR_IN_OUT 中的 `bVar` / `byVar` / "
        "`iVar` 等）保存到 **NOVRAM**（非易失性 RAM）中实现掉电不丢；上电时从 NOVRAM 自动回读。"
        "PDF 以 `FB_HVACNOVRAM_BOOL` 为代表展示接口；其他类型 FB 接口完全一致，只是变量类型不同。"
    ),
    "behavior": (
        "上电时本 FB 自动从 NOVRAM 中读出 `bVar` / `byVar` 等 IN_OUT 变量的上次值；"
        "`bSetDefault = TRUE` 时把变量重新写为 `bVar_Default` 给的初始值；运行中变量改变会触发"
        "NOVRAM 写入（由全局 `FB_HVACNOVRAMDataHandling` 在主循环中实际执行写盘动作）。"
        "**必须先在主程序里实例化 `FB_HVACNOVRAMDataHandling` 一次并周期调用**，否则本 FB 入队的写盘请求不会被消费。"
        "本 FB 是 14 个同构 FB 的家族；按变量类型选用对应后缀的 FB 即可，所有变体的接口都遵循"
        "「`bSetDefault` + `<type>Var_Default` 输入 + `<type>Var` IN_OUT」三引脚模式。"
    ),
    "scene": (
        "工程中需要掉电保留的核心参数：HMI 设的 PID 增益、行程时间、限值常量等；每个参数实例化一个对应类型的 FB_HVACNOVRAM_XX，"
        "把变量接到 IN_OUT 引脚，断电不丢。"
    ),
    "value": (
        "比起手写 NOVRAM 读 / 写 / 回读 / 校验逻辑（典型 30-50 行 ST），本 FB 一行调用搞定；"
        "并且与 Tc2_HVAC 体系内的 `FB_HVACNOVRAMDataHandling` 自动协作，避免手写写盘逻辑出现的常见错误（写盘冲突、回读时机不对等）。"
    ),
    "alternatives": (
        "**直接读写 `%MD` 区指向的 NOVRAM 地址**：底层但繁琐；"
        "**TwinCAT PERSISTENT 关键字**：写在文件系统而非 NOVRAM，断电瞬间正在写时可能损坏；"
        "**本 FB 家族**：与 Tc2_HVAC 持久化基础设施一体设计，最低集成成本。"
    ),
    "related": ["FB_HVACNOVRAMDataHandling", "FB_HVACPersistent_XX", "E_HVACDataSecurityType"],
    "cautions": [
        "**必须配合 `FB_HVACNOVRAMDataHandling`** 在主程序中实例化一次并周期调用，否则写盘请求队列不会被消费。",
        "本 FB 家族有 14 个变体（每个数据类型一个）；按变量类型精确选用，不要把 `_Int` 类型 FB 接 `LREAL` 变量。",
        "NOVRAM 容量有限（典型 8 KB / 128 KB），不要把所有变量都放 NOVRAM，只放关键持久化参数。",
        "Tc2_HVAC 全库 PDF 在 VAR 区结束处不印 `END_VAR`，但实际 IEC 声明中该终止符存在。如果用 PDF 文本直接复制到 IEC 编辑器，编译器会在 VAR_INPUT / VAR_OUTPUT 段尾报「缺少 END_VAR」错误，需要手工补齐。本仓为方便阅读已在所有文档的 IEC 代码块中显式补 `END_VAR`。（工程经验补充）",
    ],
}

EXTRA_OVERRIDES["FB_HVACPersistent_XX"] = {
    "brief": (
        "**`XX` 是一个占位符**——本 FB 实际是 15+ 个同构 FB 的家族，每个对应一种基本数据类型 / 结构："
        "`FB_HVACPersistent_BOOL` / `_BYTE` / `_INT` / `_DINT` / `_UDINT` / `_UINT` / `_SINT` / `_USINT` / "
        "`_WORD` / `_DWORD` / `_REAL` / `_LREAL` / `_TIME` / `_STRING` / `_STRUCT`。"
        "功能：把一个用户自定义的变量保存到**持久化文件**（`.bootdata` / `.bootdata-old` 双备份）实现掉电不丢；上电自动回读。"
        "PDF 以 `FB_HVACPersistent_BYTE` 为代表展示接口；其他类型 FB 接口完全一致，只是变量类型不同。"
    ),
    "behavior": (
        "上电时本 FB 自动从 `.bootdata` 持久化文件中读出 IN_OUT 变量的上次值；"
        "`bSetDefault = TRUE` 时把变量重新写为 default 引脚给的初始值；运行中变量改变会触发"
        "持久化写盘（由全局 `FB_HVACPersistentDataHandling` 在主循环中实际执行）。"
        "**必须先在主程序里实例化 `FB_HVACPersistentDataHandling` 一次并周期调用**，否则本 FB 入队的写盘请求不会被消费。"
        "本 FB 是同构 FB 家族；按变量类型选用对应后缀的 FB 即可，所有变体的接口都遵循"
        "「`bSetDefault` + `<type>Var_Default` 输入 + `<type>Var` IN_OUT」三引脚模式。"
    ),
    "scene": (
        "工程中需要掉电保留的核心参数：HMI 设的 PID 增益、行程时间、限值常量等；每个参数实例化一个对应类型的 FB_HVACPersistent_XX，"
        "把变量接到 IN_OUT 引脚，断电不丢。与 NOVRAM 变体不同的是，本家族写入文件系统（容量大、不依赖 NOVRAM 硬件）。"
    ),
    "value": (
        "比起手写 PERSISTENT 变量 + 自己处理双备份切换，本 FB 一行调用搞定；与 Tc2_HVAC 体系内的 "
        "`FB_HVACPersistentDataHandling` 自动协作的双备份机制保证断电瞬间数据完整性。"
    ),
    "alternatives": (
        "**TwinCAT PERSISTENT 关键字**：能保留但没有双备份，断电瞬间写盘时数据可能损坏；"
        "**FB_HVACNOVRAM_XX 家族**：写 NOVRAM 而非文件系统，容量小但写入速度快；"
        "**本 FB 家族**：写文件系统，双备份，容量大，适合大量持久化参数。"
    ),
    "related": ["FB_HVACPersistentDataHandling", "FB_HVACNOVRAM_XX", "FB_HVACPersistentDataFileCopy", "E_HVACDataSecurityType"],
    "cautions": [
        "**必须配合 `FB_HVACPersistentDataHandling`** 在主程序中实例化一次并周期调用，否则写盘请求队列不会被消费。",
        "本 FB 家族有 15+ 个变体（每个数据类型一个）；按变量类型精确选用。",
        "持久化文件容量大但写入慢（毫秒级而非微秒级）；不要把高频变化的过程值放持久化，只放参数 / 配置。",
        "Tc2_HVAC 全库 PDF 在 VAR 区结束处不印 `END_VAR`，但实际 IEC 声明中该终止符存在。如果用 PDF 文本直接复制到 IEC 编辑器，编译器会在 VAR_INPUT / VAR_OUTPUT 段尾报「缺少 END_VAR」错误，需要手工补齐。本仓为方便阅读已在所有文档的 IEC 代码块中显式补 `END_VAR`。（工程经验补充）",
    ],
}


EXTRA_OVERRIDES["FB_HVAC2PointCtrl"] = {
    "brief": (
        "**两点（双阈值）开关控制器**。当过程值 `rX` 越过设定值 `rW` 的上 / 下阈值时输出 `bOut` 切换。"
        "上下阈值由 `fHysteresis` 滞回宽度决定（避免在设定值附近反复抖动）。"
        "适用于带滞回的简单开关型控制：风机启停、电加热分段、补给水阀开关等。"
    ),
    "scene": (
        "热水箱补给水控制：水温低于 55 ℃（设定 60 ℃ - 滞回 5 ℃）启动加热器，高于 65 ℃（60 ℃ + 滞回 5 ℃）停加热器。"
        "对应 `rW := 60.0`、`fHysteresis := 10.0`（滞回宽度，上下各占一半）。"
    ),
    "value": (
        "一行调用替代手写 `IF rX < rW - hyst/2 THEN bOut := TRUE; ELSIF rX > rW + hyst/2 THEN bOut := FALSE; END_IF`，"
        "并且自带边沿延时、模式仲裁、反向控制等楼宇必备特性。"
    ),
    "alternatives": (
        "**裸 IF/ELSIF + 单次比较**：会在 rX = rW 时抖动；"
        "**TON / TOF 配 IF 分支手写延时**：能做但 5-10 行；"
        "**本 FB**：一行调用 + HVAC 库统一约定，最低集成成本。"
    ),
    "related": ["FB_HVAC2PointActuator", "FB_HVAC2PointCtrlSequence", "FB_HVACPIDCtrl"],
}
