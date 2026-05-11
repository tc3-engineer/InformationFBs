# FB_RemoteListenerBase

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/13723762187.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_RemoteListenerBase.xml`](../examples/P_Demo_FB_RemoteListenerBase.xml) |

---

## 1. 功能简述

`FB_RemoteListenerBase` 与 `FB_ListenerBase2` 类似——是事件订阅基类——但订阅的是**远程系统**的 EventLogger 事件（通过 ADS 跨设备通讯）。

通过覆盖回调方法可以接收远程设备的 alarm / message 事件，适合多 PLC 集中监控、HMI 网关、SCADA 中间件等场景。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    ipContext : I_TcListenerContext;
    fbEvent : REFERENCE TO FB_TcEvent;
    ipContext : I_TcListenerContext;
    fbEvent : REFERENCE TO FB_TcEvent;
    ipContext : I_TcListenerContext;
    fbEvent : REFERENCE TO FB_TcEvent;
    ipContext : I_TcListenerContext;
    fbEvent : REFERENCE TO FB_TcEvent;
    ipContext : I_TcListenerContext;
    eReason : TcRemoteConnectionChangeReason;
    ipContext : I_TcListenerContext;
    eReason : TcDatabaseChangeReason;
    ipContext : I_TcListenerContext;
    hr : HRESULT;
    ipContext : I_TcListenerContext;
    fbEvent : REFERENCE TO FB_TcEvent;
    ipRemoteLogger : I_TcRemoteEventLogger;
    ipEventFilter : I_TcEventFilterBase;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ipContext` | `I_TcListenerContext` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `fbEvent` | `REFERENCE TO FB_TcEvent` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipContext` | `I_TcListenerContext` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `fbEvent` | `REFERENCE TO FB_TcEvent` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipContext` | `I_TcListenerContext` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `fbEvent` | `REFERENCE TO FB_TcEvent` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipContext` | `I_TcListenerContext` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `fbEvent` | `REFERENCE TO FB_TcEvent` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipContext` | `I_TcListenerContext` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `eReason` | `TcRemoteConnectionChangeReason` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipContext` | `I_TcListenerContext` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `eReason` | `TcDatabaseChangeReason` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipContext` | `I_TcListenerContext` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `hr` | `HRESULT` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipContext` | `I_TcListenerContext` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `fbEvent` | `REFERENCE TO FB_TcEvent` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipRemoteLogger` | `I_TcRemoteEventLogger` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipEventFilter` | `I_TcEventFilterBase` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

本 FB 自身不维护 VAR_INPUT/OUTPUT，交互通过方法：`Subscribe` 订阅指定 AMS Net ID 远程系统的事件、`Execute` 周期推进、`Unsubscribe` 取消、回调方法 `OnAlarmRaised` / `OnAlarmCleared` / `OnAlarmConfirmed` / `OnAlarmDisposed` / `OnMessageSent` 处理远程事件。

**与本地 listener 差异**：1) 走 ADS 通讯——网络延迟决定回调延迟；2) 远程断网时事件丢失；3) `Subscribe` 必须指定远程 AMS Net ID + Port；4) 大量远程事件会占用 ADS 通讯带宽。

**使用模式**：HMI 网关 PLC 上声明本 FB 子类，订阅所有现场 PLC 的事件汇总到一处显示。

## 4. 错误码 / 返回值

本方法/属性不返回数值（`VOID` 或 getter 直接返回引用）。状态通过 EventLogger 的事件日志间接反映。

## 5. 使用注意 / 常见坑

- 远程通讯不保证传输——网络断时事件丢失，业务侧无法回填。
- 回调延迟取决于网络 RTT——10 ms 局域网正常，跨地域 VPN 可能数百 ms。（工程经验补充）
- 订阅过滤器很重要——远程事件量大且占带宽，必须服务端就过滤。（工程经验补充）
- AMS 路由必须先在 TwinCAT XAE 系统管理器里手动添加远程节点。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_RemoteListenerBase.xml`](../examples/P_Demo_FB_RemoteListenerBase.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

工厂 SCADA 网关 PLC 订阅 8 台现场 PLC 的报警事件汇总到中控 HMI


跨 PLC 事件分发由 Beckhoff 原生支持，免去自建消息中间件


自建 ADS 客户端轮询远程 EventLogger → 延迟高 + CPU 浪费；本 FB 走推送模式


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.4.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/13723762187.html
- **相关**：`FB_ListenerBase2`, `FB_TcRemoteEventLogger`
