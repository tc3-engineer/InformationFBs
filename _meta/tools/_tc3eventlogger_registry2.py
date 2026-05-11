# Tc3_EventLogger registry — Part 2: FB_TcMessage + FB_TcEventBase + FB_TcEventLogger + FB_ListenerBase2
# + FB_TcSourceInfo + FB_TcArguments + FB_TcEvent + Async-text + Conversion + Filter + Remote
from __future__ import annotations

from _tc3eventlogger_registry import reg


# ============================================================
# 3.11 FB_TcMessage + methods
# ============================================================
reg("fb_tcmessage", "FB_TcMessage",
    summary=(
        "`FB_TcMessage` 是 TwinCAT 3 EventLogger 中代表**一次性消息事件**的功能块（FB），"
        "继承自 `FB_TcEventBase` 并实现 `I_TcMessage` 接口。Message 与 Alarm 的核心差别是："
        "Message **没有持续状态**——`Send()` 调用一次即生效一次，不需要 Clear/Confirm。\n\n"
        "适用于「通知」、「操作日志」、「调试 trace」类事件，例如操作员登录、配方切换、批次开始/结束、"
        "版本上线等。EventLogger 把消息写入事件日志、转发给监听器、可导出 CSV 做事后审计。\n\n"
        "用法：声明实例 → `Create()` 注册（指定 GUID/EventID/Severity）→ 业务里上升沿调 `Send()` 发出一次通知，"
        "或直接通过 `FB_TcEventLogger.SendMessage()` 免实例发送。"
    ),
    behavior=(
        "Message 是无状态事件：`Create()` 后实例处于「已就绪」，之后每次调 `Send()` 都即时执行一次。"
        "不存在 Raised/Cleared 这种持续状态机。\n\n"
        "**典型用法**：`FB_init` 里 `Create()` 一次 → 业务里上升沿调用 `Send()`（继承自 `I_TcMessage`）"
        "发出一次通知；EventLogger 把消息异步分发到 listener / 数据库 / HMI 历史窗。\n\n"
        "**与 `FB_TcEventLogger.SendMessage()` 的关系**：那是免实例的快捷调用，适合\"发一发就完\"的场景；"
        "本 FB 适合需要复用同一消息模板（同 EventClass+EventID 多次发，避免重复构造）的场景。"
    ),
    return_kind="NONE",
    pitfalls=[
        ("Message 没有 Clear/Confirm 概念，调那些方法没意义。", False),
        ("`Send()` 是边沿触发型用法：放在 IF 上升沿后调，不要每周期调（HMI 会被刷爆）。", True),
        ("EventID 配错事件类会得到\"未知事件文本\"——HMI 显示 EventID 但没文本翻译。", False),
        ("`SetJsonAttribute()` 在 TwinCAT 4026+ 支持。", False),
        ("`Create()` 一次注册即可，重复调返回 `ERROR_ALREADY_EXISTS`。", False),
    ],
    scenario="MES/SCADA 集成的操作员审计：每次操作员在 HMI 上"
             "登录 / 注销 / 切换配方 / 修改关键工艺参数都送一条消息进 EventLogger，"
             "供 MES 定时拉取做合规审计（FDA 21 CFR Part 11 / GMP 类要求）",
    value="操作审计需要结构化字段（who/when/what）+ 持久化 + 不可篡改。"
          "EventLogger 自带这些；用 `FB_TcMessage` 只需一次 `Create()` + 每次操作一次 `Send()`，"
          "不用本 FB 就得自己写 ADSLOGSTR + CSV 拼接 + 文件轮替",
    alt="`ADSLOGSTR` → 文本日志、无字段；自建数据库写入 → 阻塞 PLC 周期；"
        "OPC UA Alarm → 需要额外 license；本 FB 走 EventLogger，免费、原生、跨 HMI 厂商",
    xml_scenario="配方切换审计：每次工艺工程师改配方都送一条结构化消息进 EventLogger",
    xml_value="一句 Send() 替代手写 ADSLOGSTR + CSV 拼接 + 时间戳格式化，且自动进 EventLogger 审计窗",
    xml_verify=(
        "登录后写 bRecipeChanged := TRUE，HMI EventLogger 视图应立刻出现一条 Message 行（带时间戳/严重级别/来源 FB）；"
        "再次置位还会再发一条；下沿不发"
    ),
    xml_vars=[
        ("fbMessage", "FB_TcMessage", None, "配方切换消息实例"),
        ("bCreated", "BOOL", None, "Create() 仅在第一次扫描调用"),
        ("bRecipeChanged", "BOOL", "FALSE", "上层在配方切换瞬间置 TRUE"),
        ("bRecipeChangedPrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "返回值监视"),
        ("guidEventClass", "GUID", None, "实际事件类 GUID"),
    ],
    xml_call=(
        "// 一次性注册\n"
        "IF NOT bCreated THEN\n"
        "    hr := fbMessage.Create(\n"
        "        eventClass := guidEventClass,\n"
        "        nEventId := 2001,                  // \"配方切换\" 事件 ID\n"
        "        eSeverity := TcEventSeverity.Info,\n"
        "        ipSourceInfo := 0);\n"
        "    bCreated := SUCCEEDED(hr);\n"
        "END_IF;\n"
        "\n"
        "// 上升沿触发 Send（继承自 I_TcMessage）\n"
        "IF bRecipeChanged AND NOT bRecipeChangedPrev THEN\n"
        "    fbMessage.Send(nTimeStamp := 0);       // 0 = 用当前系统时间\n"
        "END_IF;\n"
        "bRecipeChangedPrev := bRecipeChanged;"
    ),
    related=["FB_TcAlarm", "FB_TcEventBase", "FB_TcEventLogger.SendMessage"],
)


reg("fb_tcmessage", "Create",
    summary=(
        "`FB_TcMessage.Create()` 把 message 实例注册到 EventLogger，绑定到指定事件类（GUID）+ 事件 ID + 严重级别。"
        "注册成功后这个实例就能在后续被 `Send()` 触发。\n\n"
        "与 `FB_TcAlarm.Create()` 的差别：本方法**没有 `bWithConfirmation` 参数**——message 没有确认状态。"
        "其他参数（eventClass / nEventId / eSeverity / ipSourceInfo）含义完全一致。"
    ),
    behavior=(
        "一次性注册：调用时 EventLogger 内部建立 message 槽位、写入事件日志、把 `FB_TcMessage` 加入活动消息表。"
        "**必须只调一次**——用 `bCreated : BOOL` latch 包裹。重复调返回 `ERROR_ALREADY_EXISTS`。\n\n"
        "`ipSourceInfo` 默认 `0`：用 PLC 实例符号路径作为源信息。多 PLC 共用一个 EventLogger 时传入预先构造的"
        "`FB_TcSourceInfo` 接口指针，让 message 关联到具体设备/工位。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "message 已成功注册", "继续后续 Send()"),
        ("ERROR_ALREADY_EXISTS", "同 GUID+EventID 已注册", "用 bCreated latch 跳过重复调用"),
        ("其他错误", "事件类未定义 / ADS 异常 ⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={
        "eventClass": "事件类的 GUID（在 EventClass 编辑器里定义）",
        "nEventId": "事件 ID（事件类内唯一）",
        "eSeverity": "事件严重级别（Verbose/Info/Warning/Error/Critical）",
        "ipSourceInfo": "源信息接口指针；传 0 用默认源信息（PLC 符号路径）",
    },
    pitfalls=[
        ("一次性注册：必须用 `IF NOT bCreated THEN ... END_IF` 包裹。", False),
        ("事件类 GUID 必须在 XAE EventClass 编辑器里先定义，否则 HMI 显示\"未知事件\"。", False),
        ("Info / Verbose 级别的 message 在某些 HMI 视图被默认过滤，调试时确认严重级别。", True),
        ("`ipSourceInfo` 传无效指针会让 message 创建失败但 HRESULT 不明显——传 0 最稳妥。", True),
    ],
    scenario="设备上电时把所有 message 类事件（操作日志、配方切换、批次开始）一次性注册进 EventLogger",
    value="集中注册便于事件清单的版本管理；业务代码只需 Send 不关心元数据",
    alt="`SendMessage()` 免实例发送 → 临时一次性消息合适，不适合复用模板；"
        "`CreateEx()` 用 TcEventEntry 结构体 → 适合事件已结构化的场景",
    xml_scenario="MES 集成：注册「配方切换」消息事件",
    xml_value="一次 Create 拿到 message 槽位；后续 Send 直接复用，无需重新指定事件元数据",
    xml_verify="登录后单步：第一周期 hr = S_OK 且 bCreated 变 TRUE；之后周期被 latch 截住不再调",
    xml_vars=[
        ("fbMessage", "FB_TcMessage", None, "配方切换消息实例"),
        ("bCreated", "BOOL", None, "Create latch"),
        ("hr", "HRESULT", None, "返回值监视"),
        ("guidEventClass", "GUID", None, "事件类 GUID"),
    ],
    xml_call=(
        "IF NOT bCreated THEN\n"
        "    hr := fbMessage.Create(\n"
        "        eventClass := guidEventClass,\n"
        "        nEventId := 2001,                  // 配方切换事件 ID\n"
        "        eSeverity := TcEventSeverity.Info,\n"
        "        ipSourceInfo := 0);\n"
        "    bCreated := SUCCEEDED(hr);\n"
        "END_IF;"
    ),
    related=["FB_TcMessage", "FB_TcMessage.CreateEx", "FB_TcAlarm.Create"],
)


reg("fb_tcmessage", "CreateEx",
    summary=(
        "`FB_TcMessage.CreateEx()` 与 `Create()` 功能相同，区别在于事件参数以"
        "**`TcEventEntry` 结构体一次性传入**而不是分散字段。\n\n"
        "适用：从远程 EventLogger 接收事件清单后批量注册、从配方文件加载消息定义、"
        "或在多个 FB 之间传递事件定义而不想拆解字段。"
    ),
    behavior=(
        "调用过程与 `Create()` 完全一致：成功返回 `S_OK`，重复注册返回 `ERROR_ALREADY_EXISTS`。"
        "区别只在事件来源——`stEventEntry` 已经把 GUID、EventID、Severity 三件套打包在一个结构体里，"
        "EventLogger 内部拆开后走和分散字段一样的注册流程。\n\n"
        "**典型用法**：在 PLC 工程里维护一张 `aEvents : ARRAY[1..N] OF TcEventEntry` 的全局事件清单，"
        "初始化阶段用 FOR 循环遍历这张表调用 `CreateEx()` 批量注册，业务代码后续都通过下标引用事件，"
        "便于事件清单的版本控制（清单可以从配方文件或外部数据库加载，事件类型变更不动业务代码）。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "message 已成功注册", "继续后续 Send()"),
        ("ERROR_ALREADY_EXISTS", "同事件已注册", "用 latch 跳过"),
        ("其他错误", "⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={
        "stEventEntry": "事件入口结构体（含 GUID + EventID + Severity）",
        "ipSourceInfo": "源信息接口指针；传 0 用默认",
    },
    pitfalls=[
        ("`stEventEntry` 必须是有效的事件定义——内部 GUID 全 0 / EventID = 0 会导致 HMI 显示空白。", False),
        ("批量 CreateEx 时把成功标志放在数组每个元素旁，便于失败重试。", True),
        ("和 `Create()` 一样要 latch 防止重复注册。", False),
    ],
    scenario="从配方文件加载 30 个消息定义后批量注册",
    value="事件清单与代码解耦——改消息定义不用改业务代码",
    alt="`Create()` 分字段 → 当事件已是结构体时多此一举；"
        "`AdsErr_TO_TcEventEntry` → 把 ADS 错误码转 TcEventEntry 后 CreateEx，统一上报 ADS 错误",
    xml_scenario="从结构体一次性注册一个 message",
    xml_value="结构体形式更适合循环批量注册",
    xml_verify="登录后第一周期 hr = S_OK；第二次手动 bCreated := FALSE 再触发会得到 ERROR_ALREADY_EXISTS",
    xml_vars=[
        ("fbMessage", "FB_TcMessage", None, "message 实例"),
        ("bCreated", "BOOL", None, "Create latch"),
        ("hr", "HRESULT", None, "返回值监视"),
        ("stEventEntry", "TcEventEntry", None, "在线写入事件定义"),
    ],
    xml_call=(
        "IF NOT bCreated THEN\n"
        "    hr := fbMessage.CreateEx(\n"
        "        stEventEntry := stEventEntry,\n"
        "        ipSourceInfo := 0);\n"
        "    bCreated := SUCCEEDED(hr);\n"
        "END_IF;"
    ),
    related=["FB_TcMessage.Create", "AdsErr_TO_TcEventEntry"],
)


reg("fb_tcmessage", "SetJsonAttribute",
    summary=(
        "`FB_TcMessage.SetJsonAttribute()` 给 message 实例附加一段 JSON 自定义属性，"
        "在事件分发到 HMI / 数据库 / 远程客户端时与标准字段一起传递。\n\n"
        "用法与 `FB_TcAlarm.SetJsonAttribute()` 完全相同——单 STRING 参数，整段 JSON 一次性传入。"
        "适用：给消息附加批次号 / 操作员 / 配方版本等结构化上下文。"
    ),
    behavior=(
        "方法签名只有一个 `VAR_IN_OUT CONSTANT sJsonAttribute : STRING`。EventLogger 把整段 JSON 存入"
        "message 的扩展属性表，下一次 `Send()` 时随事件一起广播给所有 listener 与持久化存储。"
        "重复调用本方法会**覆盖**上一次的 JSON 内容，不会做合并。\n\n"
        "**调用时机**：在 `Send()` 之前调用，确保事件分发时 JSON 已附上。字符串必须是合法 JSON 对象或数组，"
        "否则 EventLogger 端解析失败、HMI 看不到自定义字段。VAR_IN_OUT CONSTANT 形式意味着 PLC 不复制字符串"
        "（节省栈空间），方法内部承诺不修改它——调用方仍可以正常使用同一变量。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "JSON 属性已成功写入", "继续业务"),
        ("其他错误", "⚠️ PDF 未列详细码", "校验 JSON 格式 / 查 ADS Return Codes"),
    ],
    var_desc={
        "sJsonAttribute": "合法 JSON 字符串（建议 STRING(255) 或更长）",
    },
    pitfalls=[
        ("传入必须是**合法 JSON 整体**——`'{\"a\":1}'` 行；裸 `'hello'` 不合法。", False),
        ("STRING 默认 80 字节往往不够，声明 `STRING(255)` 或更长。", True),
        ("调用会覆盖上次内容——要追加键得自己拼接完整 JSON。", True),
        ("HMI 端要主动消费 JSON，默认只显示标准字段。", True),
    ],
    scenario="给配方切换 message 附加 batch id + operator name 用于 MES 审计追溯",
    value="工艺上下文直接挂在 message 上，省掉 MES 端做表关联",
    alt="把字段塞进 `FB_TcArguments` → 适合标准类型不适合复杂 JSON；"
        "走外部数据库 INSERT → 阻塞 PLC 周期",
    xml_scenario="配方切换消息附加批次追溯 JSON",
    xml_value="一句调用绑定上下文到 message",
    xml_verify="登录后写 bSetAttr := TRUE，HMI 事件详情应能看到 JSON 字段",
    xml_vars=[
        ("fbMessage", "FB_TcMessage", None, "message 实例（已 Create）"),
        ("bSetAttr", "BOOL", "FALSE", "上升沿触发"),
        ("bSetAttrPrev", "BOOL", None, "边沿检测"),
        ("sBatchId", "STRING(64)", "'B-2026-0511-001'", "批次号"),
        ("sJsonAttribute", "STRING(255)", None, "拼接好的完整 JSON"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "sJsonAttribute := CONCAT('{\"batch\":\"', CONCAT(sBatchId, '\"}'));\n"
        "\n"
        "IF bSetAttr AND NOT bSetAttrPrev THEN\n"
        "    hr := fbMessage.SetJsonAttribute(sJsonAttribute := sJsonAttribute);\n"
        "END_IF;\n"
        "bSetAttrPrev := bSetAttr;"
    ),
    related=["FB_TcMessage.Create", "FB_TcAlarm.SetJsonAttribute",
             "FB_TcEventBase.GetJsonAttribute"],
)


# ============================================================
# 3.9 FB_TcEventBase + methods + properties
# ============================================================
reg("fb_tceventbase", "FB_TcEventBase",
    summary=(
        "`FB_TcEventBase` 是 TwinCAT 3 EventLogger 体系的**事件基类**（base class），"
        "为 `FB_TcAlarm` / `FB_TcMessage` 提供共有的方法与属性："
        "事件等值比较（`EqualsTo*`）、JSON 属性访问、引用释放、"
        "异步取事件文本（`RequestEventText` / `RequestEventClassName`）。\n\n"
        "实际工程里**很少直接实例化**，而是声明 `FB_TcAlarm` / `FB_TcMessage` 后通过继承用上 base 的方法。"
        "唯一例外：`I_TcEvent` / `I_TcEventBase` 接口持有时，运行时可以拿到一个 base 视图。"
    ),
    behavior=(
        "FB_TcEventBase 不直接维护状态，状态机在子类（Alarm 的三态、Message 的一次性 send）里实现。"
        "本基类只提供工具方法：EqualsTo 系列做事件等值比较（粒度从粗到细：EqualsToEventClass / "
        "EqualsToEventEntry / EqualsToEventEntryEx / EqualsTo）；RequestEventText 与 "
        "RequestEventClassName 异步取本地化文本，返回 `FB_AsyncStrResult` 句柄供轮询；"
        "GetJsonAttribute 读取 SetJsonAttribute 写入的扩展属性；Release 释放动态分配（NEW）"
        "出来的事件实例；属性 ipArguments 与 ipSourceInfo 分别访问参数列表与源信息子对象。\n\n"
        "**继承方式**：业务代码声明 `FB_TcAlarm` 或 `FB_TcMessage` 实例，自动具备本基类的所有方法。"
        "持有 `I_TcEvent` / `I_TcEventBase` 接口时也能拿到基类视图调用通用 API，便于写"
        "「不区分 alarm 还是 message 的统一处理代码」（例如 listener 回调里一段代码处理所有事件）。"
    ),
    return_kind="NONE",
    pitfalls=[
        ("不要直接 `VAR fb : FB_TcEventBase;` 然后调 `Create()`——base 没有 Create。声明 `FB_TcAlarm` 或 `FB_TcMessage`。", False),
        ("`EqualsTo*` 系列方法名相近，混用容易得到不同语义：粒度最粗 EqualsToEventClass → 中 EqualsToEventEntry → 最细 EqualsTo（含 Arguments）。", True),
        ("`Release()` 只在动态 NEW 时调；静态 VAR 实例调了会让 EventLogger 槽位提前回收。", False),
        ("`RequestEventText` 不是同步——拿到 FB_AsyncStrResult 后必须轮询 IsCompleted() 才能读结果。", False),
    ],
    scenario="把已经持有的 `I_TcEvent` 接口转为 `FB_TcEventBase` 视图后调用通用方法（如比较两个事件、读 JSON）",
    value="所有事件类型共享一套\"事件元数据访问\"API，业务代码不需要区分 alarm vs message",
    alt="为每个子类各写一套元数据 API → 重复劳动 + 不一致 bug",
    xml_scenario="演示如何通过基类接口比较两个事件是否相同",
    xml_value="一份代码同时支持 alarm 和 message 的比较，无需类型分支",
    xml_verify="无法直接独立运行——本例需在已有事件实例的工程里搭配 FB_TcAlarm / FB_TcMessage 才能演示效果",
    xml_vars=[
        ("fbAlarm1", "FB_TcAlarm", None, "事件 1（举例：用 FB_TcAlarm 持有）"),
        ("fbAlarm2", "FB_TcAlarm", None, "事件 2"),
        ("ipBase1", "I_TcEvent", None, "通过接口拿到 base 视图"),
        ("ipBase2", "I_TcEvent", None, "通过接口拿到 base 视图"),
        ("bEqual", "BOOL", None, "比较结果"),
    ],
    xml_call=(
        "// FB_TcEventBase 是基类——业务里很少直接实例化，更常见的做法是声明子类 FB_TcAlarm / FB_TcMessage，\n"
        "// 然后通过 I_TcEvent 接口拿到 FB_TcEventBase 视图调用通用 API（EqualsToEventEntry / RequestEventText 等）。\n"
        "ipBase1 := fbAlarm1;\n"
        "ipBase2 := fbAlarm2;\n"
        "\n"
        "// 比较两事件定义是否相同（最粗粒度：仅看 EventClass + EventID + Severity）\n"
        "IF ipBase1 &lt;&gt; 0 AND ipBase2 &lt;&gt; 0 THEN\n"
        "    bEqual := ipBase1.EqualsToEventEntry(ipBase2);\n"
        "END_IF;"
    ),
    related=["FB_TcAlarm", "FB_TcMessage", "I_TcEvent"],
)


reg("fb_tceventbase", "EqualsTo",
    summary=(
        "`FB_TcEventBase.EqualsTo()` 把当前事件实例与另一个 `I_TcEvent` 实例做**完整等值比较**——"
        "包括 EventClass GUID、EventID、Severity，以及 `FB_TcArguments`（事件参数列表）的逐项比对。\n\n"
        "适用于「两个事件是否同一次具体发生」的判断，例如去重相邻的两条同名报警。"
    ),
    behavior=(
        "本方法返回 `BOOL`：TRUE 表示所有字段（包括 Arguments 列表逐项内容）完全一致；FALSE 表示任一字段不同。"
        "比较粒度从粗到细共有四个方法可选，分别对应不同业务需求：EqualsToEventClass 仅看事件类 GUID、"
        "EqualsToEventEntry 加上 EventID + Severity、EqualsToEventEntryEx 再加上 bWithConfirmation、"
        "本方法 EqualsTo 再加上 Arguments 内容，是粒度最严格的等值比较。\n\n"
        "**Arguments 比较细节**：按位逐项对比，类型与值都要相同。"
        "因此两个事件即便 EventClass、EventID、Severity 都一样，只要 Arguments 列表里有一个参数值不同（比如批次号变化）"
        "就会返回 FALSE。用本方法做\"重复报警去抖\"时要先确认业务上是否真的需要这么细的粒度。"
    ),
    return_kind="BOOL",
    returns=[
        ("TRUE", "完全相同（含 Arguments）", "可视为同一次事件"),
        ("FALSE", "至少一字段不同", "视为不同事件"),
    ],
    var_desc={
        "ipEvent": "另一个事件实例的接口指针（一般来自接收到的事件回调）",
    },
    pitfalls=[
        ("Arguments 内容对比敏感——同一报警在 batch=001 与 batch=002 之间被认为不相等。", False),
        ("`ipEvent = 0` 时方法返回 FALSE 而不是错误。", True),
        ("用 `EqualsTo` 做\"短时间重复报警去抖\" 要小心：Arguments 不同时仍会被认作不同事件。改用 `EqualsToEventEntry` 才能忽略 Arguments。", True),
    ],
    scenario="去重报警：同一秒内同一故障的 5 条重复报警里只保留第一条进数据库",
    value="一次方法调用替代手写 GUID + EventID + Args 逐字段对比",
    alt="`EqualsToEventEntry` 忽略 Arguments → 适合按定义去重；"
        "手写比较 → 代码冗长易错",
    xml_scenario="判断刚收到的 alarm 是否与上一条完全相同（含参数）以做去重",
    xml_value="一次调用替代多字段手写比较",
    xml_verify="需要两条事件实例。可以新建两个 FB_TcAlarm，分别 Create 不同 EventID 后比较 → 应为 FALSE；同 EventID + 同参数 → TRUE",
    xml_vars=[
        ("fbAlarmA", "FB_TcAlarm", None, "事件 A"),
        ("fbAlarmB", "FB_TcAlarm", None, "事件 B"),
        ("ipEvent", "I_TcEvent", None, "事件 B 的接口"),
        ("bSame", "BOOL", None, "比较结果"),
    ],
    xml_call=(
        "// 假定两个 FB_TcAlarm 已 Create()。完整比较（含 Arguments）\n"
        "ipEvent := fbAlarmB;\n"
        "IF ipEvent &lt;&gt; 0 THEN\n"
        "    bSame := fbAlarmA.EqualsTo(ipEvent := ipEvent);\n"
        "END_IF;"
    ),
    related=["FB_TcEventBase.EqualsToEventClass", "FB_TcEventBase.EqualsToEventEntry",
             "FB_TcEventBase.EqualsToEventEntryEx"],
)


reg("fb_tceventbase", "EqualsToEventClass",
    summary=(
        "`FB_TcEventBase.EqualsToEventClass()` 比较当前事件与给定 EventClass GUID 是否属于同一事件类。\n\n"
        "粒度最粗——只看事件类，不看 EventID / Severity / Arguments。适合\"是否属于报警类、消息类、调试类\"这种分类判断。"
    ),
    behavior=(
        "本方法接收 `eventClass : GUID`，返回 `BOOL`：当前实例的 EventClass GUID 与参数完全相同 → TRUE，"
        "否则 FALSE。不看 EventID、不看 Severity、不看 Arguments——是四个 EqualsTo 系列里粒度最粗的一个。\n\n"
        "**典型用法**：在 listener 回调里快速分流事件类型——比如先用本方法判断「是否安全报警类」，"
        "若是再走急停处理流程；否则继续走普通报警流程。也常用在多 PLC 互连场景里"
        "「事件是不是来自本 PLC 定义的某个事件类」的快速过滤，避免误处理其他系统的事件。"
    ),
    return_kind="BOOL",
    returns=[
        ("TRUE", "EventClass GUID 匹配", "属于该事件类"),
        ("FALSE", "不匹配", "不属于该事件类"),
    ],
    var_desc={
        "eventClass": "要比较的事件类 GUID",
    },
    pitfalls=[
        ("仅按 GUID 比较，忽略 EventID/Severity——同事件类不同 ID 仍返回 TRUE。", False),
        ("GUID 误传 16 字节零值会让所有判断都 FALSE。", True),
    ],
    scenario="listener 回调里按事件类分流（安全报警 / 工艺报警 / 调试事件分别走不同处理流程）",
    value="一次 GUID 比较替代结构体多字段 IF",
    alt="`EqualsToEventEntry` → 同时看 EventID，粒度更细；"
        "手写 GUID 比较 → 一行 vs 一行没区别但本方法语义明确",
    xml_scenario="判断当前 alarm 是否属于「安全报警」类",
    xml_value="一次调用即可分流",
    xml_verify="登录后让 fbAlarm.Create 用某 GUID，再写 guidExpected 为相同 GUID → bMatch=TRUE；改 guidExpected 任一字节 → FALSE",
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "alarm 实例"),
        ("guidExpected", "GUID", None, "要匹配的事件类 GUID"),
        ("bMatch", "BOOL", None, "比较结果"),
    ],
    xml_call=(
        "// 调用者已经持有 alarm 实例，判断它是否属于 guidExpected 这个事件类\n"
        "bMatch := fbAlarm.EqualsToEventClass(eventClass := guidExpected);"
    ),
    related=["FB_TcEventBase.EqualsTo", "FB_TcEventBase.EqualsToEventEntry"],
)


reg("fb_tceventbase", "EqualsToEventEntry",
    summary=(
        "`FB_TcEventBase.EqualsToEventEntry()` 比较当前事件与给定 `TcEventEntry` 是否对应同一事件定义。\n\n"
        "粒度中等：比较 EventClass GUID + EventID + Severity 三件套，**不**比较 Arguments。"
        "适合\"是否同一种事件\"的判断，与 Arguments 无关。"
    ),
    behavior=(
        "接收 `stEventEntry : TcEventEntry` 结构体，返回 BOOL。三件套（GUID + EventID + Severity）"
        "全相同时返回 TRUE，任一字段不同返回 FALSE。Arguments 不在比较范围内——"
        "同一事件即便参数不同也会被认作相等。\n\n"
        "**典型用法**：在 PLC 工程里维护一张已知事件清单 `aKnownEvents : ARRAY[1..N] OF TcEventEntry`，"
        "新来的事件遍历这张表用本方法快速识别属于哪种已知事件，再分流到对应的处理逻辑。"
        "比 EqualsToEventClass 粒度更细（多看 EventID + Severity），比 EqualsTo 更宽松（忽略 Arguments）。"
    ),
    return_kind="BOOL",
    returns=[
        ("TRUE", "EventClass + EventID + Severity 全匹配", "属于同一事件定义"),
        ("FALSE", "任一字段不同", "不同事件"),
    ],
    var_desc={
        "stEventEntry": "要比较的 TcEventEntry（含 GUID + EventID + Severity）",
    },
    pitfalls=[
        ("不比较 Arguments——相同事件不同参数会被认作相等。需要更严格用 `EqualsTo`。", False),
        ("Severity 字段也参与比较：同 GUID+EventID 不同 Severity 返回 FALSE。", True),
    ],
    scenario="ADS 错误集中报警：把 ADS 错误码先转 TcEventEntry，再用本方法在已知清单里查类型",
    value="一次调用替代三字段比较，且语义明确",
    alt="`EqualsToEventClass` → 粒度更粗；`EqualsTo` → 粒度更细（含 Arguments）",
    xml_scenario="判断当前 alarm 是否是清单里某个预定义事件",
    xml_value="一次调用做事件定义匹配",
    xml_verify="登录后让 stKnown 与 fbAlarm 的 Create 参数一致 → bMatch=TRUE；改 nEventId → FALSE",
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "alarm 实例"),
        ("stKnown", "TcEventEntry", None, "在线写入预期事件定义"),
        ("bMatch", "BOOL", None, "比较结果"),
    ],
    xml_call=(
        "bMatch := fbAlarm.EqualsToEventEntry(stEventEntry := stKnown);"
    ),
    related=["FB_TcEventBase.EqualsTo", "FB_TcEventBase.EqualsToEventClass",
             "FB_TcEventBase.EqualsToEventEntryEx"],
)


reg("fb_tceventbase", "EqualsToEventEntryEx",
    summary=(
        "`FB_TcEventBase.EqualsToEventEntryEx()` 比较当前事件与给定 `TcEventEntry` "
        "及其**确认要求标志**（bWithConfirmation）是否一致。\n\n"
        "粒度介于 `EqualsToEventEntry` 与 `EqualsTo` 之间——比基本三件套多比一项 `bWithConfirmation`，"
        "但不比 Arguments。适合\"事件定义 + 确认策略\"完全一致的判断。"
    ),
    behavior=(
        "接收 `stEventEntry`（含 GUID + EventID + Severity）和 `bWithConfirmation` 共四个字段。"
        "全部相同时返回 TRUE，任一字段不同返回 FALSE。Arguments 仍不在比较范围内——"
        "需要逐参数比较请用 EqualsTo。\n\n"
        "**典型用法**：在批量注册 alarm 前检查是否已存在同「事件 + 确认要求」的 alarm 以避免重复 Create；"
        "或在工程升级时对比新旧事件清单中确认策略是否变化，自动迁移 alarm 实例。"
        "比 EqualsToEventEntry 多看一个 bWithConfirmation 字段，适合需要严格区分确认策略的场景。"
    ),
    return_kind="BOOL",
    returns=[
        ("TRUE", "事件定义 + 确认要求全匹配", "属于同一条 alarm"),
        ("FALSE", "任一字段不同", "不同 alarm"),
    ],
    var_desc={
        "stEventEntry": "要比较的事件入口结构体",
        "bWithConfirmation": "要比较的确认要求",
    },
    pitfalls=[
        ("仍不比较 Arguments——若需要逐参数比较用 `EqualsTo`。", False),
        ("`bWithConfirmation` 误传错值会让本应相等的事件被判为不等。", True),
    ],
    scenario="批量注册 alarm 前的去重检查",
    value="一次比较涵盖事件定义 + 确认策略",
    alt="`EqualsToEventEntry` → 不看 bWithConfirmation；`EqualsTo` → 还看 Arguments",
    xml_scenario="判断现有 alarm 是否与新事件 + 确认要求组合相同",
    xml_value="一次比较覆盖 4 字段",
    xml_verify="改 bWithConfirmation 单一字段即可让 bMatch 翻转",
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "alarm 实例"),
        ("stKnown", "TcEventEntry", None, "预期事件定义"),
        ("bExpectConfirmation", "BOOL", "TRUE", "预期确认要求"),
        ("bMatch", "BOOL", None, "比较结果"),
    ],
    xml_call=(
        "bMatch := fbAlarm.EqualsToEventEntryEx(\n"
        "    stEventEntry := stKnown,\n"
        "    bWithConfirmation := bExpectConfirmation);"
    ),
    related=["FB_TcEventBase.EqualsToEventEntry", "FB_TcEventBase.EqualsTo"],
)


reg("fb_tceventbase", "GetJsonAttribute",
    summary=(
        "`FB_TcEventBase.GetJsonAttribute()` 读取当前事件实例上之前用 `SetJsonAttribute()` 写入的 JSON 属性。\n\n"
        "返回的字符串是完整 JSON——调用方负责自己解析。"
    ),
    behavior=(
        "方法的 `sJsonAttribute` 是 VAR_IN_OUT 形式作为**输出缓冲**：方法把当前事件实例上的 JSON 内容"
        "写入这个 STRING 变量。调用方负责声明足够长度的 STRING——默认 80 字节往往不够装下完整 JSON，"
        "建议 `STRING(255)` 或 `STRING(1024)`。\n\n"
        "**典型用法**：listener（FB_ListenerBase2）的 OnAlarmRaised / OnMessageSent 回调里"
        "用本方法读出事件附带的 JSON，解析后转交 MES / ERP 系统做结构化审计或工艺追溯。"
        "若事件没设过 JSON 属性，返回的字符串通常为空，建议读取后用 `LEN(sJson) > 0` 主动判空。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "成功取出 JSON", "解析使用"),
        ("其他错误", "无 JSON / 缓冲区太小 ⚠️ PDF 未列详细码", "确认 SetJsonAttribute 是否已写过 / 加大 STRING 容量"),
    ],
    var_desc={
        "sJsonAttribute": "输出 JSON 字符串的缓冲（调用方声明足够长度）",
    },
    pitfalls=[
        ("缓冲不够大会被截断——分析时可能 JSON 不完整。", False),
        ("没设过 JSON 属性时返回内容未定义——通常是空串，建议主动判断 `LEN(sJson) > 0`。", True),
        ("VAR_IN_OUT CONSTANT：调用方传入的字符串变量会被方法写入，不要传字符串字面量。", False),
    ],
    scenario="listener 收到 alarm 后读取附带的 batch id 上报 MES",
    value="一次调用拿到完整 JSON，无需自己反序列化标准字段以外的部分",
    alt="把上下文塞 `FB_TcArguments` → 适合数值参数不适合嵌套；"
        "走外部数据库 → 阻塞 PLC 周期",
    xml_scenario="读取 alarm 的 JSON 属性以提取 batch id",
    xml_value="一句调用拿到 JSON 字符串供后续解析",
    xml_verify="先用 SetJsonAttribute 写一个 JSON，再用本方法读取，sJsonAttribute 应等于写入值",
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "alarm 实例"),
        ("sJsonAttribute", "STRING(255)", None, "JSON 输出缓冲"),
        ("bRead", "BOOL", "FALSE", "上升沿触发读取"),
        ("bReadPrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "IF bRead AND NOT bReadPrev THEN\n"
        "    hr := fbAlarm.GetJsonAttribute(sJsonAttribute := sJsonAttribute);\n"
        "END_IF;\n"
        "bReadPrev := bRead;"
    ),
    related=["FB_TcAlarm.SetJsonAttribute", "FB_TcMessage.SetJsonAttribute"],
)


reg("fb_tceventbase", "Release",
    summary=(
        "`FB_TcEventBase.Release()` 显式释放 EventLogger 内部为当前事件实例分配的槽位。\n\n"
        "**仅用于动态分配**（`__NEW` / `__DELETE`）的事件实例。静态声明的 `VAR fbAlarm : FB_TcAlarm;` 不需要调 Release——"
        "实例销毁时 FB_exit 会自动处理。"
    ),
    behavior=(
        "调用一次释放一次。调用后这个 FB 实例上的方法都会失败——Raise / Clear / Confirm 都拿不到 EventLogger 槽位，"
        "事件无法分发也无法持久化。因此 Release 之后必须立即丢弃该实例（清指针 + __DELETE）。\n\n"
        "**典型用法**：工程支持运行时动态新增/删除报警点（例如根据当前加载的配方动态生成不同报警），"
        "每个动态报警用 `__NEW(FB_TcAlarm)` 分配，配方切换时把不再需要的报警先 Release 再 __DELETE。"
        "静态声明（`VAR fbAlarm : FB_TcAlarm;`）的实例由 FB_exit 自动处理回收，**不需要也不应该**手动 Release。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "成功释放", "之后不要再调任何方法"),
        ("其他错误", "已释放 / 无效实例 ⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    pitfalls=[
        ("静态实例（VAR 声明）**不要**调 Release——会让 EventLogger 槽位提前回收，下次扫描 Raise 失败。", False),
        ("`__DELETE` 之前必须先 Release，否则 EventLogger 内部留下悬挂引用。", False),
        ("Release 后实例视为已废弃，不要再调任何方法。", True),
    ],
    scenario="工程支持运行时新增/删除报警点（动态配方），每次删除前必须释放 EventLogger 槽位",
    value="保证 EventLogger 资源不泄露，长时间运行的 PLC 也不会因为反复 Create/Delete 耗尽槽位",
    alt="不释放直接 `__DELETE` → 槽位泄露，长时间运行后 EventLogger 拒绝新事件；"
        "全部用静态实例 → 简单但无法动态调整报警点",
    xml_scenario="动态分配的临时报警实例在用完后释放",
    xml_value="防止 EventLogger 槽位泄露",
    xml_verify="登录后写 bReleaseReq := TRUE，hr 应该是 S_OK；再次 Release 会得到错误码（槽位已释放）",
    xml_vars=[
        ("pfbAlarm", "POINTER TO FB_TcAlarm", None, "动态分配的 alarm 实例指针（在本例外申请）"),
        ("bReleaseReq", "BOOL", "FALSE", "在线置 TRUE 触发一次释放"),
        ("bReleaseReqPrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "Release 返回值监视"),
    ],
    xml_call=(
        "// 假设 pfbAlarm 已通过 __NEW(FB_TcAlarm) 分配并 Create() 完成\n"
        "IF bReleaseReq AND NOT bReleaseReqPrev AND pfbAlarm &lt;&gt; 0 THEN\n"
        "    hr := pfbAlarm^.Release();\n"
        "    // 释放后建议立即把指针清零或随后 __DELETE\n"
        "END_IF;\n"
        "bReleaseReqPrev := bReleaseReq;"
    ),
    related=["FB_TcAlarm", "FB_TcMessage"],
)


reg("fb_tceventbase", "RequestEventClassName",
    summary=(
        "`FB_TcEventBase.RequestEventClassName()` 异步请求当前事件类的**名称字符串**（如 \"包装机错误\"）。\n\n"
        "返回 `FB_AsyncStrResult` 实例（一次性句柄），调用方轮询 `IsCompleted()` 后用 `GetResult()` 取字符串。"
    ),
    behavior=(
        "EventLogger 事件类名是多语言资源。本方法启动一次异步查询，"
        "返回一个 `FB_AsyncStrResult` 实例承载结果。\n\n"
        "**典型流程**：调本方法 → 拿到 fbAsync → 每个周期 `fbAsync.IsCompleted()` 判断 → "
        "完成后 `fbAsync.GetResult(sName)` 取字符串 → 用于 HMI 显示或日志。\n\n"
        "异步是因为多语言文本资源可能存放在远端（TwinCAT HMI Server / TF6420 数据库），不能阻塞 PLC 周期。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "异步请求已发起", "轮询 fbAsync 状态"),
        ("其他错误", "事件类未定义 / 内部错误 ⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={
        "nLangId": "目标语言 ID（Windows LCID，如 1033=英文、2052=简体中文）",
        "fbAsyncResult": "用于承载异步结果的 FB_AsyncStrResult 实例",
    },
    pitfalls=[
        ("不是同步——拿到 fbAsync 后必须轮询 IsCompleted 才能读结果。", False),
        ("LangId 未在事件类配置过会得到\"无翻译\"或回退到默认语言。", True),
        ("同时发起多个请求要每个 fbAsync 独立——共享一个会被相互覆盖。", True),
    ],
    scenario="HMI 显示报警时按当前 UI 语言取本地化事件类名",
    value="多语言文本异步获取，避免阻塞 PLC 周期",
    alt="把所有翻译预先嵌入 PLC 代码 → 升级翻译要重编译；本方法走 EventLogger 资源，外部修改不需要 PLC 重编",
    xml_scenario="HMI 异步取报警的事件类名做本地化显示",
    xml_value="非阻塞获取多语言文本",
    xml_verify="登录后写 bReqClassName := TRUE，下一周期 fbAsync.IsCompleted() 应在几周期内变 TRUE，sClassName 拿到字符串",
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "alarm 实例（已 Create）"),
        ("fbAsync", "FB_AsyncStrResult", None, "异步结果句柄"),
        ("nLangId", "UDINT", "2052", "简体中文 LCID"),
        ("bReqClassName", "BOOL", "FALSE", "上升沿触发请求"),
        ("bReqClassNamePrev", "BOOL", None, "边沿检测"),
        ("sClassName", "STRING(80)", None, "拿到的事件类名"),
        ("bDone", "BOOL", None, "完成状态"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "// 边沿触发：发起一次异步请求\n"
        "IF bReqClassName AND NOT bReqClassNamePrev THEN\n"
        "    hr := fbAlarm.RequestEventClassName(\n"
        "        nLangId := nLangId,\n"
        "        fbAsyncResult := fbAsync);\n"
        "END_IF;\n"
        "bReqClassNamePrev := bReqClassName;\n"
        "\n"
        "// 每周期检查异步是否完成\n"
        "bDone := fbAsync.IsCompleted();\n"
        "IF bDone THEN\n"
        "    fbAsync.GetResult(sValue := sClassName);\n"
        "END_IF;"
    ),
    related=["FB_TcEventBase.RequestEventText", "FB_AsyncStrResult",
             "FB_RequestEventClassName"],
)


reg("fb_tceventbase", "RequestEventText",
    summary=(
        "`FB_TcEventBase.RequestEventText()` 异步请求当前事件的**事件文本**——即 HMI 上显示的"
        "\"温度过高 (95°C)\" 这种带参数的本地化文本。\n\n"
        "返回 `FB_AsyncStrResult` 实例承载结果。文本里的占位符（`{0}` / `{1}`…）"
        "由 EventLogger 用 `FB_TcArguments` 里的参数填充。"
    ),
    behavior=(
        "调用启动一次异步查询：把事件 GUID + EventID + Arguments 发到 EventLogger，"
        "EventLogger 按 LangId 查文本模板、用 Arguments 填占位符、把结果写回 `fbAsyncResult`。\n\n"
        "**典型流程**：调本方法 → 拿到 fbAsync → 轮询 `IsCompleted()` → 完成后 `GetResult()` 取字符串。\n\n"
        "这是 EventLogger 多语言能力的核心——同一事件在不同语言下显示不同文本，参数填充由 EventLogger 完成，"
        "PLC 端只管发事件 + 取文本，不需要管字符串拼接。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "异步请求已发起", "轮询 fbAsync 状态"),
        ("其他错误", "事件未定义 / 文本资源缺失 ⚠️ PDF 未列详细码", "查 ADS Return Codes / 检查 EventClass 配置"),
    ],
    var_desc={
        "nLangId": "目标语言 ID（Windows LCID）",
        "fbAsyncResult": "异步结果句柄",
    },
    pitfalls=[
        ("Arguments 必须先填好——否则文本占位符会显示原始 `{0}` 等。", False),
        ("不是同步：拿到 fbAsync 后必须 IsCompleted 才能读结果。", False),
        ("文本长度超过 STRING(80) 默认会被截断，建议 `STRING(255)`+。", True),
    ],
    scenario="HMI 收到报警事件后异步取本地化文本显示",
    value="多语言 + 参数填充全部由 EventLogger 完成，PLC 不参与字符串拼接",
    alt="PLC 端手写 CONCAT 拼字符串 → 多语言切换要重编译；走 EventLogger 多语言资源外部修改即可",
    xml_scenario="异步取报警事件的本地化文本（中文）",
    xml_value="一句调用完成多语言文本 + 参数填充",
    xml_verify="登录后写 bReqText := TRUE，几个周期后 fbAsync.IsCompleted() = TRUE，sEventText 拿到带参数的中文报警文本",
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "alarm 实例（已 Create + 已 AddArgs）"),
        ("fbAsync", "FB_AsyncStrResult", None, "异步结果句柄"),
        ("nLangId", "UDINT", "2052", "简体中文 LCID"),
        ("bReqText", "BOOL", "FALSE", "上升沿触发请求"),
        ("bReqTextPrev", "BOOL", None, "边沿检测"),
        ("sEventText", "STRING(255)", None, "拿到的事件文本"),
        ("bDone", "BOOL", None, "完成状态"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "IF bReqText AND NOT bReqTextPrev THEN\n"
        "    hr := fbAlarm.RequestEventText(\n"
        "        nLangId := nLangId,\n"
        "        fbAsyncResult := fbAsync);\n"
        "END_IF;\n"
        "bReqTextPrev := bReqText;\n"
        "\n"
        "bDone := fbAsync.IsCompleted();\n"
        "IF bDone THEN\n"
        "    fbAsync.GetResult(sValue := sEventText);\n"
        "END_IF;"
    ),
    related=["FB_TcEventBase.RequestEventClassName", "FB_AsyncStrResult",
             "FB_RequestEventText"],
)


reg("fb_tceventbase", "ipArguments",
    summary=(
        "`FB_TcEventBase.ipArguments` 是一个**只读属性**（getter），返回当前事件的 `I_TcArguments` 接口指针——"
        "用于在 `Raise()` 之前给事件附加结构化参数（int / real / bool / string …），"
        "或在收到事件后读出参数。"
    ),
    behavior=(
        "属性 getter 返回 `I_TcArguments` 接口指针。通过该接口可调用 `AddInt` / `AddReal` / `AddString` / `AddBool` "
        "等 20 多个 Add 方法把不同类型的参数依次压入参数列表；事件 Raise 时 EventLogger 把整张参数表"
        "与事件元数据一起持久化到日志，HMI 显示事件文本时按顺序把参数填进文本模板的占位符 `{0}` `{1}` `{2}`…\n\n"
        "**典型用法**：在 `Raise()` 之前调一连串 Add* 方法压入工艺数据，例如"
        "`alarm.ipArguments.AddString(sValue := 'M-01')`、"
        "`alarm.ipArguments.AddReal(fValue := 95.5)`；之后 `Raise()` 让 EventLogger 把"
        "「电机 M-01 温度 95.5°C 过高」这种结构化文本送给 HMI / 持久化 / 监听器。"
        "参数顺序与文本模板占位符严格对应——顺序错了文本会乱填。"
    ),
    return_kind="INTERFACE",
    var_desc={},
    pitfalls=[
        ("属性是 getter，每次访问可能拿到同一接口实例——不要持有过久的引用。", True),
        ("Add* 方法必须在 Raise 之前调用，否则填进去的参数对前一次 Raise 无效。", False),
        ("参数顺序与文本模板 `{0}` `{1}` 严格对应。", False),
    ],
    scenario="alarm 文本 \"电机 {0} 温度 {1}°C 过高\" 的两个占位符填值",
    value="结构化参数 + EventLogger 自动文本填充，比手写字符串拼接更安全",
    alt="`SetJsonAttribute` 写 JSON → 适合嵌套数据，本方式更适合标准类型；"
        "手写 CONCAT 字符串 → 多语言切换困难",
    xml_scenario="给即将 Raise 的 alarm 附加电机名 + 当前温度两个参数",
    xml_value="文本占位符自动填充，多语言报警一次代码完成",
    xml_verify="登录后写 bAddArgs := TRUE，触发一次 Add；再 Raise；用 RequestEventText 取回事件文本应包含参数",
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "alarm 实例（已 Create）"),
        ("ipArgs", "I_TcArguments", None, "参数接口"),
        ("sMotorName", "STRING(40)", "'M-01'", "电机名"),
        ("rTemperature", "REAL", "95.5", "当前温度"),
        ("bAddArgs", "BOOL", "FALSE", "上升沿触发"),
        ("bAddArgsPrev", "BOOL", None, "边沿检测"),
    ],
    xml_call=(
        "// Raise 之前给 alarm 添加两个参数：电机名 + 温度\n"
        "IF bAddArgs AND NOT bAddArgsPrev THEN\n"
        "    ipArgs := fbAlarm.ipArguments;     // 取 getter\n"
        "    IF ipArgs &lt;&gt; 0 THEN\n"
        "        ipArgs.AddString(sValue := sMotorName);\n"
        "        ipArgs.AddReal(fValue := rTemperature);\n"
        "    END_IF;\n"
        "END_IF;\n"
        "bAddArgsPrev := bAddArgs;"
    ),
    related=["FB_TcArguments", "FB_TcEventBase.ipSourceInfo", "FB_TcAlarm.Raise"],
)


reg("fb_tceventbase", "ipSourceInfo",
    summary=(
        "`FB_TcEventBase.ipSourceInfo` 是只读属性，返回当前事件的 `I_TcSourceInfo` 接口指针——"
        "代表事件来源信息（SourceName / SourceID / SourceGuid）。\n\n"
        "默认情况下源信息由 EventLogger 在 `Create()` 时自动填——以 PLC 实例的符号路径作为 SourceName。"
        "如果手动传入了 `FB_TcSourceInfo` 实例，本属性返回的就是那个实例。"
    ),
    behavior=(
        "属性 getter 返回 `I_TcSourceInfo` 接口指针。通过该接口可以读出 SourceName / SourceID / SourceGuid 三个字段，"
        "或调用 `ExtendName` / `Clear` / `ResetToDefault` 等方法修改源信息。EventLogger 在事件分发与持久化时"
        "把 SourceInfo 与事件一起记录，便于事后审计追溯事件的来源设备。\n\n"
        "**典型用法**：listener 收到事件后用本属性取 SourceInfo 做日志归档；或在 alarm Raise 之前调"
        "`ipSourceInfo.ExtendName(sExtName := 'motor1')` 给默认 SourceName 加后缀，"
        "让多工位共享同一份 PLC 代码时每个工位的报警都能精确定位到具体设备。"
        "默认情况下 EventLogger 用 PLC 实例的符号路径作为 SourceName，多数场景已经够用。"
    ),
    return_kind="INTERFACE",
    var_desc={},
    pitfalls=[
        ("默认 SourceInfo 是 PLC 符号路径——动态生成的 alarm 实例可能符号路径不唯一，需要主动 ExtendName。", True),
        ("修改 SourceInfo 后只对**未来的事件**生效；已 Raise 过的事件 SourceInfo 已固化。", False),
        ("多个 alarm 共享一个 FB_TcSourceInfo 时，修改它会影响所有 alarm——通常每个 alarm 用独立 SourceInfo。", True),
    ],
    scenario="多工位共享一份代码（数组实例化）时，给每个 alarm 实例指定不同工位号作为 SourceInfo",
    value="事后审计能精确定位\"哪台机器哪个工位\"出的故障，而不是只看到 PLC 符号路径",
    alt="把工位号塞 Arguments → 信息混在事件参数里不够结构化；"
        "用本属性专门承载来源信息更规范",
    xml_scenario="读取 alarm 的源信息用于日志归档",
    xml_value="一次调用拿到 SourceInfo 接口供后续读 SourceName/SourceID",
    xml_verify="登录后 monitor ipSrc，应能拿到非 0 接口；调用 ipSrc 上的 getter 能读出 SourceName 字符串",
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "alarm 实例（已 Create）"),
        ("ipSrc", "I_TcSourceInfo", None, "源信息接口"),
        ("sSourceName", "STRING(80)", None, "拿到的 SourceName"),
    ],
    xml_call=(
        "ipSrc := fbAlarm.ipSourceInfo;\n"
        "IF ipSrc &lt;&gt; 0 THEN\n"
        "    sSourceName := ipSrc.sSourceName;     // I_TcSourceInfo 的属性\n"
        "END_IF;"
    ),
    related=["FB_TcSourceInfo", "FB_TcSourceInfo.ExtendName"],
)
