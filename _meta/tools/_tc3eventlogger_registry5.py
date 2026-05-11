# Tc3_EventLogger registry — Part 5: async_text + eventry_conversion + filter + remote (20 entries)
from __future__ import annotations

from _tc3eventlogger_registry import reg


# ============================================================
# 3.1 Asynchronous text requests
# ============================================================
ASYNC_PITFALLS = [
    ("**异步**：发起 Request 后必须周期检查 `bBusy` 直到 FALSE，再读结果——不能立即用。", False),
    ("失败要检查 `bError` 与 `hrErrorCode`——`bBusy = FALSE` 不等于成功。", False),
    ("发起多次 Request 之间要 `Clear()` 清理上次结果，否则可能读到旧数据。", True),
    ("LangId 必须是 Windows LCID（如 1033=英文、2052=简体中文、1031=德文）；事件类未配置对应语言会回退默认。", False),
    ("STRING 输出缓冲必须足够长（建议 STRING(255)+），否则文本被截断。", True),
]


reg("async_text", "FB_AsyncStrResult",
    summary=(
        "`FB_AsyncStrResult` 是 TwinCAT 3 EventLogger 异步字符串请求的**结果承载 FB**——"
        "`FB_TcEventBase.RequestEventText()` / `F_GetEventText()` 等异步调用都返回它的实例引用，"
        "调用方持续轮询其状态属性 + 完成后调 `GetString()` 取最终字符串。\n\n"
        "属性：`bBusy`（处理中）、`bError`（错误标志）、`hrErrorCode`（错误码）。"
        "方法：`GetString()` 取结果字符串。"
    ),
    behavior=(
        "FB_AsyncStrResult 不直接发起请求——它由 EventLogger API 内部填充。"
        "PLC 侧业务代码只负责声明实例、传入异步调用、轮询状态、取结果。\n\n"
        "**典型流程**：调用 `FB_TcEventBase.RequestEventText(..., fbAsyncResult := myFbResult)` 发起异步请求，"
        "之后每周期检查 `myFbResult.bBusy`，FALSE 表示已完成；"
        "若 `bError = FALSE` 调 `GetString` 取结果文本；若 `bError = TRUE` 读 `hrErrorCode` 排错。\n\n"
        "**并发限制**：每个 FB_AsyncStrResult 实例同时只能承载一个请求——并发查多条文本需多个实例。"
        "复用同一实例发起新请求前建议先确认 bBusy = FALSE，否则会覆盖未完成的请求。"
    ),
    return_kind="NONE",
    pitfalls=ASYNC_PITFALLS,
    scenario="HMI 后端异步取事件文本：发起请求后等结果到达再刷新显示",
    value="非阻塞获取本地化文本，PLC 周期不卡顿；多语言资源外部修改不需要重编 PLC",
    alt="同步阻塞调用 → 会拖慢 PLC 周期；本异步模式是 Beckhoff 推荐",
    xml_scenario="异步取事件文本演示",
    xml_value="异步轮询拿到本地化文本",
    xml_verify="先 fbAlarm.RequestEventText 触发；每周期看 fbResult.bBusy 应在几周期内变 FALSE；之后 GetString 取文本",
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "alarm 实例（已 Create）"),
        ("fbResult", "FB_AsyncStrResult", None, "异步结果实例"),
        ("nLangId", "UDINT", "2052", "简体中文 LCID"),
        ("bBusy", "BOOL", None, "处理状态属性"),
        ("bError", "BOOL", None, "错误状态属性"),
        ("hrErrorCode", "HRESULT", None, "错误码"),
        ("sEventText", "STRING(255)", None, "结果文本"),
        ("bDoReq", "BOOL", "FALSE", "上升沿触发请求"),
        ("bDoReqPrev", "BOOL", None, "边沿检测"),
        ("bGot", "BOOL", None, "已取到结果"),
        ("hr", "HRESULT", None, "Request 返回值"),
    ],
    xml_call=(
        "// 边沿触发发起请求\n"
        "IF bDoReq AND NOT bDoReqPrev THEN\n"
        "    hr := fbAlarm.RequestEventText(nLangId := nLangId, fbAsyncResult := fbResult);\n"
        "    bGot := FALSE;\n"
        "END_IF;\n"
        "bDoReqPrev := bDoReq;\n"
        "\n"
        "// 每周期检查异步状态\n"
        "bBusy := fbResult.bBusy;\n"
        "bError := fbResult.bError;\n"
        "hrErrorCode := fbResult.hrErrorCode;\n"
        "\n"
        "// 完成后取一次结果\n"
        "IF NOT bBusy AND NOT bError AND NOT bGot THEN\n"
        "    fbResult.GetString(sResult := sEventText);\n"
        "    bGot := TRUE;\n"
        "END_IF;"
    ),
    related=["FB_TcEventBase.RequestEventText", "F_GetEventText",
             "FB_RequestEventText"],
)


def _async_req_fb(name: str, summary: str, scenario: str, xml_scenario: str, result_type: str = "STRING", get_method: str = "GetString"):
    """Register an async-text FB (FB_Request*)."""
    if result_type == "STRING":
        result_vars = [
            ("sResult", "STRING(255)", None, "结果文本"),
            ("bGot", "BOOL", None, "已取到结果"),
        ]
        get_call = "fbReq.GetString(sResult := sResult);\n    bGot := TRUE;"
    else:
        # FB_TcDetail / FB_TcCauseRemedy returns
        result_vars = [
            ("fbDetail", "FB_TcDetail", None, "详情子 FB"),
            ("bGot", "BOOL", None, "已取到结果"),
        ]
        get_call = "fbReq.Get(nIndex := 0, fbResult := fbDetail);\n    bGot := TRUE;"

    reg("async_text", name,
        summary=summary,
        behavior=(
            "本 FB 暴露 `Request()` 发起异步请求、`bBusy` / `bError` / `hrErrorCode` 监视状态、"
            f"`{get_method}()` / `Clear()` 取结果与清理。**典型流程**：调 `Request` 发起 → "
            "每周期查 `bBusy` 直到 FALSE → 若 `bError = FALSE` 调取结果方法 → 用完调 `Clear` 准备下次请求。\n\n"
            "**异步执行**：底层走 ADS 通讯（本地或远程），不阻塞 PLC 周期。"
            "远程查询请用 `RequestRemote()` 指定目标 AMS Net ID。"
            "并发查询需要多个 FB 实例（每个实例同时只能进行一个查询）。"
        ),
        return_kind="NONE",
        pitfalls=ASYNC_PITFALLS,
        scenario=scenario,
        value="非阻塞多语言资源访问；外部修改无需 PLC 重编译",
        alt="把翻译嵌入 PLC 代码 → 升级翻译要重编译；本异步模式更灵活",
        xml_scenario=xml_scenario,
        xml_value="异步取本地化资源",
        xml_verify=(
            "登录后写 bDoReq := TRUE 触发；几周期后 bBusy 变 FALSE 且 bError 应为 FALSE；"
            "之后取结果"
        ),
        xml_vars=[
            ("fbReq", name, None, "请求 FB 实例"),
            ("fbAlarm", "FB_TcAlarm", None, "提供 fbEventBase 参考的事件源"),
            ("nLangId", "DINT", "2052", "目标 LangId（中文）"),
            ("bDoReq", "BOOL", "FALSE", "上升沿触发"),
            ("bDoReqPrev", "BOOL", None, "边沿检测"),
            ("bBusy", "BOOL", None, "状态"),
            ("bError", "BOOL", None, "错误"),
            ("hrErrorCode", "HRESULT", None, "错误码"),
            ("hr", "HRESULT", None, "Request 返回值"),
        ] + result_vars,
        xml_call=(
            "IF bDoReq AND NOT bDoReqPrev THEN\n"
            "    fbReq.Clear();                            // 清理上次结果\n"
            "    hr := fbReq.Request(nLangId := nLangId, fbEventBase := fbAlarm);\n"
            "    bGot := FALSE;\n"
            "END_IF;\n"
            "bDoReqPrev := bDoReq;\n"
            "\n"
            "bBusy := fbReq.bBusy;\n"
            "bError := fbReq.bError;\n"
            "hrErrorCode := fbReq.hrErrorCode;\n"
            "\n"
            "IF NOT bBusy AND NOT bError AND NOT bGot THEN\n"
            f"    {get_call}\n"
            "END_IF;"
        ),
        related=["FB_AsyncStrResult", "FB_TcEventBase.RequestEventText"],
    )


_async_req_fb("FB_RequestCauseRemedy",
    summary=(
        "`FB_RequestCauseRemedy` 异步请求一个事件的「原因/补救」（Cause/Remedy）列表。\n\n"
        "每个事件可以在 EventClass 配置阶段绑定多组 cause/remedy（例如「为什么会触发该故障」+「怎么修」），"
        "本 FB 把它们异步拉取后通过 `Get(nIndex)` 按下标取出。返回的子 FB 是 `FB_TcCauseRemedy`。"
    ),
    scenario="HMI 操作员双击报警 → 后台异步取该报警的「原因/补救」列表 → 显示帮助文本",
    xml_scenario="异步取一个 alarm 的 cause/remedy 列表",
    result_type="OBJ",
    get_method="Get",
)


_async_req_fb("FB_RequestEventClassDetails",
    summary=(
        "`FB_RequestEventClassDetails` 异步请求一个 EventClass 的「详情」列表（DescriptionText / DescriptionUrl / Comment）。\n\n"
        "返回的每条详情通过 `FB_TcDetail` 子 FB 携带 name + text + comment 三字段，"
        "用于 HMI 显示帮助/链接/备注。"
    ),
    scenario="HMI 右键报警 → 显示该 EventClass 的描述/链接/备注供操作员参考",
    xml_scenario="异步取一个 EventClass 的详情列表",
    result_type="OBJ",
    get_method="Get",
)


_async_req_fb("FB_RequestEventClassName",
    summary=(
        "`FB_RequestEventClassName` 异步请求一个 EventClass 的**本地化名称**（如「包装机错误」、「Packaging Machine Error」）。\n\n"
        "用于 HMI 按当前 UI 语言显示事件类名。"
    ),
    scenario="HMI 把报警按事件类分组显示，每组标题用本 FB 取本地化类名",
    xml_scenario="异步取 EventClass 的本地化名称",
)


_async_req_fb("FB_RequestEventDetails",
    summary=(
        "`FB_RequestEventDetails` 异步请求一个事件的「详情」列表（与 FB_RequestEventClassDetails 类似但针对具体事件）。\n\n"
        "返回 `FB_TcDetail` 子 FB 列表。"
    ),
    scenario="HMI 单条报警的详情面板显示帮助文本/链接/备注",
    xml_scenario="异步取一个事件的详情列表",
    result_type="OBJ",
    get_method="Get",
)


_async_req_fb("FB_RequestEventText",
    summary=(
        "`FB_RequestEventText` 异步请求一个事件的**本地化事件文本**——HMI 上显示的"
        "「温度过高 (95°C)」这种带参数的字符串。\n\n"
        "EventLogger 按 LangId 查文本模板，用事件的 Arguments 填充占位符 `{0}` `{1}`…"
    ),
    scenario="HMI 后端订阅事件后异步取本地化文本显示",
    xml_scenario="异步取事件本地化文本",
)


_async_req_fb("FB_RequestTranslation",
    summary=(
        "`FB_RequestTranslation` 不查询事件，而是**借用 EventClass 作翻译表**——传入文本 ID 与 LangId，"
        "返回对应翻译。\n\n"
        "用法：把 EventClass 当成多语言资源容器，PLC 代码里需要本地化文本时通过本 FB 查询。"
    ),
    scenario="HMI 按钮文本/标签的多语言：把翻译存在 EventClass 里，PLC 代码异步查",
    xml_scenario="异步翻译任意文本 ID",
)


# 3.1.8 FB_TcCauseRemedy
reg("async_text", "FB_TcCauseRemedy",
    summary=(
        "`FB_TcCauseRemedy` 用于显示一个事件的 cause/remedy 项。通常配合 `FB_RequestCauseRemedy.Get()` 使用——"
        "Get 把指定下标的 cause/remedy 写入本 FB 实例，调用方再通过 `GetCause` / `GetRemedy` / `GetId` 读字段。\n\n"
        "工程上是\"承载子项\"的视图 FB，不直接发起请求。"
    ),
    behavior=(
        "本 FB 由 `FB_RequestCauseRemedy.Get(nIndex := i, fbResult := myFbCauseRemedy)` 填充——"
        "调用 Get 后内部携带第 i 项的 cause + remedy + id 三个字段。之后业务代码分别调 "
        "`GetCause(sResult)`、`GetRemedy(sResult)`、`GetId(nResult)` 把字段值读到调用方变量。\n\n"
        "**生命周期**：Get 填充 → 读字段 → 下次 Get 前可调 `Release` 清空内部缓存。"
        "实例可以反复复用，避免反复 NEW/DELETE。需要循环遍历多项 cause/remedy 时复用同一 FB_TcCauseRemedy 实例即可。"
        "字段读方法（GetCause/GetRemedy/GetId）通过 VAR_IN_OUT 输出，调用方负责声明足够长的 STRING 缓冲。"
    ),
    return_kind="NONE",
    pitfalls=[
        ("本 FB 自己不发起请求——必须配合 FB_RequestCauseRemedy 使用。", False),
        ("Get 之前的字段值不定义——不要直接读 GetCause/GetRemedy。", True),
        ("不要在多个 Request 实例之间共享同一 FB_TcCauseRemedy——可能被覆盖。", True),
    ],
    scenario="HMI 显示报警 cause/remedy 时通过 Get 拿到承载 FB，再分别读字段",
    value="字段化访问替代字符串拼接",
    alt="把 cause/remedy 拼成一段字符串返回 → 字段分不开；本 FB 提供结构化访问",
    xml_scenario="读取通过 FB_RequestCauseRemedy.Get 填充的子项字段",
    xml_value="结构化访问承载子项",
    xml_verify="先有完成的 FB_RequestCauseRemedy；调 Get 填充本 FB；再读 GetCause/GetRemedy",
    xml_vars=[
        ("fbReq", "FB_RequestCauseRemedy", None, "上游请求 FB（应已完成）"),
        ("fbCauseRemedy", "FB_TcCauseRemedy", None, "承载子项"),
        ("sCause", "STRING(255)", None, "原因文本"),
        ("sRemedy", "STRING(255)", None, "补救文本"),
        ("bGot", "BOOL", None, "已读取标志"),
    ],
    xml_call=(
        "// 从上游请求里取第 0 项填充本 FB\n"
        "fbReq.Get(nIndex := 0, fbResult := fbCauseRemedy);\n"
        "\n"
        "// 读字段（Get 系列方法的 sResult 参数是 VAR_IN_OUT STRING）\n"
        "fbCauseRemedy.GetCause(sResult := sCause);\n"
        "fbCauseRemedy.GetRemedy(sResult := sRemedy);\n"
        "bGot := LEN(sCause) &gt; 0;"
    ),
    related=["FB_RequestCauseRemedy"],
)


# 3.1.9 FB_TcDetail
reg("async_text", "FB_TcDetail",
    summary=(
        "`FB_TcDetail` 用于显示事件的「详情」项（DescriptionText / DescriptionUrl / Comment）。"
        "配合 `FB_RequestEventClassDetails.Get()` 或 `FB_RequestEventDetails.Get()` 填充。\n\n"
        "字段读方法：`GetName`（key 名）、`GetText`（值）、`GetComment`（注释）。"
    ),
    behavior=(
        "本 FB 由上游 Get 方法填充内部缓存（携带某一项详情的 name + text + comment 三字段），"
        "调用方再分别调 GetName / GetText / GetComment 读出。每次 Get 都覆盖内部缓存。"
        "调用 `Release` 显式清空内部缓存以释放资源。\n\n"
        "**典型用法**：HMI 显示某事件的帮助面板时，循环 nCount 次调用 Get 把每一项填到本 FB 实例，"
        "再分别读字段拼接到面板。每次循环内部缓存被覆盖——需要保留所有项时把字段值拷贝到外部数组。"
        "字段读方法通过 VAR_IN_OUT STRING 输出，调用方负责声明足够长的 STRING 缓冲（建议 STRING(255) 起步）。"
    ),
    return_kind="NONE",
    pitfalls=[
        ("Get 之前字段未定义，不要直接读。", True),
        ("循环 Get 时上一次的字段会被覆盖——需要保存请把字段值拷贝到外部数组。", True),
        ("STRING 默认长度 80 字节——长描述需要 STRING(255)+。", True),
    ],
    scenario="HMI 详情面板显示某事件的所有 description/url/comment 项",
    value="字段化访问替代字符串拼接，便于 HMI 单独绑定每个字段到不同控件",
    alt="把详情拼成 JSON 返回 → 需要客户端解析；本 FB 直接给字段",
    xml_scenario="循环读取事件详情列表的所有项",
    xml_value="结构化访问详情字段",
    xml_verify="先有完成的 FB_RequestEventClassDetails；调 Get 填充本 FB；读各字段",
    xml_vars=[
        ("fbReq", "FB_RequestEventClassDetails", None, "上游请求 FB"),
        ("fbDetail", "FB_TcDetail", None, "承载详情子项"),
        ("sName", "STRING(80)", None, "name 字段"),
        ("sText", "STRING(255)", None, "text 字段"),
        ("sComment", "STRING(255)", None, "comment 字段"),
    ],
    xml_call=(
        "fbReq.Get(nIndex := 0, fbResult := fbDetail);\n"
        "fbDetail.GetName(sResult := sName);\n"
        "fbDetail.GetText(sResult := sText);\n"
        "fbDetail.GetComment(sResult := sComment);"
    ),
    related=["FB_RequestEventClassDetails", "FB_RequestEventDetails"],
)


# 3.1.10 / 3.1.11 — Function helpers (return HRESULT)
reg("async_text", "F_GetEventClassName",
    summary=(
        "`F_GetEventClassName` 是函数形式的便捷调用——把「为某事件触发 EventClass 名称异步查询」"
        "封装为一个 `FUNCTION`。内部把 fbResult 配置好后返回。\n\n"
        "等价于直接调 `FB_TcEventBase.RequestEventClassName()`，区别是函数形式更适合一次性调用。"
    ),
    behavior=(
        "本函数发起异步请求并立即返回 HRESULT：S_OK 表示请求已提交（不代表已完成）。"
        "调用方持有 `fbResult : FB_AsyncStrResult` 实例，之后周期检查 `fbResult.bBusy`，"
        "完成后 `fbResult.GetString` 取本地化类名。\n\n"
        "**与 FB 形式的区别**：FB 形式（FB_RequestEventClassName）适合复用同一查询模板；"
        "本函数形式适合临时一次性调用，代码简洁。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "请求已成功提交", "周期检查 fbResult.bBusy"),
        ("其他错误", "事件未注册 / 内部异常 ⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={
        "nLangId": "目标 LangId（Windows LCID）",
        "fbEventBase": "事件实例引用（继承自 FB_TcEventBase 的具体 alarm/message）",
        "fbResult": "用于承载异步结果的实例",
    },
    pitfalls=ASYNC_PITFALLS,
    scenario="HMI 一次性查某 alarm 的 EventClass 名（用完即丢，不复用模板）",
    value="函数式接口比 FB 形式更简洁",
    alt="`FB_RequestEventClassName` FB 形式 → 适合复用；本函数适合一次性",
    xml_scenario="一次性查询事件类名",
    xml_value="函数式调用简洁",
    xml_verify="登录后写 bDoReq := TRUE 触发；几周期后 fbResult.bBusy 变 FALSE，取 sClassName",
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "事件源（已 Create）"),
        ("fbResult", "FB_AsyncStrResult", None, "异步结果"),
        ("nLangId", "DINT", "2052", "中文 LangId"),
        ("bDoReq", "BOOL", "FALSE", "上升沿触发"),
        ("bDoReqPrev", "BOOL", None, "边沿检测"),
        ("sClassName", "STRING(80)", None, "类名"),
        ("bGot", "BOOL", None, "已取标志"),
        ("hr", "HRESULT", None, "Function 返回值"),
    ],
    xml_call=(
        "IF bDoReq AND NOT bDoReqPrev THEN\n"
        "    hr := F_GetEventClassName(\n"
        "        nLangId := nLangId,\n"
        "        fbEventBase := fbAlarm,\n"
        "        fbResult := fbResult);\n"
        "    bGot := FALSE;\n"
        "END_IF;\n"
        "bDoReqPrev := bDoReq;\n"
        "\n"
        "IF NOT fbResult.bBusy AND NOT fbResult.bError AND NOT bGot THEN\n"
        "    fbResult.GetString(sResult := sClassName);\n"
        "    bGot := TRUE;\n"
        "END_IF;"
    ),
    related=["FB_TcEventBase.RequestEventClassName", "FB_RequestEventClassName",
             "FB_AsyncStrResult", "F_GetEventText"],
)


reg("async_text", "F_GetEventText",
    summary=(
        "`F_GetEventText` 是函数形式的便捷调用——把「为某事件异步查询本地化事件文本」封装为一个 `FUNCTION`。\n\n"
        "等价于 `FB_TcEventBase.RequestEventText()`，区别在函数形式更适合临时一次性调用。"
    ),
    behavior=(
        "本函数发起一次异步请求并立即返回 HRESULT：S_OK 表示请求已成功提交（不代表已完成）。"
        "调用方持有 fbResult : FB_AsyncStrResult 实例，之后周期检查 `bBusy` 直到 FALSE，"
        "再调 `GetString` 取结果。文本里的占位符 `{0}` `{1}` `{2}` 由 EventLogger 按事件 "
        "Arguments 列表里的参数自动填充。\n\n"
        "**与 FB 形式的区别**：FB 形式 `FB_RequestEventText` 适合「同一查询模板复用」（如循环遍历"
        "事件清单批量取文本）；本函数形式适合「临时一次性查询」，代码更简洁。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "请求已成功提交", "周期检查 fbResult.bBusy"),
        ("其他错误", "事件未注册 / 文本资源缺失 ⚠️ PDF 未列详细码", "查 ADS Return Codes / 检查 EventClass 配置"),
    ],
    var_desc={
        "nLangId": "目标 LangId（Windows LCID）",
        "fbEventBase": "事件实例引用（继承自 FB_TcEventBase）",
        "fbResult": "用于承载异步结果的 FB_AsyncStrResult 实例",
    },
    pitfalls=ASYNC_PITFALLS,
    scenario="HMI 一次性取某 alarm 的本地化文本",
    value="函数式接口比 FB 形式更简洁",
    alt="`FB_RequestEventText` FB 形式 → 适合复用；本函数适合一次性",
    xml_scenario="一次性查询事件本地化文本",
    xml_value="函数式调用简洁",
    xml_verify="登录后写 bDoReq := TRUE 触发；几周期后 fbResult.bBusy 变 FALSE，取 sEventText",
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "事件源（已 Create + AddArguments）"),
        ("fbResult", "FB_AsyncStrResult", None, "异步结果"),
        ("nLangId", "DINT", "2052", "中文 LangId"),
        ("bDoReq", "BOOL", "FALSE", "上升沿触发"),
        ("bDoReqPrev", "BOOL", None, "边沿检测"),
        ("sEventText", "STRING(255)", None, "事件文本"),
        ("bGot", "BOOL", None, "已取标志"),
        ("hr", "HRESULT", None, "Function 返回值"),
    ],
    xml_call=(
        "IF bDoReq AND NOT bDoReqPrev THEN\n"
        "    hr := F_GetEventText(\n"
        "        nLangId := nLangId,\n"
        "        fbEventBase := fbAlarm,\n"
        "        fbResult := fbResult);\n"
        "    bGot := FALSE;\n"
        "END_IF;\n"
        "bDoReqPrev := bDoReq;\n"
        "\n"
        "IF NOT fbResult.bBusy AND NOT fbResult.bError AND NOT bGot THEN\n"
        "    fbResult.GetString(sResult := sEventText);\n"
        "    bGot := TRUE;\n"
        "END_IF;"
    ),
    related=["FB_TcEventBase.RequestEventText", "FB_RequestEventText",
             "FB_AsyncStrResult", "F_GetEventClassName"],
)


# ============================================================
# 3.2 EventEntry conversion (4 FCs returning BOOL)
# ============================================================
def _conv_fc(name: str, summary: str, scenario: str, value: str, alt: str,
             xml_scenario: str, xml_value: str, xml_call: str, xml_vars: list,
             var_desc: dict):
    reg("eventry_conversion", name,
        summary=summary,
        behavior=(
            f"本函数同步执行转换并返回 `BOOL`：TRUE 表示转换成功（输出参数已填好），"
            "FALSE 表示转换失败（典型原因：事件类未知 / 错误码不属于 ADS facility）。\n\n"
            "**典型用法**：把 ADS 调用返回的错误码统一转换为 EventLogger 可识别的事件，"
            "再通过 `FB_TcAlarm.CreateEx()` / `SendMessageEx()` 报告——把 ADS 错误纳入 EventLogger 审计体系。"
            "或反过来：把 EventLogger 收到的事件还原成 ADS 错误码做兼容旧代码处理。"
        ),
        return_kind="BOOL",
        returns=[
            ("TRUE", "转换成功，输出参数已填好", "继续使用输出"),
            ("FALSE", "转换失败（事件类未知或错误码不在 ADS facility 范围）", "检查输入是否合法 ADS 错误"),
        ],
        var_desc=var_desc,
        pitfalls=[
            ("失败时输出参数内容**未定义**——必须先检查返回 BOOL 再读输出。", False),
            ("HRESULT 转换要求 facility 码必须是 ADS_FACILITY；其他 facility 的 HRESULT 会失败。", True),
            ("E_AdsErr 范围之外的整数转换可能失败——只支持枚举内的值。", True),
        ],
        scenario=scenario,
        value=value,
        alt=alt,
        xml_scenario=xml_scenario,
        xml_value=xml_value,
        xml_verify="登录后给输入赋已知合法值；调用本 FC 后 bOk 应为 TRUE 且输出已填",
        xml_vars=xml_vars,
        xml_call=xml_call,
        related=["AdsErr_TO_TcEventEntry", "HRESULTAdsErr_TO_TcEventEntry",
                 "TcEventEntry_TO_AdsErr", "TcEventEntry_TO_HRESULTAdsErr"],
    )


_conv_fc("AdsErr_TO_TcEventEntry",
    summary=(
        "`AdsErr_TO_TcEventEntry` 把一个 `E_AdsErr` 枚举值转换成 `TcEventEntry` 结构体，"
        "便于把 ADS 错误码纳入 EventLogger 报警体系——之后用 `FB_TcAlarm.CreateEx(stEventEntry := ...)` 报告。\n\n"
        "**返回 BOOL**：TRUE = 转换成功。"
    ),
    scenario="ADS 调用失败时把错误码自动转 TcEventEntry 后调 alarm.CreateEx() 报告",
    value="ADS 错误统一进 EventLogger，HMI 不用区分\"ADS 错\"和\"业务错\"，审计一处搞定",
    alt="手写 IF/CASE 把每个 E_AdsErr 映射成 alarm → 重复劳动；本 FC 一句解决",
    xml_scenario="ADS 错误码 → TcEventEntry 转换演示",
    xml_value="一次调用完成错误码到事件定义的转换",
    xml_vars=[
        ("eErrorId", "E_AdsErr", "E_AdsErr.ADSERR_DEVICE_INVALIDPARM", "在线写入要转换的 ADS 错误码"),
        ("stEventEntry", "TcEventEntry", None, "转换输出"),
        ("bOk", "BOOL", None, "转换成功标志"),
    ],
    xml_call=(
        "// 把 ADS 错误码转成 TcEventEntry\n"
        "bOk := AdsErr_TO_TcEventEntry(\n"
        "    eErrorId := eErrorId,\n"
        "    stEventEntry := stEventEntry);"
    ),
    var_desc={
        "eErrorId": "要转换的 ADS 错误码（E_AdsErr 枚举）",
        "stEventEntry": "REFERENCE 输出：成功时为对应事件定义",
    },
)


_conv_fc("HRESULTAdsErr_TO_TcEventEntry",
    summary=(
        "`HRESULTAdsErr_TO_TcEventEntry` 把一个 HRESULT 形式的 ADS 错误码（`E_HRESULTAdsErr` 枚举）"
        "转换成 `TcEventEntry`。\n\n"
        "**返回 BOOL**：TRUE = 转换成功（要求 HRESULT facility 是 ADS_FACILITY）。"
    ),
    scenario="EventLogger 接收到远程系统的 ADS HRESULT 错误后转 TcEventEntry 报警",
    value="把不同形式的 ADS 错误码（int / HRESULT）统一归一到 EventLogger 体系",
    alt="自己解析 HRESULT facility 拆出 ADS code → 容易出错；本 FC 一句完成",
    xml_scenario="HRESULT ADS 错误码 → TcEventEntry 转换",
    xml_value="HRESULT 形式 ADS 错的归一化",
    xml_vars=[
        ("hr", "E_HRESULTAdsErr", "E_HRESULTAdsErr.HRESULTADSERR_DEVICE_INVALIDPARM", "在线写入要转换的 HRESULT 错误码"),
        ("stEventEntry", "TcEventEntry", None, "转换输出"),
        ("bOk", "BOOL", None, "成功标志"),
    ],
    xml_call=(
        "bOk := HRESULTAdsErr_TO_TcEventEntry(\n"
        "    hr := hr,\n"
        "    stEventEntry := stEventEntry);"
    ),
    var_desc={
        "hr": "要转换的 HRESULT ADS 错误码（E_HRESULTAdsErr 枚举）",
        "stEventEntry": "REFERENCE 输出：成功时为对应事件定义",
    },
)


_conv_fc("TcEventEntry_TO_AdsErr",
    summary=(
        "`TcEventEntry_TO_AdsErr` 把一个 `TcEventEntry` 反向转换成 `E_AdsErr` 错误码。\n\n"
        "**返回 BOOL**：TRUE = 转换成功（要求事件类是 ADS 错误对应的事件类）。"
    ),
    scenario="EventLogger 收到事件后转回 E_AdsErr 喂给旧版 ADS 错误处理代码",
    value="向后兼容旧 ADS 错误码体系的桥接",
    alt="维护两套错误码表 → 不一致风险；本 FC 复用 EventLogger 的映射",
    xml_scenario="TcEventEntry → E_AdsErr 反向转换",
    xml_value="向后兼容老代码",
    xml_vars=[
        ("stEventEntry", "TcEventEntry", None, "在线写入要转换的事件定义"),
        ("eErrorId", "E_AdsErr", None, "反向输出 ADS 错误码"),
        ("bOk", "BOOL", None, "成功标志"),
    ],
    xml_call=(
        "bOk := TcEventEntry_TO_AdsErr(\n"
        "    stEventEntry := stEventEntry,\n"
        "    eErrorId := eErrorId);"
    ),
    var_desc={
        "stEventEntry": "要转换的事件定义",
        "eErrorId": "REFERENCE 输出：成功时为对应 E_AdsErr 值",
    },
)


_conv_fc("TcEventEntry_TO_HRESULTAdsErr",
    summary=(
        "`TcEventEntry_TO_HRESULTAdsErr` 把一个 `TcEventEntry` 反向转换成 HRESULT 形式的 ADS 错误码（`E_HRESULTAdsErr`）。\n\n"
        "**返回 BOOL**：TRUE = 转换成功。"
    ),
    scenario="EventLogger 收到事件后转回 HRESULT 喂给基于 HRESULT 的错误处理代码",
    value="兼容 HRESULT 错误码体系的桥接",
    alt="自己实现转换映射 → 与 EventLogger 不同步风险；本 FC 一句完成",
    xml_scenario="TcEventEntry → HRESULT ADS 错误反向转换",
    xml_value="HRESULT 体系兼容",
    xml_vars=[
        ("stEventEntry", "TcEventEntry", None, "要转换的事件定义"),
        ("hr", "E_HRESULTAdsErr", None, "反向输出 HRESULT"),
        ("bOk", "BOOL", None, "成功标志"),
    ],
    xml_call=(
        "bOk := TcEventEntry_TO_HRESULTAdsErr(\n"
        "    stEventEntry := stEventEntry,\n"
        "    hr := hr);"
    ),
    var_desc={
        "stEventEntry": "要转换的事件定义",
        "hr": "REFERENCE 输出：成功时为对应 E_HRESULTAdsErr 值",
    },
)


# ============================================================
# 3.3 Filter (3 FBs)
# ============================================================
reg("filter", "FB_TcClearLoggedEventsSettings",
    summary=(
        "`FB_TcClearLoggedEventsSettings` 用于配置 `FB_TcEventLogger.ClearLoggedEvents()` 的清除规则。\n\n"
        "通过方法 `AddFilter` 添加过滤条件（按时间 / 严重级别 / EventClass 等）、`SetLimit` 限制清除数量、"
        "`SetSorting` 设置排序后再清除前 N 条，避免误删整个日志。"
    ),
    behavior=(
        "FB 自身不发起清除——只是配置容器。**用法**：1) 实例化本 FB；"
        "2) 调用 `AddFilter` 添加要清除的事件条件（按时间范围、严重级别、EventClass 等）；"
        "3) 可选 `SetLimit(nLimit := n)` 限制最多清 n 条事件作为安全网；"
        "4) 可选 `SetSorting` 设置排序规则；"
        "5) 把本实例的接口指针传给 `FB_TcEventLogger.ClearLoggedEvents(ipClearSettings := this)` 触发清除。\n\n"
        "**最佳实践**：始终调 SetLimit 避免误清整个日志；生产环境清除前先用 `ExportLoggedEvents` 归档备份。"
        "Clear 方法可以清空当前配置，便于复用同一 FB 实例配置不同规则。"
    ),
    return_kind="NONE",
    pitfalls=[
        ("不设 SetLimit 又传给 ClearLoggedEvents 可能清掉超出预期的事件——务必设上限。", True),
        ("Filter 条件错配会清错事件——上生产前在测试机上验证。", True),
        ("本 FB 配置后再修改对正在进行的 ClearLoggedEvents 无效——重新发起。", True),
    ],
    scenario="月度归档流程：清除 30 天前的 Info 级 message，保留 Warning+ 级别和 alarm",
    value="精细规则避免误删重要事件",
    alt="`ClearLoggedEvents(ipClearSettings := 0)` 清整个日志 → 太危险；本 FB 提供精细规则",
    xml_scenario="配置「清除 30 天前 Info 级 message」规则",
    xml_value="精细清理规则",
    xml_verify="实例化后调 AddFilter/SetLimit/SetSorting；之后传给 ClearLoggedEvents",
    xml_vars=[
        ("fbSettings", "FB_TcClearLoggedEventsSettings", None, "清除规则实例"),
        ("nMaxClear", "UDINT", "1000", "最多清 1000 条"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "// 配置：限制清除数量为 1000，避免误清整个日志\n"
        "hr := fbSettings.SetLimit(nLimit := nMaxClear);\n"
        "// 实际工程还应调 AddFilter 添加时间/级别条件；本例仅展示限制\n"
        "// 之后：fbLogger.ClearLoggedEvents(ipClearSettings := fbSettings, ...);"
    ),
    related=["FB_TcEventLogger.ClearLoggedEvents", "FB_TcEventFilter",
             "FB_TcEventCsvExportSettings"],
)


reg("filter", "FB_TcEventCsvExportSettings",
    summary=(
        "`FB_TcEventCsvExportSettings` 配置 `FB_TcEventLogger.ExportLoggedEvents()` 的 CSV 导出格式与过滤规则。\n\n"
        "继承 `FB_TcEventExportSettings`、实现 `I_TcEventCsvExportSettings`。"
        "支持设置：`bWithHeader`（是否含表头）、`nLangId`（导出语言 LCID）、`sDelimiter`（分隔符，默认分号）。"
    ),
    behavior=(
        "FB 是配置容器，不直接发起导出。**用法**：实例化 → 通过属性 setter 配置 CSV 选项"
        "（`bWithHeader` 是否带表头、`nLangId` 导出语言、`sDelimiter` 字段分隔符）→ "
        "把实例传给 `FB_TcEventLogger.ExportLoggedEvents(ipExportSettings := this)` 让它生效。\n\n"
        "**默认值**：`bWithHeader = TRUE`、`nLangId = 1033`（英文）、`sDelimiter = ';'`（分号）。"
        "导出的 CSV 列通常包括事件 ID、EventClass GUID、Severity、SourceName、时间戳、本地化事件文本等。"
        "中国/欧洲场景常用分号分隔（避免与日期/小数里的逗号冲突）；美国习惯用逗号。"
        "继承 FB_TcEventExportSettings 因此也具备父类的过滤能力（按时间/严重级别等）。"
    ),
    return_kind="NONE",
    pitfalls=[
        ("`nLangId` 决定事件文本的导出语言——中文 LCID 是 2052 不是 0x804。", False),
        ("`sDelimiter` 选错会让 Excel 打开 CSV 时无法分列——欧洲一般用 `;`，美国 `,`。", True),
        ("CSV 没有数据类型保留——数字会被 Excel 自动判断类型，可能误判（例如长 EventID 变科学计数法）。", True),
    ],
    scenario="按当前 UI 语言导出本月事件 CSV 供运维分析",
    value="一处配置控制导出格式，灵活适配不同地区/不同分析工具",
    alt="导出固定 CSV 格式 → 不灵活；本 FB 提供完整可配置",
    xml_scenario="配置「中文 + 分号分隔 + 带表头」的 CSV 导出",
    xml_value="灵活的 CSV 格式控制",
    xml_verify="实例化后 fbSettings 的属性应反映你的配置；之后传给 ExportLoggedEvents",
    xml_vars=[
        ("fbSettings", "FB_TcEventCsvExportSettings", None, "CSV 导出配置"),
        ("bWithHeader", "BOOL", "TRUE", "是否含表头"),
        ("nLangId", "DINT", "2052", "中文 LangId"),
        ("sDelimiter", "STRING(4)", "';'", "字段分隔符"),
    ],
    xml_call=(
        "// 实际工程通过 setter / 属性配置 fbSettings\n"
        "// （EventLogger 库版本不同接口略有差异，请参考 InfoSys topic）\n"
        "// 本例仅声明实例与变量；后续：\n"
        "// fbLogger.ExportLoggedEvents(sFileName := '...', ipExportSettings := fbSettings, ...);\n"
        "; // placeholder — 配置具体走属性 setter（取决于库版本）"
    ),
    related=["FB_TcEventLogger.ExportLoggedEvents", "FB_TcClearLoggedEventsSettings"],
)


reg("filter", "FB_TcEventFilter",
    summary=(
        "`FB_TcEventFilter` 是 TwinCAT 3 EventLogger 的**通用事件过滤器**，"
        "支持流式链式语法配置规则，用于 listener 订阅时筛选事件、批量清除/确认操作的范围限定等。\n\n"
        "支持：按 Severity、EventClass、SourceName 等过滤；用 `.AND_OP()` / `.OR_OP()` / `.NOT_OP()` 组合条件；"
        "用 `.FilterExpression()` 分组嵌套。最多 255 个条件——超出返回 `ADS_NOMOREHDL`。"
    ),
    behavior=(
        "**流式构建**：`fbFilter.Severity.GreaterThan(TcEventSeverity.Error).AND_OP().Source.Name.Like('%Main%');`"
        "—— 通过链式属性 + 方法调用一步步累加条件。条件累加完成后，把实例传给"
        "`FB_ListenerBase2.Subscribe2(ipEventFilter := fbFilter)` 等接口生效。\n\n"
        "**编译**：filter 在第一次被 Subscribe / 用于操作时\"编译\"为内部规则树。"
        "之后可以重新调 Subscribe 让 EventLogger 替换过滤器规则——支持运行时动态调整。\n\n"
        "**典型规则**：\"严重级别 ≥ Error 且来源包含 Main 模块\"，\"非调试事件类\" 等。"
    ),
    return_kind="NONE",
    pitfalls=[
        ("最多 255 个条件——超出返回 `ADS_NOMOREHDL`。", False),
        ("链式构建顺序影响逻辑——AND/OR/NOT 的优先级看库实现，复杂规则建议用 FilterExpression 分组。", False),
        ("规则要直到 Subscribe 才编译生效——配置过程中报错不会立即反馈。", True),
        ("STRING 模式匹配（`Like`）支持通配符 `%`，但区分大小写——确认目标字符串大小写一致。", True),
    ],
    scenario="HMI 后端 listener 只接收 \"严重级别 ≥ Warning 且来源是 Main 模块\" 的事件，减少回调负担",
    value="复杂条件一行链式表达，比手写 IF 嵌套清晰得多",
    alt="在 OnXxx 回调里手写 IF 过滤 → 事件已经到回调浪费 CPU；本 FB 在 EventLogger 端就过滤掉",
    xml_scenario="构建「Severity ≥ Warning AND Source.Name 含 Main」的过滤器",
    xml_value="链式条件 + 早过滤节省 CPU",
    xml_verify="实例化后链式调用配置规则；传给 Subscribe2 后只收到匹配事件",
    xml_vars=[
        ("fbFilter", "FB_TcEventFilter", None, "过滤器实例"),
        ("fbListener", "FB_ListenerBase2", None, "listener 实例"),
        ("bSubscribed", "BOOL", None, "订阅 latch"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "// 在 listener 订阅前构建过滤规则\n"
        "// 示意（具体属性接口随库版本演进；以下伪写法表达意图）：\n"
        "// fbFilter.Severity.GreaterEqual(TcEventSeverity.Warning).AND_OP()\n"
        "//         .Source.Name.Like('%Main%');\n"
        "//\n"
        "// 然后订阅：\n"
        "IF NOT bSubscribed THEN\n"
        "    hr := fbListener.Subscribe2(ipEventFilter := fbFilter);\n"
        "    bSubscribed := SUCCEEDED(hr);\n"
        "END_IF;"
    ),
    related=["FB_ListenerBase2.Subscribe2", "FB_TcEventLogger.ClearAlarms",
             "FB_TcEventLogger.ConfirmAlarms"],
)


# ============================================================
# 3.4 RemoteEventLogger (2 FBs)
# ============================================================
reg("remote", "FB_RemoteListenerBase",
    summary=(
        "`FB_RemoteListenerBase` 与 `FB_ListenerBase2` 类似——是事件订阅基类——但订阅的是**远程系统**"
        "的 EventLogger 事件（通过 ADS 跨设备通讯）。\n\n"
        "通过覆盖回调方法可以接收远程设备的 alarm / message 事件，"
        "适合多 PLC 集中监控、HMI 网关、SCADA 中间件等场景。"
    ),
    behavior=(
        "本 FB 自身不维护 VAR_INPUT/OUTPUT，交互通过方法：`Subscribe` 订阅指定 AMS Net ID 远程系统的事件、"
        "`Execute` 周期推进、`Unsubscribe` 取消、回调方法 `OnAlarmRaised` / `OnAlarmCleared` / `OnAlarmConfirmed` / "
        "`OnAlarmDisposed` / `OnMessageSent` 处理远程事件。\n\n"
        "**与本地 listener 差异**：1) 走 ADS 通讯——网络延迟决定回调延迟；2) 远程断网时事件丢失；"
        "3) `Subscribe` 必须指定远程 AMS Net ID + Port；4) 大量远程事件会占用 ADS 通讯带宽。\n\n"
        "**使用模式**：HMI 网关 PLC 上声明本 FB 子类，订阅所有现场 PLC 的事件汇总到一处显示。"
    ),
    return_kind="NONE",
    pitfalls=[
        ("远程通讯不保证传输——网络断时事件丢失，业务侧无法回填。", False),
        ("回调延迟取决于网络 RTT——10 ms 局域网正常，跨地域 VPN 可能数百 ms。", True),
        ("订阅过滤器很重要——远程事件量大且占带宽，必须服务端就过滤。", True),
        ("AMS 路由必须先在 TwinCAT XAE 系统管理器里手动添加远程节点。", True),
    ],
    scenario="工厂 SCADA 网关 PLC 订阅 8 台现场 PLC 的报警事件汇总到中控 HMI",
    value="跨 PLC 事件分发由 Beckhoff 原生支持，免去自建消息中间件",
    alt="自建 ADS 客户端轮询远程 EventLogger → 延迟高 + CPU 浪费；本 FB 走推送模式",
    xml_scenario="订阅远程 PLC 的事件",
    xml_value="跨 PLC 集中监控",
    xml_verify=(
        "需要先在 XAE 路由表配置远程 AMS Net ID。继承 FB_RemoteListenerBase 后 OVERRIDE OnXxx 回调；"
        "Subscribe 时传远程节点信息；触发远程 PLC 的 alarm 应能看到本端回调"
    ),
    xml_vars=[
        ("fbRemoteListener", "FB_RemoteListenerBase", None, "实际工程声明子类"),
        ("bSubscribed", "BOOL", None, "订阅 latch"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "// 远程订阅需要先调 Subscribe 传远程节点 AMS Net ID + Port（具体接口随库版本，参考 InfoSys）。\n"
        "// 之后周期 Execute 推进事件队列，与本地 listener 用法一致。\n"
        "hr := fbRemoteListener.Execute();"
    ),
    related=["FB_ListenerBase2", "FB_TcRemoteEventLogger"],
)


reg("remote", "FB_TcRemoteEventLogger",
    summary=(
        "`FB_TcRemoteEventLogger` 代表**远程系统**的 EventLogger 视图——本端 PLC 通过本 FB 操作远程 EventLogger："
        "清除远程 alarm、确认远程 alarm、向远程系统发送 message、清除远程日志等。\n\n"
        "实现 `I_RemoteEventLogger`。提供 `Connect` / `Disconnect` 建立 ADS 连接；方法集与 `FB_TcEventLogger` 对应"
        "（ClearAlarms / ClearLoggedEvents / ConfirmAlarms / SendMessage*）。"
    ),
    behavior=(
        "**生命周期**：声明实例 → `Connect(sNetId, nPort)` 建立 ADS 通讯 → 调用方法操作远程 EventLogger → "
        "`Disconnect()` 释放连接。所有方法走 ADS 通讯，可能有延迟与失败。\n\n"
        "**使用场景**：\n"
        "- HMI 网关 PLC 远程清除其他 PLC 的 alarm（如紧急批量处理）\n"
        "- 中央 SCADA 把统一通知 message 推送到所有现场 PLC 的 EventLogger\n"
        "- 跨地域多 PLC 集中归档：从中央节点导出所有现场的事件日志\n\n"
        "**与本地 EventLogger 的区别**：1) 所有调用都是异步 ADS 通讯——延迟取决于网络；"
        "2) 断网时方法返回 ADS 错误；3) 权限取决于远程节点的 ADS 安全配置。"
    ),
    return_kind="NONE",
    pitfalls=[
        ("远程操作走 ADS——断网会让方法失败，业务侧需要超时与重试机制。", False),
        ("Disconnect 必须显式调用，否则 PLC 重启前连接占用 ADS 资源。", True),
        ("跨地域 VPN 通讯延迟可能数百 ms——大量操作建议批量化。", True),
        ("远程节点的 EventClass 必须与本端一致——GUID 配错会找不到 alarm。", True),
    ],
    scenario="工厂中央控制室 PLC 通过本 FB 远程清除车间 PLC 的所有 alarm（批量复产前的统一复位）",
    value="跨 PLC 操作不需要 MQTT/HTTP 中间件——Beckhoff 原生 ADS 走通讯",
    alt="自建 ADS 客户端 → 重复造轮子；本 FB 把所有方法封装好",
    xml_scenario="远程清除某 PLC 的所有 alarm",
    xml_value="跨 PLC 维护操作",
    xml_verify="需要远程 AMS 路由已配置。Connect 成功后调用 ClearAllAlarms 应让远程 EventLogger 状态变化",
    xml_vars=[
        ("fbRemoteLogger", "FB_TcRemoteEventLogger", None, "远程 EventLogger 视图"),
        ("sRemoteNetId", "STRING(40)", "'192.168.1.10.1.1'", "远程 AMS Net ID"),
        ("nRemotePort", "UINT", "851", "AMS Port（默认 PLC 任务为 851）"),
        ("bConnected", "BOOL", None, "连接状态"),
        ("bDoConnect", "BOOL", "FALSE", "上升沿触发连接"),
        ("bDoConnectPrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "// 边沿触发：建立连接\n"
        "IF bDoConnect AND NOT bDoConnectPrev THEN\n"
        "    hr := fbRemoteLogger.Connect(sNetId := sRemoteNetId, nPort := nRemotePort);\n"
        "    bConnected := SUCCEEDED(hr);\n"
        "END_IF;\n"
        "bDoConnectPrev := bDoConnect;\n"
        "\n"
        "// 远程操作（示例：批量清除远程 alarm）\n"
        "// IF bConnected THEN hr := fbRemoteLogger.ClearAlarms(...); END_IF;\n"
        "// 流程结束：fbRemoteLogger.Disconnect();"
    ),
    related=["FB_TcEventLogger", "FB_RemoteListenerBase"],
)
