# SendMessage

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventLogger` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050843019.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_SendMessage.TcPOU`](../examples/P_Demo_SendMessage.TcPOU) |

---

## 1. 功能简述

`FB_TcEventLogger.SendMessage()` 免实例直接发一条 message 事件——无需事先 Create 一个 `FB_TcMessage` 实例。

适合一次性通知场景：登录/注销日志、调试 trace、临时配方变更等不需要复用模板的事件。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    eventClass : GUID;
    nEventId : UDINT;
    eSeverity : TcEventSeverity;
    ipSourceInfo : I_TcSourceInfo := 0;
    nTimeStamp : ULINT := 0;
    ipArguments : I_TcArguments := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `eventClass` | `GUID` | - | 事件类 GUID（必须事先在 EventClass 编辑器定义） |
| `nEventId` | `UDINT` | - | 事件 ID |
| `eSeverity` | `TcEventSeverity` | - | 严重级别 |
| `ipSourceInfo` | `I_TcSourceInfo` | `0` | 源信息接口；传 0 用默认 |
| `nTimeStamp` | `ULINT` | `0` | 时间戳：0 = 当前系统时间 |
| `ipArguments` | `I_TcArguments` | `0` | 参数接口；传 0 = 无参数 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

EventLogger 内部临时构造一个 message 对象 → 写入事件日志 → 分发给监听器 → 释放。调用方不持有任何 message 实例，免去注册步骤。

**参数语义**：与 `FB_TcMessage.Create()` + Send 组合等效，其中 `ipArguments` 可选——传入预先填好的 `FB_TcArguments` 接口让 EventLogger 把参数与消息一起持久化。`nTimeStamp = 0` 用当前系统时间。

**调用时机**：边沿触发，不要每周期发——HMI 会被刷爆。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 消息已发送 | 继续业务 |
| `其他错误` | 事件类未定义 / 内部异常 ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- 边沿触发不要每周期发——HMI 会被刷爆。
- 免实例 = 无法后续修改消息——SetJsonAttribute / 修改 Arguments 都得用 SendMessage2 + JSON 或 FB_TcMessage 实例。
- EventClass + EventID 必须事先在工程里定义。
- ipArguments 用完后调用方仍持有所有权——如果是 __NEW 创建的要记得 Release/__DELETE。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SendMessage.TcPOU`](../examples/P_Demo_SendMessage.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

操作员登录/注销审计：每次登录瞬间发一条 message，无需持久化 message 实例


免实例 = 少声明 FB；轻量场景代码更简洁


`FB_TcMessage` 实例 → 适合复用模板（同 GUID+ID 多次发）；本方法适合一次性通知


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.10.11
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050843019.html
- **相关**：`FB_TcEventLogger.SendMessage2`, `FB_TcEventLogger.SendMessageEx`, `FB_TcMessage`
