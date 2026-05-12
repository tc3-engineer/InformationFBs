# FB_TcEventBase

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5002595467.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcEventBase.xml`](../examples/P_Demo_FB_TcEventBase.xml) |

---

## 1. 功能简述

`FB_TcEventBase` 是 TwinCAT 3 EventLogger 体系的**事件基类**（base class），为 `FB_TcAlarm` / `FB_TcMessage` 提供共有的方法与属性：事件等值比较（`EqualsTo*`）、JSON 属性访问、引用释放、异步取事件文本（`RequestEventText` / `RequestEventClassName`）。

实际工程里**很少直接实例化**，而是声明 `FB_TcAlarm` / `FB_TcMessage` 后通过继承用上 base 的方法。唯一例外：`I_TcEvent` / `I_TcEventBase` 接口持有时，运行时可以拿到一个 base 视图。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

FB_TcEventBase 不直接维护状态，状态机在子类（Alarm 的三态、Message 的一次性 send）里实现。本基类只提供工具方法：EqualsTo 系列做事件等值比较（粒度从粗到细：EqualsToEventClass / EqualsToEventEntry / EqualsToEventEntryEx / EqualsTo）；RequestEventText 与 RequestEventClassName 异步取本地化文本，返回 `FB_AsyncStrResult` 句柄供轮询；GetJsonAttribute 读取 SetJsonAttribute 写入的扩展属性；Release 释放动态分配（NEW）出来的事件实例；属性 ipArguments 与 ipSourceInfo 分别访问参数列表与源信息子对象。

**继承方式**：业务代码声明 `FB_TcAlarm` 或 `FB_TcMessage` 实例，自动具备本基类的所有方法。持有 `I_TcEvent` / `I_TcEventBase` 接口时也能拿到基类视图调用通用 API，便于写「不区分 alarm 还是 message 的统一处理代码」（例如 listener 回调里一段代码处理所有事件）。

## 4. 错误码 / 返回值

本方法/属性不返回数值（`VOID` 或 getter 直接返回引用）。状态通过 EventLogger 的事件日志间接反映。

## 5. 使用注意 / 常见坑

- 不要直接 `VAR fb : FB_TcEventBase;` 然后调 `Create()`——base 没有 Create。声明 `FB_TcAlarm` 或 `FB_TcMessage`。
- `EqualsTo*` 系列方法名相近，混用容易得到不同语义：粒度最粗 EqualsToEventClass → 中 EqualsToEventEntry → 最细 EqualsTo（含 Arguments）。（工程经验补充）
- `Release()` 只在动态 NEW 时调；静态 VAR 实例调了会让 EventLogger 槽位提前回收。
- `RequestEventText` 不是同步——拿到 FB_AsyncStrResult 后必须轮询 IsCompleted() 才能读结果。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcEventBase.xml`](../examples/P_Demo_FB_TcEventBase.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

把已经持有的 `I_TcEvent` 接口转为 `FB_TcEventBase` 视图后调用通用方法（如比较两个事件、读 JSON）


所有事件类型共享一套"事件元数据访问"API，业务代码不需要区分 alarm vs message


为每个子类各写一套元数据 API → 重复劳动 + 不一致 bug


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5002595467.html
- **相关**：`FB_TcAlarm`, `FB_TcMessage`, `I_TcEvent`
