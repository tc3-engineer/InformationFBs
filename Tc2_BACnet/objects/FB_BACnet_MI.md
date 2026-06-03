# FB_BACnet_MI

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Multistate Input` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_MI.TcPOU`](../examples/P_Demo_FB_BACnet_MI.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Multistate Input」对象类型(BACnet Object_Type = 13 / Multistate Input)。语义上是只读多状态输入,典型用于本地操作模式开关(`AUTO`/`Low`/`Medium`/`High`/`Turbo`)、运行阶段指示(`Stop`/`Start`/`Run`/`Stopping`)等枚举型物理输入。Present_Value 为 `UDINT`,范围由 `aStateText` 数组的长度决定(无 `aStateText` 时默认 12 态,可在 `BACnet_Param` 改)。本对象类型在本库中仅基础类,无 `_IO` / `_ECAT` 变体(物理多态开关一般通过 BV 数组组合实现)。

## 2. 接口定义

> PDF §6.1.1 / §6.1.2 把所有对象 FB 统一用对象类型表 + 后缀规则描述,**未**针对单个 FB 列 `VAR_INPUT` / `VAR_OUTPUT` 区;以下表把 PDF/InfoSys 在 §6.1.1 / §6.1.2 / §9.x 提及的成员按 BACnet 标准属性分类整理。

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

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_OUTPUT` 区;运行状态以 FB 成员形式暴露,见下表。

### VAR_IN_OUT

无。

### 关键属性 / 成员(分组)

| 类别 | FB 成员 | 类型 | 含义 |
|---|---|---|---|
| 基本信息 | `iParent` / `sObjectName` / `sDescription` / `sDeviceType` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |
| Present_Value | `nVal` | `UDINT` | PLC 喂的多态值(1..N) |
| 状态枚举 | `aStateText` | `ARRAY[1..*] OF STRING(*)` | State_Text(BMS 显示用文本数组,如 `['AUTO','Low','Medium','High','Turbo']`,长度决定 Number_Of_States) |
| 报警 | `aAlarmValues` | `ARRAY OF UDINT` | Alarm_Values(哪些状态算报警态) |
| 报警 | `aFaultValues` | `ARRAY OF UDINT` | Fault_Values(哪些状态算故障态) |
| 事件 | `bEventDetectionEnable` / `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` / `nTimeDelay` / `nTimeDelayNormal` | 同 AI | Intrinsic Reporting |

## 3. 行为说明

FB_BACnet_MI 每周期调用一次,PLC 把多态枚举值写入 `nVal`,库内部映射到 Present_Value。`aStateText` 数组的长度直接决定 BACnet 标准属性 Number_Of_States — 5 个文本就是 5 态,下标按 BACnet 习惯从 1 开始。`aAlarmValues` 列出「哪些状态值算报警态」(如 `[4,5]` 表示 High 和 Turbo 触发报警);`aFaultValues` 列「哪些算故障态」(如 `[0]` 表示传感器故障 / 没读到)。Intrinsic Reporting 在 Present_Value 命中 alarm/fault 值持续 `nTimeDelay` 秒后触发对应类型事件。PDF §9.2 示例 `fbMi : FB_BACnet_MI := (aStateText := ['AUTO','Low','Medium','High','Turbo']);` 是最常见用法。

## 4. 错误码 / 返回值

无返回值;运行状态通过 `stStatusFlags` 暴露。⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **`aStateText` 的下标从 1 开始**:`aStateText[1]` 是第一个状态,而 IEC 标准数组通常 0 开始,容易写错。
- **不写 `aStateText` 默认 12 态**:PDF §9.2:Number_Of_States 默认上限 12,可在 `BACnet_Param` 改;通常应该显式声明。
- **`nVal := 0` 视为无效**:多态值合法范围是 1..Number_Of_States,写 0 会让 BMS 把对象当成Reliability=NO_SENSOR(配 fault 报警)。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_MI.TcPOU`](../examples/P_Demo_FB_BACnet_MI.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_MI
VAR
    fbFanModeSwitch : FB_BACnet_MI := (
        sObjectName := 'FanMode_AHU_3F',
        sDescription := 'Local fan speed selector (AUTO/Low/Mid/High/Turbo)',
        aStateText := ['AUTO', 'Low', 'Medium', 'High', 'Turbo'],
        aAlarmValues := [5],                     // Turbo 算报警(超出运行包络)
        bEventDetectionEnable := TRUE,
        nNotificationClass := 13);
    nFanSelectorPlc : UDINT := 1;                // 从本地旋钮读到的位置(1..5)
END_VAR

fbFanModeSwitch.nVal := nFanSelectorPlc;
fbFanModeSwitch();
```

## 7. 业务场景与实际价值

- **场景**:空调机组本地控制柜上有一个 5 档旋钮(AUTO/Low/Medium/High/Turbo)切换风机模式,BMS 需要看到当前档位以便记录运维操作;Turbo 档(超出正常运行包络)要发报警。
- **价值**:用一个 MI 对象代替「5 个 BI 拼接 + 文本解码」;BMS 端直接显示语义文本,无需在画面里维护一张码表。
- **替代方案对比**:用 5 个 BV 也能表达,但 BMS 端处理「互斥唯一态」困难;用 AV 暴露数字 1..5 又丢失文本语义。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1、§3.2.49/50/51/52(Number_Of_States / State_Text / Alarm_Values / Fault_Values)、§9.2(`aStateText` 决定态数)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_MO`(可写多态输出)、`FB_BACnet_MV` / `FB_BACnet_MV_5P`(虚拟多态值)
