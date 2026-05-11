# FB_TcRemoteEventLogger

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/13723763339.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcRemoteEventLogger.xml`](../examples/P_Demo_FB_TcRemoteEventLogger.xml) |

---

## 1. 功能简述

`FB_TcRemoteEventLogger` 代表**远程系统**的 EventLogger 视图——本端 PLC 通过本 FB 操作远程 EventLogger：清除远程 alarm、确认远程 alarm、向远程系统发送 message、清除远程日志等。

实现 `I_RemoteEventLogger`。提供 `Connect` / `Disconnect` 建立 ADS 连接；方法集与 `FB_TcEventLogger` 对应（ClearAlarms / ClearLoggedEvents / ConfirmAlarms / SendMessage*）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nTimeStamp : ULINT := 0;
    bResetConfirmation : BOOL := FALSE;
    ipFilter : I_TcEventFilter;
    ipClearSettings : I_TcClearLoggedEventsSettings;
    nTimeStamp : ULINT := 0;
    ipFilter : I_TcEventFilter;
    sNetId : T_AmsNetId;
    eventClass : GUID;
    nEventId : UDINT;
    eSeverity : TcEventSeverity;
    ipSourceInfo : I_TcSourceInfo := 0;
    nTimeStamp : ULINT := 0;
    ipArguments : I_TcArguments := 0;
    eventClass : GUID;
    nEventId : UDINT;
    eSeverity : TcEventSeverity;
    ipSourceInfo : I_TcSourceInfo := 0;
    nTimeStamp : ULINT := 0;
    ipArguments : I_TcArguments := 0;
    stEventEntry : TcEventEntry;
    ipSourceInfo : I_TcSourceInfo := 0;
    nTimeStamp : ULINT := 0;
    ipArguments : I_TcArguments := 0;
    stEventEntry : TcEventEntry;
    ipSourceInfo : I_TcSourceInfo := 0;
    nTimeStamp : ULINT := 0;
    ipArguments : I_TcArguments := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nTimeStamp` | `ULINT` | `0` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `bResetConfirmation` | `BOOL` | `FALSE` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipFilter` | `I_TcEventFilter` | - | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipClearSettings` | `I_TcClearLoggedEventsSettings` | - | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `nTimeStamp` | `ULINT` | `0` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipFilter` | `I_TcEventFilter` | - | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `sNetId` | `T_AmsNetId` | - | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `eventClass` | `GUID` | - | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `nEventId` | `UDINT` | - | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `eSeverity` | `TcEventSeverity` | - | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipSourceInfo` | `I_TcSourceInfo` | `0` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `nTimeStamp` | `ULINT` | `0` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipArguments` | `I_TcArguments` | `0` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `eventClass` | `GUID` | - | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `nEventId` | `UDINT` | - | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `eSeverity` | `TcEventSeverity` | - | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipSourceInfo` | `I_TcSourceInfo` | `0` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `nTimeStamp` | `ULINT` | `0` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipArguments` | `I_TcArguments` | `0` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `stEventEntry` | `TcEventEntry` | - | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipSourceInfo` | `I_TcSourceInfo` | `0` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `nTimeStamp` | `ULINT` | `0` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipArguments` | `I_TcArguments` | `0` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `stEventEntry` | `TcEventEntry` | - | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipSourceInfo` | `I_TcSourceInfo` | `0` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `nTimeStamp` | `ULINT` | `0` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipArguments` | `I_TcArguments` | `0` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**生命周期**：声明实例 → `Connect(sNetId, nPort)` 建立 ADS 通讯 → 调用方法操作远程 EventLogger → `Disconnect()` 释放连接。所有方法走 ADS 通讯，可能有延迟与失败。

**使用场景**：
- HMI 网关 PLC 远程清除其他 PLC 的 alarm（如紧急批量处理）
- 中央 SCADA 把统一通知 message 推送到所有现场 PLC 的 EventLogger
- 跨地域多 PLC 集中归档：从中央节点导出所有现场的事件日志

**与本地 EventLogger 的区别**：1) 所有调用都是异步 ADS 通讯——延迟取决于网络；2) 断网时方法返回 ADS 错误；3) 权限取决于远程节点的 ADS 安全配置。

## 4. 错误码 / 返回值

本方法/属性不返回数值（`VOID` 或 getter 直接返回引用）。状态通过 EventLogger 的事件日志间接反映。

## 5. 使用注意 / 常见坑

- 远程操作走 ADS——断网会让方法失败，业务侧需要超时与重试机制。
- Disconnect 必须显式调用，否则 PLC 重启前连接占用 ADS 资源。（工程经验补充）
- 跨地域 VPN 通讯延迟可能数百 ms——大量操作建议批量化。（工程经验补充）
- 远程节点的 EventClass 必须与本端一致——GUID 配错会找不到 alarm。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcRemoteEventLogger.xml`](../examples/P_Demo_FB_TcRemoteEventLogger.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

工厂中央控制室 PLC 通过本 FB 远程清除车间 PLC 的所有 alarm（批量复产前的统一复位）


跨 PLC 操作不需要 MQTT/HTTP 中间件——Beckhoff 原生 ADS 走通讯


自建 ADS 客户端 → 重复造轮子；本 FB 把所有方法封装好


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.4.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/13723763339.html
- **相关**：`FB_TcEventLogger`, `FB_RemoteListenerBase`
