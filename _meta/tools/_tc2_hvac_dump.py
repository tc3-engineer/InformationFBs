#!/usr/bin/env python3
"""Dump VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT blocks for each known section.

Produces a JSON file at _meta/.pdf-cache/Tc2_HVAC.vars.json mapping section
number -> {name, var_input, var_output, var_in_out, brief_text}.

NOT cached PDF; sidecar JSON kept in cache dir for convenience (will be
gitignored as it sits beside cache files).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta/tools"))
from _tc2_hvac_helpers import extract_section, extract_var_blocks, parse_decls

# All known section -> (name, category_dir, type_label)
ENTRIES_TOC: list[tuple[str, str, str, str]] = [
    # actuators
    ("5.1.2.1", "FB_HVAC2PointActuator", "actuators", "FUNCTION_BLOCK"),
    ("5.1.2.2", "FB_HVAC3PointActuator", "actuators", "FUNCTION_BLOCK"),
    ("5.1.2.3", "FB_HVACCirculationPump", "actuators", "FUNCTION_BLOCK"),
    ("5.1.2.4", "FB_HVACCirculationPumpEx", "actuators", "FUNCTION_BLOCK"),
    ("5.1.2.5", "FB_HVACMotor1Speed", "actuators", "FUNCTION_BLOCK"),
    ("5.1.2.6", "FB_HVACMotor2Speed", "actuators", "FUNCTION_BLOCK"),
    ("5.1.2.7", "FB_HVACMotor3Speed", "actuators", "FUNCTION_BLOCK"),
    ("5.1.2.8", "FB_HVACMux8", "actuators", "FUNCTION_BLOCK"),
    ("5.1.2.9", "FB_HVACMux8Ex", "actuators", "FUNCTION_BLOCK"),
    ("5.1.2.10", "FB_HVACMux8_BOOL", "actuators", "FUNCTION_BLOCK"),
    ("5.1.2.11", "FB_HVACRedundancyCtrl", "actuators", "FUNCTION_BLOCK"),
    ("5.1.2.12", "FB_HVACRedundancyCtrlEx", "actuators", "FUNCTION_BLOCK"),
    # analog modules
    ("5.1.3.1", "FB_HVACAnalogInput", "analog_modules", "FUNCTION_BLOCK"),
    ("5.1.3.2", "FB_HVACAnalogOutput", "analog_modules", "FUNCTION_BLOCK"),
    ("5.1.3.3", "FB_HVACAnalogOutputEx", "analog_modules", "FUNCTION_BLOCK"),
    ("5.1.3.3", "FB_HVACAnalogOutputEx2", "analog_modules", "FUNCTION_BLOCK"),
    ("5.1.3.4", "FB_HVACAnalogTo3Point", "analog_modules", "FUNCTION_BLOCK"),
    ("5.1.3.5", "FB_HVACConfigureKL32xx", "analog_modules", "FUNCTION_BLOCK"),
    ("5.1.3.6", "FB_HVACScale", "analog_modules", "FUNCTION_BLOCK"),
    ("5.1.3.7", "FB_HVACScale_nPoint", "analog_modules", "FUNCTION_BLOCK"),
    ("5.1.3.8", "FB_HVACScaleXX", "analog_modules", "FUNCTION_BLOCK"),
    ("5.1.3.9", "FB_HVACTemperatureCurve", "analog_modules", "FUNCTION_BLOCK"),
    ("5.1.3.10", "FB_HVACTemperatureSensor", "analog_modules", "FUNCTION_BLOCK"),
    ("5.1.3.11", "FB_HVACTemperatureSensorEx", "analog_modules", "FUNCTION_BLOCK"),
    ("5.1.3.12", "FB_HVACTemperatureSensorEx2", "analog_modules", "FUNCTION_BLOCK"),
    # controllers
    ("5.1.4.1", "FB_HVAC2PointCtrl", "controllers", "FUNCTION_BLOCK"),
    ("5.1.4.2", "FB_HVACI_CtrlStep", "controllers", "FUNCTION_BLOCK"),
    ("5.1.4.3", "FB_HVACI_CtrlStepEx", "controllers", "FUNCTION_BLOCK"),
    ("5.1.4.4", "FB_HVACPIDCtrl", "controllers", "FUNCTION_BLOCK"),
    ("5.1.4.5", "FB_HVACPIDCtrl_Ex", "controllers", "FUNCTION_BLOCK"),
    ("5.1.4.6", "FB_HVACPowerRangeTable", "controllers", "FUNCTION_BLOCK"),
    # sequence controllers
    ("5.1.4.7.1", "FB_HVAC2PointCtrlSequence", "sequence_controllers", "FUNCTION_BLOCK"),
    ("5.1.4.7.2", "FB_HVACBasicSequenceCtrl", "sequence_controllers", "FUNCTION_BLOCK"),
    ("5.1.4.7.3", "FB_HVACMasterSequenceCtrl", "sequence_controllers", "FUNCTION_BLOCK"),
    ("5.1.4.7.4", "FB_HVACPIDCooling", "sequence_controllers", "FUNCTION_BLOCK"),
    ("5.1.4.7.5", "FB_HVACPIDDehumidify", "sequence_controllers", "FUNCTION_BLOCK"),
    ("5.1.4.7.6", "FB_HVACPIDEnergyRecovery", "sequence_controllers", "FUNCTION_BLOCK"),
    ("5.1.4.7.7", "FB_HVACPIDHumidify", "sequence_controllers", "FUNCTION_BLOCK"),
    ("5.1.4.7.8", "FB_HVACPIDMixedAir", "sequence_controllers", "FUNCTION_BLOCK"),
    ("5.1.4.7.9", "FB_HVACPIDPreHeating", "sequence_controllers", "FUNCTION_BLOCK"),
    ("5.1.4.7.10", "FB_HVACPIDReHeating", "sequence_controllers", "FUNCTION_BLOCK"),
    # room air conditioning
    ("5.1.5.1.1", "FB_BAREnergyLevel", "room_air_conditioning", "FUNCTION_BLOCK"),
    ("5.1.5.1.2", "FB_BARFanCoil", "room_air_conditioning", "FUNCTION_BLOCK"),
    ("5.1.5.1.3", "FB_BARFctSelection", "room_air_conditioning", "FUNCTION_BLOCK"),
    ("5.1.5.1.4", "FB_BARSetpointRoom", "room_air_conditioning", "FUNCTION_BLOCK"),
    # room controller
    ("5.1.5.2.1", "FB_BARPICtrl", "room_controller", "FUNCTION_BLOCK"),
    # room lighting
    ("5.1.5.3.1", "FB_BARAutomaticLight", "room_lighting", "FUNCTION_BLOCK"),
    ("5.1.5.3.2", "FB_BARConstantLightControl", "room_lighting", "FUNCTION_BLOCK"),
    ("5.1.5.3.3", "FB_BARDaylightControl", "room_lighting", "FUNCTION_BLOCK"),
    ("5.1.5.3.4", "FB_BARLightActuator", "room_lighting", "FUNCTION_BLOCK"),
    ("5.1.5.3.5", "FB_BARLightCircuit", "room_lighting", "FUNCTION_BLOCK"),
    ("5.1.5.3.6", "FB_BARLightCircuitDim", "room_lighting", "FUNCTION_BLOCK"),
    ("5.1.5.3.7", "FB_BARStairwellAutomatic", "room_lighting", "FUNCTION_BLOCK"),
    ("5.1.5.3.8", "FB_BARTwilightAutomatic", "room_lighting", "FUNCTION_BLOCK"),
    # room sun protection
    ("5.1.5.4.5", "FB_BARBlindPositionEntry", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.6", "FB_BARDelayedHysteresis", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.7", "FB_BARFacadeElementEntry", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.8", "FB_BARReadFacadeElementList", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.9", "FB_BARReadShadingObjectsList", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.10", "FB_BARShadingCorrection", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.11", "FB_BARShadingCorrectionSouth", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.12", "FB_BARShadingObjectsEntry", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.13", "FB_BARSunblindActuator", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.14", "FB_BARSunblindActuatorEx", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.15", "FB_BARSunblindEvent", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.16", "FB_BARSunblindPrioritySwitch", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.17", "FB_BARRollerBlind", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.18", "FB_BARSunblindScene", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.19", "FB_BARSunblindSwitch", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.20", "FB_BARSunblindThermoAutomatic", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.21", "FB_BARSunblindTwilightAutomatic", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.22", "FB_BARSunblindWeatherProtection", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.23", "FB_BARSunProtectionEx", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.24", "FB_BARWithinRangeAzimuth", "room_sun_protection", "FUNCTION_BLOCK"),
    ("5.1.5.4.25", "FB_BARWithinRangeElevation", "room_sun_protection", "FUNCTION_BLOCK"),
    # setpoint modules
    ("5.1.6.1", "FB_HVACHeatingCurve", "setpoint_modules", "FUNCTION_BLOCK"),
    ("5.1.6.2", "FB_HVACHeatingCurveEx", "setpoint_modules", "FUNCTION_BLOCK"),
    ("5.1.6.3", "FB_HVACOutsideTempDamped", "setpoint_modules", "FUNCTION_BLOCK"),
    ("5.1.6.4", "FB_HVACSetpointHeating", "setpoint_modules", "FUNCTION_BLOCK"),
    ("5.1.6.5", "FB_HVACSetpointRamp", "setpoint_modules", "FUNCTION_BLOCK"),
    ("5.1.6.6", "FB_HVACSummerCompensation", "setpoint_modules", "FUNCTION_BLOCK"),
    # special functions
    ("5.1.7.1", "FB_HVACAirConditioning2Speed", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.2", "FB_HVACAlarm", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.3", "FB_HVACAntiBlockingDamper", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.4", "FB_HVACAntiBlockingPump", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.5", "FB_HVACBlink", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.6", "FB_HVACCmdCtrl_8", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.7", "FB_HVACCmdCtrlSystem1Stage", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.8", "FB_HVACCmdCtrlSystem2Stage", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.9", "FB_HVACConvertEnum", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.10", "FB_HVACEnthalpy", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.11", "FB_HVACFixedLimit", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.12", "FB_HVACFreezeProtectionHeater", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.13", "FB_HVACMUX_INT_8", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.14", "FB_HVACMUX_INT_16", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.15", "FB_HVACMUX_REAL_8", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.16", "FB_HVACMUX_REAL_16", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.17", "FB_HVACOverwriteAnalog", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.18", "FB_HVACOverwriteDigital", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.19", "FB_HVACPowerMeasurementKL3403", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.20", "FB_HVACPowerMeasurementKL3403Ex", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.21", "FB_HVACPriority_INT_8", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.22", "FB_HVACPriority_INT_16", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.23", "FB_HVACPriority_REAL_8", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.24", "FB_HVACPriority_REAL_16", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.25", "FB_HVACOptimizedOn", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.26", "FB_HVACOptimizedOff", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.27", "FB_HVACTempChangeFunction", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.28", "FB_HVACPWM", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.29", "FB_HVACStartAirConditioning", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.30", "FB_HVACSummerNightCooling", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.31", "FB_HVACSummerNightCoolingEx", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.32", "FB_HVACTimeCon", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.33", "FB_HVACTimeConSec", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.34", "FB_HVACTimeConSecMs", "special_functions", "FUNCTION_BLOCK"),
    ("5.1.7.35", "FB_HVACWork", "special_functions", "FUNCTION_BLOCK"),
    # scheduler
    ("5.1.8.1", "FB_HVACScheduler1ch", "scheduler", "FUNCTION_BLOCK"),
    ("5.1.8.2", "FB_HVACScheduler7ch", "scheduler", "FUNCTION_BLOCK"),
    ("5.1.8.3", "FB_HVACScheduler7TCHandling", "scheduler", "FUNCTION_BLOCK"),
    ("5.1.8.4", "FB_HVACScheduler28ch", "scheduler", "FUNCTION_BLOCK"),
    ("5.1.8.5", "FB_HVACScheduler28TCHandling", "scheduler", "FUNCTION_BLOCK"),
    ("5.1.8.6", "FB_HVACSchedulerPublicHolidays", "scheduler", "FUNCTION_BLOCK"),
    ("5.1.8.7", "FB_HVACSchedulerSpecialPeriods", "scheduler", "FUNCTION_BLOCK"),
    # system
    ("5.1.9.1", "FB_HVACGetSystemTime", "system", "FUNCTION_BLOCK"),
    ("5.1.9.2", "FB_HVACNOVRAMDataHandling", "system", "FUNCTION_BLOCK"),
    ("5.1.9.3", "FB_HVACPersistentDataHandling", "system", "FUNCTION_BLOCK"),
    ("5.1.9.4", "FB_HVACPersistentDataFileCopy", "system", "FUNCTION_BLOCK"),
    ("5.1.9.5", "FB_HVACSetLocalTime", "system", "FUNCTION_BLOCK"),
    ("5.1.9.6", "FB_HVACSystemTaskInfo", "system", "FUNCTION_BLOCK"),
    # backup_var
    ("5.1.10.1", "FB_HVACNOVRAM_XX", "backup_var", "FUNCTION_BLOCK"),
    ("5.1.10.2", "FB_HVACPersistent_XX", "backup_var", "FUNCTION_BLOCK"),
    # functions
    ("5.1.11.1", "F_RoundLREAL", "functions", "FUNCTION"),
    ("5.1.11.2", "F_RoundLREAL_EX", "functions", "FUNCTION"),
]


def main() -> int:
    out: dict[str, dict] = {}
    for sec, name, cat, type_label in ENTRIES_TOC:
        try:
            txt = extract_section(sec)
        except SystemExit as e:
            print(f"WARN  cannot extract {sec} {name}: {e}", file=sys.stderr)
            continue
        if not txt:
            print(f"WARN  empty extract {sec} {name}", file=sys.stderr)
            continue
        blocks = extract_var_blocks(txt)
        out[name] = {
            "section": sec,
            "category_dir": cat,
            "type_label": type_label,
            "var_input": blocks["VAR_INPUT"],
            "var_output": blocks["VAR_OUTPUT"],
            "var_in_out": blocks["VAR_IN_OUT"],
            "raw": txt,
        }
        if sys.stdout.isatty():
            print(f"  {name}  ({sec})  in:{len(parse_decls(blocks['VAR_INPUT']))}  out:{len(parse_decls(blocks['VAR_OUTPUT']))}  io:{len(parse_decls(blocks['VAR_IN_OUT']))}")
    out_path = ROOT / "_meta/.pdf-cache/Tc2_HVAC.vars.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"wrote {out_path.relative_to(ROOT)} with {len(out)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
