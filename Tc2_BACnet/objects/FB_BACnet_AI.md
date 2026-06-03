# FB_BACnet_AI

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Analog Input` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_AI.TcPOU`](../examples/P_Demo_FB_BACnet_AI.TcPOU) |


---

## 1. 功能简述

代表 BACnet 标准里的「Analog Input」对象类型,在 BACnet 服务器侧把 PLC 一个 `REAL` 量(典型为温度、湿度、流量、电流等传感器读数)暴露给 BMS。该对象类型(BACnet Object_Type = 0 / Analog Input)语义上是只读输入,客户端用 `ReadProperty(Present_Value)` 拿当前值,不直接写 Present_Value(PDF §3.1 + §6.1.1)。属于「无后缀基础类」,本库另提供 `_IO`(K-bus 端子)、`_ECAT`(EtherCAT 端子)、`_Raw`(PLC 程序提供 raw 值)三种变体后缀(PDF §6.1.2)。

## 2. 接口定义

> PDF §6.1.1 把所有「无后缀」对象 FB 集中描述,**未**针对单个 FB 列 `VAR_INPUT` / `VAR_OUTPUT` 区;PDF §6.1.2 把后缀变体也用同一张表的规则推导。下文「关键属性」表把 §6.1.1 / §6.1.2 / §9.2 / §9.3 / §9.10 / §9.16 出现的可初始化成员按 BACnet 标准属性分类。

### VAR_INPUT

```iecst
VAR_INPUT
END_VAR
```

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_INPUT` 区。所有属性以 FB 直接成员形式开放,典型用法见 §6 例程与下方「关键属性」。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
END_VAR
```

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_OUTPUT` 区。运行时读到的状态(`stStatusFlags`、`fPresVal` 等)以 FB 成员形式暴露。

### VAR_IN_OUT

无。

### 关键属性 / 成员(按 BACnet 属性分组,来源 PDF §3.2 + §9.2 + §9.10)

| 类别 | FB 成员 | 类型 | 含义(对应 BACnet 属性) |
|---|---|---|---|
| 基本信息 | `iParent` | `I_BACnet_View` | 父 Structured View 节点引用,用于 DPAD 层级(§6.2.10) |
| 基本信息 | `sObjectName` | `STRING(*)` | Object_Name(BMS 树里看到的名字) |
| 基本信息 | `sDescription` | `STRING(*)` | Description(BACnet 标准 Description 属性) |
| 基本信息 | `sDeviceType` | `STRING(*)` | Device_Type(例 `'TemperatureSensor'`) |
| 工程单位 | `eUnit` | `E_BA_Unit` | Units(如 `eTemperature_DegreesCelsius`) |
| 量程 | `fMinPresValue` | `REAL` | Min_Pres_Value |
| 量程 | `fMaxPresValue` | `REAL` | Max_Pres_Value |
| Present_Value | `fVal` | `REAL` | PLC 直接喂的 Present_Value(无后缀基础类) |
| COV | `fCovIncrement` | `REAL` | COV_Increment(超过该增量才推送 COV) |
| 报警限 | `fHighLimit` / `bHighLimitEnable` | `REAL` / `BOOL` | High_Limit + Limit_Enable[bit High] |
| 报警限 | `fLowLimit` / `bLowLimitEnable` | `REAL` / `BOOL` | Low_Limit + Limit_Enable[bit Low] |
| 报警限 | `fDeadband` | `REAL` | Deadband(防止报警闪动) |
| 报警限 | `nTimeDelay` | `UDINT` | Time_Delay(秒,触发 TO_OFFNORMAL 前等待) |
| 报警限 | `nTimeDelayNormal` | `UDINT` | Time_Delay_Normal(秒,恢复 TO_NORMAL 前等待) |
| 事件 | `nNotificationClass` | `UDINT` | Notification_Class(把报警路由到哪个 NC 实例) |
| 事件 | `aEventEnable` | `ARRAY[0..2] OF BOOL` | Event_Enable[TO_OFFNORMAL, TO_FAULT, TO_NORMAL] |
| 事件 | `aEventMessageTextsConfig` | `ARRAY[0..2] OF STRING(*)` | Event_Message_Texts_Config |
| 事件 | `bEventDetectionEnable` | `BOOL` | Event_Detection_Enable |
| 通用 | `stSettings` | `ST_BACnetObjectSettings` | aDisabled / aWriteProtected 控制属性可见性(§6.6.3 / §6.6.4) |

### 后缀变体(PDF §6.1.2)

| 变体 | 增/删的成员 | 用途 |
|---|---|---|
| `FB_BACnet_AI` | — | 基础类:PLC 直接喂 `fVal` |
| `FB_BACnet_AI_IO` | 增 `nRawVal AT %I* : INT`、可选 `nRawState AT %I* : USINT` | 通过 `{attribute 'TcLinkTo' := ...}` 直接链接 K-bus 端子通道(PDF §9.3) |
| `FB_BACnet_AI_ECAT` | 增 `nRawVal AT %I* : INT`、`nRawState : USINT`、`nRawECatState : UINT` | 通过 `{attribute 'TcLinkTo' := ...}` 直接链接 EtherCAT 端子通道,附 EtherCAT 状态(PDF §9.3) |
| `FB_BACnet_AI_Raw` | 增 `nRawVal : INT`、`nRawState : USINT` | PLC 程序自行算 raw 值与 raw 状态后赋值(常用于自定义传感器接口,PDF §6.1.2 示例) |

## 3. 行为说明

FB_BACnet_AI 在 PLC 端是单纯的「值容器 + 元数据」。每周期调用一次后,库内部把 `fVal`(或 `nRawVal` 经线性换算)推到 BACnet stack 的 Present_Value;客户端按 BACnet 标准的 RP / RPM / COV / COV-P 中任一方式拉取。报警逻辑由 stack 自动跑:`fVal` 越过 `fHighLimit + fDeadband` 且持续 `nTimeDelay` 秒后,Event_State 切到 TO_OFFNORMAL 并向 `nNotificationClass` 指定的 NC 实例上报;反向越界 + `nTimeDelayNormal` 秒后切回 TO_NORMAL(PDF §3.2.19~§3.2.21 + §9.10)。`_IO` / `_ECAT` 变体上电时 BACnet stack 自动按端子通道线性映射 `nRawVal` 到 `fVal`,无需 PLC 介入;`_Raw` 变体下 PLC 必须每周期写 `nRawVal` 和 `nRawState`(0 正常 / 1 下溢 / 2 上溢 / 4 错误)。属性变更应仅在条件触发分支里写,而不要每周期都 set,否则 BMS 写下来的值会被立刻覆盖(PDF §6.3.1)。

## 4. 错误码 / 返回值

无返回值。该 FB 本身没有错误标志输出;BACnet 协议错误集中在全局 `BACnet_Globals.Error` / `BACnet_Globals.Abort` / `BACnet_Globals.Reject` 常量(PDF §5.2.2),通过客户端读到 stStatusFlags 或 eReliability 反映:
- `stStatusFlags.bInAlarm = TRUE`:对象处于报警态(越限超时)
- `stStatusFlags.bFault = TRUE`:对象处于故障态(`_IO` / `_ECAT` 端子 nRawState 报错时自动置位)
- `stStatusFlags.bOverridden = TRUE`:被 PLC 内部机制覆盖
- `stStatusFlags.bOutOfService = TRUE`:被 BMS 写了 Out_of_Service := TRUE,值为模拟值

⚠️ PDF + InfoSys 均未在本对象类型节列出具体 BACnet error/reject 码常量数值,需对照 `BACnet_Globals` 章节查询。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **`_IO` / `_ECAT` 后缀的 raw 量是线性映射**:库内部按 `nRawVal:0..32767 → fVal:fMinPresValue..fMaxPresValue` 线性算 Present_Value,温度传感器若用 0..10V 模拟量,要在端子配置里把对应的量程也调一致。
- **`_Raw` 变体下 `nRawState` 必须自己写**:PDF §6.1.2 例:Underrange=0x01 / Overrange=0x02 / Error=0x04;不写会一直挂 Status_Flags.bFault(工程经验补充)。
- **Intrinsic Reporting 启用前要先建好对应的 NC 实例**:`nNotificationClass := 10` 时,POU 里必须实例化一个 `nObjectInstance := 10` 的 `FB_BACnet_NC`,否则报警发不出去(PDF §6.2.2.1 + §9.8)。
- **COV 不要乱开**:`fCovIncrement := 0` 时每次值变化都发 COV,会瞬时塞满网段;`fCovIncrement := 2.0` 是 PDF §9.2 推荐起点(对温度而言 ±2°C 才发)。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_AI.TcPOU`](../examples/P_Demo_FB_BACnet_AI.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_AI
VAR
    // 基础 AI:PLC 直接喂 fVal(典型场景:用 EL3208 读 PT1000 后,PLC 端把
    // 工程值再喂回来作为 BACnet AI 的 Present_Value)
    fbRoomTemp : FB_BACnet_AI := (
        sObjectName  := 'RoomTemp_3F_East',
        sDescription := 'Floor 3 East zone PT1000',
        sDeviceType  := 'TemperatureSensor',
        eUnit        := E_BA_Unit.eTemperature_DegreesCelsius,
        fMinPresValue := -50.0,
        fMaxPresValue := 150.0,
        fCovIncrement := 0.5,
        fHighLimit := 30.0,
        fLowLimit := 5.0,
        bHighLimitEnable := TRUE,
        bLowLimitEnable := TRUE,
        nTimeDelay := 60,
        nTimeDelayNormal := 30,
        bEventDetectionEnable := TRUE,
        nNotificationClass := 10);
    fSensorValue : REAL;            // 从 PLC 别的代码算好的工程值
END_VAR

fbRoomTemp.fVal := fSensorValue;
fbRoomTemp();                       // 每周期调用一次
```

## 7. 业务场景与实际价值

- **场景**:楼宇 BMS 项目要把 CX 控制器上挂的 64 路 PT1000 温度传感器(EL3208 端子)暴露给 Honeywell EBI 上位机做趋势记录与报警。每个 AI 都需要带:工程单位 ℃、量程 -50~150、超 30°C 持续 60 秒发 OFFNORMAL 报警走 NC10。
- **价值**:声明一个 `FB_BACnet_AI := (sObjectName := ..., fHighLimit := 30, nNotificationClass := 10);` 后周期调用,BACnet 协议层、Intrinsic Reporting、COV 推送全部由 stack 处理。手写 BACnet/IP 报文 + 报警延时计数 + COV 订阅管理需要 2000+ 行;此处一行声明完成。
- **替代方案对比**:
  - 直接用 ADS 把温度送出去:只能给 Beckhoff 自家 SCADA 用,跨厂商 BMS 不识别
  - 用 Modbus TCP 暴露:协议层只能传寄存器,丢失 BACnet 标准的"工程单位/量程/报警限"语义,BMS 要靠手动配点匹配
  - 用 `FB_BACnet_AI_IO`(K-bus)/ `FB_BACnet_AI_ECAT`(EtherCAT)直接链接端子:省掉 PLC 中转,适合"传感器值不经 PLC 加工"的简单工程;经过 PI 滤波 / 比例换算后才暴露的场景仍用本基础类

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §3.1、§3.2、§6.1.1、§6.1.2、§6.2.2(Event Reporting)、§9.2(典型 AI 配置)、§9.3(_IO / _ECAT 端子链接)、§9.10(报警限)、§9.12(用 AI 做 trendlog 数据源)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html(§6.1.1 对象类型表);命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_AV`(虚拟值,可写)、`FB_BACnet_AI_IO` / `_ECAT` / `_Raw`(本 FB 后缀变体)、`FB_BACnet_NC`(报警接收方)、`FB_BACnet_TLog`(以本 FB 做数据源做趋势)
