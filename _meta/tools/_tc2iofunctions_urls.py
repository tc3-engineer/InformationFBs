"""InfoSys topic URL map for Tc2_IoFunctions FBs / FCs."""
URLS = {
    # General IO FBs
    "IOF_DeviceReset": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59085835.html",
    "IOF_GetBoxAddrByName": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59087371.html",
    "IOF_GetBoxAddrByNameEx": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59088907.html",
    "IOF_GetBoxCount": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59090443.html",
    "IOF_GetBoxNameByAddr": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59091979.html",
    "IOF_GetBoxNetId": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59093515.html",
    "IOF_GetDeviceCount": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59095051.html",
    "IOF_GetDeviceIDByName": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59096587.html",
    "IOF_GetDeviceIDs": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59098123.html",
    "IOF_GetDeviceInfoByName": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59104267.html",
    "IOF_GetDeviceName": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59099659.html",
    "IOF_GetDeviceNetId": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59101195.html",
    "IOF_GetDeviceType": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59102731.html",
    # ASI master terminal
    "FB_ASI_Addressing": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59149579.html",
    "FB_ASI_SlaveDiag": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59151115.html",
    "FB_ASI_ReadParameter": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59152651.html",
    "FB_ASI_WriteParameter": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59154187.html",
    "FB_ASI_Processdata_digital": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59155723.html",
    "FB_ASI_ParameterControl": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59157259.html",
    "FB_ReadInput_analog": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59158795.html",
    "FB_WriteOutput_analog": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59160331.html",
    # AX200x Profibus
    "FB_AX2000_Parameter": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59142027.html",
    "FB_AX2000_AXACT": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59138955.html",
    "FB_AX2000_JogMode": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59140491.html",
    "FB_AX2000_Reference": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59143563.html",
    "FB_AX200X_Profibus": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59145099.html",
    # Beckhoff Lightbus
    "IOF_LB_BreakLocationTest": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59107211.html",
    "IOF_LB_ParityCheck": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59108747.html",
    "IOF_LB_ParityCheckWithReset": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59110283.html",
    # Beckhoff UPS
    "FB_GetUPSStatus": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59184523.html",
    # Bus Terminal configuration
    "FB_KL1501Config": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/2084379019.html",
    "FB_KL27x1Config": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/2084380939.html",
    "FB_KL320xConfig": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/2084382859.html",
    "FB_KL3208Config": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/2084384779.html",
    "FB_KL3228Config": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/2084386699.html",
    # CANopen
    "IOF_CAN_Layer2Command": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59113227.html",
    # NOV/DP-RAM
    "FB_NovRamReadWrite": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59131403.html",
    "FB_NovRamReadWriteEx": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59132939.html",
    "FB_GetDPRAMInfo": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59134475.html",
    "FB_GetDPRAMInfoEx": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/2217659019.html",
    # Profibus DPV1 (Sinamics)
    "F_CreateDpv1ReadReqPkg": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59163275.html",
    "F_CreateDpv1WriteReqPkg": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59167883.html",
    "F_SplitDpv1ReadResPkg": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59166347.html",
    "F_SplitDpv1WriteResPkg": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59170955.html",
    "FB_Dpv1Read": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59164811.html",
    "FB_Dpv1Write": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59169419.html",
    # Profinet DPV1 (Sinamics)
    "F_CreateDpv1ReadReqPkgPNET": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59173899.html",
    "F_CreateDpv1WriteReqPkgPNET": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59178507.html",
    "F_SplitDpv1ReadResPkgPNET": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59176971.html",
    "F_SplitDpv1WriteResPkgPNET": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59181579.html",
    "FB_Dpv1ReadPNET": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59175435.html",
    "FB_Dpv1WritePNET": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59180043.html",
    # RAID Controller
    "FB_RAIDFindCntlr": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59208459.html",
    "FB_RAIDGetInfo": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59209995.html",
    "FB_RAIDGetStatus": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59211531.html",
    # SERCOS
    "IOF_SER_GetPhase": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59116171.html",
    "IOF_SER_SaveFlash": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59117707.html",
    "IOF_SER_ResetErr": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59119243.html",
    "IOF_SER_SetPhase": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59120779.html",
    "IOF_SER_IDN_Read": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59122315.html",
    "IOF_SER_IDN_Write": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59123851.html",
    "IOF_SER_DRIVE_Backup": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59125387.html",
    "IOF_SER_DRIVE_BackupEx": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59126923.html",
    "IOF_SER_DRIVE_Reset": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59128459.html",
    # TcTouchLock
    "FB_TcTouchLock_AcquireFocus": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/6811367563.html",
    # Library version GVL
    "stLibVersion_Tc2_IoFunctions": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59267851.html",
    # Obsolete FCs (no dedicated infosys topic page; redirect to Library version page
    # which lists these as obsolete)
    "F_GetVersionTcIoFunctions": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59267851.html",
    "F_GetVersionRAIDController": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59267851.html",
}


def url_for(name: str) -> str:
    return URLS.get(name, "⚠️ not-on-infosys")
