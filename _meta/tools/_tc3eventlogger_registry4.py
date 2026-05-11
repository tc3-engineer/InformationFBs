# Tc3_EventLogger registry — Part 4: FB_ListenerBase2 + methods + FB_TcSourceInfo + FB_TcArguments + FB_TcEvent
from __future__ import annotations

from _tc3eventlogger_registry import reg


# ============================================================
# 3.5 FB_ListenerBase2 + methods
# ============================================================
reg("fb_listenerbase2", "FB_ListenerBase2",
    summary=(
        "`FB_ListenerBase2` 是 TwinCAT 3 EventLogger 的**事件订阅基类**，"
        "PLC 代码通过继承本 FB 并覆盖（OVERRIDE）回调方法接收 EventLogger 广播的事件。"
        "实现 `I_Listener2` 接口。\n\n"
        "回调方法共 5 个：`OnAlarmRaised` / `OnAlarmCleared` / `OnAlarmConfirmed` / `OnAlarmDisposed`"
        "（alarm 四状态变迁）与 `OnMessageSent`（消息发送）。继承本 FB 的子类只需要重写感兴趣的方法、"
        "并在主任务里周期调 `Execute()` 推进事件队列。\n\n"
        "应用：HMI 后端实现自定义事件展示逻辑、写第三方数据库、转发事件到 OPC UA / MQTT 等场景。"
    ),
    behavior=(
        "FB_ListenerBase2 自身没有顶层 VAR_INPUT/OUTPUT，所有交互通过方法：\n\n"
        "**典型生命周期**：声明子类实例 → `Subscribe()` 或 `Subscribe2()` 注册到 EventLogger（可选传过滤器）→ "
        "在 PLC 主任务里每周期调 `fbListener.Execute()` 推进事件队列 → "
        "EventLogger 在合适时机调用子类的 OnXxx 回调方法（同步！在 PLC 任务上下文里运行）→ "
        "退出前调 `Unsubscribe()` 释放订阅。\n\n"
        "**线程模型**：回调在调用 `Execute()` 的 PLC 任务上下文里运行——回调里的代码会占用 PLC 周期时间，"
        "重操作（数据库写、网络 IO）需要异步化或转到后台 FB。回调返回 `<> S_OK` 时 EventLogger 会**暂停**"
        "后续回调直到下一次 Execute——这是流控机制，防止队列堆积压垮 PLC。"
    ),
    return_kind="NONE",
    pitfalls=[
        ("回调里**不要**拷贝 `fbEvent : REFERENCE TO FB_TcEvent`——它只在回调期间有效，回调返回后引用失效。", False),
        ("回调返回非 S_OK 时 EventLogger 暂停后续回调到下次 Execute——可以作为业务侧节流机制，但要注意别一直返回非 S_OK 让事件队列阻塞。", False),
        ("`Execute()` 必须**周期调用**——少调一次都可能导致事件丢失或延迟。", False),
        ("回调里耗时操作（数据库写、网络通信）会拖慢 PLC 周期——重逻辑要异步化。", True),
        ("`Subscribe` / `Subscribe2` 重复调用返回 `ADS_E_EXISTS`，本身无副作用。", False),
    ],
    scenario="把 EventLogger 事件实时同步到 InfluxDB 时序数据库：继承 FB_ListenerBase2，"
             "在 OnAlarmRaised / OnMessageSent 里把事件序列化后送到后台 FB 异步发 HTTP",
    value="一次性的代码框架替代手写「轮询 EventLogger 日志 + diff 找新事件 + 推送」三件套；"
          "EventLogger 在事件发生时主动调用，零延迟",
    alt="轮询 EventLogger 日志 → 延迟高 + CPU 浪费；走 ADS 客户端拉取 → 不实时；"
        "本 FB 走事件驱动是 Beckhoff 推荐方案",
    xml_scenario="自定义 listener 监听 alarm 事件并打印到 trace（实际工程会推到数据库/OPC UA）",
    xml_value="一次声明 + Subscribe + 周期 Execute 完成事件订阅",
    xml_verify=(
        "子类需要 OVERRIDE OnAlarmRaised 等方法（本例只给出主程序）。在 PLC 项目里继承 FB_ListenerBase2 后"
        "导入本例；触发任意 alarm 应能看到子类回调被调用"
    ),
    xml_vars=[
        ("fbListener", "FB_ListenerBase2", None, "实际工程应声明子类（继承自 FB_ListenerBase2）"),
        ("bSubscribed", "BOOL", None, "订阅 latch"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "// 第一次扫描订阅（也可订阅时传过滤器）\n"
        "IF NOT bSubscribed THEN\n"
        "    hr := fbListener.Subscribe(ipMessageFilterConfig := 0, ipAlarmFilterConfig := 0);\n"
        "    bSubscribed := SUCCEEDED(hr);\n"
        "END_IF;\n"
        "\n"
        "// 每周期推进事件队列；EventLogger 会在合适时机回调子类的 OnXxx 方法\n"
        "hr := fbListener.Execute();"
    ),
    related=["FB_ListenerBase2.Subscribe", "FB_ListenerBase2.Execute",
             "FB_ListenerBase2.OnAlarmRaised"],
)


reg("fb_listenerbase2", "Execute",
    summary=(
        "`FB_ListenerBase2.Execute()` 推进事件队列处理——必须在 PLC 任务里**周期调用**，"
        "EventLogger 在本方法内部调用所有挂起的回调（OnAlarmRaised / OnAlarmCleared / OnMessageSent…）。\n\n"
        "不调或漏调都可能导致事件丢失或延迟。"
    ),
    behavior=(
        "本方法内部检查 EventLogger 内部为本 listener 排队的待处理事件，按顺序逐一调用对应的回调方法。"
        "若回调返回 `<> S_OK` 则当前事件保留在队列里，下次 Execute 时重试——这是 EventLogger 内置的流控机制。\n\n"
        "**调用频率**：建议放在 PLC 主任务的每个扫描周期里——10 ms 任务下能保证 10 ms 内事件到达。"
        "若 PLC 任务周期过长（>100 ms）可能导致 HMI 显示延迟；过短则浪费 CPU。"
        "Execute 本身开销很小（无事件时直接返回 S_OK）。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "事件队列推进成功（无事件或全部处理完）", "继续业务"),
        ("其他错误", "内部异常 ⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={},
    pitfalls=[
        ("**必须周期调用**——少调一次可能延迟事件。", False),
        ("回调耗时会拖慢 PLC 周期——重操作必须异步化。", True),
        ("无事件时返回 S_OK 开销很小，不要因为\"省 CPU\"少调。", True),
    ],
    scenario="PLC 主程序里每周期调一次推进 listener 事件队列",
    value="保证事件零延迟到达回调",
    alt="不调 Execute → 事件全部堆积在 EventLogger 内部，HMI 看不到；"
        "本方法是 listener 模式的必须步骤",
    xml_scenario="主程序里每周期推进事件队列",
    xml_value="必须周期调用以保证事件及时到达回调",
    xml_verify="登录后 monitor hr，每周期应为 S_OK；fbListener 必须已 Subscribe",
    xml_vars=[
        ("fbListener", "FB_ListenerBase2", None, "listener 实例"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "// 每周期调用一次推进事件队列\n"
        "hr := fbListener.Execute();"
    ),
    related=["FB_ListenerBase2", "FB_ListenerBase2.Subscribe"],
)


reg("fb_listenerbase2", "Subscribe",
    summary=(
        "`FB_ListenerBase2.Subscribe()` 把 listener 注册到 EventLogger，开始接收事件回调。"
        "支持分别为 message 与 alarm 配置过滤器（`POINTER TO ITcEventFilterConfig`）。\n\n"
        "传 0 = 接收对应类型的所有事件；传具体过滤器实例 = 只接收匹配的事件。"
    ),
    behavior=(
        "一次性注册：通常在 FB_init 或第一次扫描调一次。重复注册返回 `ADS_E_EXISTS`，本身无副作用。\n\n"
        "**过滤器选择**：`ipMessageFilterConfig` 控制 message 事件的接收范围；"
        "`ipAlarmFilterConfig` 控制 alarm 事件。两者独立——可以只订 alarm 不订 message，反之亦然。"
        "过滤器实例通常是 `FB_TcEventFilter` 配置好后传入。\n\n"
        "订阅成功后 EventLogger 把后续匹配事件加入本 listener 的内部队列，等下次 Execute 调用回调。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "订阅成功", "继续周期调用 Execute"),
        ("ADS_E_EXISTS", "已订阅过", "用 latch 跳过重复调用"),
        ("其他错误", "⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={
        "ipMessageFilterConfig": "message 事件过滤器；传 0 接收全部",
        "ipAlarmFilterConfig": "alarm 事件过滤器；传 0 接收全部",
    },
    pitfalls=[
        ("Subscribe 一次性调用——用 latch 包裹。", False),
        ("过滤器传 0 = 接收全部——大型系统事件量大时建议用过滤器减少回调开销。", True),
        ("`Subscribe2` 是简化版（单过滤器）——新工程推荐用 Subscribe2。", False),
    ],
    scenario="HMI 后端 listener 只接收 Error 及以上级别的 alarm 事件以减小回调负担",
    value="过滤器机制让 listener 只关心感兴趣的事件",
    alt="`Subscribe2` 单过滤器 → 新工程推荐；本方法分开过滤器更精细",
    xml_scenario="订阅所有 alarm + message 事件",
    xml_value="一次调用完成订阅，后续周期 Execute 即可收事件",
    xml_verify="登录后 monitor bSubscribed 第一周期变 TRUE",
    xml_vars=[
        ("fbListener", "FB_ListenerBase2", None, "listener 实例"),
        ("bSubscribed", "BOOL", None, "订阅 latch"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "IF NOT bSubscribed THEN\n"
        "    hr := fbListener.Subscribe(\n"
        "        ipMessageFilterConfig := 0,            // 接收全部 message\n"
        "        ipAlarmFilterConfig := 0);             // 接收全部 alarm\n"
        "    bSubscribed := SUCCEEDED(hr);\n"
        "END_IF;"
    ),
    related=["FB_ListenerBase2.Subscribe2", "FB_ListenerBase2.Unsubscribe",
             "FB_ListenerBase2.Execute", "FB_TcEventFilter"],
)


reg("fb_listenerbase2", "Subscribe2",
    summary=(
        "`FB_ListenerBase2.Subscribe2()` 是 `Subscribe()` 的简化版——只接收一个过滤器参数 `ipEventFilter : I_TcEventFilterBase`，"
        "同时控制 message 与 alarm 的接收。\n\n"
        "新工程推荐用本方法——接口更简洁，过滤器逻辑也更统一。"
    ),
    behavior=(
        "一次性订阅：成功返回 `S_OK`，重复订阅返回相应错误码。`ipEventFilter` 传 0 时接收全部事件，"
        "传具体过滤器实例时仅接收匹配规则的事件。\n\n"
        "**与 Subscribe 的区别**：Subscribe 分别配置 message 与 alarm 两个过滤器，"
        "Subscribe2 用一个统一的过滤器实例同时控制两者。新工程推荐用 Subscribe2——"
        "过滤器一次配置完毕，方便维护；老工程兼容用 Subscribe。两者不可在同一 listener 实例上混用。"
        "订阅成功后必须周期调 `Execute()` 让事件队列推进，否则事件堆积在 EventLogger 内部。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "订阅成功", "继续周期调用 Execute"),
        ("其他错误", "⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={
        "ipEventFilter": "统一事件过滤器；传 0 接收全部",
    },
    pitfalls=[
        ("Subscribe2 一次性调用——用 latch 包裹。", False),
        ("统一过滤器机制 = 没法分开控制 message / alarm 的接收——需要分开控制用 Subscribe。", True),
        ("Subscribe 与 Subscribe2 不可混用——选定一个版本就坚持用。", True),
    ],
    scenario="新工程 listener 订阅，配一个 FB_TcEventFilter 过滤所有 Severity ≥ Warning 的事件",
    value="新工程的标准订阅接口；过滤器统一管理便于维护",
    alt="`Subscribe` 双过滤器 → 老工程兼容；新工程优先 Subscribe2",
    xml_scenario="新工程统一过滤器订阅",
    xml_value="单过滤器实例同时控制 message + alarm 的接收",
    xml_verify="登录后 monitor bSubscribed 第一周期变 TRUE",
    xml_vars=[
        ("fbListener", "FB_ListenerBase2", None, "listener 实例"),
        ("fbFilter", "FB_TcEventFilter", None, "事件过滤器实例（在线配置规则）"),
        ("bSubscribed", "BOOL", None, "订阅 latch"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "IF NOT bSubscribed THEN\n"
        "    hr := fbListener.Subscribe2(ipEventFilter := fbFilter);\n"
        "    bSubscribed := SUCCEEDED(hr);\n"
        "END_IF;"
    ),
    related=["FB_ListenerBase2.Subscribe", "FB_ListenerBase2.Unsubscribe",
             "FB_TcEventFilter"],
)


reg("fb_listenerbase2", "Unsubscribe",
    summary=(
        "`FB_ListenerBase2.Unsubscribe()` 取消 listener 订阅，停止接收事件回调。\n\n"
        "调用时机：listener 实例即将销毁时（如配方切换、模块下线）；"
        "或临时停止接收事件（如调试 / 维护模式）。"
    ),
    behavior=(
        "调用即同步生效——之后 EventLogger 不再把事件加入本 listener 的内部队列，"
        "队列中尚未处理的事件会被丢弃。Unsubscribe 之后再调 Execute 不会处理任何事件（队列为空）。\n\n"
        "**典型用法**：FB_exit 里调一次 Unsubscribe 保证资源正确回收；模块下线（如配方切换需要清理旧模块）"
        "也应调用本方法。若需要临时停接事件可以 Unsubscribe → 业务处理 → 重新 Subscribe，"
        "但通常通过更新过滤器规则更轻量。listener 实例销毁前必须 Unsubscribe——"
        "否则 EventLogger 内部保留悬挂引用直到 PLC 重启。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "取消订阅成功", "可销毁 listener 或重新 Subscribe"),
        ("ADS_E_NOTFOUND", "listener 未订阅过", "通常无需处理"),
        ("其他错误", "⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={},
    pitfalls=[
        ("Unsubscribe 后队列里的事件丢失——需要先 Execute 把队列清空再 Unsubscribe。", False),
        ("`ADS_E_NOTFOUND` 表示\"本来就没订阅\"——不是真错误。", False),
        ("listener 销毁前必须 Unsubscribe——否则 EventLogger 持有悬挂引用。", False),
    ],
    scenario="模块下线前清理 listener 订阅",
    value="正确释放 EventLogger 资源",
    alt="不 Unsubscribe 直接销毁 listener → EventLogger 留下悬挂引用，重启 PLC 才清理",
    xml_scenario="模块下线前取消 listener 订阅",
    xml_value="规范的资源释放",
    xml_verify="先 Subscribe；再写 bDoUnsubscribe := TRUE 触发 Unsubscribe；hr 应为 S_OK",
    xml_vars=[
        ("fbListener", "FB_ListenerBase2", None, "listener 实例"),
        ("bDoUnsubscribe", "BOOL", "FALSE", "上升沿触发"),
        ("bDoUnsubscribePrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "IF bDoUnsubscribe AND NOT bDoUnsubscribePrev THEN\n"
        "    hr := fbListener.Unsubscribe();\n"
        "END_IF;\n"
        "bDoUnsubscribePrev := bDoUnsubscribe;"
    ),
    related=["FB_ListenerBase2.Subscribe", "FB_ListenerBase2.Subscribe2"],
)


# Callback methods (OnXxx) — these are overridden in subclasses; PDF lists them as part of base
def _onxxx(name: str, summary: str, when: str, scenario: str):
    reg("fb_listenerbase2", name,
        summary=summary,
        behavior=(
            f"本方法是事件驱动回调（callback），由 EventLogger 在 {when} 调用。"
            "调用上下文是 PLC 任务（调用 listener.Execute() 的任务），因此回调里的代码占用 PLC 周期时间。\n\n"
            "**实现约定**：用户继承 `FB_ListenerBase2` 后用 METHOD OVERRIDE 重写本方法，在方法体内执行业务逻辑——"
            "如更新内部状态、推送到第三方系统、转发到 OPC UA 等。返回 `S_OK` 让 EventLogger 继续后续回调；"
            "返回 `<> S_OK` 让 EventLogger **暂停**回调直到下次 Execute，可用作业务侧节流。\n\n"
            "**重要**：参数 `fbEvent : REFERENCE TO FB_TcEvent` 只在本回调期间有效，"
            "回调返回后引用失效——绝对不要拷贝引用到全局变量或长期持有的结构里。"
            "需要保存事件信息请把 GUID / EventID / Severity / 时间戳等字段拷贝出来。"
        ),
        return_kind="HRESULT",
        returns=[
            ("S_OK", "处理成功", "EventLogger 继续后续回调"),
            ("<> S_OK", "本回调失败 / 业务侧要求节流", "EventLogger 暂停回调到下次 Execute"),
        ],
        var_desc={
            "fbEvent": "事件引用（只在回调期间有效，禁止拷贝）",
        },
        pitfalls=[
            ("`fbEvent` 不能拷贝——回调返回后引用失效。", False),
            ("回调里耗时操作拖慢 PLC 周期——重操作必须异步化。", True),
            ("返回非 S_OK 让事件保留在队列等下次重试——可作节流但不要一直返回非 S_OK。", False),
            ("回调里禁止做阻塞 IO（文件 / 网络）——必须发到后台 FB 处理。", True),
        ],
        scenario=scenario,
        value="事件驱动模型 = 零延迟接收，无需轮询",
        alt="轮询 EventLogger 日志 → 延迟 + CPU 浪费；本回调是 Beckhoff 推荐方案",
        xml_scenario=f"覆盖（OVERRIDE）{name} 回调记录事件元数据到内部计数器",
        xml_value="事件驱动接收的最小实现",
        xml_verify=(
            "本回调由 EventLogger 在事件发生时自动调用——不能在主程序里手动调用做演示。"
            "实际工程：继承 FB_ListenerBase2 后 OVERRIDE 本方法，再让事件触发"
        ),
        xml_vars=[
            ("fbListener", "FB_ListenerBase2", None, "listener 实例（实际工程使用子类）"),
        ],
        xml_call=(
            f"// 本方法是 EventLogger 的事件回调，应该在 FB_ListenerBase2 的子类里 OVERRIDE。\n"
            f"// 这里仅展示在主程序里启动 listener 的代码骨架；具体 {name} 重写见同名 METHOD。\n"
            "// 示例（仅说明）：在子类 FB 里写——\n"
            f"//   METHOD {name} : HRESULT\n"
            "//   VAR_INPUT\n"
            "//       fbEvent : REFERENCE TO FB_TcEvent;\n"
            "//   END_VAR\n"
            "//   nEventCount := nEventCount + 1;\n"
            f"//   {name} := S_OK;\n"
            "//\n"
            "// 主程序示意：\n"
            "fbListener.Execute();"
        ),
        related=["FB_ListenerBase2", "FB_ListenerBase2.Execute", "FB_TcEvent"],
    )


_onxxx("OnAlarmCleared",
       summary=(
           "`FB_ListenerBase2.OnAlarmCleared()` 是 alarm 从 Raised 转 Cleared 时被 EventLogger 调用的回调方法。\n\n"
           "子类 OVERRIDE 本方法即可在 alarm 解除瞬间执行业务逻辑——如更新 HMI 状态、记录\"故障持续时长\"指标。"
       ),
       when="alarm 状态从 Raised 转 Cleared 时",
       scenario="计算故障持续时长指标：在 OnAlarmRaised 记开始时间，OnAlarmCleared 算差值入数据库")

_onxxx("OnAlarmConfirmed",
       summary=(
           "`FB_ListenerBase2.OnAlarmConfirmed()` 是 alarm 被确认时被 EventLogger 调用的回调方法。\n\n"
           "子类 OVERRIDE 本方法即可在操作员确认报警瞬间执行业务逻辑——如计算\"故障响应时长\"、记录确认操作员。"
       ),
       when="alarm 被 Confirm 时",
       scenario="审计指标：计算\"故障 Raise → 操作员 Confirm\"的响应时长写入运维数据库")

_onxxx("OnAlarmDisposed",
       summary=(
           "`FB_ListenerBase2.OnAlarmDisposed()` 是 alarm 实例从 EventLogger 活动表移除时被调用的回调。\n\n"
           "通常发生在 `FB_TcAlarm.Clear(bRemove := TRUE)` 或 `FB_TcAlarm.Release()` 之后。"
           "子类 OVERRIDE 用于资源清理或追溯日志。"
       ),
       when="alarm 实例从活动表移除时",
       scenario="动态报警场景：alarm 实例销毁时清理 HMI 端的对应展示卡片")

_onxxx("OnAlarmRaised",
       summary=(
           "`FB_ListenerBase2.OnAlarmRaised()` 是 alarm 从 Cleared 转 Raised 时被 EventLogger 调用的回调方法。\n\n"
           "子类 OVERRIDE 本方法即可在 alarm 触发瞬间执行业务逻辑——如转发到 MES、记录故障开始时间、"
           "触发应急联动等。"
       ),
       when="alarm 状态从 Cleared 转 Raised 时",
       scenario="生产监控：alarm Raise 瞬间发邮件通知维护班长 + 推送到 MES 工单系统")

_onxxx("OnMessageSent",
       summary=(
           "`FB_ListenerBase2.OnMessageSent()` 是 message 事件被发送时被 EventLogger 调用的回调方法。\n\n"
           "子类 OVERRIDE 本方法即可在每条 message 发送时执行业务逻辑——如审计日志同步、"
           "事件转发到 OPC UA / MQTT / 第三方 SCADA 等。"
       ),
       when="message 事件被发送时",
       scenario="MES 集成：每条 message 实时同步到 InfluxDB 时序数据库以做长期审计")


# ============================================================
# 3.12 FB_TcSourceInfo + methods
# ============================================================
reg("fb_tcsourceinfo", "FB_TcSourceInfo",
    summary=(
        "`FB_TcSourceInfo` 代表事件的**来源信息**（SourceName / SourceID / SourceGuid），实现 `I_TcSourceInfo` 接口。\n\n"
        "在 PLC 里实例化后通过 setter 配置 SourceName/SourceID/SourceGuid，"
        "再传给 `FB_TcAlarm.Create()` / `FB_TcMessage.Create()` 等方法的 `ipSourceInfo` 参数；"
        "传 `0` 时 EventLogger 用 PLC 实例的符号路径作为默认 SourceName。"
    ),
    behavior=(
        "FB_TcSourceInfo 不维护状态机，只是一个携带 SourceName/SourceID/SourceGuid 三字段的容器。"
        "三个字段都有 getter 与 setter；通常在 FB_init 阶段配置好，之后传给 alarm/message 用。\n\n"
        "**方法**：`Clear` 清空全部字段；`ExtendName` 给现有 SourceName 加后缀（适合多工位共享代码场景）；"
        "`ResetToDefault` 还原到 EventLogger 默认（用 PLC 符号路径）。\n\n"
        "**多 PLC / 多工位场景**：每个工位实例化自己的 FB_TcSourceInfo 配置不同 SourceID，"
        "让 EventLogger 能在事件日志里精确区分\"哪台机器哪个工位\"出的事件。"
    ),
    return_kind="NONE",
    pitfalls=[
        ("SourceName/SourceID/SourceGuid 三字段都要配，否则 EventLogger 用默认值——可能与本设备实际不符。", True),
        ("修改 SourceInfo 后只对**未来的事件**生效——已 Raise 过的事件 SourceInfo 已固化。", False),
        ("多 alarm 共享同一 FB_TcSourceInfo 时，修改它影响所有 alarm；通常每个 alarm 独立 FB_TcSourceInfo。", True),
        ("默认 SourceName 是 PLC 实例符号路径——动态生成的 alarm 路径可能不唯一，需要主动 ExtendName。", True),
    ],
    scenario="多工位共享同一份 PLC 代码：每个工位的 FB 实例初始化时配置自己的 FB_TcSourceInfo 用工位号区分",
    value="事后审计能精确定位\"哪台设备哪个工位\"出故障，而不是只看到 PLC 符号路径",
    alt="把工位号塞 Arguments → 信息混在事件参数里不够结构化；本 FB 专门承载来源更规范",
    xml_scenario="配置自定义 SourceInfo 给后续 alarm 用，让事件能定位到具体工位",
    xml_value="多工位事件追溯",
    xml_verify="登录后 fbSrc 实例存在；通过它的 setter 写入工位号；之后给 alarm 用",
    xml_vars=[
        ("fbSrc", "FB_TcSourceInfo", None, "自定义源信息实例"),
        ("sStationId", "STRING(40)", "'Station-01'", "工位号"),
    ],
    xml_call=(
        "// 实际工程：通常在 FB_init 里配置 fbSrc 的 SourceName 字段（通过 setter）。\n"
        "// 之后调用 fbAlarm.Create(..., ipSourceInfo := fbSrc); 把 fbSrc 传给 alarm。\n"
        "// 本例只演示实例化：实际 setter 接口请见 I_TcSourceInfo 文档。\n"
        "fbSrc.ExtendName(sExtName := sStationId);"
    ),
    related=["FB_TcSourceInfo.Clear", "FB_TcSourceInfo.ExtendName",
             "FB_TcSourceInfo.ResetToDefault", "FB_TcEventBase.ipSourceInfo"],
)


reg("fb_tcsourceinfo", "Clear",
    summary=(
        "`FB_TcSourceInfo.Clear()` 清空 SourceInfo 的全部字段（SourceName / SourceID / SourceGuid 都置为默认/空）。\n\n"
        "用于重置 SourceInfo 实例准备复用，或确保 alarm 使用 EventLogger 的默认源信息。"
    ),
    behavior=(
        "调用一次清空三字段：SourceName 变空串、SourceID 变 0、SourceGuid 变全 0。"
        "之后传给 alarm.Create() 时 EventLogger 视为「无自定义源信息」，回退到默认（PLC 符号路径）。\n\n"
        "**与 ResetToDefault 的区别**：Clear 真的清空（让字段为空）；ResetToDefault 是显式还原到 EventLogger 默认值。"
        "实际效果接近，但语义上 Clear 更适合\"准备重新填写\"，ResetToDefault 适合\"我就要默认\"。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "字段已清空", "可重新填写或直接传给 alarm 用默认"),
        ("其他错误", "⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={},
    pitfalls=[
        ("Clear 后 SourceInfo 是空——传给 alarm 后 alarm 用默认源信息（PLC 符号路径）。", False),
        ("Clear 与 ResetToDefault 语义相近，混用 OK 但建议保持一致风格。", True),
        ("不要在运行中清空已被多个 alarm 引用的 SourceInfo——会让那些 alarm 失去来源信息。", True),
    ],
    scenario="复用 FB_TcSourceInfo 实例：清空后重新填字段用于不同 alarm",
    value="支持 SourceInfo 实例的复用，节省资源",
    alt="`ResetToDefault` → 还原到默认；本方法清空字段（语义不同）",
    xml_scenario="清空 SourceInfo 字段以便重新填写",
    xml_value="一次调用让字段回到初始状态",
    xml_verify="登录后调用 Clear；之后 fbSrc 的字段应为空/0/全 0 GUID",
    xml_vars=[
        ("fbSrc", "FB_TcSourceInfo", None, "源信息实例"),
        ("bDoClear", "BOOL", "FALSE", "上升沿触发"),
        ("bDoClearPrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "IF bDoClear AND NOT bDoClearPrev THEN\n"
        "    hr := fbSrc.Clear();\n"
        "END_IF;\n"
        "bDoClearPrev := bDoClear;"
    ),
    related=["FB_TcSourceInfo.ResetToDefault", "FB_TcSourceInfo.ExtendName"],
)


reg("fb_tcsourceinfo", "ExtendName",
    summary=(
        "`FB_TcSourceInfo.ExtendName()` 给现有 SourceName 追加一个后缀字符串。\n\n"
        "典型用法：默认 SourceName 是 PLC 符号路径（如 `MAIN.fbMotor`）；"
        "在多工位场景下用本方法加上工位号（变成 `MAIN.fbMotor.Station-01`），让事件能精确定位。"
    ),
    behavior=(
        "调用即同步执行：内部 SourceName 字符串后面追加 `sExtName` 内容形成新的 SourceName。"
        "多次调用会**累加**而不是覆盖——再调一次会在已经扩展过的 SourceName 后面再加一个后缀，"
        "因此通常只调用一次。\n\n"
        "**典型用法**：FB_init 里调一次 ExtendName 给本工位的 SourceInfo 加唯一标识符（如 `Station-01`），"
        "之后所有 alarm 共享这个 SourceInfo 实例都自带工位号。多工位共用同一份 PLC 代码时，"
        "每个工位实例独立 ExtendName 加自己的工位号，让 EventLogger 在事件日志里"
        "能精确区分哪台设备出的事件。STRING 字段总长度不要超过 256 字节。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "后缀已追加", "继续业务"),
        ("其他错误", "⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={
        "sExtName": "要追加的后缀字符串",
    },
    pitfalls=[
        ("多次调用累加——避免在循环里反复调，否则 SourceName 越来越长。", False),
        ("追加 SourceName 后已存在的 alarm 不受影响——只对新建/新事件生效。", False),
        ("STRING 长度有限——`SourceName` 字段总长建议不超过 256 字节。", True),
    ],
    scenario="多工位代码复用：每个工位的 SourceInfo 实例 ExtendName 一次本工位号",
    value="事件追溯天然带工位标识，无需自建映射表",
    alt="直接 setter 重写 SourceName → 适合完全覆盖；本方法适合\"在默认基础上加后缀\"",
    xml_scenario="给当前工位的 SourceInfo 加工位号后缀",
    xml_value="事件天然带工位标识",
    xml_verify="登录后调用一次 ExtendName 后 fbSrc.sSourceName 应包含 sExtName 内容",
    xml_vars=[
        ("fbSrc", "FB_TcSourceInfo", None, "源信息实例"),
        ("sStationId", "STRING(40)", "'Station-01'", "工位号后缀"),
        ("bDoExtend", "BOOL", "FALSE", "上升沿触发"),
        ("bDoExtendPrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "IF bDoExtend AND NOT bDoExtendPrev THEN\n"
        "    hr := fbSrc.ExtendName(sExtName := sStationId);\n"
        "END_IF;\n"
        "bDoExtendPrev := bDoExtend;"
    ),
    related=["FB_TcSourceInfo", "FB_TcSourceInfo.Clear",
             "FB_TcSourceInfo.ResetToDefault"],
)


reg("fb_tcsourceinfo", "ResetToDefault",
    summary=(
        "`FB_TcSourceInfo.ResetToDefault()` 把 SourceInfo 还原到 EventLogger 的默认值——"
        "即使用 PLC 实例的符号路径作为 SourceName。\n\n"
        "用于撤销之前的 ExtendName 或自定义 setter 修改，回到\"开箱即用\"状态。"
    ),
    behavior=(
        "调用即同步执行：SourceName 重置为 PLC 默认符号路径；SourceID / SourceGuid 重置为默认值。"
        "之后传给 alarm 时 EventLogger 用这些默认源信息。\n\n"
        "**与 Clear 的区别**：ResetToDefault 显式还原到\"EventLogger 提供的默认值\"（非空）；"
        "Clear 是真的清空字段（变空）。两者最终行为接近——传给 alarm 后 alarm 都用默认源信息——"
        "但语义不同。"
    ),
    return_kind="HRESULT",
    returns=[
        ("S_OK", "已还原到默认", "继续业务"),
        ("其他错误", "⚠️ PDF 未列详细码", "查 ADS Return Codes"),
    ],
    var_desc={},
    pitfalls=[
        ("ResetToDefault 后丢失之前的 ExtendName 后缀。", False),
        ("默认 SourceName 是 PLC 符号路径——动态生成的 alarm 路径可能不唯一。", True),
        ("用 Reset 还是 Clear 看团队约定——两者实际行为接近。", True),
    ],
    scenario="测试场景：临时改了 SourceInfo 后用本方法还原到默认",
    value="一次调用还原到 EventLogger 默认行为",
    alt="`Clear` 清空字段；本方法显式还原到默认。两者效果接近",
    xml_scenario="测试结束后还原 SourceInfo 到默认",
    xml_value="一次调用还原",
    xml_verify="登录后调用 ResetToDefault 后 fbSrc 字段回到默认（SourceName = PLC 符号路径）",
    xml_vars=[
        ("fbSrc", "FB_TcSourceInfo", None, "源信息实例"),
        ("bDoReset", "BOOL", "FALSE", "上升沿触发"),
        ("bDoResetPrev", "BOOL", None, "边沿检测"),
        ("hr", "HRESULT", None, "返回值监视"),
    ],
    xml_call=(
        "IF bDoReset AND NOT bDoResetPrev THEN\n"
        "    hr := fbSrc.ResetToDefault();\n"
        "END_IF;\n"
        "bDoResetPrev := bDoReset;"
    ),
    related=["FB_TcSourceInfo", "FB_TcSourceInfo.Clear", "FB_TcSourceInfo.ExtendName"],
)


# ============================================================
# 3.7 FB_TcArguments + IsEmpty
# ============================================================
reg("fb_tcarguments", "FB_TcArguments",
    summary=(
        "`FB_TcArguments` 代表事件的**参数列表**（Arguments），实现 `I_TcArguments` 接口。\n\n"
        "在 PLC 里实例化后通过 `AddInt` / `AddReal` / `AddBool` / `AddString` 等 20+ Add 方法依次压入参数；"
        "传给 alarm/message 的 `ipArguments` 参数；EventLogger 在事件文本里用占位符 `{0}` `{1}` `{2}` … 按"
        "压入顺序填充。\n\n"
        "支持的类型：BOOL / SINT/INT/DINT/LINT / USINT/UINT/UDINT/ULINT / REAL/LREAL / BYTE/WORD/DWORD / STRING / "
        "Blob / 时间戳 / 事件引用 ID 等。"
    ),
    behavior=(
        "FB_TcArguments 不维护状态机，只是一个有序的参数列表容器。每次 `AddXxx()` 把参数追加到末尾。\n\n"
        "**调用流程**：1) 在 Raise/Send 之前实例化 FB_TcArguments；2) 调用 AddXxx 依次压入参数；"
        "3) 把它的接口指针传给 alarm.Raise / logger.SendMessage 的 ipArguments 参数；"
        "4) EventLogger 在事件文本里按序填充。\n\n"
        "**参数顺序必须严格对应文本模板的占位符**——顺序错了文本会乱填。"
        "`IsEmpty()` 方法检测当前是否无参数（适合调用 Add 前的状态判断）。"
    ),
    return_kind="NONE",
    pitfalls=[
        ("参数压入顺序与文本占位符 `{0}` `{1}` 严格对应——顺序错了文本乱填。", False),
        ("一次 Raise 用完后 Arguments 状态保留——下次 Raise 前要清空（重新实例化或用 Clear，若有）。", True),
        ("STRING 默认长度 80 字节——长字符串先 STRING(255)+。", True),
        ("AddBlob 用于二进制数据，注意 EventLogger 端不一定能显示。", True),
        ("`IsEmpty()` 适合在 Add 前判断当前列表状态。", False),
    ],
    scenario="alarm 文本「电机 {0} 温度 {1}°C 过高」的两个占位符需要在 Raise 前 AddString + AddReal 填值",
    value="结构化参数列表 + EventLogger 自动文本填充，比手写字符串拼接更安全、支持多语言",
    alt="`SetJsonAttribute` 写 JSON → 适合嵌套结构；本 FB 适合标准类型按顺序压入；"
        "手写 CONCAT 字符串 → 多语言切换困难",
    xml_scenario="给即将 Raise 的 alarm 添加电机名 + 温度两个参数",
    xml_value="结构化参数 + 自动占位符填充",
    xml_verify="登录后 ipArgs 通过 fbAlarm.ipArguments 拿到；调 IsEmpty 应该为 TRUE；调 AddString/AddReal 后 IsEmpty 为 FALSE",
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "alarm 实例（已 Create）"),
        ("ipArgs", "I_TcArguments", None, "参数列表接口"),
        ("sMotorName", "STRING(40)", "'M-01'", "电机名"),
        ("rTemperature", "REAL", "95.5", "温度"),
        ("bArgsEmpty", "BOOL", None, "参数表是否为空"),
        ("bDoAdd", "BOOL", "FALSE", "上升沿触发"),
        ("bDoAddPrev", "BOOL", None, "边沿检测"),
    ],
    xml_call=(
        "ipArgs := fbAlarm.ipArguments;                  // 拿到参数列表接口\n"
        "IF ipArgs &lt;&gt; 0 THEN\n"
        "    bArgsEmpty := ipArgs.IsEmpty();             // 调用 FB_TcArguments.IsEmpty\n"
        "    IF bDoAdd AND NOT bDoAddPrev THEN\n"
        "        ipArgs.AddString(sValue := sMotorName);\n"
        "        ipArgs.AddReal(fValue := rTemperature);\n"
        "    END_IF;\n"
        "    bDoAddPrev := bDoAdd;\n"
        "END_IF;"
    ),
    related=["FB_TcArguments.IsEmpty", "FB_TcEventBase.ipArguments"],
)


reg("fb_tcarguments", "IsEmpty",
    summary=(
        "`FB_TcArguments.IsEmpty()` 返回 BOOL，表示当前参数列表是否为空（即没有调用过任何 Add 方法）。\n\n"
        "用于在 Add 前判断列表状态——例如确保某 alarm 的 Arguments 是\"全新\"的没有残留参数。"
    ),
    behavior=(
        "本方法立即同步返回 BOOL：TRUE 表示列表当前没有任何参数（即从未调用过 Add 方法，或者实例刚刚被重置）；"
        "FALSE 表示已经有至少一个参数压入列表。本方法无副作用，可以放心反复调用。\n\n"
        "**典型用法**：在调用 alarm.Raise 之前先判断 `ipArguments.IsEmpty()`——若为 FALSE 表示上次 Raise 的"
        "参数列表残留，可能影响本次事件文本中的占位符填充。是否清空残留看业务需求——"
        "通常事件每次都应该重新填参数（保证文本占位符的语义正确），所以发现残留时建议重新实例化 FB_TcArguments。"
    ),
    return_kind="BOOL",
    returns=[
        ("TRUE", "参数列表为空", "可以开始调 AddXxx 填参数"),
        ("FALSE", "参数列表有内容", "上次的参数仍在；可能需要清空或忽略"),
    ],
    var_desc={},
    pitfalls=[
        ("IsEmpty 不是\"长度 = 0\"——只是布尔，无法知道具体多少个参数。", False),
        ("EventLogger 库没有公开 Clear 方法——若需要清空只能重新实例化 FB_TcArguments。", True),
        ("调用 IsEmpty 无副作用——可以放心反复调用。", False),
    ],
    scenario="Raise 前判断参数列表状态，若 FALSE 说明残留——决策日志输出 / 警告",
    value="一次 BOOL 判断替代手写计数器",
    alt="自建 BOOL 标志位标记是否已 Add → 容易和实际状态脱节；本方法直接问库内部状态",
    xml_scenario="Raise 前检查参数表残留",
    xml_value="一次调用获取状态",
    xml_verify="登录后 monitor bEmpty；调用 Add 前应为 TRUE，Add 后为 FALSE",
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "alarm 实例（已 Create）"),
        ("ipArgs", "I_TcArguments", None, "参数列表接口"),
        ("bEmpty", "BOOL", None, "参数表状态"),
    ],
    xml_call=(
        "ipArgs := fbAlarm.ipArguments;\n"
        "IF ipArgs &lt;&gt; 0 THEN\n"
        "    bEmpty := ipArgs.IsEmpty();\n"
        "END_IF;"
    ),
    related=["FB_TcArguments", "FB_TcEventBase.ipArguments"],
)


# ============================================================
# 3.8 FB_TcEvent (misc, read-only)
# ============================================================
reg("misc", "FB_TcEvent",
    summary=(
        "`FB_TcEvent` 是 TwinCAT 3 EventLogger 中代表**只读事件视图**的功能块——"
        "在 `FB_ListenerBase2` 的回调里收到的 `fbEvent : REFERENCE TO FB_TcEvent` 就是它。\n\n"
        "本 FB 只提供**读方法和读属性**，不能修改事件——访问 EventClass / EventID / Severity / 时间戳 / "
        "ipArguments / ipSourceInfo / GetJsonAttribute / EqualsTo* 等元信息。"
    ),
    behavior=(
        "FB_TcEvent 是只读视图，自身没有顶层 VAR_INPUT/OUTPUT。"
        "通过继承 `FB_TcEventBase` 拿到 base 类的所有读方法（EqualsTo / RequestEventText / GetJsonAttribute / "
        "ipArguments / ipSourceInfo …），但**不**提供 Raise / Clear / Confirm 这种状态改写。\n\n"
        "**使用场景**：listener 回调里的 fbEvent 参数；从 EventLogger API 拿到的事件查询结果。"
        "**注意**：fbEvent 引用只在回调期间有效，不要拷贝。需要保存事件数据请拷贝具体字段（如 GUID / EventID / 时间戳）。"
    ),
    return_kind="NONE",
    pitfalls=[
        ("fbEvent 引用只在回调期间有效——回调返回后失效。", False),
        ("禁止拷贝 fbEvent 引用到全局变量。", False),
        ("FB_TcEvent 是只读——别试图调 Raise / Clear，方法不存在。", False),
        ("需要事件数据请拷贝出 GUID / EventID / Severity / 时间戳到本地变量再用。", True),
    ],
    scenario="listener OnAlarmRaised 回调里读 fbEvent 的元数据用于自定义处理",
    value="统一的只读事件视图——所有 EventLogger 回调用同一接口，业务侧不区分 alarm/message",
    alt="把每种事件用专门类型 → 接口爆炸；本 FB 一个视图覆盖所有",
    xml_scenario="listener 回调中读取 fbEvent 的元数据",
    xml_value="只读视图统一所有事件类型访问",
    xml_verify=(
        "本 FB 主要在 listener 回调里使用——直接演示需要先继承 FB_ListenerBase2。"
        "本例演示从 alarm 实例拿到 FB_TcEvent 接口的方法。"
    ),
    xml_vars=[
        ("fbAlarm", "FB_TcAlarm", None, "alarm 实例（已 Create）"),
        ("ipEvent", "I_TcEvent", None, "只读事件接口"),
        ("bMatch", "BOOL", None, "示例：用 EqualsTo 比较"),
    ],
    xml_call=(
        "// FB_TcAlarm 通过接口转型可以暴露为 I_TcEvent / I_TcEventBase 接口\n"
        "// 即\"只读事件视图\"——listener 回调里收到的 fbEvent 就是这个视图。\n"
        "ipEvent := fbAlarm;\n"
        "IF ipEvent &lt;&gt; 0 THEN\n"
        "    bMatch := ipEvent.EqualsToEventEntry(stEventEntry := ipEvent.stEventEntry);\n"
        "END_IF;"
    ),
    related=["FB_TcAlarm", "FB_TcMessage", "FB_TcEventBase", "FB_ListenerBase2.OnAlarmRaised"],
)
