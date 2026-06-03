# FB_BACnet_BI

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Binary Input` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_BI.TcPOU`](../examples/P_Demo_FB_BACnet_BI.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Binary Input」对象类型(BACnet Object_Type = 3 / Binary Input)。语义上是只读二进制输入,典型用于灯具状态反馈、保险丝状态、开关位置反馈等单 bit 信号。Present_Value 为 `BACnetBinaryPV` 枚举(`inactive` / `active`)。属于「无后缀基础类」,另提供 `_IO`(K-bus 端子)、`_ECAT`(EtherCAT 端子)两种变体后缀。

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
| 基本信息 | `iParent` / `sObjectName` / `sDescription` / `sDeviceType` | `I_BACnet_View` / `STRING(*)` | DPAD 父节点 + 名称 |
| 文本 | `sInactiveText` / `sActiveText` | `STRING(*)` | Inactive_Text / Active_Text(在 BMS 上替代 0/1 显示的两个标签) |
| Present_Value | `bVal` | `BOOL` | PLC 直接喂的 Present_Value(基础类) |
| Polarity | `ePolarity` | `E_BACnet_Polarity` | Polarity(`eNormal` / `eReverse`,反向时 PLC 0 → BACnet active) |
| 报警 | `bAlarmValue` | `BOOL` | Alarm_Value(BACnet 标准的「哪个状态算报警态」) |
| 报警 | `bEventDetectionEnable` / `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` / `nTimeDelay` / `nTimeDelayNormal` | 同 AI | Intrinsic Reporting |
| 统计 | `nChangeOfStateCount` / `dtChangeOfStateTime` / `tElapsedActiveTime` | `UDINT` / `DT` / `TIME` | Change_Of_State_Count / Time / Elapsed_Active_Time(BACnet 标准统计) |

### 后缀变体(PDF §6.1.2)

| 变体 | 增/删的成员 | 用途 |
|---|---|---|
| `FB_BACnet_BI` | — | 基础类:PLC 喂 `bVal` |
| `FB_BACnet_BI_IO` | 增 `bRawVal AT %I* : BOOL` | 通过 `TcLinkTo` 链接 K-bus 端子通道 |
| `FB_BACnet_BI_ECAT` | 增 `bRawVal AT %I* : BOOL`、`nRawECatState : UINT` | 链接 EtherCAT 端子通道 |

## 3. 行为说明

FB_BACnet_BI 每周期调用一次,库内部把 `bVal`(或 raw bRawVal 经 polarity 翻转)送到 stack 的 Present_Value。`sInactiveText` / `sActiveText` 让 BMS 显示具体语义(`Off`/`On`、`Closed`/`Open`)而不只是 0/1。Intrinsic Reporting 简单粗暴:当 `bVal = bAlarmValue` 持续 `nTimeDelay` 秒后,Event_State 切到 TO_OFFNORMAL 并向 `nNotificationClass` 指定的 NC 实例上报报警(PDF §3.2.45 + §9.8)。`_IO` / `_ECAT` 变体下,Present_Value 由端子值经 `ePolarity` 反向后自动得出,无需 PLC 介入。BACnet 标准的 Change_Of_State_Count / Elapsed_Active_Time 由 stack 自动累加,PLC 端只读不写。PDF §9.4 示例显示如何用 `stSettings.aDisabled` 把不必要的统计属性(`PropChangeOfStateCount` / `PropChangeOfStateTime` / `PropTimeOfStateCountReset`)从对象暴露面里删掉。

## 4. 错误码 / 返回值

无返回值;`stStatusFlags.bInAlarm/bFault/bOverridden/bOutOfService` 暴露运行状态。⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码常量。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **`ePolarity` 是 BACnet 标准属性,不是物理反向**:`eReverse` 让 BACnet 端的`inactive/active` 与 PLC bVal 的 0/1 相反,适合「高电平=故障」接线习惯但 BMS 希望「故障=active」显示的场景。
- **`bAlarmValue` 决定报警的方向**:`bAlarmValue := TRUE` 表示「激活态=报警态」(典型用于「门未关」报警);`bAlarmValue := FALSE` 用于「非激活态=报警态」(典型用于「心跳信号丢失」)。
- **不要每周期写 `sActiveText` / `sInactiveText`**:这些是配置属性,运行时 BMS 也可能改,用条件触发(PDF §6.3.1)。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_BI.TcPOU`](../examples/P_Demo_FB_BACnet_BI.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_BI
VAR
    fbDoorOpen : FB_BACnet_BI := (
        sObjectName := 'Door_3F_East',
        sDescription := 'Floor 3 East door open switch',
        sInactiveText := 'Closed',
        sActiveText := 'Open',
        ePolarity := E_BACnet_Polarity.eNormal,
        bAlarmValue := TRUE,
        bEventDetectionEnable := TRUE,
        nNotificationClass := 11,
        nTimeDelay := 30);
    bDoorSensorPlc : BOOL;
END_VAR
fbDoorOpen.bVal := bDoorSensorPlc;
fbDoorOpen();
```

## 7. 业务场景与实际价值

- **场景**:楼宇安防 — 100 个房间门磁开关,每个门状态要暴露给 BMS,门开超 30 秒发报警。
- **价值**:一行声明 + 一行调用,BACnet 协议层、状态文本、报警延时全部由 stack 处理。
- **替代方案对比**:用 `_IO` 变体直接绑端子省 PLC 中转;用基础类适合「门信号要被 PLC 加工(消抖、组合逻辑)后再暴露」的场景。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1、§6.1.2、§3.2.45(Alarm_Value)、§9.4(disable 属性)、§9.8(配 NC)、§9.16(数组初始化)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_BO`(可写二进制输出)、`FB_BACnet_BV`(虚拟二进制值)、`FB_BACnet_BI_IO` / `_ECAT`(本 FB 后缀变体)、`FB_BACnet_NC`(报警接收方)
