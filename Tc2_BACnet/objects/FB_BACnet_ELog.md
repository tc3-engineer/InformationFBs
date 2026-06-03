# FB_BACnet_ELog

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Event Log` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_ELog.TcPOU`](../examples/P_Demo_FB_BACnet_ELog.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Event Log」对象类型(BACnet Object_Type = 25 / Event Log)。本地存事件 / 报警的日志缓冲,常用于网络断时把 NC 路由不出去的报警先存本地,网络恢复后让 BMS 拉走。PDF §9.9 / §9.12 给完整示例。本库提供基础类(纯 BACnet 缓冲)+ `_Buf` 变体(`FB_BACnet_ELogBuf`,在 PLC 端额外暴露 `aLogBuffer : T_BACnet_ELogBuffer` 数组让 PLC 本地读)。ELog 自动收集本机所有 NC 实例号 = 自身 nObjectInstance 的事件(PDF §6.2.5)。

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
| 实例号 | `nObjectInstance` | `UDINT` | 与目标 NC 实例号相同,自动收集该 NC 路由的事件 |
| 控制 | `bLogEnable` | `BOOL` | Enable(总开关) |
| 缓冲容量 | `nBufferSize` | `UDINT` | Buffer_Size(条数) |
| 起止时间 | `stStartTime` / `stStopTime` | `ST_BA_DateTime` | Start_Time / Stop_Time |
| 通知 | `nNotificationClass` / `nNotificationThreshold` | `UDINT` / `UDINT` | 缓冲使用率到阈值通知 |
| Process ID 过滤 | `nProcessId` | `UDINT` | Process_Identifier_Filter(只收 NC.Recipient 用 process id = 本值的事件,见 §9.9) |
| `_Buf` 增 | `aLogBuffer` | `ARRAY OF ST_BACnet_EventLogEntry` | PLC 端本地缓冲(字段见 §9.13) |

### 后缀变体(PDF §6.1.2)

| 变体 | 增/删的成员 | 用途 |
|---|---|---|
| `FB_BACnet_ELog` | — | 基础类 |
| `FB_BACnet_ELogBuf` | 增 `aLogBuffer : T_BACnet_ELogBuffer` | PLC 端本地缓冲数组(PDF §9.13) |

## 3. 行为说明

FB_BACnet_ELog 每周期调用一次。本机所有 `FB_BACnet_NC.nObjectInstance == fbELog.nObjectInstance` 的Notification Class 路由的事件,自动也写一份到本 ELog 缓冲。这是 BACnet 标准的ELog 与 NC 按实例号自动配对机制(PDF §6.2.5 明确)。`_Buf` 变体下 PLC 可读 `aLogBuffer[i].dtTime / .eType / .stStatus / .stNotification` 做本地报警历史可视化(PDF §9.13 字段说明:eStatus / eTimesync / eNotification 三种 entry 类型)。也可用 `nProcessId` 接收外部 BACnet 设备转发来的事件(PDF §9.9 示例:Device 2 的 ELog 接收 Device 1 的 NC 路由)。

## 4. 错误码 / 返回值

无返回值。⚠️ PDF + InfoSys 未列具体 error 常量。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **ELog 与 NC 必须按实例号配对**:`fbELog.nObjectInstance := 10` 自动收 `FB_BACnet_NC` 中 `nObjectInstance := 10` 路由的事件。
- **`_Buf` 变体的字段语义见 PDF §9.13**:`eType=eStatus` 是状态变化、`eTimesync` 是时间同步消息、`eNotification` 是事件(含 stNotification 子结构)。
- **接收外部设备事件用 `nProcessId`**:PDF §9.9 完整示例 — 报警发送设备的 NC.Recipient 用 process id 42,接收设备的 ELog 设 nProcessId := 42 即可自动接收。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_ELog.TcPOU`](../examples/P_Demo_FB_BACnet_ELog.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_ELog
VAR
    fbAlarmNC : FB_BACnet_NC := (
        nObjectInstance := 42, nNotificationClass := 42,
        aAckRequired := [TRUE, TRUE, TRUE], aPriority := [10, 11, 12]);
    fbAlarmELog : FB_BACnet_ELogBuf := (
        sObjectName := 'AlarmHistory_NC42',
        nObjectInstance := 42,
        bLogEnable := TRUE);
END_VAR
fbAlarmNC();
fbAlarmELog();
```

## 7. 业务场景与实际价值

- **场景**:楼控项目网络偶尔故障,故障期间 NC 路由不出去的报警必须本地存档,网络恢复后让 BMS 一次拉走,确保零丢失。
- **价值**:BACnet 标准的事件日志,BMS 用 ReadRange 拉历史;ELog 与 NC 自动配对省去 PLC 写胶水代码。
- **替代方案对比**:用 Tc3_EventLogger:Beckhoff 自家,跨厂商 BMS 不通用;用 SD 卡写文件:运维要管文件,BMS 不能远程拉。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1(ELOG = Eventlog)、§6.2.5(Event-Logging 综述)、§9.9(外部设备事件接收)、§9.12(综合示例 fbELog_NC42)、§9.13(`_Buf` 字段说明)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_ELogBuf`(本 FB 后缀变体)、`FB_BACnet_NC`(事件源)、`FB_BACnet_TLog` / `TLogBuf`(趋势日志)
