# -*- coding: utf-8 -*-
"""Generator for Tc3_MC2_AdvancedHoming docs + PLCopenXML examples.

Each entry carries the verbatim VAR interface (from PDF + InfoSys cross-check)
plus Chinese §1/§3/§5/§7 prose. Pin names in the example are taken from the
same `inputs/outputs` lists so doc and example never diverge.

All facts are from:
  PDF  TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf  (Version 1.7.7)
  InfoSys topic pages (IDs per entry below)
"""
import os
import datetime

LIB = "Tc3_MC2_AdvancedHoming"
VERSION = "1.7.7"
DATE = "2026-05-25"
PDF = ("https://download.beckhoff.com/download/document/automation/twincat3/"
       "TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf")
INFO = "https://infosys.beckhoff.com/content/1033/tcplclib_tc3_mc2_advancedhoming/{}.html"

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCDIR = os.path.join(ROOT, LIB)
EXDIR = os.path.join(DOCDIR, "examples")

CAT_DIR = {
    "Finalizing functions": "finalizing_functions",
    "Referencing functions (passive)": "referencing_functions_passive",
    "Step functions": "step_functions",
}

XML_ESC = [("&", "&amp;"), ("<", "&lt;"), (">", "&gt;")]


def esc(s):
    for a, b in XML_ESC:
        s = s.replace(a, b)
    return s


# ---- shared description fragments (translated, identical wording across FBs) ----
D = {
    "Execute": "上升沿触发一次命令执行；触发后进入处理状态，无需保持高电平",
    "Direction": "枚举（见 §8 数据类型）：定义搜索过程的起始运动方向（`mcPositiveDirection` / `mcNegativeDirection` / `mcSwitchPositive` / `mcSwitchNegative`）",
    "Velocity": "最大运行速度（必须 > 0）",
    "Acceleration": "加速度（≥ 0）；取 0 时采用轴配置里的标准加速度",
    "Deceleration": "减速度（≥ 0）；取 0 时采用轴配置里的标准减速度",
    "Jerk": "加加速度 / 急动度（≥ 0）；取 0 时采用轴配置里的标准急动度",
    "SetPosition": "搜索成功后把轴的当前位置设为该值（绝对零点）",
    "TimeLimit": "搜索耗时超过此时间则中止搜索过程",
    "DistanceLimit": "相对起始位置移动超过此距离则中止搜索过程",
    "TorqueLimit": "把电机转矩限制到该值，避免撞击时损坏机械",
    "BufferMode": "未实现（`Not implemented`），按 PDF 说明本入口当前无效",
    "ReferenceSignal": "`MC_Ref_Signal_Ref` 结构：定义参考信号源（锁存单元 `TouchProbe`、信号源 `SignalSource`、当前电平 `Level`），见 §8",
    "Done": "命令成功完成时置 `TRUE`",
    "Busy": "`Execute` 上升沿后立即置 `TRUE`，命令处理期间保持 `TRUE`；变回 `FALSE` 时 FB 可接新命令，同时 `Done` / `CommandAborted` / `Error` 之一被置位",
    "Active": "表示命令当前正在执行",
    "CommandAborted": "命令未能完整执行（被中止）时置 `TRUE`",
    "Error": "执行期间一旦发生错误即置 `TRUE`",
    "ErrorID": "`Error = TRUE` 时给出错误号（见 §4，本库 `E_HomingErrorCodes` 段）",
    "RecordedPosition": "记录到事件（开关/脉冲/堵转）时刻的轴位置；Detection 版本不改写轴位置，而是用本输出返回检测到的位置",
    "Axis": "`AXIS_REF` 轴数据结构，唯一标识系统中的一根轴，含位置、速度、错误状态等循环数据。**必须传引用**（VAR_IN_OUT 语义）",
    "Parameter": "`MC_HomingParameter` 数据结构，必须在整条归零序列的所有 FB 之间逐级传递（参数先备份、被各 FB 修改、序列结束时还原）。**必须传引用**",
    "Distance": "轴从当前位置反向退离的距离（用于释放开关或离开机械止挡）",
    "DetectionVelocityLimit": "限制速度：实际速度必须在 `DetectionVelocityTime` 时间内持续低于此值，才判定为已顶到机械止挡",
    "DetectionVelocityTime": "判定速度跌落（顶到止挡）所需的持续时间",
    "TorqueTolerance": "相对 `TorqueLimit` 的容差；实际转矩进入该容差带才判定为顶到止挡",
    "LagLimit": "位置跟随误差阈值；跟随误差超过此值即判定为顶到机械止挡",
    "PositiveLimitSwitch": "逻辑正方向硬件限位开关信号（在允许行程范围内时 `PositiveLimitSwitch = FALSE`）",
    "NegativeLimitSwitch": "逻辑负方向硬件限位开关信号（在允许行程范围内时 `NegativeLimitSwitch = FALSE`）",
    "SwitchMode": "`MC_Switch_Mode` 枚举（见 §8）：定义搜索过程的结束条件（`mcOn` / `mcOff` / `mcRisingEdge` / `mcFallingEdge` / `mcEdgeSwitchPositive` / `mcEdgeSwitchNegative` / `mcRisingEdgeInverse` / `mcFallingEdgeInverse`）",
    "LimitSwitchMode": "`MC_Switch_Mode` 枚举（见 §8）：定义限位开关搜索过程的结束条件",
    "LimitSwitchSignal": "`MC_Ref_Signal_Ref` 结构：定义限位开关参考信号源（锁存单元、信号源、当前电平），见 §8",
}

OPT2_DESC = ("`ST_Home_Options2` 结构：仅含 `DisableDriveAccess : BOOL`。"
             "Beckhoff 伺服设 `FALSE`，第三方伺服通常设 `TRUE`；设 `TRUE` 时由用户自行负责修改与恢复驱动参数")
OPT3_DESC = ("`ST_Home_Options3` 结构：含 `DisableDriveAccess : BOOL`（同 Options2）与 "
             "`InstantLagReduction : BOOL`（顶到机械止挡后突停会产生跟随误差，置 `TRUE` 让其瞬时消除，"
             "对“软”止挡尤其有用）")
OPT4_DESC = ("`ST_Home_Options4` 结构：含 `DisableDriveAccess : BOOL`（同 Options2）与 "
             "`EnableLagErrorDetection : BOOL`（step 函数默认关闭跟随误差监控以保证平顺，"
             "置 `TRUE` 可在搜索期间保持跟随误差监控）")
OPT0_DESC = "`ST_Home_Options` 结构：当前未使用（`Currently not used`）"

# entries: each is a dict. inputs/in_out/outputs are (name,type,descKey-or-literal) tuples.
# When the 3rd element is a key of D, that translation is used; else literal string.
E = []


def add(**kw):
    E.append(kw)


# ---------- 3.1 Finalizing ----------
add(
    name="MC_FinishHoming", topic="427748491", category="Finalizing functions",
    sec="3.1.1",
    s1=("归零序列的**收尾功能块**。在 step 函数成功搜到参考点后调用它来正常结束整条归零序列，"
        "把序列中被临时修改的 NC / 驱动参数还原为原值，并把轴状态从 `Homing` 切回 `Standstill`。"
        "可选地它还能发一段运动命令（指定 `Distance`），用于退离开关或离开机械止挡。"
        "除非整条序列只用被动（flying）归零函数，否则每条自定义归零序列都必须以一个收尾 FB 结束。"),
    inputs=[
        ("Execute", "BOOL", "Execute"),
        ("Distance", "LREAL", "Distance"),
        ("Velocity", "LREAL", "Velocity"),
        ("Acceleration", "LREAL", "Acceleration"),
        ("Deceleration", "LREAL", "Deceleration"),
        ("Jerk", "LREAL", "Jerk"),
        ("BufferMode", "MC_BufferMode", "BufferMode"),
        ("Options", "ST_Home_Options2", OPT2_DESC),
    ],
    in_out=[("Axis", "AXIS_REF", "Axis"), ("Parameter", "MC_HomingParameter", "Parameter")],
    outputs=[("Done", "BOOL", "Done"), ("Busy", "BOOL", "Busy"),
             ("CommandAborted", "BOOL", "CommandAborted"), ("Error", "BOOL", "Error"),
             ("ErrorID", "UDINT", "ErrorID")],
    s3=("`Execute` 上升沿启动收尾流程。本 FB 是“finalizing（收尾）”类，按 PDF 第 2.3 节它会把轴状态"
        "从 `Homing` 改回 `Standstill`，并依据传入的 `Parameter`（`MC_HomingParameter`）把先前 step 函数"
        "为搜参考点而临时修改的 NC / 驱动参数还原回备份值。若给定非零 `Distance`，FB 还会下发一段相对运动："
        "按 `Velocity` / `Acceleration` / `Deceleration` / `Jerk` 把轴反向退离当前位置 `Distance`，"
        "典型用于把轴从压住的开关或顶住的机械止挡上松开。`Busy` 在 `Execute` 上升沿后置 `TRUE` 直到收尾结束，"
        "成功后 `Done = TRUE`；被中止则 `CommandAborted = TRUE`；出错 `Error = TRUE` 并给出 `ErrorID`。"
        "调用时序：先调一个或多个 step 函数搜索参考点，搜索成功（`Done = TRUE`）后再以同一个 `Axis` 与 "
        "`Parameter` 调用本 FB 收尾；搜索失败（`Error` / `CommandAborted`）时应改调 `MC_AbortHoming`。"),
    s5=[("`Distance` = 0 时本 FB 不发运动，只做状态切换与参数还原；需要退离开关/止挡才给非零 `Distance`。", False),
        ("退离方向与 `Distance` 符号 / step 函数的搜索方向相关，退离方向选错可能把轴推向限位 ⚠️ —— 上线前务必先空载验证退离方向。", False),
        ("`Parameter` 必须是贯穿整条序列的同一个 `MC_HomingParameter` 实例，否则参数无法正确还原。", False),
        ("`BufferMode` 当前未实现，传任何值都不改变行为。", False),
        ("只用被动 flying 归零（`MC_StepReferenceFlying*`）的序列不需要收尾 FB；混合序列仍需收尾。", False)],
    s7=("- **场景**：自定义“先搜限位开关 / 撞块 / 编码器零脉冲 → 定零”的归零序列最后一步，"
        "用本 FB 正常收尾并退离开关。\n"
        "- **价值**：把“还原被改的 NC/驱动参数 + 切回 Standstill + 退离开关”三件事封装为一个 FB；"
        "不用本 FB 时这些状态机收尾要手写且极易漏还原参数。\n"
        "- **替代方案对比**：`MC_AbortHoming`（异常分支收尾，不退离、标记中止）；"
        "标准 `MC_Home`（Tc2_MC2，固定序列、不可自定义分段）。本 FB 用于成功分支的正常收尾。"),
    ex_extra={"Distance": ("LREAL", "10.0", "退离距离：成功后反向退 10（用户单位）松开开关")},
    ex_scene=("// 场景：自定义归零序列的“正常收尾”——前面用 MC_StepLimitSwitch 搜到限位开关并 Done 后，\n"
              "//       调用本 FB 把临时改过的 NC/驱动参数还原、轴状态切回 Standstill，并反向退 10 个\n"
              "//       单位松开限位开关，避免轴一直压在开关上。\n"
              "// 价值：不用本 FB 时要手写“还原参数 + 改状态 + 退离”三段逻辑，漏还原参数会让后续运动异常。\n"
              "// 验证：先让 fbStep 那侧 Done；在线写 bFinishReq := TRUE，观察 bFinishDone 短暂 TRUE，\n"
              "//       axisHoming.Status 离开 Homing 进入 Standstill，轴反向移动约 10 个单位后停。"),
)

add(
    name="MC_HomeDirect", topic="427750411", category="Finalizing functions",
    sec="3.1.2",
    s1=("归零序列的**收尾功能块**，作用是“直接置位”收尾：成功结束序列的同时把轴当前位置直接设为 "
        "`SetPosition` 给定的值，并还原被临时修改的参数、把轴状态从 `Homing` 切回 `Standstill`。"
        "与 `MC_FinishHoming` 的区别是本 FB 在收尾时把位置定到一个用户指定的绝对值，常用于静态归零"
        "（操作员把轴停在已知位置后直接告诉 NC“我现在在这”）。"),
    inputs=[
        ("Execute", "BOOL", "Execute"),
        ("SetPosition", "LREAL", "SetPosition"),
        ("BufferMode", "MC_BufferMode", "BufferMode"),
        ("Options", "ST_Home_Options2", OPT2_DESC),
    ],
    in_out=[("Axis", "AXIS_REF", "Axis"), ("Parameter", "MC_HomingParameter", "Parameter")],
    outputs=[("Done", "BOOL", "Done"), ("Busy", "BOOL", "Busy"), ("Active", "BOOL", "Active"),
             ("CommandAborted", "BOOL", "CommandAborted"), ("Error", "BOOL", "Error"),
             ("ErrorID", "UDINT", "ErrorID")],
    s3=("`Execute` 上升沿触发收尾。本 FB 属 finalizing 类：按 PDF 第 3.1.2 节，它把轴当前位置直接复位为 "
        "`SetPosition`，确保被序列临时修改的 NC / 驱动参数还原为原值，随后轴离开 `Homing` 状态回到 "
        "`Standstill`。它本身不执行搜索运动，只做“定位置 + 还参数 + 切状态”。`Busy` 在 `Execute` 上升沿后"
        "置 `TRUE`，`Active` 表示命令正在执行；成功后 `Done = TRUE`，被抢占 / 停止时 `CommandAborted = TRUE`，"
        "出错 `Error = TRUE` 给出 `ErrorID`。典型用法：用 `MC_StepReferencePulse` 等 step 函数搜到参考点后，"
        "用本 FB 把那一点定义为某个绝对坐标值并收尾；或纯静态场景下不走 step，直接以本 FB 把当前停车点设为已知坐标。"),
    s5=[("`SetPosition` 是绝对值，不是偏移量；它会覆盖轴当前位置读数，写错会让后续所有绝对定位偏移 ⚠️。", False),
        ("本 FB 不产生运动，因此不存在撞限位风险，但定位置前要确认轴确实停在 `SetPosition` 对应的物理点。", False),
        ("`Parameter` 必须是贯穿整条序列的同一个 `MC_HomingParameter` 实例，否则参数还原不正确。", False),
        ("`BufferMode` 当前未实现。", False),
        ("纯静态归零（无 step 搜索）也要保证 `Parameter.Stored` 状态正确，否则可能报 `MC_HOMINGERROR_PARAMETER_NOTSTORED`。", False)],
    s7=("- **场景**：编码器零脉冲搜索成功后，把那一点定义为机床坐标 0；或操作员手动把轴拖到已知工件原点后"
        "用本 FB 直接置位收尾。\n"
        "- **价值**：把“设位置 + 还原参数 + 切回 Standstill”封装为一个 FB，比手动写 NC 通道置位命令省事且不漏还原参数。\n"
        "- **替代方案对比**：`MC_FinishHoming`（保留搜到的位置、不强制改写为指定值，可带退离运动）；"
        "Tc2_MC2 的 `MC_Home(HomingMode := MC_Direct)`（固定序列里的直接置位）。本 FB 用于自定义序列里的“指定绝对值”收尾。"),
    ex_extra={"SetPosition": ("LREAL", "0.0", "把搜到的参考点定义为机床坐标 0")},
    ex_scene=("// 场景：自定义归零序列里，前级 step 函数搜到编码器零脉冲并 Done 后，用本 FB 把该点\n"
              "//       直接定义为机床坐标 0，同时还原被改的参数并把轴切回 Standstill。\n"
              "// 价值：相比手写 NC 置位命令，本 FB 一并完成置位+还参数+切状态，避免漏还原导致后续定位异常。\n"
              "// 验证：先让前级 step Done；在线写 bSetZeroReq := TRUE，观察 bSetZeroDone 短暂 TRUE，\n"
              "//       axisHoming.NcToPlc 位置读数被改写为 0，轴状态从 Homing 进入 Standstill。"),
)

add(
    name="MC_AbortHoming", topic="427719051", category="Finalizing functions",
    sec="3.1.3",
    s1=("归零序列的**异常收尾功能块**。当一条自定义归零序列中的 step 函数报错或被中止时，调用本 FB 来"
        "中止整条序列：它把序列中被临时修改的 NC / 驱动参数还原为原值，并把轴状态从 `Homing` 切回 "
        "`Standstill`。与 `MC_FinishHoming` 成对使用——前者用于成功分支，本 FB 用于失败分支。"),
    inputs=[
        ("Execute", "BOOL", "Execute"),
        ("Options", "ST_Home_Options2", OPT2_DESC),
    ],
    in_out=[("Axis", "AXIS_REF", "Axis"), ("Parameter", "MC_HomingParameter", "Parameter")],
    outputs=[("Done", "BOOL", "Done"), ("Busy", "BOOL", "Busy"),
             ("CommandAborted", "BOOL", "CommandAborted"), ("Error", "BOOL", "Error"),
             ("ErrorID", "UDINT", "ErrorID")],
    s3=("`Execute` 上升沿启动中止收尾。本 FB 属 finalizing 类：按 PDF 第 3.1.3 节，它终止当前归零序列，"
        "把被各 step 函数临时修改的 NC / 驱动参数依据 `Parameter`（`MC_HomingParameter`）还原回备份值，"
        "并把轴状态由 `Homing` 切回 `Standstill`。它不执行搜索也不下发定位运动，只做“安全收尾 + 参数还原”。"
        "`Busy` 在 `Execute` 上升沿后置 `TRUE`，收尾完成后 `Done = TRUE`；若收尾本身被抢占则 `CommandAborted = TRUE`，"
        "出错 `Error = TRUE` 给出 `ErrorID`。典型用法：在序列状态机里监视 step 函数的 `Error` / `CommandAborted`，"
        "一旦置位就转去调用本 FB，确保哪怕归零失败也不把临时参数残留在 NC / 驱动里（否则后续运动会异常）。"),
    s5=[("即使归零没成功，也**必须**调用本 FB（或 `MC_FinishHoming`）收尾，否则临时改过的参数残留，后续运动可能报跟随误差或限速异常 ⚠️。", False),
        ("`Parameter` 必须是贯穿整条序列的同一个 `MC_HomingParameter` 实例，否则无法还原。", False),
        ("本 FB 不停止正在进行的运动；如果 step 还在动，应先用 `MC_Stop` 停轴再 `MC_AbortHoming`（工程经验补充）。", True),
        ("收尾后轴回到 `Standstill` 但仍未校准，需重新发起归零序列。", False),
        ("`Options.DisableDriveAccess` 必须与序列中 step 函数所用设置一致，否则驱动参数还原可能不完整。", False)],
    s7=("- **场景**：归零序列中 `MC_StepBlock` 顶撞块超时报错，需要安全中止并把被改的转矩限制等参数还原。\n"
        "- **价值**：保证“归零失败也能干净收场”，避免临时参数（限速、限矩、关掉的跟随监控）残留导致设备后续异常。\n"
        "- **替代方案对比**：`MC_FinishHoming`（成功分支收尾，可带退离运动）。本 FB 专用于失败 / 中止分支，"
        "二者通常在同一状态机里按 step 函数结果二选一调用。"),
    ex_extra={},
    ex_scene=("// 场景：自定义归零序列里，前级 step 函数报错或被中止后，用本 FB 安全中止整条序列，\n"
              "//       把被临时修改的 NC/驱动参数（如限矩、关掉的跟随监控）还原并切回 Standstill。\n"
              "// 价值：归零失败时若不收尾，临时参数残留会让后续正常运动报跟随误差/限速异常；本 FB 防止该残留。\n"
              "// 验证：模拟前级失败（bStepError := TRUE）后，在线写 bAbortReq := TRUE，观察 bAbortDone\n"
              "//       短暂 TRUE，axisHoming 状态从 Homing 回到 Standstill，参数恢复原值。"),
)

# ---------- 3.2 Referencing (passive / flying) ----------
add(
    name="MC_AbortPassiveHoming", topic="427752331", category="Referencing functions (passive)",
    sec="3.2.1",
    s1=("**取消被动（flying）归零**的功能块。被动归零（`MC_StepReferenceFlyingSwitch` / "
        "`MC_StepReferenceFlyingRefPulse`）是在机器正常运行中后台等待参考信号、不影响状态机的“飞行”归零；"
        "本 FB 用于在还没等到参考信号时主动取消这类被动归零请求。它不改变轴的运动状态，"
        "可在任意运动状态下调用（类似管理类 FB）。"),
    inputs=[
        ("Execute", "BOOL", "Execute"),
        ("Options", "ST_Home_Options", OPT0_DESC),
    ],
    in_out=[("Axis", "AXIS_REF", "Axis")],
    outputs=[("Done", "BOOL", "Done"), ("Busy", "BOOL", "Busy"), ("Active", "BOOL", "Active"),
             ("CommandAborted", "BOOL", "CommandAborted"), ("Error", "BOOL", "Error"),
             ("ErrorID", "UDINT", "ErrorID")],
    s3=("`Execute` 上升沿触发取消。被动 flying 归零 FB 在执行时只是在后台“挂起”等待参考信号到来"
        "（不启动也不修改任何运动、不进入 `Homing` 状态、不影响 PLCopen 状态机）；如果在信号到来前"
        "需要放弃这次归零等待，就调用本 FB。按 PDF 第 3.2.1 节，本 FB 同样不改变轴的运动状态，"
        "因此和管理类 FB 一样可在任意运动状态下调用。`Busy` 在 `Execute` 上升沿后置 `TRUE`，`Active` 表示"
        "正在执行取消；取消成功后 `Done = TRUE`，被抢占时 `CommandAborted = TRUE`，出错 `Error = TRUE` 给 `ErrorID`。"
        "典型用法：在“飞行抓参考点”逻辑里设一个看门狗，超过预期里程仍未抓到信号就调本 FB 撤销，"
        "让被占用的锁存（touch probe）单元释放出来供其它用途。"),
    s5=[("本 FB 只取消被动 flying 归零，不影响主动 step 归零序列；用错对象不会报错但也不起作用。", False),
        ("取消后被动归零 FB 的 `CommandAborted` 会置位，应在逻辑里据此复位飞行归零请求。", False),
        ("`Options`（`ST_Home_Options`）当前未使用，传默认即可。", False),
        ("由于不改运动状态，调用本 FB 不会让运行中的轴停下；它只撤销后台的信号等待（工程经验补充）。", True),
        ("被动归零占用编码器锁存单元，长时间不取消会阻塞其它需要同一 touch probe 的功能 ⚠️。", False)],
    s7=("- **场景**：飞剪 / 收放卷设备在运行中后台等待一次参考开关脉冲来重新对零，超时未等到时撤销这次等待。\n"
        "- **价值**：及时释放被占用的编码器锁存单元，避免后台归零请求一直挂着阻塞其它锁存用途。\n"
        "- **替代方案对比**：直接复位 flying 归零 FB 的 `Execute` 并不保证 NC 侧锁存被释放；本 FB 是 PDF 指定的"
        "干净取消方式。"),
    ex_extra={},
    ex_scene=("// 场景：收放卷设备运行中用 MC_StepReferenceFlyingSwitch 后台等待参考开关脉冲对零，\n"
              "//       但本批料已走完仍未等到信号，需要撤销这次飞行归零等待以释放编码器锁存单元。\n"
              "// 价值：及时取消可让 touch probe 单元空出来供其它功能使用，避免后台请求一直挂着。\n"
              "// 验证：在线写 bAbortFlyingReq := TRUE，观察 bAbortFlyingDone 短暂 TRUE；对应的飞行归零 FB\n"
              "//       的 CommandAborted 置位，说明等待已被取消（轴运动不受影响仍在走）。"),
)

add(
    name="MC_StepReferenceFlyingRefPulse", topic="427754251", category="Referencing functions (passive)",
    sec="3.2.2",
    s1=("**被动（flying）编码器零脉冲归零**功能块。它在机器正常运行（运动进行中）时执行，对编码器的"
        "零脉冲（zero pulse / reference pulse）做参考：抓到零脉冲那一刻把轴位置设为 `SetPosition`。"
        "本 FB 自身**不启动也不修改任何运动**，只是后台监听参考信号，因此不进入 `Homing` 状态、"
        "不影响 PLCopen 状态机。"),
    inputs=[
        ("Execute", "BOOL", "Execute"),
        ("ReferenceSignal", "MC_Ref_Signal_Ref", "ReferenceSignal"),
        ("SetPosition", "LREAL", "SetPosition"),
        ("TimeLimit", "TIME", "TimeLimit"),
        ("DistanceLimit", "LREAL", "DistanceLimit"),
        ("BufferMode", "MC_BufferMode", "BufferMode"),
        ("Options", "ST_Home_Options", OPT0_DESC),
    ],
    in_out=[("Axis", "AXIS_REF", "Axis")],
    outputs=[("Done", "BOOL", "Done"), ("Busy", "BOOL", "Busy"), ("Active", "BOOL", "Active"),
             ("CommandAborted", "BOOL", "CommandAborted"), ("Error", "BOOL", "Error"),
             ("ErrorID", "UDINT", "ErrorID")],
    s3=("`Execute` 上升沿启动后台监听。按 PDF 第 3.2.2 节，本 FB 在运动进行中对编码器零脉冲做参考，"
        "**它本身不产生任何运动**——运动由其它 Move FB 提供，本 FB 只通过 `ReferenceSignal` 配置的锁存单元"
        "（touch probe）等待零脉冲事件。零脉冲到达瞬间，NC 把轴当前位置锁存并设为 `SetPosition`，`Done = TRUE`。"
        "若超过 `TimeLimit` 时间、或相对启动点移动超过 `DistanceLimit` 距离仍没抓到零脉冲，则搜索中止，"
        "`CommandAborted` 置位。`Busy` 在 `Execute` 上升沿后置 `TRUE`，`Active` 表示监听中。"
        "由于不进入 `Homing` 状态、不改运动状态，本 FB 可像管理类 FB 一样在任意运动状态下调用，适合“边走边对零”。"),
    s5=[("本 FB 不发运动；必须由别的 Move FB 让轴动起来经过零脉冲，否则永远抓不到信号、最终 `TimeLimit` 超时中止 ⚠️。", False),
        ("`SetPosition` 是抓到零脉冲那一点的绝对坐标，不是当前位置偏移。", False),
        ("`ReferenceSignal.TouchProbe` 必须选对应零脉冲的锁存单元，选错会一直抓不到。", False),
        ("`TimeLimit` / `DistanceLimit` 要留足，使运动确实能在限制内跨过至少一个零脉冲。", False),
        ("放弃等待时用 `MC_AbortPassiveHoming` 取消，以释放锁存单元。", False)],
    s7=("- **场景**：连续运转的辊轴 / 转台，不停机的情况下利用每转一次的编码器零脉冲在线重新对零，消除累积漂移。\n"
        "- **价值**：归零与生产运动并行，不必停机走专门的归零序列；零脉冲精度远高于普通接近开关。\n"
        "- **替代方案对比**：`MC_StepReferencePulse`（主动版，自己发运动找零脉冲、要进 Homing 状态、停机）；"
        "`MC_StepReferenceFlyingSwitch`（飞行版但用外部开关而非零脉冲）。本 FB 用于运行中飞抓零脉冲。"),
    ex_extra={"SetPosition": ("LREAL", "0.0", "抓到零脉冲那一点设为坐标 0"),
              "TimeLimit": ("TIME", "T#5S", "5 秒内必须跨过一个零脉冲，否则中止"),
              "DistanceLimit": ("LREAL", "360.0", "相对启动点最多走 360（约一转）仍未抓到则中止")},
    ex_scene=("// 场景：连续运转的转台不停机，用编码器每转一次的零脉冲在线重新对零，消除累积漂移。\n"
              "//       本 FB 只后台监听，转台由别的 Move 命令持续旋转。\n"
              "// 价值：归零与生产并行无需停机；零脉冲精度高于普通接近开关。\n"
              "// 验证：保证转台正在转（别的 Move 在动）；在线写 bFlyingRefReq := TRUE，观察 bFlyingRefActive\n"
              "//       TRUE；转过一个零脉冲后 bFlyingRefDone 短暂 TRUE，轴位置读数被设为 0。5 秒没抓到则 bAborted。"),
)

add(
    name="MC_StepReferenceFlyingSwitch", topic="427756555", category="Referencing functions (passive)",
    sec="3.2.3",
    s1=("**被动（flying）外部开关归零**功能块。它在机器运行（运动进行中）时执行，对一个绝对安装的外部"
        "物理开关做参考：开关按 `SwitchMode` 给定的条件触发那一刻，把轴位置设为 `SetPosition`。"
        "本 FB 自身**不启动也不修改任何运动**，只后台监听开关信号，不进入 `Homing` 状态、不影响 PLCopen 状态机。"),
    inputs=[
        ("Execute", "BOOL", "Execute"),
        ("SwitchMode", "BOOL", "SwitchMode"),
        ("ReferenceSignal", "MC_Ref_Signal_Ref", "ReferenceSignal"),
        ("SetPosition", "LREAL", "SetPosition"),
        ("TimeLimit", "TIME", "TimeLimit"),
        ("DistanceLimit", "LREAL", "DistanceLimit"),
        ("BufferMode", "MC_BufferMode", "BufferMode"),
        ("Options", "ST_Home_Options", OPT0_DESC),
    ],
    in_out=[("Axis", "AXIS_REF", "Axis")],
    outputs=[("Done", "BOOL", "Done"), ("Busy", "BOOL", "Busy"), ("Active", "BOOL", "Active"),
             ("CommandAborted", "BOOL", "CommandAborted"), ("Error", "BOOL", "Error"),
             ("ErrorID", "UDINT", "ErrorID")],
    s3=("`Execute` 上升沿启动后台监听。按 PDF 第 3.2.3 节，本 FB 在运动进行中通过一个绝对定位的外部物理开关"
        "做参考，**它本身不产生任何运动**——运动由其它 Move FB 提供。`SwitchMode`（`MC_Switch_Mode` 枚举）"
        "定义结束条件（如上升沿 / 下降沿 / 电平），`ReferenceSignal` 配置锁存单元与开关电平来源。"
        "满足结束条件那一刻 NC 锁存轴位置并设为 `SetPosition`，`Done = TRUE`；超过 `TimeLimit` 或相对启动点"
        "移动超过 `DistanceLimit` 仍未触发则 `CommandAborted` 置位。`Busy` / `Active` 指示监听进行中。"
        "本 FB 不进入 `Homing`、不改运动状态，可在任意运动状态调用，适合运行中飞抓开关对零。"
        "⚠️ 提示：PDF 第 3.2.3 节正文的 `VAR_INPUT` 代码块把 `SwitchMode` 印为 `BOOL`（本文档 §2 逐字照搬该代码块为 "
        "`BOOL`），但同节的接口图与参数说明表均把 `SwitchMode` 标为枚举 `MC_Switch_Mode`；实际工程中应按 "
        "`MC_Switch_Mode` 枚举语义理解该入口（定义开关触发的结束条件），代码块中的 `BOOL` 系 PDF 笔误。"),
    s5=[("本 FB 不发运动；必须由别的 Move FB 让轴动起来经过开关，否则抓不到信号、`TimeLimit` 超时中止 ⚠️。", False),
        ("`SwitchMode` 要与开关物理特性匹配（常开 / 常闭、上升 / 下降沿），选错会在错误时机锁位置。", False),
        ("`SetPosition` 是触发那一点的绝对坐标。", False),
        ("外部开关有机械 / 电气抖动时，应在 `ReferenceSignal` / 接线侧做滤波，否则可能锁到抖动沿导致位置偏差 ⚠️。", False),
        ("放弃等待时用 `MC_AbortPassiveHoming` 取消以释放锁存单元。", False)],
    s7=("- **场景**：往复运行的输送 / 飞剪机构，运行中经过一个固定参考开关时在线对零，不停机。\n"
        "- **价值**：开关比零脉冲更易加装、定位灵活；飞行抓取使对零与生产并行。\n"
        "- **替代方案对比**：`MC_StepReferenceFlyingRefPulse`（飞行版但用编码器零脉冲，精度更高）；"
        "`MC_StepAbsoluteSwitch`（主动版，自己发运动找开关、进 Homing 状态、停机）。本 FB 用于运行中飞抓外部开关。"),
    ex_extra={"SetPosition": ("LREAL", "0.0", "开关触发那一点设为坐标 0"),
              "TimeLimit": ("TIME", "T#5S", "5 秒内必须触发开关，否则中止"),
              "DistanceLimit": ("LREAL", "1000.0", "相对启动点最多走 1000 仍未触发则中止")},
    ex_scene=("// 场景：往复输送机构运行中经过一个固定安装的参考开关时在线对零，全程不停机。\n"
              "//       本 FB 只后台监听开关，输送运动由别的 Move 命令提供。\n"
              "// 价值：对零与生产并行无需停机；外部开关易加装、安装位置灵活。\n"
              "// 验证：保证输送轴正在走；在线写 bFlyingSwReq := TRUE，观察 bFlyingSwActive TRUE；轴经过\n"
              "//       开关并触发参考条件时 bFlyingSwDone 短暂 TRUE，轴位置读数被设为 0。"),
    ex_skip=["SwitchMode"],  # PDF 代码块把 SwitchMode 误印为 BOOL，非真实接口项，例程中省略
)

# ---------- 3.3 Step functions ----------
add(
    name="MC_StepAbsoluteSwitch", topic="427758475", category="Step functions",
    sec="3.3.1",
    s1=("**主动归零 step 函数：搜索绝对参考开关（reference cam）**。它驱动轴运动去寻找一个绝对安装的外部"
        "物理开关（参考凸轮）。一般绝对开关有两个“关”区和一个“开”区；若开关不可越过则只有一个“关”区和一个“开”区。"
        "搜到开关满足 `SwitchMode` 条件后把轴位置设为 `SetPosition`。本 FB 在 `Homing` 状态执行，"
        "完成后轴仍停留在 `Homing` 状态，需配 finalizing FB 收尾。"),
    inputs=[
        ("Execute", "BOOL", "Execute"),
        ("Direction", "MC_Home_Direction", "Direction"),
        ("SwitchMode", "MC_Switch_Mode", "SwitchMode"),
        ("ReferenceSignal", "MC_Ref_Signal_Ref", "ReferenceSignal"),
        ("Velocity", "LREAL", "Velocity"),
        ("Acceleration", "LREAL", "Acceleration"),
        ("Deceleration", "LREAL", "Deceleration"),
        ("Jerk", "LREAL", "Jerk"),
        ("SetPosition", "LREAL", "SetPosition"),
        ("TimeLimit", "TIME", "TimeLimit"),
        ("DistanceLimit", "LREAL", "DistanceLimit"),
        ("TorqueLimit", "LREAL", "TorqueLimit"),
        ("PositiveLimitSwitch", "BOOL", "PositiveLimitSwitch"),
        ("NegativeLimitSwitch", "BOOL", "NegativeLimitSwitch"),
        ("BufferMode", "MC_BufferMode", "BufferMode"),
        ("Options", "ST_Home_Options4", OPT4_DESC),
    ],
    in_out=[("Axis", "AXIS_REF", "Axis"), ("Parameter", "MC_HomingParameter", "Parameter")],
    outputs=[("Done", "BOOL", "Done"), ("Busy", "BOOL", "Busy"), ("Active", "BOOL", "Active"),
             ("CommandAborted", "BOOL", "CommandAborted"), ("Error", "BOOL", "Error"),
             ("ErrorID", "UDINT", "ErrorID")],
    s3=("`Execute` 上升沿启动搜索。按 PDF 第 3.3.1 节，本 FB 主动驱动轴去找绝对参考开关："
        "起始方向由 `Direction`（`MC_Home_Direction`）决定，轴按 `Velocity` / `Acceleration` / "
        "`Deceleration` / `Jerk` 运动；遇到行程极限传感器（`PositiveLimitSwitch` / `NegativeLimitSwitch`）"
        "或满足 `mcSwitch*` 方向条件时可反向。`SwitchMode`（`MC_Switch_Mode`）定义结束条件，"
        "`ReferenceSignal` 给出参考凸轮信号源；满足结束条件时把轴位置设为 `SetPosition`，`Done = TRUE`。"
        "搜索运动以 `TorqueLimit` 限矩、step 函数默认关闭跟随误差监控（可经 `Options.EnableLagErrorDetection` 打开）。"
        "超过 `TimeLimit` 或相对起点移动超过 `DistanceLimit` 则 `CommandAborted` 置位。"
        "本 FB 把轴置于 / 保持在 `Homing` 状态，序列结束后仍停在 `Homing`，必须再调 `MC_FinishHoming`（成功）"
        "或 `MC_AbortHoming`（失败）才能切回 `Standstill`。`Parameter`（`MC_HomingParameter`）在整条序列各 FB 间逐级传递。"),
    s5=[("`Direction` 起始方向选错会先撞向远离开关的一侧，可能直接顶上硬限位 ⚠️ —— 必须按机械布置选对方向。", False),
        ("必须正确接入 `PositiveLimitSwitch` / `NegativeLimitSwitch`，否则反向逻辑失效，轴可能越过开关撞硬限位 ⚠️。", False),
        ("`TorqueLimit` 设太低会在正常搜索运动中误判堵转 / 走不动；设太高失去撞击保护意义。", False),
        ("参考凸轮开关有抖动时要在 `ReferenceSignal` / 接线侧滤波，避免锁到抖动沿。", False),
        ("结束后轴停在 `Homing`，忘记调收尾 FB 会导致临时参数不还原、状态卡在 `Homing` ⚠️。", False)],
    s7=("- **场景**：龙门 / 直线轴用一个安装在行程中段的参考凸轮开关归零，两端有硬件限位保护。\n"
        "- **价值**：把“向参考凸轮运动 + 到限位反向 + 满足条件定零”整套搜索逻辑封装为一段可拼接的 step；"
        "配合 finalizing FB 可组成完全自定义的归零序列。\n"
        "- **替代方案对比**：`MC_StepAbsoluteSwitchDetection`（同样找开关但只返回检测位置、不改写轴位置）；"
        "`MC_StepLimitSwitch`（找硬件限位开关而非中段参考凸轮）。"),
    ex_extra={"Velocity": ("LREAL", "50.0", "搜索速度（用户单位/秒）"),
              "SetPosition": ("LREAL", "0.0", "找到参考凸轮后定为坐标 0"),
              "TimeLimit": ("TIME", "T#30S", "30 秒内必须找到，否则中止"),
              "DistanceLimit": ("LREAL", "2000.0", "搜索行程上限"),
              "TorqueLimit": ("LREAL", "100.0", "限矩，防误撞损坏（按驱动转矩刻度）"),
              "Acceleration": ("LREAL", "0.0", "0 表示用轴配置标准加速度"),
              "Deceleration": ("LREAL", "0.0", "0 表示用轴配置标准减速度"),
              "Jerk": ("LREAL", "0.0", "0 表示用轴配置标准急动度")},
    ex_scene=("// 场景：龙门直线轴用行程中段的参考凸轮开关归零，两端有硬件限位保护。本 FB 驱动轴朝负向\n"
              "//       搜索凸轮，遇限位会反向，命中凸轮上升沿后把该点定为坐标 0。\n"
              "// 价值：把“搜凸轮+到限位反向+定零”封装为可拼接 step，配收尾 FB 组成完整自定义归零序列。\n"
              "// 验证：先 MC_Power 使能轴；在线写 bSearchReq := TRUE，观察 bSearchActive TRUE，轴朝负向\n"
              "//       移动；命中凸轮后 bSearchDone 短暂 TRUE，位置读数变 0，轴仍停在 Homing 状态（需再收尾）。"),
    ex_enum={"Direction": ("MC_Home_Direction", "mcNegativeDirection", "起始向逻辑负方向搜索"),
             "SwitchMode": ("MC_Switch_Mode", "mcRisingEdge", "凸轮上升沿作为结束条件")},
    ex_limit=True,
)

add(
    name="MC_StepAbsoluteSwitchDetection", topic="427760395", category="Step functions",
    sec="3.3.2",
    s1=("**主动归零 step 函数：搜索绝对参考开关并仅返回检测位置（Detection 版）**。搜索逻辑与 "
        "`MC_StepAbsoluteSwitch` 相同（找绝对安装的外部参考凸轮），但本 Detection 版**不改写轴的当前位置**，"
        "而是把检测到开关的那一刻轴位置通过 `RecordedPosition` 返回给用户，由用户自行决定如何使用该值。"),
    inputs=[
        ("Execute", "BOOL", "Execute"),
        ("Direction", "MC_Home_Direction", "Direction"),
        ("SwitchMode", "MC_Switch_Mode", "SwitchMode"),
        ("ReferenceSignal", "MC_Ref_Signal_Ref", "ReferenceSignal"),
        ("Velocity", "LREAL", "Velocity"),
        ("Acceleration", "LREAL", "Acceleration"),
        ("Deceleration", "LREAL", "Deceleration"),
        ("Jerk", "LREAL", "Jerk"),
        ("TimeLimit", "TIME", "TimeLimit"),
        ("DistanceLimit", "LREAL", "DistanceLimit"),
        ("TorqueLimit", "LREAL", "TorqueLimit"),
        ("PositiveLimitSwitch", "BOOL", "PositiveLimitSwitch"),
        ("NegativeLimitSwitch", "BOOL", "NegativeLimitSwitch"),
        ("BufferMode", "MC_BufferMode", "BufferMode"),
        ("Options", "ST_Home_Options4", OPT4_DESC),
    ],
    in_out=[("Axis", "AXIS_REF", "Axis"), ("Parameter", "MC_HomingParameter", "Parameter")],
    outputs=[("Done", "BOOL", "Done"), ("Busy", "BOOL", "Busy"), ("Active", "BOOL", "Active"),
             ("CommandAborted", "BOOL", "CommandAborted"), ("Error", "BOOL", "Error"),
             ("ErrorID", "UDINT", "ErrorID"), ("RecordedPosition", "LREAL", "RecordedPosition")],
    s3=("`Execute` 上升沿启动搜索。搜索过程与 `MC_StepAbsoluteSwitch` 完全一致：按 `Direction` 起始方向、"
        "`Velocity` / `Acceleration` / `Deceleration` / `Jerk` 动力学驱动轴找绝对参考凸轮，遇 "
        "`PositiveLimitSwitch` / `NegativeLimitSwitch` 反向，`SwitchMode` 定义结束条件，`ReferenceSignal` "
        "给信号源，`TorqueLimit` 限矩。区别在于：按 PDF 第 3.3.2 节，本 Detection 版**不会把轴位置改写为某个值**，"
        "而是把检测到开关那一刻的轴位置写入输出 `RecordedPosition` 返回给用户（因此没有 `SetPosition` 入口）。"
        "`Done = TRUE` 表示检测成功并已给出 `RecordedPosition`；超过 `TimeLimit` / `DistanceLimit` 则 "
        "`CommandAborted` 置位。本 FB 同样在 `Homing` 状态执行、结束后保持 `Homing`，需配收尾 FB；"
        "`Parameter` 在序列各 FB 间逐级传递。Detection 版常用于先测量参考点偏差、再由用户决定置零策略的场景。"),
    s5=[("本 FB**不改写轴位置**，只给出 `RecordedPosition`；若忘了用这个值去置零，轴仍未真正校准 ⚠️。", False),
        ("`Direction` 起始方向选错可能先撞硬限位，务必结合 `PositiveLimitSwitch` / `NegativeLimitSwitch` 接线 ⚠️。", False),
        ("`TorqueLimit` 设置同 `MC_StepAbsoluteSwitch`：过低误判、过高失保护。", False),
        ("参考凸轮抖动需滤波，否则 `RecordedPosition` 会偏。", False),
        ("结束后轴停在 `Homing`，仍需 `MC_FinishHoming` / `MC_AbortHoming` 收尾。", False)],
    s7=("- **场景**：需要先测出参考凸轮相对当前坐标的实际位置（做机械装配偏差检查 / 多轴对齐），再由上层决定如何置零。\n"
        "- **价值**：把“测量”与“置零”解耦——本 FB 只负责精确测出开关位置，置零策略交给用户，灵活性更高。\n"
        "- **替代方案对比**：`MC_StepAbsoluteSwitch`（找到即改写轴位置为 `SetPosition`，一步到位）。"
        "需要拿测量值做进一步判断时用本 Detection 版。"),
    ex_extra={"Velocity": ("LREAL", "20.0", "搜索速度"),
              "TimeLimit": ("TIME", "T#30S", "搜索超时上限"),
              "DistanceLimit": ("LREAL", "2000.0", "搜索行程上限"),
              "TorqueLimit": ("LREAL", "100.0", "限矩保护"),
              "Acceleration": ("LREAL", "0.0", "0 用轴配置标准值"),
              "Deceleration": ("LREAL", "0.0", "0 用轴配置标准值"),
              "Jerk": ("LREAL", "0.0", "0 用轴配置标准值")},
    ex_scene=("// 场景：多轴装配前先测出参考凸轮相对当前坐标的实际位置做机械偏差检查，由本 FB 返回\n"
              "//       RecordedPosition，上层据此决定是否置零、置多少。本 FB 不改写轴位置。\n"
              "// 价值：测量与置零解耦——本 FB 只精确测开关位置，置零策略交给上层，便于做对齐判断。\n"
              "// 验证：先 MC_Power 使能；在线写 bDetectReq := TRUE，观察 bDetectActive TRUE，轴朝负向走；\n"
              "//       命中凸轮后 bDetectDone 短暂 TRUE，lrRecordedPos 显示检测到的位置值（轴位置读数不变）。"),
    ex_enum={"Direction": ("MC_Home_Direction", "mcNegativeDirection", "起始向逻辑负方向搜索"),
             "SwitchMode": ("MC_Switch_Mode", "mcRisingEdge", "凸轮上升沿作为结束条件")},
    ex_limit=True,
)

# Block family share structure
def block_s3(extra_cond):
    return ("`Execute` 上升沿启动搜索。本 FB 驱动轴朝 `Direction` 方向运动去顶一个机械固定止挡（撞块），"
            "为避免损坏机械，运动以 `TorqueLimit` 限矩进行。" + extra_cond +
            "满足上述两个条件即判定已顶到止挡。`Velocity` / `Acceleration` / `Deceleration` / `Jerk` 定义"
            "搜索运动动力学；超过 `TimeLimit` 或相对起点移动超 `DistanceLimit` 则 `CommandAborted` 置位。"
            "`Options`（`ST_Home_Options3`）的 `InstantLagReduction` 用于顶到“软”止挡突停后瞬时消除跟随误差。"
            "本 FB 在 `Homing` 状态执行、结束后保持 `Homing`，需配 `MC_FinishHoming` / `MC_AbortHoming` 收尾；"
            "`Parameter`（`MC_HomingParameter`）在序列各 FB 间逐级传递。")

BLOCK_S5 = [
    ("顶撞块归零靠主动撞机械止挡完成，`TorqueLimit` 必须设得足够低以免撞坏机械，但又要高于正常搜索摩擦阻力 ⚠️。", False),
    ("`Direction` 选错会朝远离止挡的方向运动，可能撞上另一侧硬限位 ⚠️。", False),
    ("`DetectionVelocityTime` 太短可能在加减速波动中误判堵转；太长会延迟检测。", False),
    ("“软”止挡突停产生的跟随误差较大，按需置 `Options.InstantLagReduction := TRUE` 让其瞬时消除。", False),
    ("结束后轴停在 `Homing` 且压在止挡上，收尾 FB 通常带退离 `Distance` 把轴从止挡松开（用 `MC_FinishHoming`）。", False),
]

add(
    name="MC_StepBlock", topic="427762315", category="Step functions",
    sec="3.3.3",
    s1=("**主动归零 step 函数：撞机械固定止挡（home on block，转矩+速度判据）**。它驱动轴去顶一个机械"
        "固定止挡，用减小的转矩（`TorqueLimit`）避免损坏机械。成功判据由两部分组成：转矩进入 "
        "`TorqueTolerance` 容差带且贴近 `TorqueLimit`，同时实际速度在 `DetectionVelocityTime` 时间内"
        "持续低于 `DetectionVelocityLimit`。顶到止挡后把轴位置设为 `SetPosition`。"),
    inputs=[
        ("Execute", "BOOL", "Execute"),
        ("Direction", "MC_Home_Direction", "Direction"),
        ("Velocity", "LREAL", "Velocity"),
        ("Acceleration", "LREAL", "Acceleration"),
        ("Deceleration", "LREAL", "Deceleration"),
        ("Jerk", "LREAL", "Jerk"),
        ("SetPosition", "LREAL", "SetPosition"),
        ("DetectionVelocityLimit", "LREAL", "DetectionVelocityLimit"),
        ("DetectionVelocityTime", "TIME", "DetectionVelocityTime"),
        ("TimeLimit", "TIME", "TimeLimit"),
        ("DistanceLimit", "LREAL", "DistanceLimit"),
        ("TorqueLimit", "LREAL", "TorqueLimit"),
        ("TorqueTolerance", "LREAL", "TorqueTolerance"),
        ("BufferMode", "MC_BufferMode", "BufferMode"),
        ("Options", "ST_Home_Options3", OPT3_DESC),
    ],
    in_out=[("Axis", "AXIS_REF", "Axis"), ("Parameter", "MC_HomingParameter", "Parameter")],
    outputs=[("Done", "BOOL", "Done"), ("Busy", "BOOL", "Busy"), ("Active", "BOOL", "Active"),
             ("CommandAborted", "BOOL", "CommandAborted"), ("Error", "BOOL", "Error"),
             ("ErrorID", "UDINT", "ErrorID")],
    s3=block_s3("成功条件由两部分组成：其一，实际转矩进入 `TorqueTolerance` 容差带并贴近 `TorqueLimit`；"
                "其二，实际速度在 `DetectionVelocityTime` 时间内持续低于 `DetectionVelocityLimit`。"
                "二者同时满足才判定顶到止挡，随后把轴位置设为 `SetPosition`，`Done = TRUE`。"),
    s5=BLOCK_S5,
    s7=("- **场景**：无参考开关 / 无零脉冲的简单机构（如夹爪、推料气缸式电动轴）用撞机械硬止挡来定零。\n"
        "- **价值**：不需要额外传感器，靠转矩+速度双判据判断顶到止挡，省去开关接线与调试。\n"
        "- **替代方案对比**：`MC_StepBlockLagBased`（用跟随误差而非转矩作判据，适合无转矩反馈的驱动）；"
        "`MC_StepBlockDetection`（只返回检测位置不置零）。本 FB 用转矩判据并直接置零。"),
    ex_extra={"Velocity": ("LREAL", "10.0", "顶止挡的低速搜索速度"),
              "SetPosition": ("LREAL", "0.0", "顶到止挡后定为坐标 0"),
              "DetectionVelocityLimit": ("LREAL", "1.0", "速度低于此值判定为已顶住"),
              "DetectionVelocityTime": ("TIME", "T#200MS", "速度需持续低于上限 200ms"),
              "TimeLimit": ("TIME", "T#20S", "搜索超时上限"),
              "DistanceLimit": ("LREAL", "500.0", "搜索行程上限"),
              "TorqueLimit": ("LREAL", "30.0", "限矩 30%（按驱动转矩刻度），避免撞坏"),
              "TorqueTolerance": ("LREAL", "5.0", "转矩容差带"),
              "Acceleration": ("LREAL", "0.0", "0 用轴配置标准值"),
              "Deceleration": ("LREAL", "0.0", "0 用轴配置标准值"),
              "Jerk": ("LREAL", "0.0", "0 用轴配置标准值")},
    ex_scene=("// 场景：无开关无零脉冲的推料电动轴，用低速撞机械硬止挡来定零。限矩 30% 防撞坏，\n"
              "//       转矩达限且速度持续低于阈值即判定顶到止挡，把该点定为坐标 0。\n"
              "// 价值：省去开关接线与调试，靠转矩+速度双判据可靠判断顶到止挡。\n"
              "// 验证：先 MC_Power 使能；在线写 bBlockReq := TRUE，观察 bBlockActive TRUE，轴低速朝正向\n"
              "//       顶；顶到止挡转矩升到限值、速度跌到 1 以下持续 200ms 后 bBlockDone TRUE，位置读数变 0。"),
    ex_enum={"Direction": ("MC_Home_Direction", "mcPositiveDirection", "向逻辑正方向顶止挡")},
)

add(
    name="MC_StepBlockDetection", topic="427763851", category="Step functions",
    sec="3.3.4",
    s1=("**主动归零 step 函数：撞机械止挡（转矩+速度判据，Detection 版）**。搜索逻辑与 `MC_StepBlock` 相同"
        "（限矩顶止挡，转矩进容差带 + 速度持续低于限值双判据），但本 Detection 版**不改写轴位置**，"
        "而是把检测到止挡那一刻的轴位置通过 `RecordedPosition` 返回给用户。"),
    inputs=[
        ("Execute", "BOOL", "Execute"),
        ("Direction", "MC_Home_Direction", "Direction"),
        ("Velocity", "LREAL", "Velocity"),
        ("Acceleration", "LREAL", "Acceleration"),
        ("Deceleration", "LREAL", "Deceleration"),
        ("Jerk", "LREAL", "Jerk"),
        ("DetectionVelocityLimit", "LREAL", "DetectionVelocityLimit"),
        ("DetectionVelocityTime", "TIME", "DetectionVelocityTime"),
        ("TimeLimit", "TIME", "TimeLimit"),
        ("DistanceLimit", "LREAL", "DistanceLimit"),
        ("TorqueLimit", "LREAL", "TorqueLimit"),
        ("TorqueTolerance", "LREAL", "TorqueTolerance"),
        ("BufferMode", "MC_BufferMode", "BufferMode"),
        ("Options", "ST_Home_Options3", OPT3_DESC),
    ],
    in_out=[("Axis", "AXIS_REF", "Axis"), ("Parameter", "MC_HomingParameter", "Parameter")],
    outputs=[("Done", "BOOL", "Done"), ("Busy", "BOOL", "Busy"), ("Active", "BOOL", "Active"),
             ("CommandAborted", "BOOL", "CommandAborted"), ("Error", "BOOL", "Error"),
             ("ErrorID", "UDINT", "ErrorID"), ("RecordedPosition", "LREAL", "RecordedPosition")],
    s3=block_s3("成功条件由两部分组成：实际转矩进入 `TorqueTolerance` 容差带并贴近 `TorqueLimit`，"
                "且实际速度在 `DetectionVelocityTime` 内持续低于 `DetectionVelocityLimit`。"
                "区别在于按 PDF 第 3.3.4 节，本 Detection 版**不改写轴位置**，而是把检测到止挡那一刻的轴位置"
                "写入输出 `RecordedPosition` 返回（因此没有 `SetPosition` 入口）。"),
    s5=BLOCK_S5,
    s7=("- **场景**：需要先测出机械止挡相对当前坐标的实际位置（检查机械磨损 / 装配偏差），再由上层决定置零策略。\n"
        "- **价值**：把“顶止挡测量”与“置零”解耦，测量值经 `RecordedPosition` 返回供上层判断。\n"
        "- **替代方案对比**：`MC_StepBlock`（顶到即置零，一步到位）；`MC_StepBlockLagBasedDetection`"
        "（同为 Detection 但用跟随误差判据）。本 FB 用转矩判据并只返回位置。"),
    ex_extra={"Velocity": ("LREAL", "10.0", "顶止挡低速"),
              "DetectionVelocityLimit": ("LREAL", "1.0", "速度低于此判定顶住"),
              "DetectionVelocityTime": ("TIME", "T#200MS", "速度持续低于上限 200ms"),
              "TimeLimit": ("TIME", "T#20S", "搜索超时上限"),
              "DistanceLimit": ("LREAL", "500.0", "搜索行程上限"),
              "TorqueLimit": ("LREAL", "30.0", "限矩 30%"),
              "TorqueTolerance": ("LREAL", "5.0", "转矩容差带"),
              "Acceleration": ("LREAL", "0.0", "0 用轴配置标准值"),
              "Deceleration": ("LREAL", "0.0", "0 用轴配置标准值"),
              "Jerk": ("LREAL", "0.0", "0 用轴配置标准值")},
    ex_scene=("// 场景：检查机械止挡因磨损产生的位置漂移——本 FB 限矩顶到止挡后只返回 RecordedPosition，\n"
              "//       上层把它和历史基准比较判断磨损量，不直接改写轴位置。\n"
              "// 价值：顶止挡测量与置零解耦，便于做磨损/装配偏差监测。\n"
              "// 验证：先 MC_Power 使能；在线写 bBlockDetReq := TRUE，观察 bBlockDetActive TRUE，轴低速顶；\n"
              "//       顶到止挡后 bBlockDetDone TRUE，lrRecordedPos 显示止挡位置（轴位置读数不变）。"),
    ex_enum={"Direction": ("MC_Home_Direction", "mcPositiveDirection", "向逻辑正方向顶止挡")},
)

add(
    name="MC_StepBlockLagBased", topic="427765387", category="Step functions",
    sec="3.3.5",
    s1=("**主动归零 step 函数：撞机械止挡（跟随误差判据）**。它驱动轴去顶机械固定止挡，用减小的转矩"
        "（`TorqueLimit`）避免损坏机械。与 `MC_StepBlock` 不同，成功判据是：位置跟随误差超过 `LagLimit`，"
        "且实际速度在 `DetectionVelocityTime` 内持续低于 `DetectionVelocityLimit`。适合没有转矩反馈、"
        "但能监测跟随误差的驱动。顶到止挡后把轴位置设为 `SetPosition`。"),
    inputs=[
        ("Execute", "BOOL", "Execute"),
        ("Direction", "MC_Home_Direction", "Direction"),
        ("Velocity", "LREAL", "Velocity"),
        ("Acceleration", "LREAL", "Acceleration"),
        ("Deceleration", "LREAL", "Deceleration"),
        ("Jerk", "LREAL", "Jerk"),
        ("SetPosition", "LREAL", "SetPosition"),
        ("DetectionVelocityLimit", "LREAL", "DetectionVelocityLimit"),
        ("DetectionVelocityTime", "TIME", "DetectionVelocityTime"),
        ("TimeLimit", "TIME", "TimeLimit"),
        ("DistanceLimit", "LREAL", "DistanceLimit"),
        ("TorqueLimit", "LREAL", "TorqueLimit"),
        ("LagLimit", "LREAL", "LagLimit"),
        ("BufferMode", "MC_BufferMode", "BufferMode"),
        ("Options", "ST_Home_Options3", OPT3_DESC),
    ],
    in_out=[("Axis", "AXIS_REF", "Axis"), ("Parameter", "MC_HomingParameter", "Parameter")],
    outputs=[("Done", "BOOL", "Done"), ("Busy", "BOOL", "Busy"), ("Active", "BOOL", "Active"),
             ("CommandAborted", "BOOL", "CommandAborted"), ("Error", "BOOL", "Error"),
             ("ErrorID", "UDINT", "ErrorID")],
    s3=block_s3("成功条件由两部分组成：其一，位置跟随误差（lag error）超过 `LagLimit`；"
                "其二，实际速度在 `DetectionVelocityTime` 内持续低于 `DetectionVelocityLimit`。"
                "二者同时满足即判定顶到止挡，随后把轴位置设为 `SetPosition`，`Done = TRUE`。"
                "该判据基于跟随误差而非转矩，适合无转矩反馈的驱动。"),
    s5=BLOCK_S5 + [("`LagLimit` 要明显大于正常运动的跟随误差波动，否则会在还没顶到止挡时误判 ⚠️。", False)],
    s7=("- **场景**：第三方 / 简易驱动没有可用转矩反馈，但 NC 能算跟随误差，用撞止挡 + 跟随误差判据归零。\n"
        "- **价值**：不依赖转矩信号即可判断顶到止挡，扩大了 home-on-block 的适用驱动范围。\n"
        "- **替代方案对比**：`MC_StepBlock`（用转矩判据，需要转矩反馈）；`MC_StepBlockLagBasedDetection`"
        "（同为跟随误差判据但只返回检测位置）。本 FB 用跟随误差判据并直接置零。"),
    ex_extra={"Velocity": ("LREAL", "10.0", "顶止挡低速"),
              "SetPosition": ("LREAL", "0.0", "顶到止挡后定为坐标 0"),
              "DetectionVelocityLimit": ("LREAL", "1.0", "速度低于此判定顶住"),
              "DetectionVelocityTime": ("TIME", "T#200MS", "速度持续低于上限 200ms"),
              "TimeLimit": ("TIME", "T#20S", "搜索超时上限"),
              "DistanceLimit": ("LREAL", "500.0", "搜索行程上限"),
              "TorqueLimit": ("LREAL", "30.0", "限矩 30%"),
              "LagLimit": ("LREAL", "5.0", "跟随误差超此值判定顶住"),
              "Acceleration": ("LREAL", "0.0", "0 用轴配置标准值"),
              "Deceleration": ("LREAL", "0.0", "0 用轴配置标准值"),
              "Jerk": ("LREAL", "0.0", "0 用轴配置标准值")},
    ex_scene=("// 场景：第三方驱动无可用转矩反馈，但 NC 能算跟随误差。用低速撞机械止挡 + 跟随误差判据归零，\n"
              "//       跟随误差超 5 且速度持续低于阈值即判定顶到止挡，把该点定为坐标 0。\n"
              "// 价值：不依赖转矩信号即可做 home-on-block，扩大适用驱动范围。\n"
              "// 验证：先 MC_Power 使能；在线写 bLagBlockReq := TRUE，观察 bLagBlockActive TRUE，轴低速顶；\n"
              "//       顶到止挡跟随误差升到 >5 且速度跌到 1 以下持续 200ms 后 bLagBlockDone TRUE，位置读数变 0。"),
    ex_enum={"Direction": ("MC_Home_Direction", "mcPositiveDirection", "向逻辑正方向顶止挡")},
)

add(
    name="MC_StepBlockLagBasedDetection", topic="427766923", category="Step functions",
    sec="3.3.6",
    s1=("**主动归零 step 函数：撞机械止挡（跟随误差判据，Detection 版）**。搜索逻辑与 `MC_StepBlockLagBased` "
        "相同（限矩顶止挡，跟随误差超 `LagLimit` + 速度持续低于限值双判据），但本 Detection 版**不改写轴位置**，"
        "而是把检测到止挡那一刻的轴位置通过 `RecordedPosition` 返回给用户。"),
    inputs=[
        ("Execute", "BOOL", "Execute"),
        ("Direction", "MC_Home_Direction", "Direction"),
        ("Velocity", "LREAL", "Velocity"),
        ("Acceleration", "LREAL", "Acceleration"),
        ("Deceleration", "LREAL", "Deceleration"),
        ("Jerk", "LREAL", "Jerk"),
        ("SetPosition", "LREAL", "SetPosition"),
        ("DetectionVelocityLimit", "LREAL", "DetectionVelocityLimit"),
        ("DetectionVelocityTime", "TIME", "DetectionVelocityTime"),
        ("TimeLimit", "TIME", "TimeLimit"),
        ("DistanceLimit", "LREAL", "DistanceLimit"),
        ("TorqueLimit", "LREAL", "TorqueLimit"),
        ("LagLimit", "LREAL", "LagLimit"),
        ("BufferMode", "MC_BufferMode", "BufferMode"),
        ("Options", "ST_Home_Options3", OPT3_DESC),
    ],
    in_out=[("Axis", "AXIS_REF", "Axis"), ("Parameter", "MC_HomingParameter", "Parameter")],
    outputs=[("Done", "BOOL", "Done"), ("Busy", "BOOL", "Busy"), ("Active", "BOOL", "Active"),
             ("CommandAborted", "BOOL", "CommandAborted"), ("Error", "BOOL", "Error"),
             ("ErrorID", "UDINT", "ErrorID"), ("RecordedPosition", "LREAL", "RecordedPosition")],
    s3=block_s3("成功条件由两部分组成：位置跟随误差超过 `LagLimit`，且实际速度在 `DetectionVelocityTime` 内"
                "持续低于 `DetectionVelocityLimit`。区别在于按 PDF 第 3.3.6 节，本 Detection 版**不会把轴位置改写**，"
                "而是把检测到止挡那一刻的轴位置写入输出 `RecordedPosition` 返回。"
                "⚠️ 提示：PDF 第 3.3.6 节正文的 `VAR_INPUT` 代码块多印了一个 `SetPosition : LREAL`（本文档 §2 逐字照搬"
                "保留），但本 FB 是 Detection 版、其接口图不含 `SetPosition`，该入口对结果无效（Detection 版不改写轴位置），"
                "实际位置仅经 `RecordedPosition` 返回。"),
    s5=BLOCK_S5 + [("`LagLimit` 要明显大于正常运动的跟随误差波动，否则会误判 ⚠️。", False)],
    s7=("- **场景**：无转矩反馈的驱动，需要先测出机械止挡实际位置（磨损 / 偏差监测）再决定置零策略。\n"
        "- **价值**：跟随误差判据 + 测量返回，既不依赖转矩信号又把置零策略交给上层。\n"
        "- **替代方案对比**：`MC_StepBlockLagBased`（顶到即置零）；`MC_StepBlockDetection`（同为 Detection 但用转矩判据）。"
        "本 FB 用跟随误差判据并只返回位置。"),
    ex_extra={"Velocity": ("LREAL", "10.0", "顶止挡低速"),
              "DetectionVelocityLimit": ("LREAL", "1.0", "速度低于此判定顶住"),
              "DetectionVelocityTime": ("TIME", "T#200MS", "速度持续低于上限 200ms"),
              "TimeLimit": ("TIME", "T#20S", "搜索超时上限"),
              "DistanceLimit": ("LREAL", "500.0", "搜索行程上限"),
              "TorqueLimit": ("LREAL", "30.0", "限矩 30%"),
              "LagLimit": ("LREAL", "5.0", "跟随误差超此值判定顶住"),
              "Acceleration": ("LREAL", "0.0", "0 用轴配置标准值"),
              "Deceleration": ("LREAL", "0.0", "0 用轴配置标准值"),
              "Jerk": ("LREAL", "0.0", "0 用轴配置标准值")},
    ex_scene=("// 场景：无转矩反馈的驱动监测机械止挡磨损——本 FB 用跟随误差判据顶到止挡后只返回\n"
              "//       RecordedPosition，上层与历史基准比对判断磨损，不直接改写轴位置。\n"
              "// 价值：不依赖转矩信号又把测量与置零解耦，适合磨损/偏差监测。\n"
              "// 验证：先 MC_Power 使能；在线写 bLagDetReq := TRUE，观察 bLagDetActive TRUE，轴低速顶；\n"
              "//       顶到止挡跟随误差>5 且速度持续低于阈值后 bLagDetDone TRUE，lrRecordedPos 显示止挡位置。"),
    ex_enum={"Direction": ("MC_Home_Direction", "mcPositiveDirection", "向逻辑正方向顶止挡")},
    ex_skip=["SetPosition"],  # Detection 版接口图无 SetPosition，PDF 代码块多印；例程中省略
)

add(
    name="MC_StepLimitSwitch", topic="427768459", category="Step functions",
    sec="3.3.7",
    s1=("**主动归零 step 函数：搜索硬件限位开关**。它驱动轴朝 `Direction` 方向运动去寻找一个硬件限位开关"
        "（行程末端的 limit switch），按 `LimitSwitchMode` 给定的结束条件判定命中，命中后把轴位置设为 "
        "`SetPosition`。常用于把行程末端的硬件限位开关同时当作归零参考点的简单机构。"),
    inputs=[
        ("Execute", "BOOL", "Execute"),
        ("Direction", "MC_Home_Direction", "Direction"),
        ("LimitSwitchMode", "MC_Switch_Mode", "LimitSwitchMode"),
        ("LimitSwitchSignal", "MC_Ref_Signal_Ref", "LimitSwitchSignal"),
        ("Velocity", "LREAL", "Velocity"),
        ("Acceleration", "LREAL", "Acceleration"),
        ("Deceleration", "LREAL", "Deceleration"),
        ("Jerk", "LREAL", "Jerk"),
        ("SetPosition", "LREAL", "SetPosition"),
        ("TimeLimit", "TIME", "TimeLimit"),
        ("DistanceLimit", "LREAL", "DistanceLimit"),
        ("TorqueLimit", "LREAL", "TorqueLimit"),
        ("BufferMode", "MC_BufferMode", "BufferMode"),
        ("Options", "ST_Home_Options4", OPT4_DESC),
    ],
    in_out=[("Axis", "AXIS_REF", "Axis"), ("Parameter", "MC_HomingParameter", "Parameter")],
    outputs=[("Done", "BOOL", "Done"), ("Busy", "BOOL", "Busy"), ("Active", "BOOL", "Active"),
             ("CommandAborted", "BOOL", "CommandAborted"), ("Error", "BOOL", "Error"),
             ("ErrorID", "UDINT", "ErrorID")],
    s3=("`Execute` 上升沿启动搜索。按 PDF 第 3.3.7 节，本 FB 主动驱动轴去找硬件限位开关："
        "起始方向由 `Direction`（`MC_Home_Direction`）决定，轴按 `Velocity` / `Acceleration` / "
        "`Deceleration` / `Jerk` 运动，`TorqueLimit` 限矩。`LimitSwitchMode`（`MC_Switch_Mode`）定义命中限位开关的"
        "结束条件（电平 / 边沿），`LimitSwitchSignal`（`MC_Ref_Signal_Ref`）给出限位开关信号源；满足条件时"
        "把轴位置设为 `SetPosition`，`Done = TRUE`。step 函数默认关闭跟随误差监控（可经 "
        "`Options.EnableLagErrorDetection` 打开）。超过 `TimeLimit` 或相对起点移动超 `DistanceLimit` 则 "
        "`CommandAborted` 置位。本 FB 在 `Homing` 状态执行、结束后保持 `Homing`，需配 `MC_FinishHoming`"
        "（通常带退离 `Distance` 把轴从限位开关退回）/ `MC_AbortHoming` 收尾；`Parameter` 在序列各 FB 间逐级传递。"),
    s5=[("把行程末端的硬件限位开关用作归零参考点时，命中后轴正压在限位上，收尾 FB 必须带退离 `Distance` 把轴退回安全区 ⚠️。", False),
        ("`Direction` 必须朝该限位开关所在方向，选反会朝另一端运动甚至撞对侧硬限位 ⚠️。", False),
        ("`LimitSwitchMode` 要与限位开关电气特性（常开 / 常闭）匹配，否则命中判定时机错误。", False),
        ("`TorqueLimit` 设置以避免压到限位时损坏机械为准。", False),
        ("限位开关抖动需在 `LimitSwitchSignal` / 接线侧滤波。", False)],
    s7=("- **场景**：行程短、成本敏感的小机构，直接复用一端的硬件限位开关作为归零参考点。\n"
        "- **价值**：省去单独的参考凸轮开关，限位开关一兼二用；配收尾退离逻辑安全回到行程内。\n"
        "- **替代方案对比**：`MC_StepAbsoluteSwitch`（用行程中段的独立参考凸轮，两端另有限位保护）；"
        "`MC_StepLimitSwitchDetection`（同找限位开关但只返回检测位置不置零）。"),
    ex_extra={"Velocity": ("LREAL", "30.0", "搜索速度"),
              "SetPosition": ("LREAL", "0.0", "命中限位开关后定为坐标 0"),
              "TimeLimit": ("TIME", "T#30S", "搜索超时上限"),
              "DistanceLimit": ("LREAL", "1500.0", "搜索行程上限"),
              "TorqueLimit": ("LREAL", "100.0", "限矩保护"),
              "Acceleration": ("LREAL", "0.0", "0 用轴配置标准值"),
              "Deceleration": ("LREAL", "0.0", "0 用轴配置标准值"),
              "Jerk": ("LREAL", "0.0", "0 用轴配置标准值")},
    ex_scene=("// 场景：行程短的小机构复用负端硬件限位开关作归零参考点。本 FB 朝负向搜索限位开关，\n"
              "//       命中其上升沿后把该点定为坐标 0（后续需收尾 FB 带退离把轴退回行程内）。\n"
              "// 价值：省去独立参考凸轮，限位开关一兼二用，降低成本与接线。\n"
              "// 验证：先 MC_Power 使能；在线写 bLimitReq := TRUE，观察 bLimitActive TRUE，轴朝负向走；\n"
              "//       命中限位开关后 bLimitDone 短暂 TRUE，位置读数变 0，轴压在限位上需后续收尾退离。"),
    ex_enum={"Direction": ("MC_Home_Direction", "mcNegativeDirection", "起始向逻辑负方向搜索限位开关"),
             "LimitSwitchMode": ("MC_Switch_Mode", "mcRisingEdge", "限位开关上升沿作为结束条件")},
)

add(
    name="MC_StepLimitSwitchDetection", topic="427769995", category="Step functions",
    sec="3.3.8",
    s1=("**主动归零 step 函数：搜索硬件限位开关并仅返回检测位置（Detection 版）**。搜索逻辑与 "
        "`MC_StepLimitSwitch` 相同（驱动轴找硬件限位开关），但本 Detection 版**不改写轴位置**，"
        "而是把命中限位开关那一刻的轴位置通过 `RecordedPosition` 返回给用户。"),
    inputs=[
        ("Execute", "BOOL", "Execute"),
        ("Direction", "MC_Home_Direction", "Direction"),
        ("LimitSwitchMode", "MC_Switch_Mode", "LimitSwitchMode"),
        ("LimitSwitchSignal", "MC_Ref_Signal_Ref", "LimitSwitchSignal"),
        ("Velocity", "LREAL", "Velocity"),
        ("Acceleration", "LREAL", "Acceleration"),
        ("Deceleration", "LREAL", "Deceleration"),
        ("Jerk", "LREAL", "Jerk"),
        ("TimeLimit", "TIME", "TimeLimit"),
        ("DistanceLimit", "LREAL", "DistanceLimit"),
        ("TorqueLimit", "LREAL", "TorqueLimit"),
        ("BufferMode", "MC_BufferMode", "BufferMode"),
        ("Options", "ST_Home_Options4", OPT4_DESC),
    ],
    in_out=[("Axis", "AXIS_REF", "Axis"), ("Parameter", "MC_HomingParameter", "Parameter")],
    outputs=[("Done", "BOOL", "Done"), ("Busy", "BOOL", "Busy"), ("Active", "BOOL", "Active"),
             ("CommandAborted", "BOOL", "CommandAborted"), ("Error", "BOOL", "Error"),
             ("ErrorID", "UDINT", "ErrorID"), ("RecordedPosition", "LREAL", "RecordedPosition")],
    s3=("`Execute` 上升沿启动搜索。搜索过程与 `MC_StepLimitSwitch` 一致：按 `Direction` 起始方向、"
        "`Velocity` / `Acceleration` / `Deceleration` / `Jerk` 动力学驱动轴找硬件限位开关，`LimitSwitchMode` "
        "定义结束条件，`LimitSwitchSignal` 给信号源，`TorqueLimit` 限矩。区别在于按 PDF 第 3.3.8 节，"
        "本 Detection 版**不改写轴位置**，而是把命中限位开关那一刻的轴位置写入输出 `RecordedPosition` 返回"
        "（因此没有 `SetPosition` 入口）。`Done = TRUE` 表示检测成功并已给出 `RecordedPosition`；"
        "超过 `TimeLimit` / `DistanceLimit` 则 `CommandAborted` 置位。本 FB 在 `Homing` 状态执行、结束后"
        "保持 `Homing`，需配收尾 FB；`Parameter` 在序列各 FB 间逐级传递。"),
    s5=[("本 FB**不改写轴位置**，只给出 `RecordedPosition`；命中后轴仍压在限位上，收尾 FB 需带退离 `Distance` ⚠️。", False),
        ("`Direction` 必须朝该限位开关方向，选反可能撞对侧硬限位 ⚠️。", False),
        ("`LimitSwitchMode` 要与限位开关电气特性匹配。", False),
        ("限位开关抖动需滤波，否则 `RecordedPosition` 会偏。", False),
        ("结束后轴停在 `Homing`，仍需收尾 FB。", False)],
    s7=("- **场景**：需要测出限位开关实际触发位置（行程标定 / 软限位设定）而不立即置零。\n"
        "- **价值**：把“测限位位置”与“置零”解耦，测量值经 `RecordedPosition` 返回供上层设定软限位。\n"
        "- **替代方案对比**：`MC_StepLimitSwitch`（命中即置零）。需要拿限位实际位置做软限位 / 行程标定时用本 Detection 版。"),
    ex_extra={"Velocity": ("LREAL", "30.0", "搜索速度"),
              "TimeLimit": ("TIME", "T#30S", "搜索超时上限"),
              "DistanceLimit": ("LREAL", "1500.0", "搜索行程上限"),
              "TorqueLimit": ("LREAL", "100.0", "限矩保护"),
              "Acceleration": ("LREAL", "0.0", "0 用轴配置标准值"),
              "Deceleration": ("LREAL", "0.0", "0 用轴配置标准值"),
              "Jerk": ("LREAL", "0.0", "0 用轴配置标准值")},
    ex_scene=("// 场景：行程标定时测出负端硬件限位开关的实际触发位置以便设定软限位——本 FB 朝负向搜限位\n"
              "//       开关，命中后只返回 RecordedPosition，上层据此设定软限位，不改写轴位置。\n"
              "// 价值：把测限位位置与置零解耦，便于行程标定 / 软限位设定。\n"
              "// 验证：先 MC_Power 使能；在线写 bLimitDetReq := TRUE，观察 bLimitDetActive TRUE，轴朝负向走；\n"
              "//       命中限位开关后 bLimitDetDone TRUE，lrRecordedPos 显示限位触发位置（轴位置读数不变）。"),
    ex_enum={"Direction": ("MC_Home_Direction", "mcNegativeDirection", "起始向逻辑负方向搜索"),
             "LimitSwitchMode": ("MC_Switch_Mode", "mcRisingEdge", "限位开关上升沿作为结束条件")},
)

add(
    name="MC_StepReferencePulse", topic="427784331", category="Step functions",
    sec="3.3.9",
    s1=("**主动归零 step 函数：搜索编码器零脉冲（reference pulse）**。它驱动轴朝 `Direction` 方向运动去寻找"
        "编码器的零脉冲（每转一次、并非所有编码器都有）。零脉冲信号精度远高于普通传感器，是高精度归零的常用参考。"
        "命中零脉冲后把轴位置设为 `SetPosition`。本 FB 在 `Homing` 状态执行，结束后保持 `Homing`，需配收尾 FB。"),
    inputs=[
        ("Execute", "BOOL", "Execute"),
        ("Direction", "MC_Home_Direction", "Direction"),
        ("SwitchMode", "MC_Switch_Mode", "SwitchMode"),
        ("ReferenceSignal", "MC_Ref_Signal_Ref", "ReferenceSignal"),
        ("Velocity", "LREAL", "Velocity"),
        ("Acceleration", "LREAL", "Acceleration"),
        ("Deceleration", "LREAL", "Deceleration"),
        ("Jerk", "LREAL", "Jerk"),
        ("SetPosition", "LREAL", "SetPosition"),
        ("TimeLimit", "TIME", "TimeLimit"),
        ("DistanceLimit", "LREAL", "DistanceLimit"),
        ("TorqueLimit", "LREAL", "TorqueLimit"),
        ("BufferMode", "MC_BufferMode", "BufferMode"),
        ("Options", "ST_Home_Options4", OPT4_DESC),
    ],
    in_out=[("Axis", "AXIS_REF", "Axis"), ("Parameter", "MC_HomingParameter", "Parameter")],
    outputs=[("Done", "BOOL", "Done"), ("Busy", "BOOL", "Busy"), ("Active", "BOOL", "Active"),
             ("CommandAborted", "BOOL", "CommandAborted"), ("Error", "BOOL", "Error"),
             ("ErrorID", "UDINT", "ErrorID")],
    s3=("`Execute` 上升沿启动搜索。按 PDF 第 3.3.9 节，本 FB 主动驱动轴去找编码器零脉冲："
        "起始方向由 `Direction`（`MC_Home_Direction`）决定，轴按 `Velocity` / `Acceleration` / "
        "`Deceleration` / `Jerk` 运动，`TorqueLimit` 限矩，`ReferenceSignal`（`MC_Ref_Signal_Ref`）通过 "
        "`TouchProbe` 锁存单元等待零脉冲。零脉冲是每转一次的高精度信号，命中那一刻把轴位置设为 `SetPosition`，"
        "`Done = TRUE`。step 函数默认关闭跟随误差监控（可经 `Options.EnableLagErrorDetection` 打开）。"
        "超过 `TimeLimit` 或相对起点移动超 `DistanceLimit` 则 `CommandAborted` 置位。本 FB 在 `Homing` 状态执行、"
        "结束后保持 `Homing`，需配 `MC_FinishHoming` / `MC_AbortHoming` 收尾；`Parameter` 在序列各 FB 间逐级传递。"
        "⚠️ 提示：PDF 第 3.3.9 节正文的 `VAR_INPUT` 代码块多印了一个 `SwitchMode : MC_Switch_Mode`（本文档 §2 逐字照搬保留），"
        "但同节的接口图与参数说明表均无此入口；零脉冲搜索的结束条件是“命中零脉冲”，并不需要 `SwitchMode`，该入口系 PDF 代码块多余项，工程中可忽略。"),
    s5=[("零脉冲并非所有编码器都有；用本 FB 前要确认编码器确实输出零脉冲且已在驱动 / NC 中正确链接 ⚠️。", False),
        ("通常先用开关 / 限位 step 粗定位到零脉冲附近，再用本 FB 在小范围内精确锁零脉冲，否则一次搜索可能跨多个零脉冲。", False),
        ("`Direction` 选错会朝远离目标的方向找，可能超 `DistanceLimit` 中止。", False),
        ("`ReferenceSignal.TouchProbe` 必须选对应零脉冲的锁存单元。", False),
        ("结束后轴停在 `Homing`，需收尾 FB。", False)],
    s7=("- **场景**：高精度机床 / 直线电机轴，先粗找开关再用编码器零脉冲精确定零，把重复定位精度提到编码器分辨率级别。\n"
        "- **价值**：零脉冲精度远高于普通接近开关，是高精度归零的关键一步；封装为可拼接 step 便于组成两段式归零序列。\n"
        "- **替代方案对比**：`MC_StepReferenceFlyingRefPulse`（飞行版，运行中后台抓零脉冲、不自己发运动）；"
        "`MC_StepReferencePulseDetection`（同找零脉冲但只返回检测位置不置零）。"),
    ex_extra={"Velocity": ("LREAL", "5.0", "找零脉冲的低速（小范围精确锁定）"),
              "SetPosition": ("LREAL", "0.0", "命中零脉冲后定为坐标 0"),
              "TimeLimit": ("TIME", "T#10S", "搜索超时上限"),
              "DistanceLimit": ("LREAL", "360.0", "约一转行程上限，避免跨多个零脉冲"),
              "TorqueLimit": ("LREAL", "100.0", "限矩保护"),
              "Acceleration": ("LREAL", "0.0", "0 用轴配置标准值"),
              "Deceleration": ("LREAL", "0.0", "0 用轴配置标准值"),
              "Jerk": ("LREAL", "0.0", "0 用轴配置标准值")},
    ex_scene=("// 场景：高精度直线电机轴两段式归零的第二段——前级已粗定位到零脉冲附近，本 FB 低速朝正向\n"
              "//       小范围搜索编码器零脉冲，命中后把该点定为坐标 0，把重复定位精度提到编码器级别。\n"
              "// 价值：零脉冲精度远高于接近开关，是高精度归零关键步骤。\n"
              "// 验证：先 MC_Power 使能且已粗定位到零脉冲附近；在线写 bPulseReq := TRUE，观察 bPulseActive\n"
              "//       TRUE，轴低速正向走约一转内命中零脉冲后 bPulseDone 短暂 TRUE，位置读数变 0。"),
    ex_enum={"Direction": ("MC_Home_Direction", "mcPositiveDirection", "起始向逻辑正方向搜索零脉冲")},
    ex_skip=["SwitchMode"],  # 接口图无 SwitchMode，PDF 代码块多印；例程中省略
)

add(
    name="MC_StepReferencePulseDetection", topic="427785867", category="Step functions",
    sec="3.3.10",
    s1=("**主动归零 step 函数：搜索编码器零脉冲并仅返回检测位置（Detection 版）**。搜索逻辑与 "
        "`MC_StepReferencePulse` 相同（驱动轴找编码器零脉冲），但本 Detection 版**不改写轴位置**，"
        "而是把命中零脉冲那一刻的轴位置通过 `RecordedPosition` 返回给用户。"),
    inputs=[
        ("Execute", "BOOL", "Execute"),
        ("Direction", "MC_Home_Direction", "Direction"),
        ("SwitchMode", "MC_Switch_Mode", "SwitchMode"),
        ("ReferenceSignal", "MC_Ref_Signal_Ref", "ReferenceSignal"),
        ("Velocity", "LREAL", "Velocity"),
        ("Acceleration", "LREAL", "Acceleration"),
        ("Deceleration", "LREAL", "Deceleration"),
        ("Jerk", "LREAL", "Jerk"),
        ("TimeLimit", "TIME", "TimeLimit"),
        ("DistanceLimit", "LREAL", "DistanceLimit"),
        ("TorqueLimit", "LREAL", "TorqueLimit"),
        ("BufferMode", "MC_BufferMode", "BufferMode"),
        ("Options", "ST_Home_Options4", OPT4_DESC),
    ],
    in_out=[("Axis", "AXIS_REF", "Axis"), ("Parameter", "MC_HomingParameter", "Parameter")],
    outputs=[("Done", "BOOL", "Done"), ("Busy", "BOOL", "Busy"), ("Active", "BOOL", "Active"),
             ("CommandAborted", "BOOL", "CommandAborted"), ("Error", "BOOL", "Error"),
             ("ErrorID", "UDINT", "ErrorID"), ("RecordedPosition", "LREAL", "RecordedPosition")],
    s3=("`Execute` 上升沿启动搜索。搜索过程与 `MC_StepReferencePulse` 一致：按 `Direction` 起始方向、"
        "`Velocity` / `Acceleration` / `Deceleration` / `Jerk` 动力学驱动轴找编码器零脉冲，`ReferenceSignal` "
        "通过 `TouchProbe` 锁存单元等待零脉冲，`TorqueLimit` 限矩。区别在于按 PDF 第 3.3.10 节，本 Detection 版"
        "**不改写轴位置**，而是把命中零脉冲那一刻的轴位置写入输出 `RecordedPosition` 返回（因此没有 `SetPosition` 入口）。"
        "`Done = TRUE` 表示检测成功并已给出 `RecordedPosition`；超过 `TimeLimit` / `DistanceLimit` 则 "
        "`CommandAborted` 置位。本 FB 在 `Homing` 状态执行、结束后保持 `Homing`，需配收尾 FB；"
        "`Parameter` 在序列各 FB 间逐级传递。"
        "⚠️ 提示：PDF 第 3.3.10 节正文的 `VAR_INPUT` 代码块多印了一个 `SwitchMode : MC_Switch_Mode`（本文档 §2 逐字照搬保留），"
        "但同节的接口图与参数说明表均无此入口；零脉冲检测的结束条件是“命中零脉冲”，并不需要 `SwitchMode`，该入口系 PDF 代码块多余项，工程中可忽略。"),
    s5=[("本 FB**不改写轴位置**，只给出 `RecordedPosition`；若忘了用它去置零，轴仍未真正校准 ⚠️。", False),
        ("零脉冲并非所有编码器都有，用前确认编码器输出零脉冲且已正确链接 ⚠️。", False),
        ("通常先粗定位再用本 FB 在小范围检测零脉冲，避免一次跨多个零脉冲。", False),
        ("`ReferenceSignal.TouchProbe` 必须选对应零脉冲的锁存单元。", False),
        ("结束后轴停在 `Homing`，仍需收尾 FB。", False)],
    s7=("- **场景**：需要先测出编码器零脉冲相对当前坐标的精确位置（编码器安装相位标定 / 多轴零脉冲对齐），再决定置零策略。\n"
        "- **价值**：以编码器级精度测出零脉冲位置并返回，把高精度测量与置零解耦。\n"
        "- **替代方案对比**：`MC_StepReferencePulse`（命中即置零）；`MC_StepReferenceFlyingRefPulse`（飞行版）。"
        "需要拿零脉冲测量值做相位标定 / 对齐时用本 Detection 版。"),
    ex_extra={"Velocity": ("LREAL", "5.0", "找零脉冲低速"),
              "TimeLimit": ("TIME", "T#10S", "搜索超时上限"),
              "DistanceLimit": ("LREAL", "360.0", "约一转行程上限"),
              "TorqueLimit": ("LREAL", "100.0", "限矩保护"),
              "Acceleration": ("LREAL", "0.0", "0 用轴配置标准值"),
              "Deceleration": ("LREAL", "0.0", "0 用轴配置标准值"),
              "Jerk": ("LREAL", "0.0", "0 用轴配置标准值")},
    ex_scene=("// 场景：编码器安装相位标定——本 FB 低速朝正向小范围搜编码器零脉冲，命中后只返回\n"
              "//       RecordedPosition，上层据此计算编码器安装相位偏差，不改写轴位置。\n"
              "// 价值：以编码器级精度测出零脉冲位置并返回，把高精度测量与置零解耦。\n"
              "// 验证：先 MC_Power 使能且已粗定位到零脉冲附近；在线写 bPulseDetReq := TRUE，观察\n"
              "//       bPulseDetActive TRUE，轴低速正向走命中零脉冲后 bPulseDetDone TRUE，lrRecordedPos 显示位置。"),
    ex_enum={"Direction": ("MC_Home_Direction", "mcPositiveDirection", "起始向逻辑正方向搜索零脉冲")},
    ex_skip=["SwitchMode"],  # 接口图无 SwitchMode，PDF 代码块多印；例程中省略
)


# --------------------------- rendering ---------------------------
ERR_TABLE = """| 错误码 | 符号名 | 含义 |
|---|---|---|
| `16#4B90` | `MC_HOMINGERROR_DRIVETYPE` | 驱动型号不受支持（支持 AX5xxx-xxxx-02xx FW≥2.05、EL7201-0000/-0001/-0010/-0011、AX8xxx 等） |
| `16#4B91` | `MC_HOMINGERROR_DIRECTION` | 参数化的方向对该 FB 不允许 |
| `16#4B92` | `MC_HOMINGERROR_SWITCHMODE` | 参数化的模式（`SwitchMode`）对该 FB 不允许 |
| `16#4B93` | `MC_HOMINGERROR_MODE` | 模式错误（PDF 未给进一步描述，⚠️ 待人工确认具体含义） |
| `16#4B94` | `MC_HOMINGERROR_TORQUEPARAMETER` | 参数化的转矩预设不允许 |
| `16#4B95` | `MC_HOMINGERROR_LAGPARAMETER` | 参数化的跟随误差不允许（< 0） |
| `16#4B96` | `MC_HOMINGERROR_DISTANCELIMIT` | 参数化的最大距离不允许（< 0） |
| `16#4B97` | `MC_HOMINGERROR_PARAMETER_ALREADYSTORED` | 已备份过参数却又以 READ 模式调用参数控制 FB |
| `16#4B98` | `MC_HOMINGERROR_PARAMETER_NOTSTORED` | 未备份参数却以 RESTORE 模式调用参数控制 FB |
"""

DATATYPE_SECTION = """本库共用的数据类型（来自 PDF 第 4 章）：

- `MC_Home_Direction`（枚举，UDINT 基）：`mcPositiveDirection := 1`（起始朝逻辑正方向）、`mcNegativeDirection := 3`（起始朝逻辑负方向）、`mcSwitchPositive := 5`、`mcSwitchNegative := 7`（后两者起始方向取决于传感器当前开关状态）。到达行程限位或开关状态变化时方向可反转。
- `MC_Switch_Mode`（枚举，UDINT 基）：`mcOn := 1`、`mcOff := 2`、`mcRisingEdge := 3`、`mcFallingEdge := 4`、`mcEdgeSwitchPositive := 5`、`mcEdgeSwitchNegative := 6`、`mcRisingEdgeInverse := 11`、`mcFallingEdgeInverse := 12`。定义搜索的结束条件。
- `MC_Ref_Signal_Ref`（结构）：`SignalSource : E_SignalSource := SignalSource_Default`（信号源，多数情况下在驱动里固定配置，取默认值）、`TouchProbe : E_TouchProbe := PlcEvent`（编码器硬件锁存单元）、`Level : BOOL`（传感器当前电平，由用户传入）。
- `ST_Home_Options`（结构）：当前为空 / 未使用。
- `ST_Home_Options2`（结构）：`DisableDriveAccess : BOOL`。
- `ST_Home_Options3`（结构）：`DisableDriveAccess : BOOL`、`InstantLagReduction : BOOL`。
- `ST_Home_Options4`（结构）：`DisableDriveAccess : BOOL`、`EnableLagErrorDetection : BOOL`。
- `MC_HomingParameter`（结构）：`Stored : BOOL`、`Nc : MC_HomingParameterNcGeneral`、`Drive : MC_HomingParameterDriveGeneral`。整条自定义归零序列必须把同一个该结构实例在所有 FB 间逐级传递（先备份、被修改、结束时还原）。"""


def render_doc(e):
    name = e["name"]
    topic = e["topic"]
    info_url = INFO.format(topic)
    lines = []
    lines.append(f"# {name}\n")
    lines.append("## 元信息\n")
    lines.append("| 字段 | 值 |")
    lines.append("|---|---|")
    lines.append(f"| Library | `{LIB}` |")
    lines.append(f"| Library Version | `{VERSION}` |")
    lines.append("| Type | `FUNCTION_BLOCK` |")
    lines.append(f"| Category | `{e['category']}` |")
    lines.append(f"| Source PDF | {PDF} |")
    lines.append(f"| Source InfoSys | {info_url} |")
    lines.append(f"| Verified | {DATE} ✅ |")
    lines.append(f"| InfoSys-checked | ✅ {DATE} |")
    lines.append("| Status | `verified` |")
    lines.append(f"| Example | [`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml) |")
    lines.append("\n---\n")

    lines.append("## 1. 功能简述\n")
    lines.append(e["s1"] + "\n")

    lines.append("## 2. 接口定义\n")
    # VAR_INPUT
    lines.append("### VAR_INPUT\n")
    lines.append("```iecst")
    lines.append("VAR_INPUT")
    w = max(len(n) for n, _, _ in e["inputs"])
    for n, t, _ in e["inputs"]:
        lines.append(f"    {n.ljust(w)} : {t};")
    lines.append("END_VAR")
    lines.append("```\n")
    lines.append("| 名称 | 类型 | 说明 |")
    lines.append("|---|---|---|")
    for n, t, d in e["inputs"]:
        desc = D.get(d, d)
        lines.append(f"| `{n}` | `{t}` | {desc} |")
    lines.append("")
    # VAR_IN_OUT
    lines.append("### VAR_IN_OUT\n")
    lines.append("```iecst")
    lines.append("VAR_IN_OUT")
    w = max(len(n) for n, _, _ in e["in_out"])
    for n, t, _ in e["in_out"]:
        lines.append(f"    {n.ljust(w)} : {t};")
    lines.append("END_VAR")
    lines.append("```\n")
    lines.append("| 名称 | 类型 | 说明 |")
    lines.append("|---|---|---|")
    for n, t, d in e["in_out"]:
        lines.append(f"| `{n}` | `{t}` | {D.get(d, d)} |")
    lines.append("")
    # VAR_OUTPUT
    lines.append("### VAR_OUTPUT\n")
    lines.append("```iecst")
    lines.append("VAR_OUTPUT")
    w = max(len(n) for n, _, _ in e["outputs"])
    for n, t, _ in e["outputs"]:
        lines.append(f"    {n.ljust(w)} : {t};")
    lines.append("END_VAR")
    lines.append("```\n")
    lines.append("| 名称 | 类型 | 说明 |")
    lines.append("|---|---|---|")
    for n, t, d in e["outputs"]:
        lines.append(f"| `{n}` | `{t}` | {D.get(d, d)} |")
    lines.append("")

    lines.append("## 3. 行为说明\n")
    lines.append(e["s3"] + "\n")

    lines.append("## 4. 错误码 / 返回值\n")
    lines.append("错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 取本库枚举 "
                 "`E_HomingErrorCodes`（UDINT 基，PDF 第 4.1.1 节）中的值；超时 / 距离超限等中止情况则通过 "
                 "`CommandAborted = TRUE` 反映而非 `Error`。`E_HomingErrorCodes` 取值：\n")
    lines.append(ERR_TABLE)
    lines.append("除上述本库专有码外，底层 NC / 驱动错误仍可能经 `ErrorID` 透传（NC 轴错误号，非 HRESULT）；"
                 "本 FB 自身不带清错入口，轴进入 Errorstop 后需先 `MC_Reset(Axis)`（Tc2_MC2）才能继续。\n")

    lines.append("## 5. 使用注意 / 常见坑\n")
    for txt, eng in e["s5"]:
        prefix = "（工程经验补充）" if eng else ""
        lines.append(f"- {prefix}{txt}")
    lines.append("")

    lines.append("## 6. 最小例程\n")
    lines.append(f"> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)\n")
    lines.append("详见上述 XML 文件，内含场景 / 价值 / 验证步骤注释，可右键 PLC 项目 → Import PLCopenXML 导入后编译运行。\n")

    lines.append("## 7. 业务场景与实际价值\n")
    lines.append(e["s7"] + "\n")

    lines.append("## 8. 参考资料\n")
    lines.append(f"- **PDF**：[TwinCAT_3_PLC_Lib_{LIB}_EN.pdf]({PDF}) 第 {e['sec']} 节（Version {VERSION}）")
    lines.append(f"- **InfoSys topic**：{info_url}")
    lines.append("- **数据类型（本库共用）**：\n")
    lines.append(DATATYPE_SECTION)
    lines.append("- **相关 FB**：`MC_FinishHoming` / `MC_AbortHoming`（序列收尾）、`MC_Power` / `MC_Reset`"
                 "（Tc2_MC2，使能与清错）、Tc2_MC2 的 `MC_Home`（固定序列归零，与本库自定义序列互补）")
    lines.append("")
    return "\n".join(lines)


# ----- example XML -----
def type_xml(t):
    base = {"BOOL": "<BOOL/>", "LREAL": "<LREAL/>", "UDINT": "<UDINT/>", "INT": "<INT/>",
            "TIME": "<TIME/>"}
    if t in base:
        return base[t]
    return f'<derived name="{t}"/>'


def render_example(e):
    name = e["name"]
    has_active = any(n == "Active" for n, _, _ in e["outputs"])
    has_rec = any(n == "RecordedPosition" for n, _, _ in e["outputs"])
    inst = "fb" + name[3:] if name.startswith("MC_") else "fb" + name
    tag = e["tag"]
    req = "b" + tag + "Req"
    v_done = "b" + tag + "Done"
    v_active = "b" + tag + "Active"
    # build local vars and call params
    localvars = []
    callparams = []  # (pin, expr)
    # instance + axis + trigger
    localvars.append(f'            <variable name="{inst}"><type><derived name="{name}"/></type></variable>')
    localvars.append('            <variable name="axisHoming"><type><derived name="AXIS_REF"/></type>'
                     '<documentation><xhtml xmlns="http://www.w3.org/1999/xhtml">归零目标轴；运行前需先 MC_Power 使能</xhtml></documentation></variable>')
    localvars.append('            <variable name="rtExec"><type><derived name="R_TRIG"/></type>'
                     '<documentation><xhtml xmlns="http://www.w3.org/1999/xhtml">把保持型请求位整成单次上升沿</xhtml></documentation></variable>')

    # request bool (online trigger) — entry-specific semantic name
    localvars.append(f'            <variable name="{req}"><initialValue><simpleValue value="FALSE"/></initialValue>'
                     '<type><BOOL/></type><documentation><xhtml xmlns="http://www.w3.org/1999/xhtml">在线置 TRUE 触发一次执行</xhtml></documentation></variable>')

    has_param = any(n == "Parameter" for n, _, _ in e["in_out"])
    if has_param:
        localvars.append('            <variable name="homingParam"><type><derived name="MC_HomingParameter"/></type>'
                         '<documentation><xhtml xmlns="http://www.w3.org/1999/xhtml">贯穿整条归零序列、各 FB 间逐级传递的参数结构</xhtml></documentation></variable>')

    # reference signal struct if needed
    needs_refsig = any(t == "MC_Ref_Signal_Ref" for n, t, _ in e["inputs"])
    refsig_pins = [n for n, t, _ in e["inputs"] if t == "MC_Ref_Signal_Ref"]
    if needs_refsig:
        localvars.append('            <variable name="refSignal"><type><derived name="MC_Ref_Signal_Ref"/></type>'
                         '<documentation><xhtml xmlns="http://www.w3.org/1999/xhtml">参考信号源配置（锁存单元 / 信号源 / 当前电平）</xhtml></documentation></variable>')

    enum_map = e.get("ex_enum", {})
    extra = e.get("ex_extra", {})
    skip = set(e.get("ex_skip", []))  # PDF-typo pins not in the real interface; omit from call
    decl_extra = []
    for n, t, _ in e["inputs"]:
        if n in skip:
            continue
        if n == "Execute":
            callparams.append(("Execute", "rtExec.Q"))
        elif t == "MC_Ref_Signal_Ref":
            callparams.append((n, "refSignal"))
        elif n in enum_map:
            etype, eval_, edesc = enum_map[n]
            callparams.append((n, eval_))
        elif n in extra:
            etype, eval_, edesc = extra[n]
            callparams.append((n, eval_))
        elif n == "BufferMode":
            callparams.append((n, "MC_Aborting"))
        elif n == "Options":
            # leave default by not passing? must pass per charter (all VAR_INPUT explicit). Use struct default var.
            callparams.append((n, "homingOptions"))
            otype = t
            decl_extra.append(f'            <variable name="homingOptions"><type><derived name="{otype}"/></type>'
                              '<documentation><xhtml xmlns="http://www.w3.org/1999/xhtml">选项结构，Beckhoff 伺服保持默认（DisableDriveAccess := FALSE）</xhtml></documentation></variable>')
        elif n in ("PositiveLimitSwitch", "NegativeLimitSwitch"):
            v = "bPosLimit" if n == "PositiveLimitSwitch" else "bNegLimit"
            callparams.append((n, v))
            desc = "正向硬件限位开关信号（行程内为 FALSE）；实机接 PLC 输入" if n == "PositiveLimitSwitch" else "负向硬件限位开关信号（行程内为 FALSE）；实机接 PLC 输入"
            decl_extra.append(f'            <variable name="{v}"><initialValue><simpleValue value="FALSE"/></initialValue>'
                              f'<type><BOOL/></type><documentation><xhtml xmlns="http://www.w3.org/1999/xhtml">{desc}</xhtml></documentation></variable>')
        else:
            # fallback: shouldn't happen; pass 0
            callparams.append((n, "0"))

    # outputs we observe
    for n, t, _ in e["outputs"]:
        if n == "Done":
            callparams.append((n, v_done))
            decl_extra.append(f'            <variable name="{v_done}"><type><BOOL/></type></variable>')
        elif n == "Active":
            callparams.append((n, v_active))
            decl_extra.append(f'            <variable name="{v_active}"><type><BOOL/></type></variable>')
        elif n == "CommandAborted":
            callparams.append((n, "bAborted"))
            decl_extra.append('            <variable name="bAborted"><type><BOOL/></type></variable>')
        elif n == "Error":
            callparams.append((n, "bError"))
            decl_extra.append('            <variable name="bError"><type><BOOL/></type></variable>')
        elif n == "ErrorID":
            callparams.append((n, "nErrorID"))
            decl_extra.append('            <variable name="nErrorID"><type><UDINT/></type></variable>')
        elif n == "Busy":
            callparams.append((n, "bBusy"))
            decl_extra.append('            <variable name="bBusy"><type><BOOL/></type></variable>')
        elif n == "RecordedPosition":
            callparams.append((n, "lrRecordedPos"))
            decl_extra.append('            <variable name="lrRecordedPos"><type><LREAL/></type>'
                             '<documentation><xhtml xmlns="http://www.w3.org/1999/xhtml">Detection 版返回的检测位置（轴位置本身不被改写）</xhtml></documentation></variable>')

    # in_out params
    for n, t, _ in e["in_out"]:
        if n == "Axis":
            callparams.append((n, "axisHoming"))
        elif n == "Parameter":
            callparams.append((n, "homingParam"))

    localvars.extend(decl_extra)

    # body: scene comment + ref signal setup + R_TRIG + call
    body = []
    body.append(e["ex_scene"])
    body.append("")
    if needs_refsig:
        body.append("// 配置参考信号源：用驱动默认信号源 + 默认锁存单元（实机按编码器/驱动手册选 TouchProbe）")
        body.append("refSignal.SignalSource := SignalSource_Default;")
        body.append("refSignal.TouchProbe   := PlcEvent;")
        body.append("")
    body.append("// 把保持型在线请求位整成单次上升沿，避免持续触发（charter: Execute 用 R_TRIG）")
    body.append(f"rtExec(CLK := {req});")
    body.append("")
    body.append("// 单次完整调用：所有 VAR_INPUT 显式赋值，Axis（及 Parameter）按 VAR_IN_OUT 必须传引用")
    body.append(f"{inst}(")
    pw = max(len(p) for p, _ in callparams)
    for i, (p, v) in enumerate(callparams):
        # determine arrow: outputs use =>
        is_out = p in ("Done", "Busy", "Active", "CommandAborted", "Error", "ErrorID", "RecordedPosition")
        sep = "=>" if is_out else ":="
        comma = "," if i < len(callparams) - 1 else ");"
        body.append(f"    {p.ljust(pw)} {sep} {v}{comma}")
    body.append("")
    body.append("// stateful 输出复位：请求复位后清掉本地观察位，便于下次干净触发")
    body.append(f"IF NOT {req} AND NOT bBusy THEN")
    body.append(f"    {v_done} := FALSE;")
    if any(n == "CommandAborted" for n, _, _ in e["outputs"]):
        body.append("    bAborted := FALSE;")
    body.append("END_IF;")

    body_text = esc("\n".join(body))

    xml = []
    xml.append('<?xml version="1.0" encoding="utf-8"?>')
    xml.append('<project xmlns="http://www.plcopen.org/xml/tc6_0200">')
    xml.append(f'  <fileHeader companyName="tc3-libraries-kb" productName="TwinCAT" productVersion="3.1" creationDateTime="{DATE}T00:00:00"/>')
    xml.append(f'  <contentHeader name="{LIB}.{name} Demo" modificationDateTime="{DATE}T00:00:00">')
    xml.append('    <coordinateInfo>')
    xml.append('      <fbd><scaling x="1" y="1"/></fbd>')
    xml.append('      <ld><scaling x="1" y="1"/></ld>')
    xml.append('      <sfc><scaling x="1" y="1"/></sfc>')
    xml.append('    </coordinateInfo>')
    xml.append('  </contentHeader>')
    xml.append('  <types>')
    xml.append('    <dataTypes/>')
    xml.append('    <pous>')
    xml.append(f'      <pou name="P_Demo_{name}" pouType="program">')
    xml.append('        <interface>')
    xml.append('          <localVars>')
    xml.extend(localvars)
    xml.append('          </localVars>')
    xml.append('        </interface>')
    xml.append('        <body>')
    xml.append('          <ST><xhtml xmlns="http://www.w3.org/1999/xhtml">' + body_text + '</xhtml></ST>')
    xml.append('        </body>')
    xml.append('      </pou>')
    xml.append('    </pous>')
    xml.append('  </types>')
    xml.append('  <instances><configurations/></instances>')
    xml.append('</project>')
    return "\n".join(xml)


TAGS = {
    "MC_FinishHoming": "Finish", "MC_HomeDirect": "SetZero", "MC_AbortHoming": "Abort",
    "MC_AbortPassiveHoming": "AbortFlying", "MC_StepReferenceFlyingRefPulse": "FlyingRef",
    "MC_StepReferenceFlyingSwitch": "FlyingSw", "MC_StepAbsoluteSwitch": "Search",
    "MC_StepAbsoluteSwitchDetection": "Detect", "MC_StepBlock": "Block",
    "MC_StepBlockDetection": "BlockDet", "MC_StepBlockLagBased": "LagBlock",
    "MC_StepBlockLagBasedDetection": "LagDet", "MC_StepLimitSwitch": "Limit",
    "MC_StepLimitSwitchDetection": "LimitDet", "MC_StepReferencePulse": "Pulse",
    "MC_StepReferencePulseDetection": "PulseDet",
}


def main():
    os.makedirs(EXDIR, exist_ok=True)
    for e in E:
        e["tag"] = TAGS[e["name"]]
    assert len(E) == 16, f"expected 16 entries got {len(E)}"
    names = [e["name"] for e in E]
    assert len(set(names)) == 16
    for e in E:
        subdir = os.path.join(DOCDIR, CAT_DIR[e["category"]])
        os.makedirs(subdir, exist_ok=True)
        doc = render_doc(e)
        with open(os.path.join(subdir, e["name"] + ".md"), "w", encoding="utf-8") as f:
            f.write(doc)
        ex = render_example(e)
        with open(os.path.join(EXDIR, "P_Demo_" + e["name"] + ".xml"), "w", encoding="utf-8") as f:
            f.write(ex)
    print("WROTE", len(E), "docs +", len(E), "examples")


if __name__ == "__main__":
    main()
