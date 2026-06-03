# FB_BACnet_NC

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Notification Class` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_NC.TcPOU`](../examples/P_Demo_FB_BACnet_NC.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Notification Class」对象类型(BACnet Object_Type = 15 / Notification Class)。它是 BACnet 报警 / 事件路由表 — 每个支持 Intrinsic Reporting 的对象(AI / AV / BI / BV / MI / MV / EE 等)通过 `nNotificationClass` 引用一个 NC 实例,该 NC 维护一张 `Recipient_List`,把符合订阅时间窗的OFFNORMAL / FAULT / NORMAL 事件按优先级分别发给所有 recipient(BMS / 报警接收 PLC / 邮件网关等)。PDF §9.8 / §9.9 给出多个完整示例。本对象类型本库仅基础类。

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
| 实例号 | `nObjectInstance` | `UDINT` | NC 对象实例号(被其它对象的 `nNotificationClass` 引用) |
| Notification Class | `nNotificationClass` | `UDINT` | 通常与 `nObjectInstance` 同值(BACnet 标准要求) |
| 优先级 | `aPriority` | `ARRAY[0..2] OF USINT` | Priority(OFFNORMAL / FAULT / NORMAL 三种类型各自的事件优先级 0..255) |
| 确认 | `aAckRequired` | `ARRAY[0..2] OF BOOL` | Ack_Required(OFFNORMAL / FAULT / NORMAL 是否需要 BMS 端 ack) |
| Recipient List | `aRecipientList` | `ARRAY OF ST_BACnet_NC_Recipient` | Recipient_List(订阅者表,详见 §9.8 示例) |

## 3. 行为说明

FB_BACnet_NC 每周期调用一次。它本身没有 Present_Value,作用是路由其它对象生成的事件。`nObjectInstance` 与 `nNotificationClass` 必须相等(BACnet 标准要求,且大多数实现按这个键关联)。其它对象设置 `nNotificationClass := 10` 后,这些对象产生 OFFNORMAL / FAULT / NORMAL 事件时,stack 会查找 `nObjectInstance := 10` 的 NC 实例,按 `aPriority[<事件类型>]` 给事件加优先级,把事件按 `aRecipientList` 中匹配 `stValidDays + stFromTime + stToTime` 的 recipient 发出。PDF §9.8 示例展示了两种 recipient:`F_BACnet_DeviceRecipient(nDeviceInstance := 42)` (按 BACnet device-id 解析,stack 自动用 Who-Is 发现);`F_BACnet_EthernetRecipient(...)`(直接给 IP / 端口 / 网络号,适合穿越路由器)。`bIssueConfirmed` 决定是否用 ConfirmedEventNotification(需 ack)还是 Unconfirmed(发即忘)。

## 4. 错误码 / 返回值

无返回值。事件路由失败时(recipient 联系不上、订阅窗口不匹配)stack 不报错,事件就静默丢弃 — 需要在 NC 实例的 Recipient_List 配合 BACnet Explorer 或抓包诊断。⚠️ PDF + InfoSys 未列具体 error 常量。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **`nObjectInstance` 不能与其它 NC 重复**:每个 NC 实例号唯一,且必须有一个对象 / EE 在引用,否则配了等于空跑。
- **`aPriority` 是 BACnet 标准的事件优先级(0..255),不是命令优先级(1..16)**:常用 OFFNORMAL=10 / FAULT=11 / NORMAL=12,让 BMS 显示报警等级。
- **空 recipient list 也合法**:PDF §9.8 示例 fbNC01_Standard 就是空列表 — 适合「BMS 自己来订阅,PLC 端不预定义 recipient」的场景。
- **预定义 recipient 与 BMS 后期订阅可共存**:PLC 端预定义的 + BMS Write 进来的会合并到 Recipient_List。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_NC.TcPOU`](../examples/P_Demo_FB_BACnet_NC.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_NC
VAR
    fbAlarmClass : FB_BACnet_NC := (
        nObjectInstance := 10,
        nNotificationClass := 10,
        sObjectName := 'NC_Alarms',
        aAckRequired := [TRUE, TRUE, FALSE],
        aPriority := [10, 11, 12]);
END_VAR
fbAlarmClass();
```

## 7. 业务场景与实际价值

- **场景**:楼控项目用 10 类 NC 把不同等级的报警分别路由 — NC10 给 BMS 主屏(需 ack),NC20 给运维微信报警网关(不 ack),NC30 给打印机(只记不显示)。每个 AI / BV 通过 `nNotificationClass` 选择把事件路由到哪个 NC。
- **价值**:BACnet 标准的报警路由,跨厂商 BMS 都识别;BMS 可远程改 Recipient_List 增删订阅。
- **替代方案对比**:用 ADS 把报警条目送到中心数据库:跨厂商不通;用 SNMP trap:协议层弱无法保证投递。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1(NC = Notification Class)、§3.2.18(Notification_Class)、§9.8(配 NC + recipient list)、§9.9(用 NC 做接收外部设备报警)、§9.10(预警限 + 双 NC)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_AI` / `BV` / `MV`(事件源)、`FB_BACnet_EE`(算法报警)、`FB_BACnet_ELog`(本地存报警)
