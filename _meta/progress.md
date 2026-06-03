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

# 2026-05-10 batch · Tc2_Utilities Round 8 (64-bit unsigned, 31 entries)
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | LREAL_TO_UINT64    | verified
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | LWORD_TO_ULARGE    | verified
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | STRING_TO_UINT64   | verified | STRING(21)
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt32x32To64      | verified | 32×32 -> 64
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UINT64_TO_LREAL    | verified
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UINT64_TO_STRING   | verified | STRING(21)
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Add64        | verified
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Add64Ex      | verified | with bOV (VAR_IN_OUT)
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64And          | verified
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Cmp64        | verified | -1/0/1
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Div16Ex      | verified | with remainder
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Div64        | verified | quotient only
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Div64Ex      | verified | with remainder
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64isZero       | verified | lowercase 'is' (cf Round 7 IsZero)
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Limit        | verified | min/in/max clamp
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Max          | verified
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Min          | verified
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Mod64        | verified
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Mul64        | verified
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Mul64Ex      | verified | with bOV
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Not          | verified
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Or           | verified
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Rol          | verified | rotate left
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Ror          | verified | rotate right
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Shl          | verified | shift left
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Shr          | verified | shift right (logical)
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Sub64        | verified | unsigned, may underflow
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | UInt64Xor          | verified
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | ULARGE_INTEGER     | verified | constructor
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | ULARGE_TO_ULINT    | verified | legacy -> native ULINT
2026-05-10T18:00:00Z | Tc2_Utilities | 64 bit integer functions (unsigned) | ULARGE_TO_LWORD    | verified | legacy -> native LWORD

# 2026-05-10 batch · Tc2_Utilities Round 9 (Functions 散, 66 entries)
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | ARG_TO_CSVFIELD                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | BIC_TO_BTN                       | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | BYTE_TO_BINSTR                   | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | BYTE_TO_DECSTR                   | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | BYTE_TO_HEXSTR                   | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | BYTE_TO_LREALEX                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | BYTE_TO_OCTSTR                   | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | BYTEARR_TO_MAXSTRING             | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | CSVFIELD_TO_ARG                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | CSVFIELD_TO_STRING               | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | DATA_TO_HEXSTR                   | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | DEG_TO_RAD                       | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | DINT_TO_DECSTR                   | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | DWORD_TO_BINSTR                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | DWORD_TO_DECSTR                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | DWORD_TO_HEXSTR                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | DWORD_TO_LREALEX                 | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | DWORD_TO_OCTSTR                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | F_BYTE_TO_CRC16_CCITT            | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | F_CheckSum16                     | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | F_CreateHashTableHnd             | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | F_CreateLinkedListHnd            | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | F_DATA_TO_CRC16_CCITT            | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | F_FormatArgToStr                 | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | F_GenerateHashValue              | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | F_GetClassIdVersioned            | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | F_LTrim                          | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | F_RTrim                          | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | F_SplitBIC                       | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | F_SwapRealEx                     | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | F_ToLCase                        | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | F_ToUCase                        | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | GUID_TO_REGSTRING                | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | GUID_TO_STRING                   | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | GuidsEqualByVal                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | HEXASCNIBBLE_TO_BYTE             | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | HEXCHRNIBBLE_TO_BYTE             | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | HEXSTR_TO_DATA                   | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | LINT_TO_DECSTR                   | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | LREAL_TO_FMTSTR                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | LWORD_TO_BASE36STR               | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | LWORD_TO_BINSTR                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | LWORD_TO_DECSTR                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | LWORD_TO_HEXSTR                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | LWORD_TO_OCTSTR                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | MAXSTRING_TO_BYTEARR             | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | PVOID_TO_BINSTR                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | PVOID_TO_DECSTR                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | PVOID_TO_HEXSTR                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | PVOID_TO_OCTSTR                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | PVOID_TO_STRING                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | RAD_TO_DEG                       | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | REGSTRING_TO_GUID                | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | ROUTETRANSPORT_TO_STRING         | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | STRING_TO_CSVFIELD               | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | STRING_TO_GUID                   | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | STRING_TO_PVOID                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | UDINT_TO_LREALEX                 | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | UINT_TO_LREALEX                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | ULINT_TO_ULARGE                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | USINT_TO_LREALEX                 | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | WORD_TO_BINSTR                   | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | WORD_TO_DECSTR                   | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | WORD_TO_HEXSTR                   | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | WORD_TO_LREALEX                  | verified
2026-05-10T19:00:00Z | Tc2_Utilities | Functions | WORD_TO_OCTSTR                   | verified

# 2026-05-10 batch · Tc2_Utilities Round 10 (Function blocks, 88 auto-generated FBs)
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | BCD_TO_DEC                               | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | DCF77_TIME                               | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | DCF77_TIME_EX                            | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | DEC_TO_BCD                               | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_AddRouteEntry                         | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_AddRouteEntryEx                       | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_AmsLogger                             | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_BasicPID                              | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_CSVMemBufferReader                    | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_CSVMemBufferWriter                    | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_CalcHashValue                         | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_CheckLicense                          | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_CheckOemLicense                       | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_EnumFindFileEntry                     | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_EnumFindFileList                      | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_EnumRouteEntry                        | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_EnumStringNumbers                     | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_FileProperties                        | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_FileRingBuffer                        | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_FileTime64ToTzSpecificLocalTime       | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_FormatString                          | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_FormatString2                         | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_GetAdaptersInfo                       | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_GetAdaptersInfoEx                     | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_GetDeviceIdentificationEx             | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_GetDongleSystemID                     | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_GetHostAddrByName                     | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_GetHostName                           | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_GetLicenseDongles                     | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_GetLicenses                           | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_GetLicensesEx                         | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_GetLocalAmsNetId                      | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_GetOemOfLicenseId                     | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_GetRouterStatusInfo                   | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_GetRtPerformanceData                  | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_GetSystemId                           | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_GetTimeZoneInformation                | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_GetVolumeId                           | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_HashTableCtrl                         | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_LicFileCopyFromDongle                 | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_LicFileCopyToDongle                   | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_LicFileCreate                         | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_LicFileDelete                         | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_LicFileGetStorageInfo                 | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_LicFileRead                           | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_LinkedListCtrl                        | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_LocalSystemTime                       | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_MemBufferMerge                        | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_MemBufferSplit                        | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_MemRingBuffer                         | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_MemRingBufferEx                       | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_MemStackBuffer                        | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_RegQueryValue                         | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_RegSetValue                           | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_RemoveRouteEntry                      | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_ScopeServerControl                    | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_SetTimeZoneInformation                | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_StringRingBuffer                      | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_SystemTimeToTzSpecificLocalTime       | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_TzSpecificLocalTimeToFileTime64       | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_TzSpecificLocalTimeToSystemTime       | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | FB_WritePersistentData                   | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | GetRemotePCInfo                          | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | NT_AbortShutdown                         | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | NT_GetTime                               | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | NT_Reboot                                | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | NT_SetLocalTime                          | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | NT_SetTimeToRTCTime                      | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | NT_Shutdown                              | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | NT_StartProcess                          | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | PLC_ReadSymInfo                          | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | PLC_ReadSymInfoByName                    | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | PLC_ReadSymInfoByNameEx                  | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | PLC_Reset                                | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | PLC_Start                                | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | PLC_Stop                                 | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | Profiler                                 | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | RTC                                      | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | RTC_EX                                   | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | RTC_EX2                                  | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | TC_Config                                | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | TC_CpuUsage                              | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | TC_CpuUsageEx                            | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | TC_Restart                               | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | TC_Stop                                  | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | TC_SysLatency                            | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | TC_SysLatencyEx                          | verified | auto-extracted VAR from PDF
2026-05-10T20:00:00Z | Tc2_Utilities | Function blocks | WritePersistentData                      | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Asynchronous text requests               | FB_AsyncStrResult                        | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Asynchronous text requests               | FB_RequestCauseRemedy                    | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Asynchronous text requests               | FB_RequestEventClassDetails              | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Asynchronous text requests               | FB_RequestEventClassName                 | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Asynchronous text requests               | FB_RequestEventDetails                   | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Asynchronous text requests               | FB_RequestEventText                      | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Asynchronous text requests               | FB_RequestTranslation                    | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Asynchronous text requests               | FB_TcCauseRemedy                         | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Asynchronous text requests               | FB_TcDetail                              | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Asynchronous text requests               | F_GetEventClassName                      | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Asynchronous text requests               | F_GetEventText                           | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | EventEntry conversion                    | AdsErr_TO_TcEventEntry                   | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | EventEntry conversion                    | HRESULTAdsErr_TO_TcEventEntry            | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | EventEntry conversion                    | TcEventEntry_TO_AdsErr                   | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | EventEntry conversion                    | TcEventEntry_TO_HRESULTAdsErr            | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Filter                                   | FB_TcClearLoggedEventsSettings           | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Filter                                   | FB_TcEventCsvExportSettings              | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Filter                                   | FB_TcEventFilter                         | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | RemoteEventLogger                        | FB_RemoteListenerBase                    | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | RemoteEventLogger                        | FB_TcRemoteEventLogger                   | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Functions and function blocks            | FB_ListenerBase2                         | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_ListenerBase2                         | Execute                                  | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_ListenerBase2                         | OnAlarmCleared                           | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_ListenerBase2                         | OnAlarmConfirmed                         | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_ListenerBase2                         | OnAlarmDisposed                          | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_ListenerBase2                         | OnAlarmRaised                            | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_ListenerBase2                         | OnMessageSent                            | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_ListenerBase2                         | Subscribe                                | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_ListenerBase2                         | Subscribe2                               | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_ListenerBase2                         | Unsubscribe                              | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Functions and function blocks            | FB_TcAlarm                               | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcAlarm                               | Clear                                    | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcAlarm                               | Confirm                                  | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcAlarm                               | Create                                   | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcAlarm                               | CreateEx                                 | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcAlarm                               | Raise                                    | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcAlarm                               | SetJsonAttribute                         | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Functions and function blocks            | FB_TcArguments                           | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcArguments                           | IsEmpty                                  | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Functions and function blocks            | FB_TcEvent                               | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Functions and function blocks            | FB_TcEventBase                           | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventBase                           | EqualsTo                                 | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventBase                           | EqualsToEventClass                       | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventBase                           | EqualsToEventEntry                       | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventBase                           | EqualsToEventEntryEx                     | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventBase                           | GetJsonAttribute                         | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventBase                           | Release                                  | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventBase                           | RequestEventClassName                    | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventBase                           | RequestEventText                         | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventBase                           | ipArguments                              | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventBase                           | ipSourceInfo                             | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Functions and function blocks            | FB_TcEventLogger                         | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventLogger                         | ClearAlarms                              | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventLogger                         | ClearAllAlarms                           | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventLogger                         | ClearLoggedEvents                        | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventLogger                         | ConfirmAlarms                            | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventLogger                         | ConfirmAllAlarms                         | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventLogger                         | ExportLoggedEvents                       | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventLogger                         | GetAlarm                                 | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventLogger                         | GetAlarmEx                               | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventLogger                         | IsAlarmRaised                            | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventLogger                         | IsAlarmRaisedEx                          | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventLogger                         | SendMessage                              | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventLogger                         | SendMessage2                             | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventLogger                         | SendMessageEx                            | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcEventLogger                         | SendMessageEx2                           | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Functions and function blocks            | FB_TcMessage                             | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcMessage                             | Create                                   | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcMessage                             | CreateEx                                 | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcMessage                             | SetJsonAttribute                         | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | Functions and function blocks            | FB_TcSourceInfo                          | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcSourceInfo                          | Clear                                    | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcSourceInfo                          | ExtendName                               | verified | auto-extracted VAR from PDF
2026-05-11T01:00:00Z | Tc3_EventLogger | FB_TcSourceInfo                          | ResetToDefault                           | verified | auto-extracted VAR from PDF
2026-05-11T04:30:00Z | Tc3_EventLogger | (audit-fix)                              | full-library                             | verified | P0-1 HRESULT template ×74 | P0-2 FB_TcAlarm.Create VAR_INPUT restored | P0-3 default-values ×15 | P0-4 PLCopenXML <derived> ×28 (REFERENCE/POINTER/STRING + 7 method-level rewires) | P1 README counts | P2 SetJsonAttribute disambiguation note | verify 74/74 PASS, lint 74/74 PASS | InfoSys cross-verified Create / SendMessage / ClearAllAlarms / FB_RequestEventText / FB_TcAlarm
2026-05-20T09:30:00Z | Tc2_System     | ads_function_blocks                      | ADSREAD                                  | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | ads_function_blocks                      | ADSREADEX                                | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | ads_function_blocks                      | ADSWRITE                                 | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | ads_function_blocks                      | ADSRDWRT                                 | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | ads_function_blocks                      | ADSRDWRTEX                               | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | ads_functions                            | ADSLOGDINT                               | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | ads_functions                            | ADSLOGLREAL                              | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | ads_functions                            | ADSLOGSTR                                | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | ads_functions                            | F_CreateAmsNetId                         | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | ads_functions                            | F_ScanAmsNetIds                          | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | character_functions                      | F_ToCHR                                  | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | character_functions                      | F_ToASC                                  | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | eventlogger_function_blocks              | ADSLOGEVENT                              | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | eventlogger_function_blocks              | ADSCLEAREVENTS                           | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | eventlogger_function_blocks              | FB_SimpleAdsLogEvent                     | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | general_function_blocks                  | DRAND                                    | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | general_function_blocks                  | FB_IecCriticalSection                    | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | general_function_blocks                  | FB_ReadTaskExceedCounter                 | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | general_function_blocks                  | FB_ResetTaskExceedCounter                | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | general_function_blocks                  | FB_SetLedColor_BAPI                      | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | general_function_blocks                  | FB_SetLedColorEx_BAPI                    | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | general_function_blocks                  | GETCURTASKINDEX                          | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | general_function_blocks                  | FB_CreateGUID                            | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | iec_sfc_function_blocks                  | AnalyzeExpression                        | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | iec_sfc_function_blocks                  | AnalyzeExpressionTable                   | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | iec_sfc_function_blocks                  | AnalyzeExpressionCombined                | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | iec_sfc_function_blocks                  | AppendErrorString                        | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | iec_sfc_function_blocks                  | SFCActionControl                         | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | time_function_blocks                     | GETCPUACCOUNT                            | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | time_function_blocks                     | GETCPUCOUNTER                            | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | time_functions                           | F_GetSystemTime                          | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | time_functions                           | F_GetTaskTime                            | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-20T09:30:00Z | Tc2_System     | time_functions                           | F_GetTaskTotalTime                       | verified | S2 scope - PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | point_to_point_motion                    | MC_MoveAbsolute                          | verified | PLCopen single-axis motion - PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | point_to_point_motion                    | MC_MoveRelative                          | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | point_to_point_motion                    | MC_MoveAdditive                          | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | point_to_point_motion                    | MC_MoveModulo                            | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | point_to_point_motion                    | MC_MoveVelocity                          | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | point_to_point_motion                    | MC_MoveContinuousAbsolute                | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | point_to_point_motion                    | MC_MoveContinuousRelative                | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | point_to_point_motion                    | MC_Halt                                  | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | point_to_point_motion                    | MC_Stop                                  | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | superposition                            | MC_MoveSuperImposed                      | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | superposition                            | MC_AbortSuperposition                    | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | homing                                   | MC_Home                                  | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | manual_motion                            | MC_Jog                                   | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | axis_coupling                            | MC_GearIn                                | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | axis_coupling                            | MC_GearInDyn                             | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | axis_coupling                            | MC_GearOut                               | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | axis_coupling                            | MC_GearInMultiMaster                     | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | phasing                                  | MC_HaltPhasing                           | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | phasing                                  | MC_PhasingAbsolute                       | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | phasing                                  | MC_PhasingRelative                       | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | torque_control                           | MC_TorqueControl                         | verified | PDF + InfoSys cross-verified
2026-05-21T10:00:00Z | Tc2_MC2        | library_version                          | stLibVersion_Tc2_MC2                     | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | function_blocks                          | FB_SocketConnect                         | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | function_blocks                          | FB_SocketClose                           | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | function_blocks                          | FB_SocketCloseAll                        | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | function_blocks                          | FB_SocketListen                          | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | function_blocks                          | FB_SocketAccept                          | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | function_blocks                          | FB_SocketSend                            | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | function_blocks                          | FB_SocketReceive                         | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | function_blocks                          | FB_SocketUdpCreate                       | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | function_blocks                          | FB_SocketUdpSendTo                       | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | function_blocks                          | FB_SocketUdpReceiveFrom                  | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | function_blocks                          | FB_SocketUdpAddMulticastAddress          | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | function_blocks                          | FB_SocketUdpDropMulticastAddress         | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | function_blocks                          | FB_TlsSocketConnect                      | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | function_blocks                          | FB_TlsSocketListen                       | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | function_blocks                          | FB_TlsSocketCreate                       | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | function_blocks                          | FB_TlsSocketAddCa                        | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | function_blocks                          | FB_TlsSocketAddCrl                       | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | function_blocks                          | FB_TlsSocketSetCert                      | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | function_blocks                          | FB_TlsSocketSetPsk                       | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | functions                                | F_CreateServerHnd                        | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | functions                                | HSOCKET_TO_STRING                        | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | functions                                | HSOCKET_TO_STRINGEX                      | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | functions                                | SOCKETADDR_TO_STRING                     | verified | PDF + InfoSys cross-verified
2026-05-21T11:30:00Z | Tc2_TcpIp      | global_constants                         | stLibVersion_Tc2_TcpIp                   | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_NcDrive    | general_soe                              | FB_SoEReset                              | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_NcDrive    | general_soe                              | FB_SoEWritePassword                      | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_NcDrive    | ax5000_soe                               | FB_SoEAX5000ReadActMainVoltage           | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_NcDrive    | ax5000_soe                               | FB_SoEAX5000SetMotorCtrlWord             | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_NcDrive    | ax5000_soe                               | FB_SoEAX5000FirmwareUpdate               | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_NcDrive    | library_version                          | F_GetVersionTcNcDrive                    | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_FlyingSaw | axis_coupling                          | MC_GearInVelo                            | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_FlyingSaw | axis_coupling                          | MC_GearInPos                             | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_FlyingSaw | diagnostics                            | MC_ReadFlyingSawCharacteristics          | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_FlyingSaw | data_types                             | MC_FlyingSawCharacValues                 | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | functions                                | F_GetVersionTcMc2Drive                   | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | general_beckhoff                         | FB_DeletePositionOffset                  | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | general_beckhoff                         | FB_BrakeControl                          | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | general_beckhoff                         | FB_SetPositionOffset                     | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | general_beckhoff                         | FB_ReadDriveInfo                         | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | general_beckhoff                         | FB_ParkAxis                              | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | general_soe                              | FB_SoERead                               | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | general_soe                              | FB_SoEWrite                              | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | general_soe                              | FB_SoEReset                              | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | general_soe                              | FB_SoEWritePassword                      | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | general_soe                              | FB_SoESetDataAccessMode                  | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | general_coe                              | FB_CoERead                               | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | general_coe                              | FB_CoEWrite                              | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | general_coe                              | FB_CoEExecuteCommand                     | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | ax5000_soe                               | FB_SoEAX5000ReadActMainVoltage           | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | ax5000_soe                               | FB_SoEAX5000SetMotorCtrlWord             | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | ax5000_soe                               | FB_SoEAX5000FirmwareUpdate               | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | ax5000_soe                               | FB_SoEAX5000SetPositionOffset            | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | ax5000_soe                               | FB_SoEAX5000DeletePositionOffset         | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | ax5000_soe                               | FB_SoEAX5000ParkAxis                     | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | ax8000_coe                               | FB_CoEAX8000BrakeControl                 | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | ax8000_coe                               | FB_CoEAX8000BrakeTest                    | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | ax8000_coe                               | FB_CoEAX8000SetPositionOffset            | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | ax8000_coe                               | FB_CoEAX8000DeletePositionOffset         | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | ax8000_coe                               | FB_CoEAX8000ParkAxis                     | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | el72xx_coe                               | FB_CoEEL72xxBrakeControl                 | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | el72xx_coe                               | FB_CoEEL72xxSetPositionOffset            | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | el72xx_coe                               | FB_CoEEL72xxDeletePositionOffset         | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc2_MC2_Drive  | soe_parameter_access                     | S_0_IDNs                                 | verified | PDF single-source (not-on-infosys)
2026-05-25T00:00:00Z | Tc3_MC2_AdvancedHoming | finalizing_functions             | MC_FinishHoming                          | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc3_MC2_AdvancedHoming | finalizing_functions             | MC_HomeDirect                            | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc3_MC2_AdvancedHoming | finalizing_functions             | MC_AbortHoming                           | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc3_MC2_AdvancedHoming | referencing_functions_passive    | MC_AbortPassiveHoming                    | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc3_MC2_AdvancedHoming | referencing_functions_passive    | MC_StepReferenceFlyingRefPulse           | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc3_MC2_AdvancedHoming | referencing_functions_passive    | MC_StepReferenceFlyingSwitch             | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc3_MC2_AdvancedHoming | step_functions                   | MC_StepAbsoluteSwitch                    | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc3_MC2_AdvancedHoming | step_functions                   | MC_StepAbsoluteSwitchDetection           | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc3_MC2_AdvancedHoming | step_functions                   | MC_StepBlock                             | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc3_MC2_AdvancedHoming | step_functions                   | MC_StepBlockDetection                    | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc3_MC2_AdvancedHoming | step_functions                   | MC_StepBlockLagBased                     | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc3_MC2_AdvancedHoming | step_functions                   | MC_StepBlockLagBasedDetection            | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc3_MC2_AdvancedHoming | step_functions                   | MC_StepLimitSwitch                       | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc3_MC2_AdvancedHoming | step_functions                   | MC_StepLimitSwitchDetection              | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc3_MC2_AdvancedHoming | step_functions                   | MC_StepReferencePulse                    | verified | PDF + InfoSys cross-verified
2026-05-25T00:00:00Z | Tc3_MC2_AdvancedHoming | step_functions                   | MC_StepReferencePulseDetection           | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | CLEARBIT32                               | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | CSETBIT32                                | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | file_function_blocks                     | FB_CreateDir                             | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | file_function_blocks                     | FB_EOF                                   | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | file_function_blocks                     | FB_FileClose                             | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | file_function_blocks                     | FB_FileDelete                            | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | file_function_blocks                     | FB_FileGets                              | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | file_function_blocks                     | FB_FileLoad                              | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | file_function_blocks                     | FB_FileOpen                              | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | file_function_blocks                     | FB_FilePuts                              | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | file_function_blocks                     | FB_FileRead                              | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | file_function_blocks                     | FB_FileRename                            | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | file_function_blocks                     | FB_FileSeek                              | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | file_function_blocks                     | FB_FileTell                              | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | file_function_blocks                     | FB_FileWrite                             | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | watchdog_function_blocks                 | FB_PcWatchDog_BAPI                       | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | watchdog_function_blocks                 | FB_PcWatchdog                            | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | file_function_blocks                     | FB_RemoveDir                             | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | F_CheckMemoryArea                        | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | F_CmpLibVersion                          | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | F_CreateIPv4Addr                         | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | F_CreateMacAddr                          | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | F_GetCpuCoreIndex                        | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | F_GetCpuCoreInfo                         | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | F_GetMappingPartner                      | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | F_GetMappingStatus                       | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | F_GetStructMemberAlignment               | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | F_GetTaskInfo                            | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | obsolete                                 | F_GetVersionTcSystem                     | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | io_port_access                           | F_IOPortRead                             | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | io_port_access                           | F_IOPortWrite                            | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | F_RaiseException                         | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | F_ScanIPv4AddrIds                        | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | F_SplitPathName                          | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | GETBIT32                                 | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | GETCURTASKINDEXEX                        | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | obsolete                                 | GETSYSTEMTIME                            | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | obsolete                                 | GETTASKTIME                              | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | LPTSIGNAL                                | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | memory_functions                         | MEMCMP                                   | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | memory_functions                         | MEMCPY                                   | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | memory_functions                         | MEMMOVE                                  | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | memory_functions                         | MEMSET                                   | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | SETBIT32                                 | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | general_functions                        | TestAndSet                               | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_System     | library_version                          | stLibVersion_Tc2_System                  | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBDiagnose                            | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBReadCoils                           | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBReadInputRegs                       | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBReadInputs                          | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBReadRegs                            | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBReadWriteRegs                       | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBUdpDiagnose                         | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBUdpReadCoils                        | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBUdpReadInputRegs                    | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBUdpReadInputs                       | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBUdpReadRegs                         | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBUdpReadWriteRegs                    | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBUdpWriteCoils                       | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBUdpWriteRegs                        | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBUdpWriteSingleCoil                  | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBUdpWriteSingleReg                   | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBWriteCoils                          | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBWriteRegs                           | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBWriteSingleCoil                     | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | function_blocks                          | FB_MBWriteSingleReg                      | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusSrv  | global_constants                         | stLibVersion_Tc2_ModbusSrv               | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | controller                             | FB_PN_SCAN                               | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | controller                             | FB_PN_SCAN_UpTo255                       | verified | PDF single-source (not-on-infosys)
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | controller                             | FB_RESET_PN_TO_FACTORY_SETTINGS          | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | controller                             | FB_SET_PN_NAME                           | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | controller_alarmdiag                   | FB_PN_ALARM_DIAG                         | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | controller_im                          | FB_PN_IM0_READ                           | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | controller_im                          | FB_PN_IM1_READ                           | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | controller_im                          | FB_PN_IM1_WRITE                          | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | controller_im                          | FB_PN_IM2_READ                           | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | controller_im                          | FB_PN_IM2_WRITE                          | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | controller_im                          | FB_PN_IM3_READ                           | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | controller_im                          | FB_PN_IM3_WRITE                          | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | controller_im                          | FB_PN_IM4_Read                           | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | controller_im                          | FB_PN_IM4_WRITE                          | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | controller_rt                          | FB_PN_ReadCompleteInfoOfDevices          | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | controller_rt                          | FB_PN_ReadStateOfDevices                 | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | device                                 | FB_PN_SEND_ALARM                         | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | device_ccat                            | FB_PROFINET_READ_IM                      | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | device_ccat                            | FB_PROFINET_READ_NAME                    | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | device_ccat                            | FB_PROFINET_READ_PRM                     | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | device_ccat                            | FB_PROFINET_SET_NAME                     | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | device_ccat                            | FB_PROFINET_WRITE_IM                     | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | device_el6631                          | FB_READ_PROFINET_NAME                    | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | device_el6631                          | FB_Read_IuM_EL6631_0010                  | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | device_el6631                          | FB_Write_IuM_EL6631_0010                 | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | port_diagnosis                         | FB_PN_GET_PORT_STATISTIC                 | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ProfinetDiag | port_diagnosis                         | FB_PN_READ_PORT_DIAG                     | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusRTU  | function_blocks                         | ModbusRtuMasterV2_Generic                | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusRTU  | function_blocks                         | ModbusRtuMasterV2_KL6x22B                | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusRTU  | function_blocks                         | ModbusRtuMasterV2_KL6x5B                 | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusRTU  | function_blocks                         | ModbusRtuMasterV2_PcCOM                  | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusRTU  | function_blocks                         | ModbusRtuSlave_Generic                   | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusRTU  | function_blocks                         | ModbusRtuSlave_KL6x22B                   | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusRTU  | function_blocks                         | ModbusRtuSlave_KL6x5B                    | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusRTU  | function_blocks                         | ModbusRtuSlave_PcCOM                     | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusRTU  | global_constants                        | Global_Version                           | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusRTU  | obsolete                                | ModbusRtuMaster_KL6x22B                  | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusRTU  | obsolete                                | ModbusRtuMaster_KL6x5B                   | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_ModbusRTU  | obsolete                                | ModbusRtuMaster_PcCOM                    | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_Filter     | function_blocks                         | FB_FTR_ActualValue                       | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_Filter     | function_blocks                         | FB_FTR_Gaussian                          | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_Filter     | function_blocks                         | FB_FTR_IIRCoeff                          | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_Filter     | function_blocks                         | FB_FTR_IIRSos                            | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_Filter     | function_blocks                         | FB_FTR_IIRSpec                           | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_Filter     | function_blocks                         | FB_FTR_LeadLag                           | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_Filter     | function_blocks                         | FB_FTR_Median                            | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_Filter     | function_blocks                         | FB_FTR_MovAvg                            | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_Filter     | function_blocks                         | FB_FTR_Notch                             | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_Filter     | function_blocks                         | FB_FTR_PT1                               | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_Filter     | function_blocks                         | FB_FTR_PT2                               | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_Filter     | function_blocks                         | FB_FTR_PT2oscillation                    | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_Filter     | function_blocks                         | FB_FTR_PT3                               | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_Filter     | function_blocks                         | FB_FTR_PTn                               | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_Filter     | function_blocks                         | FB_FTR_PTt                               | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc3_DriveMotionControl | axis_functions                  | MC_Power                                 | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc3_DriveMotionControl | axis_functions                  | MC_Reset                                 | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc3_DriveMotionControl | axis_functions                  | MC_SetPosition                           | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc3_DriveMotionControl | homing                          | MC_Home                                  | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc3_DriveMotionControl | library_version                 | stLibVersion_Tc3_DriveMotionControl      | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc3_DriveMotionControl | manual_motion                   | MC_Jog                                   | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc3_DriveMotionControl | point_to_point_motion           | MC_Halt                                  | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc3_DriveMotionControl | point_to_point_motion           | MC_MoveAbsolute                          | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc3_DriveMotionControl | point_to_point_motion           | MC_MoveModulo                            | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc3_DriveMotionControl | point_to_point_motion           | MC_MoveRelative                          | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc3_DriveMotionControl | point_to_point_motion           | MC_MoveVelocity                          | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc3_DriveMotionControl | point_to_point_motion           | MC_Stop                                  | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc3_DriveMotionControl | touch_probe                     | MC_AbortTrigger                          | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc3_DriveMotionControl | touch_probe                     | MC_TouchProbe                            | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | base                                    | FB_DMXSendRDMCommand                     | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | base                                    | FB_EL6851Communication                   | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | base                                    | FB_EL6851CommunicationEx                 | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | device_control                          | FB_DMXGetIdentifyDevice                  | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | device_control                          | FB_DMXSetIdentifyDevice                  | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | device_control                          | FB_DMXSetResetDevice                     | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | discovery                               | FB_DMXDiscMute                           | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | discovery                               | FB_DMXDiscUnMute                         | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | discovery                               | FB_DMXDiscUniqueBranch                   | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | high_level                              | FB_DMXDiscovery                          | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | high_level                              | FB_DMXDiscovery512                       | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | power_lamp                              | FB_DMXGetLampHours                       | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | power_lamp                              | FB_DMXGetLampOnMode                      | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | power_lamp                              | FB_DMXSetLampHours                       | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | power_lamp                              | FB_DMXSetLampOnMode                      | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | product_info                            | FB_DMXGetDeviceInfo                      | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | product_info                            | FB_DMXGetDeviceLabel                     | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | product_info                            | FB_DMXGetDeviceModelDescription          | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | product_info                            | FB_DMXGetManufacturerLabel               | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | product_info                            | FB_DMXGetProductDetailIdList             | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | product_info                            | FB_DMXGetSoftwareVersionLabel            | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | product_info                            | FB_DMXSetDeviceLabel                     | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | rdm_info                                | FB_DMXGetParameterDescription            | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | rdm_info                                | FB_DMXGetSupportedParameters             | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | sensor                                  | FB_DMXGetSensorDefinition                | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | sensor                                  | FB_DMXGetSensorValue                     | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | setup                                   | FB_DMXGetDMX512PersonalityDescription    | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | setup                                   | FB_DMXGetDMX512StartAddress              | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | setup                                   | FB_DMXGetSlotDescription                 | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | setup                                   | FB_DMXGetSlotInfo                        | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | setup                                   | FB_DMXSetDMX512StartAddress              | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | status                                  | FB_DMXClearStatusId                      | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | status                                  | FB_DMXGetStatusIdDescription             | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_DMX        | status                                  | FB_DMXGetStatusMessages                  | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | function_blocks                         | 3964R                                    | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | function_blocks                         | ClearComBuffer                           | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | function_blocks                         | ComReset                                 | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | function_blocks                         | KL6Configuration                         | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | function_blocks                         | KL6ReadRegisters                         | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | function_blocks                         | KL6WriteRegisters                        | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | function_blocks                         | RK512                                    | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | function_blocks                         | ReceiveByte                              | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | function_blocks                         | ReceiveData                              | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | function_blocks                         | ReceiveString                            | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | function_blocks                         | ReceiveString255                         | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | function_blocks                         | SendByte                                 | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | function_blocks                         | SendData                                 | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | function_blocks                         | SendString                               | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | function_blocks                         | SendString255                            | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | function_blocks                         | SerialLineControl                        | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | function_blocks                         | SerialLineControlADS                     | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | functions                               | ASC                                      | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | functions                               | CHR                                      | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | functions                               | ComError_TO_TcEventEntry                 | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | functions                               | P3964RError_TO_TcEventEntry              | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | functions                               | RK512Error_TO_TcEventEntry               | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | functions                               | SerialLineControlADSErr_TO_TcEventEntry  | verified | PDF + InfoSys cross-verified
2026-06-02T00:00:00Z | Tc2_SerialCom  | global_constants                        | stLibVersion_Tc2_SerialCom               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_BACnet     | client_dyn                              | FB_BACnet_DynObjectManager               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_BACnet     | global_vars                             | BACnet_Globals                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_BACnet     | global_vars                             | BACnet_Param                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_BACnet     | global_vars                             | Version                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_BACnet     | server                                  | FB_BACnet_Adapter                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_BACnet     | server                                  | FB_BACnet_Device                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_BACnet     | server                                  | FB_BACnet_Server                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | conversion                              | DCTIME64_TO_PackMLTime                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | conversion                              | DT_TO_PackMLTime                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | conversion                              | F_StateCommandToString                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | conversion                              | F_UnitModeToString                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | conversion                              | LTIME_TO_PackMLTime                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | conversion                              | TIMESTRUCT_TO_PackMLTime                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | conversion                              | TIME_TO_PackMLTime                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | conversion                              | ULINT_TO_PackMLTime                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | general                                 | M_AcknowledgeAlarm                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | general                                 | M_AcknowledgeStopReason                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | general                                 | M_AcknowledgeWarning                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | general                                 | M_ClearAlarm                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | general                                 | M_ClearStopReason                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | general                                 | M_ClearWarning                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | general                                 | M_SetAlarm                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | general                                 | M_SetStopReason                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | general                                 | M_SetWarning                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | general                                 | PML_AdminAlarm                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | general                                 | PML_AdminTime                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | packaging_machine_state                 | I_UnitState                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | packaging_machine_state                 | I_UnitStateActing                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | packaging_machine_state                 | I_UnitStateWaiting                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | packaging_machine_state                 | PML_StateMachine                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | packaging_machine_state                 | PML_UnitModeConfig                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V2  | packaging_machine_state                 | PML_UnitModeManager                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | coupler                                 | KL6301                                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | coupler                                 | KL6301_EX                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | functions                               | F_CONV_2GROUP_TO_3GROUP                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | functions                               | F_CONV_3GROUP_TO_2GROUP                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | read                                    | EIB_2OCTET_FLOAT_REC                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | read                                    | EIB_2OCTET_SIGN_REC                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | read                                    | EIB_2OCTET_UNSIGN_REC                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | read                                    | EIB_3BIT_CONTROL_REC                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | read                                    | EIB_4OCTET_FLOAT_REC                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | read                                    | EIB_4OCTET_SIGN_REC                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | read                                    | EIB_4OCTET_UNSIGN_REC                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | read                                    | EIB_8BIT_SIGN_REC                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | read                                    | EIB_8BIT_UNSIGN_REC                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | read                                    | EIB_ALL_DATA_TYPES_REC                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | read                                    | EIB_ALL_DATA_TYPES_REC_EX                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | read                                    | EIB_BIT_CONTROL_REC                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | read                                    | EIB_BIT_REC                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | read                                    | EIB_DATE_REC                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | read                                    | EIB_TIME_REC                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_2OCTET_FLOAT_SEND                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_2OCTET_FLOAT_SEND_EX                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_2OCTET_SIGN_SEND                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_2OCTET_SIGN_SEND_EX                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_2OCTET_UNSIGN_SEND                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_2OCTET_UNSIGN_SEND_EX                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_3BIT_CONTROL_SEND                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_3BIT_CONTROL_SEND_EX                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_4OCTET_FLOAT_SEND                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_4OCTET_FLOAT_SEND_EX                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_4OCTET_SIGN_SEND                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_4OCTET_SIGN_SEND_EX                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_4OCTET_UNSIGN_SEND                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_4OCTET_UNSIGN_SEND_EX                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_8BIT_SIGN_SEND                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_8BIT_SIGN_SEND_EX                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_8BIT_UNSIGN_SEND                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_8BIT_UNSIGN_SEND_EX                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_ALL_DATA_TYPES_SEND                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_BIT_CONTROL_SEND                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_BIT_CONTROL_SEND_EX                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_BIT_SEND                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_BIT_SEND_EX                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_BIT_SEND_MANUAL                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_DATE_SEND                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_DATE_SEND_EX                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_READ_SEND                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_TIME_SEND                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EIB        | send                                    | EIB_TIME_SEND_EX                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | functions                               | F_Byte_to_Temp                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | functions                               | F_Byte_to_TurnSwitch                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | kl6021_receive                          | FB_EnOceanReceive                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | kl6021_sensor                           | FB_EnOceanPTM100                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | kl6021_sensor                           | FB_EnOceanPTM200                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | kl6021_sensor                           | FB_EnOceanSTM100                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | kl6021_sensor                           | FB_EnOceanSTM100Generic                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | kl6021_sensor                           | FB_EnOceanSTM250                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | kl6581_receive                          | FB_Rec_1BS                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | kl6581_receive                          | FB_Rec_Generic                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | kl6581_receive                          | FB_Rec_RPS_Switch                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | kl6581_receive                          | FB_Rec_RPS_Window_Handle                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | kl6581_send                             | FB_Send_4BS                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | kl6581_send                             | FB_Send_Generic                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | kl6581_send                             | FB_Send_RPS_Switch                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | kl6581_send                             | FB_Send_RPS_SwitchAuto                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | kl6581_teach_in                         | FB_EnOcean_Search                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | kl6581_teach_in                         | FB_Rec_Teach_In                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | kl6581_teach_in                         | FB_Rec_Teach_In_Ex                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EnOcean    | kl6581_terminal                         | FB_KL6581                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | function_blocks                         | FB_AdsDeviceConnectionAdd                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | function_blocks                         | FB_DBConnectionAdd                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | function_blocks                         | FB_DBConnectionClose                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | function_blocks                         | FB_DBConnectionOpen                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | function_blocks                         | FB_DBCreate                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | function_blocks                         | FB_DBCyclicRdWrt                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | function_blocks                         | FB_DBOdbcConnectionAdd                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | function_blocks                         | FB_DBRead                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | function_blocks                         | FB_DBRecordArraySelect                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | function_blocks                         | FB_DBRecordDelete                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | function_blocks                         | FB_DBRecordInsert_EX                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | function_blocks                         | FB_DBReloadConfig                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | function_blocks                         | FB_DBStoredProcedures                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | function_blocks                         | FB_DBStoredProceduresRecordArray         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | function_blocks                         | FB_DBTableCreate                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | function_blocks                         | FB_DBWrite                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | function_blocks                         | FB_GetAdsDevXMLConfig                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | function_blocks                         | FB_GetDBXMLConfig                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | function_blocks                         | FB_GetStateTcDatabase                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | functions                               | F_GetVersionTcDatabase                   | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_Database   | global_constants                        | AMSPORT_DATABASESRV                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | obsolete                                | FB_DBAuthentificationAdd                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | obsolete                                | FB_DBRecordInsert                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | obsolete                                | FB_DBRecordSelect                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | obsolete                                | FB_DBRecordSelect_EX                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Database   | obsolete                                | FB_DBStoredProceduresRecordReturn        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | ads                                     | FB_EcReadBIC                             | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | ads                                     | FB_EcReadBTN                             | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | coe                                     | FB_CoERead_ByDriveRef                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | coe                                     | FB_CoEWrite_ByDriveRef                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | coe                                     | FB_EcCoESdoAbortCode                     | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | coe                                     | FB_EcCoeReadBIC                          | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | coe                                     | FB_EcCoeReadBTN                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | coe                                     | FB_EcCoeSdoRead                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | coe                                     | FB_EcCoeSdoReadEx                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | coe                                     | FB_EcCoeSdoWrite                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | coe                                     | FB_EcCoeSdoWriteEx                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | commands                                | FB_EcLogicalReadCmd                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | commands                                | FB_EcLogicalWriteCmd                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | commands                                | FB_EcPhysicalReadCmd                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | commands                                | FB_EcPhysicalWriteCmd                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | conversion                              | F_ConvBK1120CouplerStateToString         | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | conversion                              | F_ConvMasterDevStateToString             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | conversion                              | F_ConvProductCodeToString                | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | conversion                              | F_ConvSlaveStateToBits                   | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | conversion                              | F_ConvSlaveStateToBitsEx                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | conversion                              | F_ConvSlaveStateToString                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | conversion                              | F_ConvStateToString                      | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcGetAllMasters                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcGetAllSlaveAbnormalStateChanges     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcGetAllSlaveAddr                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcGetAllSlaveCrcErrors                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcGetAllSlavePresentStateChanges      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcGetAllSyncUnitSlaveAddr             | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcGetConfSlaves                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcGetLastProtErrInfo                  | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcGetMasterDevState                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcGetScannedSlaves                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcGetSlaveCount                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcGetSlaveCrcError                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcGetSlaveCrcErrorEx                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcGetSlaveIdentity                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcGetSlaveTopologyInfo                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcMasterFrameCount                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcMasterFrameStatistic                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcMasterFrameStatisticClearCRC        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcMasterFrameStatisticClearFrames     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcMasterFrameStatisticClearTxRxErr    | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | FB_EcMasterObjectID                      | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | F_CheckVendorId                          | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | F_EcGetLinkedTaskOfSyncUnit              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | F_EcGetMailboxGatewayAddr                | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | diagnostic                              | F_EcGetSyncUnitName                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | ConvertDcTimeToPathPos                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | ConvertDcTimeToPos                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | ConvertPathPosToDcTime                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | ConvertPosToDcTime                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | DCTIME64_TO_DCTIME                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | DCTIME64_TO_DCTIMESTRUCT                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | DCTIME64_TO_FILETIME64                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | DCTIME64_TO_STRING                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | DCTIME64_TO_SYSTEMTIME                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | DCTIMESTRUCT_TO_DCTIME64                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | DCTIME_TO_DCTIME64                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | FB_EcDcTimeCtrl64                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | FB_EcExtSyncCalcTimeDiff64               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | FB_EcExtSyncCheck64                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | FILETIME64_TO_DCTIME64                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | F_ConvExtTimeToDcTime64                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | F_ConvTcTimeToDcTime64                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | F_ConvTcTimeToExtTime64                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | F_GetActualDcTime64                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | F_GetCurDcTaskTime64                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | F_GetCurDcTickTime64                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | F_GetCurExtTime64                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | STRING_TO_DCTIME64                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | distributed_clocks                      | SYSTEMTIME_TO_DCTIME64                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | foe                                     | FB_EcFoeAccess                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | foe                                     | FB_EcFoeClose                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | foe                                     | FB_EcFoeLoad                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | foe                                     | FB_EcFoeOpen                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | foe                                     | FB_EcFoeReadFile                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | foe                                     | FB_EcFoeWriteFile                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | DCTIME64_TO_FILETIME                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | DCTIMESTRUCT_TO_DCTIME                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | DCTIME_TO_DCTIMESTRUCT                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | DCTIME_TO_FILETIME                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | DCTIME_TO_STRING                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | DCTIME_TO_SYSTEMTIME                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | FB_EcDcTimeCtrl                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | FB_EcExtSyncCalcTimeDiff                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | FB_EcExtSyncCheck                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | FILETIME_TO_DCTIME                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | FILETIME_TO_DCTIME64                     | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | F_ConvExtTimeToDcTime                    | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | F_ConvTcTimeToDcTime                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | F_ConvTcTimeToExtTime                    | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | F_GetActualDcTime                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | F_GetCurDcTaskTime                       | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | F_GetCurDcTickTime                       | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | F_GetCurExtTime                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | F_GetVersionTcEtherCAT                   | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | STRING_TO_DCTIME                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | obsolete                                | SYSTEMTIME_TO_DCTIME                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | soe                                     | FB_EcSoeRead                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | soe                                     | FB_EcSoeWrite                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | soe                                     | FB_SoERead_ByDriveRef                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | soe                                     | FB_SoEWrite_ByDriveRef                   | verified | PDF single-source (not-on-infosys)
2026-06-03T00:00:00Z | Tc2_EtherCAT   | state_machine                           | FB_EcGetAllSlaveStates                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | state_machine                           | FB_EcGetMasterState                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | state_machine                           | FB_EcGetSlaveState                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | state_machine                           | FB_EcReqMasterState                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | state_machine                           | FB_EcReqSlaveState                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | state_machine                           | FB_EcSetMasterState                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_EtherCAT   | state_machine                           | FB_EcSetSlaveState                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | blocksearch                             | ItpBlocksearch                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | blocksearch                             | ItpGetBlocksearchData                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | blocksearch                             | ItpStepOnAfterBlocksearch                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpDelDtg                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpEStop                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpGetBottleNeckLookAhead                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpGetBottleNeckMode                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpGetGeoInfoAndHParam                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpGoAhead                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpIsEStop                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpLoadProg                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpReadRParams                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpReadToolDesc                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpReadZeroShift                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpReset                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpResetEx                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpResetFastMFunc                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpSetBottleNeckLookAhead                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpSetBottleNeckMode                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpSetSubroutinePath                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpSetToolDescNull                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpSetZeroShiftNull                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpStartStop                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpStepOnAfterEStop                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpWriteRParams                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpWriteToolDesc                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | compatibility                           | ItpWriteZeroShift                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | configuration                           | CfgAddAxisToGroup                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | configuration                           | CfgBuild3DGroup                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | configuration                           | CfgBuildExt3DGroup                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | configuration                           | CfgRead3DAxisIds                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | configuration                           | CfgReadExt3DAxisIds                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | configuration                           | CfgReconfigAxis                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | configuration                           | CfgReconfigGroup                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpConfirmHsk                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpDelDtgEx                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpEStopEx                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpEnableDefaultGCode                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGetBlockNumber                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGetBottleNeckLookAheadEx              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGetBottleNeckModeEx                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGetChannelId                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGetChannelType                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGetCyclicLrealOffsets                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGetCyclicUDintOffsets                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGetError                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGetGeoInfoAndHParamEx                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGetGroupAxisIds                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGetGroupId                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGetHParam                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGetHskMFunc                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGetItfVersion                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGetOverridePercent                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGetSParam                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGetSetPathVelocity                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGetStateInterpreter                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGetTParam                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpGoAheadEx                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpHasError                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpIsEStopEx                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpIsFastMFunc                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpIsHskMFunc                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpLoadProgEx                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpReadCyclicLRealParam1                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpReadCyclicUdintParam1                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpReadRParamsEx                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpReadToolDescEx                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpReadZeroShiftEx                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpResetEx2                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpResetFastMFuncEx                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpSetBottleNeckLookAheadEx              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpSetBottleNeckModeEx                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpSetCyclicLrealOffsets                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpSetCyclicUDintOffsets                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpSetOverridePercent                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpSetSubroutinePathEx                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpSetToolDescNullEx                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpSetZeroShiftNullEx                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpSingleBlock                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpStartStopEx                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpStepOnAfterEStopEx                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpWriteRParamsEx                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpWriteToolDescEx                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | nci_pous                                | ItpWriteZeroShiftEx                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | obsolete                                | F_GetVersionTcNciUtilities               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | obsolete                                | Get_TcNcCfg_Version                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | obsolete                                | ItpGetVersion                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | parts_program_generator                 | ItpPpgAppendGenericBlock                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | parts_program_generator                 | ItpPpgAppendGeoCircleByRadius            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | parts_program_generator                 | ItpPpgAppendGeoLine                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | parts_program_generator                 | ItpPpgCloseMain                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | parts_program_generator                 | ItpPpgCloseSubroutine                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | parts_program_generator                 | ItpPpgCreateMain                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | parts_program_generator                 | ItpPpgCreateSubroutine                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | retrace                                 | ItpEnableFeederBackup                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | retrace                                 | ItpIsFeedFromBackupList                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | retrace                                 | ItpIsFeederBackupEnabled                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | retrace                                 | ItpIsFirstSegmentReached                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | retrace                                 | ItpIsMovingBackwards                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | retrace                                 | ItpRetraceMoveBackward                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_NCI        | retrace                                 | ItpRetraceMoveForward                    | verified | PDF + InfoSys cross-verified
