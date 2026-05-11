# Tc2_Utilities content registry (concise) — 87 FB entries.
# Per 2026-05-11 charter rules B/C/D/E. Entry shape:
#
# (summary, behavior, [pitfall lines], scenario, value, alt,
#  xml_scen, xml_val, xml_verify, var_desc_dict,
#  return_kind, related_list)
#
# All Chinese, hand-curated. var_desc dict missing keys fall back to a
# typed inference in the generator (NOT to "（详见 PDF）"). return_kind
# in {"NONE", "BOOL", "HRESULT"}.

REG = {}


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


# ------------------ helpers (Chinese) ------------------

_ADS_TIMEOUT_DESC = "ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。"
_NET_ID_DESC = "目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。"
_EXECUTE_DESC = "上升沿触发一次执行。调用期间保持高电平，完成后自动复位无需手动清零。"
_BUSY_DESC = "TRUE 表示请求正在处理；同时 `bExecute` 仍为高电平时不会响应新请求。"
_ERR_DESC = "TRUE 表示本次请求失败，错误号由 `nErrId` 给出。"
_ERRID_DESC = "ADS 错误码或本 FB 自定义错误号。0 = 无错。"


# ============================================================================
# Time / Time zone / RTC group
# ============================================================================

_add(
    "FB_LocalSystemTime",
    summary=(
        "FB_LocalSystemTime 把本机 Windows 系统时间（任务栏右下角看到的那个时钟）周期同步到 PLC 内部，"
        "并把当前时区状态（夏令时 / 标准时）一并提供给业务程序。PLC 内部用同步后的时间打时间戳，可以保证 HMI 日志、"
        "报表、报警的时间戳与操作员桌面时钟一致。\n\n"
        "内部组合 RTC_EX2、NT_GetTime、FB_GetTimeZoneInformation、NT_SetTimeToRTCTime 四个底层 FB："
        "首次使能用 NT_GetTime 拉 Windows 时间作为基准，之后由 RTC_EX2 自走，按 `dwCycle` 秒周期重同步以抗时钟漂移。"
    ),
    behavior=(
        "**调用约束**：必须周期调用（建议每 PLC 周期一次或每秒一次），否则两次同步之间的累加无法推进。\n\n"
        "**时序**：`bEnable` 上升沿后通过 ADS 异步读 Windows 时间，数个 PLC 周期后 `bValid := TRUE` 并装载 `systemTime` 与 `tzID`；"
        "之后内部自走，每过 `dwCycle` 秒重新同步一次。`bEnable := FALSE` 时停止内部计数，`bValid := FALSE`，`systemTime` 保留最后值。\n\n"
        "**`dwOpt` 位掩码**：Bit0 = 1 表示同步后也写硬件 RTC（CMOS 时钟），= 0 仅同步软件时间。默认 1。\n\n"
        "**夏令时切换**：FB 不可能精确踩在切换瞬间，所以切换会被延迟到下一次同步窗口才反映在 `tzID` 上，PDF 例子显示延迟通常在 15 秒内。"
    ),
    pitfalls=[
        ("`dwCycle` 类型为 `DWORD(1..86400)`，写 0 或 > 86400 会编译报错。", False),
        ("`systemTime.wMilliseconds` 由 RTC_EX2 内部按 PLC 周期累加，并非 Windows 真实毫秒；只适合相对计时。", False),
        ("ADS 抖动导致首次同步可能要 1-2 个 PLC 周期才把 `bValid` 拉起，使能后不要立刻读 `systemTime` 做关键判断。", False),
        ("CX 设备断电后 Windows 系统时间本身可能不准（CMOS 电池耗尽），同步出来的也不准；需要精确时钟应外接 SNTP / DCF77。", True),
        ("`tTimeout` 设得过短（< 100 ms）在跨网段调用时容易超时，本地一般 5 秒（默认）足够。", True),
    ],
    var_desc={
        "sNetID": _NET_ID_DESC,
        "bEnable": "TRUE 时启用周期同步；FALSE 时停止。电平触发，不是上升沿。",
        "dwCycle": "重同步周期，单位秒。范围 1..86400。默认 5。",
        "dwOpt": "选项位掩码。Bit0 = 1 同步时也写硬件 RTC；= 0 仅软件同步。默认 1。",
        "tTimeout": _ADS_TIMEOUT_DESC,
        "bValid": "TRUE 表示 `systemTime` 已装载有效值；首次同步未完成或被禁用时为 FALSE。",
        "systemTime": "同步后的本地系统时间，`TIMESTRUCT` 结构。",
        "tzID": "当前时区标识：`eTimeZoneID_Standard` / `eTimeZoneID_Daylight` / `eTimeZoneID_Invalid`。",
    },
    scenario="CX 工控机首次上电后把 Windows 时间同步到 PLC，让 HMI 日志、报表时间戳与桌面时钟一致；按 5 秒周期重同步抗漂移。",
    value="不用本 FB 时需要组合 `NT_GetTime` + `RTC_EX2` + `FB_GetTimeZoneInformation` 三个底层调用并自己维护同步状态机，本 FB 一行调用替代约 30 行手写代码。",
    alt=(
        "- `NT_GetTime`：只能单次读取，不能周期同步。\n"
        "- `RTC_EX2`：能走时但与 Windows 时钟不同步，会漂移。\n"
        "- **本 FB**：两者组合并自动重同步，是 Tc2_Utilities 推荐方案。"
    ),
    xml_scen="CX5020 上电后把本地 Windows 时间同步到 PLC；每 5 秒重同步并校准硬件 RTC（dwOpt = 1）。",
    xml_val="替代手写 NT_GetTime + RTC_EX2 + 时区查询 + 状态机约 30 行代码。",
    xml_verify="登录后写 bEnableSync := TRUE；观察 bTimeValid 在 1-2 个 PLC 周期后变 TRUE；stCurrentTime 应与桌面时钟一致；5 秒后再次刷新。",
    xml_extra_vars=[
        ("bEnableSync", "BOOL", "FALSE", "在线置 TRUE 触发首次同步"),
        ("stCurrentTime", "TIMESTRUCT", None, "同步出来的系统时间，monitor 此值"),
        ("bTimeValid", "BOOL", None, "首次同步成功后置 TRUE"),
        ("eCurrentTz", "E_TimeZoneID", None, "当前时区标识"),
    ],
    xml_call=(
        "fbLocalSystemTime(\n"
        "    sNetID := '',\n"
        "    bEnable := bEnableSync,\n"
        "    dwCycle := 5,\n"
        "    dwOpt := 1,\n"
        "    tTimeout := DEFAULT_ADS_TIMEOUT,\n"
        "    bValid => bTimeValid,\n"
        "    systemTime => stCurrentTime,\n"
        "    tzID => eCurrentTz\n"
        ");"
    ),
    related=["NT_GetTime", "RTC_EX2", "FB_GetTimeZoneInformation", "NT_SetTimeToRTCTime"],
)
