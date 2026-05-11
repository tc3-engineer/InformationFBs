# Per-entry content registry for Tc3_EventLogger rewrite (2026-05-11).
# Keyed by (parent_dir, name). Each entry provides §1/§3/§4/§5/§7 Chinese content
# plus the example XML scenario/value/verify + call body.
#
# Generator: _meta/tools/_tc3eventlogger_gen.py
from __future__ import annotations

# Override example XML stem for cases where the historical filename differs from
# the default `<Parent>_<Method>` rule (e.g. methods that originally used just the
# method name when the parent FB had no collisions).
EXAMPLE_STEMS: dict[str, str] = {
    # fb_tcsourceinfo only has ExtendName/ResetToDefault stems without Parent_ prefix
    "fb_tcsourceinfo/ExtendName": "ExtendName",
    "fb_tcsourceinfo/ResetToDefault": "ResetToDefault",
    "fb_tcsourceinfo/Clear": "FB_TcSourceInfo_Clear",
    # fb_tcalarm
    "fb_tcalarm/Clear": "FB_TcAlarm_Clear",
    "fb_tcalarm/Confirm": "Confirm",
    "fb_tcalarm/Raise": "Raise",
    "fb_tcalarm/Create": "FB_TcAlarm_Create",
    "fb_tcalarm/CreateEx": "FB_TcAlarm_CreateEx",
    "fb_tcalarm/SetJsonAttribute": "FB_TcAlarm_SetJsonAttribute",
    # fb_tcmessage
    "fb_tcmessage/Create": "FB_TcMessage_Create",
    "fb_tcmessage/CreateEx": "FB_TcMessage_CreateEx",
    "fb_tcmessage/SetJsonAttribute": "FB_TcMessage_SetJsonAttribute",
    # fb_tceventbase methods kept their bare name in original tree
    "fb_tceventbase/EqualsTo": "EqualsTo",
    "fb_tceventbase/EqualsToEventClass": "EqualsToEventClass",
    "fb_tceventbase/EqualsToEventEntry": "EqualsToEventEntry",
    "fb_tceventbase/EqualsToEventEntryEx": "EqualsToEventEntryEx",
    "fb_tceventbase/GetJsonAttribute": "GetJsonAttribute",
    "fb_tceventbase/Release": "Release",
    "fb_tceventbase/RequestEventClassName": "RequestEventClassName",
    "fb_tceventbase/RequestEventText": "RequestEventText",
    "fb_tceventbase/ipArguments": "ipArguments",
    "fb_tceventbase/ipSourceInfo": "ipSourceInfo",
    # fb_tceventlogger methods
    "fb_tceventlogger/ClearAlarms": "ClearAlarms",
    "fb_tceventlogger/ClearAllAlarms": "ClearAllAlarms",
    "fb_tceventlogger/ClearLoggedEvents": "ClearLoggedEvents",
    "fb_tceventlogger/ConfirmAlarms": "ConfirmAlarms",
    "fb_tceventlogger/ConfirmAllAlarms": "ConfirmAllAlarms",
    "fb_tceventlogger/ExportLoggedEvents": "ExportLoggedEvents",
    "fb_tceventlogger/GetAlarm": "GetAlarm",
    "fb_tceventlogger/GetAlarmEx": "GetAlarmEx",
    "fb_tceventlogger/IsAlarmRaised": "IsAlarmRaised",
    "fb_tceventlogger/IsAlarmRaisedEx": "IsAlarmRaisedEx",
    "fb_tceventlogger/SendMessage": "SendMessage",
    "fb_tceventlogger/SendMessage2": "SendMessage2",
    "fb_tceventlogger/SendMessageEx": "SendMessageEx",
    "fb_tceventlogger/SendMessageEx2": "SendMessageEx2",
    # fb_listenerbase2 methods
    "fb_listenerbase2/Execute": "Execute",
    "fb_listenerbase2/Subscribe": "Subscribe",
    "fb_listenerbase2/Subscribe2": "Subscribe2",
    "fb_listenerbase2/Unsubscribe": "Unsubscribe",
    "fb_listenerbase2/OnAlarmCleared": "OnAlarmCleared",
    "fb_listenerbase2/OnAlarmConfirmed": "OnAlarmConfirmed",
    "fb_listenerbase2/OnAlarmDisposed": "OnAlarmDisposed",
    "fb_listenerbase2/OnAlarmRaised": "OnAlarmRaised",
    "fb_listenerbase2/OnMessageSent": "OnMessageSent",
    # fb_tcarguments
    "fb_tcarguments/IsEmpty": "IsEmpty",
    # misc
    "misc/FB_TcEvent": "FB_TcEvent",
}

REG: dict[tuple[str, str], dict] = {}


def reg(parent: str, name: str, **kw):
    REG[(parent, name)] = kw


# ---------- shared bits ----------
COMMON_ALARM_PITFALLS = [
    ("EventLogger 实例数据不在 RETAIN 区，CX 重启后报警状态全清。需要事故重现请自己用 RETAIN BOOL 保存关键标志位。", True),
    ("`Create()` 同一 GUID+EventID 只能调一次，重复调用返回 `ERROR_ALREADY_EXISTS`。", False),
]


# ============================================================
# 3.6 FB_TcAlarm + methods
# ============================================================
reg("fb_tcalarm", "FB_TcAlarm",
    summary=(
        "`FB_TcAlarm` 是 TwinCAT 3 EventLogger 体系里代表**有状态报警**（alarm）的功能块（FB），"
        "继承自 `FB_TcEventBase` 并实现 `I_TcAlarm` 接口。一条报警在生命周期里有"
        "Raised（已触发）/ Cleared（已清除）/ Confirmed（已确认）三种状态，本 FB 把这三态封装为 "
        "`Raise()` / `Clear()` / `Confirm()` 三个方法。\n\n"
        "实际用法：声明一个 `FB_TcAlarm` 实例，先调 `Create()` 把它注册进 EventLogger"
        "（指定事件类 GUID、事件 ID、严重级别、是否需要确认），之后在业务里"
        "上升沿调 `Raise()`、下降沿调 `Clear()`、操作员点确认时调 `Confirm()`。"
        "EventLogger 负责把状态变化广播给所有 `FB_ListenerBase2` 订阅者，并写入事件日志，"
        "可被 TwinCAT HMI / ADS 客户端 / TF6420 数据库导出工具读取。"
    ),
    behavior=(
        "本 FB 自身没有顶层 VAR_INPUT；交互全部通过方法调用。**典型生命周期**：上电后第一次扫描调一次 `Create()`"
        "（向 EventLogger 申请 alarm 槽位）；业务故障逻辑里上升沿调 `Raise()` 触发报警，"
        "故障恢复后调 `Clear()` 解除报警；如果 `bWithConfirmation = TRUE`，"
        "再等操作员在 HMI 上点确认按钮后调 `Confirm()` 把确认状态置位，整条报警才走完。\n\n"
        "状态切换在调用方法时**同步**生效，但 EventLogger 把变化分发给监听器与持久化日志的过程是"
        "**异步**的（跨 RT/非 RT 域），HMI 刷新延迟通常在毫秒级。报警实例不在 RETAIN 区，"
        "CX 控制器重启后所有状态归零，长期审计必须依赖 EventLogger 自身的持久化日志（事件库文件）。"
    ),
    return_kind="NONE",
    pitfalls=[
        ("`Create()` 必须只调一次：用 `IF NOT bCreated THEN bCreated := SUCCEEDED(fb.Create(...)); END_IF` 包裹，否则每周期重复 `Create()` 会拿到 `ERROR_ALREADY_EXISTS` 并刷屏日志。", False),
        ("`bWithConfirmation = TRUE` 时只 Raise + Clear 不够：HMI 仍显示\"等待确认\"。必须等操作员动作后调 `Confirm()` 才完成生命周期。", False),
        ("掉电不保持：实例不是 RETAIN，CX 重启所有 alarm 状态归零。", True),
        ("同一 FB 实例不要交错触发多个故障——每个故障开独立 `FB_TcAlarm` 实例。", True),
        ("`Release()` 在动态 NEW/__DELETE 用法里必须显式调用；静态实例可以不释放。", False),
        ("`ipSourceInfo := 0` 即用默认源信息（PLC 实例符号路径），多 PLC 共用一个 EventLogger 时才需要自定义 `FB_TcSourceInfo`。", False),
    ],
    scenario=(
        "**场景**：包装机故障管理。每台机器配 30-50 个潜在故障点（封口温度异常、纸张卡住、气压不足、急停按下…），"
        "每个故障对应一个独立的 `FB_TcAlarm` 实例；故障发生时 HMI 红灯闪烁、生产计数暂停、要求操作员"
        "处理后按确认键，EventLogger 把全过程持久化以便事后审计。"
    ),
    value=(
        "**价值**：报警的「边沿触发-持续状态-确认归档」是工业最常见的三态模式，"
        "手写至少需要 3 个 BOOL + 1 个时间戳 + 1 套 HMI 联动。用本 FB 一句 `Raise()` 完成，"
        "且自动集成进 EventLogger 的统一审计/查询/导出，省掉自建报警表。"
    ),
    alt=(
        "**替代方案对比**：纯 BOOL + HMI 自建报警表 → 没有审计追溯；"
        "`Tc2_System.ADSLOGSTR` → 只写文本日志、没结构化字段；第三方 SCADA 报警包 → 锁品牌、与 PLC 不同步。"
        "本 FB 走 Beckhoff 原生 EventLogger，免费、跨 HMI 厂商。"
    ),
    xml_scenario="包装机封口温度异常报警（需要操作员确认才能复位的故障）",
    xml_value=("一句 Raise()/Clear()/Confirm() 完成\"上升沿报警→保持显示→等待确认\"三态，"
               "省去自建报警表 + HMI 联动 + 持久化的全部样板代码"),
    xml_verify=(
        "登录后写 bSealTempAlarm := TRUE，HMI EventLogger 视图应立即显示状态 Raised；"
        "写 FALSE 后状态变 Cleared 但 ConfirmationState 仍为 WaitForConfirmation；"
        "写 bConfirmReq := TRUE 后看到 Confirmed 状态，整条生命周期结束"
    ),
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "包装机封口温度故障报警实例"),
        ("bCreated", "BOOL", None, "Create() 是否已成功执行（一次性 latch）"),
        ("bSealTempAlarm", "BOOL", "FALSE", "上层逻辑给出的故障信号（在线置 TRUE 模拟）"),
        ("bConfirmReq", "BOOL", "FALSE", "操作员在 HMI 按下确认键时置 TRUE"),
        ("bSealTempAlarmPrev", "BOOL", None, "用于检测上升/下降沿"),
        ("hr", "HRESULT", None, "方法返回值监视"),
        ("guidEventClass", "GUID", None, "实际事件类 GUID（请通过 EventClass 编辑器导出）"),
    ],
    xml_call=(
        "// 第一次扫描注册到 EventLogger（GUID + EventID 由工程师在事件类编辑器配置）\n"
        "IF NOT bCreated THEN\n"
        "    hr := fbAlarm.Create(\n"
        "        eventClass := guidEventClass,\n"
        "        nEventId := 1001,                  // 封口温度异常事件 ID\n"
        "        eSeverity := TcEventSeverity.Error,\n"
        "        bWithConfirmation := TRUE,         // 需要操作员确认\n"
        "        ipSourceInfo := 0);                // 用默认源信息\n"
        "    bCreated := SUCCEEDED(hr);\n"
        "END_IF;\n"
        "\n"
        "// 上升沿 Raise，下降沿 Clear\n"
        "IF bSealTempAlarm AND NOT bSealTempAlarmPrev THEN\n"
        "    fbAlarm.Raise(nTimeStamp := 0);        // 0 = 用当前系统时间\n"
        "END_IF;\n"
        "IF NOT bSealTempAlarm AND bSealTempAlarmPrev THEN\n"
        "    fbAlarm.Clear(nTimeStamp := 0, bRemove := FALSE);\n"
        "END_IF;\n"
        "bSealTempAlarmPrev := bSealTempAlarm;\n"
        "\n"
        "// 操作员按确认键\n"
        "IF bConfirmReq THEN\n"
        "    fbAlarm.Confirm(nTimeStamp := 0);\n"
        "    bConfirmReq := FALSE;\n"
        "END_IF;"
    ),
    related=["FB_TcMessage", "FB_TcEventBase", "FB_TcEventLogger", "FB_ListenerBase2"],
)


reg("fb_tcalarm", "Create",
    summary=(
        "`FB_TcAlarm.Create()` 把当前 alarm 实例注册到 EventLogger，绑定到指定事件类（GUID）+ 事件 ID。"
        "调用成功后这个 `FB_TcAlarm` 实例就能在后续被 `Raise()` / `Clear()` / `Confirm()` 操作。\n\n"
        "事件类 GUID 不是 PLC 里手写的——它在 TwinCAT 工程的 EventClass 编辑器（XAE 菜单 View → Other Windows → TwinCAT EventClass）里定义，"
        "每个事件类绑定多语言文本资源（中/英/德…）。`nEventId` 是事件类内的唯一编号，对应到具体的"
        "事件文本模板。"
    ),
    behavior=(
        "本方法是一次性注册：调用时 EventLogger 内部建立 alarm 实例 → 写入事件日志 → 把 `FB_TcAlarm` 加入"
        "活动 alarm 表。**必须只调一次**：常见做法是用 `bCreated : BOOL` latch 包裹，第一次 `SUCCEEDED(hr)`"
        "之后不再调用。重复调用同一 GUID+EventID 会返回 `ERROR_ALREADY_EXISTS`。\n\n"
        "`ipSourceInfo` 为 `0` 时 EventLogger 自动用 PLC 实例的符号路径作为源信息（默认行为）；"
        "如果需要把同一 alarm 关联到一个具体设备/工位，传入预先 `FB_TcSourceInfo` 实例的接口指针。"
        "`bWithConfirmation = TRUE` 让此报警在 Clear 后仍保持 \"等待确认\" 状态，需要操作员显式 Confirm。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "alarm 已成功注册", "继续后续 Raise/Clear/Confirm"),
        ("ERROR_ALREADY_EXISTS", "同 GUID+EventID 的 alarm 已注册", "用 bCreated latch 跳过重复调用"),
        ("其他错误", "事件类未在工程里定义、ADS 通讯异常等 ⚠️ PDF 未详列", "对照 ADS Return Codes / 检查 EventClass 配置"),
    ],
    var_desc={
        "eventClass": "事件类的 GUID（在 EventClass 编辑器里定义）",
        "nEventId": "事件 ID，事件类内唯一标识（对应多语言文本模板）",
        "eSeverity": "事件严重级别（Verbose/Info/Warning/Error/Critical）",
        "bWithConfirmation": "TRUE = Clear 后仍需操作员 Confirm 才完整结束；FALSE = Clear 即完成",
        "ipSourceInfo": "源信息接口指针；传 0 用默认（PLC 符号路径）",
    },
    pitfalls=[
        ("一次性注册：必须用 `IF NOT bCreated THEN ... bCreated := SUCCEEDED(hr); END_IF` 包裹。", False),
        ("`bWithConfirmation` 设错就改不了：注册后这个属性是固定的，需要切换得先 `Release()` 再重新 Create。", True),
        ("事件类 GUID 必须在 XAE EventClass 编辑器里先定义，否则 HMI 上显示 \"未知事件\"。", False),
        ("`ipSourceInfo` 传无效指针会导致 alarm 创建失败但返回的 HRESULT 不一定明显——建议先 `<>`0 判空。", True),
    ],
    scenario=(
        "**场景**：设备启动初始化阶段，把本工位所有可能报警一次性注册进 EventLogger。"
        "比如灌装线 30 个 alarm 实例都在 `MAIN.bFirstScan` 周期里 Create()，"
        "之后业务模块只负责 Raise/Clear。"
    ),
    value=(
        "**价值**：把\"注册\"和\"触发\"解耦——业务代码只关心\"现在出故障了\"，不关心怎么向 EventLogger 报告。"
        "Create 阶段集中管理事件类/严重级别/确认策略，便于后续工艺变更时统一调整。"
    ),
    alt=(
        "**替代方案对比**：直接用 `FB_TcEventLogger.SendMessageEx()` 免实例报警 → 没法跟踪状态、没法 Clear/Confirm；"
        "用 `CreateEx` 传 `TcEventEntry` 而不是分散字段 → 当事件已经打包成 TcEventEntry（如从远程接收）时更省事。"
    ),
    xml_scenario="包装机封口温度异常报警的一次性注册",
    xml_value="把\"事件类 + ID + 严重级别 + 确认要求\"集中在 Create 里，业务代码后续只管 Raise/Clear",
    xml_verify=(
        "登录后单步：第一个扫描 hr 应该是 0 (S_OK)，bCreated 变 TRUE；"
        "之后周期再走 IF 判断被 bCreated 截住不再调用；强行让 bCreated := FALSE 再次进入 Create() 会拿到 ERROR_ALREADY_EXISTS"
    ),
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "FB_TcAlarm 实例（继承自 FB_TcEventBase）"),
        ("bCreated", "BOOL", None, "Create() 是否已成功执行（latch）"),
        ("hr", "HRESULT", None, "Create 返回值监视"),
        ("guidEventClass", "GUID", None, "事件类 GUID（请通过 EventClass 编辑器导出后写入）"),
    ],
    xml_call=(
        "// 第一次扫描注册 alarm 到 EventLogger；之后由 bCreated latch 截住\n"
        "IF NOT bCreated THEN\n"
        "    hr := fbAlarm.Create(\n"
        "        eventClass := guidEventClass,\n"
        "        nEventId := 1001,                  // 封口温度异常\n"
        "        eSeverity := TcEventSeverity.Error,\n"
        "        bWithConfirmation := TRUE,\n"
        "        ipSourceInfo := 0);                // 0 = 默认源信息（符号路径）\n"
        "    bCreated := SUCCEEDED(hr);\n"
        "END_IF;"
    ),
    related=["FB_TcAlarm", "FB_TcAlarm.CreateEx", "FB_TcAlarm.Raise", "FB_TcMessage.Create"],
)


reg("fb_tcalarm", "CreateEx",
    summary=(
        "`FB_TcAlarm.CreateEx()` 与 `Create()` 功能相同——把 alarm 实例注册到 EventLogger——区别在于"
        "事件参数以 **`TcEventEntry` 结构体一次性传入**，而不是分散的 `eventClass`/`nEventId`/`eSeverity`。\n\n"
        "适合\"事件定义本身已经是结构化数据\"的场景：从远程 EventLogger 接收事件、从配置文件加载事件清单、"
        "或在多个 FB 之间传递事件定义而不想拆解字段。"
    ),
    behavior=(
        "调用同 `Create()`：成功返回 `S_OK` 并把 alarm 加入活动表，重复返回 `ERROR_ALREADY_EXISTS`。"
        "唯一区别是事件定义来源——`stEventEntry` 包含 GUID + EventID + Severity 三件套，"
        "EventLogger 内部把它们拆开后走和 `Create()` 一样的流程。\n\n"
        "**典型用法**：维护一张全局 `aEvents : ARRAY[1..N] OF TcEventEntry`，初始化阶段循环遍历调用 `CreateEx()`"
        "批量注册；业务代码只通过下标引用，便于事件清单的版本控制。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "alarm 已成功注册", "继续后续 Raise/Clear/Confirm"),
        ("ERROR_ALREADY_EXISTS", "同事件已注册", "用 bCreated latch 跳过"),
        ("其他错误", "事件类未定义或 ADS 异常 ⚠️ PDF 未列具体码", "查 ADS Return Codes"),
    ],
    var_desc={
        "stEventEntry": "事件入口结构体（含 GUID + EventID + Severity）",
        "bWithConfirmation": "TRUE = 需要操作员 Confirm 才完整结束生命周期",
        "ipSourceInfo": "源信息接口指针；传 0 用默认（PLC 符号路径）",
    },
    pitfalls=[
        ("`stEventEntry` 必须是有效的事件定义——内部 GUID 全 0 / EventID = 0 会导致 HMI 显示空白。", False),
        ("批量 CreateEx 时把成功标志放在数组每个元素旁，便于失败重试。", True),
        ("和 `Create()` 一样要 latch 防止重复注册。", False),
    ],
    scenario="从配方文件加载 50 个工艺报警定义后批量注册到 EventLogger",
    value="事件清单与代码解耦——改报警定义不用改业务代码，"
          "只改配方文件或外部数据库",
    alt="直接 `Create()` 分字段调用 → 当事件已是结构体时多此一举；"
        "`AdsErr_TO_TcEventEntry` → 把 ADS 错误码转 TcEventEntry 再 CreateEx 是常见 ADS 错误集中报警模式",
    xml_scenario="把已经在结构体里的事件定义批量注册（典型：从远程 EventLogger 同步事件清单）",
    xml_value="一次结构体调用替代 5 个分散字段，便于循环批量注册",
    xml_verify="登录后让 bCreated := FALSE 触发一次 Create；hr 第一次应为 S_OK，再次执行得到 ERROR_ALREADY_EXISTS",
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "FB_TcAlarm 实例"),
        ("bCreated", "BOOL", None, "Create latch"),
        ("hr", "HRESULT", None, "返回值监视"),
        ("stEventEntry", "TcEventEntry", None, "在线写入事件定义（GUID + EventID + Severity）"),
    ],
    xml_call=(
        "// 用 TcEventEntry 结构体一次性注册（适合事件清单已在数组里的场景）\n"
        "IF NOT bCreated THEN\n"
        "    hr := fbAlarm.CreateEx(\n"
        "        stEventEntry := stEventEntry,\n"
        "        bWithConfirmation := TRUE,\n"
        "        ipSourceInfo := 0);\n"
        "    bCreated := SUCCEEDED(hr);\n"
        "END_IF;"
    ),
    related=["FB_TcAlarm.Create", "AdsErr_TO_TcEventEntry", "HRESULTAdsErr_TO_TcEventEntry"],
)


reg("fb_tcalarm", "Raise",
    summary=(
        "`FB_TcAlarm.Raise()` 把 alarm 状态从 \"Not Raised\" 切换到 \"Raised\"。如果创建时设了 "
        "`bWithConfirmation = TRUE`，确认状态同步置为 `WaitForConfirmation`。\n\n"
        "调用时机：业务故障逻辑里检测到故障**上升沿**——前一周期 FALSE、本周期 TRUE。"
        "调一次 Raise() 之后 EventLogger 在事件日志里追加一条 Raised 记录，HMI 把这条 alarm 标红显示。"
    ),
    behavior=(
        "方法在调用瞬间同步切换状态。`nTimeStamp = 0` 用当前系统时间；非 0 用调用方传入的时间戳"
        "（自 1601-01-01 UTC 的 100ns 数）。后者适合\"事故重放\"或\"从远程接收事件后再 Raise\"等场景。\n\n"
        "**与 Clear 的成对调用**：典型业务模式是 IF 故障信号 AND NOT 前一周期值 THEN Raise; IF NOT 故障信号 AND 前一周期值 THEN Clear。"
        "**不要每个周期都调 Raise**，否则会产生大量重复日志、刷爆 HMI。\n\n"
        "如果当前已经是 Raised 状态再次调 Raise 会返回 `ADS_E_INVALIDSTATE`，状态不变，不会重复写日志。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "状态成功切换到 Raised", "继续业务"),
        ("ADS_E_INVALIDSTATE", "alarm 已处于 Raised 状态", "通常无需处理；表示边沿检测漏了"),
        ("其他错误", "EventLogger 内部异常 ⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={
        "nTimeStamp": "事件时间戳：0 = 用当前系统时间；非 0 = 自 1601-01-01 UTC 起的 100ns 数",
    },
    pitfalls=[
        ("Raise 必须边沿触发，不能每周期都调，否则日志会被刷爆。", False),
        ("已 Raised 状态再 Raise 返回 ADS_E_INVALIDSTATE——不是错误，只是表示状态没变。", False),
        ("非 0 时间戳必须是 100ns 单位且基准是 1601-01-01 UTC（FILETIME），不是 Unix 时间。", True),
        ("Raise 之前必须先 Create()——否则方法调用无效。", False),
    ],
    scenario="电机过载检测：电流传感器读数超过阈值的上升沿触发一次 Raise()",
    value="一句调用完成\"事件日志 + HMI 显示 + 监听器分发\"三件事，"
          "手写至少需要 ADSLOGSTR + HMI 联动 + 持久化三套独立逻辑",
    alt="直接用 ADSLOGSTR 写文本日志 → 没结构化、不能 Clear/Confirm；"
        "用 `FB_TcEventLogger.SendMessageEx()` → 适合无状态通知不适合有状态报警",
    xml_scenario="电机过载故障的上升沿触发（电流瞬时超过 8A 报警）",
    xml_value="边沿触发一次 Raise() 即把报警写入 EventLogger 并自动分发到 HMI",
    xml_verify=(
        "登录后写 rCurrent := 9.0，bMotorOverCurrent 在下一周期变 TRUE 并上升沿调用 Raise；"
        "HMI EventLogger 视图出现一条 Raised 记录；再次写 9.0 不会重复触发（边沿已过）"
    ),
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "电机过载报警实例"),
        ("bCreated", "BOOL", None, "Create() latch"),
        ("rCurrent", "REAL", "0.0", "电机电流 (A)，在线写值模拟"),
        ("rOverLimit", "REAL", "8.0", "过载阈值"),
        ("bMotorOverCurrent", "BOOL", None, "故障信号（rCurrent &gt; rOverLimit）"),
        ("bMotorOverCurrentPrev", "BOOL", None, "上一周期值（边沿检测）"),
        ("hr", "HRESULT", None, "Raise 返回值监视"),
        ("guidEventClass", "GUID", None, "事件类 GUID"),
    ],
    xml_call=(
        "// 一次性注册\n"
        "IF NOT bCreated THEN\n"
        "    hr := fbAlarm.Create(eventClass := guidEventClass, nEventId := 2001,\n"
        "        eSeverity := TcEventSeverity.Error, bWithConfirmation := FALSE,\n"
        "        ipSourceInfo := 0);\n"
        "    bCreated := SUCCEEDED(hr);\n"
        "END_IF;\n"
        "\n"
        "// 故障信号 = 电流超阈值\n"
        "bMotorOverCurrent := rCurrent &gt; rOverLimit;\n"
        "\n"
        "// 上升沿调用 Raise，0 = 用当前系统时间\n"
        "IF bMotorOverCurrent AND NOT bMotorOverCurrentPrev THEN\n"
        "    hr := fbAlarm.Raise(nTimeStamp := 0);\n"
        "END_IF;\n"
        "bMotorOverCurrentPrev := bMotorOverCurrent;"
    ),
    related=["FB_TcAlarm.Clear", "FB_TcAlarm.Confirm", "FB_TcAlarm.Create"],
)


reg("fb_tcalarm", "Clear",
    summary=(
        "`FB_TcAlarm.Clear()` 把 alarm 状态从 \"Raised\" 切换到 \"Not Raised\"（已清除）。"
        "如果创建时 `bWithConfirmation = TRUE`，确认状态保持 `WaitForConfirmation` 不变，"
        "需要后续 `Confirm()` 调用才完整结束。\n\n"
        "`bRemove := TRUE` 时除了清除状态外，还把 alarm 实例从 EventLogger 的活动表中移除（释放槽位）；"
        "`bRemove := FALSE` 保留实例以便下次 Raise 复用。"
    ),
    behavior=(
        "调用时机：故障信号**下降沿**——前一周期 TRUE、本周期 FALSE。Clear 立即同步切换状态。"
        "如果当前并不在 Raised 状态（已经是 Cleared），调用返回 `ADS_E_INVALIDSTATE`，状态不变。\n\n"
        "**`bRemove` 取舍**：常驻设备故障建议 `FALSE`（实例长期复用，避免反复 Create/Remove 抖动）；"
        "动态生成的临时故障（如一次性配方告警）建议 `TRUE` 让 EventLogger 回收槽位。\n\n"
        "Clear 不会自动 Confirm。要让 alarm 完整走完生命周期，confirmation 必须显式调 `Confirm()`，"
        "或在工程里关掉 `bWithConfirmation`。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "状态成功切换到 Cleared", "若 bWithConfirmation = TRUE 等待 Confirm()"),
        ("ADS_E_INVALIDSTATE", "alarm 不在 Raised 状态", "通常表示边沿检测漏"),
        ("其他错误", "⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={
        "nTimeStamp": "事件时间戳：0 = 用当前系统时间；非 0 = 自 1601-01-01 UTC 起的 100ns 数",
        "bRemove": "TRUE = 同时从 EventLogger 活动表移除（释放槽位）；FALSE = 保留实例以便复用",
    },
    pitfalls=[
        ("Clear 不等于 Confirm：若 bWithConfirmation = TRUE，alarm 仍处于 WaitForConfirmation。", False),
        ("`bRemove := TRUE` 后再 Raise 必须重新 Create()，否则会失败。", True),
        ("已 Cleared 状态再 Clear 返回 ADS_E_INVALIDSTATE，不是错误。", False),
        ("常驻报警建议 `bRemove := FALSE`，避免反复 Create 引起的抖动。", True),
    ],
    scenario="电机过载故障消失后清除报警（电流降回阈值以下的下降沿）",
    value="下降沿一次调用完成清除 + 日志记录，免去手写状态机",
    alt="不 Clear 让 alarm 保持 Raised → HMI 永远显示故障，操作员困惑；"
        "改用 Remove 一步直接消失 → 失去\"故障已恢复但需确认\"的中间状态",
    xml_scenario="电机过载故障消失（电流降回安全值）的下降沿清除",
    xml_value="把 Clear 和 Raise 配对，让 HMI 准确反映\"故障已恢复\"状态",
    xml_verify=(
        "先让 rCurrent &gt; rOverLimit 触发 Raise（HMI 显示 Raised）；"
        "再写 rCurrent := 5.0 让信号回落，下降沿调用 Clear；HMI 状态变 Cleared 但若 bWithConfirmation 仍显示\"等待确认\""
    ),
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "电机过载报警实例"),
        ("bCreated", "BOOL", None, "Create latch"),
        ("rCurrent", "REAL", "0.0", "电机电流 (A)"),
        ("rOverLimit", "REAL", "8.0", "过载阈值"),
        ("bMotorOverCurrent", "BOOL", None, "故障信号"),
        ("bMotorOverCurrentPrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "返回值监视"),
        ("guidEventClass", "GUID", None, "事件类 GUID"),
    ],
    xml_call=(
        "IF NOT bCreated THEN\n"
        "    hr := fbAlarm.Create(eventClass := guidEventClass, nEventId := 2001,\n"
        "        eSeverity := TcEventSeverity.Error, bWithConfirmation := FALSE,\n"
        "        ipSourceInfo := 0);\n"
        "    bCreated := SUCCEEDED(hr);\n"
        "END_IF;\n"
        "\n"
        "bMotorOverCurrent := rCurrent &gt; rOverLimit;\n"
        "\n"
        "// 上升沿 Raise，下降沿 Clear（bRemove := FALSE 保留实例以便复用）\n"
        "IF bMotorOverCurrent AND NOT bMotorOverCurrentPrev THEN\n"
        "    hr := fbAlarm.Raise(nTimeStamp := 0);\n"
        "END_IF;\n"
        "IF NOT bMotorOverCurrent AND bMotorOverCurrentPrev THEN\n"
        "    hr := fbAlarm.Clear(nTimeStamp := 0, bRemove := FALSE);\n"
        "END_IF;\n"
        "bMotorOverCurrentPrev := bMotorOverCurrent;"
    ),
    related=["FB_TcAlarm.Raise", "FB_TcAlarm.Confirm", "FB_TcEventLogger.ClearAlarms"],
)


reg("fb_tcalarm", "Confirm",
    summary=(
        "`FB_TcAlarm.Confirm()` 把 alarm 的确认状态切到 `Confirmed`。"
        "只有 alarm 创建时 `bWithConfirmation = TRUE` 才需要这步——它代表\"操作员已经看到这条故障并处理了\"。\n\n"
        "调用时机：HMI 上操作员点确认按钮（边沿触发），或者业务上判定故障已被处置（如自动复位条件）。"
    ),
    behavior=(
        "Confirm 是单纯的确认状态切换，不改变 Raised/Cleared 主状态。一条 alarm 完整生命周期是："
        "Created → Raised → Cleared → Confirmed。前三步必经，第四步只在 `bWithConfirmation = TRUE` 时存在。\n\n"
        "**典型用法**：HMI 上的「确认所有未确认」按钮可以走 `FB_TcEventLogger.ConfirmAllAlarms()` 批量"
        "确认所有报警；单点确认则用本方法。`nTimeStamp = 0` 用当前时间记录确认时刻——这个时间在事后审计里"
        "是\"操作员响应时间\"的关键指标。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "确认成功", "继续业务"),
        ("ADS_E_INVALIDSTATE", "alarm 不需要确认或已确认", "通常无需处理"),
        ("其他错误", "⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={
        "nTimeStamp": "确认事件时间戳：0 = 用当前系统时间；非 0 = 自 1601-01-01 UTC 起的 100ns 数",
    },
    pitfalls=[
        ("`bWithConfirmation = FALSE` 的 alarm 不能 Confirm，否则返回 ADS_E_INVALIDSTATE。", False),
        ("Confirm 不会自动 Clear，必须先 Clear 后 Confirm 或反过来都行，但两者都得做。", False),
        ("HMI 集成时记得用边沿触发——按住按钮不松不要每周期都 Confirm。", True),
        ("操作员误确认无法撤销——审计要靠 EventLogger 的时间戳记录。", True),
    ],
    scenario="HMI 上操作员处理完故障后点\"确认\"按钮，关闭这条报警条目",
    value="确认时刻被自动写入 EventLogger 审计日志，事后能查\"故障响应时长 = Confirm 时间 - Raise 时间\"",
    alt="不用 Confirm 直接 Clear → 失去操作员审计；"
        "走 `ConfirmAllAlarms` 批量 → 适合\"全清\"按钮，不适合单条精细确认",
    xml_scenario="操作员在 HMI 上单点确认包装机封口温度异常报警",
    xml_value="一次 Confirm() 完成确认 + 时间戳写入 + 监听器分发；HMI 上该条报警从\"等待确认\"变\"已处理\"",
    xml_verify=(
        "需要先有一条 bWithConfirmation = TRUE 的 alarm 处于 Raised 状态；"
        "在线写 bConfirmReq := TRUE 模拟点击确认按钮，下一周期看 HMI 上 ConfirmationState 变 Confirmed"
    ),
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "已 Create 且 Raised 的 alarm 实例"),
        ("bConfirmReq", "BOOL", "FALSE", "操作员确认按钮（在线置 TRUE 模拟）"),
        ("bConfirmReqPrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "Confirm 返回值监视"),
    ],
    xml_call=(
        "// 假定 fbAlarm 已在前面某处 Create()+Raise()，本片段只演示确认动作\n"
        "// 上升沿触发：HMI 按钮按下瞬间调一次 Confirm（不要每周期都调）\n"
        "IF bConfirmReq AND NOT bConfirmReqPrev THEN\n"
        "    hr := fbAlarm.Confirm(nTimeStamp := 0);   // 0 = 当前时间\n"
        "END_IF;\n"
        "bConfirmReqPrev := bConfirmReq;"
    ),
    related=["FB_TcAlarm.Raise", "FB_TcAlarm.Clear", "FB_TcEventLogger.ConfirmAlarms",
             "FB_TcEventLogger.ConfirmAllAlarms"],
)


reg("fb_tcalarm", "SetJsonAttribute",
    summary=(
        "`FB_TcAlarm.SetJsonAttribute()` 给 alarm 实例追加一段 JSON 形式的自定义属性，"
        "在事件分发到 HMI / 数据库 / 远程客户端时与标准字段（EventClass/EventID/Severity/SourceInfo/Arguments）"
        "一并传递。\n\n"
        "整段属性以 JSON 字符串形式传入，可携带任意键值结构，例如 "
        "`'{\"batch\":\"B-2026-0511-001\",\"operator\":\"WangWu\",\"recipe\":\"R03\"}'`。"
        "便于 MES/ERP 系统在事后审计时做结构化分析。"
    ),
    behavior=(
        "方法签名只有一个 `VAR_IN_OUT CONSTANT sJsonAttribute : STRING`。"
        "EventLogger 把整段 JSON 存入 alarm 的扩展属性，下一次状态变化（Raise/Clear/Confirm）时随事件一起广播。\n\n"
        "**调用时机**：在 Raise 之前调用，确保事件分发时属性已附上。多次调用会**覆盖**上一次的 JSON 内容。"
        "字符串必须是合法 JSON，否则 EventLogger 端解析失败、HMI 看不到自定义字段。\n\n"
        "本方法在 TwinCAT 3 EventLogger 4026+ 版本完整可用，老版本可能行为受限。"
        "VAR_IN_OUT CONSTANT 形式：调用方传入字符串时 PLC 不复制（节省栈），方法内部不能修改它。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "JSON 属性已成功写入", "继续业务"),
        ("其他错误", "⚠️ PDF 未列详细码，可能因 JSON 非法、长度超限等", "校验 JSON 格式 / 缩短内容 / 查 ADS Return Codes"),
    ],
    var_desc={
        "sJsonAttribute": "合法 JSON 字符串（建议用 STRING(255) 或更长以容纳完整 JSON 对象）",
    },
    pitfalls=[
        ("传入字符串必须是**合法 JSON 整体**——`'{\"a\":1}'` 行；裸 `'hello'` 不是合法 JSON 对象/数组会被丢弃。", False),
        ("STRING 默认长度 80 字节往往不够，注意声明 `STRING(255)` 或 `STRING(1024)`。", True),
        ("调用会覆盖上次内容——要追加键得自己在 PLC 端拼接完整 JSON 再传入。", True),
        ("HMI 端要主动消费 JSON——TwinCAT HMI 默认只显示标准字段，需要绑定 JSON 到自定义控件。", True),
    ],
    scenario="批次追溯。每个 alarm 附带 batch id + operator name + recipe version，"
             "事故事后能精确定位\"某批某操作员在某配方下出的问题\"",
    value="把工艺上下文直接挂在 alarm 上，省掉手写\"alarm + 上下文表\"的 JOIN 查询；"
          "MES 拉数据时一个 EventEntry 就够",
    alt="把上下文塞进 `FB_TcArguments` → 适合标准类型参数（int/real/bool/string），"
        "JSON 属性更适合**嵌套/动态**结构；走外部数据库 INSERT → 阻塞 PLC 周期、且与 alarm 时间戳不严格同步",
    xml_scenario="包装机 alarm 附加批次追溯信息（batch id + 操作员）",
    xml_value="一句 SetJsonAttribute 把工艺上下文绑到 alarm 上，MES 拉取时一并到位",
    xml_verify=(
        "登录后写 bSetAttr := TRUE 触发一次设置；EventLogger 的事件详情面板（或 ADS 工具查事件）应能看到 JSON 字段；"
        "改写 sBatchId := 'B-002' 后再次触发会覆盖前一次"
    ),
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "alarm 实例（应已 Create 完成）"),
        ("bSetAttr", "BOOL", "FALSE", "上升沿触发设置属性"),
        ("bSetAttrPrev", "BOOL", None, "边沿检测"),
        ("sBatchId", "STRING(64)", "'B-2026-0511-001'", "批次号"),
        ("sJsonAttribute", "STRING(255)", None, "拼接好的完整 JSON"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "// 拼接完整 JSON（包含批次号 + 操作员）。注意 STRING 容量要够装下整段 JSON。\n"
        "sJsonAttribute := CONCAT('{\"batch\":\"',\n"
        "                        CONCAT(sBatchId,\n"
        "                        CONCAT('\",\"operator\":\"', '\"WangWu\"}')));\n"
        "\n"
        "// 边沿触发：在 Raise 之前调一次 SetJsonAttribute；该 JSON 会随后续 Raise/Clear/Confirm 一起广播\n"
        "IF bSetAttr AND NOT bSetAttrPrev THEN\n"
        "    hr := fbAlarm.SetJsonAttribute(sJsonAttribute := sJsonAttribute);\n"
        "END_IF;\n"
        "bSetAttrPrev := bSetAttr;"
    ),
    related=["FB_TcAlarm.Create", "FB_TcMessage.SetJsonAttribute",
             "FB_TcEventBase.GetJsonAttribute"],
)
