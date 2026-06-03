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
2026-06-03T00:00:00Z | Tc2_Hydraulic  | administrative                          | MC_Power_BkPlcMc                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | administrative                          | MC_ReadActualPosition_BkPlcMc            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | administrative                          | MC_ReadActualTorque_BkPlcMc              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | administrative                          | MC_ReadActualVelocity_BkPlcMc            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | administrative                          | MC_ReadAxisError_BkPlcMc                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | administrative                          | MC_ReadStatus_BkPlcMc                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | administrative                          | MC_ResetAndStop_BkPlcMc                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | administrative                          | MC_Reset_BkPlcMc                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | administrative                          | MC_SetOverride_BkPlcMc                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | administrative                          | MC_SetPosition_BkPlcMc                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | administrative                          | MC_SetReferenceFlag_BkPlcMc              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | controllers                             | MC_AxCtrlAutoZero_BkPlcMc                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | controllers                             | MC_AxCtrlPressure_BkPlcMc                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | controllers                             | MC_AxCtrlSlowDownOnPressure_BkPlcMc      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | homing                                  | MC_Home_BkPlcMc                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | motion_multiple_axis                    | MC_CamIn_BkPlcMc                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | motion_multiple_axis                    | MC_CamOut_BkPlcMc                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | motion_multiple_axis                    | MC_GearInPos_BkPlcMc                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | motion_multiple_axis                    | MC_GearIn_BkPlcMc                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | motion_multiple_axis                    | MC_GearOut_BkPlcMc                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | motion_single_axis                      | MC_EmergencyStop_BkPlcMc                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | motion_single_axis                      | MC_Halt_BkPlcMc                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | motion_single_axis                      | MC_ImediateStop_BkPlcMc                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | motion_single_axis                      | MC_MoveAbsolute_BkPlcMc                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | motion_single_axis                      | MC_MoveJoySticked_BkPlcMc                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | motion_single_axis                      | MC_MoveRelative_BkPlcMc                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | motion_single_axis                      | MC_MoveVelocity_BkPlcMc                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | motion_single_axis                      | MC_RampedStop_BkPlcMc                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | motion_single_axis                      | MC_Stop_BkPlcMc                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | pressure_force_sensing                  | MC_AxRtReadForceDiff_BkPlcMc             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | pressure_force_sensing                  | MC_AxRtReadForceSingle_BkPlcMc           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | pressure_force_sensing                  | MC_AxRtReadPressureDiff_BkPlcMc          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_Hydraulic  | pressure_force_sensing                  | MC_AxRtReadPressureSingle_BkPlcMc        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V3  | conversion                              | DCTIME64_TO_PMLTime                      | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | conversion                              | DT_TO_PMLTime                            | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | conversion                              | F_PMLStateCommandToString                | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | conversion                              | F_PMLUnitModeToString                    | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | conversion                              | LTIME_TO_PMLTime                         | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | conversion                              | TIMESTRUCT_TO_PMLTime                    | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | conversion                              | TIME_TO_PMLTime                          | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | conversion                              | ULINT_TO_PMLTime                         | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | general                                 | FB_PMLAdminAlarm                         | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | general                                 | FB_PMLAdminTime                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V3  | general                                 | M_AcknowledgeAlarm                       | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | general                                 | M_AcknowledgeAllAlarms                   | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | general                                 | M_AcknowledgeAllWarning                  | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | general                                 | M_AcknowledgeStopReason                  | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | general                                 | M_AcknowledgeWarning                     | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | general                                 | M_ClearAlarm                             | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | general                                 | M_ClearAllAlarms                         | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | general                                 | M_ClearAllWarning                        | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | general                                 | M_ClearStopReason                        | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | general                                 | M_ClearWarning                           | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | general                                 | M_GetAlarmCategory                       | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | general                                 | M_HasAlarm                               | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | general                                 | M_HasStopReason                          | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | general                                 | M_HasWarning                             | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | general                                 | M_SetAlarm                               | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | general                                 | M_SetStopReason                          | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | general                                 | M_SetWarning                             | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | interfaces                              | I_PMLUnitStateActing                     | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | interfaces                              | I_PMLUnitStateWaiting                    | verified | PDF single-source (not-on-infosys, V3 new)
2026-06-03T00:00:00Z | Tc3_PackML_V3  | packaging_machine_state                 | FB_PMLStateMachine                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V3  | packaging_machine_state                 | FB_PMLUnitModeConfig                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_PackML_V3  | packaging_machine_state                 | FB_PMLUnitModeManager                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_BACnet     | client                                  | FB_BACnetRM_AI                           | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | client                                  | FB_BACnetRM_AV                           | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | client                                  | FB_BACnetRM_BO                           | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | client                                  | FB_BACnetRM_Device                       | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | client                                  | FB_BACnetRM_MI                           | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | client                                  | FB_BACnetRM_MV                           | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | client                                  | FB_BACnetRM_ReadProperty                 | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | client                                  | FB_BACnetRM_ReadPropertyEx               | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | client                                  | FB_BACnetRM_SchedA                       | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | client                                  | FB_BACnetRM_SchedB                       | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | client                                  | FB_BACnetRM_SchedM                       | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | client                                  | FB_BACnetRM_WriteProperty                | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | client                                  | FB_BACnetRM_WritePropertyEx              | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | client                                  | FB_BACnet_Client                         | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_ACC                            | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_AI                             | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_AO                             | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_AV                             | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_BI                             | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_BO                             | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_BV                             | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_Cal                            | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_EE                             | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_ELog                           | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_File                           | verified | PDF chapter-overview (infer-from-naming-convention)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_Loop                           | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_MI                             | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_MO                             | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_MV                             | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_NC                             | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_PC                             | verified | PDF chapter-overview (infer-from-naming-convention)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_Prog                           | verified | PDF chapter-overview (infer-from-naming-convention)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_SchedA                         | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_SchedB                         | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_SchedM                         | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_TLM                            | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_TLog                           | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | objects                                 | FB_BACnet_View                           | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | primitive_values                        | FB_BACnet_Date                           | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | primitive_values                        | FB_BACnet_DateTime                       | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | primitive_values                        | FB_BACnet_INT                            | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | primitive_values                        | FB_BACnet_LAV                            | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | primitive_values                        | FB_BACnet_String                         | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | primitive_values                        | FB_BACnet_Time                           | verified | PDF chapter-overview (chapter-overview-only)
2026-06-03T00:00:00Z | Tc2_BACnet     | server                                  | FB_BACnet_ReadProperty                   | verified | PDF chapter-overview (infer-from-naming-convention)
2026-06-03T00:00:00Z | Tc2_BACnet     | server                                  | FB_BACnet_WriteProperty                  | verified | PDF chapter-overview (infer-from-naming-convention)
2026-06-03T00:00:00Z | Tc3_Database   | function_blocks                         | FB_ConfigTcDBSrvEvt                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | function_blocks                         | FB_NoSQLObjectId_MongoDB                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | function_blocks                         | FB_NoSQLQueryBuilder_DocumentDB          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | function_blocks                         | FB_NoSQLQueryBuilder_TimeSeriesDB        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | function_blocks                         | FB_NoSQLQueryEvt                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | function_blocks                         | FB_NoSQLResultEvt                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | function_blocks                         | FB_NoSQLValidationEvt                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | function_blocks                         | FB_PLCDBAutoLogEvt                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | function_blocks                         | FB_PLCDBCmdEvt                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | function_blocks                         | FB_PLCDBCreateEvt                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | function_blocks                         | FB_PLCDBReadEvt                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | function_blocks                         | FB_PLCDBWriteEvt                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | function_blocks                         | FB_SQLCommandEvt                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | function_blocks                         | FB_SQLDatabaseEvt                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | function_blocks                         | FB_SQLResultEvt                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | function_blocks                         | FB_SQLStoredProcedureEvt                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | global_constants                        | Constants                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | obsolete                                | FB_ConfigTcDBSrv                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | obsolete                                | FB_PLCDBAutoLog                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | obsolete                                | FB_PLCDBCmd                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | obsolete                                | FB_PLCDBCreate                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | obsolete                                | FB_PLCDBRead                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | obsolete                                | FB_PLCDBWrite                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | obsolete                                | FB_SQLCommand                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | obsolete                                | FB_SQLDatabase                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | obsolete                                | FB_SQLResult                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_Database   | obsolete                                | FB_SQLStoredProcedure                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | auxiliary_calc                          | F_BA_RemMsTof                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | auxiliary_calc                          | F_BA_RemMsTon                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | auxiliary_calc                          | F_BA_RemMsTp                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | auxiliary_calc                          | F_BA_RemSecsTof                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | auxiliary_calc                          | F_BA_RemSecsTone                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | auxiliary_calc                          | F_BA_RemSecsTp                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | check_enum                              | F_BA_CheckEnum                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | class_value                             | F_BA_BVal                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | class_value                             | F_BA_ByteVal                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | class_value                             | F_BA_IVal                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | class_value                             | F_BA_RVal                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | class_value                             | F_BA_UDIVal                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | compare                                 | F_BA_CompareVersion                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | controllers                             | FB_BA_PIDCtrl                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_check                              | F_BA_DateHasPlaceholder                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_check                              | F_BA_DateUnspecified                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_check                              | F_BA_IsLeapYear                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_check                              | F_BA_TimeHasPlaceholder                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_check                              | F_BA_TimeUnspecified                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_convert                            | F_BA_TimeStruct_TO_DateTime              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_convert                            | F_BA_TimeStruct_TO_Time                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_convert                            | F_BA_To100msDate                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_convert                            | F_BA_To100msTime                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_convert                            | F_BA_ToDT                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_convert                            | F_BA_ToDate                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_convert                            | F_BA_ToSTDate                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_convert                            | F_BA_ToSTDateTime                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_convert                            | F_BA_ToSTTime                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_convert                            | F_BA_ToTime                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_time                               | F_BA_CountLeapYears                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_time                               | F_BA_DateMerge                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_time                               | F_BA_DateTimeString                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_time                               | F_BA_DayOfWeek                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_time                               | F_BA_DaysInMonth                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_time                               | F_BA_GetDT                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_time                               | F_BA_GetDateTime                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_time                               | F_BA_TimeMerge                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_time                               | F_BA_TimeString                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_value                              | F_BA_DateRangeVal                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_value                              | F_BA_DateVal                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | date_value                              | F_BA_WeekNDayVal                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | gvls                                    | BAComn_EnumDE                            | verified | chapter-overview (large GVL)
2026-06-03T00:00:00Z | Tc3_BA2_Common | gvls                                    | BAComn_Global                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | gvls                                    | BAComn_Param                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | hysteresis_2p                           | FB_BA_Swi2P                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | hysteresis_2p                           | FB_BA_SwiHys2P                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | io_terminals                            | FB_BA_KL32xx                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | memory                                  | F_BA_ByteCmp                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | memory                                  | F_BA_Cmp                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | memory                                  | F_BA_DiffPtr                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | memory                                  | F_BA_GetUsedEntryCount                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | memory                                  | F_BA_MemSet                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | memory                                  | F_BA_MemSetEx                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | memory                                  | F_BA_OffsetPtr                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | persistent_data                         | FB_BA_PersistentDataHandler              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | ramps_filters                           | FB_BA_FltrPT1                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | ramps_filters                           | FB_BA_RampLmt                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | scheduler                               | F_BA_SetSchedulerEntry                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | tc_log                                  | F_BA_LogMessage                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | tc_log                                  | F_BA_LogMessage1                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | tc_log                                  | F_BA_LogMessage10                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | tc_log                                  | F_BA_LogMessage2                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | tc_log                                  | F_BA_LogMessage3                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | tc_log                                  | F_BA_LogMessage4                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | tc_log                                  | F_BA_LogMessage5                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | tc_log                                  | F_BA_LogMessage6                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | tc_log                                  | F_BA_LogMessage7                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | tc_log                                  | F_BA_LogMessage8                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | tc_log                                  | F_BA_LogMessage9                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | trend                                   | F_BA_IsDisturbed                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | trend                                   | F_BA_TrendBufferSize                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | trigger                                 | FB_BA_ATrigCOV                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | trigger                                 | FB_BA_RFTrig                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | validation                              | F_BA_IsDataClassValid                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | validation                              | F_BA_IsDataTypeValid                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | validation                              | F_BA_IsDateValChoiceValid                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | validation                              | F_BA_IsLoggingTypeValid                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | validation                              | F_BA_IsMeasuringElementValid             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | validation                              | F_BA_IsUnitValid                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_BA2_Common | validation                              | F_BA_IsWeekdayValid                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | AddArrayMember                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | AddBase64Member                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | AddBoolMember                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | AddDateTimeMember                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | AddDcTimeMember                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | AddDoubleMember                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | AddFileTimeMember                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | AddHexBinaryMember                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | AddInt64Member                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | AddIntMember                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | AddJsonMember                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | AddNullMember                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | AddObjectMember                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | AddStringMember                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | AddUint64Member                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | AddUintMember                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | ArrayBegin                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | ArrayEnd                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | ClearArray                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | CopyDocument                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | CopyFrom                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | CopyJson                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | CopyString                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | ExceptionRaised                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | FB_JsonDomParser                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | FindMember                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | FindMemberPath                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetArraySize                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetArrayValue                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetArrayValueByIdx                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetBase64                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetBool                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetDateTime                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetDcTime                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetDocument                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetDocumentLength                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetDocumentRoot                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetDouble                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetFileTime                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetHexBinary                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetInt                                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetInt64                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetJson                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetJsonLength                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetMaxDecimalPlaces                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetMemberName                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetMemberValue                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetString                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetStringLength                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetType                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetUint                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | GetUint64                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | HasMember                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | IsArray                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | IsBase64                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | IsBool                                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | IsDouble                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | IsFalse                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | IsHexBinary                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | IsISO8601TimeFormat                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | IsInt                                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | IsInt64                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | IsNull                                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | IsNumber                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | IsObject                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | IsString                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | IsTrue                                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | IsUint                                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | IsUint64                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | LoadDocumentFromFile                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | MemberBegin                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | MemberEnd                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | NewDocument                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | NextArray                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | NextMember                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | ParseDocument                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | PushbackBase64Value                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | PushbackBoolValue                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | PushbackCopyValue                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | PushbackDateTimeValue                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | PushbackDcTimeValue                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | PushbackDoubleValue                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | PushbackFileTimeValue                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | PushbackHexBinaryValue                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | PushbackInt64Value                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | PushbackIntValue                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | PushbackJsonValue                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | PushbackNullValue                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | PushbackStringValue                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | PushbackUint64Value                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | PushbackUintValue                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | RemoveAllMembers                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | RemoveArray                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | RemoveMember                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | RemoveMemberByName                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | SaveDocumentToFile                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | SetAdsProvider                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | SetArray                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | SetBase64                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | SetBool                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | SetDateTime                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | SetDcTime                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | SetDouble                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | SetFileTime                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | SetHexBinary                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | SetInt                                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | SetInt64                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | SetJson                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | SetMaxDecimalPlaces                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | SetNull                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | SetObject                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | SetString                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | SetUint                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | SetUint64                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondomparser                        | Swap                                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsondyndomparser                     | FB_JsonDynDomParser                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonreadwritedatatype                | AddJsonKeyPropertiesFromSymbol           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonreadwritedatatype                | AddJsonKeyValueFromSymbol                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonreadwritedatatype                | AddJsonValueFromSymbol                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonreadwritedatatype                | CopyJsonStringFromSymbol                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonreadwritedatatype                | CopyJsonStringFromSymbolProperties       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonreadwritedatatype                | CopySymbolNameByAddress                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonreadwritedatatype                | FB_JsonReadWriteDataType                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonreadwritedatatype                | GetDataTypeNameByAddress                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonreadwritedatatype                | GetJsonFromSymbol                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonreadwritedatatype                | GetJsonStringFromSymbol                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonreadwritedatatype                | GetJsonStringFromSymbolProperties        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonreadwritedatatype                | GetSizeJsonStringFromSymbol              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonreadwritedatatype                | GetSizeJsonStringFromSymbolProperties    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonreadwritedatatype                | GetSymbolNameByAddress                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonreadwritedatatype                | SetSymbolFromJson                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddBase64                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddBool                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddDateTime                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddDcTime                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddDint                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddFileTime                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddHexBinary                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddKey                                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddKeyBool                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddKeyDateTime                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddKeyDcTime                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddKeyFileTime                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddKeyLreal                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddKeyNull                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddKeyNumber                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddKeyString                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddLint                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddLreal                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddNull                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddRawArray                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddRawObject                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddReal                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddString                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddUdint                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | AddUlint                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | CopyDocument                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | EndArray                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | EndObject                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | FB_JsonSaxPrettyWriter                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | GetDocument                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | GetDocumentLength                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | GetMaxDecimalPlaces                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | ResetDocument                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | SetFormatOptions                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | SetIndent                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | SetMaxDecimalPlaces                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | StartArray                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxprettywriter                  | StartObject                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxreader                        | DecodeBase64                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxreader                        | DecodeDateTime                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxreader                        | DecodeDcTime                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxreader                        | DecodeFileTime                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxreader                        | DecodeHexBinary                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxreader                        | FB_JsonSaxReader                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxreader                        | IsBase64                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxreader                        | IsHexBinary                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxreader                        | IsISO8601TimeFormat                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxreader                        | Parse                                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxreader                        | ParseValues                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddBase64                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddBool                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddDateTime                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddDcTime                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddDint                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddFileTime                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddHexBinary                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddKey                                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddKeyBool                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddKeyDateTime                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddKeyDcTime                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddKeyFileTime                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddKeyLreal                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddKeyNull                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddKeyNumber                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddKeyString                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddLint                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddLreal                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddNull                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddRawArray                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddRawObject                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddReal                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddString                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddUdint                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | AddUlint                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | CopyDocument                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | EndArray                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | EndObject                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | FB_JsonSaxWriter                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | GetDocument                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | GetDocumentLength                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | GetMaxDecimalPlaces                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | ResetDocument                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | SetMaxDecimalPlaces                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | StartArray                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_jsonsaxwriter                        | StartObject                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AppendAttribute                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AppendAttributeAsBool                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AppendAttributeAsDouble                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AppendAttributeAsFloat                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AppendAttributeAsInt                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AppendAttributeAsLint                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AppendAttributeAsUint                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AppendAttributeAsUlint                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AppendAttributeCopy                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AppendChild                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AppendChildAsBool                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AppendChildAsDouble                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AppendChildAsFloat                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AppendChildAsInt                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AppendChildAsLint                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AppendChildAsUint                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AppendChildAsUlint                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AppendCopy                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AppendNode                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | Attribute                                | verified | infer-from-naming-convention (PDF same-name TOC ambiguity)
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AttributeAsBool                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AttributeAsDouble                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AttributeAsFloat                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AttributeAsInt                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AttributeAsLint                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AttributeAsUint                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AttributeAsUlint                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AttributeBegin                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AttributeFromIterator                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AttributeName                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | AttributeText                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | Attributes                               | verified | infer-from-naming-convention (PDF same-name TOC ambiguity)
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | Begin                                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | BeginByName                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | Child                                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | ChildByAttribute                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | ChildByAttributeAndName                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | ChildByName                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | Children                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | ChildrenByName                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | ClearIterator                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | Compare                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | CopyAttributeText                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | CopyDocument                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | CopyNodeText                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | CopyNodeXml                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | FB_XmlDomParser                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | FirstNodeByPath                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | GetAttributeTextLength                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | GetDocumentLength                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | GetDocumentNode                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | GetNodeTextLength                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | GetNodeXmlLength                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | GetRootNode                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | InsertAttribute                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | InsertAttributeCopy                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | InsertChild                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | InsertCopy                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | IsEnd                                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | LoadDocumentFromFile                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | NewDocument                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | Next                                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | NextAttribute                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | NextByName                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | NextSibling                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | NextSiblingByName                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | Node                                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | NodeAsBool                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | NodeAsDouble                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | NodeAsFloat                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | NodeAsInt                                | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | NodeAsLint                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | NodeAsUint                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | NodeAsUlint                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | NodeName                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | NodeText                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | ParseDocument                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | RemoveChild                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | RemoveChildByName                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | SaveDocumentToFile                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | SetAdsProvider                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | SetAttribute                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | SetAttributeAsBool                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | SetAttributeAsDouble                     | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | SetAttributeAsFloat                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | SetAttributeAsInt                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | SetAttributeAsLint                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | SetAttributeAsUint                       | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | SetAttributeAsUlint                      | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | SetChild                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | SetChildAsBool                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | SetChildAsDouble                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | SetChildAsFloat                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | SetChildAsInt                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | SetChildAsLint                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | SetChildAsUint                           | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | fb_xmldomparser                         | SetChildAsUlint                          | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | function_blocks                         | FB_JwtEncode                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxhandler                      | ITcJsonSaxHandler                        | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxhandler                      | OnBool                                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxhandler                      | OnDint                                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxhandler                      | OnEndArray                               | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxhandler                      | OnEndObject                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxhandler                      | OnKey                                    | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxhandler                      | OnLint                                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxhandler                      | OnLreal                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxhandler                      | OnNull                                   | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxhandler                      | OnStartArray                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxhandler                      | OnStartObject                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxhandler                      | OnString                                 | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxhandler                      | OnUdint                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxhandler                      | OnUlint                                  | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxvalues                       | ITcJsonSaxValues                         | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxvalues                       | OnBoolValue                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxvalues                       | OnDintValue                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxvalues                       | OnLintValue                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxvalues                       | OnLrealValue                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxvalues                       | OnNullValue                              | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxvalues                       | OnStringValue                            | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxvalues                       | OnUdintValue                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc3_JsonXml    | i_tcjsonsaxvalues                       | OnUlintValue                             | verified | PDF + InfoSys cross-verified
2026-06-03T00:00:00Z | Tc2_HVAC       | actuators                               | FB_HVAC2PointActuator                    | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | actuators                               | FB_HVAC3PointActuator                    | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | actuators                               | FB_HVACCirculationPump                   | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | actuators                               | FB_HVACCirculationPumpEx                 | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | actuators                               | FB_HVACMotor1Speed                       | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | actuators                               | FB_HVACMotor2Speed                       | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | actuators                               | FB_HVACMotor3Speed                       | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | actuators                               | FB_HVACMux8                              | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | actuators                               | FB_HVACMux8Ex                            | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | actuators                               | FB_HVACMux8_BOOL                         | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | actuators                               | FB_HVACRedundancyCtrl                    | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | actuators                               | FB_HVACRedundancyCtrlEx                  | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | analog_modules                          | FB_HVACAnalogInput                       | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | analog_modules                          | FB_HVACAnalogOutput                      | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | analog_modules                          | FB_HVACAnalogOutputEx                    | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | analog_modules                          | FB_HVACAnalogOutputEx2                   | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | analog_modules                          | FB_HVACAnalogTo3Point                    | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | analog_modules                          | FB_HVACConfigureKL32xx                   | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | analog_modules                          | FB_HVACScale                             | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | analog_modules                          | FB_HVACScaleXX                           | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | analog_modules                          | FB_HVACScale_nPoint                      | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | analog_modules                          | FB_HVACTemperatureCurve                  | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | analog_modules                          | FB_HVACTemperatureSensor                 | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | analog_modules                          | FB_HVACTemperatureSensorEx               | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | analog_modules                          | FB_HVACTemperatureSensorEx2              | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | backup_var                              | FB_HVACNOVRAM_XX                         | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | backup_var                              | FB_HVACPersistent_XX                     | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | controllers                             | FB_HVAC2PointCtrl                        | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | controllers                             | FB_HVACI_CtrlStep                        | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | controllers                             | FB_HVACI_CtrlStepEx                      | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | controllers                             | FB_HVACPIDCtrl                           | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | controllers                             | FB_HVACPIDCtrl_Ex                        | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | controllers                             | FB_HVACPowerRangeTable                   | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | functions                               | F_RoundLREAL                             | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | functions                               | F_RoundLREAL_EX                          | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | gvls                                    | HVAC_Constants                           | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | gvls                                    | HVAC_Parameter                           | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_air_conditioning                   | FB_BAREnergyLevel                        | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | room_air_conditioning                   | FB_BARFanCoil                            | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | room_air_conditioning                   | FB_BARFctSelection                       | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | room_air_conditioning                   | FB_BARSetpointRoom                       | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | room_controller                         | FB_BARPICtrl                             | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | room_lighting                           | FB_BARAutomaticLight                     | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | room_lighting                           | FB_BARConstantLightControl               | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | room_lighting                           | FB_BARDaylightControl                    | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | room_lighting                           | FB_BARLightActuator                      | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | room_lighting                           | FB_BARLightCircuit                       | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_lighting                           | FB_BARLightCircuitDim                    | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | room_lighting                           | FB_BARStairwellAutomatic                 | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_lighting                           | FB_BARTwilightAutomatic                  | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARBlindPositionEntry                 | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARDelayedHysteresis                  | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARFacadeElementEntry                 | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARReadFacadeElementList              | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARReadShadingObjectsList             | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARRollerBlind                        | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARShadingCorrection                  | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARShadingCorrectionSouth             | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARShadingObjectsEntry                | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARSunProtectionEx                    | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARSunblindActuator                   | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARSunblindActuatorEx                 | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARSunblindEvent                      | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARSunblindPrioritySwitch             | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARSunblindScene                      | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARSunblindSwitch                     | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARSunblindThermoAutomatic            | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARSunblindTwilightAutomatic          | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARSunblindWeatherProtection          | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARWithinRangeAzimuth                 | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | room_sun_protection                     | FB_BARWithinRangeElevation               | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | scheduler                               | FB_HVACScheduler1ch                      | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | scheduler                               | FB_HVACScheduler28TCHandling             | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | scheduler                               | FB_HVACScheduler28ch                     | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | scheduler                               | FB_HVACScheduler7TCHandling              | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | scheduler                               | FB_HVACScheduler7ch                      | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | scheduler                               | FB_HVACSchedulerPublicHolidays           | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | scheduler                               | FB_HVACSchedulerSpecialPeriods           | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | sequence_controllers                    | FB_HVAC2PointCtrlSequence                | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | sequence_controllers                    | FB_HVACBasicSequenceCtrl                 | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | sequence_controllers                    | FB_HVACMasterSequenceCtrl                | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | sequence_controllers                    | FB_HVACPIDCooling                        | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | sequence_controllers                    | FB_HVACPIDDehumidify                     | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | sequence_controllers                    | FB_HVACPIDEnergyRecovery                 | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | sequence_controllers                    | FB_HVACPIDHumidify                       | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | sequence_controllers                    | FB_HVACPIDMixedAir                       | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | sequence_controllers                    | FB_HVACPIDPreHeating                     | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | sequence_controllers                    | FB_HVACPIDReHeating                      | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | setpoint_modules                        | FB_HVACHeatingCurve                      | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | setpoint_modules                        | FB_HVACHeatingCurveEx                    | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | setpoint_modules                        | FB_HVACOutsideTempDamped                 | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | setpoint_modules                        | FB_HVACSetpointHeating                   | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | setpoint_modules                        | FB_HVACSetpointRamp                      | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | setpoint_modules                        | FB_HVACSummerCompensation                | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACAirConditioning2Speed             | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACAlarm                             | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACAntiBlockingDamper                | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACAntiBlockingPump                  | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACBlink                             | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACCmdCtrlSystem1Stage               | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACCmdCtrlSystem2Stage               | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACCmdCtrl_8                         | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACConvertEnum                       | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACEnthalpy                          | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACFixedLimit                        | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACFreezeProtectionHeater            | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACMUX_INT_16                        | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACMUX_INT_8                         | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACMUX_REAL_16                       | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACMUX_REAL_8                        | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACOptimizedOff                      | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACOptimizedOn                       | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACOverwriteAnalog                   | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACOverwriteDigital                  | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACPWM                               | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACPowerMeasurementKL3403            | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACPowerMeasurementKL3403Ex          | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACPriority_INT_16                   | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACPriority_INT_8                    | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACPriority_REAL_16                  | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACPriority_REAL_8                   | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACStartAirConditioning              | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACSummerNightCooling                | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACSummerNightCoolingEx              | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACTempChangeFunction                | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACTimeCon                           | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACTimeConSec                        | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACTimeConSecMs                      | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | special_functions                       | FB_HVACWork                              | verified | chapter-overview (PDF lacks END_VAR terminator)
2026-06-03T00:00:00Z | Tc2_HVAC       | system                                  | FB_HVACGetSystemTime                     | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | system                                  | FB_HVACNOVRAMDataHandling                | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | system                                  | FB_HVACPersistentDataFileCopy            | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | system                                  | FB_HVACPersistentDataHandling            | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | system                                  | FB_HVACSetLocalTime                      | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_HVAC       | system                                  | FB_HVACSystemTaskInfo                    | verified | chapter-overview + PDF single-source
2026-06-03T00:00:00Z | Tc2_DALI       | kl6811_base                             | FB_KL6811Communication                   | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | kl6821_base                             | FB_KL6821Communication                   | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | kl6821_base                             | FB_KL6821Config                          | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_addressing                      | FB_DALIV2AddressingRandomAddressing      | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_config                      | FB_DALIV2AddToGroup                      | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_config                      | FB_DALIV2RemoveFromGroup                 | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_config                      | FB_DALIV2RemoveFromScene                 | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_config                      | FB_DALIV2Reset                           | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_config                      | FB_DALIV2SetFadeRate                     | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_config                      | FB_DALIV2SetFadeTime                     | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_config                      | FB_DALIV2SetMaxLevel                     | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_config                      | FB_DALIV2SetMinLevel                     | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_config                      | FB_DALIV2SetPowerOnLevel                 | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_config                      | FB_DALIV2SetScene                        | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_config                      | FB_DALIV2SetShortAddress                 | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_config                      | FB_DALIV2SetSystemFailureLevel           | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_config                      | FB_DALIV2StoreActualLevelInDTR0          | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_power                       | FB_DALIV2DirectArcPowerControl           | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_power                       | FB_DALIV2Down                            | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_power                       | FB_DALIV2EnableDAPCSequence              | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_power                       | FB_DALIV2GoToScene                       | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_power                       | FB_DALIV2Off                             | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_power                       | FB_DALIV2OnAndStepUp                     | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_power                       | FB_DALIV2RecallMaxLevel                  | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_power                       | FB_DALIV2RecallMinLevel                  | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_power                       | FB_DALIV2StepDown                        | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_power                       | FB_DALIV2StepDownAndOff                  | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_power                       | FB_DALIV2StepUp                          | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_power                       | FB_DALIV2Up                              | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryActualLevel                | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryContentDTR0                | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryContentDTR1                | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryContentDTR2                | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryControlGearPresent         | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryDeviceType                 | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryFadeTimeFadeRate           | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryGroups                     | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryGroups0UpTo7               | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryGroups8UpTo15              | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryLampFailure                | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryLampPowerOn                | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryLimitError                 | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryMaxLevel                   | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryMinLevel                   | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryMissingShortAddress        | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryPhysicalMinLevel           | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryPowerFailure               | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryPowerOnLevel               | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryRandomAddress              | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryRandomAddressH             | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryRandomAddressL             | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryRandomAddressM             | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryResetState                 | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QuerySceneLevel                 | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryStatus                     | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QuerySystemFailureLevel         | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_queries                     | FB_DALIV2QueryVersionNumber              | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_special                     | FB_DALIV2Initialise                      | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_special                     | FB_DALIV2ProgramShortAddress             | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_special                     | FB_DALIV2Randomise                       | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_special                     | FB_DALIV2SetDTR0                         | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_special                     | FB_DALIV2SetDTR1                         | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_special                     | FB_DALIV2SetDTR2                         | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_low_special                     | FB_DALIV2Terminate                       | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_power_control                   | FB_DALIV2Dimmer1Switch                   | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_power_control                   | FB_DALIV2Dimmer2Switch                   | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_power_control                   | FB_DALIV2Light                           | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_power_control                   | FB_DALIV2Sequencer                       | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_power_control                   | FB_DALIV2StairwellDimmer                 | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part102_settings                        | FB_DALIV2GetSettings                     | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
2026-06-03T00:00:00Z | Tc2_DALI       | part202_emergency_high                  | FB_DALIV2EmergencyLightingDT             | verified | PDF + InfoSys library-root (per-FB topic not on InfoSys)
