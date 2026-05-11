# InfoSys topic URL map for Tc2_Utilities function blocks
# Verified 2026-05-11 via site:infosys.beckhoff.com searches.
# Missing IDs → ⚠️ not-on-infosys fallback handled by generator.

BASE = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities"

# Map of FB name → topic ID (string). When a name is absent the generator
# emits the documented "⚠️ not-on-infosys" fallback per the 2026-05-11 charter.
URLS = {
    # Time / time zone
    "FB_LocalSystemTime": "35008651",
    "FB_GetTimeZoneInformation": "35004043",
    "FB_SetTimeZoneInformation": "35022475",
    "FB_SystemTimeToTzSpecificLocalTime": "35025547",
    "FB_TzSpecificLocalTimeToSystemTime": "35028619",
    "FB_TzSpecificLocalTimeToFileTime64": "10500798219",
    "FB_FileTime64ToTzSpecificLocalTime": "10500868619",
    "DCF77_TIME": "34972939",
    "DCF77_TIME_EX": "34973067",
    "RTC": "35013643",
    "RTC_EX": "35014923",
    "RTC_EX2": "35016203",
    "NT_GetTime": "35037067",
    "NT_SetLocalTime": "35037835",
    "NT_SetTimeToRTCTime": "35038603",
    # Routing / network info
    "FB_AddRouteEntry": "34973323",
    "FB_AddRouteEntryEx": "9682603019",
    "FB_EnumRouteEntry": "34979723",
    "FB_RemoveRouteEntry": "35020939",
    "FB_GetLocalAmsNetId": "35001483",
    "FB_GetHostName": "34998923",
    "FB_GetHostAddrByName": "34997387",
    "FB_GetAdaptersInfo": "34995851",
    "FB_GetAdaptersInfoEx": "9682552715",
    "FB_GetRouterStatusInfo": "35002763",
    "FB_GetSystemId": "35003531",
    "FB_GetVolumeId": "35008011",
    "FB_GetDeviceIdentificationEx": "9682567307",
    # License / dongle
    "FB_CheckLicense": "34977419",
    "FB_CheckOemLicense": "9007199892812299",
    "FB_GetLicenses": "34999691",
    "FB_GetLicensesEx": "9682567435",
    "FB_GetLicenseDongles": "9007199892814347",
    "FB_GetDongleSystemID": "9007199892815499",
    "FB_GetOemOfLicenseId": "9007199892816651",
    "FB_LicFileCopyFromDongle": "9007199892817803",
    "FB_LicFileCopyToDongle": "9007199892818955",
    "FB_LicFileCreate": "9007199892820107",
    "FB_LicFileDelete": "9007199892821259",
    "FB_LicFileGetStorageInfo": "9007199892822411",
    "FB_LicFileRead": "9007199892823563",
    # File / persistence
    "FB_FileProperties": "34989963",
    "FB_FileRingBuffer": "9676815883",
    "FB_EnumFindFileEntry": "9676817803",
    "FB_EnumFindFileList": "9676819723",
    "FB_WritePersistentData": "35029387",
    "WritePersistentData": "35044235",
    # Memory buffers / CSV
    "FB_CSVMemBufferReader": "34978827",
    "FB_CSVMemBufferWriter": "34979467",
    "FB_MemBufferMerge": "34980491",
    "FB_MemBufferSplit": "34981259",
    "FB_MemRingBuffer": "35009931",
    "FB_MemRingBufferEx": "9676821643",
    "FB_MemStackBuffer": "35012107",
    "FB_StringRingBuffer": "35024651",
    # Data structures
    "FB_HashTableCtrl": "35006731",
    "FB_LinkedListCtrl": "35007499",
    "FB_EnumStringNumbers": "34988171",
    # Registry
    "FB_RegQueryValue": "35017739",
    "FB_RegSetValue": "35019403",
    # Strings / format
    "FB_FormatString": "34993803",
    "FB_FormatString2": "34994443",
    # Logger / scope
    "FB_AmsLogger": "34973963",
    "FB_ScopeServerControl": "35023115",
    # System control
    "NT_AbortShutdown": "35029643",
    "NT_Reboot": "35036299",
    "NT_Shutdown": "35039371",
    "NT_StartProcess": "35040139",
    "PLC_Reset": "35040907",
    "PLC_Start": "35041675",
    "PLC_Stop": "35042443",
    "PLC_ReadSymInfo": "35030411",
    "PLC_ReadSymInfoByName": "35031179",
    "PLC_ReadSymInfoByNameEx": "35031947",
    "TC_Config": "35033099",
    "TC_CpuUsage": "35033867",
    "TC_CpuUsageEx": "9682685451",
    "TC_Restart": "35034635",
    "TC_Stop": "35035403",
    "TC_SysLatency": "35036171",
    "TC_SysLatencyEx": "9682687371",
    # Misc
    "GetRemotePCInfo": "35044619",
    "Profiler": "35012875",
    "FB_GetRtPerformanceData": "9682569227",
    "BCD_TO_DEC": "34972043",
    "DEC_TO_BCD": "34972811",
    "FB_BasicPID": "35047819",  # InfoSys may not have; generator will fall back if 404 cached
}


def url_for(name: str) -> str | None:
    """Return full InfoSys topic URL for given name, or None if not mapped."""
    topic_id = URLS.get(name)
    if topic_id is None:
        return None
    return f"{BASE}/{topic_id}.html"
