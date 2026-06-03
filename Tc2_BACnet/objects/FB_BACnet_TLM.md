# FB_BACnet_TLM

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Trend Log Multiple` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_TLM.TcPOU`](../examples/P_Demo_FB_BACnet_TLM.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Trend Log Multiple」对象类型(BACnet Object_Type = 27 / Trend Log Multiple)。与 TLog 类似但每条记录同时记录多个属性,适合需要同时刻多通道关联分析的场景(如同时记一个 AV 的 Present_Value、Status_Flags、Event_State 来排查报警时机)。BACnet 标准只允许周期 / 触发模式,不允许 COV 模式。PDF §9.12 末尾 `fbTLogM` 示例。本对象类型本库仅基础类,无后缀变体。

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
| 多通道数据源 | `aObjectPropertyReferences` | `ARRAY OF ST_BACnet_ObjectPropertyReference` | Log_Device_Object_Property(多个属性引用) |
| 采集模式 | `eLoggingType` | `E_BA_LoggingType` | Logging_Type(`ePolled` / `eTriggered`,不支持 eCOV) |
| 采集间隔 | `nLogInterval` | `UDINT` | Log_Interval(1/100 秒) |
| 控制 | `bLogEnable` / `bTrigger` | `BOOL` | Enable / Trigger |
| 起止时间 | `stStartTime` / `stStopTime` | `ST_BA_DateTime` | Start_Time / Stop_Time |
| 缓冲容量 | `nBufferSize` | `UDINT` | Buffer_Size |

## 3. 行为说明

FB_BACnet_TLM 每周期调用一次。`ePolled` 模式下 stack 按 `nLogInterval` 间隔采样所有 `aObjectPropertyReferences` 列出的属性,把它们打包成一条记录(每条记录的字段数等于引用数量)。BMS 端用 ReadRange 拉数据后做同一时间戳下多个属性值的关联分析。PDF §9.12 示例 `fbTLogM` 同时采 `fbAv.PresentValue` + `fbAv.StatusFlags` + `fbAv.EventState`,用 `nLogInterval := 50`(0.5 秒)做高频采样。TLM 不支持 eCOV 是因为多通道难以协调(几个属性 COV 事件几乎不会同时到达)。

## 4. 错误码 / 返回值

无返回值。⚠️ PDF + InfoSys 未列具体 error 常量。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **TLM 占内存比 TLog 大得多**:每条记录长度按属性数 × 单值大小估算,3 通道 × 12 字节 ≈ 36 字节;高频 0.5 秒采样 1 小时 = 7200 条 × 36 字节 ≈ 250 KB。
- **TLM 不支持 COV 模式**:必须用 ePolled 或 eTriggered;PDF §6.2.4 明确说明。
- **`aObjectPropertyReferences` 顺序固定**:每条记录字段位置与该数组下标一一对应,BMS 端按此顺序解释。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_TLM.TcPOU`](../examples/P_Demo_FB_BACnet_TLM.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_TLM
VAR
    fbAv : FB_BACnet_AV := (sObjectName := 'AlarmDebugSrc');
    fbTLM : FB_BACnet_TLM := (
        sObjectName := 'AlarmDebug_TLM',
        eLoggingType := E_BA_LoggingType.ePolled,
        nLogInterval := 50,
        bLogEnable := TRUE,
        aObjectPropertyReferences := [
            (iObject := fbAv, ePropertyId := PropPresentValue),
            (iObject := fbAv, ePropertyId := PropStatusFlags),
            (iObject := fbAv, ePropertyId := PropEventState)
        ]);
END_VAR
fbAv();
fbTLM();
```

## 7. 业务场景与实际价值

- **场景**:排查为什么报警没准时触发 — 需要同时记录 Present_Value 与 Status_Flags / Event_State 在同一时间戳下的关联,做事后分析。
- **价值**:TLM 一次性记录多通道,无需 BMS 端把多个 TLog 按时间戳合并;高频(50 = 0.5 秒)能捕获瞬态事件。
- **替代方案对比**:用多个 TLog:BMS 端要按时间戳合并(BACnet 标准没规定时间戳精度,合并误差大);TLM 同条记录天然对齐。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1(TLM = Trendlog Multiple)、§6.2.4(TLog/TLM 综述)、§9.12 末尾(`fbTLogM` 多通道示例)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_TLog` / `FB_BACnet_TLogBuf`(单通道趋势)、`FB_BACnet_ELog` / `_Buf`(事件日志)
