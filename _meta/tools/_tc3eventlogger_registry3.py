# Tc3_EventLogger registry — Part 3: FB_TcEventLogger + 14 methods
from __future__ import annotations

from _tc3eventlogger_registry import reg


# ============================================================
# 3.10 FB_TcEventLogger + methods
# ============================================================
reg("fb_tceventlogger", "FB_TcEventLogger",
    summary=(
        "`FB_TcEventLogger` 是 TwinCAT 3 EventLogger 体系的**单例式中心组件**，"
        "代表整个 PLC 运行时里的 EventLogger 实例本身。所有报警与消息的注册、广播、查询、清除、确认、"
        "导出操作最终都通过本 FB 完成。\n\n"
        "实际工程里**不需要自己声明实例**——TwinCAT 运行时已自动持有一个全局可用的 EventLogger，"
        "PLC 代码通过 `Tc3_EventLogger` 库提供的全局变量 `FB_TcEventLogger` 或工具函数访问。"
        "本 FB 的方法集分四类：批量管理报警（ClearAlarms / ConfirmAlarms / GetAlarm / IsAlarmRaised…）、"
        "免实例发送消息（SendMessage / SendMessageEx / SendMessage2 / SendMessageEx2）、"
        "清除历史事件（ClearLoggedEvents）、导出事件历史（ExportLoggedEvents 为 CSV）。"
    ),
    behavior=(
        "FB_TcEventLogger 没有 VAR_INPUT 或 VAR_OUTPUT——它是\"对象集合的容器\"，所有交互通过方法。\n\n"
        "**生命周期**：运行时启动时初始化，PLC 停止时清理。报警注册（来自 `FB_TcAlarm.Create()`）后留在内部活动表，"
        "事件按需写入持久化事件日志（默认在 `C:\\ProgramData\\Beckhoff\\TwinCAT3\\EventLogger\\` 下）。\n\n"
        "**批量管理方法**接收一个 `I_TcEventFilter` 过滤器（不传则操作全部）——这让运维代码能针对"
        "「某事件类下所有 alarm」、「某 Severity 以上的事件」做集中清除/确认。"
        "**免实例消息方法**（SendMessage*）适合一次性通知场景，省去注册 FB_TcMessage 实例的样板代码。"
    ),
    return_kind="NONE",
    pitfalls=[
        ("EventLogger 是 PLC 运行时的资源——清除日志、批量确认这类操作影响所有订阅者，权限管控应在 HMI 端实施。", True),
        ("`ClearLoggedEvents` 不可逆——一旦执行历史事件被永久删除（除非配合 ExportLoggedEvents 先导出）。", False),
        ("`GetAlarm` / `IsAlarmRaised` 走的是符号查询不是引用——大量循环里频繁调用会有性能开销。", True),
        ("`ExportLoggedEvents` 是异步——发起后必须轮询 BOOL 返回值。", False),
        ("`SendMessage*` 系列各版本差别细微：带 2/Ex/Ex2 后缀依次增加 JSON 支持 / TcEventEntry 入口 / 二者组合。", True),
    ],
    scenario="MES 系统每天 23:00 触发一次「导出今日全部事件到 CSV → 清除已导出事件」的归档流程",
    value="一组 ClearLoggedEvents + ExportLoggedEvents + ConfirmAlarms 完成全自动归档，"
          "免去自建事件表 + 文件管理 + 状态同步的全部样板代码",
    alt="自建数据库 + 自定义清理脚本 → 阻塞 PLC 周期、与 EventLogger 状态不同步；"
        "靠 HMI 手动导出 → 漏归档风险、人工成本高",
    xml_scenario="MES 集成的每日归档触发流程（导出 + 清除日志 + 确认所有报警）",
    xml_value="一段代码完成多个 EventLogger 维护动作的串联",
    xml_verify=(
        "登录后写 bRunArchiveNow := TRUE，应先看到 ExportLoggedEvents 异步返回 TRUE（导出完成），"
        "再 ClearLoggedEvents、再 ConfirmAllAlarms 各调一次；HMI EventLogger 视图历史事件应被清空但导出文件保留"
    ),
    xml_vars=[
        ("fbLogger", "FB_TcEventLogger", None, "EventLogger 实例（实际工程用全局单例）"),
        ("bRunArchiveNow", "BOOL", "FALSE", "在线置 TRUE 触发归档流程"),
        ("bRunArchiveNowPrev", "BOOL", None, "边沿检测"),
        ("sExportPath", "STRING(120)", "'C:\\Temp\\events_2026-05-11.csv'", "导出文件路径"),
        ("bExportDone", "BOOL", None, "ExportLoggedEvents 完成标志"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "// 边沿触发：先异步导出 → 等完成 → 清日志 → 确认所有报警\n"
        "IF bRunArchiveNow AND NOT bRunArchiveNowPrev THEN\n"
        "    // 启动异步导出。实际工程要分多个状态机周期等 bExportDone = TRUE 后再继续。\n"
        "    bExportDone := fbLogger.ExportLoggedEvents(sFileName := sExportPath, ipExportSettings := 0);\n"
        "    IF bExportDone THEN\n"
        "        hr := fbLogger.ClearLoggedEvents(ipClearSettings := 0);    // 0 = 清全部\n"
        "        hr := fbLogger.ConfirmAllAlarms(nTimeStamp := 0);           // 一并确认\n"
        "    END_IF;\n"
        "END_IF;\n"
        "bRunArchiveNowPrev := bRunArchiveNow;"
    ),
    related=["FB_TcAlarm", "FB_TcMessage", "FB_TcEventCsvExportSettings",
             "FB_TcClearLoggedEventsSettings"],
)


reg("fb_tceventlogger", "ClearAlarms",
    summary=(
        "`FB_TcEventLogger.ClearAlarms()` 批量清除符合过滤条件的活动报警（即调用对应 alarm 的 `Clear()`）。"
        "支持 `I_TcEventFilter` 过滤器精确选择要清除的 alarm 集合。\n\n"
        "适用：操作员在 HMI 上点「清除全部当前报警」按钮、或自动化逻辑里按 Severity / EventClass 批量复位故障状态。"
    ),
    behavior=(
        "对每个匹配的 alarm 调用 `Clear()`：状态从 Raised 转 Cleared。若 alarm 是 `bWithConfirmation = TRUE`，"
        "确认状态保持 `WaitForConfirmation` 不变（除非传 `bResetConfirmation := TRUE`，则同时把确认状态置为 `Reset`）。\n\n"
        "**过滤器逻辑**：`ipFilter` 传 0 时清除**所有**活动 alarm；传入 `FB_TcEventFilter` 实例则按规则匹配。"
        "时间戳 `nTimeStamp = 0` 用当前系统时间记录清除时刻——这个时间在审计里就是\"批量清除动作\"的发生时间。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "批量清除成功", "继续业务"),
        ("其他错误", "过滤器无效 / 内部异常 ⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={
        "nTimeStamp": "清除事件时间戳：0 = 用当前系统时间；非 0 = 自 1601-01-01 UTC 起的 100ns 数",
        "bResetConfirmation": "TRUE = 同时把 WaitForConfirmation 状态置为 Reset；FALSE = 仅清除 Raised 状态",
        "ipFilter": "事件过滤器；传 0 清除全部活动 alarm",
    },
    pitfalls=[
        ("`bResetConfirmation := TRUE` 会绕过操作员确认环节——审计场景慎用。", False),
        ("过滤器传 0 = 清全部，操作前应在 HMI 端给操作员一个二次确认。", True),
        ("Clear 后 alarm 实例仍在活动表里——下次 Raise 可以直接复用，无需重新 Create。", False),
    ],
    scenario="夜班操作员下班前\"清空全部当前报警\"按钮——把所有遗留的报警一次性收拾干净，准备交班",
    value="一句调用替代手写 FOR 循环遍历所有 alarm 实例 + 逐个 Clear",
    alt="`ClearAllAlarms` 是本方法的简化版（不需要过滤器）；"
        "用 `GetAlarm` 拿到单个 alarm 指针后 Clear → 适合精细控制不适合批量",
    xml_scenario="HMI 上「批量清除当前所有活动报警」按钮的实现",
    xml_value="一句调用清掉所有活动 alarm，省去自建报警表遍历",
    xml_verify=(
        "需要先有几条 alarm 处于 Raised 状态。写 bClearAll := TRUE 触发后 HMI EventLogger 视图所有 Raised 应变 Cleared；"
        "若 bResetConfirmation 也为 TRUE 则 WaitForConfirmation 状态同时变 Reset"
    ),
    xml_vars=[
        ("fbLogger", "FB_TcEventLogger", None, "EventLogger 实例"),
        ("bClearAll", "BOOL", "FALSE", "上升沿触发批量清除"),
        ("bClearAllPrev", "BOOL", None, "边沿检测"),
        ("bResetConfirmation", "BOOL", "FALSE", "是否同时重置确认状态（审计场景慎用）"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "// 边沿触发：批量清除全部活动 alarm。生产环境下应在 HMI 加二次确认。\n"
        "IF bClearAll AND NOT bClearAllPrev THEN\n"
        "    hr := fbLogger.ClearAlarms(\n"
        "        nTimeStamp := 0,                       // 用当前系统时间\n"
        "        bResetConfirmation := bResetConfirmation,\n"
        "        ipFilter := 0);                        // 0 = 不过滤，清全部\n"
        "END_IF;\n"
        "bClearAllPrev := bClearAll;"
    ),
    related=["FB_TcEventLogger.ClearAllAlarms", "FB_TcEventLogger.ConfirmAlarms",
             "FB_TcEventFilter"],
)


reg("fb_tceventlogger", "ClearAllAlarms",
    summary=(
        "`FB_TcEventLogger.ClearAllAlarms()` 是 `ClearAlarms()` 的便捷版本——无过滤器参数，"
        "对所有处于 Raised 状态的 alarm 调用 Clear。\n\n"
        "适合\"全部一次清空\"场景，无需构造 `I_TcEventFilter` 实例。"
    ),
    behavior=(
        "调用本方法时 EventLogger 即对所有处于 Raised 状态的 alarm 同步执行 Clear，"
        "状态从 Raised 切换到 Cleared。`bResetConfirmation := TRUE` 时同时把"
        "处于 `WaitForConfirmation` 状态的 alarm 确认状态置为 `Reset`。"
        "`nTimeStamp = 0` 用当前系统时间记录清除时刻——这个时间在事后审计里就是\"批量清除动作\"的发生时刻。\n\n"
        "**与 ClearAlarms 的区别**：本方法少一个 ipFilter 参数，行为完全等价于 `ClearAlarms(ipFilter := 0)`。"
        "选哪个看代码可读性偏好——\"全清\"场景用 ClearAllAlarms 语义更直观；需要按规则筛选则用 ClearAlarms 加过滤器。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "全部 Raised alarm 已清除", "继续业务"),
        ("其他错误", "⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={
        "nTimeStamp": "清除事件时间戳：0 = 用当前系统时间",
        "bResetConfirmation": "TRUE = 同时把确认状态置为 Reset",
    },
    pitfalls=[
        ("`bResetConfirmation := TRUE` 绕过操作员审计——慎用。", False),
        ("\"全清\"不可撤销：清完后操作员看不到原 Raised 状态。", True),
        ("Clear 不等于 Remove——alarm 实例仍在 EventLogger 活动表里。", False),
    ],
    scenario="设备维护模式下，运维人员先确认所有故障已物理处理，再用本方法\"一键全清\"准备复产",
    value="单方法调用 vs 自己写循环遍历——少错少漏",
    alt="`ClearAlarms` 带过滤器 → 精细控制；本方法适合\"全清\"按钮",
    xml_scenario="设备维护后一键全清当前所有 Raised 报警准备复产",
    xml_value="一句调用清除全部 Raised alarm",
    xml_verify="操作前 HMI 看到若干 Raised；写 bClearAll := TRUE 后全部变 Cleared",
    xml_vars=[
        ("fbLogger", "FB_TcEventLogger", None, "EventLogger 实例"),
        ("bClearAll", "BOOL", "FALSE", "上升沿触发"),
        ("bClearAllPrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "IF bClearAll AND NOT bClearAllPrev THEN\n"
        "    hr := fbLogger.ClearAllAlarms(\n"
        "        nTimeStamp := 0,\n"
        "        bResetConfirmation := FALSE);          // 保留确认状态以便审计\n"
        "END_IF;\n"
        "bClearAllPrev := bClearAll;"
    ),
    related=["FB_TcEventLogger.ClearAlarms", "FB_TcEventLogger.ConfirmAllAlarms"],
)


reg("fb_tceventlogger", "ClearLoggedEvents",
    summary=(
        "`FB_TcEventLogger.ClearLoggedEvents()` 异步清除 EventLogger 持久化日志中的历史事件。"
        "支持通过 `I_TcClearLoggedEventsSettings`（即 `FB_TcClearLoggedEventsSettings` 实例）过滤要清除的事件子集。\n\n"
        "**返回类型是 BOOL**（不是 HRESULT！）—— TRUE 表示异步请求**已不再占用**（结束/释放），"
        "通过额外的 `bError` + `hrErrorCode` 输出端反映实际执行结果。"
    ),
    behavior=(
        "本方法是异步调用：每周期调用都返回当前请求状态。请求未完成时返回 FALSE；"
        "完成或释放时返回 TRUE。**典型调用模式**：用一个 latch 变量包裹「发起请求」逻辑，"
        "每周期重新调用直到 BOOL 返回 TRUE，再读 `bError` 判断成败。\n\n"
        "`ipClearSettings` 为 0 时清空**整个事件日志**（不可逆！）；传入 `FB_TcClearLoggedEventsSettings`"
        "可按时间范围 / 严重级别 / 事件类等条件精确删除。生产环境强烈建议先 ExportLoggedEvents 导出再清。"
    ),
    return_kind="BOOL",
    returns=[
        ("TRUE", "异步请求已结束（成功或失败）", "立刻读 bError 判断"),
        ("FALSE", "请求仍在进行中", "下一周期继续调用同方法保持轮询"),
    ],
    var_desc={
        "ipClearSettings": "可选的清除过滤器；传 0 清空整个日志",
        "bError": "TRUE = 请求执行出错",
        "hrErrorCode": "出错时的具体 HRESULT 错误码",
    },
    pitfalls=[
        ("**不可撤销操作**——清前先 ExportLoggedEvents 导出做备份。", False),
        ("`ipClearSettings := 0` 清整个日志，生产环境绝对不要直接这么调。", False),
        ("BOOL 返回值是\"请求状态\"不是\"成功/失败\"——必须额外检查 bError。", False),
        ("异步方法：每周期都要调用同一方法保持轮询，不要只调一次。", False),
    ],
    scenario="每月 1 号自动清除上月以前的事件日志，配合 ExportLoggedEvents 把要清的部分先归档到外部存储",
    value="按规则清理历史事件，控制 EventLogger 数据库大小，避免无限增长；与 ExportLoggedEvents 配合做完整归档流程",
    alt="不清理 → 长期运行后日志数据库膨胀；手动到文件系统删 → 风险高、与运行时状态不同步",
    xml_scenario="按时间范围异步清除一年前的旧事件日志",
    xml_value="可控的事件日志清理，避免数据库膨胀",
    xml_verify=(
        "登录后写 bDoClear := TRUE 触发；持续观察 bRequestDone 应在多个周期后变 TRUE；"
        "若 bError = TRUE 看 hrErrorCode 排错；EventLogger 日志视图应少掉对应时间段事件"
    ),
    xml_vars=[
        ("fbLogger", "FB_TcEventLogger", None, "EventLogger 实例"),
        ("fbClearSettings", "FB_TcClearLoggedEventsSettings", None, "清除过滤器实例（在线配置时间范围）"),
        ("bDoClear", "BOOL", "FALSE", "上升沿触发"),
        ("bRequestDone", "BOOL", None, "异步请求是否结束"),
        ("bError", "BOOL", None, "执行结果错误标志"),
        ("hrErrorCode", "HRESULT", None, "错误码"),
    ],
    xml_call=(
        "// 每周期都调用本方法以推进异步状态；返回 TRUE 表示请求结束\n"
        "IF bDoClear THEN\n"
        "    bRequestDone := fbLogger.ClearLoggedEvents(\n"
        "        ipClearSettings := fbClearSettings,\n"
        "        bError => bError,\n"
        "        hrErrorCode => hrErrorCode);\n"
        "    IF bRequestDone THEN\n"
        "        bDoClear := FALSE;                     // 流程结束，等下次触发\n"
        "    END_IF;\n"
        "END_IF;"
    ),
    related=["FB_TcClearLoggedEventsSettings", "FB_TcEventLogger.ExportLoggedEvents"],
)


reg("fb_tceventlogger", "ConfirmAlarms",
    summary=(
        "`FB_TcEventLogger.ConfirmAlarms()` 批量确认符合过滤条件的 alarm（即调用对应 alarm 的 `Confirm()`）。\n\n"
        "适用：HMI 上「确认选定报警」批量操作、或自动化逻辑按 EventClass / Severity 批量确认特定类别的故障。"
    ),
    behavior=(
        "对每个匹配的 alarm 调用 `Confirm()`：把 `WaitForConfirmation` 状态切换为 `Confirmed`。"
        "Raised/Cleared 主状态不受影响。\n\n"
        "**过滤器**：`ipFilter := 0` 时确认所有 `WaitForConfirmation` 状态的 alarm；"
        "传 `FB_TcEventFilter` 实例可按规则匹配子集。`nTimeStamp = 0` 用当前系统时间作为确认时刻。"
        "确认时刻在事后审计里就是「操作员响应时间」的关键指标——比 Raise 晚的越多代表响应越慢。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "批量确认成功", "继续业务"),
        ("其他错误", "过滤器无效 / 内部异常 ⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={
        "nTimeStamp": "确认时间戳：0 = 当前系统时间",
        "ipFilter": "过滤器；传 0 确认全部 WaitForConfirmation",
    },
    pitfalls=[
        ("批量确认绕过逐条审视——若某条故障未真正处理就被确认，事故责任不清。", True),
        ("过滤器要写对——错误的过滤器可能漏确认（看似确认实际没动）。", True),
        ("Confirm 不改变 Raised/Cleared 主状态——alarm 还在 Raised 时调 Confirm 仍生效。", False),
    ],
    scenario="HMI 上「确认选定类别报警」批量操作（例如只确认 Severity ≥ Warning 的报警，Info 类不动）",
    value="过滤器机制让批量确认精细可控",
    alt="`ConfirmAllAlarms` → 无过滤器全确认；逐个 alarm 调 Confirm → 适合精细控制不适合批量",
    xml_scenario="按过滤器批量确认 Warning 及以上级别的所有 alarm",
    xml_value="一次调用完成批量确认",
    xml_verify="先有几条 WaitForConfirmation 状态 alarm；写 bConfirmReq := TRUE，相应 alarm 变 Confirmed",
    xml_vars=[
        ("fbLogger", "FB_TcEventLogger", None, "EventLogger 实例"),
        ("fbFilter", "FB_TcEventFilter", None, "过滤器实例"),
        ("bConfirmReq", "BOOL", "FALSE", "上升沿触发"),
        ("bConfirmReqPrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "IF bConfirmReq AND NOT bConfirmReqPrev THEN\n"
        "    hr := fbLogger.ConfirmAlarms(\n"
        "        nTimeStamp := 0,\n"
        "        ipFilter := fbFilter);                 // 0 也行：fbFilter 用于按类别筛选\n"
        "END_IF;\n"
        "bConfirmReqPrev := bConfirmReq;"
    ),
    related=["FB_TcEventLogger.ConfirmAllAlarms", "FB_TcEventLogger.ClearAlarms",
             "FB_TcEventFilter"],
)


reg("fb_tceventlogger", "ConfirmAllAlarms",
    summary=(
        "`FB_TcEventLogger.ConfirmAllAlarms()` 是 `ConfirmAlarms()` 的便捷版本——无过滤器参数，"
        "对所有处于 `WaitForConfirmation` 状态的 alarm 调用 Confirm。\n\n"
        "适合\"一键确认全部\"操作。"
    ),
    behavior=(
        "调用时 EventLogger 即对所有处于 `WaitForConfirmation` 状态的 alarm 同步执行 Confirm，"
        "确认状态切换为 Confirmed。Raised/Cleared 主状态不受影响——Confirm 与主状态机正交。"
        "`nTimeStamp = 0` 用当前系统时间记录批量确认时刻，写入事件日志供事后审计。\n\n"
        "**与 ConfirmAlarms 的区别**：本方法等价于 `ConfirmAlarms(ipFilter := 0)`，无过滤参数；"
        "用本方法 vs 显式传 0 看代码可读性偏好。已 Confirmed 的 alarm 再调用本方法不会变化（幂等操作）。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "全部 WaitForConfirmation alarm 已确认", "继续业务"),
        ("其他错误", "⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={
        "nTimeStamp": "确认时间戳：0 = 用当前系统时间",
    },
    pitfalls=[
        ("\"全确认\"是审计敏感动作——HMI 端应加权限管控（管理员才能用）。", True),
        ("已 Confirmed 的 alarm 再 Confirm 不变化（幂等）。", False),
        ("批量确认时不记录\"哪些 alarm 被确认\"——审计追溯需要事后查 EventLogger 历史。", True),
    ],
    scenario="管理员下班前\"一键确认所有遗留报警\"准备交班",
    value="单次调用完成批量确认；事件日志自动记录时刻供审计",
    alt="`ConfirmAlarms` 带过滤器 → 精细控制；本方法适合\"全确认\"按钮",
    xml_scenario="管理员的「一键确认全部 WaitForConfirmation」操作",
    xml_value="一句调用完成批量确认",
    xml_verify="操作前 HMI 有若干 WaitForConfirmation；写 bConfirmAll := TRUE 后全部变 Confirmed",
    xml_vars=[
        ("fbLogger", "FB_TcEventLogger", None, "EventLogger 实例"),
        ("bConfirmAll", "BOOL", "FALSE", "上升沿触发"),
        ("bConfirmAllPrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "IF bConfirmAll AND NOT bConfirmAllPrev THEN\n"
        "    hr := fbLogger.ConfirmAllAlarms(nTimeStamp := 0);\n"
        "END_IF;\n"
        "bConfirmAllPrev := bConfirmAll;"
    ),
    related=["FB_TcEventLogger.ConfirmAlarms", "FB_TcEventLogger.ClearAllAlarms"],
)


reg("fb_tceventlogger", "ExportLoggedEvents",
    summary=(
        "`FB_TcEventLogger.ExportLoggedEvents()` 异步把 EventLogger 持久化日志中的事件导出到 CSV 文件。"
        "支持通过 `I_TcEventExportSettings`（即 `FB_TcEventCsvExportSettings` 实例）按规则筛选要导出的事件子集。\n\n"
        "**返回类型是 BOOL**——TRUE 表示异步处理完成。配合 `bError` + `hrErrorCode` 反映成败。"
    ),
    behavior=(
        "异步导出：每周期调用同一方法推进状态。请求未完成时返回 FALSE；完成时 TRUE。"
        "文件路径由 VAR_IN_OUT CONSTANT `sFileName : STRING` 传入。文件已存在会被覆盖。\n\n"
        "`ipExportSettings := 0` 时导出**全部**事件历史；传 `FB_TcEventCsvExportSettings` 实例可按"
        "时间范围 / 严重级别 / 事件类等条件筛选。导出过程不阻塞 PLC 周期——大量事件导出可能耗时数秒。\n\n"
        "**典型流程**：导出 → ClearLoggedEvents 清理旧日志 → 完成归档。"
    ),
    return_kind="BOOL",
    returns=[
        ("TRUE", "异步导出已完成", "读 bError 判断成败；可继续后续清理"),
        ("FALSE", "导出仍在进行", "下一周期继续调用同方法保持轮询"),
    ],
    var_desc={
        "sFileName": "导出 CSV 文件的完整路径（含文件名与扩展名）",
        "ipExportSettings": "导出过滤器；传 0 导出全部",
        "bError": "TRUE = 导出失败",
        "hrErrorCode": "错误码",
    },
    pitfalls=[
        ("文件路径必须 TwinCAT runtime 有写权限——典型放 `C:\\Temp\\` 或 `C:\\ProgramData\\Beckhoff\\`。", True),
        ("BOOL 返回值是\"完成状态\"不是\"成功/失败\"——必须额外检查 bError。", False),
        ("现有同名文件会被**覆盖**——批量归档时给文件名加时间戳。", True),
        ("异步方法：每周期都要调用同一方法保持轮询。", False),
    ],
    scenario="每日 23:00 自动导出当日全部事件到带日期的 CSV，配合 ClearLoggedEvents 做完整归档",
    value="一次调用 + 轮询完成大批量事件导出，无需自建数据库 SELECT",
    alt="自建 SQL Server INSERT → 阻塞 PLC 周期、网络中断风险大；"
        "通过 OPC UA Server 拉取 → 需要额外 license",
    xml_scenario="每日 23:00 触发的事件归档导出（输出文件名含当日日期）",
    xml_value="非阻塞异步导出，PLC 主流程不卡顿",
    xml_verify="登录后写 bDoExport := TRUE 触发；持续监视 bExportDone 应在几秒内变 TRUE；C:\\Temp 下出现 CSV 文件",
    xml_vars=[
        ("fbLogger", "FB_TcEventLogger", None, "EventLogger 实例"),
        ("fbExportSettings", "FB_TcEventCsvExportSettings", None, "导出过滤器实例"),
        ("sFileName", "STRING(120)", "'C:\\Temp\\events_2026-05-11.csv'", "导出文件路径"),
        ("bDoExport", "BOOL", "FALSE", "上升沿触发"),
        ("bExportDone", "BOOL", None, "完成标志"),
        ("bError", "BOOL", None, "错误标志"),
        ("hrErrorCode", "HRESULT", None, "错误码"),
    ],
    xml_call=(
        "// 每周期都调用以推进异步状态；返回 TRUE 表示导出结束\n"
        "IF bDoExport THEN\n"
        "    bExportDone := fbLogger.ExportLoggedEvents(\n"
        "        sFileName := sFileName,\n"
        "        ipExportSettings := fbExportSettings,\n"
        "        bError => bError,\n"
        "        hrErrorCode => hrErrorCode);\n"
        "    IF bExportDone THEN\n"
        "        bDoExport := FALSE;                    // 流程结束\n"
        "    END_IF;\n"
        "END_IF;"
    ),
    related=["FB_TcEventCsvExportSettings", "FB_TcEventLogger.ClearLoggedEvents"],
)


reg("fb_tceventlogger", "GetAlarm",
    summary=(
        "`FB_TcEventLogger.GetAlarm()` 通过 EventClass GUID + EventID + SourceInfo 查询已存在的 alarm 实例，"
        "拿到 `FB_TcAlarm` 引用以便对它调用 `Raise` / `Clear` / `Confirm`。\n\n"
        "适合在 listener 回调或第三方代码里只持有 GUID + ID 而没有 alarm 实例引用的场景。"
    ),
    behavior=(
        "本方法接收 `eventClass` + `nEventId` + `ipSourceInfo`，找到匹配的活动 alarm 后通过 "
        "`fbAlarm : REFERENCE TO FB_TcAlarm` 引用参数返回。\n\n"
        "**调用约定**：调用方先声明 `VAR fbAlarmRef : REFERENCE TO FB_TcAlarm;`，调用后 `fbAlarmRef` 指向"
        "EventLogger 内部 alarm 实例（不是拷贝），后续对它的方法调用都直接作用于活动 alarm。"
        "找不到时返回 `ADS_E_NOTFOUND`，引用未定义。\n\n"
        "**典型用法**：listener 收到事件后凭事件 GUID/ID 拿到 alarm 引用做自动复位、或在跨模块通信时"
        "代替手写全局变量传递 alarm 引用。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "找到 alarm，fbAlarm 引用已设置", "继续调用 fbAlarm 方法"),
        ("ADS_E_NOTFOUND", "无匹配 alarm", "fbAlarm 引用未定义，先检查 GUID/ID/SourceInfo 是否匹配"),
        ("其他错误", "⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={
        "eventClass": "事件类 GUID",
        "nEventId": "事件 ID",
        "ipSourceInfo": "源信息接口；传 0 用默认（PLC 符号路径，与 Create 时一致）",
        "fbAlarm": "REFERENCE 输出：成功时指向匹配的活动 alarm",
    },
    pitfalls=[
        ("REFERENCE 类型变量必须先声明再传入，不能直接传 VAR 指针。", True),
        ("`ipSourceInfo` 若与 Create 时传的不一致，会找不到 alarm（即便 GUID+ID 都对）。", False),
        ("找不到时返回 ADS_E_NOTFOUND 而不是 NULL——按 HRESULT 而不是引用判断。", False),
        ("拿到的引用是\"指向 EventLogger 内部实例\"——不要 __DELETE 也不要 Release。", False),
    ],
    scenario="跨模块通信：A 模块创建 alarm，B 模块只持有 GUID/ID 需要查到 alarm 引用做后续操作",
    value="解耦 alarm 创建者与使用者，无需手写全局变量传递引用",
    alt="把 alarm 实例放全局变量 → 模块间硬耦合；"
        "用本方法按 GUID 查询 → 弱耦合，事件清单是唯一接口",
    xml_scenario="按 GUID + EventID 查询已注册的 alarm 引用，调用其 Raise 方法",
    xml_value="无需直接持有 alarm 实例即可操控它",
    xml_verify=(
        "先确保有 alarm 已 Create；写 bDoGet := TRUE 触发查询；若 hr = S_OK 则 fbAlarmRef 可用，"
        "调用 Raise 应能让该 alarm 进 Raised 状态；不匹配的 GUID → hr = ADS_E_NOTFOUND"
    ),
    xml_vars=[
        ("fbLogger", "FB_TcEventLogger", None, "EventLogger 实例"),
        ("fbAlarmRef", "REFERENCE TO FB_TcAlarm", None, "查询输出"),
        ("guidEventClass", "GUID", None, "要查询的事件类 GUID"),
        ("nEventId", "UDINT", "1001", "要查询的事件 ID"),
        ("bDoGet", "BOOL", "FALSE", "上升沿触发"),
        ("bDoGetPrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "IF bDoGet AND NOT bDoGetPrev THEN\n"
        "    hr := fbLogger.GetAlarm(\n"
        "        eventClass := guidEventClass,\n"
        "        nEventId := nEventId,\n"
        "        ipSourceInfo := 0,                     // 用默认源信息匹配\n"
        "        fbAlarm := fbAlarmRef);\n"
        "    IF SUCCEEDED(hr) THEN\n"
        "        fbAlarmRef.Raise(nTimeStamp := 0);     // 拿到引用后即可操作\n"
        "    END_IF;\n"
        "END_IF;\n"
        "bDoGetPrev := bDoGet;"
    ),
    related=["FB_TcEventLogger.GetAlarmEx", "FB_TcEventLogger.IsAlarmRaised",
             "FB_TcAlarm"],
)


reg("fb_tceventlogger", "GetAlarmEx",
    summary=(
        "`FB_TcEventLogger.GetAlarmEx()` 与 `GetAlarm()` 功能相同——查询已存在的 alarm 拿到引用——"
        "区别在事件参数以 **`TcEventEntry` 结构体一次性传入**。\n\n"
        "适用：当事件定义已经是结构化数据时（如从远程 EventLogger 接收的事件、从配方加载的事件清单）"
        "免去拆字段。"
    ),
    behavior=(
        "调用过程与 `GetAlarm()` 完全一致：根据事件键匹配活动 alarm 表，找到的实例通过"
        "`fbAlarm : REFERENCE TO FB_TcAlarm` 引用参数返回，未找到时返回 `ADS_E_NOTFOUND`。"
        "区别只在事件参数来源——本方法用 `stEventEntry` 结构体一次性打包传入 GUID + EventID + Severity 三件套。\n\n"
        "**Severity 也参与匹配**：与 `GetAlarm` 不同，这里 Severity 是查询键的一部分；"
        "同 GUID+EventID 不同 Severity 会被认作不同 alarm 实例（即 Severity 升级版的同名 alarm 是新的实例）。"
        "实际工程里要注意保持 Severity 一致，否则 GetAlarmEx 找不到 alarm 但 GetAlarm 能找到。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "找到 alarm", "继续使用 fbAlarm 引用"),
        ("ADS_E_NOTFOUND", "无匹配 alarm", "检查 stEventEntry / ipSourceInfo"),
        ("其他错误", "⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={
        "stEventEntry": "事件入口结构体（GUID + EventID + Severity）",
        "ipSourceInfo": "源信息接口；传 0 用默认",
        "fbAlarm": "REFERENCE 输出：成功时指向匹配 alarm",
    },
    pitfalls=[
        ("Severity 字段也参与匹配——同 GUID+EventID 不同 Severity 算不同 alarm。", False),
        ("REFERENCE 输出变量必须先声明。", True),
        ("找不到时 fbAlarm 引用未定义，HRESULT 是唯一可靠判断。", False),
    ],
    scenario="从远程 EventLogger 接收事件后凭 TcEventEntry 查到本地对应 alarm 引用",
    value="结构体接口更适合\"事件清单已结构化\"的场景",
    alt="`GetAlarm` 分字段 → 适合已知具体 GUID/ID 的场景；本方法适合事件已经打包的场景",
    xml_scenario="凭 TcEventEntry 查询本地匹配的 alarm 引用",
    xml_value="结构体接口适合循环遍历事件清单批量查询",
    xml_verify="先 Create 一个 alarm，把同一 TcEventEntry 写入 stEventEntry 触发 GetAlarmEx → hr = S_OK；改 Severity → ADS_E_NOTFOUND",
    xml_vars=[
        ("fbLogger", "FB_TcEventLogger", None, "EventLogger 实例"),
        ("fbAlarmRef", "REFERENCE TO FB_TcAlarm", None, "查询输出"),
        ("stEventEntry", "TcEventEntry", None, "要查询的事件定义"),
        ("bDoGet", "BOOL", "FALSE", "上升沿触发"),
        ("bDoGetPrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "IF bDoGet AND NOT bDoGetPrev THEN\n"
        "    hr := fbLogger.GetAlarmEx(\n"
        "        stEventEntry := stEventEntry,\n"
        "        ipSourceInfo := 0,\n"
        "        fbAlarm := fbAlarmRef);\n"
        "    IF SUCCEEDED(hr) THEN\n"
        "        ; // 拿到引用后可调用 Raise/Clear/Confirm\n"
        "    END_IF;\n"
        "END_IF;\n"
        "bDoGetPrev := bDoGet;"
    ),
    related=["FB_TcEventLogger.GetAlarm", "FB_TcEventLogger.IsAlarmRaisedEx"],
)


reg("fb_tceventlogger", "IsAlarmRaised",
    summary=(
        "`FB_TcEventLogger.IsAlarmRaised()` 不取 alarm 引用，直接查询某事件（GUID + EventID + SourceInfo）"
        "是否处于 Raised 状态。\n\n"
        "**返回 BOOL**——TRUE 表示当前 Raised。适合\"只关心状态不操作\"的轻量查询。"
    ),
    behavior=(
        "本方法直接查询 EventLogger 全局活动 alarm 表，按 GUID + EventID + SourceInfo 三键匹配 alarm 后"
        "读取其 Raised 状态并以 BOOL 返回。找不到 alarm 返回 FALSE（不区分\"未注册过\"与\"已 Cleared\"两种情况）。\n\n"
        "**典型用法**：在工艺联锁逻辑里判断某安全报警是否还在 Raised，决定是否允许设备启动。"
        "比 `GetAlarm` 简化——不需要 REFERENCE 输出变量、不需要 SUCCEEDED 判断 HRESULT。"
        "调用次数频繁时注意性能开销——每次都走全局表查询，建议在高频循环里把结果缓存到局部 BOOL 变量。"
    ),
    return_kind="BOOL",
    returns=[
        ("TRUE", "alarm 处于 Raised 状态", "联锁逻辑拦截操作"),
        ("FALSE", "alarm 不在 Raised 状态或未找到", "继续业务"),
    ],
    var_desc={
        "eventClass": "事件类 GUID",
        "nEventId": "事件 ID",
        "ipSourceInfo": "源信息接口；传 0 匹配默认源",
    },
    pitfalls=[
        ("\"找不到\"和\"已 Cleared\"都返回 FALSE——无法区分两者。", False),
        ("`ipSourceInfo` 必须与 Create 时一致才能匹配。", False),
        ("调用次数多会有性能开销（内部查全局表）——别在高频循环里反复调。", True),
    ],
    scenario="设备启动联锁：检查所有安全报警是否都不在 Raised，是才允许启动按钮生效",
    value="一次 BOOL 查询替代手写 alarm 引用持有 + 状态访问",
    alt="`GetAlarm` + 检查状态 → 多一步；本方法直接拿 BOOL 简洁",
    xml_scenario="启动联锁：检查急停安全报警是否 Raised，若是则禁用电机启动",
    xml_value="一次查询替代手写引用持有 + 状态访问",
    xml_verify=(
        "先让某 alarm Create+Raise；写本程序的 guidEventClass+nEventId 与之匹配 → bIsRaised = TRUE；"
        "对该 alarm 调 Clear → bIsRaised 变 FALSE"
    ),
    xml_vars=[
        ("fbLogger", "FB_TcEventLogger", None, "EventLogger 实例"),
        ("guidEventClass", "GUID", None, "要查询的事件类 GUID"),
        ("nEventId", "UDINT", "9001", "急停事件 ID"),
        ("bIsRaised", "BOOL", None, "查询结果"),
        ("bMotorStartReq", "BOOL", "FALSE", "操作员启动请求"),
        ("bMotorAllowStart", "BOOL", None, "联锁后的允许启动"),
    ],
    xml_call=(
        "// 每周期查询急停报警是否 Raised\n"
        "bIsRaised := fbLogger.IsAlarmRaised(\n"
        "    eventClass := guidEventClass,\n"
        "    nEventId := nEventId,\n"
        "    ipSourceInfo := 0);\n"
        "\n"
        "// 联锁逻辑：报警 Raised 时禁止启动\n"
        "bMotorAllowStart := bMotorStartReq AND NOT bIsRaised;"
    ),
    related=["FB_TcEventLogger.IsAlarmRaisedEx", "FB_TcEventLogger.GetAlarm"],
)


reg("fb_tceventlogger", "IsAlarmRaisedEx",
    summary=(
        "`FB_TcEventLogger.IsAlarmRaisedEx()` 与 `IsAlarmRaised()` 行为相同——查询 alarm 是否 Raised——"
        "区别在事件参数以 **`TcEventEntry` 结构体一次性传入**。\n\n"
        "返回 BOOL。"
    ),
    behavior=(
        "查询过程与 `IsAlarmRaised()` 完全一致：内部按 stEventEntry 三件套（GUID + EventID + Severity）+ "
        "ipSourceInfo 匹配活动 alarm 表，返回其 Raised 状态。区别仅在事件参数来源——本方法用结构体一次性传入。\n\n"
        "**Severity 参与匹配**：与 `IsAlarmRaised` 相同，Severity 是 stEventEntry 的一部分；"
        "同 GUID+EventID 不同 Severity 算不同 alarm 实例。"
        "工程实践里要确保查询用的 stEventEntry 与 Create 时的 alarm 完全一致，否则查不到。"
        "找不到与已 Cleared 都返回 FALSE，无法区分两者。"
    ),
    return_kind="BOOL",
    returns=[
        ("TRUE", "alarm 处于 Raised 状态", "联锁逻辑拦截"),
        ("FALSE", "alarm 不在 Raised 状态或未找到", "继续业务"),
    ],
    var_desc={
        "stEventEntry": "事件入口（GUID + EventID + Severity）",
        "ipSourceInfo": "源信息接口；传 0 匹配默认源",
    },
    pitfalls=[
        ("Severity 参与匹配——别误把 Severity 配错。", False),
        ("\"找不到\"与\"已 Cleared\"都返回 FALSE。", False),
        ("高频循环里调用有开销。", True),
    ],
    scenario="结构体形式的联锁判断——事件定义来自远程或配方",
    value="结构体接口适合事件清单已经打包的场景",
    alt="`IsAlarmRaised` 分字段 → 已知 GUID/ID 时更直观；本方法适合结构体已在手的场景",
    xml_scenario="结构体形式的启动联锁判断",
    xml_value="结构体接口适合事件清单循环遍历",
    xml_verify="同 IsAlarmRaised：先让对应 alarm Raised，stEventEntry 与之匹配后 bIsRaised = TRUE",
    xml_vars=[
        ("fbLogger", "FB_TcEventLogger", None, "EventLogger 实例"),
        ("stEventEntry", "TcEventEntry", None, "要查询的事件定义"),
        ("bIsRaised", "BOOL", None, "查询结果"),
    ],
    xml_call=(
        "bIsRaised := fbLogger.IsAlarmRaisedEx(\n"
        "    stEventEntry := stEventEntry,\n"
        "    ipSourceInfo := 0);"
    ),
    related=["FB_TcEventLogger.IsAlarmRaised", "FB_TcEventLogger.GetAlarmEx"],
)


reg("fb_tceventlogger", "SendMessage",
    summary=(
        "`FB_TcEventLogger.SendMessage()` 免实例直接发一条 message 事件——无需事先 Create 一个 `FB_TcMessage` 实例。\n\n"
        "适合一次性通知场景：登录/注销日志、调试 trace、临时配方变更等不需要复用模板的事件。"
    ),
    behavior=(
        "EventLogger 内部临时构造一个 message 对象 → 写入事件日志 → 分发给监听器 → 释放。"
        "调用方不持有任何 message 实例，免去注册步骤。\n\n"
        "**参数语义**：与 `FB_TcMessage.Create()` + Send 组合等效，"
        "其中 `ipArguments` 可选——传入预先填好的 `FB_TcArguments` 接口让 EventLogger 把参数与消息一起持久化。"
        "`nTimeStamp = 0` 用当前系统时间。\n\n"
        "**调用时机**：边沿触发，不要每周期发——HMI 会被刷爆。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "消息已发送", "继续业务"),
        ("其他错误", "事件类未定义 / 内部异常 ⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={
        "eventClass": "事件类 GUID（必须事先在 EventClass 编辑器定义）",
        "nEventId": "事件 ID",
        "eSeverity": "严重级别",
        "ipSourceInfo": "源信息接口；传 0 用默认",
        "nTimeStamp": "时间戳：0 = 当前系统时间",
        "ipArguments": "参数接口；传 0 = 无参数",
    },
    pitfalls=[
        ("边沿触发不要每周期发——HMI 会被刷爆。", False),
        ("免实例 = 无法后续修改消息——SetJsonAttribute / 修改 Arguments 都得用 SendMessage2 + JSON 或 FB_TcMessage 实例。", False),
        ("EventClass + EventID 必须事先在工程里定义。", False),
        ("ipArguments 用完后调用方仍持有所有权——如果是 __NEW 创建的要记得 Release/__DELETE。", True),
    ],
    scenario="操作员登录/注销审计：每次登录瞬间发一条 message，无需持久化 message 实例",
    value="免实例 = 少声明 FB；轻量场景代码更简洁",
    alt="`FB_TcMessage` 实例 → 适合复用模板（同 GUID+ID 多次发）；"
        "本方法适合一次性通知",
    xml_scenario="操作员登录瞬间发一条审计 message",
    xml_value="无需声明 message 实例就能发事件",
    xml_verify=(
        "登录后写 bUserLogin := TRUE，HMI EventLogger 应立刻出现一条 Info 级 message；"
        "再次置位再发一条"
    ),
    xml_vars=[
        ("fbLogger", "FB_TcEventLogger", None, "EventLogger 实例"),
        ("guidEventClass", "GUID", None, "事件类 GUID"),
        ("bUserLogin", "BOOL", "FALSE", "操作员登录信号"),
        ("bUserLoginPrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "// 边沿触发：操作员登录瞬间发一条审计消息\n"
        "IF bUserLogin AND NOT bUserLoginPrev THEN\n"
        "    hr := fbLogger.SendMessage(\n"
        "        eventClass := guidEventClass,\n"
        "        nEventId := 3001,                      // \"操作员登录\" 事件 ID\n"
        "        eSeverity := TcEventSeverity.Info,\n"
        "        ipSourceInfo := 0,\n"
        "        nTimeStamp := 0,\n"
        "        ipArguments := 0);\n"
        "END_IF;\n"
        "bUserLoginPrev := bUserLogin;"
    ),
    related=["FB_TcEventLogger.SendMessage2", "FB_TcEventLogger.SendMessageEx",
             "FB_TcMessage"],
)


reg("fb_tceventlogger", "SendMessage2",
    summary=(
        "`FB_TcEventLogger.SendMessage2()` 是 `SendMessage()` 的扩展版——多一个 `sJsonAttribute` 参数"
        "用于附加 JSON 自定义属性，免去事后调 `SetJsonAttribute`。\n\n"
        "适合需要附带工艺上下文（batch id / operator name 等）的一次性通知。"
    ),
    behavior=(
        "参数 `eventClass` / `nEventId` / `eSeverity` / `ipSourceInfo` / `nTimeStamp` / `ipArguments` "
        "与 `SendMessage()` 一致；多了 VAR_IN_OUT CONSTANT `sJsonAttribute : STRING`——EventLogger 把这段 JSON 一并写入事件，"
        "随事件分发到 HMI / 数据库 / 远程客户端。\n\n"
        "**典型用法**：MES 集成审计——每次操作员动作发一条 message 同时附带 batch id + recipe + operator，"
        "免去事后再调 `SetJsonAttribute` 拼接。免实例发送场景下本方法是\"一次到位\"的首选——"
        "如果走 SendMessage 再 SetJsonAttribute 是不可能的（因为没有 message 实例可供后续修改）。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "消息已发送（含 JSON 属性）", "继续业务"),
        ("其他错误", "事件类未定义 / JSON 非法 ⚠️ PDF 未列详细码", "校验 JSON 格式 / 查 ADS Return Codes"),
    ],
    var_desc={
        "eventClass": "事件类 GUID",
        "nEventId": "事件 ID",
        "eSeverity": "严重级别",
        "ipSourceInfo": "源信息接口；传 0 用默认",
        "nTimeStamp": "时间戳：0 = 当前系统时间",
        "ipArguments": "参数接口；传 0 = 无参数",
        "sJsonAttribute": "合法 JSON 字符串（STRING(255) 起步）",
    },
    pitfalls=[
        ("JSON 必须是合法对象/数组——`'{\"k\":1}'`；裸 `'hello'` 会被丢弃。", False),
        ("STRING 默认 80 字节往往不够——声明 STRING(255)+。", True),
        ("一次性免实例发送 = 无法事后修改——JSON 必须在调用时拼好。", False),
    ],
    scenario="MES 集成审计：每次操作员动作发 message 同时附带 batch id + recipe + operator",
    value="一次调用同时完成事件发送 + JSON 上下文附加，省去两步调用",
    alt="`SendMessage` + 手写 SetJsonAttribute → 不适用免实例场景；本方法专为此场景设计",
    xml_scenario="配方切换审计带批次上下文",
    xml_value="一次调用完成事件 + JSON 附加",
    xml_verify="登录后写 bRecipeChange := TRUE，HMI EventLogger 事件详情应能看到 JSON 字段含 batch id",
    xml_vars=[
        ("fbLogger", "FB_TcEventLogger", None, "EventLogger 实例"),
        ("guidEventClass", "GUID", None, "事件类 GUID"),
        ("sBatchId", "STRING(64)", "'B-2026-0511-001'", "批次号"),
        ("sJsonAttribute", "STRING(255)", None, "拼接好的完整 JSON"),
        ("bRecipeChange", "BOOL", "FALSE", "配方切换信号"),
        ("bRecipeChangePrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "// 拼接 JSON\n"
        "sJsonAttribute := CONCAT('{\"batch\":\"', CONCAT(sBatchId, '\"}'));\n"
        "\n"
        "// 边沿触发：发送 message 同时附 JSON 上下文\n"
        "IF bRecipeChange AND NOT bRecipeChangePrev THEN\n"
        "    hr := fbLogger.SendMessage2(\n"
        "        eventClass := guidEventClass,\n"
        "        nEventId := 3002,\n"
        "        eSeverity := TcEventSeverity.Info,\n"
        "        ipSourceInfo := 0,\n"
        "        nTimeStamp := 0,\n"
        "        ipArguments := 0,\n"
        "        sJsonAttribute := sJsonAttribute);\n"
        "END_IF;\n"
        "bRecipeChangePrev := bRecipeChange;"
    ),
    related=["FB_TcEventLogger.SendMessage", "FB_TcEventLogger.SendMessageEx2"],
)


reg("fb_tceventlogger", "SendMessageEx",
    summary=(
        "`FB_TcEventLogger.SendMessageEx()` 与 `SendMessage()` 功能相同——免实例发 message——"
        "区别在事件参数以 **`TcEventEntry` 结构体一次性传入**。\n\n"
        "适用：事件定义已经是结构化数据（远程接收 / 配方加载）。"
    ),
    behavior=(
        "调用过程与 `SendMessage()` 完全一致：EventLogger 临时构造一个 message 对象 → 写入事件日志 → "
        "分发给所有监听器 → 立即释放，调用方不持有任何 message 实例。"
        "区别只在事件参数来源——本方法用 `stEventEntry` 结构体一次性传入 GUID + EventID + Severity 三件套。\n\n"
        "**参数细节**：`ipArguments` 可选附加预先填好的参数列表（用于文本占位符填充）；"
        "`nTimeStamp = 0` 用当前系统时间，非 0 时是 FILETIME 100ns 单位；"
        "`ipSourceInfo = 0` 用默认源信息（PLC 实例符号路径）。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "消息已发送", "继续业务"),
        ("其他错误", "⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={
        "stEventEntry": "事件入口（GUID + EventID + Severity）",
        "ipSourceInfo": "源信息接口；传 0 用默认",
        "nTimeStamp": "时间戳：0 = 当前系统时间",
        "ipArguments": "参数接口；传 0 = 无参数",
    },
    pitfalls=[
        ("`stEventEntry` 必须有效——GUID 全 0 / EventID = 0 会让 HMI 显示空白。", False),
        ("边沿触发不要每周期发。", False),
        ("Severity 是 stEventEntry 的一部分，注意与目标事件类配置一致。", True),
    ],
    scenario="从配方文件加载事件清单后批量按结构体发送 message",
    value="结构体接口适合循环遍历事件清单批量发送",
    alt="`SendMessage` 分字段 → 临时已知 GUID 时更直观；本方法适合事件清单已结构化",
    xml_scenario="按结构体发送一条 message",
    xml_value="结构体接口便于事件清单批量处理",
    xml_verify="登录后写 bDoSend := TRUE，HMI EventLogger 出现一条对应 message",
    xml_vars=[
        ("fbLogger", "FB_TcEventLogger", None, "EventLogger 实例"),
        ("stEventEntry", "TcEventEntry", None, "在线写入事件定义"),
        ("bDoSend", "BOOL", "FALSE", "上升沿触发"),
        ("bDoSendPrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "IF bDoSend AND NOT bDoSendPrev THEN\n"
        "    hr := fbLogger.SendMessageEx(\n"
        "        stEventEntry := stEventEntry,\n"
        "        ipSourceInfo := 0,\n"
        "        nTimeStamp := 0,\n"
        "        ipArguments := 0);\n"
        "END_IF;\n"
        "bDoSendPrev := bDoSend;"
    ),
    related=["FB_TcEventLogger.SendMessage", "FB_TcEventLogger.SendMessageEx2"],
)


reg("fb_tceventlogger", "SendMessageEx2",
    summary=(
        "`FB_TcEventLogger.SendMessageEx2()` 是 `SendMessageEx()` 的扩展版——"
        "事件参数以结构体传入，同时支持附加 JSON 自定义属性。\n\n"
        "适用：结构化事件清单 + 需要附带工艺上下文的免实例发送。"
    ),
    behavior=(
        "本方法组合了 `SendMessageEx`（结构体入口）+ `SendMessage2`（JSON 属性）两个版本的语义，"
        "是 SendMessage 系列中参数最全的版本。`stEventEntry` 三件套 + 可选 `ipSourceInfo` / `nTimeStamp` / `ipArguments` "
        "+ VAR_IN_OUT CONSTANT `sJsonAttribute : STRING` 一次调用完成完整事件发送（含元数据 + 参数 + JSON）。\n\n"
        "**典型用法**：MES 集成场景里事件清单来自外部表（关系数据库或配方文件），每条事件同时携带 "
        "batch / operator / recipe 等 JSON 上下文——本方法一次到位，免去拆分调用。命名实参写法更易读。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "消息已发送（含结构体 + JSON）", "继续业务"),
        ("其他错误", "⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={
        "stEventEntry": "事件入口（GUID + EventID + Severity）",
        "ipSourceInfo": "源信息接口；传 0 用默认",
        "nTimeStamp": "时间戳：0 = 当前系统时间",
        "ipArguments": "参数接口；传 0 = 无参数",
        "sJsonAttribute": "合法 JSON 字符串",
    },
    pitfalls=[
        ("结合了 SendMessage2 / SendMessageEx 两边的注意点——见各自条目。", False),
        ("一次调用 6+ 个参数，命名实参写法更易读。", True),
        ("JSON 必须合法、STRING 容量要够。", False),
    ],
    scenario="MES 集成的结构化事件 + JSON 上下文一次性发送",
    value="单方法调用覆盖最完整的事件发送场景",
    alt="`SendMessageEx` → 无 JSON；`SendMessage2` → 无结构体；本方法是完整组合版",
    xml_scenario="结构体 + JSON 一次性发送",
    xml_value="覆盖所有事件元数据的最完整免实例发送",
    xml_verify="登录后写 bDoSend := TRUE，HMI 事件含 JSON 字段；改 sJsonAttribute 再发可看到 JSON 内容更新",
    xml_vars=[
        ("fbLogger", "FB_TcEventLogger", None, "EventLogger 实例"),
        ("stEventEntry", "TcEventEntry", None, "事件定义"),
        ("sJsonAttribute", "STRING(255)", "'{\"batch\":\"B-001\"}'", "合法 JSON"),
        ("bDoSend", "BOOL", "FALSE", "上升沿触发"),
        ("bDoSendPrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "IF bDoSend AND NOT bDoSendPrev THEN\n"
        "    hr := fbLogger.SendMessageEx2(\n"
        "        stEventEntry := stEventEntry,\n"
        "        ipSourceInfo := 0,\n"
        "        nTimeStamp := 0,\n"
        "        ipArguments := 0,\n"
        "        sJsonAttribute := sJsonAttribute);\n"
        "END_IF;\n"
        "bDoSendPrev := bDoSend;"
    ),
    related=["FB_TcEventLogger.SendMessageEx", "FB_TcEventLogger.SendMessage2"],
)
