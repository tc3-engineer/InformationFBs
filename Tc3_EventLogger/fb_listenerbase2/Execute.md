# Execute

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_ListenerBase2` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050384907.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_Execute.xml`](../examples/P_Demo_Execute.xml) |

---

## 1. 功能简述

`FB_ListenerBase2.Execute()` 推进事件队列处理——必须在 PLC 任务里**周期调用**，EventLogger 在本方法内部调用所有挂起的回调（OnAlarmRaised / OnAlarmCleared / OnMessageSent…）。

不调或漏调都可能导致事件丢失或延迟。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

本方法内部检查 EventLogger 内部为本 listener 排队的待处理事件，按顺序逐一调用对应的回调方法。若回调返回 `<> S_OK` 则当前事件保留在队列里，下次 Execute 时重试——这是 EventLogger 内置的流控机制。

**调用频率**：建议放在 PLC 主任务的每个扫描周期里——10 ms 任务下能保证 10 ms 内事件到达。若 PLC 任务周期过长（>100 ms）可能导致 HMI 显示延迟；过短则浪费 CPU。Execute 本身开销很小（无事件时直接返回 S_OK）。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 事件队列推进成功（无事件或全部处理完） | 继续业务 |
| `其他错误` | 内部异常 ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- **必须周期调用**——少调一次可能延迟事件。
- 回调耗时会拖慢 PLC 周期——重操作必须异步化。（工程经验补充）
- 无事件时返回 S_OK 开销很小，不要因为"省 CPU"少调。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Execute.xml`](../examples/P_Demo_Execute.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

PLC 主程序里每周期调一次推进 listener 事件队列


保证事件零延迟到达回调


不调 Execute → 事件全部堆积在 EventLogger 内部，HMI 看不到；本方法是 listener 模式的必须步骤


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.5.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050384907.html
- **相关**：`FB_ListenerBase2`, `FB_ListenerBase2.Subscribe`
