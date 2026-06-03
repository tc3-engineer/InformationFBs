"""Tc2_EtherCAT registry: name -> (section, type, category_subdir, infosys_topic_id).

The TOC parser only enumerates 7 entries (Ch.10 Conversion Functions).
This module hard-codes the full PDF body roster derived from `Tc2_EtherCAT.txt`
section headings (sections 3.x EtherCAT Commands, 4.x Diagnostic, 5.x State
Machine, 6.x ADS Interface, 7.x CoE, 8.x FoE, 9.x SoE, 10.x Conversion,
11.x Distributed Clocks, 12.x Obsolete Library Version, 13.x Data Types,
14.x Appendix) plus the InfoSys topic IDs harvested via WebSearch.

Notes
-----
* §1 (Foreword), §2 (Overview), §11.4 [obsolete] subtree, §13 (data types)
  and §14 (Appendix Global constants / library version / mailbox error codes)
  are NOT separate FB/FC docs — they are either headings or referenced DUTs
  whose definitions we surface inline in §2/§4 of each consuming doc.
  The only DUTs we expose as standalone reference docs are the GVL
  `Global_Version` and the obsolete `F_GetVersionTcEtherCAT` /
  `[obsolete]` Distributed-Clock helpers (they are real callable POUs).
"""

# (name, section, type, category_dir, infosys_topic_id_or_None)
CATALOG = [
    # ----------------------------------------------------------------- §3 Commands
    ("FB_EcPhysicalReadCmd",   "3.1", "FUNCTION_BLOCK", "commands", "57003787"),
    ("FB_EcPhysicalWriteCmd",  "3.2", "FUNCTION_BLOCK", "commands", "57005323"),
    ("FB_EcLogicalReadCmd",    "3.3", "FUNCTION_BLOCK", "commands", "57006859"),
    ("FB_EcLogicalWriteCmd",   "3.4", "FUNCTION_BLOCK", "commands", "57008395"),

    # ---------------------------------------------------------------- §4 Diagnostic
    ("FB_EcGetAllMasters",                     "4.1",  "FUNCTION_BLOCK", "diagnostic", "18716287371"),
    ("FB_EcGetAllSlaveAbnormalStateChanges",   "4.2",  "FUNCTION_BLOCK", "diagnostic", "2239479947"),
    ("FB_EcGetAllSlaveAddr",                   "4.3",  "FUNCTION_BLOCK", "diagnostic", "57011339"),
    ("FB_EcGetAllSlaveCrcErrors",              "4.4",  "FUNCTION_BLOCK", "diagnostic", "57012875"),
    ("FB_EcGetAllSlavePresentStateChanges",    "4.5",  "FUNCTION_BLOCK", "diagnostic", "2239481867"),
    ("FB_EcGetAllSyncUnitSlaveAddr",           "4.6",  "FUNCTION_BLOCK", "diagnostic", "15660862603"),
    ("FB_EcGetConfSlaves",                     "4.7",  "FUNCTION_BLOCK", "diagnostic", "57019019"),
    ("FB_EcGetLastProtErrInfo",                "4.8",  "FUNCTION_BLOCK", "diagnostic", "8538584971"),
    ("FB_EcGetMasterDevState",                 "4.9",  "FUNCTION_BLOCK", "diagnostic", "2895328139"),
    ("FB_EcGetScannedSlaves",                  "4.10", "FUNCTION_BLOCK", "diagnostic", "57020555"),
    ("FB_EcGetSlaveCount",                     "4.11", "FUNCTION_BLOCK", "diagnostic", "57015947"),
    ("FB_EcGetSlaveCrcError",                  "4.12", "FUNCTION_BLOCK", "diagnostic", "57014411"),
    ("FB_EcGetSlaveCrcErrorEx",                "4.13", "FUNCTION_BLOCK", "diagnostic", "2239483787"),
    ("FB_EcGetSlaveIdentity",                  "4.14", "FUNCTION_BLOCK", "diagnostic", "57017483"),
    ("FB_EcGetSlaveTopologyInfo",              "4.15", "FUNCTION_BLOCK", "diagnostic", "9007201494226699"),
    ("FB_EcMasterFrameCount",                  "4.16", "FUNCTION_BLOCK", "diagnostic", "2895330059"),
    ("FB_EcMasterFrameStatistic",              "4.17", "FUNCTION_BLOCK", "diagnostic", "57053835"),
    ("FB_EcMasterFrameStatisticClearCRC",      "4.18", "FUNCTION_BLOCK", "diagnostic", "57055371"),
    ("FB_EcMasterFrameStatisticClearFrames",   "4.19", "FUNCTION_BLOCK", "diagnostic", "57056907"),
    ("FB_EcMasterFrameStatisticClearTxRxErr",  "4.20", "FUNCTION_BLOCK", "diagnostic", "57058443"),
    ("FB_EcMasterObjectID",                    "4.21", "FUNCTION_BLOCK", "diagnostic", "20212712843"),
    ("F_CheckVendorId",                        "4.22", "FUNCTION",       "diagnostic", "57096587"),
    ("F_EcGetLinkedTaskOfSyncUnit",            "4.23", "FUNCTION",       "diagnostic", "11328546443"),
    ("F_EcGetSyncUnitName",                    "4.24", "FUNCTION",       "diagnostic", "14455123595"),
    ("F_EcGetMailboxGatewayAddr",              "4.25", "FUNCTION",       "diagnostic", "20498780427"),

    # ------------------------------------------------------------- §5 State Machine
    ("FB_EcGetAllSlaveStates",   "5.1", "FUNCTION_BLOCK", "state_machine", "57029643"),
    ("FB_EcGetMasterState",      "5.2", "FUNCTION_BLOCK", "state_machine", "9007199311767563"),
    ("FB_EcGetSlaveState",       "5.3", "FUNCTION_BLOCK", "state_machine", "57028107"),
    ("FB_EcReqMasterState",      "5.4", "FUNCTION_BLOCK", "state_machine", "57032715"),
    ("FB_EcReqSlaveState",       "5.5", "FUNCTION_BLOCK", "state_machine", "57031179"),
    ("FB_EcSetMasterState",      "5.6", "FUNCTION_BLOCK", "state_machine", "57035787"),
    ("FB_EcSetSlaveState",       "5.7", "FUNCTION_BLOCK", "state_machine", "57034251"),

    # ------------------------------------------------------------------ §6 ADS Interface
    ("FB_EcReadBIC",  "6.1", "FUNCTION_BLOCK", "ads", "11531168267"),
    ("FB_EcReadBTN",  "6.2", "FUNCTION_BLOCK", "ads", "11531169803"),

    # ------------------------------------------------------------------ §7 CoE interface
    ("FB_EcCoeSdoRead",       "7.1", "FUNCTION_BLOCK", "coe", "56996235"),
    ("FB_EcCoeSdoReadEx",     "7.2", "FUNCTION_BLOCK", "coe", "56997771"),
    ("FB_EcCoeSdoWrite",      "7.3", "FUNCTION_BLOCK", "coe", "56999307"),
    ("FB_EcCoeSdoWriteEx",    "7.4", "FUNCTION_BLOCK", "coe", "57000843"),
    ("FB_CoERead_ByDriveRef", "7.5", "FUNCTION_BLOCK", "coe", "2217655179"),
    ("FB_CoEWrite_ByDriveRef","7.6", "FUNCTION_BLOCK", "coe", "2217657099"),
    ("FB_EcCoeReadBIC",       "7.7", "FUNCTION_BLOCK", "coe", "11531165195"),
    ("FB_EcCoeReadBTN",       "7.8", "FUNCTION_BLOCK", "coe", "11531166731"),
    ("FB_EcCoESdoAbortCode",  "7.9", "FUNCTION_BLOCK", "coe", "19126799883"),

    # ------------------------------------------------------------------ §8 FoE interface
    ("FB_EcFoeAccess",    "8.1", "FUNCTION_BLOCK", "foe", "57038731"),
    ("FB_EcFoeClose",     "8.2", "FUNCTION_BLOCK", "foe", "57040267"),
    ("FB_EcFoeLoad",      "8.3", "FUNCTION_BLOCK", "foe", "57041803"),
    ("FB_EcFoeOpen",      "8.4", "FUNCTION_BLOCK", "foe", "57043339"),
    ("FB_EcFoeReadFile",  "8.5", "FUNCTION_BLOCK", "foe", "9859439755"),
    ("FB_EcFoeWriteFile", "8.6", "FUNCTION_BLOCK", "foe", "16248044683"),

    # ------------------------------------------------------------------ §9 SoE interface
    ("FB_EcSoeRead",          "9.1", "FUNCTION_BLOCK", "soe", "57046283"),
    ("FB_EcSoeWrite",         "9.2", "FUNCTION_BLOCK", "soe", "57047819"),
    ("FB_SoERead_ByDriveRef", "9.3", "FUNCTION_BLOCK", "soe", "57049355"),
    ("FB_SoEWrite_ByDriveRef","9.4", "FUNCTION_BLOCK", "soe", "57050891"),

    # --------------------------------------------------------- §10 Conversion Functions
    ("F_ConvBK1120CouplerStateToString", "10.1", "FUNCTION", "conversion", "57073675"),
    ("F_ConvMasterDevStateToString",     "10.2", "FUNCTION", "conversion", "57075211"),
    ("F_ConvProductCodeToString",        "10.3", "FUNCTION", "conversion", "57076747"),
    ("F_ConvSlaveStateToString",         "10.4", "FUNCTION", "conversion", "57078283"),
    ("F_ConvSlaveStateToBits",           "10.5", "FUNCTION", "conversion", "57079819"),
    ("F_ConvSlaveStateToBitsEx",         "10.6", "FUNCTION", "conversion", "2239485707"),
    ("F_ConvStateToString",              "10.7", "FUNCTION", "conversion", "57081355"),

    # ------------------------------------------------------------- §11 Distributed Clocks
    # §11.1 DCTIME32
    ("ConvertDcTimeToPos",     "11.1.1", "FUNCTION_BLOCK", "distributed_clocks", "57090443"),
    ("ConvertPosToDcTime",     "11.1.2", "FUNCTION_BLOCK", "distributed_clocks", "57091979"),
    ("ConvertDcTimeToPathPos", "11.1.3", "FUNCTION_BLOCK", "distributed_clocks", "57093515"),
    ("ConvertPathPosToDcTime", "11.1.4", "FUNCTION_BLOCK", "distributed_clocks", "57095051"),
    # §11.2 DCTIME64
    ("DCTIME_TO_DCTIME64",        "11.2.1",  "FUNCTION",       "distributed_clocks", "2267334667"),
    ("DCTIME64_TO_DCTIME",        "11.2.2",  "FUNCTION",       "distributed_clocks", "9007201522077579"),
    ("DCTIME64_TO_DCTIMESTRUCT",  "11.2.3",  "FUNCTION",       "distributed_clocks", "2267402507"),
    ("DCTIME64_TO_FILETIME64",    "11.2.4",  "FUNCTION",       "distributed_clocks", "10501992459"),
    ("DCTIME64_TO_STRING",        "11.2.5",  "FUNCTION",       "distributed_clocks", "2267406347"),
    ("DCTIME64_TO_SYSTEMTIME",    "11.2.6",  "FUNCTION",       "distributed_clocks", "9007201522622475"),
    ("DCTIMESTRUCT_TO_DCTIME64",  "11.2.7",  "FUNCTION",       "distributed_clocks", "2267410187"),
    ("FILETIME64_TO_DCTIME64",    "11.2.8",  "FUNCTION",       "distributed_clocks", "10501953035"),
    ("STRING_TO_DCTIME64",        "11.2.9",  "FUNCTION",       "distributed_clocks", "2267414027"),
    ("SYSTEMTIME_TO_DCTIME64",    "11.2.10", "FUNCTION",       "distributed_clocks", "9007201522159243"),
    ("FB_EcDcTimeCtrl64",         "11.2.11", "FUNCTION_BLOCK", "distributed_clocks", "2267412107"),
    # §11.3 DCTIME64 and ULINT
    ("F_ConvExtTimeToDcTime64",   "11.3.1", "FUNCTION",       "distributed_clocks", "2285556107"),
    ("F_ConvTcTimeToDcTime64",    "11.3.2", "FUNCTION",       "distributed_clocks", "2285558027"),
    ("F_ConvTcTimeToExtTime64",   "11.3.3", "FUNCTION",       "distributed_clocks", "2285559947"),
    ("F_GetActualDcTime64",       "11.3.4", "FUNCTION",       "distributed_clocks", "2268416395"),
    ("F_GetCurDcTaskTime64",      "11.3.5", "FUNCTION",       "distributed_clocks", "2268414091"),
    ("F_GetCurDcTickTime64",      "11.3.6", "FUNCTION",       "distributed_clocks", "9007201522348427"),
    ("F_GetCurExtTime64",         "11.3.7", "FUNCTION",       "distributed_clocks", "9007201522405771"),
    ("FB_EcExtSyncCalcTimeDiff64","11.3.8", "FUNCTION_BLOCK", "distributed_clocks", "2285561867"),
    ("FB_EcExtSyncCheck64",       "11.3.9", "FUNCTION_BLOCK", "distributed_clocks", "2285554187"),

    # ------------------------------------------------------------- §11.4 [obsolete] DC helpers
    ("DCTIME_TO_DCTIMESTRUCT",  "11.4.1.1", "FUNCTION",       "obsolete", "57065995"),
    ("DCTIME_TO_FILETIME",      "11.4.1.2", "FUNCTION",       "obsolete", "57064459"),
    ("DCTIME_TO_STRING",        "11.4.1.3", "FUNCTION",       "obsolete", "57068011"),
    ("DCTIME_TO_SYSTEMTIME",    "11.4.1.4", "FUNCTION",       "obsolete", "57069547"),
    ("DCTIMESTRUCT_TO_DCTIME",  "11.4.1.5", "FUNCTION",       "obsolete", "57062923"),
    ("FILETIME_TO_DCTIME",      "11.4.1.6", "FUNCTION",       "obsolete", "57071083"),
    ("STRING_TO_DCTIME",        "11.4.1.7", "FUNCTION",       "obsolete", "57072619"),
    ("SYSTEMTIME_TO_DCTIME",    "11.4.1.8", "FUNCTION",       "obsolete", "57070603"),
    ("FB_EcDcTimeCtrl",         "11.4.1.9", "FUNCTION_BLOCK", "obsolete", "57084427"),
    ("F_ConvExtTimeToDcTime",   "11.4.2.1", "FUNCTION",       "obsolete", "2285533707"),
    ("F_ConvTcTimeToDcTime",    "11.4.2.2", "FUNCTION",       "obsolete", "2285531787"),
    ("F_ConvTcTimeToExtTime",   "11.4.2.3", "FUNCTION",       "obsolete", "2285529867"),
    ("F_GetActualDcTime",       "11.4.2.4", "FUNCTION",       "obsolete", "57088907"),
    ("F_GetCurDcTaskTime",      "11.4.2.5", "FUNCTION",       "obsolete", "57086475"),
    ("F_GetCurDcTickTime",      "11.4.2.6", "FUNCTION",       "obsolete", "57085963"),
    ("F_GetCurExtTime",         "11.4.2.7", "FUNCTION",       "obsolete", "2285085707"),
    ("FB_EcExtSyncCalcTimeDiff","11.4.2.8", "FUNCTION_BLOCK", "obsolete", "2285535627"),
    ("FB_EcExtSyncCheck",       "11.4.2.9", "FUNCTION_BLOCK", "obsolete", "2285537547"),
    ("DCTIME64_TO_FILETIME",    "11.4.3",   "FUNCTION",       "obsolete", "2267404427"),
    ("FILETIME_TO_DCTIME64",    "11.4.4",   "FUNCTION",       "obsolete", "10501950219"),
    ("F_GetVersionTcEtherCAT",  "12.1",     "FUNCTION",       "obsolete", "57099531"),
]


def by_name(n):
    for entry in CATALOG:
        if entry[0] == n:
            return entry
    return None


def all_names():
    return [e[0] for e in CATALOG]
