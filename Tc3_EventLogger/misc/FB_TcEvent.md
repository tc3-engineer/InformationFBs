# FB_TcEvent

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5002372619.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcEvent.xml`](../examples/P_Demo_FB_TcEvent.xml) |

---

## 1. 功能简述

`FB_TcEvent` 是 TwinCAT 3 EventLogger 中代表**只读事件视图**的功能块——在 `FB_ListenerBase2` 的回调里收到的 `fbEvent : REFERENCE TO FB_TcEvent` 就是它。

本 FB 只提供**读方法和读属性**，不能修改事件——访问 EventClass / EventID / Severity / 时间戳 / ipArguments / ipSourceInfo / GetJsonAttribute / EqualsTo* 等元信息。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

FB_TcEvent 是只读视图，自身没有顶层 VAR_INPUT/OUTPUT。通过继承 `FB_TcEventBase` 拿到 base 类的所有读方法（EqualsTo / RequestEventText / GetJsonAttribute / ipArguments / ipSourceInfo …），但**不**提供 Raise / Clear / Confirm 这种状态改写。

**使用场景**：listener 回调里的 fbEvent 参数；从 EventLogger API 拿到的事件查询结果。**注意**：fbEvent 引用只在回调期间有效，不要拷贝。需要保存事件数据请拷贝具体字段（如 GUID / EventID / 时间戳）。

## 4. 错误码 / 返回值

本方法/属性不返回数值（`VOID` 或 getter 直接返回引用）。状态通过 EventLogger 的事件日志间接反映。

## 5. 使用注意 / 常见坑

- fbEvent 引用只在回调期间有效——回调返回后失效。
- 禁止拷贝 fbEvent 引用到全局变量。
- FB_TcEvent 是只读——别试图调 Raise / Clear，方法不存在。
- 需要事件数据请拷贝出 GUID / EventID / Severity / 时间戳到本地变量再用。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcEvent.xml`](../examples/P_Demo_FB_TcEvent.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

listener OnAlarmRaised 回调里读 fbEvent 的元数据用于自定义处理


统一的只读事件视图——所有 EventLogger 回调用同一接口，业务侧不区分 alarm/message


把每种事件用专门类型 → 接口爆炸；本 FB 一个视图覆盖所有


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5002372619.html
- **相关**：`FB_TcAlarm`, `FB_TcMessage`, `FB_TcEventBase`, `FB_ListenerBase2.OnAlarmRaised`
