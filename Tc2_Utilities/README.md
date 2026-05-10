# Tc2_Utilities

> 通用工具库（数学/字符串/字节序/系统/许可/CSV...）。版本 `2.18.2`，**总条目 343** （97 FB + 245 FC + 1 GVL）。

- [官方 InfoSys](https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/)
- [官方 PDF](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf)
- [Roadmap](../_meta/roadmap-Tc2_Utilities.md)

## 当前进度

> 因库规模庞大（343 条），按 category 分多批 doc-shard。

| Round | Categories | 条目 | 状态 |
|---|---|---|---|
| 1 | LCOMPLEX / FLOAT / [Obsolete] / 16-bit fixed-point / Byte order / Library version | 28 | ✅ done |
| 2 | Time functions | 23 | ✅ done |
| 3 | TC_CoreBoostMonitor (parent FB + 5 methods) + [obsolete] FB (4) | 10 | ✅ done |
| 4 | T_Arg help functions | 27 | ✅ done |
| 5 | P[TYPE]_TO_[TYPE] converting functions | 26 | ✅ done |
| - | Extended STRING | 30 | ⏳ pending |
| - | 64-bit functions (signed) | 15 | ⏳ pending |
| - | 64-bit integer (unsigned) | 31 | ⏳ pending |
| - | Functions（散） | 66 | ⏳ pending |
| - | Function blocks (剩余) | ~83 | ⏳ pending |
| - | **当前累计** | **114 / 344** | 33.1% |

## Round 1 索引（28 条 · 全部 ✅ verified）

### LCOMPLEX functions（2）

| Name | 文档 | 例程 |
|---|---|---|
| LcomplexIsNaN | [✅](lcomplex/LcomplexIsNaN.md) | [P_Demo_LcomplexIsNaN.xml](examples/P_Demo_LcomplexIsNaN.xml) |
| LcomplexAbs | [✅](lcomplex/LcomplexAbs.md) | [P_Demo_LcomplexAbs.xml](examples/P_Demo_LcomplexAbs.xml) |

### FLOAT functions（4）

| Name | 文档 | 例程 |
|---|---|---|
| LrealIsFinite | [✅](float/LrealIsFinite.md) | [P_Demo_LrealIsFinite.xml](examples/P_Demo_LrealIsFinite.xml) |
| LrealIsNaN | [✅](float/LrealIsNaN.md) | [P_Demo_LrealIsNaN.xml](examples/P_Demo_LrealIsNaN.xml) |
| RealIsFinite | [✅](float/RealIsFinite.md) | [P_Demo_RealIsFinite.xml](examples/P_Demo_RealIsFinite.xml) |
| RealIsNaN | [✅](float/RealIsNaN.md) | [P_Demo_RealIsNaN.xml](examples/P_Demo_RealIsNaN.xml) |

### [Obsolete]（2）

| Name | 文档 | 例程 |
|---|---|---|
| FLOATIsFinite | [✅ deprecated](obsolete/FLOATIsFinite.md) | [P_Demo_FLOATIsFinite.xml](examples/P_Demo_FLOATIsFinite.xml) |
| FLOATIsNaN | [✅ deprecated](obsolete/FLOATIsNaN.md) | [P_Demo_FLOATIsNaN.xml](examples/P_Demo_FLOATIsNaN.xml) |

### 16 bit fixed-point number functions (signed)（9）

| Name | 文档 | 例程 |
|---|---|---|
| FIX16_TO_LREAL | [✅](fix16/FIX16_TO_LREAL.md) | [P_Demo_FIX16_TO_LREAL.xml](examples/P_Demo_FIX16_TO_LREAL.xml) |
| FIX16_TO_WORD | [✅](fix16/FIX16_TO_WORD.md) | [P_Demo_FIX16_TO_WORD.xml](examples/P_Demo_FIX16_TO_WORD.xml) |
| FIX16Add | [✅](fix16/FIX16Add.md) | [P_Demo_FIX16Add.xml](examples/P_Demo_FIX16Add.xml) |
| FIX16Align | [✅](fix16/FIX16Align.md) | [P_Demo_FIX16Align.xml](examples/P_Demo_FIX16Align.xml) |
| FIX16Div | [✅](fix16/FIX16Div.md) | [P_Demo_FIX16Div.xml](examples/P_Demo_FIX16Div.xml) |
| FIX16Mul | [✅](fix16/FIX16Mul.md) | [P_Demo_FIX16Mul.xml](examples/P_Demo_FIX16Mul.xml) |
| FIX16Sub | [✅](fix16/FIX16Sub.md) | [P_Demo_FIX16Sub.xml](examples/P_Demo_FIX16Sub.xml) |
| LREAL_TO_FIX16 | [✅](fix16/LREAL_TO_FIX16.md) | [P_Demo_LREAL_TO_FIX16.xml](examples/P_Demo_LREAL_TO_FIX16.xml) |
| WORD_TO_FIX16 | [✅](fix16/WORD_TO_FIX16.md) | [P_Demo_WORD_TO_FIX16.xml](examples/P_Demo_WORD_TO_FIX16.xml) |

### Byte order converting functions（10）

| Name | 文档 | 例程 |
|---|---|---|
| HOST_TO_BE16 | [✅](byte_order/HOST_TO_BE16.md) | [P_Demo_HOST_TO_BE16.xml](examples/P_Demo_HOST_TO_BE16.xml) |
| HOST_TO_BE32 | [✅](byte_order/HOST_TO_BE32.md) | [P_Demo_HOST_TO_BE32.xml](examples/P_Demo_HOST_TO_BE32.xml) |
| HOST_TO_BE64 | [✅](byte_order/HOST_TO_BE64.md) | [P_Demo_HOST_TO_BE64.xml](examples/P_Demo_HOST_TO_BE64.xml) |
| HOST_TO_BE64EX | [✅](byte_order/HOST_TO_BE64EX.md) | [P_Demo_HOST_TO_BE64EX.xml](examples/P_Demo_HOST_TO_BE64EX.xml) |
| HOST_TO_BE128 | [✅](byte_order/HOST_TO_BE128.md) | [P_Demo_HOST_TO_BE128.xml](examples/P_Demo_HOST_TO_BE128.xml) |
| BE16_TO_HOST | [✅](byte_order/BE16_TO_HOST.md) | [P_Demo_BE16_TO_HOST.xml](examples/P_Demo_BE16_TO_HOST.xml) |
| BE32_TO_HOST | [✅](byte_order/BE32_TO_HOST.md) | [P_Demo_BE32_TO_HOST.xml](examples/P_Demo_BE32_TO_HOST.xml) |
| BE64_TO_HOST | [✅](byte_order/BE64_TO_HOST.md) | [P_Demo_BE64_TO_HOST.xml](examples/P_Demo_BE64_TO_HOST.xml) |
| BE64_TO_HOSTEX | [✅](byte_order/BE64_TO_HOSTEX.md) | [P_Demo_BE64_TO_HOSTEX.xml](examples/P_Demo_BE64_TO_HOSTEX.xml) |
| BE128_TO_HOST | [✅](byte_order/BE128_TO_HOST.md) | [P_Demo_BE128_TO_HOST.xml](examples/P_Demo_BE128_TO_HOST.xml) |

### Time functions（23）

| Name | 文档 | 例程 |
|---|---|---|
| DT_TO_FILETIME64 | [✅](time_functions/DT_TO_FILETIME64.md) | [P_Demo_DT_TO_FILETIME64.xml](examples/P_Demo_DT_TO_FILETIME64.xml) |
| DT_TO_SYSTEMTIME | [✅](time_functions/DT_TO_SYSTEMTIME.md) | [P_Demo_DT_TO_SYSTEMTIME.xml](examples/P_Demo_DT_TO_SYSTEMTIME.xml) |
| F_EuropeanLocalTime | [✅](time_functions/F_EuropeanLocalTime.md) | [P_Demo_F_EuropeanLocalTime.xml](examples/P_Demo_F_EuropeanLocalTime.xml) |
| F_GetDayOfMonthEx | [✅](time_functions/F_GetDayOfMonthEx.md) | [P_Demo_F_GetDayOfMonthEx.xml](examples/P_Demo_F_GetDayOfMonthEx.xml) |
| F_GetDayOfWeek | [✅](time_functions/F_GetDayOfWeek.md) | [P_Demo_F_GetDayOfWeek.xml](examples/P_Demo_F_GetDayOfWeek.xml) |
| F_GetDOYOfYearMonthDay | [✅](time_functions/F_GetDOYOfYearMonthDay.md) | [P_Demo_F_GetDOYOfYearMonthDay.xml](examples/P_Demo_F_GetDOYOfYearMonthDay.xml) |
| F_GetMaxMonthDays | [✅](time_functions/F_GetMaxMonthDays.md) | [P_Demo_F_GetMaxMonthDays.xml](examples/P_Demo_F_GetMaxMonthDays.xml) |
| F_GetMonthOfDOY | [✅](time_functions/F_GetMonthOfDOY.md) | [P_Demo_F_GetMonthOfDOY.xml](examples/P_Demo_F_GetMonthOfDOY.xml) |
| F_GetWeekOfTheYear | [✅](time_functions/F_GetWeekOfTheYear.md) | [P_Demo_F_GetWeekOfTheYear.xml](examples/P_Demo_F_GetWeekOfTheYear.xml) |
| F_TranslateFileTime64Bias | [✅](time_functions/F_TranslateFileTime64Bias.md) | [P_Demo_F_TranslateFileTime64Bias.xml](examples/P_Demo_F_TranslateFileTime64Bias.xml) |
| F_YearIsLeapYear | [✅](time_functions/F_YearIsLeapYear.md) | [P_Demo_F_YearIsLeapYear.xml](examples/P_Demo_F_YearIsLeapYear.xml) |
| FILETIME64_TO_DT | [✅](time_functions/FILETIME64_TO_DT.md) | [P_Demo_FILETIME64_TO_DT.xml](examples/P_Demo_FILETIME64_TO_DT.xml) |
| FILETIME64_TO_ISO8601 | [✅](time_functions/FILETIME64_TO_ISO8601.md) | [P_Demo_FILETIME64_TO_ISO8601.xml](examples/P_Demo_FILETIME64_TO_ISO8601.xml) |
| FILETIME64_TO_SYSTEMTIME | [✅](time_functions/FILETIME64_TO_SYSTEMTIME.md) | [P_Demo_FILETIME64_TO_SYSTEMTIME.xml](examples/P_Demo_FILETIME64_TO_SYSTEMTIME.xml) |
| FILETIME64_TO_TOD | [✅](time_functions/FILETIME64_TO_TOD.md) | [P_Demo_FILETIME64_TO_TOD.xml](examples/P_Demo_FILETIME64_TO_TOD.xml) |
| OTSTRUCT_TO_TIME | [✅](time_functions/OTSTRUCT_TO_TIME.md) | [P_Demo_OTSTRUCT_TO_TIME.xml](examples/P_Demo_OTSTRUCT_TO_TIME.xml) |
| STRING_TO_SYSTEMTIME | [✅](time_functions/STRING_TO_SYSTEMTIME.md) | [P_Demo_STRING_TO_SYSTEMTIME.xml](examples/P_Demo_STRING_TO_SYSTEMTIME.xml) |
| SYSTEMTIME_TO_DT | [✅](time_functions/SYSTEMTIME_TO_DT.md) | [P_Demo_SYSTEMTIME_TO_DT.xml](examples/P_Demo_SYSTEMTIME_TO_DT.xml) |
| SYSTEMTIME_TO_FILETIME64 | [✅](time_functions/SYSTEMTIME_TO_FILETIME64.md) | [P_Demo_SYSTEMTIME_TO_FILETIME64.xml](examples/P_Demo_SYSTEMTIME_TO_FILETIME64.xml) |
| SYSTEMTIME_TO_ISO8601 | [✅](time_functions/SYSTEMTIME_TO_ISO8601.md) | [P_Demo_SYSTEMTIME_TO_ISO8601.xml](examples/P_Demo_SYSTEMTIME_TO_ISO8601.xml) |
| SYSTEMTIME_TO_STRING | [✅](time_functions/SYSTEMTIME_TO_STRING.md) | [P_Demo_SYSTEMTIME_TO_STRING.xml](examples/P_Demo_SYSTEMTIME_TO_STRING.xml) |
| SYSTEMTIME_TO_TOD | [✅](time_functions/SYSTEMTIME_TO_TOD.md) | [P_Demo_SYSTEMTIME_TO_TOD.xml](examples/P_Demo_SYSTEMTIME_TO_TOD.xml) |
| TIME_TO_OTSTRUCT | [✅](time_functions/TIME_TO_OTSTRUCT.md) | [P_Demo_TIME_TO_OTSTRUCT.xml](examples/P_Demo_TIME_TO_OTSTRUCT.xml) |

### TC_CoreBoostMonitor（父 FB + 5 methods）

| Name | 文档 | 例程 |
|---|---|---|
| **TC_CoreBoostMonitor** (父 FB) | [✅](tc_coreboostmonitor/TC_CoreBoostMonitor.md) | [P_Demo_TC_CoreBoostMonitor.xml](examples/P_Demo_TC_CoreBoostMonitor.xml) |
| GetAllRtCoreThrottling | [✅](tc_coreboostmonitor/GetAllRtCoreThrottling.md) | [P_Demo_GetAllRtCoreThrottling.xml](examples/P_Demo_GetAllRtCoreThrottling.xml) |
| GetCoreFrequency | [✅](tc_coreboostmonitor/GetCoreFrequency.md) | [P_Demo_GetCoreFrequency.xml](examples/P_Demo_GetCoreFrequency.xml) |
| GetCoreTemperature | [✅](tc_coreboostmonitor/GetCoreTemperature.md) | [P_Demo_GetCoreTemperature.xml](examples/P_Demo_GetCoreTemperature.xml) |
| GetCoreThrottling | [✅](tc_coreboostmonitor/GetCoreThrottling.md) | [P_Demo_GetCoreThrottling.xml](examples/P_Demo_GetCoreThrottling.xml) |
| GetPowerConsumption | [✅](tc_coreboostmonitor/GetPowerConsumption.md) | [P_Demo_GetPowerConsumption.xml](examples/P_Demo_GetPowerConsumption.xml) |

### [obsolete] Function blocks（4，已废弃）

| Name | 文档 | 例程 |
|---|---|---|
| FB_AdsReadEvents | [⚠️ deprecated](obsolete_fb/FB_AdsReadEvents.md) | [P_Demo_FB_AdsReadEvents.xml](examples/P_Demo_FB_AdsReadEvents.xml) |
| FB_GetDeviceIdentification | [⚠️ deprecated](obsolete_fb/FB_GetDeviceIdentification.md) | [P_Demo_FB_GetDeviceIdentification.xml](examples/P_Demo_FB_GetDeviceIdentification.xml) |
| FB_FileTimeToTzSpecificLocalTime | [⚠️ deprecated](obsolete_fb/FB_FileTimeToTzSpecificLocalTime.md) | [P_Demo_FB_FileTimeToTzSpecificLocalTime.xml](examples/P_Demo_FB_FileTimeToTzSpecificLocalTime.xml) |
| FB_TzSpecificLocalTimeToFileTime | [⚠️ deprecated](obsolete_fb/FB_TzSpecificLocalTimeToFileTime.md) | [P_Demo_FB_TzSpecificLocalTimeToFileTime.xml](examples/P_Demo_FB_TzSpecificLocalTimeToFileTime.xml) |

### T_Arg help functions（27）

| Name | 文档 | 例程 |
|---|---|---|
| F_ARGCMP | [✅](t_arg/F_ARGCMP.md) | [P_Demo_F_ARGCMP.xml](examples/P_Demo_F_ARGCMP.xml) |
| F_ARGCPY | [✅](t_arg/F_ARGCPY.md) | [P_Demo_F_ARGCPY.xml](examples/P_Demo_F_ARGCPY.xml) |
| F_ARGISZERO | [✅](t_arg/F_ARGISZERO.md) | [P_Demo_F_ARGISZERO.xml](examples/P_Demo_F_ARGISZERO.xml) |
| F_BIGTYPE | [✅](t_arg/F_BIGTYPE.md) | [P_Demo_F_BIGTYPE.xml](examples/P_Demo_F_BIGTYPE.xml) |
| F_BOOL | [✅](t_arg/F_BOOL.md) | [P_Demo_F_BOOL.xml](examples/P_Demo_F_BOOL.xml) |
| F_BYTE | [✅](t_arg/F_BYTE.md) | [P_Demo_F_BYTE.xml](examples/P_Demo_F_BYTE.xml) |
| F_DINT | [✅](t_arg/F_DINT.md) | [P_Demo_F_DINT.xml](examples/P_Demo_F_DINT.xml) |
| F_DWORD | [✅](t_arg/F_DWORD.md) | [P_Demo_F_DWORD.xml](examples/P_Demo_F_DWORD.xml) |
| F_HUGE | [✅](t_arg/F_HUGE.md) | [P_Demo_F_HUGE.xml](examples/P_Demo_F_HUGE.xml) |
| F_INT | [✅](t_arg/F_INT.md) | [P_Demo_F_INT.xml](examples/P_Demo_F_INT.xml) |
| F_LARGE | [✅](t_arg/F_LARGE.md) | [P_Demo_F_LARGE.xml](examples/P_Demo_F_LARGE.xml) |
| F_LINT | [✅](t_arg/F_LINT.md) | [P_Demo_F_LINT.xml](examples/P_Demo_F_LINT.xml) |
| F_LREAL | [✅](t_arg/F_LREAL.md) | [P_Demo_F_LREAL.xml](examples/P_Demo_F_LREAL.xml) |
| F_LWORD | [✅](t_arg/F_LWORD.md) | [P_Demo_F_LWORD.xml](examples/P_Demo_F_LWORD.xml) |
| F_REAL | [✅](t_arg/F_REAL.md) | [P_Demo_F_REAL.xml](examples/P_Demo_F_REAL.xml) |
| F_SINT | [✅](t_arg/F_SINT.md) | [P_Demo_F_SINT.xml](examples/P_Demo_F_SINT.xml) |
| F_STRING | [✅](t_arg/F_STRING.md) | [P_Demo_F_STRING.xml](examples/P_Demo_F_STRING.xml) |
| F_STRINGEx | [✅](t_arg/F_STRINGEx.md) | [P_Demo_F_STRINGEx.xml](examples/P_Demo_F_STRINGEx.xml) |
| F_UDINT | [✅](t_arg/F_UDINT.md) | [P_Demo_F_UDINT.xml](examples/P_Demo_F_UDINT.xml) |
| F_UHUGE | [✅](t_arg/F_UHUGE.md) | [P_Demo_F_UHUGE.xml](examples/P_Demo_F_UHUGE.xml) |
| F_UINT | [✅](t_arg/F_UINT.md) | [P_Demo_F_UINT.xml](examples/P_Demo_F_UINT.xml) |
| F_ULARGE | [✅](t_arg/F_ULARGE.md) | [P_Demo_F_ULARGE.xml](examples/P_Demo_F_ULARGE.xml) |
| F_ULINT | [✅](t_arg/F_ULINT.md) | [P_Demo_F_ULINT.xml](examples/P_Demo_F_ULINT.xml) |
| F_USINT | [✅](t_arg/F_USINT.md) | [P_Demo_F_USINT.xml](examples/P_Demo_F_USINT.xml) |
| F_WORD | [✅](t_arg/F_WORD.md) | [P_Demo_F_WORD.xml](examples/P_Demo_F_WORD.xml) |
| F_PVOID | [✅](t_arg/F_PVOID.md) | [P_Demo_F_PVOID.xml](examples/P_Demo_F_PVOID.xml) |
| IsFinite | [✅](t_arg/IsFinite.md) | [P_Demo_IsFinite.xml](examples/P_Demo_IsFinite.xml) |

### P[TYPE]_TO_[TYPE] converting functions（26）

> 全部为指针解引用函数，模式统一：`POINTER TO X` → `X`

| Name | 文档 | 例程 |
|---|---|---|
| PBOOL_TO_BOOL | [✅](p_to_value/PBOOL_TO_BOOL.md) | [P_Demo_PBOOL_TO_BOOL.xml](examples/P_Demo_PBOOL_TO_BOOL.xml) |
| PBYTE_TO_BYTE | [✅](p_to_value/PBYTE_TO_BYTE.md) | [P_Demo_PBYTE_TO_BYTE.xml](examples/P_Demo_PBYTE_TO_BYTE.xml) |
| PDATE_TO_DATE | [✅](p_to_value/PDATE_TO_DATE.md) | [P_Demo_PDATE_TO_DATE.xml](examples/P_Demo_PDATE_TO_DATE.xml) |
| PDINT_TO_DINT | [✅](p_to_value/PDINT_TO_DINT.md) | [P_Demo_PDINT_TO_DINT.xml](examples/P_Demo_PDINT_TO_DINT.xml) |
| PDT_TO_DT | [✅](p_to_value/PDT_TO_DT.md) | [P_Demo_PDT_TO_DT.xml](examples/P_Demo_PDT_TO_DT.xml) |
| PDWORD_TO_DWORD | [✅](p_to_value/PDWORD_TO_DWORD.md) | [P_Demo_PDWORD_TO_DWORD.xml](examples/P_Demo_PDWORD_TO_DWORD.xml) |
| PHUGE_TO_HUGE | [✅](p_to_value/PHUGE_TO_HUGE.md) | [P_Demo_PHUGE_TO_HUGE.xml](examples/P_Demo_PHUGE_TO_HUGE.xml) |
| PINT_TO_INT | [✅](p_to_value/PINT_TO_INT.md) | [P_Demo_PINT_TO_INT.xml](examples/P_Demo_PINT_TO_INT.xml) |
| PLARGE_TO_LARGE | [✅](p_to_value/PLARGE_TO_LARGE.md) | [P_Demo_PLARGE_TO_LARGE.xml](examples/P_Demo_PLARGE_TO_LARGE.xml) |
| PLINT_TO_LINT | [✅](p_to_value/PLINT_TO_LINT.md) | [P_Demo_PLINT_TO_LINT.xml](examples/P_Demo_PLINT_TO_LINT.xml) |
| PLREAL_TO_LREAL | [✅](p_to_value/PLREAL_TO_LREAL.md) | [P_Demo_PLREAL_TO_LREAL.xml](examples/P_Demo_PLREAL_TO_LREAL.xml) |
| PLWORD_TO_LWORD | [✅](p_to_value/PLWORD_TO_LWORD.md) | [P_Demo_PLWORD_TO_LWORD.xml](examples/P_Demo_PLWORD_TO_LWORD.xml) |
| PMAXSTRING_TO_MAXSTRING | [✅](p_to_value/PMAXSTRING_TO_MAXSTRING.md) | [P_Demo_PMAXSTRING_TO_MAXSTRING.xml](examples/P_Demo_PMAXSTRING_TO_MAXSTRING.xml) |
| PREAL_TO_REAL | [✅](p_to_value/PREAL_TO_REAL.md) | [P_Demo_PREAL_TO_REAL.xml](examples/P_Demo_PREAL_TO_REAL.xml) |
| PSINT_TO_SINT | [✅](p_to_value/PSINT_TO_SINT.md) | [P_Demo_PSINT_TO_SINT.xml](examples/P_Demo_PSINT_TO_SINT.xml) |
| PSTRING_TO_STRING | [✅](p_to_value/PSTRING_TO_STRING.md) | [P_Demo_PSTRING_TO_STRING.xml](examples/P_Demo_PSTRING_TO_STRING.xml) |
| PTIME_TO_TIME | [✅](p_to_value/PTIME_TO_TIME.md) | [P_Demo_PTIME_TO_TIME.xml](examples/P_Demo_PTIME_TO_TIME.xml) |
| PTOD_TO_TOD | [✅](p_to_value/PTOD_TO_TOD.md) | [P_Demo_PTOD_TO_TOD.xml](examples/P_Demo_PTOD_TO_TOD.xml) |
| PUDINT_TO_UDINT | [✅](p_to_value/PUDINT_TO_UDINT.md) | [P_Demo_PUDINT_TO_UDINT.xml](examples/P_Demo_PUDINT_TO_UDINT.xml) |
| PUHUGE_TO_UHUGE | [✅](p_to_value/PUHUGE_TO_UHUGE.md) | [P_Demo_PUHUGE_TO_UHUGE.xml](examples/P_Demo_PUHUGE_TO_UHUGE.xml) |
| PUINT_TO_UINT | [✅](p_to_value/PUINT_TO_UINT.md) | [P_Demo_PUINT_TO_UINT.xml](examples/P_Demo_PUINT_TO_UINT.xml) |
| PULARGE_TO_ULARGE | [✅](p_to_value/PULARGE_TO_ULARGE.md) | [P_Demo_PULARGE_TO_ULARGE.xml](examples/P_Demo_PULARGE_TO_ULARGE.xml) |
| PULINT_TO_ULINT | [✅](p_to_value/PULINT_TO_ULINT.md) | [P_Demo_PULINT_TO_ULINT.xml](examples/P_Demo_PULINT_TO_ULINT.xml) |
| PUSINT_TO_USINT | [✅](p_to_value/PUSINT_TO_USINT.md) | [P_Demo_PUSINT_TO_USINT.xml](examples/P_Demo_PUSINT_TO_USINT.xml) |
| PWORD_TO_WORD | [✅](p_to_value/PWORD_TO_WORD.md) | [P_Demo_PWORD_TO_WORD.xml](examples/P_Demo_PWORD_TO_WORD.xml) |
| PUINT64_TO_UINT64 | [✅](p_to_value/PUINT64_TO_UINT64.md) | [P_Demo_PUINT64_TO_UINT64.xml](examples/P_Demo_PUINT64_TO_UINT64.xml) |

### Library version（1）

| Name | 文档 | 例程 |
|---|---|---|
| stLibVersion_Tc2_Utilities | [✅](global_constants/stLibVersion_Tc2_Utilities.md) | [P_Demo_stLibVersion_Tc2_Utilities.xml](examples/P_Demo_stLibVersion_Tc2_Utilities.xml) |
