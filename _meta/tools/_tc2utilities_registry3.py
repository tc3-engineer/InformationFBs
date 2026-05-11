# Tc2_Utilities registry — part 3: DCF77/RTC, ADS routes, network info,
# license / dongle, file IO.

from _tc2utilities_registry import REG


def _add(name, *, summary, behavior, pitfalls, scenario, value, alt,
         xml_scen, xml_val, xml_verify, var_desc=None,
         return_kind="NONE", related=None, xml_extra_vars=None,
         xml_call=None):
    REG[name] = dict(
        summary=summary, behavior=behavior, pitfalls=pitfalls,
        scenario=scenario, value=value, alt=alt,
        xml_scen=xml_scen, xml_val=xml_val, xml_verify=xml_verify,
        var_desc=var_desc or {}, return_kind=return_kind,
        related=related or [], xml_extra_vars=xml_extra_vars or [],
        xml_call=xml_call,
    )


# ============================================================================
# DCF77 / RTC group
# ============================================================================

_add(
    "DCF77_TIME",
    summary=(
        "DCF77_TIME 解码 DCF77 长波时间信号脉冲序列，把每分钟一次的德国标准时间广播（PTB 法兰克福 77.5 kHz）还原成日期 / 时刻，"
        "并保持 PLC 内置软时钟与之每分钟对齐。适用于楼宇时钟、铁路时刻牌等需要可追溯校准的场合。\n\n"
        "本 FB 是经典 DCF77 解码器：依赖外部硬件接收模块每秒提供一个数字脉冲（200 ms 表示 0、100 ms 表示 1），"
        "FB 内部用一个 PLC 周期级的时间窗采样脉冲长度，按 DCF77 协议把 59 秒的报文位拼成完整时间帧。"
    ),
    behavior=(
        "**信号流**：`DCF_INPUT` 接入解调后的二进制脉冲（高有效）。FB 内部以 PLC 周期为粒度测量每个脉冲的高电平时长："
        "高电平 100 ms 解为 bit `0`、200 ms 解为 bit `1`。第 59 秒缺脉冲（同步标记）→ 触发本帧解析。\n\n"
        "**输出节奏**：每分钟整点（第 0 秒）`DCF_TIME_VALID = TRUE` 一个 PLC 周期，同时 `DCF_DATE_AND_TIME` 装载新解码的日期时间。其他时间 `DCF_TIME_VALID = FALSE`，但 `DCF_DATE_AND_TIME` 保留上一帧值。\n\n"
        "**`CDT` 输出**：1 = 当前为夏令时（CEST），0 = 标准时（CET）。`CHANGE_DT` 输出在切换前的最后 1 小时为 TRUE，提示业务侧准备处理跳变。\n\n"
        "**状态恢复**：信号丢失（连续 N 秒无脉冲）→ `DCF_TIME_VALID` 不再为 TRUE，需要等下一帧完整接收。"
    ),
    pitfalls=[
        ("**只能用在德语区 / 中欧**：DCF77 信号传播范围约 2000 km。中国、北美使用要换 BPC / WWVB 接收模块及对应解码 FB。", False),
        ("解调脉冲必须按 DCF77 标准（100 ms / 200 ms 占空），不同接收模块输出极性 / 电平不同——上电要先用示波器确认。", True),
        ("**首次有效输出要等 ≥ 1 分钟**：报文 59 位，需完整接到一次同步标记后才输出。重启 PLC 期间业务时钟应另有兜底（用 RTC_EX2）。", False),
        ("夏令时切换期 03:00 重复 / 跳过 1 小时，业务代码做时间戳差值时必须按 `DT` 类型用 UTC 计算，不能直接相减。", True),
        ("PLC 周期太长（> 50 ms）会丢失脉冲沿，建议在 ≤ 10 ms 的任务里调用本 FB。", True),
    ],
    var_desc={
        "DCF_INPUT": "解调后的 DCF77 二进制脉冲信号（高有效）。直接来自接收模块的数字输出端子。",
        "DCF_TIME_VALID": "本 PLC 周期解出一帧有效时间时为 TRUE（每分钟整点 1 个周期）。",
        "DCF_DATE_AND_TIME": "最近一次解出的日期时间，类型 `DT`。",
        "CDT": "夏令时标志：TRUE = CEST 夏令时，FALSE = CET 标准时。",
        "CHANGE_DT": "夏令时 / 标准时切换前的最后 1 小时为 TRUE，预警业务程序。",
    },
    scenario="楼宇大堂电子时钟显示，要保证误差 < 1 秒并自动处理欧洲夏令时切换；用 DCF77 接收模块 + 本 FB 解码。",
    value="替代自写状态机解析 59 位 DCF77 报文 + 校验位 + 同步标记，约省 80 行代码。",
    alt=(
        "- 用 SNTP / NTP 网络时间：需要互联网，机柜内 OT 网段不一定通，且抗干扰差。\n"
        "- **本 FB**：纯硬件信号、抗电磁干扰、欧盟内合法可追溯。"
    ),
    xml_scen="把 DI 模块上接的 DCF77 解调脉冲喂给本 FB，monitor 解码结果。",
    xml_val="自动处理 59 位 DCF77 报文。",
    xml_verify="使 bDcfPulseInput 按 DCF77 协议节奏跳变（实际是真实模块输入），1 分钟后观察 bTimeValid 翻 TRUE 一个周期，dtDecodedTime 装载新时间。",
    xml_extra_vars=[
        ("bDcfPulseInput", "BOOL", None, "DCF77 接收模块的数字脉冲输出（每秒 100 ms 或 200 ms 高电平）"),
        ("bTimeValid", "BOOL", None, "每分钟整点出现 1 个 PLC 周期的 TRUE"),
        ("dtDecodedTime", "DT", None, "最近解出的日期时间"),
        ("bIsDaylightSaving", "BOOL", None, "TRUE = CEST 夏令时"),
        ("bDstChangeHourly", "BOOL", None, "切换前 1 小时预警"),
    ],
    xml_call=(
        "fbDCF77_TIME(\n"
        "    DCF_INPUT := bDcfPulseInput,\n"
        "    DCF_TIME_VALID => bTimeValid,\n"
        "    DCF_DATE_AND_TIME => dtDecodedTime,\n"
        "    CDT => bIsDaylightSaving,\n"
        "    CHANGE_DT => bDstChangeHourly\n"
        ");"
    ),
    related=["DCF77_TIME_EX", "RTC_EX2", "FB_LocalSystemTime"],
)


_add(
    "DCF77_TIME_EX",
    summary=(
        "DCF77_TIME_EX 是 DCF77_TIME 的增强版：除了解码出日期时间外，"
        "还额外把 DCF77 报文里的星期几（`DOW` 输出）独立暴露出来，方便业务程序直接按周期日历做调度（例如周末跳过排产、周一报表）。\n\n"
        "解码逻辑与 DCF77_TIME 完全相同，仅多了一个输出引脚。"
    ),
    behavior=(
        "行为与 DCF77_TIME 完全一致（脉冲长度判位 + 59 秒同步标记），唯一区别是输出额外提供 `DOW`：\n\n"
        "- `DOW = 1` 周一 ... `DOW = 7` 周日（按 DCF77 协议）\n"
        "- `DOW` 仅在 `DCF_TIME_VALID = TRUE` 那个周期同步刷新；其他时间保留上一帧值。\n\n"
        "对脉冲信号、PLC 周期、夏令时处理的要求与 DCF77_TIME 相同。"
    ),
    pitfalls=[
        ("`DOW` 仅在 `DCF_TIME_VALID = TRUE` 时同步刷新——业务代码不要在 `DCF_TIME_VALID = FALSE` 时把 `DOW` 当做实时值用。", False),
        ("DCF77 协议规定 `DOW = 1..7`（周一到周日）；与 IEC 标准的 `DAY_OF_WEEK`（部分库 0..6 周日开始）不同，对接前要核实编号约定。", True),
        ("其余坑与 DCF77_TIME 相同：地理范围、脉冲极性、PLC 周期、夏令时跳变。", False),
        ("`DOW` 解码错（接收模块校验位失败）时会保持上一帧的 `DOW`，业务侧无法直接区分；若关键应交叉用日期算 ISO 周次再比对。", True),
        ("PDF 未单列 `DOW` 错误码——它跟整帧捆绑校验。", False),
    ],
    var_desc={
        "DCF_INPUT": "解调后的 DCF77 二进制脉冲（高有效）。",
        "DCF_TIME_VALID": "每分钟整点 1 个 PLC 周期为 TRUE。",
        "DCF_DATE_AND_TIME": "最近一次解出的日期时间。",
        "CDT": "TRUE = CEST 夏令时，FALSE = CET 标准时。",
        "CHANGE_DT": "切换前 1 小时为 TRUE。",
        "DOW": "DCF77 报文里的星期几：1 = 周一，7 = 周日。",
    },
    scenario="楼宇照明 / HVAC 排程：周一到周五自动开夜间灯，周末关；用 DCF77 解码出 DOW 直接当排程键。",
    value="比 DCF77_TIME 多 1 个 DOW 输出，省去用 `DT` 算 ISO 周次的代码。",
    alt=(
        "- 用 DCF77_TIME + IEC 函数计算星期几：可行但额外 5-10 行代码。\n"
        "- **本 FB**：硬件解码出来后直接给周次，少一步换算。"
    ),
    xml_scen="楼宇空调排程，根据 DOW 区分工作日 / 周末时段。",
    xml_val="DOW 直接由 DCF77 报文提供，免自算。",
    xml_verify="观察 byWeekday 在每分钟刷新，应在 1..7 之间。",
    xml_extra_vars=[
        ("bDcfPulse", "BOOL", None, "DCF77 接收脉冲"),
        ("bValid", "BOOL", None, ""),
        ("dtTime", "DT", None, ""),
        ("bDst", "BOOL", None, ""),
        ("bDstChange", "BOOL", None, ""),
        ("byWeekday", "BYTE", None, "1 = 周一 ... 7 = 周日"),
    ],
    xml_call=(
        "fbDCF77_TIME_EX(\n"
        "    DCF_INPUT := bDcfPulse,\n"
        "    DCF_TIME_VALID => bValid,\n"
        "    DCF_DATE_AND_TIME => dtTime,\n"
        "    CDT => bDst,\n"
        "    CHANGE_DT => bDstChange,\n"
        "    DOW => byWeekday\n"
        ");"
    ),
    related=["DCF77_TIME"],
)


_add(
    "RTC",
    summary=(
        "RTC（Real-Time Clock）是 PLC 内部的软时钟基础版：给一个起始日期时间和秒级使能信号，"
        "FB 按 PLC 周期自走，每秒推进 1 秒，输出当前日期时间。在没有外部时间源（DCF77 / SNTP）的场合做时间戳基础。\n\n"
        "起始时间需要业务程序在 `EN := TRUE` 上升沿前预置；之后 FB 内部不再依赖外部输入。"
    ),
    behavior=(
        "**启动**：`EN := TRUE` 上升沿瞬间，FB 把 `PDT` 输入装入内部状态，作为时间基准。\n\n"
        "**自走**：使能期间，每个 PLC 周期内部累加 PLC 任务周期时长；累积 ≥ 1 秒时 `ACT_TIME` 输出 +1 秒。"
        "因为基于 PLC 任务计数，精度受任务周期抖动影响，长期会漂移（典型每天数秒）。\n\n"
        "**停止 / 重启**：`EN := FALSE` 时 FB 暂停推进，`ACT_TIME` 保留最后值；再次 `EN := TRUE` 上升沿会重新把 `PDT` 装载，等于 reset。\n\n"
        "**`CDT` 输出**：固定为 FALSE（基础版 RTC 不感知夏令时；要夏令时改用 RTC_EX 或 RTC_EX2）。"
    ),
    pitfalls=[
        ("精度受 PLC 任务周期决定，长期不准（典型每天漂移数秒到数十秒）。需要精准时间应配合 `FB_LocalSystemTime` 或 DCF77 周期校准。", False),
        ("`EN := TRUE` 上升沿会重新装载 `PDT`，业务代码必须保证此刻 `PDT` 已是期望的起点；否则时间会跳回。", False),
        ("没有夏令时支持——CDT 永远 FALSE。", False),
        ("PLC 重启后 RTC 状态丢失，需要业务代码持久化保存 `ACT_TIME` 并在启动时回写到 `PDT`。（工程经验补充）", True),
        ("基础版 RTC 已被 RTC_EX2 全面取代；新代码建议直接用 RTC_EX2。", True),
    ],
    var_desc={
        "EN": "TRUE 使能时钟推进；上升沿装载 `PDT` 为起点。",
        "PDT": "起始日期时间。`EN` 上升沿时被复制到内部时钟。",
        "ACT_TIME": "当前实时时钟值，FB 每秒推进。",
        "CDT": "夏令时标志（基础版恒为 FALSE）。",
    },
    scenario="OEM 设备出厂没有外部时间源，用 PLC 程序里硬编码的起始时间 + RTC 自走，给现场日志打粗略时间戳。",
    value="封装秒级累加和起点装载逻辑，替代手写 `DT_ADD` + 计时器。",
    alt=(
        "- 自写 TON + DT_ADD：可行，约 10 行代码。\n"
        "- **本 FB**：标准库提供。\n"
        "- 升级路径：用 RTC_EX2 + 同步源（DCF77 / SNTP / 本机 Windows 时间）。"
    ),
    xml_scen="设备出厂硬编码起点 DT#2026-01-01-00:00:00，使能后内部自走作为粗略时间戳源。",
    xml_val="替代自写 TON + DT_ADD。",
    xml_verify="在线写 bEnable := TRUE，观察 dtActual 每秒 +1；改 bEnable := FALSE 停推进；再 TRUE 会重新跳回 dtStart。",
    xml_extra_vars=[
        ("bEnable", "BOOL", "FALSE", "上升沿装载起点；电平保持推进"),
        ("dtStart", "DT", "DT#2026-01-01-00:00:00", "起始时间"),
        ("dtActual", "DT", None, "当前 RTC 输出"),
        ("bDst", "BOOL", None, "夏令时（基础版恒 FALSE）"),
    ],
    xml_call=(
        "fbRTC(EN := bEnable, PDT := dtStart, ACT_TIME => dtActual, CDT => bDst);"
    ),
    related=["RTC_EX", "RTC_EX2", "FB_LocalSystemTime"],
)


_add(
    "RTC_EX",
    summary=(
        "RTC_EX 是 RTC 的增强版：在 RTC 的基础上增加毫秒级精度（`ACT_TIME` 类型 `LTIME` 或带毫秒的 `TIMESTRUCT`），"
        "并且支持外部时钟源校准——`PDT` 输入在使能期间发生变化也会被采纳，不再仅限于上升沿装载。\n\n"
        "适合需要做毫秒级时间戳的报表 / 日志场景，但精度仍受 PLC 任务周期限制（任务周期 10 ms → 毫秒数也只能 ±5 ms 抖动）。"
    ),
    behavior=(
        "**初始装载**：与 RTC 相同，`EN` 上升沿装载 `PDT`。\n\n"
        "**外部校准**：使能期间若 `PDT` 与 FB 内部当前时间差超过阈值（PDF 列出的阈值在毫秒级），FB 把内部时间向 `PDT` 拉过去，"
        "实现外部时钟（如 NT_GetTime 周期读出来）对内部 RTC 的校准。\n\n"
        "**推进精度**：每个 PLC 周期把任务周期时长累加到 `ACT_TIME`，输出含毫秒字段。\n\n"
        "**夏令时**：仍不支持。要时区 / 夏令时应继续向 RTC_EX2 升级。"
    ),
    pitfalls=[
        ("`PDT` 在使能期间不再是只读输入——业务侧若用同一变量做存储和输入，会被 FB 周期性拉值，可能产生反馈环。建议给 FB 专用的 `PDT` 输入变量。", True),
        ("毫秒字段精度受任务周期限制（10 ms 任务 → 毫秒抖动 ±5 ms），别用于硬实时同步。", False),
        ("夏令时 / 时区仍不支持。", False),
        ("外部校准阈值是固定的（PDF 详情见 RTC_EX2，RTC_EX 阈值在 1 秒级别）。校准太频繁会导致输出值跳动；推荐外部源采样率与 FB 调用周期匹配。", True),
        ("PLC 重启后状态丢失，需要业务代码做断电保护。", True),
    ],
    var_desc={
        "EN": "TRUE 使能；上升沿装载 `PDT`。",
        "PDT": "外部参考时间，使能期间也可被采纳做校准。",
        "ACT_TIME": "当前 RTC 输出（含毫秒）。",
        "CDT": "夏令时标志（恒 FALSE）。",
    },
    scenario="给 OEM 设备的事件日志打带毫秒的时间戳，用 NT_GetTime 每 5 秒读一次 Windows 时间作为 PDT 校准源。",
    value="替代自写 RTC + 外部校准对比逻辑，约省 15 行代码。",
    alt=(
        "- RTC（基础版）：无毫秒、无校准。\n"
        "- RTC_EX2（推荐）：在 RTC_EX 基础上加时区 / 夏令时支持。\n"
        "- **本 FB**：过渡选择，建议新代码直接用 RTC_EX2。"
    ),
    xml_scen="给事件日志打毫秒时间戳，NT_GetTime 5 秒一次校准。",
    xml_val="带毫秒精度 + 自动校准。",
    xml_verify="观察 stActualTime.wMilliseconds 在变；周期把 stReference 从 NT_GetTime 拉新值，stActualTime 跟随。",
    xml_extra_vars=[
        ("bEn", "BOOL", "TRUE", ""),
        ("stReference", "TIMESTRUCT", None, "外部参考时间（NT_GetTime 输出）"),
        ("stActualTime", "TIMESTRUCT", None, "RTC_EX 推进输出"),
        ("bDst", "BOOL", None, ""),
    ],
    xml_call=(
        "fbRTC_EX(EN := bEn, PDT := stReference, ACT_TIME => stActualTime, CDT => bDst);"
    ),
    related=["RTC", "RTC_EX2", "NT_GetTime"],
)


_add(
    "RTC_EX2",
    summary=(
        "RTC_EX2 是 RTC 系列的最终版：在 RTC_EX 基础上把 `TIMESTRUCT` 全面替换为 `TIMESTRUCT`（含毫秒）输出，"
        "并加上时区 / 夏令时支持（`CDT` 现在真的会根据时区状态翻 TRUE/FALSE）。是 `FB_LocalSystemTime` 内部用来"
        "做自走时钟的底层 FB。\n\n"
        "新代码做时间戳 / 日志时钟基础推荐直接用 RTC_EX2 + 配合 NT_GetTime（外部校准源）。"
    ),
    behavior=(
        "**启动 / 推进 / 校准**：与 RTC_EX 相同。\n\n"
        "**夏令时**：FB 内部不再硬编码 CDT = FALSE，而是从 `PDT` 中提取（如果 `PDT` 由 FB_LocalSystemTime 提供，则带时区信息），"
        "或在使用 NT_GetTime 校准时一并采集时区状态。\n\n"
        "**毫秒精度**：每个 PLC 周期把任务周期累加，输出 `TIMESTRUCT` 含 `wMilliseconds` 字段。\n\n"
        "**典型用法**：通常不直接调用 RTC_EX2，而是用更高层的 `FB_LocalSystemTime`（它内部组合了 RTC_EX2 + NT_GetTime + 时区查询）。"
        "直接使用 RTC_EX2 的场景是定制时间源（如 GPS / DCF77 输入做 `PDT`）。"
    ),
    pitfalls=[
        ("**优先用 FB_LocalSystemTime**：直接用 RTC_EX2 需要自己提供 `PDT` 与时区一致性；用 FB_LocalSystemTime 一行调用即可。", True),
        ("`PDT` 输入要在每次校准时同步更新时区，否则 `CDT` 不会跟随切换。", False),
        ("毫秒精度仍受 PLC 任务周期限制（10 ms 任务 → 5 ms 抖动）。", False),
        ("PLC 重启后状态丢失。", True),
        ("PDF 没有列错误码——本 FB 无错误输出。", False),
    ],
    var_desc={
        "EN": "TRUE 使能；上升沿装载 `PDT`。",
        "PDT": "外部参考时间（带时区信息），使能期间也可校准。",
        "ACT_TIME": "当前 RTC 输出（`TIMESTRUCT`，含毫秒）。",
        "CDT": "TRUE = 当前为夏令时；FALSE = 标准时。",
    },
    scenario="GPS 接收模块输出 PPS + 时间报文，业务程序解析后填 `PDT`，用 RTC_EX2 在 GPS 帧之间自走。",
    value="带时区感知 + 毫秒 + 自动校准的软时钟，是 FB_LocalSystemTime 内部底层。",
    alt=(
        "- FB_LocalSystemTime（推荐）：一行调用搞定，省 5-6 个底层 FB 组合。\n"
        "- RTC_EX：无时区支持。\n"
        "- **本 FB**：自定义校准源场景。"
    ),
    xml_scen="GPS PPS + NMEA 解析得到的 TIMESTRUCT 作为 PDT，RTC_EX2 在两次 GPS 帧之间自走。",
    xml_val="带时区 + 毫秒 + 自动校准。",
    xml_verify="观察 stActual 每秒推进，wMilliseconds 在 0..999 之间循环；改 stRef 模拟 GPS 帧，stActual 会被拉到新值。",
    xml_extra_vars=[
        ("bEnable", "BOOL", "TRUE", ""),
        ("stRef", "TIMESTRUCT", None, "外部参考（GPS / NT_GetTime）"),
        ("stActual", "TIMESTRUCT", None, "RTC_EX2 输出（含毫秒）"),
        ("bDst", "BOOL", None, ""),
    ],
    xml_call=(
        "fbRTC_EX2(EN := bEnable, PDT := stRef, ACT_TIME => stActual, CDT => bDst);"
    ),
    related=["RTC", "RTC_EX", "FB_LocalSystemTime", "NT_GetTime"],
)
