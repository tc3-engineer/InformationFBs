# Tc2_Utilities

> 通用工具库（数学/字符串/字节序/系统/许可/CSV...）。版本 `2.18.2`，**总条目 344**（97 FB + 1 OO parent FB + 245 FC + 1 GVL）·**全部完成 ✅**。

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
| 6 | Extended STRING functions | 30 | ✅ done |
| 7 | 64-bit functions (signed) | 15 | ✅ done |
| 8 | 64-bit integer functions (unsigned) | 31 | ✅ done |
| 9 | Functions（散） | 66 | ✅ done |
| 10 | Function blocks | 88 | ✅ done |
| - | **当前累计** | **344 / 344** | **100%** |

## Round 1 索引（28 条 · 全部 ✅ verified）

### LCOMPLEX functions（2）

| Name | 文档 | 例程 |
|---|---|---|
| LcomplexIsNaN | [✅](lcomplex/LcomplexIsNaN.md) | [P_Demo_LcomplexIsNaN.TcPOU](examples/P_Demo_LcomplexIsNaN.TcPOU) |
| LcomplexAbs | [✅](lcomplex/LcomplexAbs.md) | [P_Demo_LcomplexAbs.TcPOU](examples/P_Demo_LcomplexAbs.TcPOU) |

### FLOAT functions（4）

| Name | 文档 | 例程 |
|---|---|---|
| LrealIsFinite | [✅](float/LrealIsFinite.md) | [P_Demo_LrealIsFinite.TcPOU](examples/P_Demo_LrealIsFinite.TcPOU) |
| LrealIsNaN | [✅](float/LrealIsNaN.md) | [P_Demo_LrealIsNaN.TcPOU](examples/P_Demo_LrealIsNaN.TcPOU) |
| RealIsFinite | [✅](float/RealIsFinite.md) | [P_Demo_RealIsFinite.TcPOU](examples/P_Demo_RealIsFinite.TcPOU) |
| RealIsNaN | [✅](float/RealIsNaN.md) | [P_Demo_RealIsNaN.TcPOU](examples/P_Demo_RealIsNaN.TcPOU) |

### [Obsolete]（2）

| Name | 文档 | 例程 |
|---|---|---|
| FLOATIsFinite | [✅ deprecated](obsolete/FLOATIsFinite.md) | [P_Demo_FLOATIsFinite.TcPOU](examples/P_Demo_FLOATIsFinite.TcPOU) |
| FLOATIsNaN | [✅ deprecated](obsolete/FLOATIsNaN.md) | [P_Demo_FLOATIsNaN.TcPOU](examples/P_Demo_FLOATIsNaN.TcPOU) |

### 16 bit fixed-point number functions (signed)（9）

| Name | 文档 | 例程 |
|---|---|---|
| FIX16_TO_LREAL | [✅](fix16/FIX16_TO_LREAL.md) | [P_Demo_FIX16_TO_LREAL.TcPOU](examples/P_Demo_FIX16_TO_LREAL.TcPOU) |
| FIX16_TO_WORD | [✅](fix16/FIX16_TO_WORD.md) | [P_Demo_FIX16_TO_WORD.TcPOU](examples/P_Demo_FIX16_TO_WORD.TcPOU) |
| FIX16Add | [✅](fix16/FIX16Add.md) | [P_Demo_FIX16Add.TcPOU](examples/P_Demo_FIX16Add.TcPOU) |
| FIX16Align | [✅](fix16/FIX16Align.md) | [P_Demo_FIX16Align.TcPOU](examples/P_Demo_FIX16Align.TcPOU) |
| FIX16Div | [✅](fix16/FIX16Div.md) | [P_Demo_FIX16Div.TcPOU](examples/P_Demo_FIX16Div.TcPOU) |
| FIX16Mul | [✅](fix16/FIX16Mul.md) | [P_Demo_FIX16Mul.TcPOU](examples/P_Demo_FIX16Mul.TcPOU) |
| FIX16Sub | [✅](fix16/FIX16Sub.md) | [P_Demo_FIX16Sub.TcPOU](examples/P_Demo_FIX16Sub.TcPOU) |
| LREAL_TO_FIX16 | [✅](fix16/LREAL_TO_FIX16.md) | [P_Demo_LREAL_TO_FIX16.TcPOU](examples/P_Demo_LREAL_TO_FIX16.TcPOU) |
| WORD_TO_FIX16 | [✅](fix16/WORD_TO_FIX16.md) | [P_Demo_WORD_TO_FIX16.TcPOU](examples/P_Demo_WORD_TO_FIX16.TcPOU) |

### Byte order converting functions（10）

| Name | 文档 | 例程 |
|---|---|---|
| HOST_TO_BE16 | [✅](byte_order/HOST_TO_BE16.md) | [P_Demo_HOST_TO_BE16.TcPOU](examples/P_Demo_HOST_TO_BE16.TcPOU) |
| HOST_TO_BE32 | [✅](byte_order/HOST_TO_BE32.md) | [P_Demo_HOST_TO_BE32.TcPOU](examples/P_Demo_HOST_TO_BE32.TcPOU) |
| HOST_TO_BE64 | [✅](byte_order/HOST_TO_BE64.md) | [P_Demo_HOST_TO_BE64.TcPOU](examples/P_Demo_HOST_TO_BE64.TcPOU) |
| HOST_TO_BE64EX | [✅](byte_order/HOST_TO_BE64EX.md) | [P_Demo_HOST_TO_BE64EX.TcPOU](examples/P_Demo_HOST_TO_BE64EX.TcPOU) |
| HOST_TO_BE128 | [✅](byte_order/HOST_TO_BE128.md) | [P_Demo_HOST_TO_BE128.TcPOU](examples/P_Demo_HOST_TO_BE128.TcPOU) |
| BE16_TO_HOST | [✅](byte_order/BE16_TO_HOST.md) | [P_Demo_BE16_TO_HOST.TcPOU](examples/P_Demo_BE16_TO_HOST.TcPOU) |
| BE32_TO_HOST | [✅](byte_order/BE32_TO_HOST.md) | [P_Demo_BE32_TO_HOST.TcPOU](examples/P_Demo_BE32_TO_HOST.TcPOU) |
| BE64_TO_HOST | [✅](byte_order/BE64_TO_HOST.md) | [P_Demo_BE64_TO_HOST.TcPOU](examples/P_Demo_BE64_TO_HOST.TcPOU) |
| BE64_TO_HOSTEX | [✅](byte_order/BE64_TO_HOSTEX.md) | [P_Demo_BE64_TO_HOSTEX.TcPOU](examples/P_Demo_BE64_TO_HOSTEX.TcPOU) |
| BE128_TO_HOST | [✅](byte_order/BE128_TO_HOST.md) | [P_Demo_BE128_TO_HOST.TcPOU](examples/P_Demo_BE128_TO_HOST.TcPOU) |

### Time functions（23）

| Name | 文档 | 例程 |
|---|---|---|
| DT_TO_FILETIME64 | [✅](time_functions/DT_TO_FILETIME64.md) | [P_Demo_DT_TO_FILETIME64.TcPOU](examples/P_Demo_DT_TO_FILETIME64.TcPOU) |
| DT_TO_SYSTEMTIME | [✅](time_functions/DT_TO_SYSTEMTIME.md) | [P_Demo_DT_TO_SYSTEMTIME.TcPOU](examples/P_Demo_DT_TO_SYSTEMTIME.TcPOU) |
| F_EuropeanLocalTime | [✅](time_functions/F_EuropeanLocalTime.md) | [P_Demo_F_EuropeanLocalTime.TcPOU](examples/P_Demo_F_EuropeanLocalTime.TcPOU) |
| F_GetDayOfMonthEx | [✅](time_functions/F_GetDayOfMonthEx.md) | [P_Demo_F_GetDayOfMonthEx.TcPOU](examples/P_Demo_F_GetDayOfMonthEx.TcPOU) |
| F_GetDayOfWeek | [✅](time_functions/F_GetDayOfWeek.md) | [P_Demo_F_GetDayOfWeek.TcPOU](examples/P_Demo_F_GetDayOfWeek.TcPOU) |
| F_GetDOYOfYearMonthDay | [✅](time_functions/F_GetDOYOfYearMonthDay.md) | [P_Demo_F_GetDOYOfYearMonthDay.TcPOU](examples/P_Demo_F_GetDOYOfYearMonthDay.TcPOU) |
| F_GetMaxMonthDays | [✅](time_functions/F_GetMaxMonthDays.md) | [P_Demo_F_GetMaxMonthDays.TcPOU](examples/P_Demo_F_GetMaxMonthDays.TcPOU) |
| F_GetMonthOfDOY | [✅](time_functions/F_GetMonthOfDOY.md) | [P_Demo_F_GetMonthOfDOY.TcPOU](examples/P_Demo_F_GetMonthOfDOY.TcPOU) |
| F_GetWeekOfTheYear | [✅](time_functions/F_GetWeekOfTheYear.md) | [P_Demo_F_GetWeekOfTheYear.TcPOU](examples/P_Demo_F_GetWeekOfTheYear.TcPOU) |
| F_TranslateFileTime64Bias | [✅](time_functions/F_TranslateFileTime64Bias.md) | [P_Demo_F_TranslateFileTime64Bias.TcPOU](examples/P_Demo_F_TranslateFileTime64Bias.TcPOU) |
| F_YearIsLeapYear | [✅](time_functions/F_YearIsLeapYear.md) | [P_Demo_F_YearIsLeapYear.TcPOU](examples/P_Demo_F_YearIsLeapYear.TcPOU) |
| FILETIME64_TO_DT | [✅](time_functions/FILETIME64_TO_DT.md) | [P_Demo_FILETIME64_TO_DT.TcPOU](examples/P_Demo_FILETIME64_TO_DT.TcPOU) |
| FILETIME64_TO_ISO8601 | [✅](time_functions/FILETIME64_TO_ISO8601.md) | [P_Demo_FILETIME64_TO_ISO8601.TcPOU](examples/P_Demo_FILETIME64_TO_ISO8601.TcPOU) |
| FILETIME64_TO_SYSTEMTIME | [✅](time_functions/FILETIME64_TO_SYSTEMTIME.md) | [P_Demo_FILETIME64_TO_SYSTEMTIME.TcPOU](examples/P_Demo_FILETIME64_TO_SYSTEMTIME.TcPOU) |
| FILETIME64_TO_TOD | [✅](time_functions/FILETIME64_TO_TOD.md) | [P_Demo_FILETIME64_TO_TOD.TcPOU](examples/P_Demo_FILETIME64_TO_TOD.TcPOU) |
| OTSTRUCT_TO_TIME | [✅](time_functions/OTSTRUCT_TO_TIME.md) | [P_Demo_OTSTRUCT_TO_TIME.TcPOU](examples/P_Demo_OTSTRUCT_TO_TIME.TcPOU) |
| STRING_TO_SYSTEMTIME | [✅](time_functions/STRING_TO_SYSTEMTIME.md) | [P_Demo_STRING_TO_SYSTEMTIME.TcPOU](examples/P_Demo_STRING_TO_SYSTEMTIME.TcPOU) |
| SYSTEMTIME_TO_DT | [✅](time_functions/SYSTEMTIME_TO_DT.md) | [P_Demo_SYSTEMTIME_TO_DT.TcPOU](examples/P_Demo_SYSTEMTIME_TO_DT.TcPOU) |
| SYSTEMTIME_TO_FILETIME64 | [✅](time_functions/SYSTEMTIME_TO_FILETIME64.md) | [P_Demo_SYSTEMTIME_TO_FILETIME64.TcPOU](examples/P_Demo_SYSTEMTIME_TO_FILETIME64.TcPOU) |
| SYSTEMTIME_TO_ISO8601 | [✅](time_functions/SYSTEMTIME_TO_ISO8601.md) | [P_Demo_SYSTEMTIME_TO_ISO8601.TcPOU](examples/P_Demo_SYSTEMTIME_TO_ISO8601.TcPOU) |
| SYSTEMTIME_TO_STRING | [✅](time_functions/SYSTEMTIME_TO_STRING.md) | [P_Demo_SYSTEMTIME_TO_STRING.TcPOU](examples/P_Demo_SYSTEMTIME_TO_STRING.TcPOU) |
| SYSTEMTIME_TO_TOD | [✅](time_functions/SYSTEMTIME_TO_TOD.md) | [P_Demo_SYSTEMTIME_TO_TOD.TcPOU](examples/P_Demo_SYSTEMTIME_TO_TOD.TcPOU) |
| TIME_TO_OTSTRUCT | [✅](time_functions/TIME_TO_OTSTRUCT.md) | [P_Demo_TIME_TO_OTSTRUCT.TcPOU](examples/P_Demo_TIME_TO_OTSTRUCT.TcPOU) |

### TC_CoreBoostMonitor（父 FB + 5 methods）

| Name | 文档 | 例程 |
|---|---|---|
| **TC_CoreBoostMonitor** (父 FB) | [✅](tc_coreboostmonitor/TC_CoreBoostMonitor.md) | [P_Demo_TC_CoreBoostMonitor.TcPOU](examples/P_Demo_TC_CoreBoostMonitor.TcPOU) |
| GetAllRtCoreThrottling | [✅](tc_coreboostmonitor/GetAllRtCoreThrottling.md) | [P_Demo_GetAllRtCoreThrottling.TcPOU](examples/P_Demo_GetAllRtCoreThrottling.TcPOU) |
| GetCoreFrequency | [✅](tc_coreboostmonitor/GetCoreFrequency.md) | [P_Demo_GetCoreFrequency.TcPOU](examples/P_Demo_GetCoreFrequency.TcPOU) |
| GetCoreTemperature | [✅](tc_coreboostmonitor/GetCoreTemperature.md) | [P_Demo_GetCoreTemperature.TcPOU](examples/P_Demo_GetCoreTemperature.TcPOU) |
| GetCoreThrottling | [✅](tc_coreboostmonitor/GetCoreThrottling.md) | [P_Demo_GetCoreThrottling.TcPOU](examples/P_Demo_GetCoreThrottling.TcPOU) |
| GetPowerConsumption | [✅](tc_coreboostmonitor/GetPowerConsumption.md) | [P_Demo_GetPowerConsumption.TcPOU](examples/P_Demo_GetPowerConsumption.TcPOU) |

### [obsolete] Function blocks（4，已废弃）

| Name | 文档 | 例程 |
|---|---|---|
| FB_AdsReadEvents | [⚠️ deprecated](obsolete_fb/FB_AdsReadEvents.md) | [P_Demo_FB_AdsReadEvents.TcPOU](examples/P_Demo_FB_AdsReadEvents.TcPOU) |
| FB_GetDeviceIdentification | [⚠️ deprecated](obsolete_fb/FB_GetDeviceIdentification.md) | [P_Demo_FB_GetDeviceIdentification.TcPOU](examples/P_Demo_FB_GetDeviceIdentification.TcPOU) |
| FB_FileTimeToTzSpecificLocalTime | [⚠️ deprecated](obsolete_fb/FB_FileTimeToTzSpecificLocalTime.md) | [P_Demo_FB_FileTimeToTzSpecificLocalTime.TcPOU](examples/P_Demo_FB_FileTimeToTzSpecificLocalTime.TcPOU) |
| FB_TzSpecificLocalTimeToFileTime | [⚠️ deprecated](obsolete_fb/FB_TzSpecificLocalTimeToFileTime.md) | [P_Demo_FB_TzSpecificLocalTimeToFileTime.TcPOU](examples/P_Demo_FB_TzSpecificLocalTimeToFileTime.TcPOU) |

### T_Arg help functions（27）

| Name | 文档 | 例程 |
|---|---|---|
| F_ARGCMP | [✅](t_arg/F_ARGCMP.md) | [P_Demo_F_ARGCMP.TcPOU](examples/P_Demo_F_ARGCMP.TcPOU) |
| F_ARGCPY | [✅](t_arg/F_ARGCPY.md) | [P_Demo_F_ARGCPY.TcPOU](examples/P_Demo_F_ARGCPY.TcPOU) |
| F_ARGISZERO | [✅](t_arg/F_ARGISZERO.md) | [P_Demo_F_ARGISZERO.TcPOU](examples/P_Demo_F_ARGISZERO.TcPOU) |
| F_BIGTYPE | [✅](t_arg/F_BIGTYPE.md) | [P_Demo_F_BIGTYPE.TcPOU](examples/P_Demo_F_BIGTYPE.TcPOU) |
| F_BOOL | [✅](t_arg/F_BOOL.md) | [P_Demo_F_BOOL.TcPOU](examples/P_Demo_F_BOOL.TcPOU) |
| F_BYTE | [✅](t_arg/F_BYTE.md) | [P_Demo_F_BYTE.TcPOU](examples/P_Demo_F_BYTE.TcPOU) |
| F_DINT | [✅](t_arg/F_DINT.md) | [P_Demo_F_DINT.TcPOU](examples/P_Demo_F_DINT.TcPOU) |
| F_DWORD | [✅](t_arg/F_DWORD.md) | [P_Demo_F_DWORD.TcPOU](examples/P_Demo_F_DWORD.TcPOU) |
| F_HUGE | [✅](t_arg/F_HUGE.md) | [P_Demo_F_HUGE.TcPOU](examples/P_Demo_F_HUGE.TcPOU) |
| F_INT | [✅](t_arg/F_INT.md) | [P_Demo_F_INT.TcPOU](examples/P_Demo_F_INT.TcPOU) |
| F_LARGE | [✅](t_arg/F_LARGE.md) | [P_Demo_F_LARGE.TcPOU](examples/P_Demo_F_LARGE.TcPOU) |
| F_LINT | [✅](t_arg/F_LINT.md) | [P_Demo_F_LINT.TcPOU](examples/P_Demo_F_LINT.TcPOU) |
| F_LREAL | [✅](t_arg/F_LREAL.md) | [P_Demo_F_LREAL.TcPOU](examples/P_Demo_F_LREAL.TcPOU) |
| F_LWORD | [✅](t_arg/F_LWORD.md) | [P_Demo_F_LWORD.TcPOU](examples/P_Demo_F_LWORD.TcPOU) |
| F_REAL | [✅](t_arg/F_REAL.md) | [P_Demo_F_REAL.TcPOU](examples/P_Demo_F_REAL.TcPOU) |
| F_SINT | [✅](t_arg/F_SINT.md) | [P_Demo_F_SINT.TcPOU](examples/P_Demo_F_SINT.TcPOU) |
| F_STRING | [✅](t_arg/F_STRING.md) | [P_Demo_F_STRING.TcPOU](examples/P_Demo_F_STRING.TcPOU) |
| F_STRINGEx | [✅](t_arg/F_STRINGEx.md) | [P_Demo_F_STRINGEx.TcPOU](examples/P_Demo_F_STRINGEx.TcPOU) |
| F_UDINT | [✅](t_arg/F_UDINT.md) | [P_Demo_F_UDINT.TcPOU](examples/P_Demo_F_UDINT.TcPOU) |
| F_UHUGE | [✅](t_arg/F_UHUGE.md) | [P_Demo_F_UHUGE.TcPOU](examples/P_Demo_F_UHUGE.TcPOU) |
| F_UINT | [✅](t_arg/F_UINT.md) | [P_Demo_F_UINT.TcPOU](examples/P_Demo_F_UINT.TcPOU) |
| F_ULARGE | [✅](t_arg/F_ULARGE.md) | [P_Demo_F_ULARGE.TcPOU](examples/P_Demo_F_ULARGE.TcPOU) |
| F_ULINT | [✅](t_arg/F_ULINT.md) | [P_Demo_F_ULINT.TcPOU](examples/P_Demo_F_ULINT.TcPOU) |
| F_USINT | [✅](t_arg/F_USINT.md) | [P_Demo_F_USINT.TcPOU](examples/P_Demo_F_USINT.TcPOU) |
| F_WORD | [✅](t_arg/F_WORD.md) | [P_Demo_F_WORD.TcPOU](examples/P_Demo_F_WORD.TcPOU) |
| F_PVOID | [✅](t_arg/F_PVOID.md) | [P_Demo_F_PVOID.TcPOU](examples/P_Demo_F_PVOID.TcPOU) |
| IsFinite | [✅](t_arg/IsFinite.md) | [P_Demo_IsFinite.TcPOU](examples/P_Demo_IsFinite.TcPOU) |

### P[TYPE]_TO_[TYPE] converting functions（26）

> 全部为指针解引用函数，模式统一：`POINTER TO X` → `X`

| Name | 文档 | 例程 |
|---|---|---|
| PBOOL_TO_BOOL | [✅](p_to_value/PBOOL_TO_BOOL.md) | [P_Demo_PBOOL_TO_BOOL.TcPOU](examples/P_Demo_PBOOL_TO_BOOL.TcPOU) |
| PBYTE_TO_BYTE | [✅](p_to_value/PBYTE_TO_BYTE.md) | [P_Demo_PBYTE_TO_BYTE.TcPOU](examples/P_Demo_PBYTE_TO_BYTE.TcPOU) |
| PDATE_TO_DATE | [✅](p_to_value/PDATE_TO_DATE.md) | [P_Demo_PDATE_TO_DATE.TcPOU](examples/P_Demo_PDATE_TO_DATE.TcPOU) |
| PDINT_TO_DINT | [✅](p_to_value/PDINT_TO_DINT.md) | [P_Demo_PDINT_TO_DINT.TcPOU](examples/P_Demo_PDINT_TO_DINT.TcPOU) |
| PDT_TO_DT | [✅](p_to_value/PDT_TO_DT.md) | [P_Demo_PDT_TO_DT.TcPOU](examples/P_Demo_PDT_TO_DT.TcPOU) |
| PDWORD_TO_DWORD | [✅](p_to_value/PDWORD_TO_DWORD.md) | [P_Demo_PDWORD_TO_DWORD.TcPOU](examples/P_Demo_PDWORD_TO_DWORD.TcPOU) |
| PHUGE_TO_HUGE | [✅](p_to_value/PHUGE_TO_HUGE.md) | [P_Demo_PHUGE_TO_HUGE.TcPOU](examples/P_Demo_PHUGE_TO_HUGE.TcPOU) |
| PINT_TO_INT | [✅](p_to_value/PINT_TO_INT.md) | [P_Demo_PINT_TO_INT.TcPOU](examples/P_Demo_PINT_TO_INT.TcPOU) |
| PLARGE_TO_LARGE | [✅](p_to_value/PLARGE_TO_LARGE.md) | [P_Demo_PLARGE_TO_LARGE.TcPOU](examples/P_Demo_PLARGE_TO_LARGE.TcPOU) |
| PLINT_TO_LINT | [✅](p_to_value/PLINT_TO_LINT.md) | [P_Demo_PLINT_TO_LINT.TcPOU](examples/P_Demo_PLINT_TO_LINT.TcPOU) |
| PLREAL_TO_LREAL | [✅](p_to_value/PLREAL_TO_LREAL.md) | [P_Demo_PLREAL_TO_LREAL.TcPOU](examples/P_Demo_PLREAL_TO_LREAL.TcPOU) |
| PLWORD_TO_LWORD | [✅](p_to_value/PLWORD_TO_LWORD.md) | [P_Demo_PLWORD_TO_LWORD.TcPOU](examples/P_Demo_PLWORD_TO_LWORD.TcPOU) |
| PMAXSTRING_TO_MAXSTRING | [✅](p_to_value/PMAXSTRING_TO_MAXSTRING.md) | [P_Demo_PMAXSTRING_TO_MAXSTRING.TcPOU](examples/P_Demo_PMAXSTRING_TO_MAXSTRING.TcPOU) |
| PREAL_TO_REAL | [✅](p_to_value/PREAL_TO_REAL.md) | [P_Demo_PREAL_TO_REAL.TcPOU](examples/P_Demo_PREAL_TO_REAL.TcPOU) |
| PSINT_TO_SINT | [✅](p_to_value/PSINT_TO_SINT.md) | [P_Demo_PSINT_TO_SINT.TcPOU](examples/P_Demo_PSINT_TO_SINT.TcPOU) |
| PSTRING_TO_STRING | [✅](p_to_value/PSTRING_TO_STRING.md) | [P_Demo_PSTRING_TO_STRING.TcPOU](examples/P_Demo_PSTRING_TO_STRING.TcPOU) |
| PTIME_TO_TIME | [✅](p_to_value/PTIME_TO_TIME.md) | [P_Demo_PTIME_TO_TIME.TcPOU](examples/P_Demo_PTIME_TO_TIME.TcPOU) |
| PTOD_TO_TOD | [✅](p_to_value/PTOD_TO_TOD.md) | [P_Demo_PTOD_TO_TOD.TcPOU](examples/P_Demo_PTOD_TO_TOD.TcPOU) |
| PUDINT_TO_UDINT | [✅](p_to_value/PUDINT_TO_UDINT.md) | [P_Demo_PUDINT_TO_UDINT.TcPOU](examples/P_Demo_PUDINT_TO_UDINT.TcPOU) |
| PUHUGE_TO_UHUGE | [✅](p_to_value/PUHUGE_TO_UHUGE.md) | [P_Demo_PUHUGE_TO_UHUGE.TcPOU](examples/P_Demo_PUHUGE_TO_UHUGE.TcPOU) |
| PUINT_TO_UINT | [✅](p_to_value/PUINT_TO_UINT.md) | [P_Demo_PUINT_TO_UINT.TcPOU](examples/P_Demo_PUINT_TO_UINT.TcPOU) |
| PULARGE_TO_ULARGE | [✅](p_to_value/PULARGE_TO_ULARGE.md) | [P_Demo_PULARGE_TO_ULARGE.TcPOU](examples/P_Demo_PULARGE_TO_ULARGE.TcPOU) |
| PULINT_TO_ULINT | [✅](p_to_value/PULINT_TO_ULINT.md) | [P_Demo_PULINT_TO_ULINT.TcPOU](examples/P_Demo_PULINT_TO_ULINT.TcPOU) |
| PUSINT_TO_USINT | [✅](p_to_value/PUSINT_TO_USINT.md) | [P_Demo_PUSINT_TO_USINT.TcPOU](examples/P_Demo_PUSINT_TO_USINT.TcPOU) |
| PWORD_TO_WORD | [✅](p_to_value/PWORD_TO_WORD.md) | [P_Demo_PWORD_TO_WORD.TcPOU](examples/P_Demo_PWORD_TO_WORD.TcPOU) |
| PUINT64_TO_UINT64 | [✅](p_to_value/PUINT64_TO_UINT64.md) | [P_Demo_PUINT64_TO_UINT64.TcPOU](examples/P_Demo_PUINT64_TO_UINT64.TcPOU) |

### Extended STRING functions（30）

| 子类 | 条目 |
|---|---|
| 任意长 STRING/WSTRING ops | `CONCAT2` `DELETE2` `FIND2` `INSERT2` `REPLACE2` `LEN2` `WCONCAT2` `WLEN2` `STRNCPY` `WSTRNCPY` |
| Find-and-* 模式 | `FindAndDelete` `FindAndDeleteChar` `FindAndReplace` `FindAndReplaceChar` `FindAndSplit` `FindAndSplitChar` |
| 单字符转换 | `CHAR_TO_WCHAR` `WCHAR_TO_CHAR` |
| STRING ↔ WSTRING（任意长） | `STRING_TO_WSTRING2` `WSTRING_TO_STRING2` |
| UTF-8 转换 | `STRING_TO_UTF8` `UTF8_TO_STRING` `WSTRING_TO_UTF8` `UTF8_TO_WSTRING` `UTF8Len` |
| UTF-8 字面量 | `sLiteral_TO_UTF8` `wsLiteral_TO_UTF8` |
| 检查 | `F_StringIsASCII` |
| HEX ↔ binary | `DATA_TO_HEXSTR2` `HEXSTR_TO_DATA2` |

各条文档与例程：`Tc2_Utilities/extended_string/<Name>.md` + `Tc2_Utilities/examples/P_Demo_<Name>.TcPOU`。

### 64-bit functions (signed)（15）

| Name | 文档 | 例程 |
|---|---|---|
| INT64_TO_LREAL | [✅](int64_signed/INT64_TO_LREAL.md) | [P_Demo_INT64_TO_LREAL.TcPOU](examples/P_Demo_INT64_TO_LREAL.TcPOU) |
| Int64Add64 | [✅](int64_signed/Int64Add64.md) | [P_Demo_Int64Add64.TcPOU](examples/P_Demo_Int64Add64.TcPOU) |
| Int64Add64Ex | [✅](int64_signed/Int64Add64Ex.md) | [P_Demo_Int64Add64Ex.TcPOU](examples/P_Demo_Int64Add64Ex.TcPOU) |
| Int64Cmp64 | [✅](int64_signed/Int64Cmp64.md) | [P_Demo_Int64Cmp64.TcPOU](examples/P_Demo_Int64Cmp64.TcPOU) |
| Int64Div64Ex | [✅](int64_signed/Int64Div64Ex.md) | [P_Demo_Int64Div64Ex.TcPOU](examples/P_Demo_Int64Div64Ex.TcPOU) |
| Int64IsZero | [✅](int64_signed/Int64IsZero.md) | [P_Demo_Int64IsZero.TcPOU](examples/P_Demo_Int64IsZero.TcPOU) |
| Int64Negate | [✅](int64_signed/Int64Negate.md) | [P_Demo_Int64Negate.TcPOU](examples/P_Demo_Int64Negate.TcPOU) |
| Int64Not | [✅](int64_signed/Int64Not.md) | [P_Demo_Int64Not.TcPOU](examples/P_Demo_Int64Not.TcPOU) |
| Int64Sub64 | [✅](int64_signed/Int64Sub64.md) | [P_Demo_Int64Sub64.TcPOU](examples/P_Demo_Int64Sub64.TcPOU) |
| LARGE_INTEGER | [✅](int64_signed/LARGE_INTEGER.md) | [P_Demo_LARGE_INTEGER.TcPOU](examples/P_Demo_LARGE_INTEGER.TcPOU) |
| LARGE_TO_LINT | [✅](int64_signed/LARGE_TO_LINT.md) | [P_Demo_LARGE_TO_LINT.TcPOU](examples/P_Demo_LARGE_TO_LINT.TcPOU) |
| LARGE_TO_ULARGE | [✅](int64_signed/LARGE_TO_ULARGE.md) | [P_Demo_LARGE_TO_ULARGE.TcPOU](examples/P_Demo_LARGE_TO_ULARGE.TcPOU) |
| LINT_TO_LARGE | [✅](int64_signed/LINT_TO_LARGE.md) | [P_Demo_LINT_TO_LARGE.TcPOU](examples/P_Demo_LINT_TO_LARGE.TcPOU) |
| LREAL_TO_INT64 | [✅](int64_signed/LREAL_TO_INT64.md) | [P_Demo_LREAL_TO_INT64.TcPOU](examples/P_Demo_LREAL_TO_INT64.TcPOU) |
| ULARGE_TO_LARGE | [✅](int64_signed/ULARGE_TO_LARGE.md) | [P_Demo_ULARGE_TO_LARGE.TcPOU](examples/P_Demo_ULARGE_TO_LARGE.TcPOU) |

### 64-bit integer functions (unsigned)（31）

> 围绕 `T_ULARGE_INTEGER`（TwinCAT 2 legacy 64-bit 无符号结构）。Round 7 是同结构的有符号版。

| 子类 | 条目 |
|---|---|
| 算术 | `UInt64Add64` `UInt64Add64Ex`(bOV) `UInt64Sub64` `UInt64Mul64` `UInt64Mul64Ex`(bOV) `UInt64Div64` `UInt64Div64Ex`(remainder) `UInt64Div16Ex`(WORD divisor) `UInt64Mod64` `UInt32x32To64`(32×32→64) |
| 位运算 | `UInt64And` `UInt64Or` `UInt64Xor` `UInt64Not` `UInt64Shl` `UInt64Shr` `UInt64Rol` `UInt64Ror` |
| 比较/谓词 | `UInt64Cmp64` `UInt64isZero` |
| 限幅 | `UInt64Limit`(min,in,max) `UInt64Max` `UInt64Min` |
| 转换 | `LREAL_TO_UINT64` `UINT64_TO_LREAL` `STRING_TO_UINT64` `UINT64_TO_STRING` `LWORD_TO_ULARGE` `ULARGE_TO_LWORD` `ULARGE_TO_ULINT` |
| 构造器 | `ULARGE_INTEGER`(high, low) |

各条文档 / 例程：`Tc2_Utilities/uint64/<Name>.md` + `Tc2_Utilities/examples/P_Demo_<Name>.TcPOU`。

### Functions（66 散类）

> 涵盖 CRC/CSV/GUID/hash/角度/格式化/HEX/Base36/字符串大小写/路由层枚举 等。详见 `Tc2_Utilities/functions/<Name>.md` 与 `Tc2_Utilities/examples/P_Demo_<Name>.TcPOU`。

| 子类 | 条目（部分） |
|---|---|
| CRC / 校验和 | `F_BYTE_TO_CRC16_CCITT` `F_DATA_TO_CRC16_CCITT` `F_CheckSum16` |
| 哈希 | `F_GenerateHashValue`（SHA/MD5） `F_CreateHashTableHnd` `F_CreateLinkedListHnd` |
| CSV | `ARG_TO_CSVFIELD` `CSVFIELD_TO_ARG` `STRING_TO_CSVFIELD` `CSVFIELD_TO_STRING`（PDF typo `CSFIELD`） |
| GUID | `GUID_TO_STRING` `GUID_TO_REGSTRING` `STRING_TO_GUID` `REGSTRING_TO_GUID` `GuidsEqualByVal` |
| 数 ↔ 字符串 | `BYTE/WORD/DWORD/LWORD/PVOID/DINT/LINT_TO_{BIN,DEC,OCT,HEX}STR` `LWORD_TO_BASE36STR` `LREAL_TO_FMTSTR` |
| HEX ↔ binary | `DATA_TO_HEXSTR`(≤85B) `HEXSTR_TO_DATA` `HEXASCNIBBLE_TO_BYTE` `HEXCHRNIBBLE_TO_BYTE` |
| 角度 | `DEG_TO_RAD` `RAD_TO_DEG` |
| 字符串处理 | `F_LTrim` `F_RTrim` `F_ToLCase` `F_ToUCase` `MAXSTRING_TO_BYTEARR` `BYTEARR_TO_MAXSTRING` |
| BIC | `BIC_TO_BTN` `F_SplitBIC` |
| LREALEX 安全转换 | `BYTE/WORD/DWORD/UINT/UDINT/USINT_TO_LREALEX`（TC2 ARM unsigned safe） |
| ULINT ↔ ULARGE | `ULINT_TO_ULARGE` |
| 其他 | `F_SwapRealEx`(BC/BX ↔ IPC) `F_GetClassIdVersioned` `F_FormatArgToStr`(FB_FormatString helper) `PVOID_TO_STRING`/`STRING_TO_PVOID` `ROUTETRANSPORT_TO_STRING` |

### Function blocks（88，Round 10 自动生成）

> 88 个 FB 自动从 PDF 抽取 VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT，描述句简化版（详细行为与错误码请对照 PDF 第 3.x 章）。所有 doc + xml 均通过 `verify_doc.py` 与 `lint_tcpou.py`。

涵盖：BCD ↔ DEC、DCF77 时钟、AMS 路由、ADS logger、PID、Hash 计算（含 OO 父 FB）、License/Dongle、CSV 缓冲、FindFile 枚举、文件属性/环形缓冲、Format 字符串、网卡信息、Hash 表 / 链表控制、本地系统时间、内存合并/拆分/环形缓冲/栈缓冲、注册表读写、Scope server 控制、时区设置/转换、持久化数据写入、RT 性能、远程 PC 信息、NT 操作（重启/关机/进程）、PLC 控制（启动/停止/复位/符号表）、Profiler、RTC 系列、TC_Config/TC_Restart/TC_Stop、CPU 使用率、系统延迟等。

各条文档与例程在 `Tc2_Utilities/function_blocks/<Name>.md` + `Tc2_Utilities/examples/P_Demo_<Name>.TcPOU`。

### Library version（1）

| Name | 文档 | 例程 |
|---|---|---|
| stLibVersion_Tc2_Utilities | [✅](global_constants/stLibVersion_Tc2_Utilities.md) | [P_Demo_stLibVersion_Tc2_Utilities.TcPOU](examples/P_Demo_stLibVersion_Tc2_Utilities.TcPOU) |
