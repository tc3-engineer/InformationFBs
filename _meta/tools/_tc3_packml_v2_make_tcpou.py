#!/usr/bin/env python3
"""Generate all 25 P_Demo_*.TcPOU files for Tc3_PackML_V2.

This is a library-local helper (file prefixed `_tc3_packml_v2_`) per Wave-2
brief §0. It does NOT modify any shared tool. Run it from the repo root:

    python3 _meta/tools/_tc3_packml_v2_make_tcpou.py

Outputs to: Tc3_PackML_V2/examples/P_Demo_<Name>.TcPOU
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EX_DIR = ROOT / "Tc3_PackML_V2" / "examples"

_NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def gid(name: str) -> str:
    key = f"tc3-libraries-kb/Tc3_PackML_V2/P_Demo_{name}"
    return "{" + str(uuid.uuid5(_NS, key)) + "}"


# Each entry: (name, declaration_body, st_body, scenario, value, verify_steps)
# scenario/value/verify will be injected into the header comment.

ENTRIES: list[dict] = [
    # ===== INTERFACES =====
    {
        "name": "I_UnitState",
        "scenario": "演示如何在 unit FB 上实现 PackML V3 全集状态接口（19 方法），\n//       并把实例引用通过 I_UnitState 传给 PackML 状态机。",
        "value": "应用层一次性获得标准 PackML 状态分派点；中央状态机自动按 eState 调对应方法。",
        "verify": "登录后写 bGoExecute := TRUE，观察 nExecuteTickCounter 持续累加，\n//        说明 PML_StateMachine 通过 I_UnitState 引用调到了 M_Execute 钩子。\n//        切到 bGoAbort := TRUE 后 nAbortTickCounter 开始累加，M_Execute 停下。",
        "decl": """VAR
    (* 演示用：状态机持有 I_UnitState 引用，按 eState 调对应方法 *)
    fbStateMachine     : PML_StateMachine;          // 中央状态机
    fbUnit             : FB_DemoUnit_AllStates;     // 实现 I_UnitState 的工艺 FB
    ipUnit             : I_UnitState;               // 把 fbUnit 暴露为 I_UnitState 引用
    bGoExecute         : BOOL := FALSE;             // 在线置 TRUE 进入 Execute
    bGoAbort           : BOOL := FALSE;             // 在线置 TRUE 触发急停
    eCmd               : E_PMLCommand;              // 主任务向状态机注入的命令
    nExecuteTickCounter: UDINT;                     // M_Execute 被调次数（监视用）
    nAbortTickCounter  : UDINT;                     // M_Aborting 被调次数
    stSubUnitInfoRef   : ST_PMLSubUnitInfoRef;      // 子单元状态汇总，本例不用
    stOptions          : ST_PMLStateMachineOptions; // 状态机选项，PDF V1.2.4 未用
END_VAR""",
        "st": """(* 把 fbUnit 暴露为 I_UnitState 引用——典型注入模式：
   PackML 状态机不直接持有 FB 实例，只持有接口引用，便于多机型替换。 *)
ipUnit := fbUnit;

(* 把演示按钮映射到状态机命令——电平触发 *)
IF bGoAbort THEN
    eCmd := E_PMLCommand.ePMLCommand_Abort;     // 急停命令优先级最高
ELSIF bGoExecute THEN
    eCmd := E_PMLCommand.ePMLCommand_Start;     // 启动命令
ELSE
    eCmd := E_PMLCommand.ePMLCommand_Undefined; // 无命令保持
END_IF

(* 状态机周期推进——它会按 eState 通过 ipUnit 多态分派到 M_Execute / M_Aborting 等 *)
fbStateMachine(
    eMode            := 1,                 // 1 = Production 基础模式
    eCommand         := eCmd,
    stSubUnitInfoRef := stSubUnitInfoRef,
    stOptions        := stOptions
);

(* 在演示里直接调用 fbUnit 内部的计数器读取，方便在线观察 *)
nExecuteTickCounter := fbUnit.GetExecuteTicks();
nAbortTickCounter   := fbUnit.GetAbortTicks();

(* 注意：FB_DemoUnit_AllStates 需要您在 PLC 项目里另建——
   声明 IMPLEMENTS I_UnitState、19 个方法各填 nXxxTickCounter += 1。
   本例程只演示主程序调用框架。 *)""",
    },
    {
        "name": "I_UnitStateWaiting",
        "scenario": "演示在不需要全集 19 方法的场景下，单元 FB 仅实现 7 个 Waiting 稳态方法。\n//       本例展示一个温控保持模块——只在 Held/Idle/Stopped 等稳态做 PID 控温。",
        "value": "比直接实现 I_UnitState 节省 12 个空方法骨架；编译期约束 FB 只做维持类逻辑。",
        "verify": "在线写 bHoldRequest := TRUE，观察 nHoldTicks 在每周期累加，\n//        说明 M_Held 被反复调用做 PID 控温维持。",
        "decl": """VAR
    fbTempKeeper        : FB_DemoTempKeeper;        // 实现 I_UnitStateWaiting 的温控保持 FB
    ipWaiting           : I_UnitStateWaiting;       // 暴露为子接口
    bHoldRequest        : BOOL := FALSE;            // 演示用：模拟状态机处于 Held 时调 M_Held
    bIdleRequest        : BOOL := FALSE;            // 演示用：模拟处于 Idle
    nHoldTicks          : UDINT;                    // 观察 M_Held 被调次数
    nIdleTicks          : UDINT;                    // 观察 M_Idle 被调次数
    rCurrentTempC       : REAL;                     // 当前温度读数（在线查看 PID 输出）
END_VAR""",
        "st": """(* 把 fbTempKeeper 暴露为 I_UnitStateWaiting 接口——只关心稳态控制逻辑 *)
ipWaiting := fbTempKeeper;

(* 演示场景：模拟状态机停在 Held 或 Idle 稳态时，反复调用对应钩子 *)
IF bHoldRequest THEN
    ipWaiting.M_Held();          // 调 Held 钩子：内部做 PID 保温
ELSIF bIdleRequest THEN
    ipWaiting.M_Idle();          // 调 Idle 钩子：内部做"待命"逻辑
END_IF

(* 从 FB 读出在线计数器和当前温度——便于观察控制效果 *)
nHoldTicks    := fbTempKeeper.GetHoldTicks();
nIdleTicks    := fbTempKeeper.GetIdleTicks();
rCurrentTempC := fbTempKeeper.GetCurrentTempC();

(* 注意：FB_DemoTempKeeper 需要您在 PLC 项目里另建——
   声明 IMPLEMENTS I_UnitStateWaiting、7 个方法。M_Held 里做 PID
   控温到 60°C 维持，M_Idle 里关加热器、M_Aborted 里强制断电等。 *)""",
    },
    {
        "name": "I_UnitStateActing",
        "scenario": "演示只实现 PackML 12 个 Acting 过渡方法的场景——本例是贴标主动作模块。\n//       启动序列（M_Starting）预热贴头到 80°C，生产主循环（M_Execute）每件工件下发贴标，\n//       急停（M_Aborting）抬贴头、停传送带。",
        "value": "把 Acting 与 Waiting 分到不同 FB，新工艺替换 Acting FB、Waiting 不动。",
        "verify": "登录后写 bGoStarting := TRUE，观察 nStartingTicks 累加 + rLabelHeadTempC 升至 80。\n//        随后写 bGoExecute := TRUE，观察 nExecuteTicks 累加 + nLabeledProductCount 递增。\n//        写 bGoAbort := TRUE 验证 nAbortTicks 立即累加且 Execute 停下。",
        "decl": """VAR
    fbLabelActor        : FB_DemoLabelActor;        // 实现 I_UnitStateActing 的贴标动作 FB
    ipActing            : I_UnitStateActing;        // 暴露为子接口
    bGoStarting         : BOOL := FALSE;            // 演示触发 M_Starting
    bGoExecute          : BOOL := FALSE;            // 演示触发 M_Execute
    bGoAbort            : BOOL := FALSE;            // 演示触发 M_Aborting
    nStartingTicks      : UDINT;
    nExecuteTicks       : UDINT;
    nAbortTicks         : UDINT;
    rLabelHeadTempC     : REAL;                     // 贴头温度（M_Starting 预热目标 80°C）
    nLabeledProductCount: UDINT;                    // 已贴标件数（M_Execute 计数）
END_VAR""",
        "st": """(* 把 fbLabelActor 暴露为 I_UnitStateActing 接口 *)
ipActing := fbLabelActor;

(* 演示用：手动驱动状态过渡的 Acting 钩子（实际工程由 PML_StateMachine 自动调度） *)
IF bGoAbort THEN
    ipActing.M_Aborting();       // 急停：抬贴头、停传送带
ELSIF bGoExecute THEN
    ipActing.M_Execute();        // 主循环：每周期检查工件、贴标
ELSIF bGoStarting THEN
    ipActing.M_Starting();       // 启动序列：预热到 80°C
END_IF

(* 读出计数与状态供在线观察 *)
nStartingTicks       := fbLabelActor.GetStartingTicks();
nExecuteTicks        := fbLabelActor.GetExecuteTicks();
nAbortTicks          := fbLabelActor.GetAbortTicks();
rLabelHeadTempC      := fbLabelActor.GetLabelHeadTempC();
nLabeledProductCount := fbLabelActor.GetLabeledCount();

(* 注意：FB_DemoLabelActor 需要您在 PLC 项目里另建——
   IMPLEMENTS I_UnitStateActing；M_Starting 做温度上升模拟、M_Execute
   做计数与贴标动作、M_Aborting 立即复位贴头位置。 *)""",
    },

    # ===== Packaging Machine State FBs =====
    {
        "name": "PML_StateMachine",
        "scenario": "在 HMI 上模拟 Start / Stop / Hold / Abort 按钮驱动状态机；\n//       状态机按 PackML V3 标准规则做状态切换、拒绝非法命令。",
        "value": "不用本 FB 需要手写 17×9 = 153 个分支判断；用本 FB 一次实例化全搞定，\n//       且非法命令自动报错避免状态跑飞。",
        "verify": "登录后顺序写 bBtnReset := TRUE→FALSE → bBtnStart := TRUE→FALSE，\n//        观察 eState 从 0(Undefined) → 15(Resetting) → 4(Idle) → 3(Starting) → 6(Execute)。\n//        再写 bBtnAbort := TRUE→FALSE，验证 eState 立刻切到 8(Aborting) → 9(Aborted)。",
        "decl": """VAR
    fbStateMachine    : PML_StateMachine;
    bBtnReset         : BOOL := FALSE;             // HMI Reset 按钮（在线置 TRUE→FALSE）
    bBtnStart         : BOOL := FALSE;             // HMI Start 按钮
    bBtnStop          : BOOL := FALSE;             // HMI Stop 按钮
    bBtnHold          : BOOL := FALSE;             // HMI Hold 按钮
    bBtnAbort         : BOOL := FALSE;             // HMI Abort 按钮（急停）
    eCmd              : E_PMLCommand;              // 当前下发命令
    eState            : E_PMLState;                // 状态机当前状态（在线观察）
    bError            : BOOL;                      // 状态机错误标志
    nErrorId          : UDINT;                     // 错误号
    eMode             : DINT := 1;                 // 当前 UnitMode（1 = Production）
    stSubUnitInfoRef  : ST_PMLSubUnitInfoRef;      // 子单元状态汇总（本例无子单元）
    stOptions         : ST_PMLStateMachineOptions; // 选项（PDF V1.2.4 标 "Not used at present"）
END_VAR""",
        "st": """(* 把按钮事件按优先级（Abort 最高）映射到命令枚举——电平触发 *)
IF bBtnAbort THEN
    eCmd := E_PMLCommand.ePMLCommand_Abort;
ELSIF bBtnReset THEN
    eCmd := E_PMLCommand.ePMLCommand_Reset;
ELSIF bBtnStart THEN
    eCmd := E_PMLCommand.ePMLCommand_Start;
ELSIF bBtnStop THEN
    eCmd := E_PMLCommand.ePMLCommand_Stop;
ELSIF bBtnHold THEN
    eCmd := E_PMLCommand.ePMLCommand_Hold;
ELSE
    eCmd := E_PMLCommand.ePMLCommand_Undefined;
END_IF

(* 单次完整调用形式：所有 VAR_INPUT 显式赋值 *)
fbStateMachine(
    eMode            := eMode,
    eCommand         := eCmd,
    stSubUnitInfoRef := stSubUnitInfoRef,
    stOptions        := stOptions,
    eState           => eState,
    bError           => bError,
    nErrorId         => nErrorId
);""",
    },
    {
        "name": "PML_UnitModeConfig",
        "scenario": "在制药 CIP 清洗机上注册一个自定义 UnitMode 4 = Cleaning，\n//       禁用 Hold 类状态（清洗周期不允许暂停保持），\n//       只允许在 Stopped / Idle 切到/切走清洗模式。",
        "value": "把模式工艺约束（哪些状态可用、哪些状态可切换模式）配置化，不必硬编码到状态机。\n//       新工艺增加模式只需注册一次、不改主程序。",
        "verify": "登录后该 FB 一上电运行即注册 Mode 4 = 'Cleaning'。把 bError 加入 Watch List：\n//        若 bError = FALSE 表示注册成功；尝试用 PML_UnitModeManager 在 Idle 态切到 Mode 4 应成功，\n//        切到 Execute 时切 Mode 4 会被 Manager 拒（验证 bDisable/bEnable 规则生效）。",
        "decl": """VAR
    fbModeCfg : PML_UnitModeConfig;
    bRegistered : BOOL := FALSE;       // 一次性注册 latch
    bError      : BOOL;                 // 注册结果（在线观察）
    nErrorID    : UDINT;
END_VAR""",
        "st": """(* 一次性注册自定义模式 Cleaning（编号 4）——用 latch 避免周期重复 *)
IF NOT bRegistered THEN
    fbModeCfg(
        (* —— 模式编号与名称 —— *)
        eMode                          := 4,
        sName                          := 'Cleaning',
        (* —— 禁用 PML 状态：清洗时不允许 Hold/Held/Unhold —— *)
        bDisableClearing               := FALSE,
        bDisableStarting               := FALSE,
        bDisableSuspended              := TRUE,    // 清洗时禁用 Suspended 稳态
        bDisableStopping               := FALSE,
        bDisableAborting               := FALSE,
        bDisableHolding                := TRUE,    // 禁用 Holding 过渡
        bDisableHeld                   := TRUE,    // 禁用 Held 稳态（级联禁 Holding/Unholding）
        bDisableUnholding              := TRUE,
        bDisableSuspending             := TRUE,
        bDisableUnsuspending           := TRUE,
        bDisableResetting              := FALSE,
        bDisableIdle                   := FALSE,
        bDisableCompleting             := FALSE,
        bDisableComplete               := FALSE,
        (* —— 允许切换模式的稳态：仅 Stopped / Idle —— *)
        bEnableUnitModeChangeStopped   := TRUE,
        bEnableUnitModeChangeIdle      := TRUE,
        bEnableUnitModeChangeSuspended := FALSE,
        bEnableUnitModeChangeExecute   := FALSE,
        bEnableUnitModeChangeAborted   := FALSE,
        bEnableUnitModeChangeHeld      := FALSE,
        bEnableUnitModeChangeComplete  := FALSE,
        (* —— 输出回报 —— *)
        bError                         => bError,
        nErrorID                       => nErrorID
    );
    bRegistered := NOT bError;
END_IF""",
    },
    {
        "name": "PML_UnitModeManager",
        "scenario": "HMI 上有一个 切到维护模式 按钮——按下后本 FB 检查当前 PackML 状态是否允许，\n//       允许则切换、并把 eModeStatus 回馈给 PML_StateMachine.eMode。",
        "value": "把模式切换的 什么状态允许切 规则集中执行，不让操作员在错误状态强切。\n//       sModeStatus 字符串输出可直接绑 HMI 显示。",
        "verify": "登录后把 ePMLState_Watch 在线设到 ePMLState_Stopped（2），\n//        然后写 bSwitchToMaintBtn := TRUE→FALSE 一次（上升沿）。\n//        观察 bDone 闪一下变 TRUE、eModeStatus 由 1 变 2、sModeStatus 变 'Maintenance'。",
        "decl": """VAR
    fbModeMgr         : PML_UnitModeManager;
    bSwitchToMaintBtn : BOOL := FALSE;             // 在线模拟 HMI 按钮（上升沿触发）
    eRequestedMode    : DINT := 2;                  // 目标模式编号（2 = Maintenance）
    ePMLState_Watch   : E_PMLState                  // 演示用：手动设当前状态供 Manager 判定
                      := E_PMLState.ePMLState_Stopped;
    eModeStatus       : DINT;                       // 当前生效模式（输出）
    sModeStatus       : STRING;                     // 当前模式名（输出）
    bDone             : BOOL;
    bError            : BOOL;
    bErrorID          : UDINT;
END_VAR""",
        "st": """(* 单次完整调用形式：所有 VAR_INPUT 显式赋值。
   bExecute 是上升沿触发——bSwitchToMaintBtn 持续 TRUE 只切一次。 *)
fbModeMgr(
    bExecute     := bSwitchToMaintBtn,
    eModeCommand := eRequestedMode,
    ePMLState    := ePMLState_Watch,
    eModeStatus  => eModeStatus,
    sModeStatus  => sModeStatus,
    bDone        => bDone,
    bError       => bError,
    bErrorID     => bErrorID
);""",
    },

    # ===== General: PML_AdminAlarm + 9 methods =====
    {
        "name": "PML_AdminAlarm",
        "scenario": "构建完整的 alarm 上报+确认+清除业务循环：在 R_TRIG 上升沿调 M_SetAlarm 写报警；\n//       HMI 按钮调 M_AcknowledgeAlarm 确认；清除按钮调 M_ClearAlarm 归档到 AlarmHistory。\n//       本例演示一条 出料温度过高 报警的完整三阶段流程。",
        "value": "ISA-18.2 标准三阶段报警管理一次性封装，HMI/MES 走 PackTags 统一数据契约。",
        "verify": "确保 PackTags 全局已声明。在线写 bFault := TRUE 触发报警——\n//        Watch PackTags.Admin.Alarm[1].Trigger 应变 TRUE。然后 bAckBtn := TRUE→FALSE，\n//        Alarm[1].Trigger 应变 FALSE 但条目仍在；bClearBtn := TRUE→FALSE 后条目移入 AlarmHistory[]。",
        "decl": """VAR
    fbAdminAlarm  : PML_AdminAlarm;     // 报警管理 FB
    fbAdminTime   : PML_AdminTime;       // 必须配合周期调用，保证 PlcDateTime 新鲜
    stAdmin       : ST_PMLa;             // PackML 管理 PackTag 实例
    stStatus      : ST_PMLs;             // 状态 PackTag（PML_AdminTime 需要）
    bFault        : BOOL := FALSE;       // 在线模拟"故障检测"位
    rtFaultEdge   : R_TRIG;              // 边沿检测：保证 Set 只在故障出现的一刻调用
    bAckBtn       : BOOL := FALSE;       // HMI 确认按钮
    rtAckEdge     : R_TRIG;
    bClearBtn     : BOOL := FALSE;       // HMI 清除按钮
    rtClearEdge   : R_TRIG;
    stThisAlarm   : ST_Alarm := (
        Id := 1001,
        Value := 85,
        Message := 'Outlet temperature exceeded 85C',
        Category := 1
    );
    bSetOk        : BOOL;
    bAckOk        : BOOL;
    bClearOk      : BOOL;
    bReset        : BOOL := FALSE;       // PML_AdminTime 复位输入
    stTimeOptions : ST_AdminTimeOptions; // 默认使用 Windows 系统时间
END_VAR""",
        "st": """(* —— 第一步：必须周期调 PML_AdminTime 喂新鲜 PlcDateTime，否则报警时间戳全是 0 —— *)
fbAdminTime(
    bReset    := bReset,
    stOptions := stTimeOptions,
    stAdmin   := stAdmin,
    stStatus  := stStatus
);

(* —— 边沿检测：故障检测位上升沿才触发一次 SetAlarm —— *)
rtFaultEdge(CLK := bFault);
IF rtFaultEdge.Q THEN
    bSetOk := fbAdminAlarm.M_SetAlarm(stAdmin := stAdmin, stAlarm := stThisAlarm);
END_IF

(* —— HMI"确认"按钮上升沿调 M_AcknowledgeAlarm —— *)
rtAckEdge(CLK := bAckBtn);
IF rtAckEdge.Q THEN
    bAckOk := fbAdminAlarm.M_AcknowledgeAlarm(stAdmin := stAdmin, stAlarm := stThisAlarm);
END_IF

(* —— HMI"清除"按钮上升沿调 M_ClearAlarm 把项目移入 AlarmHistory —— *)
rtClearEdge(CLK := bClearBtn);
IF rtClearEdge.Q THEN
    bClearOk := fbAdminAlarm.M_ClearAlarm(stAdmin := stAdmin, stAlarm := stThisAlarm);
END_IF""",
    },
    {
        "name": "M_SetAlarm",
        "scenario": "上料温度传感器超过阈值时上报一条 alarm 到 PackTags.Admin.Alarm[]。",
        "value": "一行调用完成 找空位+置触发+写时间戳+复制字段 的标准操作。",
        "verify": "Watch stAdmin.Alarm[1].Trigger——在线写 bFaultDetected := TRUE 应立刻变 TRUE，\n//        DateTime[0]..[5] 应等于当前系统时间。",
        "decl": """VAR
    fbAdminAlarm   : PML_AdminAlarm;
    fbAdminTime    : PML_AdminTime;
    stAdmin        : ST_PMLa;
    stStatus       : ST_PMLs;
    bFaultDetected : BOOL := FALSE;       // 模拟故障检测信号
    rtFaultEdge    : R_TRIG;
    stHighTempAlarm: ST_Alarm := (
        Id       := 1001,
        Value    := 85,
        Message  := 'Outlet temperature exceeded 85C',
        Category := 1
    );
    bSetSuccess    : BOOL;
    bReset         : BOOL := FALSE;
    stTimeOptions  : ST_AdminTimeOptions;
END_VAR""",
        "st": """(* 周期推进时间统计——否则 alarm 时间戳全是 0 *)
fbAdminTime(bReset := bReset, stOptions := stTimeOptions,
            stAdmin := stAdmin, stStatus := stStatus);

(* 故障检测上升沿才调 M_SetAlarm——否则每周期会覆盖数组 *)
rtFaultEdge(CLK := bFaultDetected);
IF rtFaultEdge.Q THEN
    bSetSuccess := fbAdminAlarm.M_SetAlarm(stAdmin := stAdmin, stAlarm := stHighTempAlarm);
END_IF""",
    },
    {
        "name": "M_AcknowledgeAlarm",
        "scenario": "操作员在 HMI 看到温度报警后按 确认 按钮，本方法把 Alarm[].Trigger 置 FALSE\n//       并写入 AckDateTime。报警条目仍留在 Alarm[] 数组（待清除归档）。",
        "value": "符合 ISA-18.2 报警管理标准的两阶段处理；AckDateTime 时间戳便于事后审计。",
        "verify": "假设已通过 SetAlarm 设置了一条 Id=1001 报警。在线写 bAckBtn := TRUE→FALSE，\n//        Watch stAdmin.Alarm[1].Trigger 应变 FALSE 但 .Id 仍为 1001、AckDateTime[*] 不再为 0。",
        "decl": """VAR
    fbAdminAlarm   : PML_AdminAlarm;
    fbAdminTime    : PML_AdminTime;
    stAdmin        : ST_PMLa;
    stStatus       : ST_PMLs;
    bAckBtn        : BOOL := FALSE;       // HMI 确认按钮
    rtAckEdge      : R_TRIG;
    stAckTarget    : ST_Alarm := (Id := 1001);   // 仅 Id 用于匹配
    bAckSuccess    : BOOL;
    bReset         : BOOL := FALSE;
    stTimeOptions  : ST_AdminTimeOptions;
END_VAR""",
        "st": """(* 周期推进时间——AckDateTime 来自 stAdmin.PlcDateTime *)
fbAdminTime(bReset := bReset, stOptions := stTimeOptions,
            stAdmin := stAdmin, stStatus := stStatus);

(* HMI"确认"按钮上升沿触发一次 Acknowledge *)
rtAckEdge(CLK := bAckBtn);
IF rtAckEdge.Q THEN
    bAckSuccess := fbAdminAlarm.M_AcknowledgeAlarm(
        stAdmin := stAdmin,
        stAlarm := stAckTarget    // 按 Id 找到对应活动 alarm
    );
END_IF""",
    },
    {
        "name": "M_ClearAlarm",
        "scenario": "操作员在 HMI 按 清除 按钮把已确认的 alarm 移入 AlarmHistory 归档。\n//       归档后 Alarm[] 数组对应槽位释放，AlarmHistory[] 保留可查。",
        "value": "三阶段处理 Set → Ack → Clear 完整闭环；归档保留历史可被 MES 周期采集。",
        "verify": "假设已 Ack 过一条 Id=1001 报警。在线写 bClearBtn := TRUE→FALSE，\n//        Watch stAdmin.Alarm[1].Id 应变 0 / Trigger=FALSE，\n//        stAdmin.AlarmHistory[1].Id 应变为 1001。",
        "decl": """VAR
    fbAdminAlarm   : PML_AdminAlarm;
    fbAdminTime    : PML_AdminTime;
    stAdmin        : ST_PMLa;
    stStatus       : ST_PMLs;
    bClearBtn      : BOOL := FALSE;
    rtClearEdge    : R_TRIG;
    stClearTarget  : ST_Alarm := (Id := 1001);
    bClearSuccess  : BOOL;
    bReset         : BOOL := FALSE;
    stTimeOptions  : ST_AdminTimeOptions;
END_VAR""",
        "st": """(* 保持时间新鲜（虽然 Clear 不写 DateTime，但与其他方法配合时一致性更好） *)
fbAdminTime(bReset := bReset, stOptions := stTimeOptions,
            stAdmin := stAdmin, stStatus := stStatus);

(* HMI"清除"按钮上升沿触发一次 Clear——把 alarm 移入 AlarmHistory *)
rtClearEdge(CLK := bClearBtn);
IF rtClearEdge.Q THEN
    bClearSuccess := fbAdminAlarm.M_ClearAlarm(
        stAdmin := stAdmin,
        stAlarm := stClearTarget
    );
END_IF""",
    },
    {
        "name": "M_SetWarning",
        "scenario": "原料桶液位低于 30% 时上报 warning 提醒补料——不停机不报警，只是黄色提示。",
        "value": "HMI 区分 alarm 红色 vs warning 黄色，操作员凭颜色判断严重度。",
        "verify": "在线写 bLowLevel := TRUE，Watch stAdmin.Warning[1].Trigger 应立刻变 TRUE，\n//        DateTime[*] 不为 0。再写 bLowLevel := FALSE 不会自动清除（要主动调 Clear）。",
        "decl": """VAR
    fbAdminAlarm        : PML_AdminAlarm;
    fbAdminTime         : PML_AdminTime;
    stAdmin             : ST_PMLa;
    stStatus            : ST_PMLs;
    bLowLevel           : BOOL := FALSE;
    rtLowLevelEdge      : R_TRIG;
    stMaterialLowWarning: ST_Alarm := (
        Id       := 100,
        Value    := 30,
        Message  := 'Material level below 30%',
        Category := 2
    );
    bSetOk              : BOOL;
    bReset              : BOOL := FALSE;
    stTimeOptions       : ST_AdminTimeOptions;
END_VAR""",
        "st": """fbAdminTime(bReset := bReset, stOptions := stTimeOptions,
            stAdmin := stAdmin, stStatus := stStatus);

(* 低液位检测上升沿才写 warning *)
rtLowLevelEdge(CLK := bLowLevel);
IF rtLowLevelEdge.Q THEN
    bSetOk := fbAdminAlarm.M_SetWarning(
        stAdmin   := stAdmin,
        stWarning := stMaterialLowWarning
    );
END_IF""",
    },
    {
        "name": "M_AcknowledgeWarning",
        "scenario": "操作员看到液位低 warning 后按 了解 按钮——本方法标记已确认。",
        "value": "AckDateTime 记录了 warning 何时被人看到，便于审计响应时间。",
        "verify": "假设已 Set 过一条 Id=100 warning。bAckBtn := TRUE→FALSE 后\n//        stAdmin.Warning[1].Trigger 应变 FALSE，但条目仍在（AckDateTime 不再为 0）。",
        "decl": """VAR
    fbAdminAlarm  : PML_AdminAlarm;
    fbAdminTime   : PML_AdminTime;
    stAdmin       : ST_PMLa;
    stStatus      : ST_PMLs;
    bAckBtn       : BOOL := FALSE;
    rtAckEdge     : R_TRIG;
    stTarget      : ST_Alarm := (Id := 100);
    bAckOk        : BOOL;
    bReset        : BOOL := FALSE;
    stTimeOptions : ST_AdminTimeOptions;
END_VAR""",
        "st": """fbAdminTime(bReset := bReset, stOptions := stTimeOptions,
            stAdmin := stAdmin, stStatus := stStatus);

rtAckEdge(CLK := bAckBtn);
IF rtAckEdge.Q THEN
    bAckOk := fbAdminAlarm.M_AcknowledgeWarning(
        stAdmin   := stAdmin,
        stWarning := stTarget
    );
END_IF""",
    },
    {
        "name": "M_ClearWarning",
        "scenario": "补料后液位回到 60%——检测代码自动清除 低液位 warning，HMI 黄色提示消失。",
        "value": "自动清除让 HMI 始终反映当前需要操作员注意的事项，避免陈旧提示淹没。",
        "verify": "假设有活动 warning Id=100。在线写 bRecovered := TRUE，\n//        Watch stAdmin.Warning[1].Trigger 应变 FALSE。",
        "decl": """VAR
    fbAdminAlarm  : PML_AdminAlarm;
    fbAdminTime   : PML_AdminTime;
    stAdmin       : ST_PMLa;
    stStatus      : ST_PMLs;
    bRecovered    : BOOL := FALSE;     // 液位回到正常——上升沿清除 warning
    rtRecoverEdge : R_TRIG;
    stTarget      : ST_Alarm := (Id := 100);
    bClearOk      : BOOL;
    bReset        : BOOL := FALSE;
    stTimeOptions : ST_AdminTimeOptions;
END_VAR""",
        "st": """fbAdminTime(bReset := bReset, stOptions := stTimeOptions,
            stAdmin := stAdmin, stStatus := stStatus);

rtRecoverEdge(CLK := bRecovered);
IF rtRecoverEdge.Q THEN
    bClearOk := fbAdminAlarm.M_ClearWarning(
        stAdmin   := stAdmin,
        stWarning := stTarget
    );
END_IF""",
    },
    {
        "name": "M_SetStopReason",
        "scenario": "PackML 状态机切到 Stopped 时上报一条 StopReason 换班停机（Id=1），\n//       供 MES 做 OEE 分类聚合。",
        "value": "PackML 标准化的停机原因记录——OEE 计算的计划/非计划停机分类必备数据源。",
        "verify": "在线写 bShiftEnd := TRUE→FALSE 一次。Watch stAdmin.StopReason[1].Trigger=TRUE，\n//        StopReason[1].Id=1，DateTime 不为 0。",
        "decl": """VAR
    fbAdminAlarm       : PML_AdminAlarm;
    fbAdminTime        : PML_AdminTime;
    stAdmin            : ST_PMLa;
    stStatus           : ST_PMLs;
    bShiftEnd          : BOOL := FALSE;       // 模拟换班停机触发
    rtShiftEdge        : R_TRIG;
    stShiftChangeStop  : ST_Alarm := (
        Id       := 1,
        Value    := 0,
        Message  := 'Shift change',
        Category := 1                          // 1 = 计划停机
    );
    bSetOk             : BOOL;
    bReset             : BOOL := FALSE;
    stTimeOptions      : ST_AdminTimeOptions;
END_VAR""",
        "st": """fbAdminTime(bReset := bReset, stOptions := stTimeOptions,
            stAdmin := stAdmin, stStatus := stStatus);

(* 停机事件上升沿才写——否则会重复刷新数组 *)
rtShiftEdge(CLK := bShiftEnd);
IF rtShiftEdge.Q THEN
    bSetOk := fbAdminAlarm.M_SetStopReason(
        stAdmin      := stAdmin,
        stStopReason := stShiftChangeStop
    );
END_IF""",
    },
    {
        "name": "M_AcknowledgeStopReason",
        "scenario": "MES 通过 ADS 调用本方法把已采走的 StopReason 标为已确认，避免下次重采。",
        "value": "AckDateTime 记录信息系统消费时刻，便于反查 MES 响应延迟。",
        "verify": "假设已 Set 过一条 Id=1 StopReason。在线写 bMesAck := TRUE→FALSE。\n//        Watch stAdmin.StopReason[1].Trigger 应变 FALSE、AckDateTime[*] 不再为 0。",
        "decl": """VAR
    fbAdminAlarm  : PML_AdminAlarm;
    fbAdminTime   : PML_AdminTime;
    stAdmin       : ST_PMLa;
    stStatus      : ST_PMLs;
    bMesAck       : BOOL := FALSE;       // 模拟 MES 通过 ADS 触发确认
    rtAckEdge     : R_TRIG;
    stAckTarget   : ST_Alarm := (Id := 1);
    bAckOk        : BOOL;
    bReset        : BOOL := FALSE;
    stTimeOptions : ST_AdminTimeOptions;
END_VAR""",
        "st": """fbAdminTime(bReset := bReset, stOptions := stTimeOptions,
            stAdmin := stAdmin, stStatus := stStatus);

rtAckEdge(CLK := bMesAck);
IF rtAckEdge.Q THEN
    bAckOk := fbAdminAlarm.M_AcknowledgeStopReason(
        stAdmin      := stAdmin,
        stStopReason := stAckTarget
    );
END_IF""",
    },
    {
        "name": "M_ClearStopReason",
        "scenario": "换班时班长在 HMI 点 清班 按钮——遍历 StopReason[] 调用本方法清掉上班次记录。",
        "value": "让 OEE 统计从干净状态起步，新班次数据不被上班次污染。",
        "verify": "假设有活动 StopReason Id=1。在线写 bShiftClearBtn := TRUE→FALSE。\n//        Watch stAdmin.StopReason[1].Trigger 应变 FALSE。",
        "decl": """VAR
    fbAdminAlarm   : PML_AdminAlarm;
    fbAdminTime    : PML_AdminTime;
    stAdmin        : ST_PMLa;
    stStatus       : ST_PMLs;
    bShiftClearBtn : BOOL := FALSE;
    rtClearEdge    : R_TRIG;
    stTarget       : ST_Alarm := (Id := 1);
    bClearOk       : BOOL;
    bReset         : BOOL := FALSE;
    stTimeOptions  : ST_AdminTimeOptions;
END_VAR""",
        "st": """fbAdminTime(bReset := bReset, stOptions := stTimeOptions,
            stAdmin := stAdmin, stStatus := stStatus);

rtClearEdge(CLK := bShiftClearBtn);
IF rtClearEdge.Q THEN
    bClearOk := fbAdminAlarm.M_ClearStopReason(
        stAdmin      := stAdmin,
        stStopReason := stTarget
    );
END_IF""",
    },
    {
        "name": "PML_AdminTime",
        "scenario": "在每个 PLC 周期把当前模式（PMLs.UnitModeCurrent）和状态（PMLs.StateCurrent）\n//       的停留时间累计到 PackTags.Admin.*Time 数组，供 MES 做 OEE 时间分配。",
        "value": "OEE 计算的 时间分配数据 由本 FB 自动累计——节省手写状态停留时间累计逻辑。\n//       PlcDateTime 输出还为所有 PML_AdminAlarm 方法供新鲜时间戳。",
        "verify": "登录后写 stStatus.UnitModeCurrent := 1; stStatus.StateCurrent := 6;\n//        每秒看 stAdmin.StateCurrentTime[1,6] 累加，stAdmin.PlcDateTime 与系统时间一致。\n//        切到 StateCurrent := 4（Idle）观察 [1,4] 开始累加、[1,6] 停止。",
        "decl": """VAR
    fbAdminTime    : PML_AdminTime;
    stAdmin        : ST_PMLa;            // 累计时间存这里
    stStatus       : ST_PMLs;            // 当前模式/状态从这里读
    bResetTimes    : BOOL := FALSE;       // HMI"复位累计"按钮（上升沿）
    stTimeOptions  : ST_AdminTimeOptions; // 默认用 Windows 系统时间
END_VAR""",
        "st": """(* 演示场景：把当前 UnitMode 设为 1（Production）、State 设为 6（Execute）。
   实际工程里这两个值由 PML_StateMachine 与 PML_UnitModeManager 输出后写入。 *)
stStatus.UnitModeCurrent := 1;
stStatus.StateCurrent    := 6;

(* 必须每周期调一次——少调一次时间累计就缺一段 *)
fbAdminTime(
    bReset    := bResetTimes,
    stOptions := stTimeOptions,
    stAdmin   := stAdmin,
    stStatus  := stStatus
);""",
    },

    # ===== Conversion functions =====
    {
        "name": "LTIME_TO_PackMLTime",
        "scenario": "把 LTIME 类型的累计运行时长转成 PackML 7 元素数组写入 Admin PackTag。",
        "value": "标准化 LTIME → PackML 时长数组转换，避免手写时长拆解。",
        "verify": "登录后看 aPackMLDuration[*]：tInput=LTIME#1H 应得 [0,0,0,1,0,0,0] 或类似。",
        "decl": """VAR
    tInput          : LTIME := LTIME#1H30M;        // 演示用：1 小时 30 分钟时长
    aPackMLDuration : ARRAY[0..6] OF DINT;          // 转换结果（在线观察）
END_VAR""",
        "st": """(* 纯函数调用——单行完成 *)
aPackMLDuration := LTIME_TO_PackMLTime(Input := tInput);""",
    },
    {
        "name": "TIME_TO_PackMLTime",
        "scenario": "把 TIME 类型测得的 本次循环用时 转成 PackML 数组写入 OEE 字段。",
        "value": "TIME 是最常用的 IEC 时长类型，本函数提供 PackML 数组标准转换。",
        "verify": "tInput=T#1H23M45S 时 aPackMLDuration 应填好对应分量。",
        "decl": """VAR
    tInput          : TIME := T#1H23M45S;          // 演示用：1 小时 23 分 45 秒
    aPackMLDuration : ARRAY[0..6] OF DINT;
END_VAR""",
        "st": """aPackMLDuration := TIME_TO_PackMLTime(Input := tInput);""",
    },
    {
        "name": "ULINT_TO_PackMLTime",
        "scenario": "把 EtherCAT 主站给的裸 ULINT 时长计数（约定纳秒单位）转成 PackML 数组。",
        "value": "处理无类型的裸时长计数值——接口适配场景必备转换。",
        "verify": "uliInput=3600_000_000_000（1 小时纳秒）时 aPackMLDuration 应填出 1 小时。",
        "decl": """VAR
    (* 演示用：1 小时 = 3600_000_000_000 纳秒 *)
    uliInput        : ULINT := ULINT#3600000000000;
    aPackMLDuration : ARRAY[0..6] OF DINT;
END_VAR""",
        "st": """aPackMLDuration := ULINT_TO_PackMLTime(Input := uliInput);""",
    },
    {
        "name": "DCTIME64_TO_PackMLTime",
        "scenario": "用 EtherCAT 分布式时钟（DC）替代本地 Windows 时间——\n//       多 PLC 协同时所有报警时间戳跨设备纳秒级一致。",
        "value": "EtherCAT DC 与 PackML 时间标准的桥接，多 PLC 同步场景必备。",
        "verify": "需要 EtherCAT DC 同步已配置。读 F_GetSystemTime 等拿 DCTIME64，\n//        本例直接演示 API：dctInput 填 0 时 aPackMLNow 应得 2000-01-01。",
        "decl": """VAR
    dctInput   : DCTIME64;                  // 通常来自 EtherCAT 主站时钟
    aPackMLNow : ARRAY[0..6] OF DINT;
END_VAR""",
        "st": """(* 实际工程：dctInput := F_GetCurDcTaskTime64();（来自 Tc2_EtherCAT）
   本例只演示函数 API——dctInput 默认 0 对应 2000-01-01 00:00:00 *)
aPackMLNow := DCTIME64_TO_PackMLTime(Input := dctInput);""",
    },
    {
        "name": "DT_TO_PackMLTime",
        "scenario": "把 HMI 用户选择的 上次维护日期 DT 值转成 PackML 数组写入 PackTag。",
        "value": "IEC 标准 DT 类型与 PackML 时间数组直接互转——最常用的时刻转换。",
        "verify": "dtInput := DT#2026-06-03-14:30:00 应得 aPackMLTime = [2026,6,3,14,30,0,0]。",
        "decl": """VAR
    dtInput     : DT := DT#2026-06-03-14:30:00;
    aPackMLTime : ARRAY[0..6] OF DINT;
END_VAR""",
        "st": """aPackMLTime := DT_TO_PackMLTime(Input := dtInput);""",
    },
    {
        "name": "TIMESTRUCT_TO_PackMLTime",
        "scenario": "Tc2_System.GetSystemTime 返回 TIMESTRUCT，转成 PackML 数组写报警时间戳。",
        "value": "毫秒精度的时刻转换标准函数，满足绝大多数 PackML 应用精度需求。",
        "verify": "tsInput 各字段填好后 aPackMLTime[0..6] 应分别对应年/月/日/时/分/秒/毫秒。",
        "decl": """VAR
    tsInput     : TIMESTRUCT := (
        wYear         := 2026,
        wMonth        := 6,
        wDayOfWeek    := 3,           // 星期 ——本函数不映射到数组
        wDay          := 3,
        wHour         := 14,
        wMinute       := 30,
        wSecond       := 0,
        wMilliseconds := 123
    );
    aPackMLTime : ARRAY[0..6] OF DINT;
END_VAR""",
        "st": """aPackMLTime := TIMESTRUCT_TO_PackMLTime(Input := tsInput);""",
    },
    {
        "name": "F_StateCommandToString",
        "scenario": "HMI 报警日志要记录 操作员发了 Start 命令，把 E_PMLCommand 数值转可读字符串。",
        "value": "枚举↔字符串标准映射封装，HMI 显示文本一致性保证。",
        "verify": "eCmd := ePMLCommand_Start 时 sCmdName 应为 'Start' 或类似字面值。",
        "decl": """VAR
    eCmd      : E_PMLCommand := E_PMLCommand.ePMLCommand_Start;
    sCmdName  : STRING;
END_VAR""",
        "st": """sCmdName := F_StateCommandToString(eStateCommand := eCmd);""",
    },
    {
        "name": "F_UnitModeToString",
        "scenario": "HMI 显示当前模式 Production——把 DINT 模式编号转字符串。",
        "value": "支持基础模式 1-3 硬编码 + 自定义模式 4-31 查 PML_UnitModeConfig.sName。",
        "verify": "eMode := 1 应得 sModeName = 'Production'；eMode := 2 应得 'Maintenance'。",
        "decl": """VAR
    eMode     : DINT := 1;        // 1=Production / 2=Maintenance / 3=Manual
    sModeName : STRING;
END_VAR""",
        "st": """sModeName := F_UnitModeToString(eMode := eMode);""",
    },
]


_TPL = """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">
  <POU Name="P_Demo_{name}" Id="{guid}" SpecialFunc="None">
    <Declaration><![CDATA[PROGRAM P_Demo_{name}
{decl}
]]></Declaration>
    <Implementation>
      <ST><![CDATA[// ============================================================
// Tc3_PackML_V2.{name} 演示程序
// ============================================================
// 场景：{scenario}
// 价值：{value}
// 验证：{verify}
// 验证步骤：
//   1. 右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选本 .TcPOU 文件
//   2. 引用 Tc3_PackML_V2（References → Add library）
//   3. 编译 → 登录 → 运行；按上方"验证"指引在线写值观察
// ============================================================

{st}
]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>
"""


def main() -> int:
    EX_DIR.mkdir(parents=True, exist_ok=True)
    for e in ENTRIES:
        name = e["name"]
        out = EX_DIR / f"P_Demo_{name}.TcPOU"
        text = _TPL.format(
            name=name,
            guid=gid(name),
            decl=e["decl"],
            scenario=e["scenario"],
            value=e["value"],
            verify=e["verify"],
            st=e["st"],
        )
        out.write_text(text)
        print(f"wrote {out.relative_to(ROOT)}")
    print(f"\n{len(ENTRIES)} TcPOU files generated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
