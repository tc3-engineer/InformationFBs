# Progress Log

> 由 `/doc-shard` 与 `/discover` 命令自动追加。每行格式：
> `<UTC时间> | <library> | <category> | <name> | <verified|verify-failed|pending|skipped> | <note>`

---

2026-05-09T00:00:00Z | Tc2_Standard | manual-seed | RS | verified | golden sample
2026-05-09T00:00:00Z | Tc2_Standard | manual-seed | SR | verified | golden sample
2026-05-09T00:00:00Z | Tc2_Standard | manual-seed | TON | verified | golden sample

# 2026-05-10 batch
2026-05-10T08:00:00Z | Tc2_Standard | Counter        | CTD      | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | Counter        | CTU      | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | Counter        | CTUD     | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | Timer          | TOF      | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | Timer          | TP       | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | Timer (LTIME)  | LTOF     | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | Timer (LTIME)  | LTON     | verified | doc-shard auto-gen; PDF 注释 'imter' 拼写错误已逐字保留
2026-05-10T08:00:00Z | Tc2_Standard | Timer (LTIME)  | LTP      | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | Trigger        | F_TRIG   | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | Trigger        | R_TRIG   | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | String         | CONCAT   | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | String         | DELETE   | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | String         | FIND     | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | String         | INSERT   | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | String         | LEFT     | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | String         | LEN      | verified | doc-shard auto-gen; PDF 'END_VA' 拼写错误已识别
2026-05-10T08:00:00Z | Tc2_Standard | String         | MID      | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | String         | REPLACE  | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | String         | RIGHT    | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | WString        | WCONCAT  | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | WString        | WDELETE  | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | WString        | WFIND    | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | WString        | WINSERT  | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | WString        | WLEFT    | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | WString        | WLEN     | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | WString        | WMID     | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | WString        | WREPLACE | verified | doc-shard auto-gen
2026-05-10T08:00:00Z | Tc2_Standard | WString        | WRIGHT   | verified | doc-shard auto-gen

# 2026-05-10 增补
2026-05-10T08:30:00Z | Tc2_Standard | Library version | stLibVersion_Tc2_Standard | verified | global constant; tools 扩展支持 GVL 类型 + NBSP 规范化

# 2026-05-10 batch · 3 small libs
2026-05-10T09:00:00Z | Tc2_SUPS         | CB3011                   | FB_S_UPS_CB3011                | verified | doc-shard auto-gen
2026-05-10T09:00:00Z | Tc2_SUPS         | CX50x0                   | FB_S_UPS                       | verified | doc-shard auto-gen
2026-05-10T09:00:00Z | Tc2_SUPS         | CX51x0                   | FB_S_UPS_CX51x0                | verified | doc-shard auto-gen
2026-05-10T09:00:00Z | Tc2_SUPS         | CX9020-U900              | FB_S_UPS_CX9020_U900           | verified | doc-shard auto-gen
2026-05-10T09:00:00Z | Tc2_SUPS         | BAPI                     | FB_S_UPS_BAPI                  | verified | doc-shard auto-gen
2026-05-10T09:00:00Z | Tc2_SUPS         | Function blocks          | FB_NT_QuickShutdown            | verified | doc-shard auto-gen
2026-05-10T09:00:00Z | Tc2_SUPS         | Library version          | stLibVersion_Tc2_SUPS          | verified | doc-shard auto-gen
2026-05-10T09:00:00Z | Tc2_Coupler      | Function blocks          | ReadWriteTerminalReg           | verified | doc-shard auto-gen
2026-05-10T09:00:00Z | Tc2_Coupler      | Function blocks          | CouplerReset                   | verified | doc-shard auto-gen
2026-05-10T09:00:00Z | Tc2_Coupler      | Function blocks          | FB_ReadCouplerDiag             | verified | doc-shard auto-gen
2026-05-10T09:00:00Z | Tc2_Coupler      | Function blocks          | FB_ReadCouplerRegs             | verified | doc-shard auto-gen
2026-05-10T09:00:00Z | Tc2_Coupler      | Function blocks          | FB_WriteCouplerRegs            | verified | doc-shard auto-gen
2026-05-10T09:00:00Z | Tc2_Coupler      | [obsolete functions]     | F_GetVersionTcPlcCoupler       | verified | doc-shard auto-gen; deprecated, use stLibVersion
2026-05-10T09:00:00Z | Tc2_Coupler      | Library version          | stLibVersion_Tc2_Coupler       | verified | doc-shard auto-gen
2026-05-10T09:00:00Z | Tc2_DataExchange | Watchdog function blocks | FB_CheckWatchdog               | verified | doc-shard auto-gen
2026-05-10T09:00:00Z | Tc2_DataExchange | Watchdog function blocks | FB_WriteWatchdog               | verified | doc-shard auto-gen
2026-05-10T09:00:00Z | Tc2_DataExchange | Library version          | stLibVersion_Tc2_DataExchange  | verified | doc-shard auto-gen

# 2026-05-10 batch · Tc2_Math
2026-05-10T10:00:00Z | Tc2_Math | Functions             | CEIL                  | verified | doc-shard auto-gen
2026-05-10T10:00:00Z | Tc2_Math | Functions             | FLOOR                 | verified | doc-shard auto-gen
2026-05-10T10:00:00Z | Tc2_Math | Functions             | FRAC                  | verified | doc-shard auto-gen
2026-05-10T10:00:00Z | Tc2_Math | Functions             | LMOD                  | verified | doc-shard auto-gen
2026-05-10T10:00:00Z | Tc2_Math | Functions             | LTRUNC                | verified | doc-shard auto-gen
2026-05-10T10:00:00Z | Tc2_Math | Functions             | MODABS                | verified | doc-shard auto-gen
2026-05-10T10:00:00Z | Tc2_Math | Functions             | MODTURNS              | verified | doc-shard auto-gen
2026-05-10T10:00:00Z | Tc2_Math | [obsolete functions]  | F_GetVersionTcMath    | verified | doc-shard auto-gen; deprecated
2026-05-10T10:00:00Z | Tc2_Math | Library version       | stLibVersion_Tc2_Math | verified | doc-shard auto-gen

# 2026-05-10 batch · Tc2_Utilities Round 1 (28 entries)
2026-05-10T11:00:00Z | Tc2_Utilities | LCOMPLEX functions                        | LcomplexIsNaN              | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | LCOMPLEX functions                        | LcomplexAbs                | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | FLOAT functions                           | LrealIsFinite              | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | FLOAT functions                           | LrealIsNaN                 | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | FLOAT functions                           | RealIsFinite               | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | FLOAT functions                           | RealIsNaN                  | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | [Obsolete]                                | FLOATIsFinite              | verified | deprecated
2026-05-10T11:00:00Z | Tc2_Utilities | [Obsolete]                                | FLOATIsNaN                 | verified | deprecated
2026-05-10T11:00:00Z | Tc2_Utilities | 16 bit fixed point number functions       | FIX16_TO_LREAL             | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | 16 bit fixed point number functions       | FIX16_TO_WORD              | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | 16 bit fixed point number functions       | FIX16Add                   | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | 16 bit fixed point number functions       | FIX16Align                 | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | 16 bit fixed point number functions       | FIX16Div                   | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | 16 bit fixed point number functions       | FIX16Mul                   | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | 16 bit fixed point number functions       | FIX16Sub                   | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | 16 bit fixed point number functions       | LREAL_TO_FIX16             | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | 16 bit fixed point number functions       | WORD_TO_FIX16              | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | Byte order converting functions           | HOST_TO_BE16               | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | Byte order converting functions           | HOST_TO_BE32               | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | Byte order converting functions           | HOST_TO_BE64               | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | Byte order converting functions           | HOST_TO_BE64EX             | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | Byte order converting functions           | HOST_TO_BE128              | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | Byte order converting functions           | BE16_TO_HOST               | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | Byte order converting functions           | BE32_TO_HOST               | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | Byte order converting functions           | BE64_TO_HOST               | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | Byte order converting functions           | BE64_TO_HOSTEX             | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | Byte order converting functions           | BE128_TO_HOST              | verified | doc-shard auto-gen
2026-05-10T11:00:00Z | Tc2_Utilities | Library version                           | stLibVersion_Tc2_Utilities | verified | doc-shard auto-gen

# 2026-05-10 batch · Tc2_Utilities Round 2 (Time functions, 23 entries)
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | DT_TO_FILETIME64           | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | DT_TO_SYSTEMTIME           | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | F_EuropeanLocalTime        | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | F_GetDayOfMonthEx          | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | F_GetDayOfWeek             | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | F_GetDOYOfYearMonthDay     | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | F_GetMaxMonthDays          | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | F_GetMonthOfDOY            | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | F_GetWeekOfTheYear         | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | F_TranslateFileTime64Bias  | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | F_YearIsLeapYear           | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | FILETIME64_TO_DT           | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | FILETIME64_TO_ISO8601      | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | FILETIME64_TO_SYSTEMTIME   | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | FILETIME64_TO_TOD          | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | OTSTRUCT_TO_TIME           | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | STRING_TO_SYSTEMTIME       | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | SYSTEMTIME_TO_DT           | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | SYSTEMTIME_TO_FILETIME64   | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | SYSTEMTIME_TO_ISO8601      | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | SYSTEMTIME_TO_STRING       | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | SYSTEMTIME_TO_TOD          | verified | doc-shard auto-gen
2026-05-10T12:00:00Z | Tc2_Utilities | Time functions | TIME_TO_OTSTRUCT           | verified | doc-shard auto-gen
