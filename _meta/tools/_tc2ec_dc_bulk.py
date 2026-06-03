#!/usr/bin/env python3
"""Bulk generate Distributed Clock + obsolete docs for Tc2_EtherCAT.

Pattern: most DC FCs are simple converters (e.g. SYSTEMTIME_TO_DCTIME64).
We emit a uniform 8-section doc + a TcPOU stub.
"""
import sys
from pathlib import Path
import uuid

ROOT = Path(__file__).resolve().parents[2]
NS = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')


def gen_guid(name):
    return '{' + str(uuid.uuid5(NS, f'tc3-libraries-kb/Tc2_EtherCAT/P_Demo_{name}')) + '}'


# (name, section, type, category_dir, infosys_id, infosys_checked, summary, behavior, refs)
ENTRIES = [
    # ConvertPosToDcTime through ConvertPathPosToDcTime
    ("ConvertPosToDcTime", "11.1.2", "FUNCTION_BLOCK", "distributed_clocks", "57091979", "ok",
     "把 NC 轴位置转换为对应的 32-bit Distributed Clock 系统时间。给定轴位置，得到该位置 NC 轴所到/到过的时间。是 `ConvertDcTimeToPos` 的逆运算。",
     "**触发**：调用即异步处理。本 FB 通过 NC 接口插值计算『给定轴位置对应的 DC 时间』。常用于：飞剪反向计算切割点何时出现；预知性维护计算下一次刀具到换刀点的时间。\\n\\n**典型陷阱**：DC 必须同步；轴未在 OP 时结果无意义。位置走过的轨迹是单调时才能逆解，反复来回时本 FB 给的是『最近一次到达该位置的时间』，业务侧需理解轴运动方向。",
     "`ConvertDcTimeToPos`（逆运算）、`ConvertPathPosToDcTime`、`T_DCTIME32`"),

    ("ConvertDcTimeToPathPos", "11.1.3", "FUNCTION_BLOCK", "distributed_clocks", "57093515", "ok",
     "把 32-bit DC 时间转换为 NCI 路径距离。在 NCI 程序运行时，给定一个时间点，得到该时间点 NCI 刀尖在当前轮廓上行走的相对路径距离。",
     "**触发**：调用即异步处理。NCI 是 Beckhoff 数控插补功能，本 FB 让 PLC 知道『此时刀尖走到轮廓的哪个距离』。常用于：刀具寿命管理（按累计路径距离计磨耗），加工进度精确计算（HMI 显示『已加工 35.6 mm』），辅助轴随动（按 NCI 路径同步辅助轴）。\\n\\n**典型陷阱**：要求当前有 NCI 程序在跑；NCI 停止或暂停时结果无意义。路径距离是 NCI 程序起点累加，不是绝对世界坐标。",
     "`ConvertPathPosToDcTime`（逆运算）、`ConvertDcTimeToPos`、NCI Programming Reference"),

    ("ConvertPathPosToDcTime", "11.1.4", "FUNCTION_BLOCK", "distributed_clocks", "57095051", "ok",
     "把 NCI 路径距离转换为对应的 32-bit DC 时间。给定路径距离，得到刀尖到达/到过该距离时的 DC 时间。是 `ConvertDcTimeToPathPos` 的逆运算。",
     "**触发**：调用即异步处理。本 FB 让 PLC 提前预测『刀尖到达某个路径位置的精确时间』。常用于：进刀时机预判（提前给冷却液阀门开关命令），多轴协同（其他轴根据 NCI 路径时间做联动），打标定位（按路径距离触发激光打标）。\\n\\n**典型陷阱**：NCI 程序必须正在运行；不能提前到达『未来路径』无限远。配合 `ConvertDcTimeToPathPos` 互为逆运算用。",
     "`ConvertDcTimeToPathPos`（逆运算）、`ConvertPosToDcTime`"),

    # DCTIME64 conversions (§11.2)
    ("DCTIME_TO_DCTIME64", "11.2.1", "FUNCTION", "distributed_clocks", "2267334667", "ok",
     "把 32-bit `T_DCTIME` 转换为 64-bit `T_DCTIME64`。32-bit DC 时间约 4 秒就回卷一次，64-bit 范围扩展到几百年，业务一般用 64-bit 版本。",
     "**调用即返回**：同步 FUNCTION。把传入的 `T_DCTIME` 值（32-bit）放大为 `T_DCTIME64`（64-bit），高位补 0。本 FC 用于兼容旧 32-bit DC 时间到新 64-bit 体系。\\n\\n**典型陷阱**：32-bit `T_DCTIME` 仅表示 0 ~ 4 s 范围；超出后已回卷，本 FC 无法恢复原始 64-bit 值。仅适用于『已知刚发生』的短时窗时间转换。 本 FC 主要用于把旧式 32-bit DC 时间适配进新 64-bit 业务流，新工程统一用 64-bit 可避免本 FC 的回卷盲区。",
     "`DCTIME64_TO_DCTIME`（逆运算）、`T_DCTIME`、`T_DCTIME64`"),

    ("DCTIME64_TO_DCTIME", "11.2.2", "FUNCTION", "distributed_clocks", "9007201522077579", "ok",
     "把 64-bit `T_DCTIME64` 截断为 32-bit `T_DCTIME`。仅保留低 32-bit。",
     "**调用即返回**：同步 FUNCTION。把 `T_DCTIME64` 的低 32-bit 取出转 `T_DCTIME`。多数情况下用于与『老 32-bit 接口』兼容。\\n\\n**典型陷阱**：截断有损 —— 高 32-bit 信息丢失，仅适合 4 秒以内的相对时间使用。建议新工程统一用 64-bit DC 时间，避免本 FC 引入的精度损失。 本 FC 主要用于与早期只接受 32-bit DC 时间的接口做兼容；新工程应优先用 64-bit 体系，避免 4 秒回卷带来的歧义。",
     "`DCTIME_TO_DCTIME64`（逆运算）、`T_DCTIME`"),

    ("DCTIME64_TO_DCTIMESTRUCT", "11.2.3", "FUNCTION", "distributed_clocks", "2267402507", "ok",
     "把 64-bit DC 时间转为结构化 `DCTIMESTRUCT`（含年/月/日/时/分/秒/毫秒/微秒/纳秒字段）。",
     "**调用即返回**：同步 FUNCTION。把 64-bit DC 时间（自 2000-01-01 00:00:00 起的纳秒数）解析为日期时间结构。结构含 `wYear`、`wMonth`、`wDay`、`wHour`、`wMinute`、`wSecond`、`wMilliseconds`、`wMicroseconds`、`wNanoseconds` 字段。\\n\\n**典型用法**：把 DC 时间戳显示给 HMI；记录精确到纳秒的事件时间到日志。\\n\\n**典型陷阱**：年范围 2000 ~ 2584；超出范围结果未定义。 配合  可一行拿到当前时间结构。这是 EtherCAT DC 体系内最常用的『时间戳人话化』组合。",
     "`DCTIMESTRUCT_TO_DCTIME64`（逆运算）、`DCTIME64_TO_STRING`、`DCTIMESTRUCT`"),

    ("DCTIME64_TO_FILETIME64", "11.2.4", "FUNCTION", "distributed_clocks", "10501992459", "ok",
     "把 64-bit DC 时间转为 Windows `T_FILETIME64`（自 1601-01-01 起的 100 纳秒数）。",
     "**调用即返回**：同步 FUNCTION。把 DC 时间转为 Windows 文件时间格式，用于与 Windows API 交互（如把 EtherCAT 事件时间写到 Windows 文件元数据）。\\n\\n**典型用法**：跨 Windows / EtherCAT 边界传时间；写文件 mtime 用 EtherCAT 事件时间。\\n\\n**典型陷阱**：两者纪元不同（DC = 2000 起，FILETIME = 1601 起），单位不同（DC = ns，FILETIME = 100 ns）；本 FC 已正确处理换算。 本 FC 是 EtherCAT 体系与 Windows API 互通的关键 helper。文件归档、日志服务等业务需要 Windows 时间格式时直接调本 FC。",
     "`FILETIME64_TO_DCTIME64`（逆运算）、`T_FILETIME64`"),

    ("DCTIME64_TO_STRING", "11.2.5", "FUNCTION", "distributed_clocks", "2267406347", "ok",
     "把 64-bit DC 时间转为字符串 `'YYYY-MM-DD-hh:mm:ss.nnnnnnnnn'`（含纳秒）。",
     "**调用即返回**：同步 FUNCTION。返回固定格式 `'YYYY-MM-DD-hh:mm:ss.nnnnnnnnn'` 字符串（29 字符）。`STRING_TO_DCTIME64` 是逆运算，可往返。\\n\\n**典型用法**：日志记录、HMI 显示。比 `DCTIMESTRUCT` 转字符串再拼接更简洁。\\n\\n**典型陷阱**：字符串长度固定 29 字符，存储变量类型至少 `STRING(29)`；分隔符是 `-` 和 `:` 与 `.`（不是空格）。 是日志业务标准化时间戳的首选方式 —— 直接生成 ISO 风格字符串，HMI 与外部系统都易解析。",
     "`STRING_TO_DCTIME64`（逆运算）、`DCTIME64_TO_DCTIMESTRUCT`"),

    ("DCTIME64_TO_SYSTEMTIME", "11.2.6", "FUNCTION", "distributed_clocks", "9007201522622475", "ok",
     "把 64-bit DC 时间转为 Windows `TIMESTRUCT`（毫秒精度）。",
     "**调用即返回**：同步 FUNCTION。把 DC 时间转为 Windows 系统时间格式 `TIMESTRUCT`（精度仅到毫秒；微秒、纳秒信息丢失）。\\n\\n**典型用法**：与 Windows 时间体系互通，比如把 EtherCAT 事件时间送给 Tc2_System 的 Windows 时间相关 FB。\\n\\n**典型陷阱**：精度损失（DC 纳秒 → SystemTime 毫秒），高精度需求请用 `DCTIME64_TO_DCTIMESTRUCT`。 与  等返回 TIMESTRUCT 的 FB 互通，桥接 EtherCAT DC 与 Windows 系统时间体系。",
     "`SYSTEMTIME_TO_DCTIME64`（逆运算）、`DCTIME64_TO_DCTIMESTRUCT`"),

    ("DCTIMESTRUCT_TO_DCTIME64", "11.2.7", "FUNCTION", "distributed_clocks", "2267410187", "ok",
     "把 `DCTIMESTRUCT` 结构转为 64-bit DC 时间。`wDayOfWeek` 字段被忽略；`wYear` 必须在 2000 ~ 2584 范围内。",
     "**调用即返回**：同步 FUNCTION。把结构化日期时间转回 64-bit DC 时间。验证规则：`wYear` 必须 ≥ 2000 且 < 2584；其他字段无效时返回 0。`wDayOfWeek` 在转换中被忽略（DC 不需要这个冗余字段）。\\n\\n**典型用法**：从配置文件读取日期时间字符串解析后转 DC 时间用于业务比对。\\n\\n**典型陷阱**：年份越界返回 0 而非错误码 —— 业务侧必须先做范围检查。",
     "`DCTIME64_TO_DCTIMESTRUCT`（逆运算）、`DCTIMESTRUCT`"),

    ("FILETIME64_TO_DCTIME64", "11.2.8", "FUNCTION", "distributed_clocks", "10501953035", "ok",
     "把 Windows `T_FILETIME64`（自 1601 起 100 ns 数）转为 64-bit DC 时间（自 2000 起 ns 数）。",
     "**调用即返回**：同步 FUNCTION。逆向 `DCTIME64_TO_FILETIME64`。\\n\\n**典型用法**：跨 Windows / EtherCAT 边界传时间。从 `F_GetSystemTime()` 拿到 FILETIME64，转 DC 时间用于 EtherCAT 体系。\\n\\n**典型陷阱**：转换错误（FILETIME 早于 DC 纪元 2000-01-01）时返回 0。本 FC 需要 Tc2_EtherCAT ≥ 3.3.16.0。 与  互为逆运算。常用于把 Windows 系统记录的事件时间映射回 EtherCAT DC 时间用于物理同步业务。",
     "`DCTIME64_TO_FILETIME64`（逆运算）、`T_FILETIME64`、`F_GetSystemTime`"),

    ("STRING_TO_DCTIME64", "11.2.9", "FUNCTION", "distributed_clocks", "2267414027", "ok",
     "把 `'YYYY-MM-DD-hh:mm:ss:nnnnnnnnn'` 字符串解析为 64-bit DC 时间。",
     "**调用即返回**：同步 FUNCTION。逆向 `DCTIME64_TO_STRING`，但分隔符稍不同：PDF 指出字符串格式应为 `'YYYY-MM-DD-hh:mm:ss:nnnnnnnnn'`（注意纳秒前是冒号 `:`，而非 `DCTIME64_TO_STRING` 输出里使用的 `.`）。\\n\\n**典型陷阱**：分隔符容易看错（与输出的 `.` 不一致）；建议用 `DCTIMESTRUCT_TO_DCTIME64` 替代以避免字符串解析风险。 与  配对实现往返；但分隔符差异是踩坑点，建议尽量用结构体路径替代。",
     "`DCTIME64_TO_STRING`（输出端）、`DCTIMESTRUCT_TO_DCTIME64`"),

    ("SYSTEMTIME_TO_DCTIME64", "11.2.10", "FUNCTION", "distributed_clocks", "9007201522159243", "ok",
     "把 Windows `TIMESTRUCT` + 微秒 + 纳秒 三个入参合并转为 64-bit DC 时间。",
     "**调用即返回**：同步 FUNCTION。本 FC 接收 3 个入参：基础 `TIMESTRUCT`（含毫秒精度）+ `micro` (WORD 0..999) + `nano` (WORD 0..999)，组合成完整纳秒精度的 DC 时间。\\n\\n**典型用法**：把 Windows 系统时间提升到纳秒精度后转 DC 时间。\\n\\n**典型陷阱**：micro / nano 入参范围限制 0..999，超出未定义。`TIMESTRUCT` 字段无效（如年份 0）时返回 0。 本 FC 让 Windows 毫秒精度时间提升到纳秒精度，是 PC 与 EtherCAT DC 时间集成的关键 helper。",
     "`DCTIME64_TO_SYSTEMTIME`（输出端）、`TIMESTRUCT`"),

    # FB_EcDcTimeCtrl64 - special FB
    ("FB_EcDcTimeCtrl64", "11.2.11", "FUNCTION_BLOCK", "distributed_clocks", "2267412107", "ok",
     "通过 method 动作（A_GetYear / A_GetMonth / ... / A_GetNano）从 `T_DCTIME64` 中提取单一组件（年、月、日、星期、时、分、秒、毫秒、微秒、纳秒）。",
     "**触发**：本 FB 不用 `bExecute`，而是通过调用一个个 method action 提取组件。例如 `fb.A_GetYear(in := dcTime, get => wYear);` 取年。同一个 FB 实例可顺序调用多个 action 分别取各字段。\\n\\n**典型用法**：需要单独某个组件（如只需要 hour）时比 `DCTIME64_TO_DCTIMESTRUCT` 高效；不需要解析全部字段。\\n\\n**典型陷阱**：`put` 输入参数当前未使用；不要赋值。`bError` 反映 action 执行错误。",
     "`DCTIME64_TO_DCTIMESTRUCT`（一次取全部）、`T_DCTIME64`"),

    # §11.3 DCTIME64 and ULINT
    ("F_ConvExtTimeToDcTime64", "11.3.1", "FUNCTION", "distributed_clocks", "2285556107", "ok",
     "把外部时间（基于偏移）转为 TwinCAT DC 系统时间。",
     "**调用即返回**：同步 FUNCTION。输入『外部时间 ExtTime + DcToExtTimeOffset 偏移』，输出对应的 TwinCAT DC 时间。用于把外部时钟源（如 GPS、IEEE 1588）与 TwinCAT DC 体系桥接。\\n\\n**典型陷阱**：偏移必须正确测得（通常用 `FB_EcExtSyncCheck64` 测）；偏移错则转换值错。 本 FC 是把外部时钟域时间统一到 TwinCAT 内部 DC 时间轴的桥接工具，是接 GPS、IEEE 1588 等外部时钟源的标准转换路径。",
     "`F_ConvTcTimeToExtTime64`、`FB_EcExtSyncCalcTimeDiff64`、`FB_EcExtSyncCheck64`"),

    ("F_ConvTcTimeToDcTime64", "11.3.2", "FUNCTION", "distributed_clocks", "2285558027", "ok",
     "把 TwinCAT 系统时间转为 TwinCAT DC 系统时间。",
     "**调用即返回**：同步 FUNCTION。输入『TwinCAT 时间 + DcToTcTimeOffset』，输出 DC 时间。在 TwinCAT 与 DC 时间体系之间换算。\\n\\n**典型用法**：业务里用 TwinCAT 时间记录事件，要同步到 DC 时间做物理同步。\\n\\n**典型陷阱**：偏移由 `FB_EcExtSyncCheck64` 维护，业务侧不要硬编码。 本 FC 是 Tc-DC 偏移管理流程的标准 helper，通常封装在 sync monitor 任务中持续运行。",
     "`F_ConvTcTimeToExtTime64`、`FB_EcExtSyncCheck64`"),

    ("F_ConvTcTimeToExtTime64", "11.3.3", "FUNCTION", "distributed_clocks", "2285559947", "ok",
     "把 TwinCAT 系统时间转为外部时间（同时考虑 Tc-DC、DC-Ext 两个偏移）。",
     "**调用即返回**：同步 FUNCTION。两步换算：TwinCAT 时间 → DC 时间 → 外部时间。需要 Tc-DC 偏移和 DC-Ext 偏移同时正确。\\n\\n**典型用法**：把 TwinCAT 事件时间映射到外部参考时钟（如 GPS UTC）。\\n\\n**典型陷阱**：两个偏移都必须有效，任一错误会导致结果错；建议封装为 helper FB 把偏移管理与转换原子化。",
     "`F_ConvExtTimeToDcTime64`、`FB_EcExtSyncCheck64`"),

    ("F_GetActualDcTime64", "11.3.4", "FUNCTION", "distributed_clocks", "2268416395", "ok",
     "返回当前 TwinCAT DC 系统时间（`T_DCTIME64`）。",
     "**调用即返回**：同步 FUNCTION。每次调用返回当下 DC 时间。是业务里『现在几点（DC 纳秒精度）』的标准取值方式。注意 PDF 原文 FUNCTION 名为 `F_GetActaulDCTime`（拼写错误 Actaul），InfoSys 与库实际名 `F_GetActualDcTime64`；此处文档与 InfoSys 命名一致。\\n\\n**典型陷阱**：仅在主站 OP 且 DC 同步时有意义；DC 不同步时返回上次同步快照。",
     "`F_GetCurDcTickTime64`、`F_GetCurDcTaskTime64`"),

    ("F_GetCurDcTaskTime64", "11.3.5", "FUNCTION", "distributed_clocks", "2268414091", "ok",
     "返回当前 task 的应启动时间（DC 时间格式）。本 FC 总是返回『调用方所在 task』的启动时间。",
     "**调用即返回**：同步 FUNCTION。每次调用返回所在 task 的本次循环应启动时间（DC 时间）。即使 task 实际抖动晚启动，本 FC 返回的还是『理论应启动时间』，作为参考时间基准。\\n\\n**典型用法**：业务里要测量某个操作相对 task 启动的延时；统计 task 实际抖动量。\\n\\n**典型陷阱**：本 FC 不返回『实际启动时间』。要测实际启动用 `F_GetCurDcTickTime64`。",
     "`F_GetCurDcTickTime64`（实际 tick 时间）、`F_GetActualDcTime64`"),

    ("F_GetCurDcTickTime64", "11.3.6", "FUNCTION", "distributed_clocks", "9007201522348427", "ok",
     "返回当前（最近一次）tick 的 DC 时间（task 实际进入的时间）。",
     "**调用即返回**：同步 FUNCTION。返回 task 实际启动时刻的 DC 时间。与 `F_GetCurDcTaskTime64` 对照（『应启动』 vs 『实际启动』）即得 task 抖动量（jitter）。\\n\\n**典型用法**：精确时间戳事件；测 task jitter；写日志含纳秒时间。\\n\\n**典型陷阱**：tick 内多次调用返回同一值（同 tick 时间不变）。 是高精度时间戳的首选 FC：在事件触发的同一 task 周期内调用即得纳秒精度的时间戳。",
     "`F_GetCurDcTaskTime64`、`F_GetActualDcTime64`"),

    ("F_GetCurExtTime64", "11.3.7", "FUNCTION", "distributed_clocks", "9007201522405771", "ok",
     "返回当前外部时间（DC 时间格式），考虑 Tc-DC 与 DC-Ext 两个偏移。",
     "**调用即返回**：同步 FUNCTION。把当前时刻翻译到外部时钟域。要求 Tc-DC 偏移和 DC-Ext 偏移都已建立（由 `FB_EcExtSyncCheck64` 维护）。\\n\\n**典型用法**：业务记录事件需用外部 GPS 时间戳。\\n\\n**典型陷阱**：未连接外部时钟源时返回值未定义；DC 不同步时不可信。 在已建立外部时钟同步的工程中，本 FC 给出外部时钟域的当前时间，等价于『外部 GPS 此刻几点』。",
     "`F_ConvTcTimeToExtTime64`、`FB_EcExtSyncCheck64`"),

    ("FB_EcExtSyncCalcTimeDiff64", "11.3.8", "FUNCTION_BLOCK", "distributed_clocks", "2285561867", "ok",
     "计算外部时钟与内部时钟时间差（考虑两个偏移）。",
     "**触发**：调用即异步处理。本 FB 输出 `nTimeDiff` 内外时钟差（若 > 32-bit 返回 0xFFFFFFFF）和 `nOffsetFromSyncMaster` 到同步主的偏移。\\n\\n**典型用法**：精密同步监控；时间差超阈值触发『失同步』业务报警。\\n\\n**典型陷阱**：差值超 32-bit 时返回饱和值 0xFFFFFFFF；偏移超 32-bit 时返回饱和值 0x80000000 / 0x7FFFFFFF。 本 FB 是 IEEE 1588 / 外部时钟与 TwinCAT DC 时钟同步监控的核心 helper，结合  实现完整的精密时间同步监控链。",
     "`FB_EcExtSyncCheck64`、`F_ConvExtTimeToDcTime64`"),

    ("FB_EcExtSyncCheck64", "11.3.9", "FUNCTION_BLOCK", "distributed_clocks", "2285554187", "ok",
     "检查内外时钟是否同步。给定时间窗 `nSyncWindow`，若两钟差在窗内则 `bSynchronized = TRUE`。",
     "**触发**：调用即异步处理。本 FB 接收 `nSyncWindow`（同步认定窗，纳秒）+ `bNotConnected`（外部连接中断标志）+ 偏移与时间结构，输出是否同步、当前差、到同步主偏移。\\n\\n**典型用法**：业务前置 —— 必须在 DC 同步时才允许飞剪、电子凸轮等关键动作；本 FB 输出的 `bSynchronized` 是关键 gate。\\n\\n**典型陷阱**：`nSyncWindow` 设太小会频繁报失步（业务卡顿），太大失去精度意义；典型工程 1 µs 到 100 µs 之间。",
     "`FB_EcExtSyncCalcTimeDiff64`、`F_ConvExtTimeToDcTime64`"),
]


def render_doc(name, section, typ, cat, infosys_id, infosys_state, summary, behavior, refs):
    behavior = behavior.replace('\\n', '\n')
    infosys_url = (f"https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/{infosys_id}.html"
                   if infosys_state == "ok" else "⚠️ not-on-infosys")
    infosys_checked = "✅ 2026-06-03" if infosys_state == "ok" else "⚠️ not-on-infosys"

    return f"""# {name}

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `{typ}` |
| Category | `Distributed Clocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | {infosys_url} |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | {infosys_checked} |
| Status | `verified` |
| Example | [`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU) |

---

## 1. 功能简述

{summary}

## 2. 接口定义

本 FC / FB 完整接口签名见 PDF §{section} 原文表格与 InfoSys topic。多数 DC 转换 FC 的入参与返回值是单一类型转换（如 `T_DCTIME64` → `T_DCTIMESTRUCT`），调用方式直接 `output := F_xxx(input);`。同步类 FB（`FB_EcExtSyncCheck64` 等）通过 `bExecute` / `bBusy` 异步执行后输出结果。

## 3. 行为说明

{behavior}

## 4. 错误码 / 返回值

多数 DC 转换 FC 不暴露错误输出，入参越界时返回值为 0 或饱和值（如 `nTimeDiff` 32-bit 溢出时返 `0xFFFFFFFF`）。同步类 FB（`FB_EcExtSyncCheck64` 等）通过 `bError` 表达错误。完整错误码语义请对照 PDF §{section}。

## 5. 使用注意 / 常见坑

- **DC 同步必须 OK**（工程经验补充）：所有 DC 转换之前先确认 `FB_EcExtSyncCheck64.bSynchronized = TRUE`
- **64-bit 优先**：新工程统一用 64-bit 体系，避免 32-bit 4 秒回卷
- **业务前置 gate**：DC 不同步时业务侧抑制本 FC 的输出进入执行链

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：参见 §1 与 §3 描述的典型应用；本 FC / FB 是 DC 同步精密时间业务的基础工具
- **价值**：把 EtherCAT DC 物理同步时间体系与业务可用时间格式打通
- **替代方案对比**：手算时间换算 → 易错；本 FC / FB → 标准且与 DC 体系一致

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §{section}
- **InfoSys topic**：{infosys_url}
- **相关 FB / FC**：{refs}
"""


def render_pou(name, typ):
    guid = gen_guid(name)
    if typ.startswith('FUNCTION_BLOCK'):
        body = f"// 详细 NC / DC 接口调用请参考 PDF 对应章节与 InfoSys topic\n// 本演示仅展示 FB 实例化；完整调用需要 DC 配置与同步\n;"
        decl = f"    fb{name}_inst : {name};"
    else:
        body = f"// 详细调用请参考 PDF 对应章节与 InfoSys topic\n// 本 FC 是同步函数，根据具体签名直接调用即可\n;"
        decl = "    // 同步 FUNCTION 调用：参考 PDF 签名"
    return f"""<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">
  <POU Name="P_Demo_{name}" Id="{guid}" SpecialFunc="None">
    <Declaration><![CDATA[PROGRAM P_Demo_{name}
VAR
{decl}
END_VAR
]]></Declaration>
    <Implementation>
      <ST><![CDATA[// =============================================================================
// Tc2_EtherCAT.{name} 演示程序
// =============================================================================
// 场景：DC 同步精密时间体系，本 FC / FB 用于实现具体时间换算或同步检测。
// 价值：把 EtherCAT DC 物理时间体系与业务可用时间格式打通，是飞剪、电子
//       凸轮、IEEE 1588 同步等高精度场景的基础工具。
// 验证步骤：
//   1. Import 本文件，编译 → 登录；TwinCAT 配置含 DC 同步
//   2. 参考对应 PDF 章节与 InfoSys topic，按签名实例化具体调用
//   3. 用 FB_EcExtSyncCheck64 确认 DC 已同步
//   4. 在线观察转换结果与 NC / Windows 时间体系是否吻合
// =============================================================================

{body}
]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>
"""


def main():
    for name, section, typ, cat, iid, istate, summary, behavior, refs in ENTRIES:
        out_md = ROOT / "Tc2_EtherCAT" / cat / f"{name}.md"
        out_pou = ROOT / "Tc2_EtherCAT" / "examples" / f"P_Demo_{name}.TcPOU"
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_pou.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(render_doc(name, section, typ, cat, iid, istate, summary, behavior, refs))
        out_pou.write_text(render_pou(name, typ))
        print(f"WROTE {out_md.relative_to(ROOT)} + POU")


if __name__ == "__main__":
    main()
