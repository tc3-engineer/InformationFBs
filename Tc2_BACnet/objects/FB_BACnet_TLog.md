# FB_BACnet_TLog

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Trend Log` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_TLog.TcPOU`](../examples/P_Demo_FB_BACnet_TLog.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Trend Log」对象类型(BACnet Object_Type = 20 / Trend Log)。按周期 / COV / 触发模式记录另一个对象属性(典型 Present_Value)的时序数据,缓存到 router memory 的循环缓冲区中,BMS 端通过 `ReadRange` 服务读出做趋势图。PDF §9.12 / §9.13 给完整示例。本库提供基础类(纯 BACnet 缓冲)+ `_Buf` 变体(`FB_BACnet_TLogBuf`,在 PLC 端额外暴露 `aLogBuffer : T_BACnet_TLogBuffer` 数组,让 PLC 本地可视化历史数据)。

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
| 触发源 | `stObjectPropertyReference` | `ST_BACnet_ObjectPropertyReference` | Log_Device_Object_Property(`F_BACnet_Reference(fbAv, PropPresentValue)`) |
| 采集模式 | `eLoggingType` | `E_BA_LoggingType` | Logging_Type(`ePolled` / `eCOV` / `eTriggered`) |
| 采集间隔 | `nLogInterval` | `UDINT` | Log_Interval(1/100 秒,如 300 = 3 秒) |
| 控制 | `bLogEnable` / `bTrigger` | `BOOL` | Enable / Trigger(eTriggered 模式下置 TRUE 触发一次采集) |
| 起止时间 | `stStartTime` / `stStopTime` | `ST_BA_DateTime` | Start_Time / Stop_Time |
| 缓冲容量 | `nBufferSize` | `UDINT` | Buffer_Size(条数) |
| COV 模式 | `nCOVResubscriptionInterval` / `stClientCOV` | `UDINT` / `ST_BACnet_ClientCOV` | COV_Resubscription_Interval / Client_COV_Increment |
| 通知 | `nNotificationClass` / `nNotificationThreshold` | `UDINT` / `UDINT` | 缓冲使用率到阈值触发通知 |
| `_Buf` 增 | `aLogBuffer` | `ARRAY OF ST_BA_TrendEntry` | PLC 端本地缓冲(字段见 §9.13) |

### 后缀变体(PDF §6.1.2)

| 变体 | 增/删的成员 | 用途 |
|---|---|---|
| `FB_BACnet_TLog` | — | 基础类:缓冲仅在 router memory |
| `FB_BACnet_TLogBuf` | 增 `aLogBuffer : T_BACnet_TLogBuffer` | PLC 端额外可读本地缓冲数组(PDF §9.13) |

## 3. 行为说明

FB_BACnet_TLog 每周期调用一次。`ePolled` 模式下 stack 按 `nLogInterval` 间隔采样 stObjectPropertyReference 指向的属性,写一条记录;`eCOV` 模式下被采样对象自身触发 COV 时记录(PDF §9.12 `fbTLogCov` 示例,需配 `nCOVResubscriptionInterval` 与 `stClientCOV` 指定增量);`eTriggered` 模式下 PLC 写 `bTrigger := TRUE` 触发一次记录(适合按门禁刷卡事件采样温度等)。`bLogEnable` 是总开关,FALSE 时不记录,记录时也写一条 type=eStopLogging 的事件条目。缓冲区满后行为按 `bStopWhenFull` 决定:TRUE 停止记录,FALSE 覆盖最老条目。`_Buf` 变体下 PLC 可直接读 `aLogBuffer[i].dtTime / .eType / .uValue` 做本地趋势可视化(PDF §9.13 详细字段:eBinary / eAnalog / eMultistate / eEvent + bStart / bStop / bBufferPurged / bInterrupted 状态位)。

## 4. 错误码 / 返回值

无返回值。`stStatusFlags.bFault = TRUE` 在被采样对象不可达 / Reference 无效时置位。⚠️ PDF + InfoSys 未列具体 error 常量。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **TLog 占内存大**:每条记录约 56 字节(PDF §6.5.1),Buffer_Size = 1008(7 天 × 24 × 6 次/小时)占约 56 KB router memory;一个项目几十个 TLog 容易撑满 32 MB 默认 router memory。
- **`eCOV` 模式不要乱用**:被采样对象 COV 太频繁(如 fCovIncrement=0)会让 TLog 缓冲瞬间撑满。
- **`_Buf` 变体的本地数组访问受同步约束**:PDF §9.13 警告读 `aLogBuffer` 时要避开 stack 写入瞬间;实际工程用 R_TRIG 仅在外部条件触发时读取。
- **触发型 TLog 的 `bTrigger` 是脉冲**:置 TRUE 后 stack 记一条,PLC 应配 R_TRIG 把 bTrigger 改为单脉冲避免重复触发。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_TLog.TcPOU`](../examples/P_Demo_FB_BACnet_TLog.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_TLog
VAR
    fbRoomTemp : FB_BACnet_AI := (sObjectName := 'RoomTemp_3F');
    fbRoomTempTLog : FB_BACnet_TLog := (
        sObjectName := 'RoomTemp_3F_TLog',
        eLoggingType := E_BA_LoggingType.ePolled,
        nLogInterval := 300,
        bLogEnable := TRUE,
        stObjectPropertyReference := F_BACnet_Reference(fbRoomTemp, PropPresentValue));
END_VAR

fbRoomTemp();
fbRoomTempTLog();
```

## 7. 业务场景与实际价值

- **场景**:运维想在 BMS 上看每个房间温度的过去 7 天趋势,做空调系统的舒适度审计,无需在 PLC 上额外装 SQL 数据库。
- **价值**:BACnet 标准的 ReadRange 服务跨厂商通用,BMS 端不需要写自定义协议;TLog 自带按时间 / 按序号查找,通信效率高。
- **替代方案对比**:用 PLC 内部 Tc3_EventLogger:Beckhoff 自家生态;用 SQL 历史库:运维要管数据库,第三方 BMS 不易接入。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1(Tlog = Trendlog)、§6.2.4(Trend-Logging 综述)、§6.5.1(内存计算示例)、§9.12(TLog/TLogCov/TLogBuf 示例)、§9.13(`_Buf` 字段处理)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_TLogBuf`(本 FB 后缀变体)、`FB_BACnet_TLM`(多通道趋势)、`FB_BACnet_ELog` / `_Buf`(事件日志);采集源可以是 AI / AV / BV / MV 等
