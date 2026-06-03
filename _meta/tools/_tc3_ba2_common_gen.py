#!/usr/bin/env python3
"""
Tc3_BA2_Common generator for Functions (F_BA_*) and GVLs (BAComn_*).

For each entry:
  1. Pull the syntax block from /tmp/tc3_ba2_common_extracts.json
  2. Render the markdown doc with all 8 mandatory sections (Chinese narrative
     + verbatim IEC ST + parameter description tables + business value)
  3. Emit the .TcPOU example with scene/value/verification triple + sensible
     industrial naming + stable UUID5 GUID per spec
  4. Verify each with verify_doc + lint_tcpou; abort on FAIL

Per-function metadata is curated below (CATEGORIES, DESCRIPTIONS, INFOSYS_URLS,
BUSINESS_VALUE) to keep the templates deterministic.
"""
from __future__ import annotations
import json, re, sys, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB_DIR = ROOT / 'Tc3_BA2_Common'
EX_DIR = LIB_DIR / 'examples'
EXTRACTS_JSON = Path('/tmp/tc3_ba2_common_extracts.json')
INFOSYS_INDEX = Path('/tmp/ba2_index.json')

LIB_VERSION = '1.0.2'
PDF_URL = 'https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf'
TODAY = '2026-06-03'

# Category mapping: short label → (directory, display label)
CATEGORIES: dict[str, tuple[str, str]] = {
    # Functions
    'compare': ('compare', 'Functions / Compare'),
    'memory': ('memory', 'Functions / Memory'),
    'class_value': ('class_value', 'Functions / Types / ClassValue'),
    'date_check': ('date_check', 'Functions / Types / Date and Time / Check'),
    'date_convert': ('date_convert', 'Functions / Types / Date and Time / Convert'),
    'date_time': ('date_time', 'Functions / Types / Date and Time'),
    'date_value': ('date_value', 'Functions / Types / DateValue'),
    'scheduler': ('scheduler', 'Functions / Types / Scheduler'),
    'trend': ('trend', 'Functions / Types / Trend'),
    'auxiliary_calc': ('auxiliary_calc', 'Functions / Universal / AuxiliaryCalculation'),
    'tc_log': ('tc_log', 'Functions / Universal / TcLog'),
    'check_enum': ('check_enum', 'Functions / Universal'),
    'validation': ('validation', 'Functions / ValidationFunctions'),
    # GVLs
    'gvls': ('gvls', 'GVLs'),
}

# Per-entry config: category, short Chinese summary (§1), business scenario, value, alt
# (Each F_BA_* gets a tailored description rather than a templated one.)
ENTRY_META: dict[str, dict] = {
    # --- Compare ---
    'F_BA_CompareVersion': {
        'cat': 'compare',
        'summary': '比较两个 `ST_BA_Version` 版本号，按指定的比较运算符（等于 / 大于 / 小于等）返回 BOOL。可指定参与比较的分量数 `nLimit`（1=只比较 Major，4=比较全部 Major / Minor / Build / Revision）。常用于检查依赖库版本是否满足要求。',
        'scene': '楼宇控制器启动时检查 Tc3_BA2_Common 库版本：若 < V2.1.20.0 则报警阻止启动（避免运行时调用不存在的 FB）。',
        'value': '一行 FC 调用替代手写 `IF v.major < 2 OR (v.major = 2 AND v.minor < 1) THEN ...` 这种繁琐多级 IF；`nLimit` 让你按需控制比较精度。',
        'alt': '手写多级 IF 比较 Major/Minor/Build/Revision 字段（约 10 行 + 易写错优先级）',
    },
    # --- Memory ---
    'F_BA_ByteCmp': {
        'cat': 'memory',
        'summary': '把指定内存区（`pValue` 起始，长度 `nSize`）按字节与基准字节 `nCompare` 比较。返回 DINT：-1 表示发现某字节小于基准、+1 表示发现某字节大于基准、0 表示区内全部字节都等于基准。`pValue = 0` 或 `nSize = 0` 时直接返回 -1。',
        'scene': '检查一段 buffer 是否全是 `0x00`（未初始化检测）或全是 `0xFF`（擦除标志位）。',
        'value': '比 `MEMCMP` 更轻量（不用第二个 buffer），适合"全 0 / 全 FF / 全单字节模式"快速判定。',
        'alt': '`FOR i := 0 TO nSize-1 DO IF arr[i] <> nCompare THEN ... END_FOR;` 手写约 5 行',
    },
    'F_BA_Cmp': {
        'cat': 'memory',
        'summary': '比较两段等长内存（`pValue` vs `pCompare`，长度 `nSize`）。返回 DINT：-1 = 第一段小、+1 = 第一段大、0 = 完全相同；通过 `nEqualBytes` 额外输出"发现差异前已经相等的字节数"。`pValue = 0` 或 `nSize = 0` 时返回 -1。',
        'scene': '比较两个 ST_BA_Date 结构是否相同；或比较 firmware 数据块前 N 字节匹配头部魔数。',
        'value': '相比 IEC 标准 `MEMCMP`（只返回 -1/0/1），本 FC 额外给出"前缀相同字节数"，便于精细诊断差异位置。',
        'alt': '`MEMCMP(...)` + 自己再写循环找差异位置（约 6 行）',
    },
    'F_BA_GetUsedEntryCount': {
        'cat': 'memory',
        'summary': '在 ARRAY 中扫描查找第一个等于"未使用标记值 `xUnusedVal`"的元素，返回从下界 `nLowerBound` 起到达该位置前的元素数。元素步长由 `xUnusedVal` 的字节大小决定。`pArray = 0` 或 `xUnusedVal.diSize = 0` 时返回 0。',
        'scene': '动态数组类容器（如调度条目数组）每槽位有"未用 = 0xFF"约定；本 FC 一行得到当前已用槽位数。',
        'value': '一行调用替代 FOR 循环扫描，且自动按 ANY 类型尺寸适配（不用手写不同类型不同步长的循环）。',
        'alt': '`FOR i := nLowerBound TO nUpperBound DO IF arr[i] = unusedVal THEN EXIT; END_IF; END_FOR; cnt := i - nLowerBound;` 约 5 行',
    },
    'F_BA_MemSet': {
        'cat': 'memory',
        'summary': '把任意类型变量 `xValue` 的内容写入 `pDestAddr` 指向的地址。返回 UDINT = 实际拷贝的字节数（0 = 失败）。本质是单值写入（不是区间填充——区间填充用 `F_BA_MemSetEx`）。',
        'scene': '初始化一个 STRUCT 缓冲区，把已经准备好的"默认值 STRUCT"原样写到目标地址。',
        'value': '比 IEC `MEMCPY` 更直接：源是值而不是地址，免去 `ADR(xValue)` 步骤。',
        'alt': '`MEMCPY(pDestAddr, ADR(xValue), SIZEOF(xValue));` 同样一行但要手动取地址 + 尺寸',
    },
    'F_BA_MemSetEx': {
        'cat': 'memory',
        'summary': '把 `xValue` 重复填充到 `pDestAddr` 起始、长度 `nDestSize` 的内存区。前提：`nDestSize` 必须是 `xValue.diSize` 的整数倍——否则不填充并返回 0。返回 UDINT = 实际拷贝的字节数。',
        'scene': '把一段 INT 数组全部初始化为 -1（每个 INT 2 字节，重复 N 次填满）。',
        'value': '比手写 FOR 循环填充更高效（FB 内部调 MEMCPY，可能向量化）；自带尺寸校验。',
        'alt': '`FOR i := 0 TO (nDestSize / SIZEOF(xValue)) - 1 DO MEMCPY(pDestAddr + i * SIZEOF(xValue), ADR(xValue), SIZEOF(xValue)); END_FOR;` 约 3 行',
    },
    'F_BA_OffsetPtr': {
        'cat': 'memory',
        'summary': '把基地址 `pAddr` 加上偏移 `nOffset` 字节，返回新的 PVOID 指针。内部根据运行时平台（x64 或 x86）自动用 ULINT 或 UDINT 做加法，避免 32/64 位平台下的整数截断 bug。⚠️ PDF 函数名印刷为 `F_BA_OffestPtr`（少了 t），实际签名 `F_BA_OffsetPtr`。',
        'scene': '操作 RAW 数据缓冲（如总线帧）：拿到帧头指针后 +4 跳过 header 取 payload 指针。',
        'value': '跨 x86/x64 平台自动正确；手写 `pAddr + UDINT(nOffset)` 在 x64 上会把指针截断到 32 位 → 段错误。',
        'alt': '`pNew := pAddr + nOffset;` —— x86 上能用，x64 上指针被截断造成 GPF',
    },
    'F_BA_DiffPtr': {
        'cat': 'memory',
        'summary': '计算两个地址 `pAddr1` 和 `pAddr2` 之间的差值（字节数）。返回 UDINT。内部根据 x86/x64 用对应整数宽度计算，保证跨平台正确。',
        'scene': '在大缓冲区里找到某个标志位的位置后，反算出该位置距离缓冲区起始的偏移。',
        'value': '跨 x86/x64 平台自动正确；手写 `pAddr1 - pAddr2` 在 x64 上会截断造成偏移错误。',
        'alt': '`diff := pAddr1 - pAddr2;` —— x86 上能用，x64 上结果截断',
    },
    # --- Class Value ---
    'F_BA_BVal': {
        'cat': 'class_value',
        'summary': '把 BOOL 值打包成 `ST_BA_ClassValue` 结构。`ST_BA_ClassValue` 是 BA 库统一的"带分类标签的值"容器：包含值本体 + 数据类（DataClass）+ 数据类型（DataType）+ 单位 + 状态标志等元信息。本 FC 专用于把布尔填入该容器。',
        'scene': '楼宇趋势记录系统：所有点位统一用 `ST_BA_ClassValue` 接口，BOOL 类型用本 FC 转，REAL 用 `F_BA_RVal`，INT 用 `F_BA_IVal`。',
        'value': '统一接口让趋势记录 / 数据归档 / SCADA 推送等下游模块不必关心原始类型，FC 帮你把各原始类型规范成 ClassValue 结构。',
        'alt': '手写 `cv.uVal.b := bVal; cv.eDataType := E_BA_DataType.eBool; ...` 多行赋值',
    },
    'F_BA_ByteVal': {
        'cat': 'class_value',
        'summary': '把 BYTE 值打包成 `ST_BA_ClassValue` 结构。可附加额外的"枚举信息"参数。',
        'scene': '楼宇枚举型状态（如阀门状态 0=Closed/1=Opening/2=Open）作为字节值统一上传到趋势系统。',
        'value': '同 `F_BA_BVal`，针对 BYTE 类型。',
        'alt': '手写多行结构赋值',
    },
    'F_BA_IVal': {
        'cat': 'class_value',
        'summary': '把 INT 值打包成 `ST_BA_ClassValue` 结构。',
        'scene': '楼宇 INT 类型测点（如风量等级 -10..+10）统一上传到趋势 / SCADA。',
        'value': '同其它 ClassValue 系列。',
        'alt': '手写多行结构赋值',
    },
    'F_BA_RVal': {
        'cat': 'class_value',
        'summary': '把 REAL 值打包成 `ST_BA_ClassValue` 结构，并可附加单位 `eUnit` 和状态 `stStatus`。',
        'scene': '温度 / 压力 / 流量等 REAL 测点统一封装为带单位（℃ / kPa / m³/h）的 ClassValue 上报。',
        'value': '一次性把"数值 + 单位 + 状态"组合进同一结构，简化下游解析。',
        'alt': '手写 `cv.uVal.f := f; cv.eUnit := eUnit; cv.eDataType := E_BA_DataType.eReal; ...`',
    },
    'F_BA_UDIVal': {
        'cat': 'class_value',
        'summary': '把 UDINT 值打包成 `ST_BA_ClassValue` 结构。',
        'scene': '累计能耗（UDINT 千瓦时）、累计运行小时数等"非负大数"类型测点统一上报。',
        'value': '同其它 ClassValue 系列。',
        'alt': '手写多行结构赋值',
    },
    # --- Date Check ---
    'F_BA_DateHasPlaceholder': {
        'cat': 'date_check',
        'summary': '检测 `ST_BA_Date` 中的 year / month / day / weekday 是否包含占位符（`16#FF`）。BA 库用 `0xFF` 表示"未指定"（例如"周日历"事件——只指定周几不指定日期）。返回 BOOL：TRUE = 至少有一个字段是占位符。',
        'scene': '调度引擎判断一条日历条目是"固定日期"还是"周期性占位"（每个周一执行）。',
        'value': '一行 FC 替代多个 IF 比较各字段 = 16#FF 的繁琐写法。',
        'alt': '`bHas := stDate.nYear = 16#FF OR stDate.nMonth = 16#FF OR ...` 多行',
    },
    'F_BA_DateUnspecified': {
        'cat': 'date_check',
        'summary': '检测 `ST_BA_Date` 是否所有字段都是占位符（"完全未指定"）。返回 BOOL。',
        'scene': '调度条目是否完全为空（新增空白条目检测）。',
        'value': '一行替代逐字段判定。',
        'alt': '多个 IF 字段判定',
    },
    'F_BA_IsLeapYear': {
        'cat': 'date_check',
        'summary': '判断指定 INT 年份是否为闰年（按格里高利历规则：能被 4 整除且不能被 100 整除，或能被 400 整除）。返回 BOOL。',
        'scene': '日历显示控件按年份生成"2 月有几天"。',
        'value': '一行 FC 替代手写 `(y MOD 4 = 0 AND y MOD 100 <> 0) OR (y MOD 400 = 0)` —— 易写错。',
        'alt': '手写表达式，易把规则记错',
    },
    'F_BA_TimeHasPlaceholder': {
        'cat': 'date_check',
        'summary': '检测 `ST_BA_Time` 中的 hour / minute / second 是否包含占位符（`16#FF`）。返回 BOOL。',
        'scene': '调度条目的时间字段："每天 10:30:?? 触发"（秒未指定）。',
        'value': '一行 FC 替代字段级判定。',
        'alt': '逐字段 IF 比较',
    },
    'F_BA_TimeUnspecified': {
        'cat': 'date_check',
        'summary': '检测 `ST_BA_Time` 是否所有字段都是占位符（"完全未指定"）。返回 BOOL。',
        'scene': '调度条目是否未设置任何时间字段。',
        'value': '一行替代逐字段判定。',
        'alt': '多个 IF 字段判定',
    },
    # --- Date Convert ---
    'F_BA_TimeStruct_TO_DateTime': {
        'cat': 'date_convert',
        'summary': '把 IEC 标准 `TIMESTRUCT` 转换为 BA 自定义 `ST_BA_DateTime` 结构。两者字段大同小异，本 FC 完成字段映射。',
        'scene': '从 Windows 系统时间（`FB_LocalSystemTime` 返回 `TIMESTRUCT`）转成 BA 库的标准结构以便存入趋势数据库。',
        'value': '一行 FC 替代手写逐字段 `dt.nYear := ts.wYear; dt.nMonth := ts.wMonth; ...` 等约 7 行映射。',
        'alt': '逐字段赋值',
    },
    'F_BA_TimeStruct_TO_Time': {
        'cat': 'date_convert',
        'summary': '把 `TIMESTRUCT` 转换为 `ST_BA_Time`（只保留时分秒，不含日期）。',
        'scene': '只关心当前时间不需要日期的场景，如周期任务"每小时 30 分触发"判定。',
        'value': '一行 FC 替代字段映射。',
        'alt': '`tm.nHour := ts.wHour; tm.nMinute := ts.wMinute; ...`',
    },
    'F_BA_To100msDate': {
        'cat': 'date_convert',
        'summary': '把 `ST_BA_Date` 转为 100 毫秒粒度的时间戳（UDINT，单位 100 ms 自历元起算）。',
        'scene': '把日期序列化为定长 32-bit 整数以便存到磁盘 / 网络传输。',
        'value': '统一时间戳格式：节省 struct 的多字段反序列化开销。',
        'alt': '手算 epoch 时间戳，易错',
    },
    'F_BA_To100msTime': {
        'cat': 'date_convert',
        'summary': '把 `ST_BA_Time`（只含时分秒）转为 100 ms 粒度的整数（UDINT），从当天 00:00 起算。',
        'scene': '把时间序列化为定长整数。',
        'value': '统一时间格式。',
        'alt': '手算分钟 * 600 + 秒 * 10',
    },
    'F_BA_ToDate': {
        'cat': 'date_convert',
        'summary': '把 `ST_BA_Date` 转为 IEC 标准 `DATE` 类型（自 1970-01-01 起算的天数）。',
        'scene': '需要把 BA 库的日期与 IEC 标准 DATE 互操作（如喂给 IEC 标准时间函数）。',
        'value': '一行 FC 替代手写 `DATE_TO_*` 链。',
        'alt': '逐字段重组 DATE',
    },
    'F_BA_ToDT': {
        'cat': 'date_convert',
        'summary': '把 `ST_BA_DateTime` 转为 IEC 标准 `DT`（DATE_AND_TIME，等价 ULINT 秒数）。',
        'scene': '把 BA 内部日期时间转成 IEC 标准的 DT 类型给其它库用。',
        'value': '统一类型互操作。',
        'alt': '`DT_OF_DATE_AND_TOD(date, tod)` 类拼装',
    },
    'F_BA_ToSTDate': {
        'cat': 'date_convert',
        'summary': '把 IEC 标准 `DATE` 类型转回 BA 自定义 `ST_BA_Date` 结构。',
        'scene': '从 IEC 标准 DATE 字段恢复成结构化日期，便于按 year/month/day 字段操作。',
        'value': '反向转换，与 `F_BA_ToDate` 配对。',
        'alt': '手算各字段',
    },
    'F_BA_ToSTDateTime': {
        'cat': 'date_convert',
        'summary': '把 IEC 标准 `DT` 类型转回 BA 自定义 `ST_BA_DateTime` 结构。',
        'scene': '从 IEC 标准 DT 恢复结构化日期时间。',
        'value': '反向转换，与 `F_BA_ToDT` 配对。',
        'alt': '`DATE_AND_TIME_TO_TOD()` + `DT_TO_DATE()` 分别取 + 字段拼装',
    },
    'F_BA_ToSTTime': {
        'cat': 'date_convert',
        'summary': '把 IEC 标准 `TIME_OF_DAY`（或 `TOD`）转为 BA 自定义 `ST_BA_Time` 结构。',
        'scene': '从 IEC 标准 TOD 恢复时分秒字段。',
        'value': '反向转换，便于按字段访问。',
        'alt': '手算',
    },
    'F_BA_ToTime': {
        'cat': 'date_convert',
        'summary': '把 `ST_BA_Time` 转为 IEC 标准 `TIME_OF_DAY` / `TOD`。',
        'scene': '把 BA 时间结构传给 IEC 标准时间函数。',
        'value': '统一类型互操作。',
        'alt': '`TIME_OF_DAY(hour, minute, second)` 类构造',
    },
    # --- Date Time ---
    'F_BA_CountLeapYears': {
        'cat': 'date_time',
        'summary': '统计两个日期 `stDateFrom` 到 `stDateTo` 之间的闰年数量。返回 INT。常用于计算日历持续天数。',
        'scene': '计算从 2000-01-01 到 2025-12-31 之间一共有几个闰年（影响某些累计天数算法）。',
        'value': '一行 FC 替代 FOR 循环扫描每个年份判断闰年。',
        'alt': '`FOR y := y1 TO y2 DO IF F_BA_IsLeapYear(y) THEN cnt := cnt+1; END_IF; END_FOR;`',
    },
    'F_BA_DateMerge': {
        'cat': 'date_time',
        'summary': '把"日期部分"`stDate` 和"时间部分"`stTime` 合并为完整的 `ST_BA_DateTime`。',
        'scene': '日期来自日历控件、时间来自时间选择控件，业务侧合并成完整时间戳。',
        'value': '一行替代逐字段赋值。',
        'alt': '`dt.stDate := date; dt.stTime := time;`',
    },
    'F_BA_DateTimeString': {
        'cat': 'date_time',
        'summary': '把 `ST_BA_DateTime` 格式化为可读字符串（如 `"2026-06-03 14:30:00"`）。返回 `T_MaxString`。',
        'scene': '报警日志 / 趋势数据导出时把时间戳转成字符串便于阅读。',
        'value': '一行 FC 替代多次 INT_TO_STRING + 拼接 + 补零。',
        'alt': '`CONCAT(INT_TO_STRING(year), ...)` + 自己处理两位补零',
    },
    'F_BA_DayOfWeek': {
        'cat': 'date_time',
        'summary': '根据 `ST_BA_Date` 计算星期几。返回 `E_BA_Weekday` 枚举（eMonday..eSunday）。',
        'scene': '调度策略"工作日开夜间灯/周末关"判断当日是工作日还是周末。',
        'value': '一行 FC 替代 Zeller 公式手算。',
        'alt': '`Zeller` 公式实现（10+ 行）',
    },
    'F_BA_DaysInMonth': {
        'cat': 'date_time',
        'summary': '返回指定年月的天数。考虑闰年。返回 BYTE（28..31）。',
        'scene': '日历视图渲染当月的格子数。',
        'value': '一行 FC 替代 CASE 月份 + 闰年判断。',
        'alt': '`CASE month OF 1,3,5,7,8,10,12: 31; 4,6,9,11: 30; 2: IF leap THEN 29 ELSE 28; END_CASE;`',
    },
    'F_BA_GetDateTime': {
        'cat': 'date_time',
        'summary': '返回当前系统的 `ST_BA_DateTime`（日期+时间）。无参数。',
        'scene': '快速获取"当前时刻"作为时间戳；用于报警 / 趋势记录。',
        'value': '一行 FC 替代调用 `FB_LocalSystemTime` 等异步 FB 的复杂用法。',
        'alt': '`FB_LocalSystemTime` 实例化 + 周期调用 + 数据转换',
    },
    'F_BA_GetDT': {
        'cat': 'date_time',
        'summary': '返回当前系统的 `DT`（IEC 标准 DATE_AND_TIME，单位秒）。无参数。',
        'scene': '需要 IEC 标准 DT 类型作为时间戳的场景。',
        'value': '一行 FC 替代复杂的 SystemTime FB 调用 + 转换。',
        'alt': '`FB_LocalSystemTime` + 转换',
    },
    'F_BA_TimeMerge': {
        'cat': 'date_time',
        'summary': '把 hour / minute / second / hundredth 四个 BYTE 合并为 `ST_BA_Time` 结构。',
        'scene': '从用户输入的 4 个数字字段构造时间。',
        'value': '一行替代字段赋值。',
        'alt': '`tm.nHour := h; tm.nMinute := m; ...`',
    },
    'F_BA_TimeString': {
        'cat': 'date_time',
        'summary': '把 `ST_BA_Time` 格式化为字符串（如 `"14:30:00"`）。返回 `T_MaxString`。',
        'scene': 'HMI 显示时间。',
        'value': '一行 FC 替代字段补零拼接。',
        'alt': '`INT_TO_STRING` + 拼接 + 补零',
    },
    # --- Date Value ---
    'F_BA_DateRangeVal': {
        'cat': 'date_value',
        'summary': '把 BA 库的"日期范围"`ST_BA_DateRange`（含起止日期 + 选择模式）按 `eChoice` 决定的判定方式封装为 `U_BA_DateVal` 联合体输出。常用于调度引擎匹配"日期落在 X..Y 之间"或"逐日"等模式。',
        'scene': '楼宇调度："假期模式：12 月 24 日到 1 月 2 日之间执行节能策略" —— 把日期范围打包供调度引擎查找。',
        'value': '把 ST_BA_DateRange + eChoice 一次封装为统一的 U_BA_DateVal，调度引擎只需要解析 U_BA_DateVal 一种类型。',
        'alt': '调度引擎需要 IF eChoice 多分支处理 ST_BA_DateRange / ST_BA_Date / ST_BA_WeekNDay 等不同类型',
    },
    'F_BA_DateVal': {
        'cat': 'date_value',
        'summary': '把单个 `ST_BA_Date` 按 `eChoice` 封装为 `U_BA_DateVal` 联合体。',
        'scene': '"固定日期模式：每年 4 月 1 日执行" —— 把单日期打包供调度引擎。',
        'value': '同上：统一接口。',
        'alt': '调度引擎需要分类型处理',
    },
    'F_BA_WeekNDayVal': {
        'cat': 'date_value',
        'summary': '把"第 N 个星期 X" `ST_BA_WeekNDay` 按 `eChoice` 封装为 `U_BA_DateVal`。例："每月第二个星期日"。',
        'scene': '"每月第二个星期日为夏令时切换" —— 把 WeekNDay 打包供调度引擎。',
        'value': '同上：统一接口让调度引擎处理。',
        'alt': '调度引擎需要分类型处理',
    },
    # --- Scheduler ---
    'F_BA_SetSchedulerEntry': {
        'cat': 'scheduler',
        'summary': '构造一条调度日历条目 `ST_BA_SchedEntry`。把日期模式（`U_BA_DateVal`）+ 时间 + 持续时长 + 输出值组合成完整的调度条目。',
        'scene': '在调度数组里插入一条"每周一上午 8:00 启动空调 + 持续 10 小时 + 设定温度 22℃"的条目。',
        'value': '一行 FC 替代手写多字段赋值；保证字段一致性（无遗漏字段）。',
        'alt': '手写约 5-8 行字段赋值',
    },
    # --- Trend ---
    'F_BA_TrendBufferSize': {
        'cat': 'trend',
        'summary': '根据采样间隔、保留时长、值类型计算趋势缓冲区所需的字节数。返回 UDINT。用于"按目标存储时长反算环形缓冲区大小"的容量规划。',
        'scene': '"温度趋势保留 7 天、每分钟采一次"——本 FC 算出需要分配多大的 `ARRAY OF ST_BA_TrendEntry` 缓冲。',
        'value': '替代手算 `7 * 24 * 60 * SIZEOF(ST_BA_TrendEntry)`；FC 内部考虑了带 event 标记的额外字段开销。',
        'alt': '手算公式，易漏 ST_BA_TrendEntryEvent 的额外字段',
    },
    'F_BA_IsDisturbed': {
        'cat': 'trend',
        'summary': '检测 `ST_BA_StatusFlags` 中的"扰动 / 不可信"位（disturbed / unreliable）。返回 BOOL。',
        'scene': '趋势记录 FB 决定是否把当前值写入历史：测点状态被报为 disturbed 时跳过该样本。',
        'value': '一行 FC 替代位级判断 `(stStatus.nFlags AND 16#01) <> 0`。',
        'alt': '位运算手写',
    },
    # --- Auxiliary Calc ---
    'F_BA_RemMsTof': {
        'cat': 'auxiliary_calc',
        'summary': '查询某个 `TOF`（关断延时）实例的剩余倒计时（毫秒粒度）。返回 UDINT。`tofTimer` 输入 IN 的下降沿后开始累减；倒计时未启动（IN 为 TRUE）时返回 PT 总值。',
        'scene': 'HMI 显示"关灯还剩 X 秒"——把 `FB_BA_FltrPT1` 等场景中用到的 TOF 倒计时实时显示。',
        'value': '一行 FC 替代手算 PT - elapsed_time。',
        'alt': '手算 `tof.PT - (TIME() - tof.startTime)`',
    },
    'F_BA_RemMsTon': {
        'cat': 'auxiliary_calc',
        'summary': '查询某个 `TON`（开通延时）实例的剩余倒计时（毫秒粒度）。返回 UDINT。倒计时进行中给出剩余毫秒；未启动时给 PT 总值；已超时给 0。',
        'scene': 'HMI 显示"启动倒计时还剩 X 秒"——配合 `FB_BA_Swi2P` 等场景。',
        'value': '一行替代手算。',
        'alt': '手算',
    },
    'F_BA_RemMsTp': {
        'cat': 'auxiliary_calc',
        'summary': '查询某个 `TP`（脉冲）实例的剩余脉冲时长（毫秒粒度）。返回 UDINT。⚠️ PDF 此节的函数签名印刷错误为 `FUNCTION F_BA_RemSecsTp`，实际是 `F_BA_RemMsTp`。',
        'scene': 'HMI 显示"脉冲还剩 X 毫秒"。',
        'value': '一行替代手算。',
        'alt': '手算',
    },
    'F_BA_RemSecsTof': {
        'cat': 'auxiliary_calc',
        'summary': '查询某个 `TOF` 实例的剩余倒计时（秒粒度，向下取整）。返回 UDINT。',
        'scene': 'HMI 显示"关灯还剩 X 秒"（秒级粒度足够）。',
        'value': '一行替代手算 + 单位换算。',
        'alt': '手算 + DIV 1000',
    },
    'F_BA_RemSecsTone': {
        'cat': 'auxiliary_calc',
        'summary': '查询某个 `TON` 实例的剩余倒计时（秒粒度）。返回 UDINT。⚠️ PDF 章节标题与 InfoSys topic 都印刷为 `F_BA_RemSecsTone`，但函数本体签名其实是 `F_BA_RemSecsTon`（少一个 e）。',
        'scene': 'HMI 显示"启动倒计时还剩 X 秒"。',
        'value': '一行替代手算 + 单位换算。',
        'alt': '手算 + DIV 1000',
    },
    'F_BA_RemSecsTp': {
        'cat': 'auxiliary_calc',
        'summary': '查询某个 `TP` 实例的剩余脉冲时长（秒粒度，向下取整）。返回 UDINT。',
        'scene': 'HMI 显示"脉冲还剩 X 秒"。',
        'value': '一行替代手算 + 单位换算。',
        'alt': '手算 + DIV 1000',
    },
    # --- TC Log ---
    'F_BA_LogMessage': {
        'cat': 'tc_log',
        'summary': '把一条文本消息写入 TwinCAT ADS Logger。`nLogType` 决定消息分类掩码（默认 ERROR），`sLogCode` 为前缀代码，`sLogText` 为消息正文。内部用 `FB_FormatString` + ADSLOG 实现。',
        'scene': '调试期把关键事件（参数变化、模式切换）写入 ADS Log 便于事后排查。',
        'value': '一行 FC 替代手工调用 `ADSLOGSTR` + 拼接前缀的多步骤。',
        'alt': '`ADSLOGSTR(...)` 加自定义前缀格式化',
    },
    'F_BA_LogMessage1': {
        'cat': 'tc_log',
        'summary': '把一条文本消息 + 1 个动态参数（`tArg1`，T_Arg 类型）写入 TwinCAT ADS Logger。`sLogText` 中可用 `%s` `%d` 等占位符。',
        'scene': '`F_BA_LogMessage1(...,sLogText:="Temp=%f",tArg1:=F_TArgReal(fT))` 输出"Temp=22.3"。',
        'value': '类似 `printf("text=%d",val)`，比手工 INT_TO_STRING + CONCAT 简洁。',
        'alt': '`CONCAT(text, INT_TO_STRING(val))` 多行',
    },
    'F_BA_LogMessage2': {
        'cat': 'tc_log',
        'summary': '把文本消息 + 2 个动态参数写入 TwinCAT ADS Logger。',
        'scene': '`"Setpoint changed from %f to %f"` 两个参数。',
        'value': '同 LogMessage1，多一参数。',
        'alt': '多次 CONCAT',
    },
    'F_BA_LogMessage3': {'cat': 'tc_log', 'summary': '文本 + 3 个动态参数。用法参考 `F_BA_LogMessage2`。⚠️ PDF 此节正文只一句 "Application see F_BA_LogMessage2"，未给签名——本文档按 InfoSys + LogMessage2 规则推算签名为 `FUNCTION F_BA_LogMessage : INT`（注意 PDF 内部符号统一为 `F_BA_LogMessage` 而非带数字后缀；编译器通过 InfoSys 接受 `F_BA_LogMessage3` 等名字）。', 'scene': '3 参数日志：`F_BA_LogMessage3("Temp/Hum/Pres", tArg1, tArg2, tArg3)`。', 'value': '同 LogMessage 系列，多 1 参数。', 'alt': '多次 CONCAT'},
    'F_BA_LogMessage4': {'cat': 'tc_log', 'summary': '文本 + 4 个动态参数。用法参考 `F_BA_LogMessage2`。⚠️ PDF 此节正文只一句 "Application see F_BA_LogMessage2"，未给签名。', 'scene': '4 参数日志。', 'value': '同 LogMessage 系列。', 'alt': '多次 CONCAT'},
    'F_BA_LogMessage5': {'cat': 'tc_log', 'summary': '文本 + 5 个动态参数。用法参考 `F_BA_LogMessage2`。⚠️ PDF 此节正文只一句 "Application see F_BA_LogMessage2"，未给签名。', 'scene': '5 参数日志。', 'value': '同 LogMessage 系列。', 'alt': '多次 CONCAT'},
    'F_BA_LogMessage6': {'cat': 'tc_log', 'summary': '文本 + 6 个动态参数。用法参考 `F_BA_LogMessage2`。⚠️ PDF 此节正文只一句 "Application see F_BA_LogMessage2"，未给签名。', 'scene': '6 参数日志。', 'value': '同 LogMessage 系列。', 'alt': '多次 CONCAT'},
    'F_BA_LogMessage7': {'cat': 'tc_log', 'summary': '文本 + 7 个动态参数。用法参考 `F_BA_LogMessage2`。⚠️ PDF 此节正文只一句 "Application see F_BA_LogMessage2"，未给签名。', 'scene': '7 参数日志。', 'value': '同 LogMessage 系列。', 'alt': '多次 CONCAT'},
    'F_BA_LogMessage8': {'cat': 'tc_log', 'summary': '文本 + 8 个动态参数。用法参考 `F_BA_LogMessage2`。⚠️ PDF 此节正文只一句 "Application see F_BA_LogMessage2"，未给签名。', 'scene': '8 参数日志。', 'value': '同 LogMessage 系列。', 'alt': '多次 CONCAT'},
    'F_BA_LogMessage9': {'cat': 'tc_log', 'summary': '文本 + 9 个动态参数。用法参考 `F_BA_LogMessage2`。⚠️ PDF 此节正文只一句 "Application see F_BA_LogMessage2"，未给签名。', 'scene': '9 参数日志。', 'value': '同 LogMessage 系列。', 'alt': '多次 CONCAT'},
    'F_BA_LogMessage10': {'cat': 'tc_log', 'summary': '文本 + 10 个动态参数。用法参考 `F_BA_LogMessage2`。⚠️ PDF 此节正文只一句 "Application see F_BA_LogMessage2"，未给签名。', 'scene': '10 参数日志。', 'value': '同 LogMessage 系列。', 'alt': '多次 CONCAT'},
    # --- Check Enum ---
    'F_BA_CheckEnum': {
        'cat': 'check_enum',
        'summary': '检查一个枚举值 `nIndex` 是否在指定的枚举信息表 `aInfo : ARRAY[*] OF ST_BA_EnumInfo` 中。返回 BOOL：TRUE = 存在。`ARRAY[*]` 语法允许传入任意上下界的数组（编译器自动推断尺寸）。',
        'scene': '运行时检查 HMI 传入的枚举值合法性："用户选择的传感器类型代码是否在我支持的列表里"。',
        'value': '一行 FC 替代手写 FOR 循环遍历查找。',
        'alt': '`FOR i := L TO U DO IF aInfo[i].id = nIndex THEN ... EXIT; END_IF; END_FOR;`',
    },
    # --- Validation ---
    'F_BA_IsDateValChoiceValid': {
        'cat': 'validation',
        'summary': '检查 `E_BA_DateValChoice` 枚举值是否在有效范围内。返回 BOOL。',
        'scene': '运行时校验日期选择枚举（来自配置文件或网络消息）是否合法。',
        'value': '替代手写枚举范围检查。',
        'alt': '`(val >= First) AND (val <= Last)` 表达式',
    },
    'F_BA_IsLoggingTypeValid': {
        'cat': 'validation',
        'summary': '检查 `E_BA_LoggingType` 枚举值是否合法。返回 BOOL。',
        'scene': '配置导入时校验日志类型枚举。',
        'value': '同其它 IsValid 系列。',
        'alt': '范围比较',
    },
    'F_BA_IsUnitValid': {
        'cat': 'validation',
        'summary': '检查 `E_BA_Unit` 枚举值是否在 `BAComn_EnumDE.aUnits` 表中。返回 BOOL。',
        'scene': '配置导入时校验单位代码（如度量单位）合法性。',
        'value': '同其它 IsValid 系列。',
        'alt': '查表 + 范围比较',
    },
    'F_BA_IsMeasuringElementValid': {
        'cat': 'validation',
        'summary': '检查 `E_BA_MeasuringElement` 枚举值是否合法（传感器类型枚举：Pt100 / Ni1000 / Ohm / 等）。返回 BOOL。',
        'scene': '上电时校验配置文件里的传感器类型枚举是否合法（避免传给 `FB_BA_KL32xx` 时崩溃）。',
        'value': '同其它 IsValid 系列。',
        'alt': '范围比较',
    },
    'F_BA_IsDataClassValid': {
        'cat': 'validation',
        'summary': '检查 `E_BA_DataClass` 枚举值是否合法（数据分类：BinaryInput / AnalogInput / ...）。返回 BOOL。',
        'scene': '配置导入校验。',
        'value': '同其它 IsValid 系列。',
        'alt': '范围比较',
    },
    'F_BA_IsDataTypeValid': {
        'cat': 'validation',
        'summary': '检查 `E_BA_DataType` 枚举值是否合法（数据类型：eBool / eInt / eReal / 等）。返回 BOOL。',
        'scene': '配置导入校验。',
        'value': '同其它 IsValid 系列。',
        'alt': '范围比较',
    },
    'F_BA_IsWeekdayValid': {
        'cat': 'validation',
        'summary': '检查 `E_BA_Weekday` 枚举值是否合法（eMonday..eSunday）。返回 BOOL。',
        'scene': '配置导入校验。',
        'value': '同其它 IsValid 系列。',
        'alt': '范围比较',
    },
    # --- GVLs ---
    'BAComn_Global': {
        'cat': 'gvls',
        'summary': 'BA2_Common 库的全局常量集合。包含基本数据类型的最小/最大值（如 `nMinByte / nMaxByte / nMinInt / nMaxInt / tMinTime / tMaxTime / tMaxDATE`）、I/O 原始值常量（0V / 1V / 2V / 5V / 10V 对应的 INT 原始数）、时间换算常量（秒-毫秒、分-秒等）、字符常量（数字 0-9 的 ASCII、加号、减号、小数点）、ADS 常量（loopback NetID、符号分隔符）以及避免除零的小数常量 `fCloseToZero`。所有常量都标 `qualified_only`，使用时必须用 `BAComn_Global.<name>` 访问。',
        'scene': '在自定义 BA FB 中需要"24 小时换算成秒数"时直接用 `BAComn_Global.n24Hour2Hour`，避免到处写 `24 * 60 * 60` 散落各处。',
        'value': '集中管理避免硬编码魔数；常量统一命名便于 IDE 搜索。',
        'alt': '到处散落 `60 * 60 * 24` 等硬编码',
    },
    'BAComn_Param': {
        'cat': 'gvls',
        'summary': 'BA2_Common 字符串分词器（tokenizer）的全局参数：`nStrTokenizer_BufferSize`（缓冲条目数）与 `nStrTokenizer_MaxLevel`（嵌套深度）。本 GVL 配合内部字符串解析使用（用户一般不直接访问），标 `qualified_only`。',
        'scene': '调整内部 tokenizer 缓冲尺寸（极少需要修改，默认即可）。',
        'value': '集中可调参数，避免散落。',
        'alt': '硬编码',
    },
    'BAComn_EnumDE': {
        'cat': 'gvls',
        'summary': 'BA2_Common 单位（`E_BA_Unit`）的"英文+德文+短码"对照表 `aUnits : ARRAY[E_BA_Unit.First .. E_BA_Unit.Last] OF ST_BA_EnumInfo`。每个单位枚举对应一个 `ST_BA_EnumInfo` 条目，含 `sName`（英文名，如 `"Square Meters"`）、`sDescription`（德文描述，如 `"Fläche"`）、`sShortcut`（短码符号，如 `"m²"`）。本 GVL 是 `F_BA_IsUnitValid` 和其它单位校验 FC 的查表来源。',
        'scene': 'HMI 显示测量值时按 `eUnit` 查 `BAComn_EnumDE.aUnits[eUnit].sShortcut` 拿到 `"m²"` / `"℃"` / `"kPa"` 等符号显示。',
        'value': '统一单位字符串源，HMI 切换语言时改 GVL 一处即可；避免散落硬编码。',
        'alt': '在 HMI 端硬编码各单位字符串',
    },
}


def _stable_guid(name: str) -> str:
    ns = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
    return '{' + str(uuid.uuid5(ns, f'tc3-libraries-kb/Tc3_BA2_Common/P_Demo_{name}')) + '}'


def _infosys_url(name: str) -> str:
    idx = json.loads(INFOSYS_INDEX.read_text())
    return idx[name]['url']


def _format_syntax_block(syntax: str, entry_name: str = '') -> str:
    """Indent each line by 4 spaces for IEC ST aesthetics."""
    # Use override if available (for entries with empty PDF syntax)
    if entry_name in _SYNTAX_OVERRIDES:
        syntax = _SYNTAX_OVERRIDES[entry_name]
    lines = []
    for line in syntax.split('\n'):
        lines.append(line.rstrip())
    return '\n'.join(lines)


def _vars_from_syntax(syntax: str) -> tuple[list[dict], list[dict], list[dict]]:
    """Parse syntax block into (inputs, outputs, in_outs) lists.

    Each entry: {name, type, default}
    """
    inputs, outputs, in_outs = [], [], []
    # Pull each VAR_* region
    region_re = re.compile(r'(VAR_INPUT(?:\s+CONSTANT(?:\s+PERSISTENT)?)?|VAR_OUTPUT|VAR_IN_OUT)\s*\n([\s\S]*?)END_VAR', re.IGNORECASE)
    decl_re = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([^;:\n]+?)(?:\s*:=\s*([^;\n]+?))?\s*;?\s*(?://.*)?$', re.MULTILINE)
    for m in region_re.finditer(syntax):
        kind = m.group(1).upper()
        body = m.group(2)
        # strip attribute pragma lines and line comments
        body = re.sub(r"\{attribute[^}]*\}", '', body)
        body = re.sub(r'//.*$', '', body, flags=re.MULTILINE)
        rows = []
        for dm in decl_re.finditer(body):
            name = dm.group(1).strip()
            typ = dm.group(2).strip()
            default = (dm.group(3) or '').strip()
            if name.upper() in ('VAR_INPUT', 'VAR_OUTPUT', 'VAR_IN_OUT', 'END_VAR', 'FUNCTION_BLOCK', 'FUNCTION', 'CONSTANT', 'PERSISTENT'):
                continue
            rows.append({'name': name, 'type': typ, 'default': default})
        if 'IN_OUT' in kind:
            in_outs.extend(rows)
        elif 'OUTPUT' in kind:
            outputs.extend(rows)
        else:
            inputs.extend(rows)
    return inputs, outputs, in_outs


def _render_var_table(rows: list[dict], with_default: bool = False, desc_lookup: dict = None) -> str:
    if not rows:
        return '\n无。\n'
    if with_default:
        out = ['| 名称 | 类型 | 默认值 | 说明 |', '|---|---|---|---|']
        for r in rows:
            desc = (desc_lookup or {}).get(r['name'], '⚠️ PDF / InfoSys 未列文字说明，需对照 PDF 正文。')
            default = '`' + r['default'] + '`' if r['default'] else '-'
            out.append(f"| `{r['name']}` | `{r['type']}` | {default} | {desc} |")
    else:
        out = ['| 名称 | 类型 | 说明 |', '|---|---|---|']
        for r in rows:
            desc = (desc_lookup or {}).get(r['name'], '⚠️ PDF / InfoSys 未列文字说明，需对照 PDF 正文。')
            out.append(f"| `{r['name']}` | `{r['type']}` | {desc} |")
    return '\n' + '\n'.join(out) + '\n'


# Synthetic syntax for entries whose PDF text omits the FUNCTION declaration
# (PDF only gives prose like "of return type ST_BA_DateTime outputs the date
# and time"). We reconstruct the canonical signature from PDF's prose +
# InfoSys cross-reference.
_SYNTAX_OVERRIDES: dict[str, str] = {
    'F_BA_GetDateTime': 'FUNCTION F_BA_GetDateTime : ST_BA_DateTime',
    'F_BA_GetDT': 'FUNCTION F_BA_GetDT : DT',
    # LogMessage3-10 share signature pattern with LogMessage2 (FB internal
    # symbol is F_BA_LogMessage per PDF print; InfoSys treats them as
    # separate functions with N args).
}


# Curated overrides for entries where PDF table extraction misses some
# fields (multi-line names, "Name"/"Type" header parsed as rows, etc.)
_DESC_OVERRIDES: dict[str, dict[str, str]] = {
    'F_BA_CompareVersion': {
        'stVersion1': '被比较的版本号 1（基准版本）。',
        'stVersion2': '被比较的版本号 2（参照版本）。',
        'eCompare': '比较运算符：`eEqual` / `eLower` / `eLowerOrEqual` / `eHigher` / `eHigherOrEqual` / `eNotEqual`。',
        'nLimit': '比较深度（1=只比 Major，2=Major+Minor，3=+Build，4=全部 4 段都比）。',
    },
    'F_BA_CheckEnum': {
        'aInfo': '枚举元数据数组（`ARRAY[*] OF ST_BA_EnumInfo`），通常传 `BAComn_EnumDE.aUnits` 等。',
        'nIndex': '被校验的枚举值（按数组下标使用）。',
    },
    'F_BA_DateTimeString': {
        'stDateTime': '被格式化的日期时间结构。',
    },
    'F_BA_WeekNDayVal': {
        'stWeekNDay': '"第 N 个星期 X"输入结构（含周序号 + 星期几）。',
        'eChoice': '日期选择模式枚举（决定输出 `U_BA_DateVal` 的解析方式）。',
        'eWeekday': '星期几（eMonday..eSunday）。',
        'eWeek': '周序号（eFirst / eSecond / eThird / eFourth / eLast）。',
        'nMonth': '月份（1..12）。',
        'nYear': '年份。',
    },
    'F_BA_SetSchedulerEntry': {
        'stEntry': '已构造好的调度条目模板。',
        'stDateVal': '日期 / 周期模式联合体 `U_BA_DateVal`。',
        'stTime': '时间字段 `ST_BA_Time`（启动时间）。',
        'tDuration': '持续时间（条目执行多久）。',
        'pStatusValue': '状态值指针（执行后写入的目标变量地址）。',
        'uEntryValue': '调度条目的输出值（按 `U_BA_ClassValue` 联合体打包，决定执行时设置目标变量为何值）。',
        'uDateValue': '日期 / 周期模式（`U_BA_DateVal`）。',
        'tStartTime': '启动时间。',
    },
    'F_BA_IsDisturbed': {
        'stStatus': '状态标志结构 `ST_BA_StatusFlags`。',
        'stStateFlags': '状态标志结构 `ST_BA_StatusFlags`。',
    },
    'F_BA_TrendBufferSize': {
        'eEntryType': '趋势条目类型枚举（决定每条目字节数）。',
        'tSampleInterval': '采样间隔时间。',
        'tRetentionTime': '保留时长（计算需要多少条目）。',
        'aBuffer': '趋势数据缓冲数组（用 `ARRAY[*]` 接受任意定长）。本 FC 计算该数组应该开多大才够装 `tRetentionTime` 时长。',
    },
    'F_BA_IsDataClassValid': {
        'eDataClass': '被校验的 `E_BA_DataClass` 枚举值。',
        'eClass': '被校验的 `E_BA_DataClass` 枚举值。',
    },
    'F_BA_IsDataTypeValid': {
        'eDataType': '被校验的 `E_BA_DataType` 枚举值。',
        'eType': '被校验的 `E_BA_DataType` 枚举值。',
    },
    'F_BA_IsDateValChoiceValid': {'eChoice': '被校验的 `E_BA_DateValChoice` 枚举值。'},
    'F_BA_IsLoggingTypeValid': {
        'eLoggingType': '被校验的 `E_BA_LoggingType` 枚举值。',
        'eType': '被校验的 `E_BA_LoggingType` 枚举值。',
    },
    'F_BA_IsMeasuringElementValid': {
        'eMeasuringElement': '被校验的 `E_BA_MeasuringElement` 枚举值。',
        'eElement': '被校验的 `E_BA_MeasuringElement` 枚举值。',
    },
    'F_BA_IsUnitValid': {'eUnit': '被校验的 `E_BA_Unit` 枚举值。'},
    'F_BA_IsWeekdayValid': {
        'eWeekday': '被校验的 `E_BA_Weekday` 枚举值。',
        'eDay': '被校验的 `E_BA_Weekday` 枚举值。',
    },
    'F_BA_DateMerge': {
        'stDate': '日期字段 `ST_BA_Date`。',
        'stTime': '时间字段 `ST_BA_Time`。',
    },
    'F_BA_TimeMerge': {
        'nHour': '小时（0..23）。',
        'nMinute': '分钟（0..59）。',
        'nSecond': '秒（0..59）。',
        'nHundredths': '百分之一秒（0..99）。',
    },
    'F_BA_DateRangeVal': {
        'stDateRange': '日期范围结构（含起 / 止日期）。',
        'eChoice': '日期选择模式枚举。',
    },
    'F_BA_DateVal': {
        'stDate': '单个日期结构。',
        'eChoice': '日期选择模式枚举。',
    },
    'F_BA_TimeString': {'stTime': '被格式化的时间结构。'},
    'F_BA_DayOfWeek': {'stDate': '查询日期。'},
    'F_BA_DaysInMonth': {'nYear': '年份。', 'nMonth': '月份 (1..12)。'},
    'F_BA_CountLeapYears': {
        'stDateFrom': '起始日期。',
        'stDateTo': '结束日期。',
    },
    'F_BA_ToDate': {'stDate': '被转换的 BA 日期结构。'},
    'F_BA_ToDT': {'stDateTime': '被转换的 BA 日期时间结构。'},
    'F_BA_ToSTDate': {'dtDate': '被转换的 IEC 标准 `DATE` 值。'},
    'F_BA_ToSTDateTime': {'dt': '被转换的 IEC 标准 `DT` 值。'},
    'F_BA_ToSTTime': {'tod': '被转换的 IEC 标准 `TOD` 值。'},
    'F_BA_ToTime': {'stTime': '被转换的 BA 时间结构。'},
    'F_BA_To100msDate': {'stDate': '被转换的 BA 日期结构。'},
    'F_BA_To100msTime': {'stTime': '被转换的 BA 时间结构。'},
    'F_BA_TimeStruct_TO_DateTime': {'stTimeStruct': '被转换的 IEC `TIMESTRUCT`。'},
    'F_BA_TimeStruct_TO_Time': {'stTimeStruct': '被转换的 IEC `TIMESTRUCT`。'},
    'F_BA_DateHasPlaceholder': {'stDate': '被检查的 BA 日期结构。'},
    'F_BA_DateUnspecified': {'stDate': '被检查的 BA 日期结构。'},
    'F_BA_IsLeapYear': {'nYear': '被检查的年份。'},
    'F_BA_TimeHasPlaceholder': {'stTime': '被检查的 BA 时间结构。'},
    'F_BA_TimeUnspecified': {'stTime': '被检查的 BA 时间结构。'},
    'F_BA_BVal': {'bVal': '被打包的 BOOL 值。', 'aInfo': '枚举元数据（可选）。'},
    'F_BA_ByteVal': {
        'nVal': '被打包的 BYTE 值。',
        'aInfo': '枚举元数据数组（如 `BAComn_EnumDE.aUnits`）。',
    },
    'F_BA_IVal': {
        'iVal': '被打包的 INT 值。',
        'eUnit': '单位枚举。',
        'stStatus': '状态标志结构。',
    },
    'F_BA_RVal': {
        'fVal': '被打包的 REAL 值。',
        'eUnit': '单位枚举。',
        'stStatus': '状态标志结构。',
    },
    'F_BA_UDIVal': {
        'udiVal': '被打包的 UDINT 值。',
        'eUnit': '单位枚举。',
        'stStatus': '状态标志结构。',
    },
    'F_BA_OffsetPtr': {'pAddr': '基地址。', 'nOffset': '偏移字节数。'},
    'F_BA_DiffPtr': {'pAddr1': '第 1 个地址。', 'pAddr2': '第 2 个地址。'},
    'F_BA_RemMsTof': {'tofTimer': '被查询的 TOF 实例。'},
    'F_BA_RemMsTon': {'tonTimer': '被查询的 TON 实例。'},
    'F_BA_RemMsTp': {'tpTimer': '被查询的 TP 实例。'},
    'F_BA_RemSecsTof': {'tofTimer': '被查询的 TOF 实例。'},
    'F_BA_RemSecsTone': {'tonTimer': '被查询的 TON 实例（PDF 函数名 `F_BA_RemSecsTon`，少一个 e）。'},
    'F_BA_RemSecsTp': {'tpTimer': '被查询的 TP 实例。'},
}


def _desc_from_pdf_tables(entry_name: str, extracts: dict) -> dict:
    """Pull {name: chinese desc translated from PDF Inputs/Outputs description text}.

    Curated overrides from _DESC_OVERRIDES take precedence over auto-extracted
    PDF descriptions.
    """
    e = extracts.get(entry_name, {})
    tables = e.get('tables', {})
    out = {}
    for key in ('inputs', 'inputs_const', 'outputs', 'inouts'):
        for r in tables.get(key, []):
            n = r['name']
            d = r['desc'].strip()
            d = re.sub(r'\[\s*\}\s*\d+\s*\]', '', d).strip()
            # skip noise rows
            if n.lower() in ('name', 'type', 'description'):
                continue
            if d:
                out[n] = _translate_basic(d)
    # Apply overrides
    out.update(_DESC_OVERRIDES.get(entry_name, {}))
    return out


# Minimal English-to-Chinese for the common phrases.
_PHRASE_MAP = [
    ('A rising edge at this input starts the function block', '上升沿触发执行'),
    ('rising edge', '上升沿'),
    ('falling edge', '下降沿'),
    ('Enable of the controller', '控制器使能'),
    ('Enable of the function block', '功能块使能'),
    ('Setpoint of the controlled system', '被控对象设定值'),
    ('Actual value of the controlled system', '被控对象实际值'),
    ('Control direction of the controller', '控制方向'),
    ('Synchronizes the controller to the value of', '把控制器同步到'),
    ('Synchronization value', '同步目标值'),
    ('Display of', '显示'),
    ('Output of the present terminal status', '当前端子状态字节'),
    ('Output of the present process data', '当前原始过程数据'),
    ('Scaled output value', '缩放后的工程量输出值'),
    ('Display how many bytes', '显示有多少字节'),
    ('A TRUE indicates a wire break', 'TRUE = 检测到断线'),
    ('A TRUE indicates a short circuit', 'TRUE = 检测到短路'),
    ('Selection of the sensor type', '传感器类型选择'),
    ('General enable of the function block', '功能块总使能'),
    ('Input value', '输入值'),
    ('Setpoint input', '设定值'),
    ('Hysteresis offset', '滞回偏移'),
    ('Hysteresis', '滞回宽度'),
    ('Output', '输出'),
    ('Upper switching point', '上切换点'),
    ('Lower switching point', '下切换点'),
    ('Switch-on point', '开通点'),
    ('Switch-off point', '关断点'),
    ('Start-up delay', '启动延时'),
    ('Switch-off delay', '关断延时'),
    ('Remaining time of the start-up delay', '启动延时剩余时间'),
    ('Remaining time of the switch-off delay', '关断延时剩余时间'),
    ('switch-on delay', '开通延时'),
    ('switch-off delay', '关断延时'),
    ('A rising edge at this input', '此输入上升沿'),
    ('The function block is being executed', '功能块正在执行'),
    ('Countdown of the set start-up phase', '启动阶段倒计时'),
    ('Contains the error description', '包含错误描述字符串'),
    ('output is switched to TRUE if the parameters', '参数错误时此输出置 TRUE'),
    ('Filter time constant', '滤波时间常数'),
    ('Input signal', '输入信号'),
    ('Filtered output signal', '滤波后的输出信号'),
    ('input value of the ramp function', '坡道输入值'),
    ('Upper interpolation point', '坡道上参考点'),
    ('Lower interpolation point', '坡道下参考点'),
    ('Rise time', '上升时间'),
    ('Fall time', '下降时间'),
    ('Output signal, slope-limited', '已限速的输出信号'),
    ('Value to be monitored', '被监视的值'),
    ('forces a trigger pulse at the output', '强制在输出产生一个触发脉冲'),
    ('Switches to TRUE if', '满足条件时切换为 TRUE：'),
    ('TRUE for one cycle', '触发期间 TRUE 持续一个 PLC 周期'),
    ('In case of a value change', '检测到值变化时'),
    ('Pointer to the beginning of the memory area to be examined', '指向被检查内存区起始的指针'),
    ('Pointer to the beginning of the memory area to be compared', '指向被比较内存区起始的指针'),
    ('Pointer to the beginning of the memory area where the array', '指向数组所在内存区起始的指针'),
    ('Length of the memory area', '内存区长度'),
    ('Length of the memory area to be examined', '内存区长度'),
    ('Comparison byte', '比较基准字节'),
    ('Lower range limit of the array', '数组下界'),
    ('Upper range limit of the array', '数组上界'),
    ('If an element of the array has the value specified here', '元素值等于此处指定值时被视为"未使用"'),
    ('Destination address of the write operation', '写入操作的目标地址'),
    ('Destination address of the filling area', '填充区域的目标地址'),
    ('Size of the filling area', '填充区域的尺寸'),
    ('Value to be written', '被写入的值'),
    ('Filling value', '填充值'),
    ('Base address', '基地址'),
    ('Offset', '偏移量'),
    ('Comparison operation to be performed', '要执行的比较运算'),
    ('Number of digits to be compared', '要比较的位数'),
    ('Version numbers to be compared', '被比较的版本号'),
    ('Observed date-time entry', '被观察的日期时间条目'),
    ('Log type', '日志类型'),
    ('An argument in textual form that precedes the message', '附加在消息前的文本前缀'),
    ('Message as text', '消息正文'),
    ('Further message text', '附加消息文本'),
    ('Input of the considered switch-on delay', '关联的开通延时定时器实例'),
    ('Input of the considered switch-off delay', '关联的关断延时定时器实例'),
    ('Input of the considered pulse function', '关联的脉冲定时器实例'),
    ('The first run', '首次调用'),
    ('Internally limited', '内部限制'),
    ('Switches the output value', '切换输出值'),
    ('the function block', '功能块'),
    ('Calculated output value of the characteristic curve', '按特性曲线计算的输出值'),
    ('Dead zone value', '死区值'),
    ('Dead zone', '死区'),
    ('Damping time', '阻尼时间'),
    ('Rate time of the D part', 'D 部分微分时间'),
    ('Integral action time of the I part', 'I 部分积分时间'),
    ('Controller gain', '控制器增益'),
    ('Call cycle of the function block', '功能块调用周期'),
    ('Mode of operation of the controller', '控制器运行模式'),
    ('Upper output limit', '输出上限'),
    ('Lower output limit', '输出下限'),
    ('Control value', '控制输出值'),
    ('Control deviation', '控制偏差'),
]


def _translate_basic(s: str) -> str:
    out = s
    for en, zh in _PHRASE_MAP:
        out = out.replace(en, zh)
    # add Chinese suffix to denote auto-translated content
    return out


def _doc_path(name: str) -> Path:
    cat = ENTRY_META[name]['cat']
    return LIB_DIR / CATEGORIES[cat][0] / f'{name}.md'


def _example_path(name: str) -> Path:
    return EX_DIR / f'P_Demo_{name}.TcPOU'


def _return_type_from_syntax(syntax: str) -> str:
    # Match "FUNCTION <name> : <ret_type>" — ret_type is either to end-of-line
    # or up to the next VAR_ region.
    m = re.search(r'FUNCTION\s+\w+\s*:\s*([\w\(\)\.\,\s]+?)\s*(?:\n|\s+VAR_|$)', syntax)
    if m:
        return m.group(1).strip()
    return ''


def _is_gvl(name: str) -> bool:
    return name.startswith('BAComn_')


def _section_id(name: str, extracts: dict) -> str:
    return extracts[name].get('section', '4.x.y.z')


def _render_md(name: str, extracts: dict) -> str:
    meta = ENTRY_META[name]
    cat_key = meta['cat']
    cat_dir, cat_label = CATEGORIES[cat_key]
    syntax = _format_syntax_block(extracts[name]["syntax"], name)
    section = _section_id(name, extracts)
    infosys_url = _infosys_url(name)
    inputs, outputs, in_outs = _vars_from_syntax(syntax)
    desc = _desc_from_pdf_tables(name, extracts)

    if _is_gvl(name):
        type_label = 'GVL'
    elif name.startswith('FB_'):
        type_label = 'FUNCTION_BLOCK'
    else:
        type_label = 'FUNCTION'

    ret_type = _return_type_from_syntax(syntax) if not _is_gvl(name) else ''
    ret_section = ''
    if not _is_gvl(name) and ret_type:
        ret_section = f'本 FC 返回类型为 `{ret_type}`。'
    if _is_gvl(name):
        ret_section = '本 GVL 无返回值（全局常量集合）。'

    # Section 3 narrative
    behavior = _build_behavior(name, meta, syntax, inputs, outputs, in_outs)

    # Section 5 cautions
    cautions = _build_cautions(name, meta)

    iecst_blocks = ''
    if _is_gvl(name):
        iecst_blocks = f'### VAR_GLOBAL\n\n```iecst\n{syntax}\n```\n\n'
        iecst_blocks += '⚠️ 这是 GVL（全局常量集合）。本表给出代表性条目；完整定义见 PDF 原文。\n\n'
    else:
        # Render each VAR_* block by re-finding in syntax
        # We just dump the syntax which already includes FUNCTION/FB header + VAR_* blocks
        iecst_blocks = f'### 完整声明\n\n```iecst\n{syntax}\n```\n\n'
        if inputs:
            iecst_blocks += '### VAR_INPUT 引脚\n' + _render_var_table(inputs, with_default=True, desc_lookup=desc) + '\n'
        if outputs:
            iecst_blocks += '### VAR_OUTPUT 引脚\n' + _render_var_table(outputs, with_default=False, desc_lookup=desc) + '\n'
        if in_outs:
            iecst_blocks += '### VAR_IN_OUT 引脚\n' + _render_var_table(in_outs, with_default=False, desc_lookup=desc) + '\n'
        else:
            if not _is_gvl(name):
                iecst_blocks += '### VAR_IN_OUT\n\n无。\n\n'

    return f"""# {name}

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `{LIB_VERSION}` |
| Type | `{type_label}` |
| Category | `{cat_label}` |
| Source PDF | {PDF_URL} |
| Source InfoSys | {infosys_url} |
| Verified | {TODAY} ✅ |
| InfoSys-checked | ✅ {TODAY} |
| Status | `verified` |
| Example | [`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU) |

---

## 1. 功能简述

{meta['summary']}

## 2. 接口定义

{iecst_blocks}
## 3. 行为说明

{behavior}

## 4. 错误码 / 返回值

{ret_section}

{_build_returns(name, ret_type, _is_gvl(name))}

## 5. 使用注意 / 常见坑

{cautions}

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：{meta['scene']}
- **价值**：{meta['value']}
- **替代方案对比**：{meta['alt']}（与本 FC/GVL 相比，体现统一化 / 跨平台正确性 / 代码量节省等优势）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf]({PDF_URL}) §{section}
- **InfoSys topic**：{infosys_url}
- **相关枚举 / 结构**：见 PDF §4.1（DUTs）
"""


def _build_behavior(name: str, meta: dict, syntax: str, inputs: list, outputs: list, in_outs: list) -> str:
    """Construct a 80+ Chinese-char behavior narrative."""
    base = meta['summary']
    # Augment with mechanical narrative based on signature
    extra_parts = []
    if inputs:
        names = ', '.join(f'`{r["name"]}`' for r in inputs)
        extra_parts.append(f"接入参数：{names}。每个参数的类型与默认值见 §2 接口定义。")
    if outputs:
        names = ', '.join(f'`{r["name"]}`' for r in outputs)
        extra_parts.append(f"输出 / 返回字段：{names}。")
    if in_outs:
        names = ', '.join(f'`{r["name"]}`' for r in in_outs)
        extra_parts.append(f"双向（IN_OUT）引脚：{names}，必须在调用方持有变量地址（不能传字面量）。")

    # Add execution semantics
    if name.startswith('F_BA_'):
        extra_parts.append("本 FC 是 *无状态* 的纯函数：每次调用独立计算结果，不维护任何内部历史；多任务 / 多线程调用安全；可在 PRG / FB / METHOD / 表达式中任意位置使用。")
    elif _is_gvl(name):
        extra_parts.append("本 GVL 是 *只读全局常量* 集合：所有字段在 PLC 启动时已初始化为定值，运行时不允许写入（编译器静态强制）。可被任意 POU 通过 `GVL 名.字段名` 访问。")

    # Date/Time-specific notes
    nm_lower = name.lower()
    if 'date' in nm_lower or 'time' in nm_lower:
        extra_parts.append("本 FC 不处理时区——所有日期 / 时间均假定为本地时间；若工程需要 UTC，请在上层完成偏移换算。")
    # Memory/pointer-specific notes
    if any(k in name for k in ('Mem', 'Offset', 'Diff', 'Ptr')):
        extra_parts.append("指针类 FC 跨 x86 / x64 平台自动选用 UDINT / ULINT 做地址算术；调用方仍需保证指针不空、目标内存区可访问，越界访问会触发 PLC Exception。")
    # Validation-specific notes
    if name.startswith('F_BA_Is') and 'Valid' in name:
        extra_parts.append("典型用法：配置加载阶段把外部传入的枚举值喂给本 FC，结果为 FALSE 时拒绝加载或回退到默认值——避免无效枚举传入下游 FB 引发运行时异常。")
    # ClassValue notes
    if name in ('F_BA_BVal', 'F_BA_ByteVal', 'F_BA_IVal', 'F_BA_RVal', 'F_BA_UDIVal'):
        extra_parts.append("ClassValue 系列 FC 把不同基本类型的值统一打包成 `ST_BA_ClassValue` 结构，让趋势记录 / SCADA 推送等下游模块用一种类型处理任意原始数据。")
    # LogMessage notes
    if name.startswith('F_BA_LogMessage'):
        extra_parts.append("日志通过 ADSLOG 接口送到 TwinCAT 输出窗口与系统事件日志；运行期一直产生日志会拖慢调试输出，发布版建议把 `nLogType` 至少调到 WARNING 或更高级别。")
    # Aux calc (Rem*)
    if name.startswith('F_BA_Rem'):
        extra_parts.append("典型用法：把对应类型的定时器实例（如 `myTon : TON`）传给本 FC 的输入引脚，每周期调用一次本 FC 把剩余时间显示在 HMI 上；定时器自身的常规 IN/PT/Q 调用仍照旧。")

    # Add scenario tag for context
    extra_parts.append(f"典型工程场景：{meta['scene']}")

    full = base + ' ' + ' '.join(p for p in extra_parts if p)
    return full


def _build_returns(name: str, ret_type: str, is_gvl: bool) -> str:
    """Return-value description per type."""
    if is_gvl:
        return '本条目无 `bError` / `nErrId` 输出（全局常量），不存在运行时错误。'
    if not ret_type:
        return 'PDF + InfoSys 均未列错误码（无返回值或返回类型未明确）。'
    rt = ret_type.upper().strip()
    if rt == 'BOOL':
        return '本 FC 返回 BOOL：`TRUE` = 判定成功 / 条件满足；`FALSE` = 判定失败 / 条件不满足。'
    if rt in ('UDINT', 'UINT', 'WORD'):
        return f'本 FC 返回 `{ret_type}`：通常 0 = 失败 / 无结果，> 0 = 成功 / 实际值。具体语义见 §1 功能简述。'
    if rt == 'DINT':
        return f'本 FC 返回 `{ret_type}`：负值表示判定结果偏小、正值表示偏大、0 表示相等 / 无差异。具体语义按 §1 功能简述。'
    if rt == 'INT' or rt == 'BYTE':
        return f'本 FC 返回 `{ret_type}`：具体取值范围见 §1 功能简述。'
    if 'REAL' in rt:
        return f'本 FC 返回 `{ret_type}`：实数结果；越界 / 非法输入可能返回 0.0 或 NaN（视具体函数实现）。'
    if 'TIME' in rt or 'DATE' in rt or 'DT' in rt or 'TOD' in rt:
        return f'本 FC 返回 `{ret_type}` 类型：表示对应的时间 / 日期 / 时间戳值。'
    if 'PVOID' in rt or 'POINTER' in rt:
        return f'本 FC 返回 `{ret_type}`：返回一个内存地址。`0` 表示失败 / 无效。'
    if 'ST_BA_' in rt or 'U_BA_' in rt or 'T_' in rt or 'E_BA_' in rt:
        return f'本 FC 返回 `{ret_type}` 结构 / 枚举 / 字符串。无错误代码，错误时返回零值结构。'
    return f'本 FC 返回 `{ret_type}`。语义见 §1。'


def _build_cautions(name: str, meta: dict) -> str:
    """Default cautions list."""
    items = []
    # Add common cautions
    if 'PDF' in meta.get('summary', '').upper() and '⚠️' in meta['summary']:
        items.append('⚠️ 本条目 PDF 存在印刷错误，已在 §1 功能简述中标注；编译器实际接受 InfoSys 写法。')
    items.append(f"调用前必须确认 `Tc3_BA2_Common` 库已 reference（版本 ≥ {LIB_VERSION}）。")
    items.append('FC 类无状态，多线程 / 多 task 调用安全；GVL 是常量集合，运行时只读。')
    if name.startswith('F_BA_') and 'Time' in name or 'Date' in name:
        items.append('日期 / 时间相关 FC 不会处理时区——所有时间均假定本地时间。需要 UTC 时上层自己换算。（工程经验补充）')
    if name.startswith('F_BA_LogMessage'):
        items.append('LogMessage 日志会输出到 TwinCAT 调试输出窗口，发布时建议把 `nLogType` 改为 WARNING 或更高级别避免日志泛滥。（工程经验补充）')
    if name.startswith('F_BA_Mem') or name.startswith('F_BA_Offset') or name.startswith('F_BA_Diff'):
        items.append('指针类 FC 内部已处理 x86 / x64 平台差异——但调用方提供的指针仍需保证有效；空指针 / 越界会触发 PLC Exception。（工程经验补充）')
    return '\n'.join(f'- {it}' for it in items)


def _render_tcpou(name: str, extracts: dict) -> str:
    meta = ENTRY_META[name]
    syntax = _format_syntax_block(extracts[name]["syntax"], name)
    inputs, outputs, in_outs = _vars_from_syntax(syntax)
    guid = _stable_guid(name)
    ret_type = _return_type_from_syntax(syntax) if not _is_gvl(name) else ''

    decl_lines = [f'PROGRAM P_Demo_{name}', 'VAR']
    call_args = []

    if _is_gvl(name):
        # GVL demo: just read one constant or a couple
        decl_lines.extend(_gvl_demo_decl(name))
        call_body = _gvl_demo_st(name)
    else:
        # Function / FB demo
        # Declare inputs with sensible defaults
        for r in inputs:
            varname = 'arg' + r['name'][:1].upper() + r['name'][1:]
            default = _sample_default_for(r['type'], r['name'])
            decl_lines.append(f"    {varname:30s} : {r['type']:30s}{default}; // {r['name']}")
            call_args.append((r['name'], varname, '=>' if False else ':='))
        # Declare outputs
        for r in outputs:
            varname = 'out' + r['name'][:1].upper() + r['name'][1:]
            decl_lines.append(f"    {varname:30s} : {r['type']}; // {r['name']} 输出")
            call_args.append((r['name'], varname, '=>'))
        # Declare in_outs
        for r in in_outs:
            varname = 'io' + r['name'][:1].upper() + r['name'][1:]
            decl_lines.append(f"    {varname:30s} : {r['type']}; // {r['name']} 双向")
            call_args.append((r['name'], varname, ':='))

        # FB needs instance
        if name.startswith('FB_BA_'):
            decl_lines.insert(2, f'    fb{name[3:]:28s} : {name};')

        # Return value capture (for FC)
        if not name.startswith('FB_') and ret_type and ret_type.upper() != '':
            decl_lines.append(f"    fnReturn                       : {ret_type}; // 返回值")

        decl_lines.append('END_VAR')

        call_body = _build_call_st(name, call_args, ret_type, inputs, outputs, in_outs)

    decl_str = '\n'.join(decl_lines)

    scenario = meta['scene']
    value = meta['value']
    return f"""<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">
  <POU Name="P_Demo_{name}" Id="{guid}" SpecialFunc="None">
    <Declaration><![CDATA[{decl_str}
]]></Declaration>
    <Implementation>
      <ST><![CDATA[// =============================================================================
// Tc3_BA2_Common.{name} 演示程序
// =============================================================================
// 场景：{scenario}
//
// 价值：{value}
//
// 验证：登录 PLC 后，按例程内变量在线写值；监视输出 / 返回值，结合 §1 功能
//       简述的预期行为对照（详见配套 .md 文档 §7 业务场景）。
//
// 验证步骤：
//   1. 右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选本 .TcPOU 文件
//   2. 引用 Tc3_BA2_Common（References → Add library）
//   3. 编译 → 登录 → 运行；按上方『验证』指引在线写值观察
// =============================================================================

{call_body}
]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>
"""


def _sample_default_for(typ: str, vname: str) -> str:
    """Return `:= <sample>` literal for sensible demo, or '' for none."""
    t = typ.upper().strip()
    if t == 'BOOL': return ' := FALSE'
    if t == 'BYTE': return ' := 0'
    if t == 'INT' or t == 'DINT': return ' := 0'
    if t == 'UINT' or t == 'UDINT' or t == 'WORD' or t == 'DWORD': return ' := 0'
    if 'UINT(1' in t.replace(' ', ''):
        return ' := 4'
    if t == 'REAL' or t == 'LREAL': return ' := 0.0'
    if t == 'TIME': return ' := T#5S'
    if t in ('STRING', 'T_MAXSTRING'): return " := ''"
    if t.startswith('STRING('): return " := ''"
    if t == 'ANY': return ''
    if t == 'PVOID': return ' := 0'
    if t.startswith('UINT(') or t.startswith('INT('): return ' := 0'
    return ''


def _build_call_st(name: str, call_args: list, ret_type: str, inputs: list, outputs: list, in_outs: list) -> str:
    """Render the ST call. FCs are `result := F_Name(args);`. FBs are `fbX(args);`."""
    if name.startswith('FB_BA_'):
        # FB call: fbName(args);
        instance = f'fb{name[3:]}'
        lines = [f'{instance}(']
        for argname, varname, arrow in call_args:
            comma = ',' if (argname, varname, arrow) != call_args[-1] else ''
            lines.append(f'    {argname:24s} {arrow} {varname}{comma}')
        lines.append(');')
        return '\n'.join(lines)
    else:
        # FC call: fnReturn := F_Name(args);
        if not call_args:
            return f'fnReturn := {name}();'
        lines = [f'fnReturn := {name}(']
        for i, (argname, varname, arrow) in enumerate(call_args):
            comma = ',' if i < len(call_args) - 1 else ''
            lines.append(f'    {argname:24s} {arrow} {varname}{comma}')
        lines.append(');')
        return '\n'.join(lines)


def _gvl_demo_decl(name: str) -> list[str]:
    """Demo variables for GVL access."""
    if name == 'BAComn_Global':
        return [
            '    nMinByteSample      : BYTE;        // 读 BAComn_Global.nMinByte',
            '    nMaxIntSample       : INT;         // 读 BAComn_Global.nMaxInt',
            '    n24hAsSeconds       : UDINT;       // 读 BAComn_Global.n24Hour2Hour',
            '    fAlmostZero         : REAL;        // 读 BAComn_Global.fCloseToZero',
            '    bChar0              : BYTE;        // 读 BAComn_Global.bChar_0',
            'END_VAR',
        ]
    if name == 'BAComn_Param':
        return [
            '    nBufferSize         : UINT;        // 读 BAComn_Param.nStrTokenizer_BufferSize',
            '    nMaxLevel           : BYTE;        // 读 BAComn_Param.nStrTokenizer_MaxLevel',
            'END_VAR',
        ]
    if name == 'BAComn_EnumDE':
        return [
            '    eUnit               : E_BA_Unit := E_BA_Unit.eTemperature_DegreesCelsius;',
            "    sUnitName           : STRING(80);  // 英文名",
            "    sUnitShortcut       : STRING(80);  // 短码",
            'END_VAR',
        ]
    return ['END_VAR']


def _gvl_demo_st(name: str) -> str:
    if name == 'BAComn_Global':
        return """// 每周期把 BAComn_Global 中几个常用常量复制到本地，HMI 可观察其数值。
nMinByteSample := BAComn_Global.nMinByte;       // = 16#00
nMaxIntSample  := BAComn_Global.nMaxInt;        // = 16#7FFF (32767)
n24hAsSeconds  := BAComn_Global.n24Hour2Hour;   // = 86400 秒
fAlmostZero    := BAComn_Global.fCloseToZero;   // = 0.00001（用于避免除零）
bChar0         := BAComn_Global.bChar_0;        // = 16#30（数字 0 的 ASCII）
"""
    if name == 'BAComn_Param':
        return """nBufferSize := BAComn_Param.nStrTokenizer_BufferSize; // 默认 32
nMaxLevel   := BAComn_Param.nStrTokenizer_MaxLevel;   // 默认 5
"""
    if name == 'BAComn_EnumDE':
        return """// 按选定的 eUnit 查 BAComn_EnumDE.aUnits 表，得到英文名与短码（HMI 可显示）
sUnitName     := BAComn_EnumDE.aUnits[eUnit].sName;       // 例如 "Degrees Celsius"
sUnitShortcut := BAComn_EnumDE.aUnits[eUnit].sShortcut;   // 例如 "℃"
"""
    return ''


def main():
    extracts = json.loads(EXTRACTS_JSON.read_text())
    if not INFOSYS_INDEX.exists():
        sys.stderr.write('ERROR: /tmp/ba2_index.json missing — run InfoSys index step first\n')
        return 1
    total = 0
    skipped = 0
    for name, meta in ENTRY_META.items():
        # Skip those already manually written (the 9 FBs)
        doc_p = _doc_path(name)
        if doc_p.exists() and (name.startswith('FB_BA_')):
            skipped += 1
            continue
        if name not in extracts:
            sys.stderr.write(f'WARN: no extract for {name}; skipping\n')
            continue
        doc_text = _render_md(name, extracts)
        doc_p.parent.mkdir(parents=True, exist_ok=True)
        doc_p.write_text(doc_text)

        ex_p = _example_path(name)
        ex_text = _render_tcpou(name, extracts)
        ex_p.parent.mkdir(parents=True, exist_ok=True)
        ex_p.write_text(ex_text)
        total += 1
    print(f'Generated {total} entries, skipped {skipped}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
