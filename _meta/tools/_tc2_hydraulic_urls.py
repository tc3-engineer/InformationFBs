"""Topic URL map for Tc2_Hydraulic FBs (TF5810).

The base URL is https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/
Each value is the topic id .html portion.

Only entries that this library agent decided to ship are listed.
"""

BASE = "https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/"

TOPICS = {
    # Administrative
    "MC_Power_BkPlcMc": "1599672203.html",
    "MC_ReadActualPosition_BkPlcMc": "1599673227.html",
    "MC_ReadActualTorque_BkPlcMc": "1599674251.html",
    "MC_ReadActualVelocity_BkPlcMc": "1599675275.html",
    "MC_ReadAxisError_BkPlcMc": "1599676299.html",
    "MC_ReadStatus_BkPlcMc": "1599680395.html",
    "MC_Reset_BkPlcMc": "1599681419.html",
    "MC_ResetAndStop_BkPlcMc": "1599682443.html",
    "MC_SetOverride_BkPlcMc": "1599683467.html",
    "MC_SetPosition_BkPlcMc": "1599684491.html",
    "MC_SetReferenceFlag_BkPlcMc": "1599685515.html",
    # Motion single axis
    "MC_MoveAbsolute_BkPlcMc": "1599701771.html",
    "MC_MoveRelative_BkPlcMc": "1599703819.html",
    "MC_MoveVelocity_BkPlcMc": "1599704843.html",
    "MC_MoveJoySticked_BkPlcMc": "1599702795.html",
    "MC_Halt_BkPlcMc": "1599698699.html",
    "MC_Stop_BkPlcMc": "1599705867.html",
    "MC_RampedStop_BkPlcMc": "9073620363.html",
    "MC_EmergencyStop_BkPlcMc": "1599694603.html",
    "MC_ImediateStop_BkPlcMc": "1599700747.html",
    # Multi axis
    "MC_GearIn_BkPlcMc": "1599695627.html",
    "MC_GearInPos_BkPlcMc": "1599696651.html",
    "MC_GearOut_BkPlcMc": "1599697675.html",
    "MC_CamIn_BkPlcMc": "1599690507.html",
    "MC_CamOut_BkPlcMc": "1599691531.html",
    # Homing
    "MC_Home_BkPlcMc": "1599699723.html",
    # Hydraulic-specific controllers
    "MC_AxCtrlPressure_BkPlcMc": "1599750027.html",
    "MC_AxCtrlSlowDownOnPressure_BkPlcMc": "1599751051.html",
    "MC_AxCtrlAutoZero_BkPlcMc": "1599749003.html",
    # Pressure / Force sensing
    "MC_AxRtReadPressureSingle_BkPlcMc": "1599760011.html",
    "MC_AxRtReadPressureDiff_BkPlcMc": "1599758987.html",
    "MC_AxRtReadForceSingle_BkPlcMc": "1599757963.html",
    "MC_AxRtReadForceDiff_BkPlcMc": "1599756939.html",
}

def url(name: str) -> str:
    return BASE + TOPICS[name]
