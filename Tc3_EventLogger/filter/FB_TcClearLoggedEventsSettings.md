# FB_TcClearLoggedEventsSettings

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/9956769291.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcClearLoggedEventsSettings.TcPOU`](../examples/P_Demo_FB_TcClearLoggedEventsSettings.TcPOU) |

---

## 1. 功能简述

`FB_TcClearLoggedEventsSettings` 用于配置 `FB_TcEventLogger.ClearLoggedEvents()` 的清除规则。

通过方法 `AddFilter` 添加过滤条件（按时间 / 严重级别 / EventClass 等）、`SetLimit` 限制清除数量、`SetSorting` 设置排序后再清除前 N 条，避免误删整个日志。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

FB 自身不发起清除——只是配置容器。**用法**：1) 实例化本 FB；2) 调用 `AddFilter` 添加要清除的事件条件（按时间范围、严重级别、EventClass 等）；3) 可选 `SetLimit(nLimit := n)` 限制最多清 n 条事件作为安全网；4) 可选 `SetSorting` 设置排序规则；5) 把本实例的接口指针传给 `FB_TcEventLogger.ClearLoggedEvents(ipClearSettings := this)` 触发清除。

**最佳实践**：始终调 SetLimit 避免误清整个日志；生产环境清除前先用 `ExportLoggedEvents` 归档备份。Clear 方法可以清空当前配置，便于复用同一 FB 实例配置不同规则。

## 4. 错误码 / 返回值

本方法/属性不返回数值（`VOID` 或 getter 直接返回引用）。状态通过 EventLogger 的事件日志间接反映。

## 5. 使用注意 / 常见坑

- 不设 SetLimit 又传给 ClearLoggedEvents 可能清掉超出预期的事件——务必设上限。（工程经验补充）
- Filter 条件错配会清错事件——上生产前在测试机上验证。（工程经验补充）
- 本 FB 配置后再修改对正在进行的 ClearLoggedEvents 无效——重新发起。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcClearLoggedEventsSettings.TcPOU`](../examples/P_Demo_FB_TcClearLoggedEventsSettings.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

月度归档流程：清除 30 天前的 Info 级 message，保留 Warning+ 级别和 alarm


精细规则避免误删重要事件


`ClearLoggedEvents(ipClearSettings := 0)` 清整个日志 → 太危险；本 FB 提供精细规则


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/9956769291.html
- **相关**：`FB_TcEventLogger.ClearLoggedEvents`, `FB_TcEventFilter`, `FB_TcEventCsvExportSettings`
