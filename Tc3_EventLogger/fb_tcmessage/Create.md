# Create

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcMessage` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050907915.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcMessage_Create.TcPOU`](../examples/P_Demo_FB_TcMessage_Create.TcPOU) |

---

## 1. 功能简述

`FB_TcMessage.Create()` 把 message 实例注册到 EventLogger，绑定到指定事件类（GUID）+ 事件 ID + 严重级别。注册成功后这个实例就能在后续被 `Send()` 触发。

与 `FB_TcAlarm.Create()` 的差别：本方法**没有 `bWithConfirmation` 参数**——message 没有确认状态。其他参数（eventClass / nEventId / eSeverity / ipSourceInfo）含义完全一致。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    eventClass : GUID;
    nEventId : UDINT;
    eSeverity : TcEventSeverity;
    ipSourceInfo : I_TcSourceInfo := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `eventClass` | `GUID` | - | 事件类的 GUID（在 EventClass 编辑器里定义） |
| `nEventId` | `UDINT` | - | 事件 ID（事件类内唯一） |
| `eSeverity` | `TcEventSeverity` | - | 事件严重级别（Verbose/Info/Warning/Error/Critical） |
| `ipSourceInfo` | `I_TcSourceInfo` | `0` | 源信息接口指针；传 0 用默认源信息（PLC 符号路径） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

一次性注册：调用时 EventLogger 内部建立 message 槽位、写入事件日志、把 `FB_TcMessage` 加入活动消息表。**必须只调一次**——用 `bCreated : BOOL` latch 包裹。重复调返回 `ERROR_ALREADY_EXISTS`。

`ipSourceInfo` 默认 `0`：用 PLC 实例符号路径作为源信息。多 PLC 共用一个 EventLogger 时传入预先构造的`FB_TcSourceInfo` 接口指针，让 message 关联到具体设备/工位。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | message 已成功注册 | 继续后续 Send() |
| `ERROR_ALREADY_EXISTS` | 同 GUID+EventID 已注册 | 用 bCreated latch 跳过重复调用 |
| `其他错误` | 事件类未定义 / ADS 异常 ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- 一次性注册：必须用 `IF NOT bCreated THEN ... END_IF` 包裹。
- 事件类 GUID 必须在 XAE EventClass 编辑器里先定义，否则 HMI 显示"未知事件"。
- Info / Verbose 级别的 message 在某些 HMI 视图被默认过滤，调试时确认严重级别。（工程经验补充）
- `ipSourceInfo` 传无效指针会让 message 创建失败但 HRESULT 不明显——传 0 最稳妥。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcMessage_Create.TcPOU`](../examples/P_Demo_FB_TcMessage_Create.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

设备上电时把所有 message 类事件（操作日志、配方切换、批次开始）一次性注册进 EventLogger


集中注册便于事件清单的版本管理；业务代码只需 Send 不关心元数据


`SendMessage()` 免实例发送 → 临时一次性消息合适，不适合复用模板；`CreateEx()` 用 TcEventEntry 结构体 → 适合事件已结构化的场景


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.11.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050907915.html
- **相关**：`FB_TcMessage`, `FB_TcMessage.CreateEx`, `FB_TcAlarm.Create`
