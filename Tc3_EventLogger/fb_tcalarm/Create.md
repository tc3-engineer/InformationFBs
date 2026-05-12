# Create

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcAlarm` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050465035.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcAlarm_Create.xml`](../examples/P_Demo_FB_TcAlarm_Create.xml) |

---

## 1. 功能简述

`FB_TcAlarm.Create()` 把当前 alarm 实例注册到 EventLogger，绑定到指定事件类（GUID）+ 事件 ID。调用成功后这个 `FB_TcAlarm` 实例就能在后续被 `Raise()` / `Clear()` / `Confirm()` 操作。

事件类 GUID 不是 PLC 里手写的——它在 TwinCAT 工程的 EventClass 编辑器（XAE 菜单 View → Other Windows → TwinCAT EventClass）里定义，每个事件类绑定多语言文本资源（中/英/德…）。`nEventId` 是事件类内的唯一编号，对应到具体的事件文本模板。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    eventClass : GUID;
    nEventId : UDINT;
    eSeverity : TcEventSeverity;
    bWithConfirmation : BOOL;
    ipSourceInfo : I_TcSourceInfo;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `eventClass` | `GUID` | 事件类的 GUID（在 EventClass 编辑器里定义） |
| `nEventId` | `UDINT` | 事件 ID，事件类内唯一标识（对应多语言文本模板） |
| `eSeverity` | `TcEventSeverity` | 事件严重级别（Verbose/Info/Warning/Error/Critical） |
| `bWithConfirmation` | `BOOL` | TRUE = Clear 后仍需操作员 Confirm 才完整结束；FALSE = Clear 即完成 |
| `ipSourceInfo` | `I_TcSourceInfo` | 源信息接口指针；传 0 用默认（PLC 符号路径） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

本方法是一次性注册：调用时 EventLogger 内部建立 alarm 实例 → 写入事件日志 → 把 `FB_TcAlarm` 加入活动 alarm 表。**必须只调一次**：常见做法是用 `bCreated : BOOL` latch 包裹，第一次 `SUCCEEDED(hr)`之后不再调用。重复调用同一 GUID+EventID 会返回 `ERROR_ALREADY_EXISTS`。

`ipSourceInfo` 为 `0` 时 EventLogger 自动用 PLC 实例的符号路径作为源信息（默认行为）；如果需要把同一 alarm 关联到一个具体设备/工位，传入预先 `FB_TcSourceInfo` 实例的接口指针。`bWithConfirmation = TRUE` 让此报警在 Clear 后仍保持 "等待确认" 状态，需要操作员显式 Confirm。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | alarm 已成功注册 | 继续后续 Raise/Clear/Confirm |
| `ERROR_ALREADY_EXISTS` | 同 GUID+EventID 的 alarm 已注册 | 用 bCreated latch 跳过重复调用 |
| `其他错误` | 事件类未在工程里定义、ADS 通讯异常等 ⚠️ PDF 未详列 | 对照 ADS Return Codes / 检查 EventClass 配置 |

## 5. 使用注意 / 常见坑

- 一次性注册：必须用 `IF NOT bCreated THEN ... bCreated := SUCCEEDED(hr); END_IF` 包裹。
- `bWithConfirmation` 设错就改不了：注册后这个属性是固定的，需要切换得先 `Release()` 再重新 Create。（工程经验补充）
- 事件类 GUID 必须在 XAE EventClass 编辑器里先定义，否则 HMI 上显示 "未知事件"。
- `ipSourceInfo` 传无效指针会导致 alarm 创建失败但返回的 HRESULT 不一定明显——建议先 `<>`0 判空。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcAlarm_Create.xml`](../examples/P_Demo_FB_TcAlarm_Create.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

**场景**：设备启动初始化阶段，把本工位所有可能报警一次性注册进 EventLogger。比如灌装线 30 个 alarm 实例都在 `MAIN.bFirstScan` 周期里 Create()，之后业务模块只负责 Raise/Clear。


**价值**：把"注册"和"触发"解耦——业务代码只关心"现在出故障了"，不关心怎么向 EventLogger 报告。Create 阶段集中管理事件类/严重级别/确认策略，便于后续工艺变更时统一调整。


**替代方案对比**：直接用 `FB_TcEventLogger.SendMessageEx()` 免实例报警 → 没法跟踪状态、没法 Clear/Confirm；用 `CreateEx` 传 `TcEventEntry` 而不是分散字段 → 当事件已经打包成 TcEventEntry（如从远程接收）时更省事。


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.6.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050465035.html
- **相关**：`FB_TcAlarm`, `FB_TcAlarm.CreateEx`, `FB_TcAlarm.Raise`, `FB_TcMessage.Create`
