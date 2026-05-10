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

# 2026-05-10 batch · Tc2_Utilities Round 3 (TC_CoreBoostMonitor + obsolete FBs, 10 entries)
2026-05-10T13:00:00Z | Tc2_Utilities | Function blocks      | TC_CoreBoostMonitor               | verified | parent FB (OO)
2026-05-10T13:00:00Z | Tc2_Utilities | TC_CoreBoostMonitor  | GetAllRtCoreThrottling            | verified | METHOD on TC_CoreBoostMonitor
2026-05-10T13:00:00Z | Tc2_Utilities | TC_CoreBoostMonitor  | GetCoreFrequency                  | verified | METHOD on TC_CoreBoostMonitor
2026-05-10T13:00:00Z | Tc2_Utilities | TC_CoreBoostMonitor  | GetCoreTemperature                | verified | METHOD on TC_CoreBoostMonitor
2026-05-10T13:00:00Z | Tc2_Utilities | TC_CoreBoostMonitor  | GetCoreThrottling                 | verified | METHOD on TC_CoreBoostMonitor
2026-05-10T13:00:00Z | Tc2_Utilities | TC_CoreBoostMonitor  | GetPowerConsumption               | verified | METHOD on TC_CoreBoostMonitor
2026-05-10T13:00:00Z | Tc2_Utilities | [obsolete]           | FB_AdsReadEvents                  | verified | deprecated; replaced by Tc3_EventLogger
2026-05-10T13:00:00Z | Tc2_Utilities | [obsolete]           | FB_GetDeviceIdentification        | verified | deprecated; use *Ex variant
2026-05-10T13:00:00Z | Tc2_Utilities | [obsolete]           | FB_FileTimeToTzSpecificLocalTime  | verified | deprecated; use FB_FileTime64ToTz...
2026-05-10T13:00:00Z | Tc2_Utilities | [obsolete]           | FB_TzSpecificLocalTimeToFileTime  | verified | deprecated; use FB_TzSpecificLocalTimeToFileTime64

# 2026-05-10 batch · Tc2_Utilities Round 4 (T_Arg help functions, 27 entries)
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_ARGCMP    | verified | doc-shard auto-gen
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_ARGCPY    | verified | doc-shard auto-gen; uses VAR_IN_OUT for dest/src
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_ARGISZERO | verified | doc-shard auto-gen
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_BIGTYPE   | verified | doc-shard auto-gen; pointer + length pattern for struct/array
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_BOOL      | verified | typed wrapper
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_BYTE      | verified | typed wrapper
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_DINT      | verified | typed wrapper
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_DWORD     | verified | typed wrapper
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_HUGE      | verified | typed wrapper (T_HUGE_INTEGER)
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_INT       | verified | typed wrapper
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_LARGE     | verified | typed wrapper (T_LARGE_INTEGER)
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_LINT      | verified | typed wrapper
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_LREAL     | verified | typed wrapper
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_LWORD     | verified | typed wrapper
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_REAL      | verified | typed wrapper
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_SINT      | verified | typed wrapper
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_STRING    | verified | typed wrapper (T_MaxString fixed-len)
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_STRINGEx  | verified | typed wrapper (arbitrary-len STRING via VAR_IN_OUT CONSTANT)
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_UDINT     | verified | typed wrapper
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_UHUGE     | verified | typed wrapper (T_UHUGE_INTEGER)
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_UINT      | verified | typed wrapper
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_ULARGE    | verified | typed wrapper (T_ULARGE_INTEGER)
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_ULINT     | verified | typed wrapper
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_USINT     | verified | typed wrapper
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_WORD      | verified | typed wrapper
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | F_PVOID     | verified | typed wrapper (PVOID)
2026-05-10T14:00:00Z | Tc2_Utilities | T_Arg help functions | IsFinite    | verified | LREAL/REAL IEEE finite check; needs F_LREAL/F_REAL wrapper

# 2026-05-10 batch · Tc2_Utilities Round 5 (P[TYPE]_TO_[TYPE], 26 entries)
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PBOOL_TO_BOOL           | verified | uniform pointer-deref pattern
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PBYTE_TO_BYTE           | verified | uniform pointer-deref pattern
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PDATE_TO_DATE           | verified | uniform pointer-deref pattern
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PDINT_TO_DINT           | verified | uniform pointer-deref pattern
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PDT_TO_DT               | verified | uniform pointer-deref pattern
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PDWORD_TO_DWORD         | verified | uniform pointer-deref pattern
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PHUGE_TO_HUGE           | verified | T_HUGE_INTEGER 128-bit legacy
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PINT_TO_INT             | verified | uniform pointer-deref pattern
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PLARGE_TO_LARGE         | verified | T_LARGE_INTEGER 64-bit legacy
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PLINT_TO_LINT           | verified | uniform pointer-deref pattern
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PLREAL_TO_LREAL         | verified | uniform pointer-deref pattern
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PLWORD_TO_LWORD         | verified | uniform pointer-deref pattern
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PMAXSTRING_TO_MAXSTRING | verified | T_MaxString
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PREAL_TO_REAL           | verified | uniform pointer-deref pattern
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PSINT_TO_SINT           | verified | uniform pointer-deref pattern
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PSTRING_TO_STRING       | verified | PDF table 'String' typo, VAR_INPUT 'STRING' authoritative
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PTIME_TO_TIME           | verified | uniform pointer-deref pattern
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PTOD_TO_TOD             | verified | uniform pointer-deref pattern
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PUDINT_TO_UDINT         | verified | uniform pointer-deref pattern
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PUHUGE_TO_UHUGE         | verified | T_UHUGE_INTEGER 128-bit legacy
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PUINT_TO_UINT           | verified | uniform pointer-deref pattern
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PULARGE_TO_ULARGE       | verified | T_ULARGE_INTEGER 64-bit legacy
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PULINT_TO_ULINT         | verified | uniform pointer-deref pattern
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PUSINT_TO_USINT         | verified | uniform pointer-deref pattern
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PWORD_TO_WORD           | verified | uniform pointer-deref pattern
2026-05-10T15:00:00Z | Tc2_Utilities | P[TYPE]_TO_[TYPE] | PUINT64_TO_UINT64       | verified | name has UINT64 but returns T_ULARGE_INTEGER

# 2026-05-10 batch · Tc2_Utilities Round 6 (Extended STRING functions, 30 entries)
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | CHAR_TO_WCHAR        | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | CONCAT2              | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | DATA_TO_HEXSTR2      | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | DELETE2              | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | F_StringIsASCII      | verified | PDF doc-table 'pString' typo, VAR_INPUT 'pSTRING' authoritative
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | FIND2                | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | FindAndDelete        | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | FindAndDeleteChar    | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | FindAndReplace       | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | FindAndReplaceChar   | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | FindAndSplit         | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | FindAndSplitChar     | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | HEXSTR_TO_DATA2      | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | INSERT2              | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | LEN2                 | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | REPLACE2             | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | sLiteral_TO_UTF8     | verified | VAR_IN_OUT CONSTANT
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | STRING_TO_UTF8       | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | STRING_TO_WSTRING2   | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | STRNCPY              | verified | with VAR_OUTPUT nSrcLen/nDstLen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | UTF8_TO_STRING       | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | UTF8_TO_WSTRING      | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | UTF8Len              | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | WCHAR_TO_CHAR        | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | WCONCAT2             | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | WLEN2                | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | wsLiteral_TO_UTF8    | verified | VAR_IN_OUT CONSTANT
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | WSTRING_TO_STRING2   | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | WSTRING_TO_UTF8      | verified | doc-shard auto-gen
2026-05-10T16:00:00Z | Tc2_Utilities | Extended STRING functions | WSTRNCPY             | verified | with VAR_OUTPUT nSrcLen/nDstLen

# 2026-05-10 batch · Tc2_Utilities Round 7 (64-bit signed, 15 entries)
2026-05-10T17:00:00Z | Tc2_Utilities | 64 bit functions (signed) | INT64_TO_LREAL    | verified | doc-shard auto-gen
2026-05-10T17:00:00Z | Tc2_Utilities | 64 bit functions (signed) | Int64Add64        | verified | doc-shard auto-gen
2026-05-10T17:00:00Z | Tc2_Utilities | 64 bit functions (signed) | Int64Add64Ex      | verified | with bOV overflow flag (VAR_IN_OUT)
2026-05-10T17:00:00Z | Tc2_Utilities | 64 bit functions (signed) | Int64Cmp64        | verified | -1/0/1 tri-state
2026-05-10T17:00:00Z | Tc2_Utilities | 64 bit functions (signed) | Int64Div64Ex      | verified | with remainder (VAR_IN_OUT)
2026-05-10T17:00:00Z | Tc2_Utilities | 64 bit functions (signed) | Int64IsZero       | verified | PDF return-table typo "Int64isZero" lowercase i, real name uppercase
2026-05-10T17:00:00Z | Tc2_Utilities | 64 bit functions (signed) | Int64Negate       | verified | doc-shard auto-gen
2026-05-10T17:00:00Z | Tc2_Utilities | 64 bit functions (signed) | Int64Not          | verified | doc-shard auto-gen
2026-05-10T17:00:00Z | Tc2_Utilities | 64 bit functions (signed) | Int64Sub64        | verified | no overflow check
2026-05-10T17:00:00Z | Tc2_Utilities | 64 bit functions (signed) | LARGE_INTEGER     | verified | constructor (high/low DWORD)
2026-05-10T17:00:00Z | Tc2_Utilities | 64 bit functions (signed) | LARGE_TO_LINT     | verified | legacy -> native 64-bit
2026-05-10T17:00:00Z | Tc2_Utilities | 64 bit functions (signed) | LARGE_TO_ULARGE   | verified | signed -> unsigned bit-cast
2026-05-10T17:00:00Z | Tc2_Utilities | 64 bit functions (signed) | LINT_TO_LARGE     | verified | native -> legacy 64-bit
2026-05-10T17:00:00Z | Tc2_Utilities | 64 bit functions (signed) | LREAL_TO_INT64    | verified | LREAL -> legacy 64-bit
2026-05-10T17:00:00Z | Tc2_Utilities | 64 bit functions (signed) | ULARGE_TO_LARGE   | verified | unsigned -> signed bit-cast
