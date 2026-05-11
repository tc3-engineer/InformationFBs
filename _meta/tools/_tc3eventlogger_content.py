# Per-entry hand-curated Chinese content for Tc3_EventLogger rewrite (2026-05-11).
# Keyed by (parent_dir, name). parent_dir empty for non-OO entries.
#
# Each entry provides:
#   summary  : §1 功能简述 (2-3 Chinese paragraphs)
#   var_desc : { var_name: "中文描述" } for VAR_INPUT/OUTPUT description column
#   behavior : §3 行为说明 (≥80 CJK chars, time-sequence/state-machine/lifecycle)
#   returns  : list of (code/value, meaning, advice) tuples; for HRESULT use S_OK + actual codes from PDF
#   return_kind: "HRESULT" | "BOOL" | "NONE" | "INTERFACE"  (drives §4 template)
#   pitfalls : list of (text, is_engineering) — is_engineering=True marks 工程经验补充
#   scenario : §7 业务场景 (一段中文)
#   value    : §7 价值 (一段中文)
#   alt      : §7 替代方案 (一段中文)
#   xml_scenario / xml_value / xml_verify : 例程头注释三件套
#   xml_vars : optional override for example local vars (list of (name, type, default, comment))
#   xml_call : optional override for the call body text (str)
#   related  : list of related FB/method names (str)
from __future__ import annotations

CONTENT: dict[tuple[str, str], dict] = {}


def reg(parent: str, name: str, **kw):
    CONTENT[(parent, name)] = kw


# ============================================================
# OO PARENT FBs (no own VAR_INPUT; describe purpose + method API)
# ============================================================

reg("fb_tcalarm", "FB_TcAlarm",
    summary=(
        "`FB_TcAlarm` 是 TwinCAT 3 EventLogger 中代表"
        "**报警事件实例**（alarm）的功能块（Function Block, FB），"
        "继承自 `FB_TcEventBase` 并实现 `I_TcAlarm` 接口。一条报警在生命周期里有"
        "三种状态：Raised（已触发）/ Cleared（已清除）/ Confirmed（已确认），"
        "本 FB 把这三态封装为 `Raise()` / `Clear()` / `Confirm()` 三个方法。\n\n"
        "实际用法：在某个工艺逻辑模块里声明一个 `FB_TcAlarm` 实例，调用 `Create()`"
        "把它注册进 EventLogger（指定事件类 GUID、事件 ID、严重级别、是否需要确认），"
        "之后用 `Raise()` 报警、`Clear()` 解除、`Confirm()` 确认。EventLogger 会把状态"
        "广播给所有订阅了 `FB_ListenerBase2` 的监听器（HMI、数据库、远程服务器），"
        "并写入持久化事件日志。\n\n"
        "与 `FB_TcMessage` 的区别：Message 是一次性通知（送出即结束），"
        "Alarm 是有持续状态、需操作员确认的报警，更适合用作"
        "故障停机/操作复位类事件。"
    ),
    behavior=(
        "本 FB 没有顶层 VAR_INPUT；交互全部通过方法调用：先 `Create()` 注册到"
        "EventLogger，再用 `Raise()` / `Clear()` / `Confirm()` 切换状态。\n\n"
        "**典型生命周期**：上电 → 在 `FB_init` 或第一个扫描周期里调一次 `Create()`"
        "（拿到 EventLogger 内部分配的 alarm 槽位）→ 业务逻辑里上升沿"
        "调 `Raise()` 触发报警 → 故障恢复后调 `Clear()` 解除 → 若 `bWithConfirmation = TRUE`"
        "再等操作员点 HMI 确认按钮后调 `Confirm()` 把确认状态置位。\n\n"
        "**线程模型**：状态切换是同步的（方法返回即生效），但"
        "EventLogger 把事件分发到订阅者那一段是异步的（走 RT/非 RT 跨域），"
        "HMI 收到刷新的延迟通常在毫秒级。\n\n"
        "**注意**：实例数据不在 RETAIN 区，掉电重启所有 alarm 状态归零，"
        "需要持久化故障必须自己用 RETAIN 变量保存关键标志位。"
    ),
    return_kind="NONE",
    pitfalls=[
        ("`Create()` 只调一次：重复调用同一 GUID + EventID 会返回 `ERROR_ALREADY_EXISTS`，必须用 `IF NOT bCreated THEN bCreated := SUCCEEDED(fbAlarm.Create(...)); END_IF` 之类的"一次性"包裹。", False),
        ("`bWithConfirmation = TRUE` 时只调 `Raise()` 然后 `Clear()` 不够：HMI 仍会显示 "等待确认"。必须等操作员动作后调 `Confirm()` 才能完成生命周期。", False),
        ("掉电不保持：FB 实例不是 RETAIN，CX 重启后报警全清。生产事故重现需要自己做日志持久化。", True),
        ("不要在同一 FB 实例上交错调多个 `Raise()`：状态会被覆盖。每个故障开一个独立 `FB_TcAlarm` 实例。", True),
        ("引用计数：本 FB 用 `Release()` 显式释放（继承自 `FB_TcEventBase`），手写动态 NEW 时记得释放。", False),
        ("`ipSourceInfo` 传 `0` 用默认源信息（PLC 实例符号路径）即可；大型站点（多 PLC 同 EventLogger）才需要自定义 `FB_TcSourceInfo`。", False),
    ],
    scenario=(
        "**场景**：包装机故障管理。生产线上每台包装机配 30-50 个潜在故障点"
        "（封口温度异常、纸张卡住、气压低、急停按下…），每个故障对应一个 `FB_TcAlarm` 实例。"
        "故障发生时 HMI 红灯闪烁、生产计数暂停、要求操作员处理后按确认键。"
        "全部状态由 EventLogger 持久化，事后能查"某天某点故障次数 / 平均处理时长"。"
    ),
    value=(
        "**价值**：报警的"边沿触发-持续状态-确认归档"是工业常见的三态模式，"
        "手写至少需要 3 个 BOOL + 1 个时间戳 + 1 套 HMI 联动。用本 FB 一句 `Raise()` 完成；"
        "且天然集成进 EventLogger 的统一审计/查询/导出，省掉自建报警表的活。"
    ),
    alt=(
        "**替代方案对比**：纯 BOOL 数组 + HMI 自建报警表 → 没有审计追溯；"
        "Tc2_System 旧式 `ADSLOGSTR` → 只能写文本日志，没结构化状态；"
        "第三方 SCADA 报警包 → 锁定品牌、与 PLC 状态不同步。EventLogger + `FB_TcAlarm` 是 Beckhoff 官方原生方案，"
        "TwinCAT HMI / TC3 ADS 客户端开箱即用。"
    ),
    xml_scenario="包装机封口温度异常报警（需要操作员确认才能复位的故障）",
    xml_value="一句 Raise() 完成"上升沿报警→保持显示→等待确认"三态，"
              "省去自建报警表 + HMI 联动 + 持久化的全部样板代码",
    xml_verify=(
        "登录后写 bSealTempAlarm := TRUE，HMI EventLogger 视图应立即显示 Raised；"
        "写 FALSE 后状态变 Cleared 但 ConfirmationState 仍为 WaitForConfirmation；"
        "调用 fbAlarm.Confirm() 后才完整结束生命周期"
    ),
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "包装机封口温度故障报警实例"),
        ("bCreated", "BOOL", None, "记录 Create() 是否已成功执行（只调一次）"),
        ("bSealTempAlarm", "BOOL", "FALSE", "上层逻辑给出的故障信号（在线置 TRUE 模拟）"),
        ("bConfirmReq", "BOOL", "FALSE", "操作员在 HMI 按下确认键时置 TRUE"),
        ("bSealTempAlarmPrev", "BOOL", None, "用于检测上升/下降沿"),
        ("hr", "HRESULT", None, "方法返回值监视"),
        ("guidEventClass", "GUID", None, "在线写入实际事件类 GUID（请用 EventClass 编辑器导出）"),
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
        "END_IF\n"
        "\n"
        "// 上升沿触发报警，下降沿清除\n"
        "IF bSealTempAlarm AND NOT bSealTempAlarmPrev THEN\n"
        "    fbAlarm.Raise(nTimeStamp := 0);        // 0 = 用当前系统时间\n"
        "END_IF\n"
        "IF NOT bSealTempAlarm AND bSealTempAlarmPrev THEN\n"
        "    fbAlarm.Clear(nTimeStamp := 0, bRemove := FALSE);\n"
        "END_IF\n"
        "bSealTempAlarmPrev := bSealTempAlarm;\n"
        "\n"
        "// 操作员按确认键\n"
        "IF bConfirmReq THEN\n"
        "    fbAlarm.Confirm(nTimeStamp := 0);\n"
        "    bConfirmReq := FALSE;\n"
        "END_IF"
    ),
    related=["FB_TcMessage", "FB_TcEventBase", "FB_TcEventLogger", "FB_ListenerBase2"],
)


reg("fb_tcmessage", "FB_TcMessage",
    summary=(
        "`FB_TcMessage` 是 TwinCAT 3 EventLogger 中代表**一次性消息事件**（message）的功能块，"
        "继承自 `FB_TcEventBase` 并实现 `I_TcMessage` 接口。Message 与 Alarm 的核心差别是："
        "Message **没有持续状态**——`Send()` 调用一次就生效一次，"
        "不需要 Clear/Confirm。\n\n"
        "适用于"通知"、"操作日志"、"调试 trace"类事件，"
        "例如操作员登录、配方切换、批次开始结束、版本上线等。"
        "EventLogger 会把消息加入事件日志、转发给监听器、可导出 CSV 做事后审计。\n\n"
        "用法：声明实例 → `Create()` 注册（同 alarm，给 GUID/EventID/Severity）→"
        "需要发消息时调 `Send()`（继承自 base）或直接通过 `FB_TcEventLogger.SendMessage()`"
        "免实例发送。"
    ),
    behavior=(
        "Message 是无状态事件：本 FB 在 `Create()` 后处于"已就绪"，"
        "之后每次调 `Send()` / `Release()` 都即时执行，不存在 Raised/Cleared 这种"
        "持续状态。\n\n"
        "**典型用法**：`FB_init` 里 `Create()` 一次 → 业务里上升沿调用 `Send()` 发出一次通知。"
        "EventLogger 把消息异步分发到 listener / 数据库 / HMI 历史窗。\n\n"
        "**与 `FB_TcEventLogger.SendMessage()` 的关系**：那是免实例的快捷调用，适合"发一发就完"的场景；"
        "本 FB 适合需要复用同一消息模板（同 EventClass+EventID 多次发，避免重复构造）的场景。"
    ),
    return_kind="NONE",
    pitfalls=[
        ("Message 没有 Clear/Confirm：调 `Raise()` 之类方法是无效的，编译器不会拦截但运行时也没意义。", False),
        ("`Send()` 是边沿触发型用法：放在 IF rising_edge 后调，不要每个周期都送（HMI 会被刷爆）。", True),
        ("`Create()` 的 EventID 配错事件类会得到"未知事件文本"——HMI 上显示 EventID 但没文本翻译。", False),
        ("`SetJsonAttribute()` 用来给消息附加 JSON 上下文（如 batch id、user name）——TwinCAT 4026+ 才支持。", False),
        ("发出后释放：长生命周期 FB 用完调 `Release()` 让 EventLogger 释放槽位；短期实例就用栈对象不显式释放也行。", True),
    ],
    scenario=(
        "**场景**：MES/SCADA 集成的操作员审计。每次操作员在 HMI 上"
        "登录 / 注销 / 切换配方 / 修改关键工艺参数都要发一条消息进 EventLogger，"
        "供 MES 系统定时拉取做合规审计（FDA 21 CFR Part 11 / GMP 类要求）。"
    ),
    value=(
        "**价值**：操作审计需要结构化字段（who/when/what）+ 持久化 + 不可篡改。"
        "EventLogger 自带这些；用 `FB_TcMessage` 只要一次 `Create()` + 每次操作一次 `Send()`。"
        "不用本 FB 就得自己写 ADSLOGSTR + CSV 拼接 + 文件轮替——既不结构化也不安全。"
    ),
    alt=(
        "**替代方案对比**：`ADSLOGSTR` → 文本日志，无字段；自建数据库写入 → 阻塞 PLC 周期；"
        "OPC UA Alarm → 需要额外 license；本 FB 走 EventLogger，免费、原生、跨 HMI 厂商。"
    ),
    xml_scenario="操作员配方切换审计：每次工艺工程师改配方都送一条结构化消息进 EventLogger",
    xml_value="一句 Send() 替代手写 ADSLOGSTR + CSV 拼接 + 时间戳格式化，且自动进 EventLogger 审计窗",
    xml_verify=(
        "登录后写 bRecipeChanged := TRUE，HMI EventLogger 视图应立刻出现一条 Message 行（带时间戳、严重级别、来源 FB）；再次置位还会再发一条"
    ),
    xml_vars=[
        ("fbMessage", "FB_TcMessage", None, "配方切换消息实例"),
        ("bCreated", "BOOL", None, "Create() 仅在第一次扫描调用"),
        ("bRecipeChanged", "BOOL", "FALSE", "上层在配方切换瞬间置 TRUE"),
        ("bRecipeChangedPrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "返回值监视"),
        ("guidEventClass", "GUID", None, "实际事件类 GUID（请通过 EventClass 编辑器导出）"),
    ],
    xml_call=(
        "// 一次性注册\n"
        "IF NOT bCreated THEN\n"
        "    hr := fbMessage.Create(\n"
        "        eventClass := guidEventClass,\n"
        "        nEventId := 2001,                  // "配方切换" 事件 ID\n"
        "        eSeverity := TcEventSeverity.Info,\n"
        "        ipSourceInfo := 0);\n"
        "    bCreated := SUCCEEDED(hr);\n"
        "END_IF\n"
        "\n"
        "// 上升沿触发 Send（继承自 I_TcMessage）：每次配方切换发送一条消息\n"
        "IF bRecipeChanged AND NOT bRecipeChangedPrev THEN\n"
        "    fbMessage.Send(nTimeStamp := 0);       // 0 = 用当前系统时间\n"
        "END_IF\n"
        "bRecipeChangedPrev := bRecipeChanged;"
    ),
    related=["FB_TcAlarm", "FB_TcEventBase", "FB_TcEventLogger.SendMessage"],
)


# ============================================================
# Continued in the registry file — entries are added incrementally.
# ============================================================
