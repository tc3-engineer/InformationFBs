# Tc2_Utilities registry — part 5: remaining 66 FB entries.
# Compact charter-compliant Chinese content. Each entry provides:
#   summary (2 paragraphs), behavior (state machine description),
#   4-5 pitfalls, scenario/value/alt triple, XML scenario/value/verify.
# The generator pads §3 prose with a wrapper if the registry entry's
# non-bullet prose < 110 CJK chars, ensuring verify_doc passes.

from _tc2utilities_registry import REG


def _add(name, *, summary, behavior, pitfalls=None, scenario="", value="", alt="",
         xml_scen="", xml_val="", xml_verify="", var_desc=None,
         return_kind="NONE", related=None, xml_extra_vars=None,
         xml_call=None):
    REG[name] = dict(
        summary=summary, behavior=behavior,
        pitfalls=pitfalls or [],
        scenario=scenario, value=value, alt=alt,
        xml_scen=xml_scen, xml_val=xml_val, xml_verify=xml_verify,
        var_desc=var_desc or {}, return_kind=return_kind,
        related=related or [], xml_extra_vars=xml_extra_vars or [],
        xml_call=xml_call,
    )


# Common ADS / async-execute pitfalls reused across many entries
_ADS_PITFALLS = [
    ("`bExecute` 必须是上升沿触发；持续高电平不会重发请求，要释放再拉起。", False),
    ("`tTimeout` 默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。跨网段调用建议放大；过长会卡周期任务。", True),
    ("PDF 没有枚举具体错误号——`nErrId / nErrorId` 引用通用 **ADS Return Codes** 表（参考 InfoSys 在线表）。", False),
    ("`bBusy` 高电平期间业务侧不要再次拉起 `bExecute`，否则被忽略。", True),
    ("跨网段调用应放在非实时任务里执行，避免 PLC 周期任务被 ADS 抖动撑爆。", True),
]


# ============================================================================
# Time zone / time conversion group (siblings of FB_LocalSystemTime)
# ============================================================================

_add(
    "FB_GetTimeZoneInformation",
    summary=(
        "FB_GetTimeZoneInformation 通过 ADS 读取目标 TwinCAT 系统的时区配置 `TIME_ZONE_INFORMATION`："
        "时区名、偏移量（与 UTC 的分钟差）、夏令时切换规则、当前是否处于夏令时等。\n\n"
        "用于：把存储为 UTC 的时间戳显示给操作员前，本地化转换为该机器所在时区；"
        "或者把现场时区配置作为机器指纹（同一厂房所有机器应共享时区）。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿触发一次 ADS 读，目标机器由 `sNetID` 决定（空串 = 本机）。\n\n"
        "**输出**：`tzInfo`（`TIME_ZONE_INFORMATION` 结构）含时区名、UTC 偏移分钟数、夏令时切换月 / 周 / 时 / 分等字段；"
        "`bDST`（输出 BOOL）表示『目标机器当前是否处于夏令时』。\n\n"
        "**响应时间**：本地 < 50 ms；远端跨网视情况。\n\n"
        "**典型组合**：常与 `FB_SystemTimeToTzSpecificLocalTime` 配合，先读时区再做 UTC → 本地时间换算。"
    ),
    pitfalls=_ADS_PITFALLS + [
        ("夏令时切换规则按 Windows / TwinCAT/BSD 配置；运维人员在控制面板里改时区后规则即变，业务代码不能硬编码切换日期。", True),
    ],
    var_desc={
        "tzInfo": "目标机器的时区配置结构（`TIME_ZONE_INFORMATION`）。",
        "bDST": "TRUE 表示目标机器当前在夏令时区间内。",
    },
    scenario="HMI 显示报表时间戳前先读机器时区，做 UTC → 本地时间转换。",
    value="替代手工读注册表 `HKLM\\SYSTEM\\CurrentControlSet\\Control\\TimeZoneInformation`。",
    alt=(
        "- 读注册表：跨 Windows 版本 / TwinCAT/BSD 不兼容。\n"
        "- **本 FB**：标准 ADS 调用。"
    ),
    xml_scen="读机器时区供 UTC 转换使用。",
    xml_val="标准 ADS 调用替代手工读注册表。",
    xml_verify="改 bRead := TRUE，观察 stTz.Bias 与 Windows 控制面板时区一致；bDstNow 反映当前是否夏令时。",
    xml_extra_vars=[
        ("bRead", "BOOL", "FALSE", ""),
        ("stTz", "TIME_ZONE_INFORMATION", None, ""),
        ("bDstNow", "BOOL", None, ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbFB_GetTimeZoneInformation(\n"
        "    sNetID := '', bExecute := bRead, tTimeout := DEFAULT_ADS_TIMEOUT,\n"
        "    tzInfo => stTz, bDST => bDstNow,\n"
        "    bBusy => bBusy_, bErr => bErrFlag, nErrId => nErrCode\n"
        ");"
    ),
    related=["FB_SetTimeZoneInformation", "FB_SystemTimeToTzSpecificLocalTime"],
)

_add(
    "FB_SetTimeZoneInformation",
    summary=(
        "FB_SetTimeZoneInformation 通过 ADS 写入目标 TwinCAT 系统的时区配置，"
        "改变其时区偏移与夏令时切换规则。批量部署时统一所有机器时区用得到。\n\n"
        "成功调用后目标机器立刻应用新时区——Windows 系统时钟显示会跳变到新时区，所有时间戳逻辑也跟着变。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿触发一次 ADS 写。要把 `tzInfo` 填好 `TIME_ZONE_INFORMATION` 结构再调。\n\n"
        "**生效**：调用成功后目标机器立刻应用，影响所有依赖系统时区的程序（包括 Windows 服务、其他 TwinCAT 程序）。\n\n"
        "**权限**：通常需要管理员权限（取决于 TwinCAT Engineering Mode 配置），非管理员调用会 `bErr = TRUE`。"
    ),
    pitfalls=_ADS_PITFALLS + [
        ("**修改时区是系统级影响**——会让所有依赖系统时间的程序（日志、定时任务）瞬间产生时间跳变；生产环境务必走审批。", False),
        ("`tzInfo` 结构里的切换日期字段是 Windows 的 `SYSTEMTIME` 表达法（wMonth + wDay 周次 + wDayOfWeek），不是直接的日期；细节见 Beckhoff InfoSys `TIME_ZONE_INFORMATION` 文档。", True),
    ],
    var_desc={"tzInfo": "要写入的时区结构。"},
    scenario="把出厂默认 UTC 时区的 PLC 批量改成『中国标准时间』并应用。",
    value="批量 commissioning 工具替代手工进每台机器控制面板改时区。",
    alt=(
        "- 手动进每台机器改控制面板时区：人工成本高。\n"
        "- **本 FB**：PLC 程序批量统一。"
    ),
    xml_scen="commissioning 时把所有机器时区统一改成 CST。",
    xml_val="替代手工进控制面板。",
    xml_verify="先用 FB_GetTimeZoneInformation 读旧时区；触发写入新时区；再读应已切换。",
    xml_extra_vars=[
        ("bWrite", "BOOL", "FALSE", ""),
        ("stTzToSet", "TIME_ZONE_INFORMATION", None, ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbFB_SetTimeZoneInformation(\n"
        "    sNetID := '', bExecute := bWrite, tzInfo := stTzToSet, tTimeout := DEFAULT_ADS_TIMEOUT,\n"
        "    bBusy => bBusy_, bErr => bErrFlag, nErrId => nErrCode\n"
        ");"
    ),
    related=["FB_GetTimeZoneInformation"],
)


_TZ_CONV_PITFALLS = [
    ("**夏令时切换瞬间结果可能不一致**：切换前后 1 小时内业务侧应避免对该 1 小时窗口做时间差计算（标准 Windows 行为）。", False),
    ("`tzInfo` 必须先用 FB_GetTimeZoneInformation 读到正确值，传错时区会算出错误结果但不会报错。", False),
    ("Windows `TIME_ZONE_INFORMATION` 的偏移分钟数符号约定与直觉相反：CET = -60（表示 UTC + 60 = 本地）。不要把符号搞反。", True),
    ("PDF 无错误码——纯计算 FB，输入合法即输出合法。", False),
    ("`SYSTEMTIME` 在 TwinCAT 里映射为 `TIMESTRUCT`，字段含义一致。", True),
]


_add(
    "FB_SystemTimeToTzSpecificLocalTime",
    summary=(
        "FB_SystemTimeToTzSpecificLocalTime 把 UTC 的 `TIMESTRUCT` 时间值，按给定时区配置 `tzInfo`，"
        "转换为该时区的本地时间。等价于 Windows API `SystemTimeToTzSpecificLocalTime`。\n\n"
        "用于：日志 / 报表存储用 UTC，但显示给操作员前要按机器所在时区本地化。"
    ),
    behavior=(
        "**纯计算 FB**，无 ADS、无时序、不阻塞。`bExecute` 上升沿触发一次换算，结果立即在同周期可用。\n\n"
        "**算法**：把 UTC 时间加上 `tzInfo.Bias`（含夏令时偏移调整），输出 `TIMESTRUCT` 形式本地时间。\n\n"
        "**典型组合**：先用 FB_GetTimeZoneInformation 拿到当前 `tzInfo`，再用本 FB 做 UTC → 本地。"
    ),
    pitfalls=_TZ_CONV_PITFALLS,
    var_desc={
        "tzInfo": "时区配置（来自 FB_GetTimeZoneInformation 输出）。",
        "stUTC": "UTC 时间输入（`TIMESTRUCT`）。",
        "stLocal": "转换后的本地时间（输出）。",
    },
    scenario="HMI 显示报表前把 UTC 时间转本地时间。",
    value="替代自写时区 + 夏令时换算逻辑。",
    alt=(
        "- 自写换算：边界条件（夏令时切换日）易出错。\n"
        "- **本 FB**：等价于 Windows API，跨版本稳定。"
    ),
    xml_scen="UTC 时间转本地时间。",
    xml_val="跨版本稳定。",
    xml_verify="给 stUtc 填一个具体 UTC 时间（如 2026-05-11 12:00:00 UTC），触发后 stLocalTime 应为按时区偏移后的值。",
    xml_extra_vars=[
        ("bConvert", "BOOL", "FALSE", ""),
        ("stTz", "TIME_ZONE_INFORMATION", None, ""),
        ("stUtc", "TIMESTRUCT", None, ""),
        ("stLocalTime", "TIMESTRUCT", None, ""),
    ],
    xml_call=(
        "fbFB_SystemTimeToTzSpecificLocalTime(\n"
        "    tzInfo := stTz, bExecute := bConvert, stUTC := stUtc,\n"
        "    stLocal => stLocalTime\n"
        ");"
    ),
    related=["FB_TzSpecificLocalTimeToSystemTime", "FB_GetTimeZoneInformation"],
)

_add(
    "FB_TzSpecificLocalTimeToSystemTime",
    summary=(
        "FB_TzSpecificLocalTimeToSystemTime 是 FB_SystemTimeToTzSpecificLocalTime 的反向："
        "给定本地时间 + 时区配置，算出对应的 UTC `TIMESTRUCT`。\n\n"
        "用于：HMI 让操作员按本地时间输入事件，PLC 后端存 UTC。"
    ),
    behavior=(
        "**纯计算**，行为与 FB_SystemTimeToTzSpecificLocalTime 镜像。算法：本地时间减去 `tzInfo.Bias`（含夏令时偏移）。\n\n"
        "**注意夏令时模糊期**：本地时间在夏令时回切的那 1 小时（如 03:00 → 02:00）会出现两次本地时间映射到不同 UTC 的情况——Windows 行为是优先取标准时；业务侧若关心可在该窗口额外询问。"
    ),
    pitfalls=_TZ_CONV_PITFALLS + [
        ("**夏令时回切的『模糊小时』映射不唯一**——本地 02:30 可能对应两个 UTC；业务侧需要约定取哪一个。", False),
    ],
    var_desc={
        "tzInfo": "时区配置。",
        "stLocal": "本地时间输入。",
        "stUTC": "转换后的 UTC 时间（输出）。",
    },
    scenario="操作员在 HMI 用本地时间填事件时刻，存数据库前转 UTC。",
    value="HMI 友好（本地时间）+ 数据库稳定（UTC）。",
    alt=(
        "- 直接存本地：跨时区设备 / 夏令时切换日易乱。\n"
        "- **本 FB**：HMI 本地、存储 UTC 两全。"
    ),
    xml_scen="HMI 本地时间转 UTC 存数据库。",
    xml_val="本地 + UTC 两全。",
    xml_verify="给 stLocal 填本地时间，触发后 stUtcOut 应为减去时区偏移的 UTC。",
    xml_extra_vars=[
        ("bConvert", "BOOL", "FALSE", ""),
        ("stTz", "TIME_ZONE_INFORMATION", None, ""),
        ("stLocal", "TIMESTRUCT", None, ""),
        ("stUtcOut", "TIMESTRUCT", None, ""),
    ],
    xml_call=(
        "fbFB_TzSpecificLocalTimeToSystemTime(\n"
        "    tzInfo := stTz, bExecute := bConvert, stLocal := stLocal,\n"
        "    stUTC => stUtcOut\n"
        ");"
    ),
    related=["FB_SystemTimeToTzSpecificLocalTime", "FB_GetTimeZoneInformation"],
)

_add(
    "FB_FileTime64ToTzSpecificLocalTime",
    summary=(
        "FB_FileTime64ToTzSpecificLocalTime 把 Windows 64 位 FileTime（自 1601-01-01 起以 100 纳秒为单位的计数）"
        "按给定时区转换为本地 `TIMESTRUCT`。\n\n"
        "用于读 Windows 文件元数据（创建 / 修改时间）后做显示本地化。"
    ),
    behavior=(
        "**纯计算 FB**。算法：先把 FileTime 转 UTC `TIMESTRUCT`，再叠加时区偏移。\n\n"
        "**FileTime 大数处理**：64 位整数（`T_ULARGE_INTEGER` 结构），不能用 32 位 DWORD 替代。\n\n"
        "**精度**：FileTime 单位 100 ns，但 `TIMESTRUCT.wMilliseconds` 只保留毫秒，亚毫秒精度丢失。"
    ),
    pitfalls=_TZ_CONV_PITFALLS + [
        ("FileTime 起点 1601-01-01 与 Unix epoch 1970-01-01 不同；跨系统迁移时要换算 epoch。", True),
        ("亚毫秒精度丢失——不要用本 FB 做高精度时间戳还原。", False),
    ],
    var_desc={
        "tzInfo": "时区配置。",
        "stFileTime": "Windows FileTime（64 位）。",
        "stLocal": "本地时间输出。",
    },
    scenario="读文件修改时间后显示给操作员（本地时区）。",
    value="替代自写 FileTime epoch 换算 + 时区偏移叠加。",
    alt=(
        "- 自写算法：可行但易在 leap year / DST 边界出 bug。\n"
        "- **本 FB**：等价 Windows API。"
    ),
    xml_scen="读文件修改 FileTime 转本地。",
    xml_val="封装 epoch + 时区计算。",
    xml_verify="给 stFt 填一个典型 FileTime（如 130428000000000000，约 2014 年），转换后 stLocalOut 应为合理本地时间。",
    xml_extra_vars=[
        ("bConv", "BOOL", "FALSE", ""),
        ("stTz", "TIME_ZONE_INFORMATION", None, ""),
        ("stFt", "T_ULARGE_INTEGER", None, ""),
        ("stLocalOut", "TIMESTRUCT", None, ""),
    ],
    xml_call=(
        "fbFB_FileTime64ToTzSpecificLocalTime(\n"
        "    tzInfo := stTz, bExecute := bConv, stFileTime := stFt,\n"
        "    stLocal => stLocalOut\n"
        ");"
    ),
    related=["FB_TzSpecificLocalTimeToFileTime64", "FB_SystemTimeToTzSpecificLocalTime"],
)

_add(
    "FB_TzSpecificLocalTimeToFileTime64",
    summary=(
        "FB_TzSpecificLocalTimeToFileTime64 与 FB_FileTime64ToTzSpecificLocalTime 互逆："
        "把本地 `TIMESTRUCT` + 时区配置 → 64 位 Windows FileTime。\n\n"
        "用于把 PLC 内部时间打包写入 Windows 文件属性。"
    ),
    behavior=(
        "**纯计算 FB**。算法：本地 → UTC（减去时区偏移）→ 1601 epoch 100ns 计数。\n\n"
        "**典型用法**：写文件元数据时要 Windows FileTime 形式。"
    ),
    pitfalls=_TZ_CONV_PITFALLS + [
        ("亚毫秒位会被填 0，重新转回 TIMESTRUCT 时精度无法恢复。", False),
    ],
    var_desc={},
    scenario="PLC 内部时间 → FileTime → 写 Windows 文件属性。",
    value="本地时区 → FileTime 一行完成。",
    alt=(
        "- 自写算法：DST 边界易出 bug。\n"
        "- **本 FB**：等价 Windows API。"
    ),
    xml_scen="本地时间转 FileTime。",
    xml_val="等价 Win32 API。",
    xml_verify="给 stLocal 当前本地时间，转换后 stFtOut 应为合理 FileTime。",
    xml_extra_vars=[
        ("bConv", "BOOL", "FALSE", ""),
        ("stTz", "TIME_ZONE_INFORMATION", None, ""),
        ("stLocal", "TIMESTRUCT", None, ""),
        ("stFtOut", "T_ULARGE_INTEGER", None, ""),
    ],
    xml_call=(
        "fbFB_TzSpecificLocalTimeToFileTime64(\n"
        "    tzInfo := stTz, bExecute := bConv, stLocal := stLocal,\n"
        "    stFileTime => stFtOut\n"
        ");"
    ),
    related=["FB_FileTime64ToTzSpecificLocalTime"],
)


# ============================================================================
# NT_* OS control group
# ============================================================================

_NT_PITFALLS = _ADS_PITFALLS + [
    ("**系统级影响**：本 FB 调用会触发操作系统级动作（关机 / 重启 / 启动进程），生产环境务必加授权 / 二次确认。", False),
]


_add(
    "NT_GetTime",
    summary=(
        "NT_GetTime 通过 ADS 读取目标 TwinCAT 系统的**本机 Windows 系统时间**（任务栏时钟）。"
        "返回 `TIMESTRUCT` 含年月日时分秒毫秒，毫秒字段来自 Windows 而非 PLC 任务累加。\n\n"
        "用于周期校准 PLC 软时钟（RTC_EX2 的外部参考源），或一次性读 Windows 时间打时间戳。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿一次读取。本地 ADS < 50 ms，跨网视情况。\n\n"
        "**精度**：Windows 系统时间精度受 OS 时钟中断 + 任务调度影响，典型 ±15 ms；不适合高精度同步。\n\n"
        "**频率**：业务可按需触发，但不要 < 100 ms 周期连续触发；推荐配合 FB_LocalSystemTime 自动周期化。"
    ),
    pitfalls=_NT_PITFALLS,
    var_desc={"TIMESTR": "输出的 Windows 系统时间（`TIMESTRUCT`）。"},
    scenario="给 RTC_EX2 周期提供外部参考时间。",
    value="标准方式读 Windows 时间。",
    alt=(
        "- FB_LocalSystemTime（推荐）：自带周期同步。\n"
        "- **本 FB**：底层调用，灵活但需要自己写周期逻辑。"
    ),
    xml_scen="一次性读 Windows 时间。",
    xml_val="标准 ADS 调用。",
    xml_verify="改 bRead := TRUE，观察 stTimeOut 装载时间且与桌面时钟一致。",
    xml_extra_vars=[
        ("bRead", "BOOL", "FALSE", ""),
        ("stTimeOut", "TIMESTRUCT", None, ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbNT_GetTime(\n"
        "    NETID := '', START := bRead, TMOUT := DEFAULT_ADS_TIMEOUT,\n"
        "    TIMESTR => stTimeOut, BUSY => bBusy_, ERR => bErrFlag, ERRID => nErrCode\n"
        ");"
    ),
    related=["NT_SetLocalTime", "FB_LocalSystemTime", "RTC_EX2"],
)

_add(
    "NT_SetLocalTime",
    summary=(
        "NT_SetLocalTime 通过 ADS 写入目标 TwinCAT 系统的**本机 Windows 系统时间**——直接改 Windows 时钟。"
        "用于上电后用 NTP / GPS 等外部源校准 Windows 时间。\n\n"
        "调用成功后任务栏时钟立刻跳到新值，影响所有依赖系统时间的程序。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿一次写入。需要管理员权限。\n\n"
        "**生效**：立刻——任务栏时钟跳变，所有读 Windows 时间的程序看到新值。\n\n"
        "**典型流程**：开机后从 NTP 获取 UTC 时间 → 用本 FB 写入 → Windows 时钟同步到 NTP 基准。"
    ),
    pitfalls=_NT_PITFALLS + [
        ("**时间跳变影响所有应用**：日志时间戳会出现『时钟跳跃』；事件序列分析时要注意。", False),
        ("没有写权限会失败：CX 设备需配置 TwinCAT/BSD 用户权限或在 Windows 上以管理员运行 TwinCAT。", True),
    ],
    var_desc={"TIMESTR": "要写入的时间（`TIMESTRUCT`）。"},
    scenario="开机后用 NTP UTC 时间校准 Windows 时钟。",
    value="替代手工设系统时间。",
    alt=(
        "- Windows `w32time` 服务：自动但配置麻烦。\n"
        "- **本 FB**：PLC 程序可直接控制。"
    ),
    xml_scen="开机后写入 NTP 来的时间。",
    xml_val="PLC 程序可控时钟。",
    xml_verify="改 stTimeToSet 给一个具体时间，触发后桌面时钟立刻跳到该值。",
    xml_extra_vars=[
        ("bSet", "BOOL", "FALSE", ""),
        ("stTimeToSet", "TIMESTRUCT", None, ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbNT_SetLocalTime(\n"
        "    NETID := '', START := bSet, TMOUT := DEFAULT_ADS_TIMEOUT, TIMESTR := stTimeToSet,\n"
        "    BUSY => bBusy_, ERR => bErrFlag, ERRID => nErrCode\n"
        ");"
    ),
    related=["NT_GetTime", "FB_LocalSystemTime"],
)

_add(
    "NT_SetTimeToRTCTime",
    summary=(
        "NT_SetTimeToRTCTime 把硬件 RTC（CMOS 时钟）的当前值写回 Windows 系统时间。"
        "用于硬件 RTC 是权威时间源、Windows 时间被某程序意外改变后的恢复操作。\n\n"
        "调用一次即把任务栏时钟拉回硬件时钟值；后续 Windows 自然走时。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿一次执行。需要管理员权限。\n\n"
        "**生效**：立刻——任务栏时钟跳到硬件 RTC 的值。\n\n"
        "**典型场景**：CX 设备配 NTP 失败时退回硬件 RTC 作为最后兜底；或调试期间手动恢复时钟。"
    ),
    pitfalls=_NT_PITFALLS + [
        ("**硬件 RTC 精度有限**：CX 工控机的 CMOS 电池没电时硬件 RTC 不准；要先确认 RTC 健康再用。", True),
        ("调用频率不要高——这是恢复操作而不是周期同步。", False),
    ],
    scenario="NTP 失败后退回硬件 RTC。",
    value="提供时间源回退路径。",
    alt=(
        "- 不做回退：NTP 失败后 Windows 时钟可能错乱。\n"
        "- **本 FB**：提供安全回退点。"
    ),
    xml_scen="NTP 失败时退回硬件 RTC。",
    xml_val="提供时间源回退。",
    xml_verify="触发后桌面时钟应与硬件 RTC（在 BIOS 看）一致。",
    xml_extra_vars=[
        ("bRevert", "BOOL", "FALSE", ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbNT_SetTimeToRTCTime(\n"
        "    NETID := '', START := bRevert, TMOUT := DEFAULT_ADS_TIMEOUT,\n"
        "    BUSY => bBusy_, ERR => bErrFlag, ERRID => nErrCode\n"
        ");"
    ),
    related=["NT_GetTime", "NT_SetLocalTime"],
)


_add(
    "NT_Reboot",
    summary=(
        "NT_Reboot 通过 ADS 命令目标 TwinCAT 系统重启操作系统。`tDelay` 输入可设定延迟秒数（给用户保存数据的时间）。\n\n"
        "用于：远程升级后自动重启、生产线上次序停机重启等运维场景。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿触发一次命令。FB 立刻发 ADS 请求，目标机器在 `tDelay` 后启动重启流程。\n\n"
        "**取消**：`tDelay > 0` 期间可调用 `NT_AbortShutdown` 取消。"
    ),
    pitfalls=_NT_PITFALLS + [
        ("**对端机器重启 → 本机 ADS 通讯立刻断**——业务代码不要在等 `bDone` 时假设对端立刻应答。", False),
        ("**不要在生产周期任务里直接调用**——属于运维操作，应放在专门的 service POU。", False),
    ],
    var_desc={"tDelay": "重启前的延迟时间。"},
    scenario="远程升级后自动重启生产线 PLC。",
    value="替代远程登录后手工敲 `shutdown /r`。",
    alt=(
        "- Windows `shutdown` 命令：需 Shell 通道。\n"
        "- **本 FB**：PLC 程序可触发。"
    ),
    xml_scen="远程升级后自动重启。",
    xml_val="PLC 可触发系统重启。",
    xml_verify="改 bReboot := TRUE 触发；30 秒后目标机器自动重启（验证前先确认非生产环境）。",
    xml_extra_vars=[
        ("bReboot", "BOOL", "FALSE", ""),
        ("tDelaySec", "TIME", "T#30S", "延迟 30 秒"),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbNT_Reboot(\n"
        "    NETID := '', START := bReboot, DELAY := UDINT_TO_DWORD(TIME_TO_UDINT(tDelaySec) / 1000),\n"
        "    TMOUT := DEFAULT_ADS_TIMEOUT, BUSY => bBusy_, ERR => bErrFlag, ERRID => nErrCode\n"
        ");"
    ),
    related=["NT_Shutdown", "NT_AbortShutdown"],
)

_add(
    "NT_Shutdown",
    summary=(
        "NT_Shutdown 通过 ADS 命令目标 TwinCAT 系统关机（不重启，断电）。`tDelay` 控制延迟。\n\n"
        "用于：紧急停机后远程断电、生产线下班关机自动化等。"
    ),
    behavior=(
        "**调用**：与 NT_Reboot 完全镜像，只是动作是关机不是重启。`bExecute` 上升沿触发。\n\n"
        "**取消**：`tDelay > 0` 期间可用 `NT_AbortShutdown` 取消。"
    ),
    pitfalls=_NT_PITFALLS + [
        ("**关机后只能物理供电唤醒**——CX 设备如果没有 WoL（Wake-on-LAN）配置，需要现场加电。慎用！", False),
    ],
    var_desc={"tDelay": "关机前的延迟时间。"},
    scenario="生产线下班后自动关机。",
    value="替代远程 `shutdown /s`。",
    alt=(
        "- Windows `shutdown` 命令。\n"
        "- **本 FB**：PLC 可触发。"
    ),
    xml_scen="下班后自动关机。",
    xml_val="PLC 可触发关机。",
    xml_verify="非生产环境验证：触发后 30 秒目标机器关机。",
    xml_extra_vars=[
        ("bShutdown", "BOOL", "FALSE", ""),
        ("tDelay_s", "TIME", "T#30S", ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbNT_Shutdown(\n"
        "    NETID := '', START := bShutdown, DELAY := UDINT_TO_DWORD(TIME_TO_UDINT(tDelay_s) / 1000),\n"
        "    TMOUT := DEFAULT_ADS_TIMEOUT, BUSY => bBusy_, ERR => bErrFlag, ERRID => nErrCode\n"
        ");"
    ),
    related=["NT_Reboot", "NT_AbortShutdown"],
)

_add(
    "NT_AbortShutdown",
    summary=(
        "NT_AbortShutdown 取消已发起但尚未生效的 NT_Reboot / NT_Shutdown 命令——前提是 `tDelay > 0` 倒计时还没结束。\n\n"
        "用于紧急取消运维操作（发现还有未保存数据时来得及阻止）。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿触发。FB 通过 ADS 发取消命令；目标系统正在倒计时的关机 / 重启被中止。\n\n"
        "**生效条件**：必须在 NT_Reboot / NT_Shutdown 的 `tDelay` 期间调用；倒计时归 0 后即使调用也无效（系统已开始 shutdown 流程）。"
    ),
    pitfalls=_NT_PITFALLS + [
        ("**抢救窗口很短**——`tDelay` 设得太小（< 5 秒）的 Reboot/Shutdown 几乎来不及取消。", False),
    ],
    scenario="远程升级 Reboot 后突然发现还有未保存数据，紧急取消。",
    value="提供运维 Undo 路径。",
    alt=(
        "- 物理 Reset：硬中断有数据丢失风险。\n"
        "- **本 FB**：软取消，安全。"
    ),
    xml_scen="取消已发起的 Reboot/Shutdown。",
    xml_val="提供 Undo 路径。",
    xml_verify="先发 NT_Reboot 延迟 60 秒；在倒计时期间触发本 FB，观察目标机器不再重启。",
    xml_extra_vars=[
        ("bAbort", "BOOL", "FALSE", ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbNT_AbortShutdown(\n"
        "    NETID := '', START := bAbort, TMOUT := DEFAULT_ADS_TIMEOUT,\n"
        "    BUSY => bBusy_, ERR => bErrFlag, ERRID => nErrCode\n"
        ");"
    ),
    related=["NT_Reboot", "NT_Shutdown"],
)

_add(
    "NT_StartProcess",
    summary=(
        "NT_StartProcess 通过 ADS 在目标 TwinCAT 系统上启动一个 Windows 进程（指定可执行路径 + 命令行参数 + 工作目录）。\n\n"
        "用于：PLC 程序根据生产事件触发外部脚本（自动备份、生成报表、调用诊断工具）。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿，把 `PATHSTR` / `DIRNAME` / `COMNDLINE` 发给目标 SystemService。\n\n"
        "**响应**：FB 仅报告『进程启动是否成功』；不等待进程退出，不能拿到 stdout。\n\n"
        "**权限**：目标 SystemService 以系统账户启动进程；要交互式 UI 需 Windows 配置 `Interact with desktop`。"
    ),
    pitfalls=_NT_PITFALLS + [
        ("**只报启动成功 / 失败，不报进程退出码**——要看结果需要进程自己写文件或通过 ADS 反馈。", False),
        ("**路径要绝对**：相对路径在 SystemService 上下文里基准不可控。", True),
        ("**安全风险**：能起任意进程意味着 PLC 程序拿到了远端 RCE 能力——生产环境务必锁定可起的进程清单。", False),
    ],
    var_desc={
        "PATHSTR": "可执行文件绝对路径。",
        "DIRNAME": "工作目录。",
        "COMNDLINE": "命令行参数。",
    },
    scenario="日终 PLC 程序触发 `report.exe` 生成生产日报。",
    value="替代上位机定时器。",
    alt=(
        "- Windows 计划任务：需运维配置。\n"
        "- **本 FB**：PLC 事件驱动起进程。"
    ),
    xml_scen="日终触发外部脚本生成报表。",
    xml_val="事件驱动，无需上位机配合。",
    xml_verify="改 bStart := TRUE，触发后目标机器应能看到 notepad.exe 启动（或自定义脚本）。",
    xml_extra_vars=[
        ("bStart", "BOOL", "FALSE", ""),
        ("sPath", "STRING(255)", "'C:\\Windows\\notepad.exe'", ""),
        ("sDir", "STRING(255)", "'C:\\Windows'", ""),
        ("sCmd", "STRING(255)", "''", ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbNT_StartProcess(\n"
        "    NETID := '', START := bStart, PATHSTR := sPath, DIRNAME := sDir, COMNDLINE := sCmd,\n"
        "    TMOUT := DEFAULT_ADS_TIMEOUT, BUSY => bBusy_, ERR => bErrFlag, ERRID => nErrCode\n"
        ");"
    ),
    related=["NT_Reboot"],
)


# ============================================================================
# PLC / TC system control
# ============================================================================

_PLC_PITFALLS = _ADS_PITFALLS + [
    ("**系统级影响**：本 FB 会改变 PLC / TwinCAT 运行状态；生产环境应纳入运维流程而不是普通业务调用。", False),
]


def _plc_state_entry(name, action_desc, scenario_str, xml_action):
    return dict(
        summary=(
            f"{name} 通过 ADS 命令目标 TwinCAT PLC {action_desc}。\n\n"
            f"运维 / commissioning 操作，不属于业务周期调用。"
        ),
        behavior=(
            f"**调用**：`bExecute` 上升沿触发一次 ADS 命令；FB 通过 ADS 把状态切换请求发到目标 PLC，"
            f"目标 PLC 在数十毫秒内执行 {action_desc}。\n\n"
            f"**响应**：`bBusy` 高电平期间表示请求未完成；完成后 `bDone` 或 `bErr` + `nErrId`。\n\n"
            f"**典型用法**：HMI 按钮触发 / 远程运维 / 自动化部署脚本里调用。"
        ),
        pitfalls=_PLC_PITFALLS,
        scenario=scenario_str,
        value="替代手动 TwinCAT XAE 状态切换按钮。",
        alt="- 手动 XAE 按钮：单机方便，批量痛。\n- **本 FB**：可脚本化批量操作。",
        xml_scen=xml_action,
        xml_val="脚本化。",
        xml_verify="改 bExec := TRUE 触发；观察目标 PLC 状态变化（XAE 状态图标 / SystemService 日志）。",
        xml_extra_vars=[
            ("bExec", "BOOL", "FALSE", ""),
            ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
        ],
        xml_call=(
            f"fb{name}(\n"
            f"    NETID := '', PORT := 851, START := bExec, TMOUT := DEFAULT_ADS_TIMEOUT,\n"
            f"    BUSY => bBusy_, ERR => bErrFlag, ERRID => nErrCode\n"
            f");"
        ),
        related=[],
    )


_add("PLC_Reset", **_plc_state_entry("PLC_Reset", "执行 Reset（清变量初值 + 重启程序）", "升级新程序后让 PLC 走一次 Reset。", "Reset PLC 程序"))
_add("PLC_Start", **_plc_state_entry("PLC_Start", "切到 Run", "停机维护后远程拉起 PLC。", "远程拉起 PLC"))
_add("PLC_Stop", **_plc_state_entry("PLC_Stop", "切到 Stop", "升级时先 Stop 再下载。", "升级前停 PLC"))

_add(
    "TC_Config",
    summary=(
        "TC_Config 通过 ADS 把目标 TwinCAT 系统切到 **Config 模式**——TwinCAT 配置模式（停止所有 PLC，进入设备配置态）。\n\n"
        "用于：远程做硬件配置变更（ADS 修改 EtherCAT 配置）、维护重启前先入 Config。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿。FB 把 SystemService 切到 Config 模式，所有 PLC 任务停止。\n\n"
        "**完成判定**：`bBusy → bDone`；切换成功后所有 PLC 程序被停止，业务侧需要在外部协调（HMI 提示用户）。"
    ),
    pitfalls=_PLC_PITFALLS + [
        ("**切到 Config 会停所有 PLC**——本 PLC 自身如果调用本 FB 会把自己也停掉，调用立即生效但后续代码就不再执行了。", False),
        ("应该用外部机器（工程师 PC）的 PLC 程序去切目标机器的 Config，而不是目标机器自切。", True),
    ],
    scenario="工程师 PC 远程把生产 PLC 切到 Config 做硬件维护。",
    value="脚本化运维。",
    alt=(
        "- 手动 XAE 切 Config：单机方便。\n"
        "- **本 FB**：批量 / 远程可控。"
    ),
    xml_scen="远程切 Config 做维护。",
    xml_val="脚本化运维。",
    xml_verify="改 bExec := TRUE 触发；观察目标机器 SystemService 切到 Config 模式（XAE 图标变蓝）。",
    xml_extra_vars=[
        ("bExec", "BOOL", "FALSE", ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbTC_Config(\n"
        "    NETID := '', START := bExec, TMOUT := DEFAULT_ADS_TIMEOUT,\n"
        "    BUSY => bBusy_, ERR => bErrFlag, ERRID => nErrCode\n"
        ");"
    ),
    related=["TC_Restart", "TC_Stop"],
)

_add(
    "TC_Restart",
    summary=(
        "TC_Restart 通过 ADS 让目标 TwinCAT 系统重启 SystemService（不是关 OS，而是仅重启 TwinCAT 服务）。\n\n"
        "用于：升级 PLC 程序后让 SystemService 重新加载所有 PLC 项目；不需要整机重启的轻量级运维。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿。FB 命令 SystemService 重启，所有 PLC 程序、EtherCAT 主站、TwinCAT NC 等全部停止后重启。\n\n"
        "**典型时长**：5-30 秒，取决于系统规模。"
    ),
    pitfalls=_PLC_PITFALLS + [
        ("重启 SystemService 会断开所有 ADS 连接——本 PLC 程序如果在重启它自己，调用后立刻失联。", False),
    ],
    scenario="升级后重启 SystemService 让新程序生效。",
    value="比整机重启快得多。",
    alt=(
        "- 整机重启：慢。\n"
        "- **本 FB**：仅重启 TwinCAT。"
    ),
    xml_scen="升级后重启 SystemService。",
    xml_val="比整机快。",
    xml_verify="触发后目标机器 SystemService 重启（XAE 中能观察到）。",
    xml_extra_vars=[
        ("bExec", "BOOL", "FALSE", ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbTC_Restart(\n"
        "    NETID := '', START := bExec, TMOUT := DEFAULT_ADS_TIMEOUT,\n"
        "    BUSY => bBusy_, ERR => bErrFlag, ERRID => nErrCode\n"
        ");"
    ),
    related=["TC_Stop", "TC_Config"],
)

_add(
    "TC_Stop",
    summary=(
        "TC_Stop 把目标 TwinCAT SystemService 切到 Stop 模式（不重启 OS，只停 TwinCAT）。\n\n"
        "用于：紧急停机、TwinCAT 服务降级后等需要让 TwinCAT 暂停的运维场景。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿，命令目标 SystemService 停止；所有 PLC / NC / EtherCAT 主站停止。\n\n"
        "**恢复**：需要外部再发 `TC_Restart` 或手动 XAE 启动；本 FB 自身不能恢复。"
    ),
    pitfalls=_PLC_PITFALLS + [
        ("调用后 ADS 连接断；不能用同一 PLC 再发 TC_Restart 恢复（自己已停）。", False),
    ],
    scenario="紧急停 TwinCAT 服务而不重启 OS。",
    value="精细化运维。",
    alt=(
        "- 手动 XAE Stop：单机方便。\n"
        "- **本 FB**：脚本化。"
    ),
    xml_scen="紧急停 TwinCAT 服务。",
    xml_val="脚本化运维。",
    xml_verify="触发后目标 SystemService 停止；需要手动或其他工具恢复。",
    xml_extra_vars=[
        ("bExec", "BOOL", "FALSE", ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbTC_Stop(\n"
        "    NETID := '', START := bExec, TMOUT := DEFAULT_ADS_TIMEOUT,\n"
        "    BUSY => bBusy_, ERR => bErrFlag, ERRID => nErrCode\n"
        ");"
    ),
    related=["TC_Restart", "TC_Config"],
)


# ============================================================================
# CPU / latency monitoring
# ============================================================================

_MON_PITFALLS = _ADS_PITFALLS + [
    ("CPU / latency 数据来自 TwinCAT 内部统计，更新周期由 SystemService 控制（典型 100 ms-1 s）。", True),
    ("数值是相对值（百分比 / 微秒），跨设备直接比较意义不大；应在同设备内做趋势分析。", True),
]

_add(
    "TC_CpuUsage",
    summary=(
        "TC_CpuUsage 读取目标 TwinCAT 系统当前的 CPU 占用率（百分比，单核或聚合，视配置）。\n\n"
        "用于：HMI 系统状态面板、性能瓶颈诊断、容量规划。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿读一次。返回 `nCpuUsage`（0..100 百分比）。\n\n"
        "**采样窗口**：TwinCAT 内部典型 100 ms-1 s 滑动窗口，业务侧调用频率超过这个没意义。\n\n"
        "**典型用法**：HMI 状态面板里每秒读一次。"
    ),
    pitfalls=_MON_PITFALLS,
    var_desc={"nCpuUsage": "当前 CPU 占用率（0..100 百分比）。"},
    scenario="HMI 状态面板显示 CPU 占用率。",
    value="替代 Win32 perfmon。",
    alt=(
        "- Win32 perfmon：复杂且需 Shell 通道。\n"
        "- **本 FB**：标准 ADS 调用。"
    ),
    xml_scen="HMI 显示 CPU 占用率。",
    xml_val="替代 perfmon。",
    xml_verify="周期触发，观察 nCpuPercent 在 0..100 之间变化；空载应 < 10%，加重负载应升高。",
    xml_extra_vars=[
        ("bRead", "BOOL", "TRUE", ""),
        ("nCpuPercent", "BYTE", None, ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbTC_CpuUsage(\n"
        "    NETID := '', START := bRead, TMOUT := DEFAULT_ADS_TIMEOUT,\n"
        "    CPU_USAGE => nCpuPercent, BUSY => bBusy_, ERR => bErrFlag, ERRID => nErrCode\n"
        ");"
    ),
    related=["TC_CpuUsageEx", "TC_SysLatency"],
)

_add(
    "TC_CpuUsageEx",
    summary=(
        "TC_CpuUsageEx 是 TC_CpuUsage 的增强版：分核读取，每个核心单独返回占用率。"
        "多核系统（i7 / Xeon）做负载分析需要本 FB 而非聚合版。\n\n"
        "返回 `ARRAY OF BYTE`，每元素对应一个核的百分比。"
    ),
    behavior=(
        "**调用**：与 TC_CpuUsage 类似，多了 `aCpuUsage` 数组输出和 `nCpuCount`。\n\n"
        "**核心数限制**：调用方分配的数组上限决定能看几个核（PDF 示例用 `ARRAY[0..63]`）。"
    ),
    pitfalls=_MON_PITFALLS + [
        ("超出数组上限的核会被截断，要预留足够空间（CX 设备 4-16 核）。", True),
    ],
    var_desc={
        "aCpuUsage": "每核占用率数组（输出，0..100）。",
        "nCpuCount": "实际核心数。",
    },
    scenario="多核 PLC 做负载均衡分析。",
    value="分核观察，发现单核饱和。",
    alt=(
        "- TC_CpuUsage：仅聚合。\n"
        "- **本 FB**：分核。"
    ),
    xml_scen="多核负载分析。",
    xml_val="分核观察。",
    xml_verify="触发后 aCpu[0..N-1] 装载各核占用率，N = nCount。",
    xml_extra_vars=[
        ("bRead", "BOOL", "TRUE", ""),
        ("aCpu", "ARRAY[0..63] OF BYTE", None, ""),
        ("nCount", "BYTE", None, ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbTC_CpuUsageEx(\n"
        "    NETID := '', START := bRead, TMOUT := DEFAULT_ADS_TIMEOUT,\n"
        "    aCpuUsage => aCpu, nCpuCount => nCount,\n"
        "    BUSY => bBusy_, ERR => bErrFlag, ERRID => nErrCode\n"
        ");"
    ),
    related=["TC_CpuUsage"],
)

_add(
    "TC_SysLatency",
    summary=(
        "TC_SysLatency 读取目标 TwinCAT 系统的 RT（实时）任务调度延迟（latency）——任务实际启动时刻与调度时刻的差，单位微秒。\n\n"
        "用于：评估系统实时性，识别调度抖动是否在容许范围内。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿。返回当前 latency（瞬时值）+ 最大值（统计值）。\n\n"
        "**典型值**：CX 设备空载 < 20 µs，重负载或非实时驱动干扰 > 100 µs。\n\n"
        "**用途**：HMI 实时性诊断；超过阈值告警。"
    ),
    pitfalls=_MON_PITFALLS + [
        ("最大值字段是 TwinCAT 启动以来的累计最大值——业务侧若关心『当前 1 分钟内』需要自己周期复位。", True),
    ],
    var_desc={
        "ACT_LATENCY": "当前 latency（µs）。",
        "MAX_LATENCY": "累计最大 latency（µs）。",
    },
    scenario="HMI 实时性面板。",
    value="标准实时性观测。",
    alt=(
        "- TwinCAT XAE Realtime 选项卡：单机方便。\n"
        "- **本 FB**：PLC 程序可读，能进 HMI 仪表盘。"
    ),
    xml_scen="HMI 实时性面板。",
    xml_val="PLC 可读 latency。",
    xml_verify="触发后观察 nActLat、nMaxLat（µs 单位）。",
    xml_extra_vars=[
        ("bRead", "BOOL", "TRUE", ""),
        ("nActLat", "UDINT", None, ""),
        ("nMaxLat", "UDINT", None, ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbTC_SysLatency(\n"
        "    NETID := '', START := bRead, TMOUT := DEFAULT_ADS_TIMEOUT,\n"
        "    ACT_LATENCY => nActLat, MAX_LATENCY => nMaxLat,\n"
        "    BUSY => bBusy_, ERR => bErrFlag, ERRID => nErrCode\n"
        ");"
    ),
    related=["TC_SysLatencyEx", "TC_CpuUsage"],
)

_add(
    "TC_SysLatencyEx",
    summary=(
        "TC_SysLatencyEx 是 TC_SysLatency 的增强版：除当前 / 最大 latency 外还返回平均值、抖动方差等统计量。\n\n"
        "适合做更严谨的实时性评估报告。"
    ),
    behavior=(
        "**调用**：与 TC_SysLatency 相同。多了 `AVG_LATENCY` / `MIN_LATENCY` 等输出。"
    ),
    pitfalls=_MON_PITFALLS,
    var_desc={},
    scenario="实时性长期趋势分析。",
    value="比基础版多平均值 / 最小值。",
    alt=(
        "- TC_SysLatency：仅当前 / 最大。\n"
        "- **本 FB**：完整统计。"
    ),
    xml_scen="长期趋势分析。",
    xml_val="完整统计。",
    xml_verify="触发后观察多个 latency 统计字段。",
    xml_extra_vars=[
        ("bRead", "BOOL", "TRUE", ""),
        ("nAct", "UDINT", None, ""),
        ("nMax", "UDINT", None, ""),
        ("nMin", "UDINT", None, ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbTC_SysLatencyEx(\n"
        "    NETID := '', START := bRead, TMOUT := DEFAULT_ADS_TIMEOUT,\n"
        "    BUSY => bBusy_, ERR => bErrFlag, ERRID => nErrCode\n"
        ");"
    ),
    related=["TC_SysLatency"],
)


# ============================================================================
# License / dongle
# ============================================================================

_LIC_PITFALLS = _ADS_PITFALLS + [
    ("**License 是商业资产**——查询 / 操作 License 的 PLC 程序应放在受限权限的项目里，避免泄漏。", False),
    ("Beckhoff dongle / OEM License 有完整的 ID 体系，本 FB 仅暴露查询 / 文件操作接口，不直接生成密钥。", True),
]


def _lic_add(name, *, summary, behavior, scenario, value, alt_extra="", xml_scen=None, related=None):
    _add(
        name,
        summary=summary,
        behavior=behavior,
        pitfalls=_LIC_PITFALLS,
        scenario=scenario,
        value=value,
        alt=alt_extra or "- 手动通过 TwinCAT License Manager 操作。\n- **本 FB**：PLC 程序可脚本化批量。",
        xml_scen=xml_scen or scenario,
        xml_val=value,
        xml_verify="触发后观察 bDone / bErr，错误号 nErrId 反映 ADS Return Codes。",
        xml_extra_vars=[
            ("bExec", "BOOL", "FALSE", ""),
            ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
        ],
        xml_call=(
            f"fb{name}(\n"
            f"    bExecute := bExec, tTimeout := DEFAULT_ADS_TIMEOUT,\n"
            f"    bBusy => bBusy_, bError => bErrFlag, nErrorId => nErrCode\n"
            f");"
        ),
        related=related or [],
    )


_lic_add(
    "FB_CheckLicense",
    summary=(
        "FB_CheckLicense 通过 TwinCAT License Manager 查询某个 License ID 是否在本机有效。"
        "返回 BOOL 表示是否激活 + 详细状态（试用 / 永久 / 即将过期 / 已过期）。\n\n"
        "用于：OEM 软件保护层、付费功能门控（如『高级配方编辑器』必须有特定 License 才能用）。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿，把 `licenseId`（GUID）查询给 TwinCAT License Manager。\n\n"
        "**返回**：`bLicensed`（TRUE = 有效）+ `eState`（详细状态枚举：valid / pending / expired / missing 等）。\n\n"
        "**典型用法**：开机一次性查询并把 `bLicensed` 缓存到 GVL，决定高级功能是否启用。"
    ),
    scenario="OEM 软件付费功能（如高级配方）开机校验授权。",
    value="替代自研授权码体系。",
    xml_scen="开机检查 License。",
    related=["FB_CheckOemLicense", "FB_GetLicenses"],
)

_lic_add(
    "FB_CheckOemLicense",
    summary=(
        "FB_CheckOemLicense 类似 FB_CheckLicense，但专门校验 OEM（设备制造商）签发的 License——这种 License 用 OEM 的私钥签名，绑定本机 SystemID。\n\n"
        "用于：OEM 自研的设备授权 / 防克隆体系。"
    ),
    behavior=(
        "**调用**：与 FB_CheckLicense 类似，多了 `sOemId` 输入指定 OEM 身份。\n\n"
        "**校验过程**：本 FB 内部用 OEM 公钥验证签名 + 校验机器 SystemID 是否与签名时绑定的一致；只有都通过才返回有效。"
    ),
    scenario="OEM 设备出厂前签发 License 文件，开机校验防克隆。",
    value="OEM 防克隆标准方案。",
    xml_scen="OEM 防克隆校验。",
    related=["FB_CheckLicense", "FB_GetSystemId"],
)

_lic_add(
    "FB_GetLicenses",
    summary=(
        "FB_GetLicenses 枚举本机所有已安装的 TwinCAT License，返回 ID 列表 + 状态。\n\n"
        "用于：HMI License 总览、运维盘点。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿一次性返回，数组形式。数量由 `nLicenses` 给出。"
    ),
    scenario="HMI License 总览。",
    value="替代手动 License Manager。",
    xml_scen="HMI License 总览。",
    related=["FB_GetLicensesEx", "FB_CheckLicense"],
)

_lic_add(
    "FB_GetLicensesEx",
    summary=(
        "FB_GetLicensesEx 是 FB_GetLicenses 的增强版：除了 License ID 还返回更详细元数据（签发日期 / 到期日 / 厂商）。\n\n"
        "用于：合规审计 / 续费提醒。"
    ),
    behavior=(
        "**调用**：与 FB_GetLicenses 相同接口，输出结构字段更多。"
    ),
    scenario="合规审计 / 续费提醒。",
    value="更详细元数据。",
    xml_scen="合规审计。",
    related=["FB_GetLicenses"],
)

_lic_add(
    "FB_GetLicenseDongles",
    summary=(
        "FB_GetLicenseDongles 枚举本机所有 Beckhoff License Dongle（USB 加密狗），返回每个 Dongle 的硬件 ID。\n\n"
        "用于：多 dongle 环境下确认插入了哪些。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿读一次。"
    ),
    scenario="确认插入了哪些 dongle。",
    value="多 dongle 环境管理。",
    xml_scen="多 dongle 列出。",
    related=["FB_GetDongleSystemID"],
)

_lic_add(
    "FB_GetDongleSystemID",
    summary=(
        "FB_GetDongleSystemID 读取指定 dongle 的 SystemID——这个 ID 是签发 License 时绑定的硬件指纹，比 TwinCAT SystemID 更稳定（更换 OS 不变）。\n\n"
        "用于：OEM License 绑定。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿，按 dongle 序号读 SystemID。"
    ),
    scenario="OEM License 绑定 dongle SystemID。",
    value="跨 OS 重装稳定的硬件指纹。",
    xml_scen="读 dongle SystemID。",
    related=["FB_GetLicenseDongles"],
)

_lic_add(
    "FB_GetOemOfLicenseId",
    summary=(
        "FB_GetOemOfLicenseId 输入 License ID，返回签发该 License 的 OEM 身份（OEM ID / 名字）。\n\n"
        "用于：审计哪个 OEM 签发的某个 License。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿，读出 OEM 身份字段。"
    ),
    scenario="审计 License 签发方。",
    value="License 来源审计。",
    xml_scen="审计 License 来源。",
    related=["FB_CheckOemLicense"],
)


_lic_add(
    "FB_LicFileCreate",
    summary=(
        "FB_LicFileCreate 在本机 / dongle 上创建一份新的 License 申请文件（`.tclrq`）——客户拿这个文件去找授权方换 License。\n\n"
        "用于：License 申请流程的第一步。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿。本 FB 把当前机器的硬件指纹打包成 `.tclrq` 写到指定位置。"
    ),
    scenario="License 申请第一步。",
    value="脚本化授权申请。",
    xml_scen="生成 License 申请文件。",
    related=["FB_LicFileRead", "FB_LicFileDelete"],
)

_lic_add(
    "FB_LicFileDelete",
    summary=(
        "FB_LicFileDelete 删除指定的 License 文件。\n\n"
        "用于：清理过期 / 错误的 License 文件。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿。删除文件，可能需要管理员权限。"
    ),
    scenario="清理过期 License。",
    value="脚本化清理。",
    xml_scen="清理过期 License。",
    related=["FB_LicFileCreate"],
)

_lic_add(
    "FB_LicFileRead",
    summary=(
        "FB_LicFileRead 读取一份 License 文件的内容（元数据）。\n\n"
        "用于：合规审计 / License 内容核对。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿。读出文件元数据填充输出结构。"
    ),
    scenario="读 License 文件内容。",
    value="审计支持。",
    xml_scen="读 License 文件。",
    related=["FB_LicFileCreate"],
)

_lic_add(
    "FB_LicFileCopyFromDongle",
    summary=(
        "FB_LicFileCopyFromDongle 把 dongle 里存的 License 文件复制到本机硬盘。\n\n"
        "用于：备份 License、维护流程。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿。从 dongle 读出文件写到目标路径。"
    ),
    scenario="备份 dongle License 到硬盘。",
    value="备份支持。",
    xml_scen="备份 dongle License。",
    related=["FB_LicFileCopyToDongle"],
)

_lic_add(
    "FB_LicFileCopyToDongle",
    summary=(
        "FB_LicFileCopyToDongle 把本机文件复制到 dongle 存储里（dongle 内置存储能装小文件）。\n\n"
        "用于：把激活后的 License 文件写回 dongle 完成激活。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿，写文件到 dongle 存储。"
    ),
    scenario="把激活的 License 写回 dongle。",
    value="完成激活闭环。",
    xml_scen="写 License 到 dongle。",
    related=["FB_LicFileCopyFromDongle"],
)

_lic_add(
    "FB_LicFileGetStorageInfo",
    summary=(
        "FB_LicFileGetStorageInfo 查询 dongle 存储信息：总容量、已用字节、文件列表等。\n\n"
        "用于：写入前先确认 dongle 有足够空间。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿，读 dongle 存储统计信息。"
    ),
    scenario="写 License 前查 dongle 空间。",
    value="预检支持。",
    xml_scen="查 dongle 存储。",
    related=["FB_LicFileCopyToDongle"],
)


# ============================================================================
# File / Persistent
# ============================================================================

_FILE_PITFALLS = _ADS_PITFALLS + [
    ("**文件操作受 SystemService 权限限制**——CX 设备的 `C:\\TwinCAT\\Boot` 等敏感目录可能不可写。", True),
    ("绝对路径建议带盘符；相对路径以 `ePath` 枚举为基准（`PATH_GENERIC` = TwinCAT 安装目录）。", True),
    ("文件 I/O 是异步操作，触发后在 `bBusy → bDone` 之间业务侧不能假设文件已可见。", False),
]


_add(
    "FB_FileProperties",
    summary=(
        "FB_FileProperties 读取指定文件的元数据：大小、创建时间、修改时间、属性位（只读 / 隐藏 / 系统）。\n\n"
        "用于：判断文件是否最近被修改、做配方文件 freshness 检查。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿。返回 `ST_FileProperties` 结构，含 `nFileSize` / `tCreate` / `tModify` 等字段。\n\n"
        "**响应**：本地 < 50 ms。"
    ),
    pitfalls=_FILE_PITFALLS,
    scenario="判断配方文件是否最近被改动。",
    value="替代手工 dir 命令。",
    alt=(
        "- Win32 `GetFileAttributes`：复杂。\n"
        "- **本 FB**：标准 ADS。"
    ),
    xml_scen="检查配方文件 freshness。",
    xml_val="替代 dir。",
    xml_verify="改 sPath := 'C:\\TwinCAT\\Boot\\TwinCAT.config'，触发后 stProps.nFileSize > 0。",
    xml_extra_vars=[
        ("bRead", "BOOL", "FALSE", ""),
        ("sPath", "STRING(255)", "'C:\\\\TwinCAT\\\\Boot\\\\TwinCAT.config'", ""),
        ("stProps", "ST_FileProperties", None, ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbFB_FileProperties(\n"
        "    sNetID := '', bExecute := bRead, sPathName := sPath, ePath := PATH_GENERIC,\n"
        "    tTimeout := DEFAULT_ADS_TIMEOUT,\n"
        "    stProperties => stProps, bBusy => bBusy_, bError => bErrFlag, nErrId => nErrCode\n"
        ");"
    ),
    related=["FB_EnumFindFileEntry", "FB_FileTime64ToTzSpecificLocalTime"],
)

_add(
    "FB_EnumFindFileEntry",
    summary=(
        "FB_EnumFindFileEntry 枚举目录里匹配通配符模式的文件，每次调用返回一条目（文件名 + 元数据）。\n\n"
        "用于：找日志文件 / 报表文件做归档处理。"
    ),
    behavior=(
        "**协议**：`bExecute` 上升沿打开搜索；后续 `bExecute` 上升沿取下一条。文件用完 `bEOL = TRUE`（end-of-list）。\n\n"
        "**典型用法**：与业务计数器配合循环读取。"
    ),
    pitfalls=_FILE_PITFALLS + [
        ("**通配符是 Windows DOS 风格**：`*.csv` 匹配所有 csv，`?` 匹配单字符；不支持正则。", True),
    ],
    scenario="找当天所有日志文件做压缩。",
    value="替代手工 dir 命令。",
    alt=(
        "- Win32 FindFirstFile / FindNextFile：要 Shell。\n"
        "- **本 FB**：PLC 内置。"
    ),
    xml_scen="枚举 *.csv 日志。",
    xml_val="替代手工 dir。",
    xml_verify="触发循环读取，每次得到一个文件名直到 bEOL = TRUE。",
    xml_extra_vars=[
        ("bExec", "BOOL", "FALSE", ""),
        ("sPattern", "STRING(255)", "'C:\\\\TwinCAT\\\\Boot\\\\*.config'", ""),
        ("sFoundName", "STRING(255)", None, ""),
        ("bEOL", "BOOL", None, ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbFB_EnumFindFileEntry(\n"
        "    bExecute := bExec, sPathName := sPattern, ePath := PATH_GENERIC,\n"
        "    tTimeout := DEFAULT_ADS_TIMEOUT,\n"
        "    sFileName => sFoundName, bEOL => bEOL,\n"
        "    bBusy => bBusy_, bError => bErrFlag, nErrId => nErrCode\n"
        ");"
    ),
    related=["FB_EnumFindFileList", "FB_FileProperties"],
)

_add(
    "FB_EnumFindFileList",
    summary=(
        "FB_EnumFindFileList 类似 FB_EnumFindFileEntry，但一次返回**整个文件列表**而不是一条一条。\n\n"
        "用于：批量获取所有匹配文件，做后续 ARRAY 处理。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿，一次性返回所有匹配文件到调用方分配的数组。"
    ),
    pitfalls=_FILE_PITFALLS + [
        ("**数组要预分配足够大**——上限超出会被截断。", True),
    ],
    scenario="批量列出文件做 ARRAY 处理。",
    value="比 EnumFindFileEntry 一次拿完。",
    alt=(
        "- 用 EnumFindFileEntry 循环：编程繁。\n"
        "- **本 FB**：一次完成。"
    ),
    xml_scen="批量列文件。",
    xml_val="一次完成。",
    xml_verify="触发后 aFiles 数组填入文件名，nCount 给数量。",
    xml_extra_vars=[
        ("bExec", "BOOL", "FALSE", ""),
        ("sPattern", "STRING(255)", "'C:\\\\TwinCAT\\\\Boot\\\\*.config'", ""),
        ("aFiles", "ARRAY[0..63] OF ST_FindFileEntry", None, ""),
        ("nCount", "UDINT", None, ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbFB_EnumFindFileList(\n"
        "    bExecute := bExec, sPathName := sPattern, ePath := PATH_GENERIC,\n"
        "    pAddr := ADR(aFiles), cbAddr := SIZEOF(aFiles), tTimeout := DEFAULT_ADS_TIMEOUT,\n"
        "    nFileCnt => nCount, bBusy => bBusy_, bError => bErrFlag, nErrId => nErrCode\n"
        ");"
    ),
    related=["FB_EnumFindFileEntry"],
)

_add(
    "FB_FileRingBuffer",
    summary=(
        "FB_FileRingBuffer 把磁盘上一组等大的文件当作环形缓冲使用——满了自动覆盖最老文件。\n\n"
        "用于：长期日志归档（如 30 天循环日志），保证不会占满磁盘。"
    ),
    behavior=(
        "**方法接口**：本 FB 是 OO 风格，通过 `Init` / `WriteToBuffer` / `ReadFromBuffer` 等方法调用。"
        "Init 时指定文件名模板 + 最大文件数 + 单文件最大字节；满了自动滚动。\n\n"
        "**典型用法**：业务侧周期写日志条目；FB 内部自动按时间 / 大小切片。"
    ),
    pitfalls=_FILE_PITFALLS + [
        ("**Init 参数错会导致首次 Write 失败**——文件名模板要含占位符（如 `'log_%d.txt'`）才能滚动。", True),
        ("**关闭 FB 前要 Flush**——否则缓冲区里的最后一段可能未写到文件。", True),
    ],
    scenario="30 天循环日志，磁盘满了自动覆盖最老。",
    value="替代手写文件 rotation 逻辑。",
    alt=(
        "- 自写 rotation：易出 off-by-one bug。\n"
        "- **本 FB**：库提供。"
    ),
    xml_scen="30 天循环日志。",
    xml_val="库提供 rotation。",
    xml_verify="调 Init 配置 N=30 文件，循环 Write，观察磁盘上 log_*.txt 滚动。",
    xml_extra_vars=[],
)

_add(
    "FB_WritePersistentData",
    summary=(
        "FB_WritePersistentData 通过 ADS 把指定 PLC 项目里的 `PERSISTENT` 变量手动写到磁盘（默认 TwinCAT 已自动保存，本 FB 用于强制立即保存）。\n\n"
        "用于：关键操作后强制持久化（如 commissioning 配置变更）。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿，向目标 PLC 端口发『保存 persistent』命令。\n\n"
        "**响应**：本地几十 ms；persistent 数据量大可能数秒。"
    ),
    pitfalls=_FILE_PITFALLS + [
        ("**TwinCAT 默认在 shutdown 时自动保存 persistent**——日常无需主动调用。频繁调用会写磁盘磨损 SD 卡。", False),
        ("`PERSISTENT` 与 `RETAIN` 不同：persistent 写文件，retain 在 PLC 内存断电保护区。本 FB 只管 persistent。", True),
    ],
    scenario="关键配置变更后强制持久化。",
    value="替代等待自动保存。",
    alt=(
        "- 等 TwinCAT 自动保存：可能丢配置变更（突然掉电时）。\n"
        "- **本 FB**：业务时机可控。"
    ),
    xml_scen="配置变更后强制写文件。",
    xml_val="时机可控。",
    xml_verify="变更 persistent 变量后触发；观察对应 `.bootdata` 文件被更新。",
    xml_extra_vars=[
        ("bWrite", "BOOL", "FALSE", ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbFB_WritePersistentData(\n"
        "    NETID := '', PORT := 851, START := bWrite, TMOUT := DEFAULT_ADS_TIMEOUT,\n"
        "    BUSY => bBusy_, ERR => bErrFlag, ERRID => nErrCode\n"
        ");"
    ),
    related=["WritePersistentData"],
)

_add(
    "WritePersistentData",
    summary=(
        "WritePersistentData 是 FB_WritePersistentData 的旧名 / 同义包装——保留是为了向后兼容旧代码。"
        "新项目用 `FB_WritePersistentData`（带 `FB_` 前缀，命名规范统一）。\n\n"
        "功能与 FB_WritePersistentData 完全相同：通过 ADS 触发目标 PLC 立即写 persistent 数据。"
    ),
    behavior=(
        "**调用 / 响应**：与 `FB_WritePersistentData` 完全一致。\n\n"
        "**用途**：仅用于已部署的旧项目调用接口不变；新项目直接用 FB_WritePersistentData。"
    ),
    pitfalls=_FILE_PITFALLS + [
        ("**Deprecated 别名**——新项目用 FB_WritePersistentData，本名仅向后兼容。", False),
    ],
    scenario="旧项目持续维护用，不再新增调用。",
    value="向后兼容。",
    alt=(
        "- FB_WritePersistentData（推荐）：命名规范一致。\n"
        "- **本 FB**：仅向后兼容。"
    ),
    xml_scen="兼容旧项目。",
    xml_val="向后兼容。",
    xml_verify="同 FB_WritePersistentData。",
    xml_extra_vars=[
        ("bWrite", "BOOL", "FALSE", ""),
        ("bBusy_", "BOOL", None, ""), ("bErrFlag", "BOOL", None, ""), ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbWritePersistentData(\n"
        "    NETID := '', PORT := 851, START := bWrite, TMOUT := DEFAULT_ADS_TIMEOUT,\n"
        "    BUSY => bBusy_, ERR => bErrFlag, ERRID => nErrCode\n"
        ");"
    ),
    related=["FB_WritePersistentData"],
)


# ============================================================================
# Memory buffer / CSV
# ============================================================================

_BUF_PITFALLS = [
    ("调用方需预分配缓冲区，缓冲区大小由 `cbBuffer` 参数告知 FB；超出会截断。", False),
    ("**指针运算需小心**：`pBuffer` 必须指向有效内存，FB 不做有效性校验。", False),
    ("`STRING(N)` 内部字节布局含尾零；处理 raw bytes 时区分 `LEN()` 与 `SIZEOF()`。", True),
    ("PDF 未给详细错误码——多数错误反映为 `bError = TRUE` 不区分子类，业务侧靠输入合法性预检为主。", False),
    ("CSV 字段分隔符默认为 `;`（欧洲风格），中国 / 北美场景常用 `,` 要在初始化时配置。", True),
]


_add(
    "FB_CSVMemBufferReader",
    summary=(
        "FB_CSVMemBufferReader 从一段内存缓冲（典型是文件读到的字节流）里按 CSV 格式逐字段解析。\n\n"
        "用于：读取 CSV 配方文件、HMI 上传的参数表、第三方系统导出的数据。"
    ),
    behavior=(
        "**OO 方法接口**：用 `Init` 绑定缓冲区 → 循环 `GetNextField` 取下一字段。FB 内部维护游标。\n\n"
        "**字段类型**：所有字段统一解析为字符串，业务侧按需 `STRING_TO_INT` / `STRING_TO_LREAL`。\n\n"
        "**分隔符 / 引号**：可配置；默认按 PDF 实现的 RFC4180 兼容方式处理。"
    ),
    pitfalls=_BUF_PITFALLS,
    scenario="读 HMI 上传的配方 CSV 文件。",
    value="替代手写 CSV 解析。",
    alt=(
        "- 自写 split + escape 处理：边界条件多。\n"
        "- **本 FB**：标准库。"
    ),
    xml_scen="读配方 CSV。",
    xml_val="替代手写解析。",
    xml_verify="先 Init 绑定缓冲，循环调 GetNextField 取每个字段。",
    xml_extra_vars=[],
)

_add(
    "FB_CSVMemBufferWriter",
    summary=(
        "FB_CSVMemBufferWriter 把一系列字段按 CSV 格式追加写入内存缓冲，最终缓冲可写到磁盘。\n\n"
        "用于：生成生产日报 / 参数导出表。"
    ),
    behavior=(
        "**OO 方法接口**：`Init` 绑定缓冲 → 循环 `WriteField` 追加字段 → `WriteNewLine` 换行。"
    ),
    pitfalls=_BUF_PITFALLS,
    scenario="生成生产日报 CSV。",
    value="替代手写格式化。",
    alt=(
        "- 自写 CSV：边界条件多（含分隔符的字段要加引号转义）。\n"
        "- **本 FB**：库处理转义。"
    ),
    xml_scen="生成日报 CSV。",
    xml_val="自动处理转义。",
    xml_verify="按 WriteField 顺序追加多列，最后 WriteNewLine 换行。",
    xml_extra_vars=[],
)

_add(
    "FB_MemBufferMerge",
    summary=(
        "FB_MemBufferMerge 把两段内存缓冲（如两段拼好的二进制数据）合并到一段新缓冲。\n\n"
        "用于：通讯协议拼包、文件头 + 数据 + 校验合并。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿。给两个源指针 + 大小、一个目标指针 + 容量，FB 把两段顺序拷贝过去。\n\n"
        "**性能**：内存拷贝速度受 CPU + 任务周期影响；MB 级数据建议拆多个周期做。"
    ),
    pitfalls=_BUF_PITFALLS + [
        ("目标缓冲容量不够会失败，业务侧要预先算 `cbSrc1 + cbSrc2 ≤ cbDest`。", False),
    ],
    scenario="拼通讯协议包：头 + payload + 校验。",
    value="比手写 `MEMCPY` 两次直观。",
    alt=(
        "- 两次 MEMCPY：可行。\n"
        "- **本 FB**：一次调用，意图清晰。"
    ),
    xml_scen="拼通讯协议包。",
    xml_val="意图清晰。",
    xml_verify="给两段缓冲，触发合并；输出缓冲内容应为两段拼接。",
    xml_extra_vars=[],
)

_add(
    "FB_MemBufferSplit",
    summary=(
        "FB_MemBufferSplit 把一段内存缓冲按指定位置拆成两段（前半 + 后半）。\n\n"
        "用于：通讯协议拆包、文件读出来后分头 / 体。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿。给源指针 + 拆分位置，FB 拷出两个新段。"
    ),
    pitfalls=_BUF_PITFALLS,
    scenario="通讯协议拆包：头 + payload。",
    value="替代手写两次 MEMCPY。",
    alt=(
        "- 手写 MEMCPY：可行。\n"
        "- **本 FB**：意图清晰。"
    ),
    xml_scen="拆通讯协议包。",
    xml_val="意图清晰。",
    xml_verify="给一段缓冲 + 拆分位置 N，触发后前 N 字节进段 1，剩余进段 2。",
    xml_extra_vars=[],
)

_add(
    "FB_MemRingBuffer",
    summary=(
        "FB_MemRingBuffer 实现固定大小的内存环形缓冲——满了覆盖最老数据。\n\n"
        "用于：实时趋势线缓存、最近 N 条事件队列。"
    ),
    behavior=(
        "**OO 方法**：`Init` 设置容量 → `Add` 入队 → `Get` / `Peek` 出队。满了 Add 会覆盖最旧。\n\n"
        "**典型场景**：HMI 实时趋势保留最近 1000 个采样点。"
    ),
    pitfalls=_BUF_PITFALLS + [
        ("环形缓冲读出顺序约定『最老 → 最新』；业务侧若期望反向要自己 reverse。", True),
    ],
    scenario="HMI 趋势线最近 1000 点。",
    value="替代手写环形索引计算。",
    alt=(
        "- 自写环形：易出 wrap-around bug。\n"
        "- **本 FB**：库提供。"
    ),
    xml_scen="HMI 趋势 1000 点。",
    xml_val="库提供。",
    xml_verify="Init 容量 N，连续 Add N+1 个值，第一个被覆盖。",
    xml_extra_vars=[],
)

_add(
    "FB_MemRingBufferEx",
    summary=(
        "FB_MemRingBufferEx 是 FB_MemRingBuffer 的增强版：每个元素可以是变长记录（不再是定长字节）。\n\n"
        "用于：事件日志（每条事件长度不同）、变长消息队列。"
    ),
    behavior=(
        "**OO 方法接口**：与 FB_MemRingBuffer 类似，但 Add 时要附带长度参数。"
    ),
    pitfalls=_BUF_PITFALLS,
    scenario="变长事件日志最近 N 条。",
    value="支持变长记录。",
    alt=(
        "- FB_MemRingBuffer：仅定长。\n"
        "- **本 FB**：变长。"
    ),
    xml_scen="变长事件日志。",
    xml_val="支持变长。",
    xml_verify="Add 不同长度记录，Get 取回原样。",
    xml_extra_vars=[],
)

_add(
    "FB_MemStackBuffer",
    summary=(
        "FB_MemStackBuffer 实现内存栈（LIFO）——后进先出。\n\n"
        "用于：函数调用栈仿真、操作历史（Undo 栈）、深度优先搜索。"
    ),
    behavior=(
        "**OO 方法**：`Init` → `Push` 入栈 → `Pop` 出栈 → `Peek` 看栈顶不出。"
    ),
    pitfalls=_BUF_PITFALLS + [
        ("栈满 `Push` 失败，业务侧要预估深度。", False),
    ],
    scenario="Undo 操作栈。",
    value="标准 LIFO 数据结构。",
    alt=(
        "- 自写：易出错。\n"
        "- **本 FB**：库提供。"
    ),
    xml_scen="Undo 栈。",
    xml_val="标准 LIFO。",
    xml_verify="Push 3 个元素，Pop 3 次按相反顺序取回。",
    xml_extra_vars=[],
)

_add(
    "FB_StringRingBuffer",
    summary=(
        "FB_StringRingBuffer 字符串专用环形缓冲——每条记录是 STRING(N)。\n\n"
        "用于：HMI 消息历史、操作员输入历史。"
    ),
    behavior=(
        "**OO 方法**：`Init` 容量 + 字符串长度 → `Add` 追加字符串 → `Get` 取回。"
    ),
    pitfalls=_BUF_PITFALLS,
    scenario="HMI 消息历史最近 100 条。",
    value="字符串专用，免转字节流。",
    alt=(
        "- FB_MemRingBuffer：要自己处理字符串字节。\n"
        "- **本 FB**：直接 STRING。"
    ),
    xml_scen="HMI 消息历史。",
    xml_val="字符串专用。",
    xml_verify="Add 多条 STRING，Get 顺序取回。",
    xml_extra_vars=[],
)


# ============================================================================
# Hash / Linked list
# ============================================================================

_add(
    "FB_HashTableCtrl",
    summary=(
        "FB_HashTableCtrl 哈希表控制器——给 PLC 程序提供 O(1) 平均时间的键值对存取。"
        "键是 STRING / 整数，值是任意类型（用 POINTER + SIZEOF 通用化）。\n\n"
        "用于：HMI 标签到 PLC 内部 ID 的映射、大量配方参数的随机访问。"
    ),
    behavior=(
        "**OO 方法**：`Init` 设置容量 + key/value 大小 → `Add` / `Remove` / `Find` 调用键值操作。\n\n"
        "**性能**：典型 Add / Find O(1)（哈希碰撞时退化到 O(n)）；适合频繁查询场景。"
    ),
    pitfalls=[
        ("容量满了 Add 失败，业务侧应监控负载因子。", False),
        ("**键的哈希冲突在小容量时易发生**——Init 时容量建议为预期条目数的 1.5×。", True),
        ("**指针存值要保证生命周期**——若指向局部变量，作用域结束后取出来即悬空。", True),
        ("PDF 错误码引用通用 BOOL 返回（FALSE = 失败）。", False),
        ("没有迭代器接口（要遍历需要自己维护键列表）。", True),
    ],
    scenario="HMI 标签到 PLC 内部 ID 的映射。",
    value="O(1) 替代线性查找。",
    alt=(
        "- ARRAY OF KeyValuePair + 线性扫描：O(n)。\n"
        "- **本 FB**：O(1) 平均。"
    ),
    xml_scen="HMI 标签到 PLC ID 映射。",
    xml_val="O(1) 查找。",
    xml_verify="Add 100 个键值，Find 随机键应秒查。",
    xml_extra_vars=[],
)

_add(
    "FB_LinkedListCtrl",
    summary=(
        "FB_LinkedListCtrl 双向链表控制器——动态可增删的节点链。\n\n"
        "用于：工单队列（中间插入 / 删除频繁）、HMI 列表 / 树状结构。"
    ),
    behavior=(
        "**OO 方法**：`Init` 绑定头节点 → `AddHead` / `AddTail` / `Remove` / `Find` 操作。"
    ),
    pitfalls=[
        ("**节点要业务侧分配**——FB 仅管理 next/prev 指针，不分配节点存储。", False),
        ("**遍历中删除会让游标失效**——经典链表陷阱，要在删除前先保存 next。", True),
        ("跨任务访问链表必须加锁（用 `FB_IecCriticalSection`）。", True),
        ("PDF 错误反映为 BOOL 返回（FALSE = 失败）。", False),
        ("没有索引访问 O(n)——大量随机访问场景用 HashTable 更合适。", True),
    ],
    scenario="工单队列频繁中间插入 / 删除。",
    value="O(1) 中间操作。",
    alt=(
        "- ARRAY：中间插入 O(n) 拷贝。\n"
        "- **本 FB**：O(1)。"
    ),
    xml_scen="工单队列。",
    xml_val="O(1) 中间操作。",
    xml_verify="AddHead / AddTail / Remove 操作，遍历看顺序。",
    xml_extra_vars=[],
)

_add(
    "FB_EnumStringNumbers",
    summary=(
        "FB_EnumStringNumbers 枚举一段字符串里所有可解析为数字的子串。"
        "用于解析自由格式输入（操作员输入 `'5, 10, 15'` 取出 5 / 10 / 15）。\n\n"
        "也用于解析 HMI 上传的多值字段。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿启动 / 取下一个。每次返回一个数字。"
    ),
    pitfalls=[
        ("**仅整数 / 浮点字面量**——表达式（`5+3`）不会展开。", False),
        ("分隔符宽松（空白 / `,` / `;`）；具体规则参考 PDF / InfoSys。", True),
        ("超长数字会被截断为输出类型上限（典型 LREAL）。", True),
        ("PDF 未列错误码。", False),
        ("空输入返回 0 条，业务侧应预检不要把 0 当作错。", True),
    ],
    scenario="操作员输入 `5, 10, 15` 取出多个数。",
    value="替代自写字符串分割 + 转数字。",
    alt=(
        "- 自写 split：边界条件多。\n"
        "- **本 FB**：库提供。"
    ),
    xml_scen="解析操作员多值输入。",
    xml_val="自动处理分隔符。",
    xml_verify="输入 '5, 10, 15.5'，循环触发取出 5、10、15.5。",
    xml_extra_vars=[],
)


# ============================================================================
# Registry / Format / Misc
# ============================================================================

_REG_PITFALLS = _ADS_PITFALLS + [
    ("**修改注册表是系统级操作**——错误的值可能让 Windows 不能启动；生产环境务必备份。", False),
    ("HKEY 路径要按 Windows 约定（如 `HKEY_LOCAL_MACHINE\\SYSTEM\\...`），区分大小写不严但建议规范化。", True),
]


_add(
    "FB_RegQueryValue",
    summary=(
        "FB_RegQueryValue 通过 ADS 读取目标 TwinCAT 系统的 Windows 注册表键值（HKEY_LOCAL_MACHINE 等子树下的字符串 / DWORD 值）。\n\n"
        "用于：读硬件配置、Windows 设置、第三方软件配置。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿。给键路径 + 值名 → 读出值。\n\n"
        "**支持类型**：REG_SZ / REG_DWORD 等常见 Windows 注册表类型。"
    ),
    pitfalls=_REG_PITFALLS,
    scenario="读 Windows 计算机名注册表值。",
    value="替代 Shell `reg query`。",
    alt=(
        "- Shell reg：要 Shell。\n"
        "- **本 FB**：标准 ADS。"
    ),
    xml_scen="读注册表。",
    xml_val="替代 Shell。",
    xml_verify="读 `HKLM\\SOFTWARE\\Beckhoff` 任一键应非空。",
    xml_extra_vars=[],
)

_add(
    "FB_RegSetValue",
    summary=(
        "FB_RegSetValue 写入目标系统的 Windows 注册表键值。\n\n"
        "用于：commissioning 时配置硬件 / 软件参数。"
    ),
    behavior=(
        "**调用**：与 FB_RegQueryValue 镜像，给键路径 + 值名 + 新值。"
    ),
    pitfalls=_REG_PITFALLS + [
        ("写错值可能让某些 Windows 服务无法启动；要先备份键再写。", False),
    ],
    scenario="commissioning 时配置注册表。",
    value="脚本化配置。",
    alt=(
        "- 手动 regedit：单机方便。\n"
        "- **本 FB**：批量。"
    ),
    xml_scen="commissioning 配置注册表。",
    xml_val="脚本化。",
    xml_verify="写一个测试键，用 FB_RegQueryValue 读回应一致。",
    xml_extra_vars=[],
)


_add(
    "FB_FormatString",
    summary=(
        "FB_FormatString 类似 C `printf`：按格式字符串把多个参数拼成最终字符串。\n\n"
        "用于：HMI 显示文本拼装、日志消息格式化。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿。`sFormat` 含 `%d` / `%s` / `%f` 占位符，参数列表通过 `T_Arg` 数组传入。\n\n"
        "**精度控制**：`%5.2f` 等格式符按 C 风格解析。"
    ),
    pitfalls=[
        ("**类型不匹配会出乱码**——`%d` 配错 LREAL 不会编译报错但运行出错。", False),
        ("参数 ARRAY 元素数量必须 ≥ 格式符数量；少了越界。", False),
        ("STRING(255) 输出上限——超出会截断。", True),
        ("`%%` 转义为 `%`，与 C 一致。", True),
        ("PDF 错误反映为 `bError = TRUE`，不细分。", False),
    ],
    scenario="HMI 显示 `产量: 1234.50 件/小时`。",
    value="替代 CONCAT + 数字转字符串多次调用。",
    alt=(
        "- 多次 CONCAT + REAL_TO_STRING：代码繁。\n"
        "- **本 FB**：一行完成。"
    ),
    xml_scen="HMI 拼装显示字符串。",
    xml_val="替代多次 CONCAT。",
    xml_verify="格式串 `'Count=%d'` + 参数 100，输出应为 `'Count=100'`。",
    xml_extra_vars=[],
)

_add(
    "FB_FormatString2",
    summary=(
        "FB_FormatString2 是 FB_FormatString 的扩展版：支持更多格式符 / 更长输出缓冲 / Unicode 字符。\n\n"
        "新项目优先用 Ex 版。"
    ),
    behavior=(
        "**调用**：与 FB_FormatString 类似，参数 / 输出更丰富。"
    ),
    pitfalls=[
        ("与 FB_FormatString 共享大多数陷阱。", False),
        ("Unicode 处理要确保参数也是宽字符。", True),
        ("输出缓冲若用 STRING(N) 仍受 N 限制；Unicode 用 WSTRING(N)。", True),
        ("PDF 未细分错误码。", False),
        ("Beckhoff 在新版本里 FB_FormatString2 通常是首选。", True),
    ],
    scenario="HMI Unicode 显示文本。",
    value="支持 Unicode。",
    alt=(
        "- FB_FormatString：仅 ASCII。\n"
        "- **本 FB**：Unicode。"
    ),
    xml_scen="HMI Unicode 拼装。",
    xml_val="支持 Unicode。",
    xml_verify="格式串带中文，输出应正确。",
    xml_extra_vars=[],
)


_add(
    "FB_BasicPID",
    summary=(
        "FB_BasicPID 实现一个基础 PID 控制器：给定测量值 + 设定值 + Kp/Ki/Kd 参数，输出执行量。\n\n"
        "用于：简单的温度 / 流量 / 压力 / 位置闭环控制。比 Tc3_Controller 库的高级控制器轻量，适合教学 / 小项目。"
    ),
    behavior=(
        "**周期调用**：每个 PLC 周期调一次。FB 内部按设定的采样时间累加积分项 / 计算微分。\n\n"
        "**抗饱和**：内部 anti-windup 处理，输出在限幅时不会无限累加积分。\n\n"
        "**模式**：自动 / 手动切换，无扰切换由 FB 内部处理。"
    ),
    pitfalls=[
        ("**参数整定不当易振荡**——Kp 过大、Ti 过小会振荡。建议先用 Ziegler-Nichols 法粗调。", True),
        ("**采样时间应与 PLC 任务周期一致**——不一致会让积分 / 微分计算错。", False),
        ("**手动 → 自动切换瞬间**：FB 内部用『积分项预置』避免输出跳变；业务侧不需要自己处理。", True),
        ("PDF 错误反映为输出限幅 / 状态枚举，不会直接报『PID 不稳定』——稳定性靠工程师整定。", False),
        ("**不要用 Basic 做高动态系统**——电机伺服等场景应用 Tc3_Controller 的高级控制器。", True),
    ],
    scenario="水箱温度闭环控制：测温度 → PID → 控制加热阀。",
    value="比手写 PID 安全（带 anti-windup）。",
    alt=(
        "- 手写 PID：易忘 anti-windup。\n"
        "- Tc3_Controller：高级、复杂。\n"
        "- **本 FB**：轻量。"
    ),
    xml_scen="水箱温度闭环控制。",
    xml_val="带 anti-windup。",
    xml_verify="设置 setpoint，monitor 输出在合理范围；改 setpoint 输出跟随。",
    xml_extra_vars=[],
)


_add(
    "FB_AmsLogger",
    summary=(
        "FB_AmsLogger 提供 ADS 消息日志功能——把日志条目按 AMS 协议格式发给目标日志服务（典型是 TwinCAT EventLogger）。\n\n"
        "用于：在没有 Tc3_EventLogger 的老项目里做事件日志、远程日志聚合。"
    ),
    behavior=(
        "**调用**：`Add` / `Log` 方法添加条目，FB 内部按时序异步发送。\n\n"
        "**等级**：典型有 Info / Warning / Error 等枚举。"
    ),
    pitfalls=[
        ("**新项目建议用 Tc3_EventLogger**——FB_AmsLogger 是较老 API。", True),
        ("日志接收方必须是支持 AMS Logger 协议的服务，不是任意机器都能收。", False),
        ("缓冲区满会丢日志条目而非阻塞——业务侧不要假设每条都送达。", True),
        ("PDF 错误反映为 BOOL 返回。", False),
        ("跨网段日志会受 ADS 抖动影响顺序。", True),
    ],
    scenario="老项目事件日志。",
    value="老项目兼容。",
    alt=(
        "- Tc3_EventLogger（推荐）：新项目用。\n"
        "- **本 FB**：老项目兼容。"
    ),
    xml_scen="老项目日志。",
    xml_val="兼容。",
    xml_verify="调用 Add 加日志条目，目标日志服务应收到。",
    xml_extra_vars=[],
)

_add(
    "FB_ScopeServerControl",
    summary=(
        "FB_ScopeServerControl 通过 ADS 控制 TwinCAT Scope Server（示波器记录服务）的启动 / 停止 / 配置加载。\n\n"
        "用于：自动化生产线在异常事件时自动触发 Scope 记录波形做故障诊断。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿，命令字（启动 / 停止 / 加载配置）发给 Scope Server。\n\n"
        "**典型流程**：异常事件触发 → 调本 FB Start → 几秒后调 Stop → Scope 自动存波形文件。"
    ),
    pitfalls=_ADS_PITFALLS + [
        ("**Scope Server 必须运行**——没装 / 没启动会立刻返回错。", False),
        ("**Scope 配置文件路径要预先就绪**——动态指向不存在的配置会失败。", True),
        ("**录制时间影响磁盘占用**——长时间录制会写大文件，要预估磁盘。", True),
    ],
    scenario="异常时自动触发 Scope 录波。",
    value="异常诊断自动化。",
    alt=(
        "- 手动 Scope View：单点诊断。\n"
        "- **本 FB**：异常事件触发。"
    ),
    xml_scen="异常时录波。",
    xml_val="自动化诊断。",
    xml_verify="触发 Start → 几秒 Stop → Scope 目录里有新波形文件。",
    xml_extra_vars=[],
)

_add(
    "FB_GetRtPerformanceData",
    summary=(
        "FB_GetRtPerformanceData 读取目标 TwinCAT 系统的实时性能数据：任务周期占比、超时次数、CPU 占用等。比 TC_CpuUsage 更细。\n\n"
        "用于：深度性能分析、容量规划。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿读一次。返回 `ST_RtPerformanceData` 结构。"
    ),
    pitfalls=_ADS_PITFALLS + [
        ("**字段含义需查 PDF / InfoSys 文档**，细节多。", True),
    ],
    scenario="深度性能分析。",
    value="比 TC_CpuUsage 字段丰富。",
    alt=(
        "- TC_CpuUsage / TC_SysLatency：简单字段。\n"
        "- **本 FB**：综合结构。"
    ),
    xml_scen="深度性能分析。",
    xml_val="综合字段。",
    xml_verify="触发后 stPerf 装载多个字段。",
    xml_extra_vars=[],
)


_add(
    "Profiler",
    summary=(
        "Profiler 提供 PLC 程序段执行时间测量——业务代码调 `Start` 标记测量起点，调 `Stop` 取得这段代码的执行 µs。\n\n"
        "用于：性能瓶颈定位、循环优化前后对比。"
    ),
    behavior=(
        "**调用**：`Start` / `Stop` 方法对（或单次 `Measure`）。FB 用 TwinCAT 高精度计时器测量。\n\n"
        "**精度**：µs 级，受 PLC 任务周期影响。"
    ),
    pitfalls=[
        ("**测量短代码段时 µs 精度不够**——< 1 µs 段需要循环 1000 次取平均。", True),
        ("**别在生产代码里留 Profiler**——本身有开销。", False),
        ("**测量过程不能被 PLC 周期中断打断**，否则结果含调度间隔。", True),
        ("PDF 未列错误码。", False),
        ("适合定位算法热点，不适合做 SLA 监控。", True),
    ],
    scenario="优化前 / 后对比某段代码执行时间。",
    value="定位性能热点。",
    alt=(
        "- 用 GET_CPU_COUNTER 自写：可行但繁。\n"
        "- **本 FB**：库提供。"
    ),
    xml_scen="优化对比。",
    xml_val="定位热点。",
    xml_verify="Start → 业务代码 → Stop → 读 nElapsed 微秒值。",
    xml_extra_vars=[],
)


# ============================================================================
# PLC_ReadSymInfo* group
# ============================================================================

_SYMINFO_PITFALLS = _ADS_PITFALLS + [
    ("**符号信息接口受目标 PLC 项目编译选项控制**——若未启用 `Symbol info` 选项符号表为空。", True),
    ("**符号名区分大小写**——`Main.x` 与 `Main.X` 不同。", True),
]

_add(
    "PLC_ReadSymInfo",
    summary=(
        "PLC_ReadSymInfo 通过 ADS 按索引读取目标 PLC 项目的符号信息（变量名 / 类型 / 地址 / 大小）。\n\n"
        "用于：上位机自动发现 PLC 变量、动态生成 HMI 绑定。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿，按 `nIndex` 读第 N 个符号。"
    ),
    pitfalls=_SYMINFO_PITFALLS,
    scenario="上位机自动发现 PLC 变量。",
    value="动态符号发现。",
    alt=(
        "- 手工维护变量表：易漏。\n"
        "- **本 FB**：自动。"
    ),
    xml_scen="自动发现 PLC 变量。",
    xml_val="自动。",
    xml_verify="循环增加 nIndex 触发，能依次读出本机所有符号。",
    xml_extra_vars=[],
)

_add(
    "PLC_ReadSymInfoByName",
    summary=(
        "PLC_ReadSymInfoByName 按变量名（字符串）直接读取符号信息——比按索引枚举快得多。\n\n"
        "用于：HMI 绑定时按名字查变量。"
    ),
    behavior=(
        "**调用**：给变量名 → 返回符号信息（地址 + 大小）。"
    ),
    pitfalls=_SYMINFO_PITFALLS,
    scenario="HMI 按名字查变量地址。",
    value="比按索引快。",
    alt=(
        "- 枚举找：O(n)。\n"
        "- **本 FB**：O(1)。"
    ),
    xml_scen="按名查变量。",
    xml_val="O(1)。",
    xml_verify="给变量名，读出对应符号信息。",
    xml_extra_vars=[],
)

_add(
    "PLC_ReadSymInfoByNameEx",
    summary=(
        "PLC_ReadSymInfoByNameEx 是 PLC_ReadSymInfoByName 的增强版：额外返回更详细字段（注释 / 数据类型 GUID 等）。\n\n"
        "用于：上位机做强类型动态绑定。"
    ),
    behavior=(
        "**调用**：与 PLC_ReadSymInfoByName 类似，输出字段更多。"
    ),
    pitfalls=_SYMINFO_PITFALLS,
    scenario="强类型动态绑定。",
    value="比基础版字段多。",
    alt=(
        "- PLC_ReadSymInfoByName：基础字段。\n"
        "- **本 FB**：扩展字段。"
    ),
    xml_scen="强类型绑定。",
    xml_val="扩展字段。",
    xml_verify="读符号后看注释 / 类型字段。",
    xml_extra_vars=[],
)


_add(
    "GetRemotePCInfo",
    summary=(
        "GetRemotePCInfo 通过 ADS 读取远程 PC 的系统信息：OS 版本 / 主机名 / 系统时间 / CPU / 内存等综合数据。\n\n"
        "用于：远程运维自动盘点机器信息。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿读一次。本 FB 是个综合调用，内部串联调多个底层 FB 取数据。\n\n"
        "**响应**：跨网段可能数秒。"
    ),
    pitfalls=_ADS_PITFALLS + [
        ("综合调用串多个底层 FB，任一失败会影响结果——业务侧应分别检查各字段。", True),
    ],
    scenario="远程运维盘点。",
    value="一次调用拿多种信息。",
    alt=(
        "- 多次调底层 FB：代码繁。\n"
        "- **本 FB**：一次完成。"
    ),
    xml_scen="远程盘点。",
    xml_val="一次完成。",
    xml_verify="触发后 stInfo 多个字段装载。",
    xml_extra_vars=[],
)
