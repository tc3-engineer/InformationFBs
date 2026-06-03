# FB_BACnet_SchedM

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Schedule Multistate` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_SchedM.TcPOU`](../examples/P_Demo_FB_BACnet_SchedM.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Schedule Multistate」对象类型,周程序时间表 — 按 Monday..Sunday 每天定义一组「时刻 → 值」对(类型 `UDINT`),stack 每分钟检查当前时刻,把对应值写到所有 `aObjectPropertyReferences` 列出的目标对象属性。Schedule 可以引用一个或多个 Calendar 做例外日(节假日不同时间表),也可直接在 `aException` 内联例外。本变体处理多态枚举值(运行场景 Day/Night/Eco、灯光场景 1/2/3 等)。 PDF §9.11 给完整示例。

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
| 每周时间表 | `aWeek` | `ARRAY[1..7] OF ST_BACnet_SchedWeek*` | Weekly_Schedule(Monday..Sunday 各自的 时刻 → 值 对) |
| 当前值 | `bPresVal` / `fPresVal` / `nPresVal`(按变体取一) | `UDINT` | Present_Value(当前时段对应的 UDINT 值) |
| 默认值 | `bScheduleDefault` / `fScheduleDefault` / `nScheduleDefault` | 同 Present_Value 类型 | Schedule_Default(每天 0 点 / 任何「无定义」时刻使用) |
| Calendar 例外 | `aCalendar` | `ARRAY OF ST_BACnet_SchedCalRef` | List_Of_Calendars(每项含 `iRefCalendar + aEntry`,Cal.PresVal=TRUE 那天用 aEntry 代替 aWeek) |
| 内联例外 | `aException` | `ARRAY OF ST_BACnet_SchedException` | Exception_Schedule(节假日 / 单日 / 区间内联,优先级高于 aWeek) |
| 目标对象 | `aObjectPropertyReferences` | `ARRAY OF ST_BACnet_ObjectPropertyReference` | List_Of_Object_Property_References(把 Present_Value 写到哪些对象的哪个属性) |
| 写优先级 | `nPriorityForWriting` | `USINT` | Priority_For_Writing(写目标对象用什么 BACnet 优先级,默认 16) |

## 3. 行为说明

FB_BACnet_Schedule 每周期调用一次,stack 每分钟比较当前时刻与本周对应天的 aWeek 表,取该时刻已过的最后一个「时刻 → 值」对作为 Present_Value;在每天 0 点开始时若 aWeek[今日]为空,则使用 Schedule_Default。`aCalendar` / `aException` 的判定优先级高于 aWeek:Cal.PresVal=TRUE 或 Exception 命中时用对应 aEntry 替换。`aObjectPropertyReferences` 列出目标对象 + 属性 ID(如 `(iObject := fbAO, ePropertyId := PropPresentValue)`),stack 在 Present_Value 变化时用 `nPriorityForWriting` 写一次目标对象。PDF §9.11 用 F_BACnet_SchedWeekly3xM 帮助函数声明周程序(如 `F_BACnet_SchedWeekly3xM(eMonday, eFriday, T#0H, ..., T#6H, ..., T#20H, ...)` 表示周一到周五对应时刻取对应值,非 aWeek 中提到的时刻继承前一时段值)。

## 4. 错误码 / 返回值

无返回值。⚠️ PDF + InfoSys 未列具体 error 常量。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **改 Schedule 用条件触发**:运行时改 aWeek / aException 要用 `IF bChanged THEN ...; bChanged := FALSE; END_IF`,周期写会覆盖 BMS 端调整。
- **`bWriteException` 是特殊触发位**:PDF §9.11 示例显示 `fbSchedM.bWriteException := TRUE;` 用来强制把当前修改的 aCalendar 项写到 stack(运行时改后必须置位才生效)。
- **不要把多个 Schedule 写到同一目标属性**:目标对象的优先级槽位会被几个 Schedule 抢,行为不确定;改用一个 Schedule + Calendar 做不同情况切换。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_SchedM.TcPOU`](../examples/P_Demo_FB_BACnet_SchedM.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_SchedM
VAR
    fbSched : FB_BACnet_SchedM := (
        sObjectName := 'MultistateSchedule',
        aWeek := F_BACnet_SchedWeekly3xM(
            E_BA_Weekday.eMonday, E_BA_Weekday.eFriday,
            T#0H, 2,
            T#7H, 1,
            T#19H, 2));
END_VAR
fbSched();
```

## 7. 业务场景与实际价值

- **场景**:工作日 7 点开空调到 22°C / 开灯 / 切运行模式,19 点切回 18°C / 关灯 / 待机;周末与节假日(引用 PublicHolidays Calendar)按 Schedule_Default 节能运行。
- **价值**:BACnet 标准的时间表,BMS 端可视化拖时段;PLC 端把工程量写到下游 AO/BO/MO 全自动。
- **替代方案对比**:用 PLC 内部 TON + IF 判断当前时刻:跨节假日要 PLC 写一堆 IF,BMS 看不到时间表内容。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1(SchedA/B/M = Schedule Multistate)、§9.11(Calendar + Schedule 完整示例)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_SchedA` / `FB_BACnet_SchedB`(REAL / 布尔变体)、`FB_BACnet_Cal`(节假日表)、`FB_BACnetRM_SchedM`(远端 Schedule 引用)
