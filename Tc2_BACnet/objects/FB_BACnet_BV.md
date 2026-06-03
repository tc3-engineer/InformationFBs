# FB_BACnet_BV

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Binary Value` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_BV.TcPOU`](../examples/P_Demo_FB_BACnet_BV.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Binary Value」对象类型(BACnet Object_Type = 5 / Binary Value)。语义上是虚拟二进制值,典型用于程序内部状态、报警标志、设备故障汇总位等「非物理 I/O 但需要被 BMS 读写或订阅」的场景。基础类支持 16 优先级槽位(行为同 BO,但 priority 6 不被 Min_On/Off 占用)。本库提供基础类 + `_5P`(5 优先级)+ `_Event`(只读 + Event Reporting,PDF §9.8 示例 fbBV1 / fbBV2)三种变体。

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
| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD 父节点 + 名称 |
| 文本 | `sInactiveText` / `sActiveText` | `STRING(*)` | Inactive_Text / Active_Text |
| Present_Value 命令(基础类 + `_5P`) | `bEnPgm` / `bValPgm` | `BOOL` | PLC 在 Program 优先级写值 |
| `_5P` 增 | `bEnSfty/bValSfty` 等 5 优先级 | `BOOL` | 同 `FB_BACnet_BO_5P` |
| 回退 | `bRelinquishDefault` | `BOOL` | 16 槽位全 NULL 时回退值 |
| Present_Value 直写(`_Event`) | `bPresVal` 或 `bVal`(只读暴露) | `BOOL` | PLC 写 Present_Value,BMS 只能读 |
| 报警 | `bAlarmValue` / `bEventDetectionEnable` / `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` / `nTimeDelay` / `nTimeDelayNormal` / `eNotifyType` | 同 BI | Intrinsic Reporting |
| 通知类型 | `eNotifyType` | `E_BACnet_NotifyType` | Notify_Type(`eAlarm` / `eNotifyEvent`,区分报警 vs 一般事件) |

### 后缀变体(PDF §6.1.2)

| 变体 | 增/删的成员 | 用途 |
|---|---|---|
| `FB_BACnet_BV` | — | 基础类,16 优先级 |
| `FB_BACnet_BV_5P` | 5 优先级槽位 | 楼控多优先级场景 |
| `FB_BACnet_BV_Event` | 只读 + 启用 Event Reporting | PLC 内部状态位,BMS 只能读但能订阅事件 |

## 3. 行为说明

基础类 BV 与 BO 的差别仅在语义(虚拟值不绑物理输出,priority 6 可被 PLC/BMS 使用),命令优先级机制完全相同。BV 最常见的用法见 PDF §9.8:`bAlarmValue := TRUE` + `aEventEnable := [TRUE,TRUE,TRUE]` 的纯报警 flag — PLC 把「过滤器堵塞」、「压力低低限」等汇总诊断布尔位写到 `bValPgm`,触发 NC 类对象向 BMS 发报警。`_Event` 变体把 Present_Value 改为只读(PLC 写 `bPresVal`,BMS 不能写),适合「PLC 是该位的唯一源,但希望 BMS 能订阅状态变化」的场景。Notify_Type(`eAlarm` vs `eNotifyEvent`)只是 BMS 端显示分类,不影响触发逻辑(PDF §6.2.2)。

## 4. 错误码 / 返回值

无返回值;运行状态通过 `stStatusFlags` 暴露。⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **命令优先级(commandable 对象)**:`_5P` 系列在 BACnet 16 个优先级中取 5 个槽位(LifeSafety=1 / Critical=5 / ManLocal=7 / ManOperator=8 / Program=15,默认值见 `BACnet_Param`),用 `bEnSfty` / `bEnCrit` / `bEnManLoc` / `bEnPgm` / `bEnManualOperator` 配对的 `f|b|nVal*` 写槽位。`bEn*` 由 TRUE 转 FALSE 等价于写 NULL(释放该槽位)。全部 16 槽位都为 NULL 时取 `fRelinquishDefault` / `bRelinquishDefault` / `nRelinquishDefault`(PDF §6.2.1 / §9.5 / §9.6)。
- **不写槽位也要每周期调用 FB**:库内部用周期调用驱动写值锁存到 BACnet stack;只置 `bEnPgm := TRUE` 而不调用 FB,值不会被发布。
- **BV 用作汇总报警 flag 时,务必同时声明对应 NC 实例**:`nNotificationClass := 10` + 没有 `FB_BACnet_NC` with `nObjectInstance := 10` → 报警发不出去(PDF §9.8 示例 fbBV1 + fbNC01)。
- **`_Event` 变体不能用 `bEnPgm + bValPgm`**:Present_Value 只读,PLC 用 `bPresVal := ...` 写,不参与优先级。
- **`eNotifyType` 与 `aEventMessageTextsConfig` 配合**:把字符串数组按 `[OFFNORMAL, FAULT, NORMAL]` 顺序填,比如 `['过滤器堵塞', '传感器故障', '已恢复']`。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_BV.TcPOU`](../examples/P_Demo_FB_BACnet_BV.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_BV
VAR
    // 过滤器堵塞汇总报警位:PLC 写,BMS 订阅
    fbFilterClogged : FB_BACnet_BV := (
        sObjectName := 'FilterClogged_AHU_3F',
        sInactiveText := 'OK',
        sActiveText := 'Clogged',
        bAlarmValue := TRUE,                  // active = 报警
        aEventEnable := [TRUE,TRUE,TRUE],
        bEventDetectionEnable := TRUE,
        nNotificationClass := 12,
        aEventMessageTextsConfig := ['过滤器堵塞', '传感器故障', '已恢复']);
    bFilterAlarmPlc : BOOL := FALSE;
END_VAR

fbFilterClogged.bEnPgm  := TRUE;
fbFilterClogged.bValPgm := bFilterAlarmPlc;
fbFilterClogged();
```

## 7. 业务场景与实际价值

- **场景**:空调机组的「过滤器堵塞」汇总报警 — PLC 通过压差传感器算出 `bFilterAlarmPlc`,需要让 BMS 知道并触发维护工单。
- **价值**:把「PLC 内部布尔位」包装成符合 BACnet 标准的 alarm 对象,BMS 可以直接订阅 alarm summary、生成工单,无需 PLC 单独发邮件 / 短信。
- **替代方案对比**:用 `_Event` 变体 BMS 只能读不能写(更安全,避免误操作);用 `_5P` 适合「多源都可置位汇总报警」场景。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1、§6.1.2(_5P / _Event)、§6.2.2(Event Reporting)、§9.6(WritePropertyNull 释放优先级)、§9.8(配 NC + recipient list)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_BI`(只读二进制输入)、`FB_BACnet_BO`(物理二进制输出)、`FB_BACnet_BV_5P` / `_Event`(本 FB 后缀变体)、`FB_BACnet_NC`(报警接收方)
