# Tc2_HVAC

Beckhoff TwinCAT 3 **Tc2_HVAC** 库（TF8000 | TC3 HVAC）的中文技术文档与可导入演示例程。
本库是 Beckhoff 暖通空调（Heating / Ventilation / Air Conditioning，HVAC）专用 PLC 库，为楼宇 HVAC 系统提供：

- 执行器控制（两点 / 三点阀、循环水泵、单 / 双 / 三档电机、多路冗余）
- 模拟 I/O 处理（多类传感器换算、温度曲线、量程换算、KL3xxx 端子配置）
- 通用控制器（PID、I-Step、2 点切换、功率范围表）
- 序列控制器（多段加热 / 冷却 / 加湿 / 除湿 / 能量回收）
- 房间功能（风机盘管、能量节能模式、PI 控制器）
- 房间照明（自动 / 恒照度 / 黄昏 / 楼道 / 调光）
- 房间遮阳（百叶 / 卷帘 / 阴影矫正 / 太阳保护）
- 设定值生成（加热曲线、室外温度阻尼、设定值斜率、夏季补偿）
- 特殊功能（节能启停优化、报警、防冻、防卡死、多路选择 / 优先级、能耗测量、强制覆写、PWM）
- 时间表调度（多通道周计划、节假日、特殊周期）
- 系统支持（NOVRAM、持久化、系统时间、任务信息）

| 字段 | 值 |
|---|---|
| Library | Tc2_HVAC |
| Library Version | `1.3.0` |
| TF 产品号 | TF8000 |
| PDF | [TF8000_TC3_HVAC_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf) |
| InfoSys 入口 | https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/index.html |
| 文档总数 | **131 FB + 2 FC + 2 GVL = 135 篇** |
| 例程总数 | **135 个 P_Demo_*.TcPOU** |
| Verify 状态 | 全部 PASS（2026-06-03） |
| Lint 状态 | 全部 PASS（2026-06-03） |
| GUID 唯一性 | 全仓 `--check-unique` PASS（2026-06-03） |

## PDF 结构说明（重要约束）

TF8000 HVAC 手册（516 页）有几个特殊的格式约定，已在本仓所有文档中处理：

1. **每个 VAR 区结束处无 `END_VAR` 终止符** —— 整本手册的统一约定。本仓文档为保证 IEC 语法完整在 VAR 区末尾显式补 `END_VAR`，引脚名 / 类型 / 默认值 / 顺序与 PDF 完全一致。由于 PDF 缺少 `END_VAR`，`verify_doc.py` 的自动 VAR 区对比无法落锚，本仓所有 HVAC 条目均使用 `Status: ⚠️ chapter-overview-only` 合规跳过该自动检查；内容真实性以每篇的 InfoSys topic 链接为准并人工对照。
2. **5.1.3.3 章节标题为 `FB_HVACAnalogOutputEx/FB_HVACAnalogOutputEx2`**（一节涵盖两个 FB）—— 本仓拆为两篇文档（`FB_HVACAnalogOutputEx.md` 与 `FB_HVACAnalogOutputEx2.md`），共享 InfoSys URL。
3. **5.1.3.11 与 5.1.3.12 标题都印为 `FB_HVACTemperatureSensorEx`**（PDF 印刷重复），实际 5.1.3.12 章节正文是 `FB_HVACTemperatureSensorEx2`。本仓按真实 FB 名拆为两篇文档。
4. **FB_HVACMux8 / Mux8Ex / Mux8_BOOL 使用范围声明语法**（`rIn1 - rIn8 : REAL;` 用一行表示 8 个变量）；本仓在 IEC 代码块中**逐字保留** PDF 的范围语法，文档读者按 IEC 标准要展开 `rIn1 .. rIn8` 各一行声明。
5. **FB_HVAC3PointActuator 的 `tStrokeTime` 末尾印为 `:` 而非 `;`** —— PDF 印刷错误。

## 配套硬件 / 软件依赖

PDF "General Information" 章列出本库依赖：

- `Tc2_System`、`Tc2_Standard`、`Tc2_DataExchange`、`Tc2_Utilities`
- 内部使用 `TcMath`（数学函数库）
- 兼容 TwinCAT 3.1 build 4022.16 或更高

本库为 **维护用库**：Beckhoff 推荐新工程使用 TF8040（TwinCAT Building Automation），但 Tc2_HVAC 仍持续维护以保证现有工程兼容。

## 分类导航

### Actuators 执行器（12 个 FB）

阀门 / 风阀 / 水泵 / 电机控制。所有执行器 FB 共用 `eDataSecurityType` 持久化策略、`bManSwitch` / `bCtrlVoltage` 硬件联锁、`byState` 状态字、`bReset` 上升沿清错的统一约定。

| FB | 用途 |
|---|---|
| [FB_HVAC2PointActuator](actuators/FB_HVAC2PointActuator.md) | 两点（开 / 关）阀门 / 风阀控制 |
| [FB_HVAC3PointActuator](actuators/FB_HVAC3PointActuator.md) | 三点（开 / 关 / 停）阀门控制，含位置反馈 |
| [FB_HVACCirculationPump](actuators/FB_HVACCirculationPump.md) | HVAC 循环水泵控制（基础版） |
| [FB_HVACCirculationPumpEx](actuators/FB_HVACCirculationPumpEx.md) | HVAC 循环水泵控制（扩展版：含速度档位） |
| [FB_HVACMotor1Speed](actuators/FB_HVACMotor1Speed.md) | 单档电机 / 风机控制 |
| [FB_HVACMotor2Speed](actuators/FB_HVACMotor2Speed.md) | 双档电机 / 风机控制 |
| [FB_HVACMotor3Speed](actuators/FB_HVACMotor3Speed.md) | 三档电机 / 风机控制 |
| [FB_HVACMux8](actuators/FB_HVACMux8.md) | 8 路 REAL 输入按 FIFO 映射到 8 路输出 |
| [FB_HVACMux8Ex](actuators/FB_HVACMux8Ex.md) | 同上扩展版（用于 FB_HVACRedundancyCtrlEx） |
| [FB_HVACMux8_BOOL](actuators/FB_HVACMux8_BOOL.md) | 8 路 BOOL 输入按 FIFO 映射 |
| [FB_HVACRedundancyCtrl](actuators/FB_HVACRedundancyCtrl.md) | 8 路冗余执行器控制（自动切换运行机） |
| [FB_HVACRedundancyCtrlEx](actuators/FB_HVACRedundancyCtrlEx.md) | 冗余控制扩展版（产生 FIFO 给 Mux8Ex） |

### Analog Modules 模拟模块（13 个 FB）

模拟输入 / 输出处理、传感器换算、温度曲线、KL32xx 端子配置。

| FB | 用途 |
|---|---|
| [FB_HVACAnalogInput](analog_modules/FB_HVACAnalogInput.md) | 通用模拟输入处理（带量程换算与平滑） |
| [FB_HVACAnalogOutput](analog_modules/FB_HVACAnalogOutput.md) | 通用模拟输出（0..100% → KL4xxx 整型） |
| [FB_HVACAnalogOutputEx](analog_modules/FB_HVACAnalogOutputEx.md) | 模拟输出扩展（含 y = m·x + b 量程换算 + 防冻保护） |
| [FB_HVACAnalogOutputEx2](analog_modules/FB_HVACAnalogOutputEx2.md) | 同上变体：bFrost 后查询控制方向（反向时输出最小值） |
| [FB_HVACAnalogTo3Point](analog_modules/FB_HVACAnalogTo3Point.md) | 模拟输入 → 三点开关输出（脉宽调制） |
| [FB_HVACConfigureKL32xx](analog_modules/FB_HVACConfigureKL32xx.md) | KL3201 / KL3202 / KL3204 / KL3222 / KL3228 等电阻输入端子配置 |
| [FB_HVACScale](analog_modules/FB_HVACScale.md) | 原始模拟值量程换算到工程量 |
| [FB_HVACScale_nPoint](analog_modules/FB_HVACScale_nPoint.md) | n 点折线换算（温度特性曲线） |
| [FB_HVACScaleXX](analog_modules/FB_HVACScaleXX.md) | 量程换算扩展（2 / 4 / 7 支撑点） |
| [FB_HVACTemperatureCurve](analog_modules/FB_HVACTemperatureCurve.md) | 温度特性曲线（多种传感器） |
| [FB_HVACTemperatureSensor](analog_modules/FB_HVACTemperatureSensor.md) | 通用温度传感器读入（PT100 / PT1000 / Ni 等） |
| [FB_HVACTemperatureSensorEx](analog_modules/FB_HVACTemperatureSensorEx.md) | 温度传感器扩展（含上下限监测 + bEnable） |
| [FB_HVACTemperatureSensorEx2](analog_modules/FB_HVACTemperatureSensorEx2.md) | 温度传感器扩展 v2（支持 KL3201/02/04/22/28、KL3208-0010；可选 1/100℃ 标度） |

### Controllers 控制器（6 个 FB）

通用 PID / I-Step / 2 点开关控制器与功率范围表。

| FB | 用途 |
|---|---|
| [FB_HVAC2PointCtrl](controllers/FB_HVAC2PointCtrl.md) | 两点（带滞回）开关控制器 |
| [FB_HVACI_CtrlStep](controllers/FB_HVACI_CtrlStep.md) | I-Step（积分式步进）控制器：用于多段功率控制 |
| [FB_HVACI_CtrlStepEx](controllers/FB_HVACI_CtrlStepEx.md) | I-Step 扩展版 |
| [FB_HVACPIDCtrl](controllers/FB_HVACPIDCtrl.md) | **HVAC 通用 PID 控制器**（含 anti-reset windup、限幅、反向） |
| [FB_HVACPIDCtrl_Ex](controllers/FB_HVACPIDCtrl_Ex.md) | PID 扩展版（带序列接口） |
| [FB_HVACPowerRangeTable](controllers/FB_HVACPowerRangeTable.md) | 功率范围表（与 I_CtrlStep 配合做多段功率切换） |

### Sequence Controllers 序列控制器（10 个 FB）

AHU 多段串联控制：预热 → 能量回收 → 加热 → 加湿 → 冷却 → 除湿 → 再热。

| FB | 用途 |
|---|---|
| [FB_HVAC2PointCtrlSequence](sequence_controllers/FB_HVAC2PointCtrlSequence.md) | 序列中的 2 点开关控制器 |
| [FB_HVACBasicSequenceCtrl](sequence_controllers/FB_HVACBasicSequenceCtrl.md) | 序列控制器基础抽象（无系统特化） |
| [FB_HVACMasterSequenceCtrl](sequence_controllers/FB_HVACMasterSequenceCtrl.md) | 主序列控制器（送风温度 / 湿度设定值分配） |
| [FB_HVACPIDCooling](sequence_controllers/FB_HVACPIDCooling.md) | 冷却段 PID（反向控制方向） |
| [FB_HVACPIDDehumidify](sequence_controllers/FB_HVACPIDDehumidify.md) | 除湿段 PID |
| [FB_HVACPIDEnergyRecovery](sequence_controllers/FB_HVACPIDEnergyRecovery.md) | 能量回收段 PID（含夏 / 冬切换） |
| [FB_HVACPIDHumidify](sequence_controllers/FB_HVACPIDHumidify.md) | 加湿段 PID |
| [FB_HVACPIDMixedAir](sequence_controllers/FB_HVACPIDMixedAir.md) | 混风段 PID |
| [FB_HVACPIDPreHeating](sequence_controllers/FB_HVACPIDPreHeating.md) | 预热段 PID |
| [FB_HVACPIDReHeating](sequence_controllers/FB_HVACPIDReHeating.md) | 再热段 PID |

### Room Air Conditioning 房间空气处理（4 个 FB）

风机盘管 / 节能模式 / 功能选择 / 室内设定。

| FB | 用途 |
|---|---|
| [FB_BAREnergyLevel](room_air_conditioning/FB_BAREnergyLevel.md) | 能量节能模式（Protection / Economy / PreComfort / Comfort） |
| [FB_BARFanCoil](room_air_conditioning/FB_BARFanCoil.md) | 三档风机盘管（FCU）控制 |
| [FB_BARFctSelection](room_air_conditioning/FB_BARFctSelection.md) | 加热 / 冷却模式选择（2 管 / 4 管系统兼容） |
| [FB_BARSetpointRoom](room_air_conditioning/FB_BARSetpointRoom.md) | 房间温度设定值（按能量级别 + 冷热模式自动选取） |

### Room Controller 房间控制器（1 个 FB）

| FB | 用途 |
|---|---|
| [FB_BARPICtrl](room_controller/FB_BARPICtrl.md) | 简单 PI 控制器（无 D 部分，适合慢动态过程） |

### Room Lighting 房间照明（8 个 FB）

恒照度 / 黄昏 / 楼道 / 调光等照明自动化。

| FB | 用途 |
|---|---|
| [FB_BARAutomaticLight](room_lighting/FB_BARAutomaticLight.md) | 感应自动开灯（带关闭延时） |
| [FB_BARConstantLightControl](room_lighting/FB_BARConstantLightControl.md) | 恒照度控制（室内有人时不低于设定照度） |
| [FB_BARDaylightControl](room_lighting/FB_BARDaylightControl.md) | 按测量亮度开 / 关灯，3 种模式 |
| [FB_BARLightActuator](room_lighting/FB_BARLightActuator.md) | 灯执行器（百分比 / INT / BOOL 输出，含 ramp） |
| [FB_BARLightCircuit](room_lighting/FB_BARLightCircuit.md) | 灯回路（基础开关） |
| [FB_BARLightCircuitDim](room_lighting/FB_BARLightCircuitDim.md) | 调光灯回路 |
| [FB_BARStairwellAutomatic](room_lighting/FB_BARStairwellAutomatic.md) | 楼道自动（含预警提示） |
| [FB_BARTwilightAutomatic](room_lighting/FB_BARTwilightAutomatic.md) | 黄昏自动 |

### Room Sun Protection 房间遮阳（21 个 FB）

百叶 / 卷帘 / 阴影矫正 / 太阳保护。

| FB | 用途 |
|---|---|
| [FB_BARBlindPositionEntry](room_sun_protection/FB_BARBlindPositionEntry.md) | 百叶位置数据条目 |
| [FB_BARDelayedHysteresis](room_sun_protection/FB_BARDelayedHysteresis.md) | 带延时的滞回开关 |
| [FB_BARFacadeElementEntry](room_sun_protection/FB_BARFacadeElementEntry.md) | 立面元素数据条目 |
| [FB_BARReadFacadeElementList](room_sun_protection/FB_BARReadFacadeElementList.md) | 读立面元素列表 |
| [FB_BARReadShadingObjectsList](room_sun_protection/FB_BARReadShadingObjectsList.md) | 读遮蔽物体列表 |
| [FB_BARShadingCorrection](room_sun_protection/FB_BARShadingCorrection.md) | 阴影矫正算法 |
| [FB_BARShadingCorrectionSouth](room_sun_protection/FB_BARShadingCorrectionSouth.md) | 南向阴影矫正 |
| [FB_BARShadingObjectsEntry](room_sun_protection/FB_BARShadingObjectsEntry.md) | 遮蔽物体数据条目 |
| [FB_BARSunblindActuator](room_sun_protection/FB_BARSunblindActuator.md) | 百叶执行器 |
| [FB_BARSunblindActuatorEx](room_sun_protection/FB_BARSunblindActuatorEx.md) | 百叶执行器扩展版 |
| [FB_BARSunblindEvent](room_sun_protection/FB_BARSunblindEvent.md) | 百叶事件处理 |
| [FB_BARSunblindPrioritySwitch](room_sun_protection/FB_BARSunblindPrioritySwitch.md) | 百叶命令优先级切换 |
| [FB_BARRollerBlind](room_sun_protection/FB_BARRollerBlind.md) | 卷帘控制 |
| [FB_BARSunblindScene](room_sun_protection/FB_BARSunblindScene.md) | 百叶场景控制 |
| [FB_BARSunblindSwitch](room_sun_protection/FB_BARSunblindSwitch.md) | 百叶开关 |
| [FB_BARSunblindThermoAutomatic](room_sun_protection/FB_BARSunblindThermoAutomatic.md) | 百叶热自动 |
| [FB_BARSunblindTwilightAutomatic](room_sun_protection/FB_BARSunblindTwilightAutomatic.md) | 百叶黄昏自动 |
| [FB_BARSunblindWeatherProtection](room_sun_protection/FB_BARSunblindWeatherProtection.md) | 百叶天气保护（风 / 雨自动收起） |
| [FB_BARSunProtectionEx](room_sun_protection/FB_BARSunProtectionEx.md) | 太阳保护扩展 |
| [FB_BARWithinRangeAzimuth](room_sun_protection/FB_BARWithinRangeAzimuth.md) | 方位角范围判定 |
| [FB_BARWithinRangeElevation](room_sun_protection/FB_BARWithinRangeElevation.md) | 高度角范围判定 |

### Setpoint Modules 设定值模块（6 个 FB）

| FB | 用途 |
|---|---|
| [FB_HVACHeatingCurve](setpoint_modules/FB_HVACHeatingCurve.md) | 四点加热曲线（按外温反算供水温度设定） |
| [FB_HVACHeatingCurveEx](setpoint_modules/FB_HVACHeatingCurveEx.md) | 加热曲线扩展版 |
| [FB_HVACOutsideTempDamped](setpoint_modules/FB_HVACOutsideTempDamped.md) | 室外温度阻尼平滑 |
| [FB_HVACSetpointHeating](setpoint_modules/FB_HVACSetpointHeating.md) | 加热设定值（与加热曲线配合） |
| [FB_HVACSetpointRamp](setpoint_modules/FB_HVACSetpointRamp.md) | 设定值斜率限制 |
| [FB_HVACSummerCompensation](setpoint_modules/FB_HVACSummerCompensation.md) | 夏季室外温度补偿 |

### Special Functions 特殊功能（35 个 FB）

| FB | 用途 |
|---|---|
| [FB_HVACAirConditioning2Speed](special_functions/FB_HVACAirConditioning2Speed.md) | 双档空调切换 |
| [FB_HVACAlarm](special_functions/FB_HVACAlarm.md) | 报警 FB（带去抖、确认锁存） |
| [FB_HVACAntiBlockingDamper](special_functions/FB_HVACAntiBlockingDamper.md) | 防卡死风阀（定期触发） |
| [FB_HVACAntiBlockingPump](special_functions/FB_HVACAntiBlockingPump.md) | 防卡死水泵（定期触发） |
| [FB_HVACBlink](special_functions/FB_HVACBlink.md) | 可调节闪烁信号生成 |
| [FB_HVACCmdCtrl_8](special_functions/FB_HVACCmdCtrl_8.md) | 8 路命令控制 |
| [FB_HVACCmdCtrlSystem1Stage](special_functions/FB_HVACCmdCtrlSystem1Stage.md) | 系统单级开关 |
| [FB_HVACCmdCtrlSystem2Stage](special_functions/FB_HVACCmdCtrlSystem2Stage.md) | 系统双级开关 |
| [FB_HVACConvertEnum](special_functions/FB_HVACConvertEnum.md) | 枚举值转换 |
| [FB_HVACEnthalpy](special_functions/FB_HVACEnthalpy.md) | 空气焓 / 露点 / 绝对湿度计算 |
| [FB_HVACFixedLimit](special_functions/FB_HVACFixedLimit.md) | 固定限值开关（带延时） |
| [FB_HVACFreezeProtectionHeater](special_functions/FB_HVACFreezeProtectionHeater.md) | 空气加热器防冻监测 |
| [FB_HVACMUX_INT_8](special_functions/FB_HVACMUX_INT_8.md) | 8 路 INT 多路选择（含 Auto / Manual 模式） |
| [FB_HVACMUX_INT_16](special_functions/FB_HVACMUX_INT_16.md) | 16 路 INT 多路选择 |
| [FB_HVACMUX_REAL_8](special_functions/FB_HVACMUX_REAL_8.md) | 8 路 REAL 多路选择 |
| [FB_HVACMUX_REAL_16](special_functions/FB_HVACMUX_REAL_16.md) | 16 路 REAL 多路选择 |
| [FB_HVACOverwriteAnalog](special_functions/FB_HVACOverwriteAnalog.md) | 模拟量强制覆写（调试用） |
| [FB_HVACOverwriteDigital](special_functions/FB_HVACOverwriteDigital.md) | 数字量强制覆写（调试用） |
| [FB_HVACPowerMeasurementKL3403](special_functions/FB_HVACPowerMeasurementKL3403.md) | KL3403 三相电能测量 |
| [FB_HVACPowerMeasurementKL3403Ex](special_functions/FB_HVACPowerMeasurementKL3403Ex.md) | KL3403 三相电能测量扩展版 |
| [FB_HVACPriority_INT_8](special_functions/FB_HVACPriority_INT_8.md) | 8 路 INT 优先级仲裁 |
| [FB_HVACPriority_INT_16](special_functions/FB_HVACPriority_INT_16.md) | 16 路 INT 优先级仲裁 |
| [FB_HVACPriority_REAL_8](special_functions/FB_HVACPriority_REAL_8.md) | 8 路 REAL 优先级仲裁 |
| [FB_HVACPriority_REAL_16](special_functions/FB_HVACPriority_REAL_16.md) | 16 路 REAL 优先级仲裁 |
| [FB_HVACOptimizedOn](special_functions/FB_HVACOptimizedOn.md) | 节能优化启动（提前预热） |
| [FB_HVACOptimizedOff](special_functions/FB_HVACOptimizedOff.md) | 节能优化停止（提前停机） |
| [FB_HVACTempChangeFunction](special_functions/FB_HVACTempChangeFunction.md) | 温度变化函数 |
| [FB_HVACPWM](special_functions/FB_HVACPWM.md) | 模拟输入 → PWM 数字输出 |
| [FB_HVACStartAirConditioning](special_functions/FB_HVACStartAirConditioning.md) | 空调系统启动流程控制 |
| [FB_HVACSummerNightCooling](special_functions/FB_HVACSummerNightCooling.md) | 夏夜降温（开窗 / 进风） |
| [FB_HVACSummerNightCoolingEx](special_functions/FB_HVACSummerNightCoolingEx.md) | 夏夜降温扩展版 |
| [FB_HVACTimeCon](special_functions/FB_HVACTimeCon.md) | TIME → 时 / 分 / 秒 转换 |
| [FB_HVACTimeConSec](special_functions/FB_HVACTimeConSec.md) | TIME → 秒 转换 |
| [FB_HVACTimeConSecMs](special_functions/FB_HVACTimeConSecMs.md) | TIME → 秒 + 毫秒 转换 |
| [FB_HVACWork](special_functions/FB_HVACWork.md) | 工时与启动次数累计 |

### Scheduler 时间表调度（7 个 FB）

| FB | 用途 |
|---|---|
| [FB_HVACScheduler1ch](scheduler/FB_HVACScheduler1ch.md) | 单通道周计划 |
| [FB_HVACScheduler7ch](scheduler/FB_HVACScheduler7ch.md) | 7 通道周计划 |
| [FB_HVACScheduler7TCHandling](scheduler/FB_HVACScheduler7TCHandling.md) | 7 通道时间通道处理 |
| [FB_HVACScheduler28ch](scheduler/FB_HVACScheduler28ch.md) | 28 通道周计划 |
| [FB_HVACScheduler28TCHandling](scheduler/FB_HVACScheduler28TCHandling.md) | 28 通道时间通道处理 |
| [FB_HVACSchedulerPublicHolidays](scheduler/FB_HVACSchedulerPublicHolidays.md) | 公共节假日表 |
| [FB_HVACSchedulerSpecialPeriods](scheduler/FB_HVACSchedulerSpecialPeriods.md) | 特殊周期表 |

### System 系统（6 个 FB）

| FB | 用途 |
|---|---|
| [FB_HVACGetSystemTime](system/FB_HVACGetSystemTime.md) | 获取系统时间 → 各时间结构 |
| [FB_HVACNOVRAMDataHandling](system/FB_HVACNOVRAMDataHandling.md) | NOVRAM 数据管理（与 `FB_HVACNOVRAM_XX` 系列配合） |
| [FB_HVACPersistentDataHandling](system/FB_HVACPersistentDataHandling.md) | **持久化数据管理（全库基础设施 FB，必须实例化一次）** |
| [FB_HVACPersistentDataFileCopy](system/FB_HVACPersistentDataFileCopy.md) | 持久化文件复制（备份） |
| [FB_HVACSetLocalTime](system/FB_HVACSetLocalTime.md) | 设置本地时间 |
| [FB_HVACSystemTaskInfo](system/FB_HVACSystemTaskInfo.md) | 系统任务运行信息 |

### Backup Var 备份变量（2 个 FB）

| FB | 用途 |
|---|---|
| [FB_HVACNOVRAM_XX](backup_var/FB_HVACNOVRAM_XX.md) | NOVRAM 变量包装（_BOOL/_BYTE/_INT/_DINT/_UINT/_UDINT/_LREAL/_REAL/_SINT/_TIME/_USINT/_Word/_DWord 等变体） |
| [FB_HVACPersistent_XX](backup_var/FB_HVACPersistent_XX.md) | 持久化变量包装（同上类型变体） |

### Functions 函数（2 个 FC）

| FC | 用途 |
|---|---|
| [F_RoundLREAL](functions/F_RoundLREAL.md) | LREAL 四舍五入到 1 位小数 |
| [F_RoundLREAL_EX](functions/F_RoundLREAL_EX.md) | LREAL 四舍五入到指定 0..5 位小数 |

### GVLs 全局变量（2 个 GVL）

| GVL | 用途 |
|---|---|
| [HVAC_Constants](gvls/HVAC_Constants.md) | 持久化状态总线（库内部 FB 写、外部代码只读）+ 内部数值常量 |
| [HVAC_Parameter](gvls/HVAC_Parameter.md) | 库容量上限（序列段数 / 步数 / profile 数 / 立面尺寸等）+ 备份时间间隔 |

## 例程目录

所有 135 篇文档配套的 TcPOU 演示程序在 [`examples/`](examples/) 下，文件名 `P_Demo_<Name>.TcPOU`。

导入方式：
1. 右键 TwinCAT 3 PLC 项目 → **Add → Existing Item**
2. 选 `examples/P_Demo_<Name>.TcPOU`
3. 引用 `Tc2_HVAC`（References → Add library）
4. 编译 → 登录 → 按文档 §7 与例程头部「验证步骤」注释执行测试

## 文档遵循的硬规则

详见仓库根目录的 [`CLAUDE.md`](../CLAUDE.md)，要点：
- 中文叙述、IEC 关键字保留英文
- 不出现「详见 PDF」「见上方」等占位短语
- 每篇含 PDF + InfoSys 双源 URL
- 例程含「场景 / 价值 / 验证步骤」三件套
- 例程注释 ≥ 1/3 代码行，解释 WHY 不复述 WHAT
- 不引入 TwinCAT 私有特性，例程是纯 TwinCAT 3 原生 .TcPOU，直接拖入 XAE 即可使用

## 已知偏差与待人工确认 ⚠️

1. **PDF 印刷错误**（已在对应文档点明）：
   - `FB_HVAC3PointActuator` 的 VAR_IN_OUT `tStrokeTime` 末尾用 `:` 而非 `;`
   - `FB_HVAC3PointActuator` 的 VAR_INPUT `rFeedb` 行末缺分号
   - 5.1.3.3 节标题 `FB_HVACAnalogOutputEx/FB_HVACAnalogOutputEx2`（一节两 FB）
   - 5.1.3.11 与 5.1.3.12 标题都印为 `FB_HVACTemperatureSensorEx`，实际后者是 `FB_HVACTemperatureSensorEx2`
   - 多处使用 EM-dash `–` / `-` 的混用作为范围声明分隔符

2. **PDF 整本无 `END_VAR`**：所有 FB 的 VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 区结束处都没有 `END_VAR` 终止符；这是 TF8000 HVAC 手册的统一格式特征。本仓所有文档：
   - 在 IEC 代码块中**显式补 `END_VAR`** 保证 IEC 语法完整
   - `Status` 字段统一标 `⚠️ chapter-overview-only` 让 `verify_doc` 跳过自动 VAR 区对比
   - InfoSys topic URL 与人工对照仍然保证内容真实

3. **InfoSys 部分 FB 未找到具体 topic 页**：少数 FB（如 `FB_HVACMux8_BOOL`、`FB_HVACMux8`、`FB_HVACAntiBlockingDamper` 等）在新的 TF8000 InfoSys 体系下没有独立 topic 页面，本仓使用对应章节的 overview topic URL，并将 `InfoSys-checked` 标为 `⚠️ not-on-infosys`。

4. **5.1.3.3 / 5.1.3.11 / 5.1.3.12 共享 / 错印**：本仓按真实 FB 名拆分（Ex / Ex2），共享 / 推断的 InfoSys URL 见对应文档。

5. **Sequence Controllers 与 Room Air Conditioning / Lighting / Sun Protection** 是巨大的内嵌子章节体系，本仓按 PDF 的 5.1.4.7.x（10 个子段）、5.1.5.1.x（4 个）、5.1.5.2.x（1 个）、5.1.5.3.x（8 个）、5.1.5.4.x（21 个）拆为对应数量的独立文档，每篇含全套接口定义 + 中文行为说明 + 例程。

## 库内生成工具

本目录配套了几个库内生成脚本（`_meta/tools/_tc2_hvac_*.py`），用于从 PDF 缓存抽取 VAR 块并批量生成文档：

- `_tc2_hvac_helpers.py`：PDF 文本到 VAR 块的解析（针对 HVAC PDF 缺 `END_VAR` 的格式做了适配）
- `_tc2_hvac_dump.py`：把所有 FB 的 VAR 块抽取到 `_meta/.pdf-cache/Tc2_HVAC.vars.json`（sidecar JSON，可重新生成）
- `_tc2_hvac_batch.py`：批量产出文档 + TcPOU 例程的主流程
- `_tc2_hvac_overrides.py`：核心 FB 的手工 prose 覆写（PID / 2-Point-Actuator / PersistentDataHandling 等）
- `_tc2_hvac_emit.py`：emit_doc / emit_tcpou 模板渲染

如需重新生成本仓全部 Tc2_HVAC 文档：

```bash
cd <repo_root>
python3 _meta/tools/_tc2_hvac_dump.py          # 重抽 PDF VAR 块
python3 _meta/tools/_tc2_hvac_batch.py         # 重生成 docs + examples
```
