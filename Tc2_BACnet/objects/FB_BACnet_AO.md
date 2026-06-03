# FB_BACnet_AO

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Analog Output` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_AO.TcPOU`](../examples/P_Demo_FB_BACnet_AO.TcPOU) |


---

## 1. 功能简述

代表 BACnet 标准里的「Analog Output」对象类型(BACnet Object_Type = 1 / Analog Output)。语义上是**可写、可命令优先级化的模拟输出**,典型用于 0-10V / 4-20mA 等物理输出。客户端用 `WriteProperty(Present_Value, ..., priority)` 写值到 BACnet 16 个优先级槽位中的某一个,Present_Value 取最高优先级非空槽位的值;全空时回落 `fRelinquishDefault`(PDF §3.1 + §6.1.1 + §6.2.1)。属于「无后缀基础类」,本库另提供 `_IO`(K-bus)/`_ECAT`(EtherCAT)/`_5P`(5 优先级槽位,大部分楼控场景够用)/`_IO5P`/`_RAW5P` 五种后缀变体(PDF §6.1.2)。

## 2. 接口定义

> PDF §6.1.1 / §6.1.2 把所有「无后缀」对象 FB 集中描述,**未**针对单个 FB 列 `VAR_INPUT` / `VAR_OUTPUT` 区。下表把 §6.1.1 / §6.1.2 / §9.5 / §9.6 出现的可初始化成员按 BACnet 标准属性分类。

### VAR_INPUT

```iecst
VAR_INPUT
END_VAR
```

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_INPUT` 区;成员见下表。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
END_VAR
```

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_OUTPUT` 区;成员见下表。

### VAR_IN_OUT

无。

### 关键属性 / 成员(分组)

| 类别 | FB 成员 | 类型 | 含义 |
|---|---|---|---|
| 基本信息 | `iParent` | `I_BACnet_View` | 父 View 节点 |
| 基本信息 | `sObjectName` / `sDescription` / `sDeviceType` | `STRING(*)` | Object_Name / Description / Device_Type |
| 工程单位 / 量程 | `eUnit` / `fMinPresValue` / `fMaxPresValue` / `fResolution` | `E_BA_Unit` / `REAL` | 量程 + 最小可写步长 |
| 命令优先级 | `bEnPgm` | `BOOL` | TRUE 时 PLC 在 Program 优先级(默认 16/15)写值;FALSE 等价 NULL,该槽位释放 |
| 命令优先级 | `fValPgm` | `REAL` | PLC 在 Program 优先级写的值 |
| Present_Value | `fRelinquishDefault` | `REAL` | 16 槽位都为空时使用的回退值 |
| 报警限 | `fHighLimit` / `fLowLimit` / `fDeadband` / `bHighLimitEnable` / `bLowLimitEnable` / `nTimeDelay` / `nTimeDelayNormal` | 同 AI | Intrinsic Reporting 报警限 |
| 事件 | `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` / `bEventDetectionEnable` | 同 AI | 事件路由 |

### 后缀变体(PDF §6.1.2)

| 变体 | 增/删的成员 | 用途 |
|---|---|---|
| `FB_BACnet_AO` | — | 基础类:PLC 用 `bEnPgm` + `fValPgm` 写 Program 优先级 |
| `FB_BACnet_AO_IO` | 增 `nRawVal AT %Q* : INT` | 写出去的 Present_Value 自动写到 K-bus 端子通道(PDF §9.3) |
| `FB_BACnet_AO_ECAT` | 增 `nRawVal AT %Q* : INT`、`nRawECatState : UINT` | 写到 EtherCAT 端子通道,附 EtherCAT 状态(PDF §9.3) |
| `FB_BACnet_AO_5P` | 增 `bEnSfty`/`fValSfty`、`bEnCrit`/`fValCrit`、`bEnManLoc`/`fValManLoc`、`bEnManualOperator`/`fValManualOperator`、`bEnPgm`/`fValPgm` | 5 个 of 16 优先级槽位由 PLC 内部控制(PDF §9.5) |
| `FB_BACnet_AO_IO5P` | `_5P` + `nRawVal AT %Q* : INT` | 5 优先级 + 写到 K-bus 端子 |
| `FB_BACnet_AO_RAW5P` | `_5P` + `nRawVal : INT` | 5 优先级 + raw 值由 PLC 自行算 |

## 3. 行为说明

每周期调用一次,所有 BACnet 对象 FB 必须用同一周期任务,否则启动期同步失败。基础类 AO 的 Present_Value 计算流程:对 BACnet 16 个优先级槽位轮询,从槽 1(最高)到槽 16(最低)找第一个非 NULL 的值——基础类下,PLC 通过 `bEnPgm := TRUE` + `fValPgm := <val>` 占用 Program 优先级(默认槽 16,可在 `BACnet_Param` 调到 15);BMS 通过 `WriteProperty(Present_Value, ..., priority := 8)` 占用 Manual Operator(槽 8)。当 `bEnPgm := FALSE` 时槽 16 释放为 NULL(PDF §6.2.1 + §6.6.5)。所有槽位全 NULL 时取 `fRelinquishDefault`。`_5P` 变体则把 5 个常用优先级(LifeSafety / Critical / ManLocal / ManOperator / Program)以 `bEn*` + `f|nVal*` 形式直接暴露给 PLC,把"调度 + 切换优先级"做成布尔逻辑,无需调 `WritePropertyNull` 释放(PDF §9.5)。

## 4. 错误码 / 返回值

无返回值;运行状态通过 `stStatusFlags` / `eEventState` / `eReliability` 暴露,语义与 FB_BACnet_AI §4 一致。**写值越限**:BMS 若试图写超出 `fMinPresValue` / `fMaxPresValue` 的值,BACnet stack 会返回 `Value_Out_Of_Range` 错误(PDF §3.2.13 / §3.2.14)。

⚠️ PDF + InfoSys 均未在本对象类型节列出 BACnet error/reject 码具体数值,见 `BACnet_Globals`。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **命令优先级(commandable 对象)**:`_5P` 系列在 BACnet 16 个优先级中取 5 个槽位(LifeSafety=1 / Critical=5 / ManLocal=7 / ManOperator=8 / Program=15,默认值见 `BACnet_Param`),用 `bEnSfty` / `bEnCrit` / `bEnManLoc` / `bEnPgm` / `bEnManualOperator` 配对的 `f|b|nVal*` 写槽位。`bEn*` 由 TRUE 转 FALSE 等价于写 NULL(释放该槽位)。全部 16 槽位都为 NULL 时取 `fRelinquishDefault` / `bRelinquishDefault` / `nRelinquishDefault`(PDF §6.2.1 / §9.5 / §9.6)。
- **不写槽位也要每周期调用 FB**:库内部用周期调用驱动写值锁存到 BACnet stack;只置 `bEnPgm := TRUE` 而不调用 FB,值不会被发布。
- **基础类 `FB_BACnet_AO` 和 `_5P` 行为差别大**:基础类只占 1 个槽位,常用于"PLC 是该输出的唯一控制源"的简单场景;`_5P` 适合"BMS 手动覆盖 + PLC 自动 + 紧急停车按钮"等多控制源场景。混用会让人难以追踪谁在写值。
- **`_IO` / `_ECAT` 后缀写出的 Present_Value 是 stack 自动换算到 raw**,linear `fVal:fMin..fMax → nRawVal:0..32767`。
- **不调用 FB 不会写端子**:即使 `bEnPgm := TRUE` 并赋了 `fValPgm`,若忘了 `fbAO()`,Present_Value 不会传到 BACnet 也不会传到 `_IO`/`_ECAT` 端子。
- **释放优先级要走 BACnet `WritePropertyNull` 服务**(基础类),而不是直接 `fbAO.fValPgm := NULL`(IEC 没有 NULL)。基础类下用 `bEnPgm := FALSE` 表示释放;`_5P` 下用对应的 `bEn* := FALSE`。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_AO.TcPOU`](../examples/P_Demo_FB_BACnet_AO.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_AO
VAR
    // 基础类 AO:PLC 在 Program 优先级写值;BMS 仍可在 ManOperator(8) 覆盖
    fbValveCmd : FB_BACnet_AO := (
        sObjectName := 'Valve_3F_East',
        sDescription := 'Floor 3 East zone valve cmd (0..100%)',
        eUnit := E_BA_Unit.eOther_Percent,
        fMinPresValue := 0.0,
        fMaxPresValue := 100.0,
        fRelinquishDefault := 0.0);     // 没人写时回退到全关
    fAutoCmd : REAL;                    // PLC 自动算出来的指令
    bEnableAuto : BOOL := FALSE;        // 在线写 TRUE 进入自动模式
END_VAR

fbValveCmd.bEnPgm  := bEnableAuto;
fbValveCmd.fValPgm := fAutoCmd;
fbValveCmd();
```

## 7. 业务场景与实际价值

- **场景**:楼控 VAV 风阀 / 冷冻水阀 / 加热阀控制,需要既被 PLC 自动控制(根据室温偏差算阀位),又允许 BMS 手动覆盖(运维人员在 SCADA 上拖动滑块强制开 60%)。
- **价值**:用基础类 `FB_BACnet_AO` 时,PLC 写 Program 优先级 + BMS 写 Manual Operator 优先级,Present_Value 自然取较高者(8 > 16),无需 PLC 端写"是否被覆盖"判断;BMS 释放后 PLC 自动恢复控制。
- **替代方案对比**:
  - 用 `_5P` 变体把 5 个优先级全摊在 PLC 内,适合"PLC 内部多个控制源竞争同一输出"(节能模式 vs 防冻模式 vs 手操)的复杂场景
  - 用普通 AO + 一个 BV 做"BMS 是否已覆盖"标志:工作量大且无法应对多优先级写
  - 用 `_IO` 变体直接绑端子省掉 PLC 中转 `nRawVal := REAL_TO_INT(fVal * 3276.7);`

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §3.1、§6.1.1、§6.1.2、§6.2.1(命令优先级)、§6.6.5(PLC 写访问)、§9.3(_IO / _ECAT 端子链接)、§9.5(_5P 优先级控制)、§9.6(WritePropertyNull 释放)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_AV`(虚拟值)、`FB_BACnet_AO_5P` / `_IO` / `_ECAT` / `_IO5P` / `_RAW5P`(本 FB 后缀变体)、`FB_BACnet_Loop_Ref`(把本 FB 当 PID 输出引用)
