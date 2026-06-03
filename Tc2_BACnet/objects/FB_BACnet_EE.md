# FB_BACnet_EE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Event Enrollment` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_EE.TcPOU`](../examples/P_Demo_FB_BACnet_EE.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Event Enrollment」对象类型(BACnet Object_Type = 9 / Event Enrollment)。用于在 Intrinsic Reporting 之外做算法 / 阈值监测 — 比如给 AV 加预警限(Intrinsic Reporting 已经监测 fHighLimit 报警限,EE 再监测一组更低的预警限,触发不同 NC)。EE 通过 `stEventParameter` 配置事件类型(`eOutOfRange` / `eChangeOfState` / `eChangeOfBitstring` 等),通过 `stObjectPropertyReference` 指定监测的目标属性。PDF §9.10 给完整双限报警示例。本对象类型本库仅基础类。

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
| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |
| 监测目标 | `stObjectPropertyReference` | `ST_BACnet_ObjectPropertyReference` | Object_Property_Reference(监测哪个对象的哪个属性) |
| 事件参数 | `stEventParameter` | `ST_BACnet_EventParameter` | Event_Parameters(事件类型 + 类型相关阈值) |
| 通知类型 | `eNotifyType` | `E_BACnet_NotifyType` | Notify_Type(`eAlarm` / `eNotifyEvent`) |
| 通知路由 | `nNotificationClass` | `UDINT` | Notification_Class |
| 通用 | `aEventEnable` / `aEventMessageTextsConfig` | 同 AI | Event_Enable / Event_Message_Texts_Config |

## 3. 行为说明

FB_BACnet_EE 每周期调用一次。stack 周期监测 `stObjectPropertyReference` 指向的目标属性的值,按 `stEventParameter.eEventType` 决定监测算法:`eOutOfRange` 比 stEventArgs.stOutOfRange 中的 fLowLimit / fHighLimit 范围;`eChangeOfState` 监测值变化为指定状态;`eChangeOfBitstring` 监测位串特定位变化;还有 eFloatingLimit / eBufferReady 等更复杂的事件类型。命中则按 `aEventEnable` 决定触发哪个事件(OFFNORMAL / FAULT / NORMAL)→ 走 `nNotificationClass` 指定的 NC 路由 →按 `eNotifyType` 标记为 alarm 或 event。PDF §9.10 双限报警示例:同一个 fbAv 既启用 Intrinsic Reporting(报警限 fLowLimit / fHighLimit)走 NC10,又用 EE(预警限 fLowLimit / fHighLimit)走 NC20,BMS 端看到两个事件等级。

## 4. 错误码 / 返回值

无返回值。⚠️ PDF + InfoSys 未列具体 error 常量。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **EE 适合补充而不是替代 Intrinsic Reporting**:对象自身的 Intrinsic Reporting 是 BACnet 标准首选;EE 主要用于多套阈值 / 复杂算法。
- **`eOutOfRange` 阈值配在 stEventArgs.stOutOfRange 子结构里**:PDF §9.10 示例显示嵌套结构,容易写漏 `stEventArgs := (stOutOfRange := (...))`。
- **EE 的 Notify_Type 通常设 `eNotifyEvent`**:与 Intrinsic Reporting 的 alarm 区分开,BMS 端用不同颜色显示。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_EE.TcPOU`](../examples/P_Demo_FB_BACnet_EE.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_EE
VAR
    fbAv : FB_BACnet_AV := (sObjectName := 'TempAv', bEnPgm := TRUE);
    fbEE : FB_BACnet_EE := (
        sObjectName := 'TempPrewarning',
        nNotificationClass := 20,
        eNotifyType := E_BACnet_NotifyType.eNotifyEvent,
        aEventEnable := [TRUE, TRUE, TRUE],
        stEventParameter := (
            eEventType := E_BACnet_EventType.eOutOfRange,
            stEventArgs := (stOutOfRange := (
                nTimeDelay := 0, fLowLimit := 25.0, fHighLimit := 82.0, fDeadband := 0.0))),
        stObjectPropertyReference := F_BACnet_Reference(fbAv, PropPresentValue));
END_VAR
fbAv();
fbEE();
```

## 7. 业务场景与实际价值

- **场景**:楼控加预警限 — 温度 5°C 报警(走 NC10 红色 alarm),温度 10°C 预警(走 NC20 黄色 event)给运维一个缓冲时间。
- **价值**:在不重叠 Intrinsic Reporting 报警的前提下加预警限,等同于 BACnet 标准的双限报警。
- **替代方案对比**:用第二个 AV 复制阈值监测:重复对象浪费 router memory + BMS 端 UI 杂乱;EE 标准化优雅。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1(EE = EventEnrollment)、§6.2.2.2(Algorithmic Change Reporting)、§9.10(预警限完整示例)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_NC`(路由)、`FB_BACnet_AI` / `AV` / `BV`(被监测的对象);Intrinsic Reporting 的字段直接在被监测对象上配,EE 是 Algorithmic Reporting
