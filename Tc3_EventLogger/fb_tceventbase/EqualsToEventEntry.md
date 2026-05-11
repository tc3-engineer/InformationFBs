# EqualsToEventEntry

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventBase` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5007225483.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_EqualsToEventEntry.xml`](../examples/P_Demo_EqualsToEventEntry.xml) |

---

## 1. 功能简述

`FB_TcEventBase.EqualsToEventEntry()` 比较当前事件与给定 `TcEventEntry` 是否对应同一事件定义。

粒度中等：比较 EventClass GUID + EventID + Severity 三件套，**不**比较 Arguments。适合"是否同一种事件"的判断，与 Arguments 无关。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    OtherEventClass : GUID;
    nOtherEventID : UDINT;
    eOtherSeverity : TcEventSeverity;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `OtherEventClass` | `GUID` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `nOtherEventID` | `UDINT` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `eOtherSeverity` | `TcEventSeverity` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

接收 `stEventEntry : TcEventEntry` 结构体，返回 BOOL。三件套（GUID + EventID + Severity）全相同时返回 TRUE，任一字段不同返回 FALSE。Arguments 不在比较范围内——同一事件即便参数不同也会被认作相等。

**典型用法**：在 PLC 工程里维护一张已知事件清单 `aKnownEvents : ARRAY[1..N] OF TcEventEntry`，新来的事件遍历这张表用本方法快速识别属于哪种已知事件，再分流到对应的处理逻辑。比 EqualsToEventClass 粒度更细（多看 EventID + Severity），比 EqualsTo 更宽松（忽略 Arguments）。

## 4. 错误码 / 返回值

本方法/函数返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | EventClass + EventID + Severity 全匹配 | 属于同一事件定义 |
| `FALSE` | 任一字段不同 | 不同事件 |

## 5. 使用注意 / 常见坑

- 不比较 Arguments——相同事件不同参数会被认作相等。需要更严格用 `EqualsTo`。
- Severity 字段也参与比较：同 GUID+EventID 不同 Severity 返回 FALSE。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_EqualsToEventEntry.xml`](../examples/P_Demo_EqualsToEventEntry.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

ADS 错误集中报警：把 ADS 错误码先转 TcEventEntry，再用本方法在已知清单里查类型


一次调用替代三字段比较，且语义明确


`EqualsToEventClass` → 粒度更粗；`EqualsTo` → 粒度更细（含 Arguments）


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.9.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5007225483.html
- **相关**：`FB_TcEventBase.EqualsTo`, `FB_TcEventBase.EqualsToEventClass`, `FB_TcEventBase.EqualsToEventEntryEx`
