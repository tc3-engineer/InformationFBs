# ClearLoggedEvents

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventLogger` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/10408816395.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_ClearLoggedEvents.xml`](../examples/P_Demo_ClearLoggedEvents.xml) |

---

## 1. 功能简述

`FB_TcEventLogger.ClearLoggedEvents()` 异步清除 EventLogger 持久化日志中的历史事件。支持通过 `I_TcClearLoggedEventsSettings`（即 `FB_TcClearLoggedEventsSettings` 实例）过滤要清除的事件子集。

**返回类型是 BOOL**（不是 HRESULT！）—— TRUE 表示异步请求**已不再占用**（结束/释放），通过额外的 `bError` + `hrErrorCode` 输出端反映实际执行结果。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    ipClearSettings : I_TcClearLoggedEventsSettings;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ipClearSettings` | `I_TcClearLoggedEventsSettings` | 可选的清除过滤器；传 0 清空整个日志 |


### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError : BOOL;
    hrErrorCode : HRESULT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | TRUE = 请求执行出错 |
| `hrErrorCode` | `HRESULT` | 出错时的具体 HRESULT 错误码 |


### VAR_IN_OUT

无。

## 3. 行为说明

本方法是异步调用：每周期调用都返回当前请求状态。请求未完成时返回 FALSE；完成或释放时返回 TRUE。**典型调用模式**：用一个 latch 变量包裹「发起请求」逻辑，每周期重新调用直到 BOOL 返回 TRUE，再读 `bError` 判断成败。

`ipClearSettings` 为 0 时清空**整个事件日志**（不可逆！）；传入 `FB_TcClearLoggedEventsSettings`可按时间范围 / 严重级别 / 事件类等条件精确删除。生产环境强烈建议先 ExportLoggedEvents 导出再清。

## 4. 错误码 / 返回值

本方法/函数返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 异步请求已结束（成功或失败） | 立刻读 bError 判断 |
| `FALSE` | 请求仍在进行中 | 下一周期继续调用同方法保持轮询 |

## 5. 使用注意 / 常见坑

- **不可撤销操作**——清前先 ExportLoggedEvents 导出做备份。
- `ipClearSettings := 0` 清整个日志，生产环境绝对不要直接这么调。
- BOOL 返回值是"请求状态"不是"成功/失败"——必须额外检查 bError。
- 异步方法：每周期都要调用同一方法保持轮询，不要只调一次。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ClearLoggedEvents.xml`](../examples/P_Demo_ClearLoggedEvents.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

每月 1 号自动清除上月以前的事件日志，配合 ExportLoggedEvents 把要清的部分先归档到外部存储


按规则清理历史事件，控制 EventLogger 数据库大小，避免无限增长；与 ExportLoggedEvents 配合做完整归档流程


不清理 → 长期运行后日志数据库膨胀；手动到文件系统删 → 风险高、与运行时状态不同步


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.10.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/10408816395.html
- **相关**：`FB_TcClearLoggedEventsSettings`, `FB_TcEventLogger.ExportLoggedEvents`
