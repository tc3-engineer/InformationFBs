# FB_ListenerBase2

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5001704075.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_ListenerBase2.TcPOU`](../examples/P_Demo_FB_ListenerBase2.TcPOU) |

---

## 1. 功能简述

`FB_ListenerBase2` 是 TwinCAT 3 EventLogger 的**事件订阅基类**，PLC 代码通过继承本 FB 并覆盖（OVERRIDE）回调方法接收 EventLogger 广播的事件。实现 `I_Listener2` 接口。

回调方法共 5 个：`OnAlarmRaised` / `OnAlarmCleared` / `OnAlarmConfirmed` / `OnAlarmDisposed`（alarm 四状态变迁）与 `OnMessageSent`（消息发送）。继承本 FB 的子类只需要重写感兴趣的方法、并在主任务里周期调 `Execute()` 推进事件队列。

应用：HMI 后端实现自定义事件展示逻辑、写第三方数据库、转发事件到 OPC UA / MQTT 等场景。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

FB_ListenerBase2 自身没有顶层 VAR_INPUT/OUTPUT，所有交互通过方法：

**典型生命周期**：声明子类实例 → `Subscribe()` 或 `Subscribe2()` 注册到 EventLogger（可选传过滤器）→ 在 PLC 主任务里每周期调 `fbListener.Execute()` 推进事件队列 → EventLogger 在合适时机调用子类的 OnXxx 回调方法（同步！在 PLC 任务上下文里运行）→ 退出前调 `Unsubscribe()` 释放订阅。

**线程模型**：回调在调用 `Execute()` 的 PLC 任务上下文里运行——回调里的代码会占用 PLC 周期时间，重操作（数据库写、网络 IO）需要异步化或转到后台 FB。回调返回 `<> S_OK` 时 EventLogger 会**暂停**后续回调直到下一次 Execute——这是流控机制，防止队列堆积压垮 PLC。

## 4. 错误码 / 返回值

本方法/属性不返回数值（`VOID` 或 getter 直接返回引用）。状态通过 EventLogger 的事件日志间接反映。

## 5. 使用注意 / 常见坑

- 回调里**不要**拷贝 `fbEvent : REFERENCE TO FB_TcEvent`——它只在回调期间有效，回调返回后引用失效。
- 回调返回非 S_OK 时 EventLogger 暂停后续回调到下次 Execute——可以作为业务侧节流机制，但要注意别一直返回非 S_OK 让事件队列阻塞。
- `Execute()` 必须**周期调用**——少调一次都可能导致事件丢失或延迟。
- 回调里耗时操作（数据库写、网络通信）会拖慢 PLC 周期——重逻辑要异步化。（工程经验补充）
- `Subscribe` / `Subscribe2` 重复调用返回 `ADS_E_EXISTS`，本身无副作用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_ListenerBase2.TcPOU`](../examples/P_Demo_FB_ListenerBase2.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

把 EventLogger 事件实时同步到 InfluxDB 时序数据库：继承 FB_ListenerBase2，在 OnAlarmRaised / OnMessageSent 里把事件序列化后送到后台 FB 异步发 HTTP


一次性的代码框架替代手写「轮询 EventLogger 日志 + diff 找新事件 + 推送」三件套；EventLogger 在事件发生时主动调用，零延迟


轮询 EventLogger 日志 → 延迟高 + CPU 浪费；走 ADS 客户端拉取 → 不实时；本 FB 走事件驱动是 Beckhoff 推荐方案


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5001704075.html
- **相关**：`FB_ListenerBase2.Subscribe`, `FB_ListenerBase2.Execute`, `FB_ListenerBase2.OnAlarmRaised`
